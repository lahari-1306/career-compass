"""
Comprehensive Test Suite for Qualification-Aware AI Career Guide & Assistant
Tests all 10 profiles in the user's evaluation matrix + stage-aware assistant Q&A + anti-hallucination.
"""
import unittest
import json
import re
from app import app
from ai_engine import AIEngine, get_verified_current_data

class AIProfilesTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.client = app.test_client()
        cls.client.testing = True

    # -------------------------------------------------------------
    # 1. PROFILE 1: After 10th interested in Engineering
    # -------------------------------------------------------------
    def test_profile_1_tenth_engineering(self):
        payload = {
            "message": "I finished 10th and want to go towards engineering. What should I do next?",
            "profile": {
                "qualification": "10th",
                "education_level": "10th",
                "branch": "General",
                "interests": ["Engineering", "Mathematics"],
                "preferred_career_direction": "Intermediate (MPC / BiPC / CEC / MEC)"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        # Must focus on next stage options: Intermediate MPC, Polytechnic Diploma, ITI
        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("mpc" in options_text or "polytechnic" in options_text or "diploma" in options_text)
        # Must NOT suggest post-B.Tech careers like SDE or GATE PSU
        self.assertNotIn("gate exam", options_text)
        self.assertNotIn("sde at", options_text)
        # Section 10 fields check
        self.assertIn("current_position", r)
        self.assertIn("option_selected", r)
        self.assertIn("eligibility", r)
        self.assertIn("what_to_study_skills", r)
        self.assertIn("admission_process", r)
        self.assertIn("next_education_or_career_step", r)
        self.assertIn("career_opportunities", r)

    # -------------------------------------------------------------
    # 2. PROFILE 2: After 10th interested in Medicine
    # -------------------------------------------------------------
    def test_profile_2_tenth_medicine(self):
        payload = {
            "message": "I finished 10th and want to become a doctor. What should I study?",
            "profile": {
                "qualification": "10th",
                "interests": ["Medicine", "Biology", "Doctor"],
                "preferred_career_direction": "Medical & Allied Health Sciences"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("bipc" in options_text or "biology" in options_text or "neet" in options_text)
        self.assertNotIn("sde", options_text)
        self.assertNotIn("software engineer", options_text)

    # -------------------------------------------------------------
    # 3. PROFILE 3: Intermediate MPC
    # -------------------------------------------------------------
    def test_profile_3_intermediate_mpc(self):
        payload = {
            "message": "I am in Intermediate MPC. What are my options?",
            "profile": {
                "qualification": "Intermediate",
                "branch": "MPC",
                "status": "Currently Studying"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("b.tech" in options_text or "engineering" in options_text)
        exams = [e.lower() for e in r["entrance_exams"]]
        self.assertTrue(any("jee" in e or "cet" in e or "nda" in e for e in exams))
        # Must not suggest Lateral Entry ECET (that's for Diploma!)
        self.assertNotIn("ecet", options_text)

    # -------------------------------------------------------------
    # 4. PROFILE 4: Intermediate BiPC
    # -------------------------------------------------------------
    def test_profile_4_intermediate_bipc(self):
        payload = {
            "message": "I completed Intermediate BiPC. What can I do?",
            "profile": {
                "qualification": "Intermediate",
                "branch": "BiPC",
                "status": "Completed"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("mbbs" in options_text or "pharmacy" in options_text or "neet" in options_text or "b.sc agriculture" in options_text)
        self.assertNotIn("jee main", options_text)
        self.assertNotIn("sde", options_text)

    # -------------------------------------------------------------
    # 5. PROFILE 5: Diploma CSE
    # -------------------------------------------------------------
    def test_profile_5_diploma_cse(self):
        payload = {
            "message": "What can I do after Diploma CSE?",
            "profile": {
                "qualification": "Diploma",
                "branch": "CSE",
                "status": "Final Year"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("lateral entry" in options_text or "ecet" in options_text or "rrb" in options_text)
        exams = [e.lower() for e in r["entrance_exams"]]
        self.assertTrue(any("ecet" in e or "rrb" in e for e in exams))

    # -------------------------------------------------------------
    # 6. PROFILE 6: Diploma Mechanical
    # -------------------------------------------------------------
    def test_profile_6_diploma_mechanical(self):
        payload = {
            "message": "Career opportunities after Diploma in Mechanical Engineering?",
            "profile": {
                "qualification": "Diploma",
                "branch": "Mechanical Engineering",
                "status": "Completed"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("lateral entry" in options_text or "junior engineer" in options_text or "ssc je" in options_text or "core" in options_text)
        self.assertNotIn("mbbs", options_text)
        self.assertNotIn("frontend developer", options_text)

    # -------------------------------------------------------------
    # 7. PROFILE 7: B.Tech CSE
    # -------------------------------------------------------------
    def test_profile_7_btech_cse(self):
        payload = {
            "message": "Career roadmap for B.Tech CSE graduate",
            "profile": {
                "qualification": "B.Tech",
                "branch": "CSE",
                "status": "Completed"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("sde" in options_text or "software" in options_text or "gate" in options_text)
        # Must NOT suggest intermediate or polytechnic options
        self.assertNotIn("intermediate mpc", options_text)
        self.assertNotIn("polycet", options_text)

    # -------------------------------------------------------------
    # 8. PROFILE 8: B.Tech Cyber Security
    # -------------------------------------------------------------
    def test_profile_8_btech_cyber_security(self):
        payload = {
            "message": "Career guidance for B.Tech Cyber Security student",
            "profile": {
                "qualification": "B.Tech",
                "branch": "Cyber Security",
                "status": "Final Year"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("soc" in options_text or "security" in options_text or "cert-in" in options_text or "comptia" in options_text)
        # Distinct from generic CSE
        self.assertTrue("cyber" in data["title"].lower())

    # -------------------------------------------------------------
    # 9. PROFILE 9: B.Tech Mechanical
    # -------------------------------------------------------------
    def test_profile_9_btech_mechanical(self):
        payload = {
            "message": "Career path after B.Tech Mechanical Engineering",
            "profile": {
                "qualification": "B.Tech",
                "branch": "Mechanical Engineering",
                "status": "Completed"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("psu" in options_text or "gate me" in options_text or "automotive" in options_text or "ese" in options_text)
        # Must not suggest software SDE coding roadmap
        self.assertNotIn("leetcode", " ".join(r["next_steps"]).lower())

    # -------------------------------------------------------------
    # 10. PROFILE 10: Postgraduate
    # -------------------------------------------------------------
    def test_profile_10_postgraduate(self):
        payload = {
            "message": "Career direction after M.Tech / Postgraduate",
            "profile": {
                "qualification": "Postgraduate",
                "branch": "M.Tech (CSE)",
                "status": "Completed"
            }
        }
        res = self.client.post("/api/ai/chat", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()["data"]
        r = data["roadmap"]

        options_text = " ".join(r["suitable_options"]).lower()
        self.assertTrue("ph.d" in options_text or "research" in options_text or "ugc net" in options_text or "professor" in options_text)
        self.assertNotIn("b.tech admission", options_text)
        self.assertNotIn("polycet", options_text)

    # -------------------------------------------------------------
    # 11. Assistant Question-Answering Tests
    # -------------------------------------------------------------
    def test_assistant_stage_specific_answers(self):
        # Q: What exams can I write? (Stage-specific test)
        res_10th = self.client.post("/api/ai/chat", json={"message": "Which exams can I write?", "profile": {"qualification": "10th"}})
        res_btech = self.client.post("/api/ai/chat", json={"message": "Which exams can I write?", "profile": {"qualification": "B.Tech", "branch": "CSE"}})
        
        reply_10th = res_10th.get_json().get("reply", "")
        reply_btech = res_btech.get_json().get("reply", "")

        self.assertIn("POLYCET", reply_10th)
        self.assertIn("GATE", reply_btech)
        self.assertNotEqual(reply_10th, reply_btech)

        # Q: Can I go for higher studies?
        res_dip = self.client.post("/api/ai/chat", json={"message": "Can I go for higher studies?", "profile": {"qualification": "Diploma"}})
        reply_dip = res_dip.get_json().get("reply", "")
        self.assertIn("Lateral Entry", reply_dip)

    # -------------------------------------------------------------
    # 12. Anti-Hallucination & Verified Database Citation
    # -------------------------------------------------------------
    def test_anti_hallucination_for_dates_and_fees(self):
        # Asking for future unknown date/fees for a non-existing exam
        res = self.client.post("/api/ai/chat", json={"message": "What is the application deadline and fee for XYZ Random Exam 2035?", "profile": {"qualification": "B.Tech"}})
        reply = res.get_json().get("reply", "")
        # Must not fabricate an exact fee or deadline
        self.assertTrue("don't have a verified" in reply.lower() or "check the official" in reply.lower() or "not available" in reply.lower())

if __name__ == "__main__":
    unittest.main()
