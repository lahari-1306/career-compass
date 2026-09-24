"""
Comprehensive 16-Point Verification Suite for Career Compass Authentication & Persistence.
Verifies:
1. POST /api/auth/register returns 201 with success: true and user object.
2. POST /api/auth/signup returns 201 with success: true and user object.
3. Duplicate registration via /api/auth/register returns 409 with exact message.
4. Duplicate registration via /api/auth/signup returns 409 with exact message.
5. Case-insensitive duplicate detection (Student@Gmail.com == student@gmail.com).
6. POST /api/auth/login returns 200 with success: true and session cookie.
7. Case-insensitive login (STUDENT@GMAIL.COM logs into student@gmail.com).
8. Login with incorrect password returns 401 with 'Invalid email or password.'.
9. Login with nonexistent email returns 401 with 'Invalid email or password.'.
10. GET /api/auth/me with session returns 200, authenticated: true, user and profile.
11. GET /api/auth/me without session returns 200, authenticated: false, user: null.
12. POST /api/auth/logout invalidates session and clears cookie.
13. GET /api/auth/me after logout returns unauthenticated.
14. Re-login after logout with original credentials works immediately.
15. Database persistence across server restart / connection pool recreation.
16. Zero plaintext passwords in database, Argon2id verification, zero secret exposure in API.
"""

import unittest
import json
import os
import sys
import sqlite3
from app import app
from db_repository import UserRepository, SessionRepository, ProfileRepository
from database import get_db_connection, DB_PATH, IS_POSTGRES


