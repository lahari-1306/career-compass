import unittest
import json
from app import app
from radar.models import StudentProfile
from radar.matcher import RadarMatcher

class TestExpandedOptions(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
        self.matcher = RadarMatcher()

    def test_api_options_endpoint(self):
        res = self.client.get('/api/options')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertIn('btech_branches', data)
        self.assertIn('states', data)
        self.assertIn('union_territories', data)
        self.assertIn('completion_years', data)
        self.assertIn('completion_statuses', data)

        # Verify all 33 branches are present
        branches = data['btech_branches']
        self.assertGreaterEqual(len(branches), 33)
        self.assertIn('CSE', branches)
        self.assertIn('Information Technology (IT)', branches)
        self.assertIn('ECE', branches)
        self.assertIn('EEE', branches)
        self.assertIn('Mechanical Engineering', branches)
        self.assertIn('Civil Engineering', branches)
        self.assertIn('Aerospace / Aeronautical Engineering', branches)
        self.assertIn('Mechatronics', branches)
        self.assertIn('Cyber Security', branches)
        self.assertIn('Data Science', branches)
        self.assertIn('AI & ML', branches)
        self.assertIn('Biotechnology', branches)

        # Verify 28 states and 8 UTs
        self.assertEqual(len(data['states']), 28)
        self.assertEqual(len(data['union_territories']), 8)
        self.assertIn('Andhra Pradesh', data['states'])
        self.assertIn('Maharashtra', data['states'])
        self.assertIn('Delhi', data['union_territories'])
        self.assertIn('Ladakh', data['union_territories'])

        # Verify completion statuses
        self.assertIn('Currently Studying', data['completion_statuses'])
        self.assertIn('Final Year', data['completion_statuses'])
        self.assertIn('Completed', data['completion_statuses'])

    def test_student_profile_completion_status(self):
        profile = StudentProfile(
            qualification="B.Tech",
            stream_or_branch="Information Technology (IT)",
            completion_status="Completed",
            completion_year="2024",
            state="Maharashtra"
        )
        d = profile.to_dict()
        self.assertEqual(d['completion_status'], 'Completed')
        self.assertEqual(d['stream_or_branch'], 'Information Technology (IT)')

        reconstructed = StudentProfile.from_dict(d)
        self.assertEqual(reconstructed.completion_status, 'Completed')
        self.assertEqual(reconstructed.stream_or_branch, 'Information Technology (IT)')

    def test_matcher_branch_families(self):
        # Test branch family matching: IT student matches CSE/IT targets
        self.assertTrue(RadarMatcher._branch_matches("Information Technology (IT)", ["CSE"]))
        self.assertTrue(RadarMatcher._branch_matches("Information Technology (IT)", ["IT"]))
        self.assertTrue(RadarMatcher._branch_matches("CSE (AI)", ["AI/ML"]))
        self.assertTrue(RadarMatcher._branch_matches("Mechanical Engineering", ["Mechanical"]))
        self.assertTrue(RadarMatcher._branch_matches("Civil Engineering", ["Civil"]))
        self.assertTrue(RadarMatcher._branch_matches("Aerospace / Aeronautical Engineering", ["Aerospace"]))

    def test_matcher_national_scope(self):
        opp = {
            "id": "opp_gate_2026",
            "title": "GATE 2026 Official Application",
            "category": "Entrance Exams",
            "target_qualifications": ["B.Tech"],
            "target_branches": ["ALL_ENGINEERING"],
            "target_states": ["All India / National"]
        }
        profile = StudentProfile(
            profile_id="test_mech_01",
            qualification="B.Tech",
            stream_or_branch="Mechanical Engineering",
            completion_status="Final Year",
            state="Karnataka",
            interests=["GATE", "Higher Studies"]
        )
        matches = RadarMatcher.match(profile.to_dict(), [opp])
        self.assertEqual(len(matches), 1)
        self.assertGreater(matches[0]['match_score'], 50)

    def test_btech_jobs_with_expanded_branch(self):
        # Test jobs query with Information Technology (IT)
        res = self.client.get('/api/btech/jobs?branch=Information%20Technology%20(IT)')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertGreater(data['total_roles'], 0)

        # Test jobs query with Civil Engineering
        res_civil = self.client.get('/api/btech/jobs?branch=Civil%20Engineering')
        self.assertEqual(res_civil.status_code, 200)
        data_civil = json.loads(res_civil.data)
        self.assertGreater(data_civil['total_roles'], 0)

if __name__ == '__main__':
    unittest.main()
