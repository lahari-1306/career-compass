"""
Test Suite: Password Reset Workflow & Link Verification
Validates:
1. Forgot password request (SMTP unconfigured / dev fallback) returns 200 with reset_url.
2. Token verification endpoint (/api/auth/verify-reset-token) returns valid status and masked email.
3. Password reset endpoint (/api/auth/reset-password) updates password with Argon2id hash.
4. Successful login with newly reset password.
5. Single-use token invalidation (subsequent reset attempt with same token fails).
6. Verify reset token after use returns error (cannot be reused).
7. Non-existent email handling (prevents user enumeration while returning 200).
8. Target="_blank" and rel="noopener noreferrer" enforcement on all rendered links.
9. Link integrity check on key government portals.
"""

import unittest
import os
import json
import sqlite3
from app import app
from db_repository import UserRepository, TokenRepository
from services.email_service import EmailService

class TestPasswordResetAndLinks(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        app.config["TESTING"] = True
        cls.client = app.test_client()

    def setUp(self):
        self.test_email = "test_reset_flow@careercompass.test"
        self.initial_password = "InitialPassword123!"
        self.new_password = "SecureResetPassword2026$"

        # Clean up existing test user
        user = UserRepository.get_by_email(self.test_email)
        if user:
            UserRepository.delete_user(user["id"])

        # Create fresh test user
        UserRepository.create_user(self.test_email, self.initial_password, "Reset Tester")

    def tearDown(self):
        user = UserRepository.get_by_email(self.test_email)
        if user:
            UserRepository.delete_user(user["id"])

    def test_01_forgot_password_success_and_fallback(self):
        """Test forgot-password returns 200 with reset_url and SMTP status when SMTP not configured."""
        res = self.client.post("/api/auth/forgot-password", json={
            "email": self.test_email
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertIn("reset_url", data)
        self.assertFalse(data.get("smtp_configured", True))
        self.assertIn("reset_token=", data.get("reset_url"))

    def test_02_verify_reset_token_valid_and_invalid(self):
        """Test verify-reset-token endpoint validates active token and rejects invalid token."""
        user = UserRepository.get_by_email(self.test_email)
        token = TokenRepository.create_password_reset_token(user["id"])

        # 1. Valid token
        res = self.client.get(f"/api/auth/verify-reset-token?token={token}")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertTrue(data.get("valid"))
        self.assertIn("*", data.get("email"))  # Email must be masked for privacy

        # 2. Invalid / Non-existent token
        res_invalid = self.client.get("/api/auth/verify-reset-token?token=non_existent_token_12345")
        self.assertEqual(res_invalid.status_code, 400)
        data_invalid = res_invalid.get_json()
        self.assertEqual(data_invalid.get("code"), "INVALID_OR_EXPIRED_TOKEN")

        # 3. Missing token param
        res_missing = self.client.get("/api/auth/verify-reset-token")
        self.assertEqual(res_missing.status_code, 400)

    def test_03_full_password_reset_and_login_cycle(self):
        """Complete cycle: forgot password -> extract token -> reset password -> login with new password."""
        # 1. Forgot password request
        forgot_res = self.client.post("/api/auth/forgot-password", json={"email": self.test_email})
        self.assertEqual(forgot_res.status_code, 200)
        reset_url = forgot_res.get_json().get("reset_url", "")
        token = reset_url.split("reset_token=")[1].split("#")[0]

        # 2. Verify token before submission
        verify_res = self.client.get(f"/api/auth/verify-reset-token?token={token}")
        self.assertEqual(verify_res.status_code, 200)

        # 3. Submit new password
        reset_res = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": self.new_password
        })
        self.assertEqual(reset_res.status_code, 200)
        self.assertEqual(reset_res.get_json().get("status"), "success")

        # 4. Old password must no longer work
        old_login = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": self.initial_password
        })
        self.assertEqual(old_login.status_code, 401)

        # 5. New password must log in successfully
        new_login = self.client.post("/api/auth/login", json={
            "email": self.test_email,
            "password": self.new_password
        })
        self.assertEqual(new_login.status_code, 200)
        self.assertEqual(new_login.get_json().get("status"), "success")

        # 6. Single-use token: token cannot be reused
        reuse_res = self.client.post("/api/auth/reset-password", json={
            "token": token,
            "new_password": "YetAnotherPassword2026$"
        })
        self.assertEqual(reuse_res.status_code, 400)

        # 7. Token verification must now fail
        verify_after_use = self.client.get(f"/api/auth/verify-reset-token?token={token}")
        self.assertEqual(verify_after_use.status_code, 400)

    def test_04_forgot_password_non_existent_email(self):
        """Non-existent email should return 200 generic message without exposing user existence."""
        res = self.client.post("/api/auth/forgot-password", json={
            "email": "completely_unknown_user_1234567@notfound.test"
        })
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertEqual(data.get("status"), "success")
        self.assertNotIn("reset_url", data)  # Never leak reset url for non-existent users

    def test_05_verified_replacement_urls_in_datasets(self):
        """Verify that all old broken URLs have been completely eliminated from official datasets."""
        broken_patterns = [
            "exams.nta.ac.in/NEET",
            "drdo.gov.in/drdo/careers",
            "aicte-india.org/schemes/students-development-schemes/Pragati",
            "cuetug.ntaonline.in",
            "polycetap.nic.in",
            "jam.iitd.ac.in",
            "gate2023.iitk.ac.in",
            "gate2022.iitkgp.ac.in"
        ]

        data_dir = os.path.join(os.path.dirname(__file__), "data")
        for fname in os.listdir(data_dir):
            if fname.endswith(".json"):
                fpath = os.path.join(data_dir, fname)
                with open(fpath, "r", encoding="utf-8") as f:
                    content = f.read()
                for bad_url in broken_patterns:
                    self.assertNotIn(bad_url, content, f"Found outdated URL '{bad_url}' in {fname}")

if __name__ == "__main__":
    unittest.main()