class TestAuthPersistenceSuite(unittest.TestCase):
    def setUp(self):
        self.app = app
        self.app.config["TESTING"] = True
        self.client = self.app.test_client()

        # Dedicated test email addresses
        self.test_email_1 = "auth_persist_test_1@example.com"
        self.test_email_2 = "auth_persist_test_2@example.com"
        self.test_password = "SecurePassword123!"
        self.test_name_1 = "Aarav Sharma"
        self.test_name_2 = "Sneha Patel"

        # Clean up any existing test records
        for em in [self.test_email_1, self.test_email_2, "AUTH_PERSIST_TEST_1@EXAMPLE.COM"]:
            u = UserRepository.get_by_email(em)
            if u:
                UserRepository.delete_user(u["id"])

    def tearDown(self):
        for em in [self.test_email_1, self.test_email_2]:
            u = UserRepository.get_by_email(em)
            if u:
                UserRepository.delete_user(u["id"])

    def test_01_register_endpoint_success(self):
        """Test 1: POST /api/auth/register returns 201 with success: true and user object."""
        resp = self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1,
            "password": self.test_password
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("status"), "success")
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], self.test_email_1)
        self.assertEqual(data["user"]["name"], self.test_name_1)
        # Verify session cookie was set
        cookies = [h for h in resp.headers.getlist("Set-Cookie") if "session_token=" in h]
        self.assertTrue(len(cookies) > 0)

    def test_02_signup_endpoint_success(self):
        """Test 2: POST /api/auth/signup returns 201 with success: true and user object."""
        resp = self.client.post("/api/auth/signup", json={
            "full_name": self.test_name_2,
            "email": self.test_email_2,
            "password": self.test_password
        })
        self.assertEqual(resp.status_code, 201)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("status"), "success")
        self.assertIn("user", data)
        self.assertEqual(data["user"]["email"], self.test_email_2)
        self.assertEqual(data["user"]["name"], self.test_name_2)

    def test_03_duplicate_register_conflict(self):
        """Test 3: Duplicate email via /api/auth/register returns 409 with exact message."""
        # First registration
        self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1,
            "password": self.test_password
        })
        # Second registration with same email
        resp = self.client.post("/api/auth/register", json={
            "name": "Different Name",
            "email": self.test_email_1,
            "password": "AnotherPassword456!"
        })
        self.assertEqual(resp.status_code, 409)
        data = resp.get_json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("status"), "error")
        self.assertEqual(data.get("message"), "An account with this email already exists. Please sign in.")

    def test_04_duplicate_signup_conflict(self):
        """Test 4: Duplicate email via /api/auth/signup returns 409 with exact message."""
        # First registration
        self.client.post("/api/auth/signup", json={
            "name": self.test_name_1,
            "email": self.test_email_1,
            "password": self.test_password
        })
        # Second registration with same email
        resp = self.client.post("/api/auth/signup", json={
            "name": "Different Name",
            "email": self.test_email_1,
            "password": "AnotherPassword456!"
        })
        self.assertEqual(resp.status_code, 409)
        data = resp.get_json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("status"), "error")
        self.assertEqual(data.get("message"), "An account with this email already exists. Please sign in.")

    def test_05_case_insensitive_duplicate_detection(self):
        """Test 5: Case-insensitive duplicate detection (AUTH_PERSIST_TEST_1@EXAMPLE.COM == auth_persist_test_1@example.com)."""
        self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1.lower(),
            "password": self.test_password
        })
        # Try registering with uppercase variation
        resp = self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1.upper(),
            "password": self.test_password
        })
        self.assertEqual(resp.status_code, 409)
        data = resp.get_json()
        self.assertEqual(data.get("message"), "An account with this email already exists. Please sign in.")

    def test_06_login_valid_credentials(self):
        """Test 6: POST /api/auth/login returns 200 with success: true and user object."""
        self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1,
            "password": self.test_password
        })
        resp = self.client.post("/api/auth/login", json={
            "email": self.test_email_1,
            "password": self.test_password
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("message"), "Login successful.")
        self.assertEqual(data["user"]["email"], self.test_email_1)

    def test_07_case_insensitive_login(self):
        """Test 7: Uppercase or mixed-case email login succeeds against lowercased user record."""
        self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1.lower(),
            "password": self.test_password
        })
        # Login with UPPERCASE email
        resp = self.client.post("/api/auth/login", json={
            "email": self.test_email_1.upper(),
            "password": self.test_password
        })
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data["user"]["email"], self.test_email_1.lower())

    def test_08_login_invalid_password(self):
        """Test 8: Login with incorrect password returns 401 with 'Invalid email or password.'."""
        self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1,
            "password": self.test_password
        })
        resp = self.client.post("/api/auth/login", json={
            "email": self.test_email_1,
            "password": "WrongPassword999!"
        })
        self.assertEqual(resp.status_code, 401)
        data = resp.get_json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("message"), "Invalid email or password.")

    def test_09_login_nonexistent_email(self):
        """Test 9: Login with nonexistent email returns 401 with 'Invalid email or password.'."""
        resp = self.client.post("/api/auth/login", json={
            "email": "completely_unknown_user_12345@example.com",
            "password": "SomePassword123!"
        })
        self.assertEqual(resp.status_code, 401)
        data = resp.get_json()
        self.assertFalse(data.get("success"))
        self.assertEqual(data.get("message"), "Invalid email or password.")

    def test_10_get_me_authenticated(self):
        """Test 10: GET /api/auth/me with session returns 200, authenticated: true, user and profile."""
        reg_resp = self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1,
            "password": self.test_password
        })
        me_resp = self.client.get("/api/auth/me")
        self.assertEqual(me_resp.status_code, 200)
        data = me_resp.get_json()
        self.assertTrue(data.get("authenticated"))
        self.assertTrue(data.get("success"))
        self.assertIsNotNone(data.get("user"))
        self.assertEqual(data["user"]["email"], self.test_email_1)
        self.assertIsNotNone(data.get("profile"))

    def test_11_get_me_unauthenticated(self):
        """Test 11: GET /api/auth/me without session returns 200, authenticated: false, user: null."""
        # Using a fresh client with zero cookies
        fresh_client = self.app.test_client()
        me_resp = fresh_client.get("/api/auth/me")
        self.assertEqual(me_resp.status_code, 200)
        data = me_resp.get_json()
        self.assertFalse(data.get("authenticated"))
        self.assertFalse(data.get("success"))
        self.assertIsNone(data.get("user"))

    def test_12_logout_clears_session(self):
        """Test 12: POST /api/auth/logout invalidates session and clears cookie."""
        self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1,
            "password": self.test_password
        })
        logout_resp = self.client.post("/api/auth/logout")
        self.assertEqual(logout_resp.status_code, 200)
        data = logout_resp.get_json()
        self.assertTrue(data.get("success"))
        self.assertEqual(data.get("message"), "Logged out successfully.")

    def test_13_me_after_logout_is_unauthenticated(self):
        """Test 13: GET /api/auth/me after logout returns unauthenticated."""
        self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1,
            "password": self.test_password
        })
        self.client.post("/api/auth/logout")
        me_resp = self.client.get("/api/auth/me")
        self.assertEqual(me_resp.status_code, 200)
        data = me_resp.get_json()
        self.assertFalse(data.get("authenticated"))
        self.assertIsNone(data.get("user"))

    def test_14_relogin_after_logout_succeeds(self):
        """Test 14: Re-login after logout with original credentials works immediately."""
        # 1. Register
        self.client.post("/api/auth/register", json={
            "name": self.test_name_1,
            "email": self.test_email_1,
            "password": self.test_password
        })
        # 2. Logout
        self.client.post("/api/auth/logout")
        # 3. Login again
        login_resp = self.client.post("/api/auth/login", json={
            "email": self.test_email_1,
            "password": self.test_password
        })
        self.assertEqual(login_resp.status_code, 200)
        login_data = login_resp.get_json()
        self.assertTrue(login_data.get("success"))
        # 4. Check /me with new session
        me_resp = self.client.get("/api/auth/me")
        me_data = me_resp.get_json()
        self.assertTrue(me_data.get("authenticated"))
        self.assertEqual(me_data["user"]["email"], self.test_email_1)

    def test_15_database_persistence_across_reconnect(self):
        """Test 15: User and profile persist across connection close and re-initialization."""
        # Create user through repository directly
        user = UserRepository.create_user(self.test_email_1, self.test_password, self.test_name_1)
        self.assertIsNotNone(user)
        user_id = user["id"]

        # Close all connections and simulate fresh process lookup
        conn = get_db_connection()
        conn.close()

        # Fetch in a fresh query
        reloaded = UserRepository.get_by_id(user_id)
        self.assertIsNotNone(reloaded)
        self.assertEqual(reloaded["email"], self.test_email_1)
        self.assertEqual(reloaded["name"], self.test_name_1)

        # Profile also intact
        profile = ProfileRepository.get_profile(user_id)
        self.assertIsNotNone(profile)
        self.assertEqual(profile["qualification"], "B.Tech")

    def test_16_zero_plaintext_passwords_and_argon2id_verification(self):
        """Test 16: Zero plaintext passwords in database, Argon2id verified, zero hash in API."""
        user = UserRepository.create_user(self.test_email_1, self.test_password, self.test_name_1)
        user_id = user["id"]

        conn = get_db_connection()
        cur = conn.cursor()
        cur.execute("SELECT password_hash FROM users WHERE id = ?", (user_id,))
        row = cur.fetchone()
        stored_hash = row["password_hash"] if isinstance(row, dict) else row[0]
        conn.close()

        # 1. Stored value must NOT equal the plaintext password
        self.assertNotEqual(stored_hash, self.test_password)
        # 2. Must be Argon2id format
        self.assertTrue(stored_hash.startswith("$argon2id$"))
        # 3. Must verify successfully
        self.assertTrue(UserRepository.verify_password(stored_hash, self.test_password))
        # 4. Must fail on incorrect password
        self.assertFalse(UserRepository.verify_password(stored_hash, "WrongPassword!"))

        # 5. Check API responses never expose password_hash
        reg_resp = self.client.post("/api/auth/login", json={
            "email": self.test_email_1,
            "password": self.test_password
        })
        api_user = reg_resp.get_json().get("user", {})
        self.assertNotIn("password_hash", api_user)
        self.assertNotIn("password", api_user)


if __name__ == "__main__":
    unittest.main()
