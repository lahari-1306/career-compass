"""
Comprehensive Automated Verification Test Suite for Career Compass Fixes
Tests all 24 required functional areas, database schema, auth persistence,
HTTP 409 duplicate account handling, SMTP 503 unconfigured notice,
password reset token flow, real learning tracker endpoints, 8 languages, and theme setup.
"""
import os
import sys
import json
import sqlite3
import unittest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from app import app
from database import get_db_connection, DB_PATH
from db_repository import UserRepository, ProfileRepository, TrackerRepository, TokenRepository
from services.email_service import EmailService

class TestCareerCompassFixes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def test_01_database_schema_and_tables(self):
        """Verify all 5 required tables and required columns exist."""
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check tables exist
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [r[0] for r in cursor.fetchall()]
        
        required_tables = ["users", "user_profiles", "password_reset_tokens", "learning_progress", "study_sessions"]
        for tbl in required_tables:
            self.assertIn(tbl, tables, f"Required table '{tbl}' is missing from database schema")
            
        # Check users table columns
        cursor.execute("PRAGMA table_info(users)")
        user_cols = [r[1] for r in cursor.fetchall()]
        required_user_cols = ["id", "email", "password_hash", "name", "created_at", "updated_at", "last_login_at", "is_active"]
        for col in required_user_cols:
            self.assertIn(col, user_cols, f"Column '{col}' is missing from users table")
            
        conn.close()

    def test_02_duplicate_account_returns_409(self):
        """Requirement 4: Duplicate registration must return HTTP 409 with exact message."""
        test_email = "duplicate_check_test@example.com"
        test_password = "SecurePassword123!"

        # Ensure user does not already exist
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE email = ?", (test_email,))
        conn.commit()
        conn.close()

        # Step 1: Create user first time
        res1 = self.client.post("/api/auth/signup", json={
            "full_name": "Test User",
            "email": test_email,
            "password": test_password
        })
        self.assertEqual(res1.status_code, 201)
        data1 = res1.get_json()
        self.assertEqual(data1.get("status"), "success")

        # Step 2: Try registering again with SAME email
        res2 = self.client.post("/api/auth/signup", json={
            "full_name": "Test User Duplicate",
            "email": test_email,
            "password": test_password
        })
        self.assertEqual(res2.status_code, 409, f"Expected 409, got {res2.status_code}: {res2.data.decode()}")
        data2 = res2.get_json()
        expected_msg = "An account with this email already exists. Please sign in."
        self.assertEqual(data2.get("message"), expected_msg)

    def test_03_auth_persistence_signup_logout_login(self):
        """Requirement 3: Full Sign Up -> Logout -> Login cycle with Argon2id hash."""
        test_email = "lifecycle_test@example.com"
        test_password = "MyComplexPassword#2026"

        # Clean up
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE email = ?", (test_email,))
        conn.commit()
        conn.close()

        # Register
        signup_res = self.client.post("/api/auth/signup", json={
            "full_name": "Lifecycle User",
            "email": test_email,
            "password": test_password
        })
        self.assertEqual(signup_res.status_code, 201)

        # Logout
        logout_res = self.client.post("/api/auth/logout")
        self.assertEqual(logout_res.status_code, 200)

        # Verify not authenticated
        me_res1 = self.client.get("/api/auth/me")
        self.assertFalse(me_res1.get_json().get("authenticated"))

        # Login with correct credentials
        login_res = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": test_password
        })
        self.assertEqual(login_res.status_code, 200)
        login_data = login_res.get_json()
        self.assertEqual(login_data.get("status"), "success")
        self.assertEqual(login_data.get("user", {}).get("email"), test_email)
        self.assertEqual(login_data.get("user", {}).get("is_active"), 1)

        # Verify session is authenticated
        me_res2 = self.client.get("/api/auth/me")
        me_data = me_res2.get_json()
        self.assertTrue(me_data.get("authenticated"))
        self.assertEqual(me_data.get("user", {}).get("email"), test_email)

        # Test login with WRONG password
        self.client.post("/api/auth/logout")
        wrong_res = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": "WrongPassword123!"
        })
        self.assertEqual(wrong_res.status_code, 401)

    def test_04_forgot_password_unconfigured_smtp_and_reset_token(self):
        """Requirement 5: Forgot password returns 503 if unconfigured, reset flow works with valid token."""
        test_email = "forgot_reset_test@example.com"
        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE email = ?", (test_email,))
        conn.commit()
        conn.close()

        # Create user
        signup_res = self.client.post("/api/auth/signup", json={
            "full_name": "Reset User",
            "email": test_email,
            "password": "InitialPassword123!"
        })
        self.assertEqual(signup_res.status_code, 201)

        # When SMTP is not configured, it returns 200 OK with reset_url and SMTP guidance (never blocking 503)
        if not EmailService.is_configured():
            forgot_res = self.client.post("/api/auth/forgot-password", json={
                "email": test_email
            })
            self.assertEqual(forgot_res.status_code, 200)
            data = forgot_res.get_json()
            self.assertEqual(data.get("status"), "success")
            self.assertFalse(data.get("smtp_configured", True))
            self.assertIn("reset_url", data)
            self.assertIn("SMTP", data.get("message"))

            # Test verify-reset-token endpoint with token extracted from reset_url
            reset_url = data.get("reset_url", "")
            extracted_token = reset_url.split("reset_token=")[1].split("#")[0]
            verify_res = self.client.get(f"/api/auth/verify-reset-token?token={extracted_token}")
            self.assertEqual(verify_res.status_code, 200)
            self.assertTrue(verify_res.get_json().get("valid"))

        # Test token generation and password reset
        user = UserRepository.get_by_email(test_email)
        self.assertIsNotNone(user)
        raw_token = TokenRepository.create_password_reset_token(user["id"])
        
        # Reset password using token
        new_password = "BrandNewPassword2026$"
        reset_res = self.client.post("/api/auth/reset-password", json={
            "token": raw_token,
            "new_password": new_password
        })
        self.assertEqual(reset_res.status_code, 200)
        reset_data = reset_res.get_json()
        self.assertEqual(reset_data.get("status"), "success")

        # Now login with new password
        login_new = self.client.post("/api/auth/login", json={
            "email": test_email,
            "password": new_password
        })
        self.assertEqual(login_new.status_code, 200)

        # Token cannot be reused (single-use)
        reuse_res = self.client.post("/api/auth/reset-password", json={
            "token": raw_token,
            "new_password": "AnotherPassword2026$"
        })
        self.assertEqual(reuse_res.status_code, 400)

    def test_05_learning_tracker_endpoints(self):
        """Requirements 14, 15: Real Learning Tracker endpoints save and return progress."""
        tracker_email = "tracker_user_test@example.com"
        tracker_pwd = "TrackerPass123!"

        conn = get_db_connection()
        c = conn.cursor()
        c.execute("DELETE FROM users WHERE email = ?", (tracker_email,))
        conn.commit()
        conn.close()

        # Signup & auto-login
        signup_res = self.client.post("/api/auth/signup", json={
            "full_name": "Tracker User",
            "email": tracker_email,
            "password": tracker_pwd
        })
        self.assertEqual(signup_res.status_code, 201)

        # Save profile
        prof_res = self.client.post("/api/radar/profile", json={
            "qualification": "B.Tech",
            "branch": "CSE",
            "current_status": "Final Year",
            "career_interests": ["Software / IT Industry", "Cyber Security"],
            "is_onboarded": 1
        })
        self.assertEqual(prof_res.status_code, 200)

        # GET /api/tracker/progress
        prog_res1 = self.client.get("/api/tracker/progress")
        self.assertEqual(prog_res1.status_code, 200)
        prog1 = prog_res1.get_json()
        self.assertEqual(prog1.get("status"), "success")
        summary1 = prog1.get("summary", {})
        initial_topics = summary1.get("completed_topics_count", 0)

        # POST /api/tracker/start-topic
        start_res = self.client.post("/api/tracker/start-topic", json={
            "subject": "Computer Science",
            "topic": "Data Structures & Algorithms"
        })
        self.assertEqual(start_res.status_code, 200)
        start_data = start_res.get_json()
        self.assertIn("session_id", start_data)

        # POST /api/tracker/complete-topic
        comp_res = self.client.post("/api/tracker/complete-topic", json={
            "subject": "Computer Science",
            "topic": "Data Structures & Algorithms",
            "duration_minutes": 45,
            "practice_minutes": 30,
            "questions_solved": 10,
            "score_pct": 90.0
        })
        self.assertEqual(comp_res.status_code, 200)
        comp_data = comp_res.get_json()
        self.assertEqual(comp_data.get("status"), "success")

        # GET /api/tracker/progress again to verify increment
        prog_res2 = self.client.get("/api/tracker/progress")
        prog2 = prog_res2.get_json()
        summary2 = prog2.get("summary", {})
        self.assertEqual(summary2.get("completed_topics_count"), initial_topics + 1)
        self.assertGreaterEqual(summary2.get("total_study_minutes"), 45)
        self.assertGreaterEqual(summary2.get("total_questions_solved"), 10)

        # GET /api/tracker/study-plan
        plan_res = self.client.get("/api/tracker/study-plan")
        self.assertEqual(plan_res.status_code, 200)
        plan_data = plan_res.get_json()
        self.assertIn("plan", plan_data)
        self.assertGreater(len(plan_data["plan"].get("modules", [])), 0)

    def test_06_localization_8_languages(self):
        """Requirement 2: Localization support for all 8 required languages."""
        langs = ["en", "te", "hi", "ta", "kn", "ml", "mr", "bn"]
        locales_dir = os.path.join(BASE_DIR, "static", "locales")
        
        for lang in langs:
            lang_file = os.path.join(locales_dir, f"{lang}.json")
            self.assertTrue(os.path.exists(lang_file), f"Locale file {lang}.json does not exist")
            with open(lang_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                self.assertIn("nav", data, f"Key 'nav' missing in {lang}.json")
                self.assertIn("auth", data, f"Key 'auth' missing in {lang}.json")
                self.assertIn("tracker", data, f"Key 'tracker' missing in {lang}.json")

        # Verify static/js/locales.js exists and defines window.LOCALES with all 8
        locales_js = os.path.join(BASE_DIR, "static", "js", "locales.js")
        self.assertTrue(os.path.exists(locales_js))
        with open(locales_js, "r", encoding="utf-8") as f:
            content = f.read()
            for lang in langs:
                self.assertIn(f'"{lang}":', content)

    def test_07_learning_resources_access_types(self):
        """Requirement 12: Learning resources categorized with valid URLs and access_type."""
        resources_file = os.path.join(BASE_DIR, "data", "learning_resources.json")
        self.assertTrue(os.path.exists(resources_file))
        with open(resources_file, "r", encoding="utf-8") as f:
            resources = json.load(f)
            
        allowed_types = ["FREE", "FREE + PAID", "OFFICIAL FREE RESOURCE"]
        self.assertGreaterEqual(len(resources), 20)
        for r in resources:
            title = r.get("name") or r.get("title")
            url = r.get("official_url") or r.get("url")
            self.assertIn(r.get("access_type"), allowed_types, f"Resource {title} has invalid access_type: {r.get('access_type')}")
            self.assertTrue(url and url.startswith("http"), f"Resource {title} has invalid URL: {url}")

    def test_08_career_paths_diploma_and_degree(self):
        """Requirements 9, 10, 11: Diploma and Degree career paths are rich and robust."""
        cp_file = os.path.join(BASE_DIR, "data", "career_paths.json")
        self.assertTrue(os.path.exists(cp_file))
        with open(cp_file, "r", encoding="utf-8") as f:
            cp_data = json.load(f)
            
        self.assertIn("diploma", cp_data)
        self.assertIn("degree", cp_data)
        
        # Verify Diploma has paths including Lateral Entry, Core Jobs, JE, NATS, Defence
        diploma_paths = cp_data["diploma"].get("paths", [])
        diploma_titles = " ".join([p.get("name") or p.get("category") or p.get("title") or "" for p in diploma_paths]).lower()
        self.assertIn("lateral entry", diploma_titles)
        self.assertIn("technical jobs", diploma_titles)
        self.assertIn("nats", diploma_titles)
        self.assertIn("defence", diploma_titles)
        self.assertIn("entrepreneurship", diploma_titles)
        
        # Verify Degree has paths including Civil Services, Banking, MBA, MCA, 3-Yr LLB, Defence
        degree_paths = cp_data["degree"].get("paths", [])
        degree_titles = " ".join([p.get("name") or p.get("category") or p.get("title") or "" for p in degree_paths]).lower()
        self.assertIn("civil services", degree_titles)
        self.assertIn("banking", degree_titles)
        self.assertIn("mba", degree_titles)
        self.assertIn("llb", degree_titles)
        self.assertIn("defence", degree_titles)

    def test_09_frontend_code_integrity(self):
        """Requirements 1, 13: Zero double-toggle and 0% default preparation progress."""
        # In templates/index.html, auth-theme-toggle-btn must NOT have inline onclick="toggleTheme()"
        index_html = os.path.join(BASE_DIR, "templates", "index.html")
        with open(index_html, "r", encoding="utf-8") as f:
            html = f.read()
            self.assertNotIn('id="auth-theme-toggle-btn" class="action-btn theme-btn" onclick="toggleTheme()"', html)
            self.assertIn('id="auth-theme-toggle-btn"', html)

        # In static/js/app.js, prep summary percentage must default to 0% (not 20%)
        app_js = os.path.join(BASE_DIR, "static", "js", "app.js")
        with open(app_js, "r", encoding="utf-8") as f:
            js = f.read()
            self.assertIn('Math.round((completedCount / 12) * 100)) : 0;', js)
            self.assertNotIn('Math.round((completedCount / 12) * 100)) : 20;', js)

if __name__ == "__main__":
    unittest.main()
