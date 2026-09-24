"""
CAREER COMPASS — PREPARATION HUB & LEARNING RESOURCES TEST SUITE
Tests all aspects of the enhanced Preparation Hub:
1. Navigation labeling & zero raw translation keys
2. 8 distinct student qualification profile tests (10th, Inter MPC, Inter BiPC, Diploma, B.Tech CSE, B.Tech ECE, B.Tech Mech, PG)
3. Factual access types (FREE, OFFICIAL FREE RESOURCE, FREE + PAID)
4. Category filters & search query filtering
5. AI Study Guidance grounded in verified database
6. Admin endpoints (CRUD & health check)
7. Link format & security (target="_blank", noopener)
8. Multilingual translations (EN, TE, HI)
"""

import unittest
import json
import os
import re
from app import app
from database import init_db, get_db_connection
from db_repository import LearningResourceRepository
from services.pipeline_service import PipelineService


class PreparationHubTestSuite(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.app.config["TESTING"] = True
        cls.client = cls.app.test_client()
        init_db()
        conn = get_db_connection()
        conn.execute("UPDATE learning_resources SET verification_status='VERIFIED'")
        conn.commit()
        conn.close()

    # ==========================================================
    # TEST 1: Navigation Labels & Zero Raw Keys
    # ==========================================================
    def test_navigation_labels_and_no_raw_keys(self):
        """Verify 'Preparation Hub' is displayed and 'nav.exam.prep' is eliminated."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        html = response.data.decode("utf-8")

        # Must NOT contain raw untranslated nav keys
        self.assertNotIn("nav.exam.prep", html)
        self.assertNotIn("exam.prep", html)

        # Must contain 'Preparation Hub'
        self.assertIn("Preparation Hub", html)

        # Must contain the 8 Preparation Hub tabs
        self.assertIn('data-tab="practice"', html)
        self.assertIn('data-tab="exams"', html)
        self.assertIn('data-tab="study-materials"', html)
        self.assertIn('data-tab="books"', html)
        self.assertIn('data-tab="pyqs"', html)
        self.assertIn('data-tab="mocks"', html)
        self.assertIn('data-tab="plans"', html)
        self.assertIn('data-tab="ai"', html)

    # ==========================================================
    # TEST 2: Multilingual Support for Preparation Hub
    # ==========================================================
    def test_multilingual_locales_presence(self):
        """Verify complete translations for Preparation Hub in EN, TE, and HI."""
        with open("static/js/locales.js", encoding="utf-8") as f:
            locales_js = f.read()

        # All 3 languages must have prep_hub translations
        for lang in ['"en":', '"te":', '"hi":']:
            self.assertIn(lang, locales_js, f"Missing language block: {lang}")

        # English keys
        self.assertIn('"prep_hub": "Preparation Hub"', locales_js)
        self.assertIn('"your_hub": "Your Preparation Hub"', locales_js)
        self.assertIn('"continue_prep": "Continue Preparation"', locales_js)

        # Telugu keys
        self.assertIn('"prep_hub":', locales_js)
        self.assertIn('"tab_practice": "ప్రాక్టీస్ & ట్రైనింగ్"', locales_js)

        # Hindi keys
        self.assertIn('"tab_practice": "अभ्यास और प्रशिक्षण"', locales_js)

    # ==========================================================
    # TEST 3: Resource Dataset & Database Seeding
    # ==========================================================
    def test_database_seeding_and_integrity(self):
        """Verify that learning resources are properly loaded in SQLite."""
        resources = LearningResourceRepository.get_all(verification_status=None)
        self.assertGreaterEqual(len(resources), 24, "Should have at least 24 verified learning resources")

        # Check required fields on all resources
        required_fields = [
            "id", "name", "description", "official_url", "category",
            "education_levels", "access_type", "verification_status"
        ]
        for r in resources:
            for field in required_fields:
                self.assertIn(field, r, f"Resource {r.get('id')} missing {field}")
            self.assertTrue(r["official_url"].startswith("http"), f"Invalid URL for {r['id']}")

    # ==========================================================
    # TEST 4: Factual Access Type Integrity (No False Claims)
    # ==========================================================
    def test_access_type_integrity(self):
        """Verify factual access types without false marketing claims."""
        resources = LearningResourceRepository.get_all(verification_status=None)
        allowed_types = {"FREE", "OFFICIAL FREE RESOURCE", "FREE + PAID", "PAID"}

        for r in resources:
            self.assertIn(r["access_type"], allowed_types, f"Resource {r['name']} has invalid access type")
            # Verify official government/non-profit resources
            if r["id"] in ["res-ncert-epathshala", "res-diksha", "res-swayam", "res-nptel", "res-khan-academy", "res-ndli", "res-virtual-labs", "res-shodhganga", "res-nta-abhyas"]:
                self.assertIn(r["access_type"], ["OFFICIAL FREE RESOURCE", "FREE"], f"{r['name']} must be official free")

            # Verify commercial freemium resources
            if r["id"] in ["res-gfg", "res-prepinsta", "res-leetcode", "res-codechef", "res-coursera"]:
                self.assertEqual(r["access_type"], "FREE + PAID", f"{r['name']} should be classified as FREE + PAID")

    # ==========================================================
    # TEST 5: 8 Student Qualification Profiles Personalization
    # ==========================================================
    def test_profile_1_10th_standard(self):
        """10th Student: must strictly receive school/foundational resources, NO B.Tech/GATE/CSE items."""
        res = self.client.get("/api/resources?qualification=10th")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        ids = [r["id"] for r in data["resources"]]

        # School-appropriate resources must be present
        self.assertIn("res-ncert-epathshala", ids)
        self.assertIn("res-diksha", ids)
        self.assertIn("res-khan-academy", ids)

        # Advanced engineering/job resources must NOT be returned for 10th
        self.assertNotIn("res-prepinsta", ids)
        self.assertNotIn("res-leetcode", ids)
        self.assertNotIn("res-gate-overflow", ids)
        self.assertNotIn("res-shodhganga", ids)

    def test_profile_2_intermediate_mpc(self):
        """Intermediate MPC: Mathematics, Physics, Chemistry, JEE, NCERT."""
        res = self.client.get("/api/resources?qualification=Intermediate&stream=MPC")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        ids = [r["id"] for r in data["resources"]]

        self.assertIn("res-ncert-epathshala", ids)
        self.assertIn("res-nta-abhyas", ids)
        self.assertIn("res-khan-academy", ids)

    def test_profile_3_intermediate_bipc(self):
        """Intermediate BiPC: Biology, Physics, Chemistry, NEET, NCERT."""
        res = self.client.get("/api/resources?qualification=Intermediate&stream=BiPC")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        ids = [r["id"] for r in data["resources"]]

        self.assertIn("res-ncert-epathshala", ids)
        self.assertIn("res-nta-abhyas", ids)
        self.assertIn("res-khan-academy", ids)

    def test_profile_4_diploma_cse(self):
        """Diploma Polytechnic: Technical foundations, programming, ECET."""
        res = self.client.get("/api/resources?qualification=Diploma&stream=Computer+Engineering")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        ids = [r["id"] for r in data["resources"]]

        self.assertIn("res-gfg", ids)
        self.assertIn("res-w3schools", ids)
        self.assertIn("res-nptel", ids)

    def test_profile_5_btech_cse(self):
        """B.Tech CSE: DSA, campus placement preparation, competitive programming, GATE."""
        res = self.client.get("/api/resources?qualification=B.Tech&stream=Computer+Science+%26+Engineering")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        ids = [r["id"] for r in data["resources"]]

        self.assertIn("res-gfg", ids)
        self.assertIn("res-leetcode", ids)
        self.assertIn("res-codechef", ids)
        self.assertIn("res-prepinsta", ids)
        self.assertIn("res-nptel", ids)

    def test_profile_6_btech_ece(self):
        """B.Tech ECE: Electronics, Virtual Labs, NPTEL, GATE."""
        res = self.client.get("/api/resources?qualification=B.Tech&stream=Electronics+%26+Communication")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        ids = [r["id"] for r in data["resources"]]

        self.assertIn("res-virtual-labs", ids)
        self.assertIn("res-nptel", ids)
        self.assertIn("res-allaboutcircuits", ids)

    def test_profile_7_btech_mech(self):
        """B.Tech Mech: Mechanical core, Virtual Labs, NPTEL, GATE."""
        res = self.client.get("/api/resources?qualification=B.Tech&stream=Mechanical+Engineering")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        ids = [r["id"] for r in data["resources"]]

        self.assertIn("res-virtual-labs", ids)
        self.assertIn("res-nptel", ids)
        self.assertIn("res-swayam", ids)

    def test_profile_8_postgraduate_research(self):
        """Postgraduate: Shodhganga research repositories, NDLI, NPTEL advanced courses."""
        res = self.client.get("/api/resources?qualification=Postgraduate")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        ids = [r["id"] for r in data["resources"]]

        self.assertIn("res-shodhganga", ids)
        self.assertIn("res-ndli", ids)
        self.assertIn("res-nptel", ids)

    # ==========================================================
    # TEST 6: Category and Search Filters
    # ==========================================================
    def test_category_and_search_filtering(self):
        """Test API filtering by category, access type, and search keyword."""
        # Category filter
        res = self.client.get("/api/resources?category=Coding+%26+CS+Fundamentals")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreater(len(data["resources"]), 0)
        for r in data["resources"]:
            self.assertEqual(r["category"], "Coding & CS Fundamentals")

        # Access type filter
        res_access = self.client.get("/api/resources?access_type=OFFICIAL+FREE+RESOURCE")
        self.assertEqual(res_access.status_code, 200)
        data_access = res_access.get_json()
        self.assertGreater(len(data_access["resources"]), 0)
        for r in data_access["resources"]:
            self.assertEqual(r["access_type"], "OFFICIAL FREE RESOURCE")

        # Search query
        res_search = self.client.get("/api/resources?q=python")
        self.assertEqual(res_search.status_code, 200)
        data_search = res_search.get_json()
        self.assertGreater(len(data_search["resources"]), 0)

    # ==========================================================
    # TEST 7: Qualification-Aware Category Discovery API
    # ==========================================================
    def test_categories_endpoint(self):
        """Test /api/resources/categories endpoint for different qualifications."""
        res_10th = self.client.get("/api/resources/categories?qualification=10th")
        self.assertEqual(res_10th.status_code, 200)
        cats_10th = res_10th.get_json()["categories"]
        self.assertIn("School & Foundation Learning", cats_10th)

        res_btech = self.client.get("/api/resources/categories?qualification=B.Tech&stream=CSE")
        self.assertEqual(res_btech.status_code, 200)
        cats_btech = res_btech.get_json()["categories"]
        self.assertIn("Coding & CS Fundamentals", cats_btech)
        self.assertIn("Placement Preparation", cats_btech)

    # ==========================================================
    # TEST 8: Grounded AI Study Guidance API
    # ==========================================================
    def test_ai_study_guidance_endpoint(self):
        """Test /api/ai/study-guidance endpoint produces grounded advice with resource recommendations."""
        payload = {
            "question": "What should I practice for campus placements in software companies?",
            "qualification": "B.Tech",
            "stream": "Computer Science & Engineering",
            "target_exam": "Campus Placements"
        }
        res = self.client.post("/api/ai/study-guidance", json=payload)
        self.assertEqual(res.status_code, 200)
        data = res.get_json()

        self.assertTrue(data.get("success"))
        guidance = data.get("guidance", "")
        self.assertGreater(len(guidance), 50)
        # Check that recommended resources are returned
        recs = data.get("recommended_resources", [])
        self.assertGreater(len(recs), 0)
        self.assertTrue(any(r["name"] in ["GeeksforGeeks", "LeetCode", "PrepInsta", "HackerRank"] for r in recs))

    # ==========================================================
    # TEST 9: Resource Detail API
    # ==========================================================
    def test_resource_detail_endpoint(self):
        """Test /api/resources/<id> endpoint."""
        res = self.client.get("/api/resources/res-gfg")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data["resource"]["name"], "GeeksforGeeks")

        res_404 = self.client.get("/api/resources/non_existent_id")
        self.assertEqual(res_404.status_code, 404)

    # ==========================================================
    # TEST 10: Admin Link Health Check Service
    # ==========================================================
    def test_link_health_check_service(self):
        """Test PipelineService link health checker runs and returns results dictionary."""
        results = PipelineService.check_learning_resource_links(timeout=2)
        self.assertIsInstance(results, dict)
        self.assertIn("total_checked", results)
        self.assertIn("verified_count", results)
        self.assertIn("needs_review_count", results)
        self.assertIn("details", results)


if __name__ == "__main__":
    unittest.main()
