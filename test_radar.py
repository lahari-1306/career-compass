import unittest
import json
from app import app
from data_updater.validator import DataValidator
from radar.dispatcher import RadarDispatcher
from radar.storage import RadarStorage

class RadarSystemTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_validator_domain_whitelist(self):
        # Valid official domains
        valid_gov, _ = DataValidator.validate_official_url("https://upsc.gov.in/examinations")
        self.assertTrue(valid_gov)

        valid_nic, _ = DataValidator.validate_official_url("https://jeemain.nta.nic.in")
        self.assertTrue(valid_nic)

        valid_ac, _ = DataValidator.validate_official_url("https://gate2025.iitr.ac.in")
        self.assertTrue(valid_ac)

        # Prohibited 3rd party blog scraper
        invalid_scraper, msg1 = DataValidator.validate_official_url("https://www.sarkariresult.com/latestjobs")
        self.assertFalse(invalid_scraper)
        self.assertIn("Prohibited", msg1)

        # Random unofficial commercial site
        invalid_com, msg2 = DataValidator.validate_official_url("https://careerguideblog.org/gate-info")
        self.assertFalse(invalid_com)
        self.assertIn("not in verified official authority whitelist", msg2)

    def test_validator_chronology(self):
        opp_bad = {
            "id": "test-bad",
            "title": "Bad Date Exam",
            "organization": "Testing Board",
            "category": "Entrance Exams",
            "status": "OPEN",
            "official_source": "https://nta.ac.in",
            "start_datetime": "2026-10-10T10:00:00+05:30",
            "end_datetime": "2026-09-01T10:00:00+05:30"  # start after end!
        }
        is_valid, errors = DataValidator.validate_opportunity(opp_bad)
        self.assertFalse(is_valid)
        self.assertTrue(any("Chronology violation" in e for e in errors))

    def test_profile_a_btech_cse(self):
        profile_btech = {
            "profile_id": "test_btech_cse_001",
            "qualification": "B.Tech",
            "stream_or_branch": "CSE",
            "state": "Andhra Pradesh",
            "interests": ["Higher Studies / M.Tech", "PSU / Govt Jobs"]
        }
        res = self.app.post("/api/radar/matches", json=profile_btech)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        matches = data["matches"]
        
        match_ids = [m["opportunity_id"] for m in matches]
        # B.Tech CSE must match GATE
        self.assertIn("notif-gate-2027", match_ids)
        # B.Tech CSE must NOT match 10th polytechnic
        self.assertNotIn("notif-polycet-admissions", match_ids)

        # Verify transparent reasons exist
        gate_match = next(m for m in matches if m["opportunity_id"] == "notif-gate-2027")
        self.assertGreater(len(gate_match["match_reasons"]), 0)
        self.assertTrue(any("qualification: B.Tech" in r for r in gate_match["match_reasons"]))

    def test_profile_b_inter_mpc(self):
        profile_inter = {
            "profile_id": "test_inter_mpc_002",
            "qualification": "Intermediate",
            "stream_or_branch": "MPC",
            "state": "Andhra Pradesh",
            "interests": ["Engineering Entrance", "Defence Forces"]
        }
        res = self.app.post("/api/radar/matches", json=profile_inter)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        matches = data["matches"]
        match_ids = [m["opportunity_id"] for m in matches]

        # Must match JEE Main or NDA or Army TES
        self.assertTrue(any(id in match_ids for id in ["notif-jeemain-cycle", "notif-nda-cycle", "notif-army-tes", "notif-eapcet-counselling"]))
        # Must NOT match B.Tech/Diploma specific exams like GATE or ECET
        self.assertNotIn("notif-gate-2027", match_ids)
        self.assertNotIn("notif-ecet-counselling", match_ids)

    def test_profile_c_10th(self):
        profile_10th = {
            "profile_id": "test_10th_003",
            "qualification": "10th",
            "stream_or_branch": "General",
            "state": "Andhra Pradesh",
            "interests": ["Polytechnic Admissions"]
        }
        res = self.app.post("/api/radar/matches", json=profile_10th)
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        matches = data["matches"]
        match_ids = [m["opportunity_id"] for m in matches]

        # Must match AP POLYCET
        self.assertIn("notif-polycet-admissions", match_ids)
        # Must NOT match higher qualifications
        self.assertNotIn("notif-gate-2027", match_ids)
        self.assertNotIn("notif-cat-2026", match_ids)
        self.assertNotIn("notif-upsc-cds", match_ids)

    def test_save_profile_and_duplicate_prevention(self):
        prof = {
            "profile_id": "prof_test_dedup_004",
            "qualification": "B.Tech",
            "stream_or_branch": "CSE",
            "state": "Andhra Pradesh",
            "interests": ["Higher Studies / M.Tech"]
        }
        # First save
        res1 = self.app.post("/api/radar/profile", json=prof)
        self.assertEqual(res1.status_code, 200)

        # Check alerts
        res_alerts = self.app.get(f"/api/radar/alerts?id={prof['profile_id']}")
        self.assertEqual(res_alerts.status_code, 200)
        alerts_data = json.loads(res_alerts.data)
        initial_alert_count = alerts_data["total_alerts"]
        self.assertGreater(initial_alert_count, 0)

        # Dispatch again for same opportunities
        notifs = json.loads(self.app.get("/api/notifications/all").data)["notifications"]
        dispatched_second = RadarDispatcher.dispatch_for_profile(prof, notifs)
        # Should be 0 because of duplicate fingerprint prevention!
        self.assertEqual(dispatched_second, 0)

        # Mark alerts as read
        mark_res = self.app.post("/api/radar/mark-read", json={"profile_id": prof["profile_id"]})
        self.assertEqual(mark_res.status_code, 200)
        
        # Verify unread count is now 0
        res_after = self.app.get(f"/api/radar/alerts?id={prof['profile_id']}")
        self.assertEqual(json.loads(res_after.data)["unread_count"], 0)

    def test_admin_updater_status(self):
        res = self.app.get("/api/admin/updater-status")
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn("registry", data)
        self.assertGreaterEqual(data["total_sources"], 8)

if __name__ == "__main__":
    unittest.main()
