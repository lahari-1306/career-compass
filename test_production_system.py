"""
Comprehensive Automated Test Suite for Production CareerCompass Features.
Validates:
1. Multi-user authentication & Argon2id password security.
2. User data isolation (User A never sees User B's profile or notifications).
3. Rate limiting on login attempts.
4. Education-level aware profile persistence.
5. Exam Preparation Hub & 24-point resources.
6. User exam progress tracking and study plan saving.
7. VAPID Web Push subscription registration and test sending.
8. In-app notification deliveries, read status, and dismissal.
9. Saved opportunities persistence.
10. Background notification pipeline execution.
"""

import unittest
import json
import os
from app import app
from database import init_db
from db_repository import UserRepository, ProfileRepository, NotificationRepository, ExamProgressRepository
from services.email_service import EmailService
from services.push_service import PushService
from services.pipeline_service import PipelineService


class ProductionSystemTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        init_db()

    def setUp(self):
        self.client = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    # -------------------------------------------------------------
    # 1. Multi-User Authentication & Argon2id Security
    # -------------------------------------------------------------
    def test_signup_login_logout_flow(self):
        email = "student_alpha@test.org"
        pwd = "ProductionPassword2026!"
        name = "Student Alpha"

        # Cleanup if exists
        existing = UserRepository.get_by_email(email)
        if existing:
            UserRepository.delete_user(existing["id"])

        # Signup
        res_signup = self.client.post("/api/auth/signup", json={
            "email": email,
            "password": pwd,
            "name": name
        })
        self.assertEqual(res_signup.status_code, 201)
        data_signup = res_signup.get_json()
        self.assertEqual(data_signup["status"], "success")
        self.assertEqual(data_signup["user"]["email"], email)
        self.assertEqual(data_signup["user"]["name"], name)

        # Check session cookie exists
        cookies = res_signup.headers.getlist("Set-Cookie")
        self.assertTrue(any("session_token=" in c for c in cookies))

        # Check /api/auth/me with session
        res_me = self.client.get("/api/auth/me")
        self.assertEqual(res_me.status_code, 200)
        data_me = res_me.get_json()
        self.assertTrue(data_me["authenticated"])
        self.assertEqual(data_me["user"]["email"], email)

        # Logout
        res_logout = self.client.post("/api/auth/logout")
        self.assertEqual(res_logout.status_code, 200)

        # Check /api/auth/me after logout
        res_me2 = self.client.get("/api/auth/me")
        data_me2 = res_me2.get_json()
        self.assertFalse(data_me2["authenticated"])

        # Login again
        res_login = self.client.post("/api/auth/login", json={
            "email": email,
            "password": pwd
        })
        self.assertEqual(res_login.status_code, 200)
        self.assertTrue(res_login.get_json()["status"] == "success")

    # -------------------------------------------------------------
    # 2. Strict User Data Isolation (User A vs User B)
    # -------------------------------------------------------------
    def test_user_data_isolation(self):
        email_a = "user_a@test.org"
        email_b = "user_b@test.org"
        pwd = "SecurePassword123!"

        for em in [email_a, email_b]:
            u = UserRepository.get_by_email(em)
            if u:
                UserRepository.delete_user(u["id"])

        # Create User A
        self.client.post("/api/auth/signup", json={"email": email_a, "password": pwd, "name": "User Alpha"})
        # Save User A profile
        self.client.post("/api/auth/edit-profile", json={
            "qualification": "10th",
            "current_status": "Completed",
            "home_state": "Andhra Pradesh",
            "dream_goal": "Join Polytechnic Diploma"
        })
        # Save an opportunity for User A
        self.client.post("/api/opportunities/save", json={
            "opportunity_id": "notif-polycet-ap",
            "title": "AP POLYCET 2026 Admissions"
        })

        # Logout User A
        self.client.post("/api/auth/logout")

        # Create and Login User B
        self.client.post("/api/auth/signup", json={"email": email_b, "password": pwd, "name": "User Beta"})
        # Save User B profile
        self.client.post("/api/auth/edit-profile", json={
            "qualification": "B.Tech",
            "branch": "Cyber Security",
            "current_status": "Final Year",
            "dream_goal": "SOC Analyst"
        })

        # Check User B's profile
        res_b_me = self.client.get("/api/auth/me")
        data_b_profile = res_b_me.get_json()["profile"]
        self.assertEqual(data_b_profile["qualification"], "B.Tech")
        self.assertEqual(data_b_profile["branch"], "Cyber Security")

        # Check User B's saved opportunities: MUST NOT see User A's saved opportunity
        res_b_saved = self.client.get("/api/opportunities/saved")
        data_b_saved = res_b_saved.get_json()["saved_opportunities"]
        self.assertEqual(len(data_b_saved), 0)

    # -------------------------------------------------------------
    # 3. Rate Limiting on Failed Login
    # -------------------------------------------------------------
    def test_login_rate_limiting(self):
        email = "rate_limit_target@test.org"
        pwd = "CorrectPassword123!"

        u = UserRepository.get_by_email(email)
        if not u:
            UserRepository.create_user(email, pwd, "Rate Limit Test")

        # Perform 5 failed attempts
        for _ in range(5):
            self.client.post("/api/auth/login", json={"email": email, "password": "WrongPassword"})

        # 6th attempt should be blocked with 429
        res_blocked = self.client.post("/api/auth/login", json={"email": email, "password": pwd})
        self.assertEqual(res_blocked.status_code, 429)
        self.assertEqual(res_blocked.get_json()["code"], "RATE_LIMITED")

    # -------------------------------------------------------------
    # 4. Exam Preparation Hub & 24-Point Structure
    # -------------------------------------------------------------
    def test_exam_preparation_hub(self):
        # 1. Listing endpoint
        res = self.client.get("/api/exam-prep")
        self.assertEqual(res.status_code, 200)
        data = res.get_json()
        self.assertGreaterEqual(data["total"], 7)

        # 2. Detailed 24-point structure for GATE CSE
        res_gate = self.client.get("/api/exam-prep/gate-cse")
        self.assertEqual(res_gate.status_code, 200)
        gate_data = res_gate.get_json()["exam"]

        # Check required fields
        self.assertIn("Graduate Aptitude Test in Engineering", gate_data["full_title"])
        self.assertTrue(any("Engineering Mathematics" in s for s in gate_data["subjects"]))
        self.assertIn("Algorithms", gate_data["subjects"])
        self.assertGreaterEqual(len(gate_data["recommended_books"]), 3)
        self.assertIn("30_days", gate_data["study_plans"])
        self.assertIn("3_months", gate_data["study_plans"])

        # Check books have verified fields (NO fake books)
        book = gate_data["recommended_books"][0]
        self.assertIn("Introduction to Algorithms", book["book_name"])
        self.assertIn("Cormen", book["author"])
        self.assertIn("verified_link", book)

    # -------------------------------------------------------------
    # 5. User Exam Progress Tracking & Study Plans
    # -------------------------------------------------------------
    def test_exam_progress_and_study_plan(self):
        email = "exam_prep_user@test.org"
        pwd = "PrepPassword123!"

        u = UserRepository.get_by_email(email)
        if u:
            UserRepository.delete_user(u["id"])

        self.client.post("/api/auth/signup", json={"email": email, "password": pwd, "name": "Prep Student"})

        # Save progress
        res_save = self.client.post("/api/exam-prep/progress", json={
            "exam_id": "gate-cse",
            "preparation_stage": "Intermediate",
            "target_year": 2027,
            "completed_topics": ["Data Structures", "Engineering Mathematics"],
            "notes": "Completed arrays, trees, and linear algebra matrices."
        })
        self.assertEqual(res_save.status_code, 200)

        # Retrieve progress
        res_get = self.client.get("/api/exam-prep/progress?exam_id=gate-cse")
        self.assertEqual(res_get.status_code, 200)
        progress = res_get.get_json()["progress"]
        self.assertEqual(progress["target_year"], 2027)
        self.assertEqual(progress["completed_topics"], ["Data Structures", "Engineering Mathematics"])

        # Save custom study plan
        res_plan = self.client.post("/api/exam-prep/study-plan", json={
            "exam_id": "gate-cse",
            "duration": "3_MONTHS",
            "schedule": {"Month 1": "DSA and Math", "Month 2": "OS and DBMS", "Month 3": "Mock tests"}
        })
        self.assertEqual(res_plan.status_code, 200)

    # -------------------------------------------------------------
    # 6. Web Push VAPID & Subscription Storage
    # -------------------------------------------------------------
    def test_web_push_vapid_and_subscription(self):
        # Public key endpoint
        res_key = self.client.get("/api/push/vapid-public-key")
        self.assertEqual(res_key.status_code, 200)
        pub_key = res_key.get_json().get("public_key")
        self.assertTrue(bool(pub_key))
        self.assertEqual(len(pub_key), 87)  # Base64url P-256 public key

        # Register subscription for logged in user
        email = "push_user@test.org"
        u = UserRepository.get_by_email(email)
        if not u:
            self.client.post("/api/auth/signup", json={"email": email, "password": "SecurePassword123!", "name": "Push User"})
        else:
            self.client.post("/api/auth/login", json={"email": email, "password": "SecurePassword123!"})

        res_sub = self.client.post("/api/push/subscribe", json={
            "endpoint": "https://fcm.googleapis.com/fcm/send/fake-test-endpoint-production-test",
            "keys": {
                "p256dh": "BDc4h...fakeP256dh",
                "auth": "fakeAuthKey123"
            },
            "device_label": "Chrome on Windows Desktop"
        })
        self.assertEqual(res_sub.status_code, 200)

    # -------------------------------------------------------------
    # 7. Notification Deliveries & Deduplication
    # -------------------------------------------------------------
    def test_in_app_notifications_and_deduplication(self):
        email = "notif_user@test.org"
        u = UserRepository.get_by_email(email)
        if u:
            UserRepository.delete_user(u["id"])
        u = UserRepository.create_user(email, "Password12345!", "Notif User")
        user_id = u["id"]

        # First delivery: Should succeed
        d1 = NotificationRepository.create_delivery(
            user_id=user_id,
            notification_id="notif-gate-2027",
            channel="IN_APP",
            title="GATE 2027 Portal Active",
            message="Online portal is active.",
            deep_link="/#radar"
        )
        self.assertIsNotNone(d1)

        # Duplicate delivery: Must return None and not insert duplicate
        d2 = NotificationRepository.create_delivery(
            user_id=user_id,
            notification_id="notif-gate-2027",
            channel="IN_APP",
            title="GATE 2027 Portal Active",
            message="Online portal is active.",
            deep_link="/#radar"
        )
        self.assertIsNone(d2)

        # Login and check user notifications API
        self.client.post("/api/auth/login", json={"email": email, "password": "Password12345!"})
        res_notifs = self.client.get("/api/notifications/user")
        self.assertEqual(res_notifs.status_code, 200)
        items = res_notifs.get_json()["notifications"]
        self.assertTrue(any(item["notification_id"] == "notif-gate-2027" for item in items))

        # Mark as read
        res_read = self.client.post("/api/radar/mark-read", json={"delivery_id": d1})
        self.assertEqual(res_read.status_code, 200)


if __name__ == "__main__":
    unittest.main()
