import unittest
import json
from app import app

class BTechCareersTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True

    def test_btech_completed_cse_pathways(self):
        """TEST 1: B.Tech Completed + CSE must return 9 post-grad pathways, NOT raw branches"""
        res = self.app.get('/api/btech/pathways?branch=CSE')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertGreaterEqual(data["total_pathways"], 9)
        pathway_ids = [p["id"] for p in data["pathways"]]
        # Must contain major pathways
        self.assertIn("job", pathway_ids)
        self.assertIn("higher_studies", pathway_ids)
        self.assertIn("competitive_exams", pathway_ids)
        self.assertIn("govt_psu", pathway_ids)
        self.assertIn("defence", pathway_ids)
        self.assertIn("entrepreneurship", pathway_ids)
        self.assertIn("study_abroad", pathway_ids)
        self.assertIn("upskilling", pathway_ids)
        self.assertIn("career_change", pathway_ids)
        # Verify CSE / ECE / EEE are NOT returned as pathways
        self.assertNotIn("cse", pathway_ids)
        self.assertNotIn("ece", pathway_ids)
        self.assertNotIn("civil", pathway_ids)

    def test_btech_completed_cse_jobs(self):
        """TEST 2: B.Tech Completed + CSE + Software Job shows IT/software categories & roles"""
        res = self.app.get('/api/btech/jobs?branch=CSE&category=it_software')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertGreater(data["total_roles"], 0)
        # Check that categories returned contains it_software
        cat = next((c for c in data["categories"] if c["id"] == "it_software"), None)
        self.assertIsNotNone(cat)
        role_names = [r["name"] for r in cat["roles"]]
        self.assertTrue(any("Developer" in name or "Engineer" in name for name in role_names))

    def test_btech_completed_gate_integration(self):
        """TEST 3: B.Tech Completed + CSE + GATE shows GATE details and official portal"""
        res = self.app.get('/api/btech/gate')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        gate = data["gate_guide"]
        self.assertIn("Graduate Aptitude Test in Engineering", gate["title"])
        self.assertIn("gate", gate["official_portal"])
        self.assertIn("CSE / IT", gate["papers_map"])
        self.assertIn("psus_hiring_through_gate", gate)
        self.assertGreater(len(gate["psus_hiring_through_gate"]), 5)

    def test_btech_completed_ece(self):
        """TEST 4: B.Tech Completed + ECE shows ECE-relevant roles (VLSI, Embedded)"""
        res = self.app.get('/api/btech/jobs?branch=ECE&category=core_engineering')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        cat = next((c for c in data["categories"] if c["id"] == "core_engineering"), None)
        self.assertIsNotNone(cat)
        role_ids = [r["id"] for r in cat["roles"]]
        self.assertIn("role-vlsi", role_ids)
        self.assertIn("role-embedded", role_ids)
        # Civil structural should NOT be in ECE core
        self.assertNotIn("role-structural-civil", role_ids)

    def test_btech_completed_civil(self):
        """TEST 5: B.Tech Completed + Civil shows Civil-relevant careers"""
        res = self.app.get('/api/btech/jobs?branch=Civil&category=core_engineering')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        cat = next((c for c in data["categories"] if c["id"] == "core_engineering"), None)
        self.assertIsNotNone(cat)
        role_ids = [r["id"] for r in cat["roles"]]
        self.assertIn("role-structural-civil", role_ids)
        # VLSI should NOT be in Civil core
        self.assertNotIn("role-vlsi", role_ids)

    def test_btech_completed_cyber_security(self):
        """TEST 6: B.Tech Completed + Cyber Security shows cybersecurity roles, skills, and companies"""
        res = self.app.get('/api/btech/jobs?branch=CSE&category=cyber_security')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        cat = next((c for c in data["categories"] if c["id"] == "cyber_security"), None)
        self.assertIsNotNone(cat)
        self.assertGreater(len(cat["roles"]), 0)
        soc_role = next((r for r in cat["roles"] if r["id"] == "role-soc-analyst"), None)
        self.assertIsNotNone(soc_role)
        self.assertIn("SIEM Tools (Splunk / Sentinel)", soc_role["skills"])
        self.assertIn("Cisco", soc_role["companies"])

    def test_btech_completed_higher_studies(self):
        """TEST 7: B.Tech Completed + Higher Studies shows M.Tech/MS/MBA/PhD with entrance routes"""
        res = self.app.get('/api/btech/higher-studies')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        studies = data["higher_studies"]
        degree_ids = [hs["id"] for hs in studies]
        self.assertIn("hs-mtech", degree_ids)
        self.assertIn("hs-ms-abroad", degree_ids)
        self.assertIn("hs-mba", degree_ids)
        self.assertIn("hs-phd", degree_ids)

    def test_company_directory(self):
        """TEST 8: Company selection shows official company info + official careers link + verified data"""
        res = self.app.get('/api/btech/companies?search=Infosys')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        self.assertGreater(data["total"], 0)
        infy = data["companies"][0]
        self.assertEqual(infy["name"], "Infosys")
        self.assertIn("https://careers.infosys.com", infy["official_careers_url"])
        self.assertIn("https://www.infosys.com", infy["official_website"])
        self.assertIn("Java", infy["verified_skills"])
        self.assertIn("last_verified", infy)

    def test_pathway_comparison(self):
        """Test pathway side-by-side comparison without bias"""
        res = self.app.get('/api/btech/compare?id=comp-job-vs-mtech')
        self.assertEqual(res.status_code, 200)
        data = json.loads(res.data)
        self.assertEqual(data["status"], "success")
        comp = data["comparison"]
        self.assertIn("Private Industry Job vs M.Tech", comp["title"])
        self.assertIn("left", comp)
        self.assertIn("right", comp)

if __name__ == '__main__':
    unittest.main()
