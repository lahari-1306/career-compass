"""
Data Access Repository for CareerCompass.
Handles all relational queries, user isolation, Argon2id password hashing,
session tokens, and notification tracking with complete parameterization.
"""

import sqlite3
import secrets
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError
from database import get_db_connection, now_ist_iso, IST

ph = PasswordHasher(time_cost=3, memory_cost=65536, parallelism=4)


# ====================================================
# USER & AUTHENTICATION REPOSITORY
# ====================================================

class UserRepository:
    @staticmethod
    def hash_password(password: str) -> str:
        return ph.hash(password)

    @staticmethod
    def verify_password(hash_str: str, password: str) -> bool:
        try:
            return ph.verify(hash_str, password)
        except (VerifyMismatchError, VerificationError):
            return False

    @staticmethod
    def create_user(email: str, password: str, name: str, role: str = "user") -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        pwd_hash = UserRepository.hash_password(password)

        try:
            cursor.execute("""
            INSERT INTO users (email, password_hash, name, role, is_verified, is_active, created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, 1, ?, ?)
            """, (email.strip().lower(), pwd_hash, name.strip(), role, now_str, now_str))
            user_id = cursor.lastrowid

            # Initialize empty education-aware profile (default is_onboarded = 0)
            cursor.execute("""
            INSERT INTO user_profiles (user_id, qualification, current_status, is_onboarded, created_at, updated_at)
            VALUES (?, 'B.Tech', 'Final Year', 0, ?, ?)
            """, (user_id, now_str, now_str))

            # Initialize user preferences
            cursor.execute("""
            INSERT INTO user_preferences (user_id, created_at, updated_at)
            VALUES (?, ?, ?)
            """, (user_id, now_str, now_str))

            # Initialize notification preferences
            cursor.execute("""
            INSERT INTO notification_preferences (user_id, created_at, updated_at)
            VALUES (?, ?, ?)
            """, (user_id, now_str, now_str))

            conn.commit()
            return UserRepository.get_by_id(user_id)
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()

    @staticmethod
    def get_by_id(user_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name, role, is_verified, is_active, created_at, last_login_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip().lower(),))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def update_password(user_id: int, new_password: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        pwd_hash = UserRepository.hash_password(new_password)
        now_str = now_ist_iso()
        cursor.execute("UPDATE users SET password_hash = ?, updated_at = ? WHERE id = ?", (pwd_hash, now_str, user_id))
        # Invalidate active sessions
        cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE user_id = ?", (user_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    @staticmethod
    def update_last_login(user_id: int) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET last_login_at = ? WHERE id = ?", (now_ist_iso(), user_id))
        conn.commit()
        conn.close()

    @staticmethod
    def delete_user(user_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success


# ====================================================
# SESSION REPOSITORY (Secure HttpOnly Cookie Backend)
# ====================================================

class SessionRepository:
    SESSION_DURATION_DAYS = 14

    @staticmethod
    def create_session(user_id: int, ip_address: str = "", user_agent: str = "") -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        token = secrets.token_urlsafe(48)
        now = datetime.now(IST)
        now_str = now.isoformat()
        expires_str = (now + timedelta(days=SessionRepository.SESSION_DURATION_DAYS)).isoformat()

        cursor.execute("""
        INSERT INTO user_sessions (session_token, user_id, ip_address, user_agent, created_at, expires_at, is_active)
        VALUES (?, ?, ?, ?, ?, ?, 1)
        """, (token, user_id, ip_address, user_agent[:255] if user_agent else "", now_str, expires_str))
        conn.commit()
        conn.close()
        return token

    @staticmethod
    def get_user_from_token(token: str) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        cursor.execute("""
        SELECT u.id, u.email, u.name, u.role, u.is_verified, s.expires_at
        FROM user_sessions s
        JOIN users u ON s.user_id = u.id
        WHERE s.session_token = ? AND s.is_active = 1 AND s.expires_at > ?
        """, (token, now_str))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def invalidate_session(token: str) -> None:
        if not token:
            return
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE user_sessions SET is_active = 0 WHERE session_token = ?", (token,))
        conn.commit()
        conn.close()


# ====================================================
# PASSWORD RESET & EMAIL VERIFICATION
# ====================================================

class TokenRepository:
    @staticmethod
    def create_password_reset_token(user_id: int) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        token = secrets.token_urlsafe(32)
        now = datetime.now(IST)
        now_str = now.isoformat()
        expires_str = (now + timedelta(hours=2)).isoformat()

        cursor.execute("""
        INSERT INTO password_reset_tokens (user_id, token, created_at, expires_at)
        VALUES (?, ?, ?, ?)
        """, (user_id, token, now_str, expires_str))
        conn.commit()
        conn.close()
        return token

    @staticmethod
    def verify_reset_token(token: str) -> Optional[Dict[str, Any]]:
        if not token:
            return None
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        cursor.execute("""
        SELECT t.user_id, t.expires_at, u.email, u.name
        FROM password_reset_tokens t
        JOIN users u ON t.user_id = u.id
        WHERE t.token = ? AND t.used_at IS NULL AND t.expires_at > ?
        """, (token, now_str))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def verify_and_use_reset_token(token: str) -> Optional[int]:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        cursor.execute("""
        SELECT user_id FROM password_reset_tokens
        WHERE token = ? AND used_at IS NULL AND expires_at > ?
        """, (token, now_str))
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        user_id = row["user_id"]
        cursor.execute("UPDATE password_reset_tokens SET used_at = ? WHERE token = ?", (now_str, token))
        conn.commit()
        conn.close()
        return user_id


# ====================================================
# USER PROFILE REPOSITORY (EDUCATION-LEVEL AWARE)
# ====================================================

class ProfileRepository:
    @staticmethod
    def get_profile(user_id: int) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_profiles WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        for key in ["career_interests", "selected_exams", "preferred_pathways"]:
            if key in d and isinstance(d[key], str):
                try:
                    d[key] = json.loads(d[key])
                except Exception:
                    d[key] = []
        return d

    @staticmethod
    def save_profile(user_id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()

        # Parse JSON fields
        interests = json.dumps(data.get("career_interests") or [])
        exams = json.dumps(data.get("selected_exams") or [])
        pathways = json.dumps(data.get("preferred_pathways") or [])

        is_onboarded = 1 if data.get("is_onboarded", 1) in (1, "1", True) else 0

        cursor.execute("""
        INSERT INTO user_profiles (
            user_id, qualification, current_status, stream, branch, completion_year,
            home_state, scope, score, age, career_interests, selected_exams, preferred_pathways,
            preferred_language, dream_goal, is_onboarded, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id) DO UPDATE SET
            qualification = excluded.qualification,
            current_status = excluded.current_status,
            stream = excluded.stream,
            branch = excluded.branch,
            completion_year = excluded.completion_year,
            home_state = excluded.home_state,
            scope = excluded.scope,
            score = excluded.score,
            age = excluded.age,
            career_interests = excluded.career_interests,
            selected_exams = excluded.selected_exams,
            preferred_pathways = excluded.preferred_pathways,
            preferred_language = excluded.preferred_language,
            dream_goal = excluded.dream_goal,
            is_onboarded = excluded.is_onboarded,
            updated_at = excluded.updated_at
        """, (
            user_id,
            data.get("qualification", "B.Tech"),
            data.get("current_status", "Final Year"),
            data.get("stream", ""),
            data.get("branch", ""),
            data.get("completion_year"),
            data.get("home_state", "All India / National"),
            data.get("scope", "All India"),
            data.get("score", ""),
            data.get("age"),
            interests,
            exams,
            pathways,
            data.get("preferred_language", "en"),
            data.get("dream_goal", ""),
            is_onboarded,
            now_str,
            now_str
        ))
        conn.commit()
        conn.close()
        return ProfileRepository.get_profile(user_id) or {}


# ====================================================
# PREFERENCES & NOTIFICATION SETTINGS
# ====================================================

class SettingsRepository:
    @staticmethod
    def get_settings(user_id: int) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_preferences WHERE user_id = ?", (user_id,))
        pref_row = cursor.fetchone()
        cursor.execute("SELECT * FROM notification_preferences WHERE user_id = ?", (user_id,))
        notif_row = cursor.fetchone()
        conn.close()

        prefs = dict(pref_row) if pref_row else {}
        notifs = dict(notif_row) if notif_row else {}
        return {"preferences": prefs, "notifications": notifs}

    @staticmethod
    def update_settings(user_id: int, prefs: Dict[str, Any], notifs: Dict[str, Any]) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()

        if prefs:
            cursor.execute("""
            UPDATE user_preferences SET
                theme = COALESCE(?, theme),
                preferred_language = COALESCE(?, preferred_language),
                email_notifications_enabled = COALESCE(?, email_notifications_enabled),
                push_notifications_enabled = COALESCE(?, push_notifications_enabled),
                weekly_digest_enabled = COALESCE(?, weekly_digest_enabled),
                updated_at = ?
            WHERE user_id = ?
            """, (
                prefs.get("theme"),
                prefs.get("preferred_language"),
                prefs.get("email_notifications_enabled"),
                prefs.get("push_notifications_enabled"),
                prefs.get("weekly_digest_enabled"),
                now_str,
                user_id
            ))

        if notifs:
            cursor.execute("""
            UPDATE notification_preferences SET
                new_opportunities = COALESCE(?, new_opportunities),
                deadlines = COALESCE(?, deadlines),
                admit_cards = COALESCE(?, admit_cards),
                results = COALESCE(?, results),
                counselling = COALESCE(?, counselling),
                scholarships = COALESCE(?, scholarships),
                email_channel = COALESCE(?, email_channel),
                push_channel = COALESCE(?, push_channel),
                in_app_channel = COALESCE(?, in_app_channel),
                updated_at = ?
            WHERE user_id = ?
            """, (
                notifs.get("new_opportunities"),
                notifs.get("deadlines"),
                notifs.get("admit_cards"),
                notifs.get("results"),
                notifs.get("counselling"),
                notifs.get("scholarships"),
                notifs.get("email_channel"),
                notifs.get("push_channel"),
                notifs.get("in_app_channel"),
                now_str,
                user_id
            ))
        conn.commit()
        conn.close()


# ====================================================
# NOTIFICATIONS & DELIVERIES (User Isolation)
# ====================================================

class NotificationRepository:
    @staticmethod
    def get_all_active_notifications() -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM notifications ORDER BY priority DESC, created_at DESC")
        rows = cursor.fetchall()
        conn.close()
        res = []
        for r in rows:
            d = dict(r)
            for k in ["target_qualifications", "target_branches", "target_states"]:
                if isinstance(d.get(k), str):
                    try:
                        d[k] = json.loads(d[k])
                    except Exception:
                        d[k] = []
            res.append(d)
        return res

    @staticmethod
    def get_user_notifications(user_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT d.*, n.category, n.organization, n.official_source, n.end_datetime AS deadline
        FROM notification_deliveries d
        LEFT JOIN notifications n ON d.notification_id = n.id
        WHERE d.user_id = ? AND d.status != 'DISMISSED'
        ORDER BY d.delivery_timestamp DESC
        LIMIT ?
        """, (user_id, limit))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def get_unread_count(user_id: int) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT COUNT(*) AS unread FROM notification_deliveries
        WHERE user_id = ? AND is_read = 0 AND status != 'DISMISSED'
        """, (user_id,))
        row = cursor.fetchone()
        conn.close()
        return row["unread"] if row else 0

    @staticmethod
    def mark_as_read(user_id: int, delivery_id: Optional[int] = None) -> int:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        if delivery_id:
            cursor.execute("""
            UPDATE notification_deliveries SET is_read = 1, read_timestamp = ?
            WHERE user_id = ? AND id = ?
            """, (now_str, user_id, delivery_id))
        else:
            cursor.execute("""
            UPDATE notification_deliveries SET is_read = 1, read_timestamp = ?
            WHERE user_id = ? AND is_read = 0
            """, (now_str, user_id))
        count = cursor.rowcount
        conn.commit()
        conn.close()
        return count

    @staticmethod
    def dismiss(user_id: int, delivery_id: int) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        UPDATE notification_deliveries SET status = 'DISMISSED'
        WHERE user_id = ? AND id = ?
        """, (user_id, delivery_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success

    @staticmethod
    def has_delivered(user_id: int, notification_id: str, channel: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT id FROM notification_deliveries
        WHERE user_id = ? AND notification_id = ? AND channel = ?
        """, (user_id, notification_id, channel))
        row = cursor.fetchone()
        conn.close()
        return row is not None

    @staticmethod
    def create_delivery(user_id: int, notification_id: str, channel: str,
                        title: str, message: str, deep_link: str = "",
                        status: str = "SENT") -> Optional[int]:
        if NotificationRepository.has_delivered(user_id, notification_id, channel):
            return None
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        cursor.execute("""
        INSERT INTO notification_deliveries (
            user_id, notification_id, channel, status, title, message, deep_link, delivery_timestamp
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (user_id, notification_id, channel, status, title, message, deep_link, now_str))
        delivery_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return delivery_id


# ====================================================
# PUSH SUBSCRIPTIONS REPOSITORY
# ====================================================

class PushRepository:
    @staticmethod
    def save_subscription(user_id: int, endpoint: str, p256dh: str, auth: str,
                          user_agent: str = "", device_label: str = "") -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        cursor.execute("""
        INSERT INTO push_subscriptions (user_id, endpoint, p256dh_key, auth_key, user_agent, device_label, is_active, created_at, last_used_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
        ON CONFLICT(endpoint) DO UPDATE SET
            user_id = excluded.user_id,
            p256dh_key = excluded.p256dh_key,
            auth_key = excluded.auth_key,
            is_active = 1,
            last_used_at = excluded.last_used_at
        """, (user_id, endpoint, p256dh, auth, user_agent[:255], device_label, now_str, now_str))
        conn.commit()
        conn.close()
        return True

    @staticmethod
    def get_subscriptions_for_user(user_id: int) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT * FROM push_subscriptions WHERE user_id = ? AND is_active = 1
        """, (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def deactivate_subscription(endpoint: str) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE push_subscriptions SET is_active = 0 WHERE endpoint = ?", (endpoint,))
        conn.commit()
        conn.close()


# ====================================================
# SAVED OPPORTUNITIES REPOSITORY
# ====================================================

class SavedOpportunitiesRepository:
    @staticmethod
    def save(user_id: int, opp_id: str, title: str = "", category: str = "",
             organization: str = "", deadline: str = "", official_url: str = "") -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        try:
            cursor.execute("""
            INSERT INTO saved_opportunities (user_id, opportunity_id, title, category, organization, deadline, official_url, saved_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(user_id, opportunity_id) DO UPDATE SET saved_at = excluded.saved_at
            """, (user_id, opp_id, title, category, organization, deadline, official_url, now_str))
            conn.commit()
            return True
        except Exception:
            return False
        finally:
            conn.close()

    @staticmethod
    def get_saved(user_id: int) -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM saved_opportunities WHERE user_id = ? ORDER BY saved_at DESC", (user_id,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(r) for r in rows]

    @staticmethod
    def remove(user_id: int, opp_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM saved_opportunities WHERE user_id = ? AND opportunity_id = ?", (user_id, opp_id))
        conn.commit()
        success = cursor.rowcount > 0
        conn.close()
        return success


# ====================================================
# EXAM PROGRESS & STUDY PLANS
# ====================================================

class ExamProgressRepository:
    @staticmethod
    def get_progress(user_id: int, exam_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM exam_progress WHERE user_id = ? AND exam_id = ?", (user_id, exam_id))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        if isinstance(d.get("completed_topics"), str):
            try:
                d["completed_topics"] = json.loads(d["completed_topics"])
            except Exception:
                d["completed_topics"] = []
        return d

    @staticmethod
    def save_progress(user_id: int, exam_id: str, stage: str, target_year: Optional[int],
                      completed_topics: List[str], notes: str = "") -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        topics_json = json.dumps(completed_topics)
        cursor.execute("""
        INSERT INTO exam_progress (user_id, exam_id, preparation_stage, target_year, completed_topics, notes, updated_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, exam_id) DO UPDATE SET
            preparation_stage = excluded.preparation_stage,
            target_year = excluded.target_year,
            completed_topics = excluded.completed_topics,
            notes = excluded.notes,
            updated_at = excluded.updated_at
        """, (user_id, exam_id, stage, target_year, topics_json, notes, now_str))
        conn.commit()
        conn.close()

    @staticmethod
    def get_study_plan(user_id: int, exam_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM study_plans WHERE user_id = ? AND exam_id = ?", (user_id, exam_id))
        row = cursor.fetchone()
        conn.close()
        if not row:
            return None
        d = dict(row)
        if isinstance(d.get("custom_schedule"), str):
            try:
                d["custom_schedule"] = json.loads(d["custom_schedule"])
            except Exception:
                d["custom_schedule"] = {}
        return d

    @staticmethod
    def save_study_plan(user_id: int, exam_id: str, duration: str, schedule: Dict[str, Any]) -> None:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        cursor.execute("""
        INSERT INTO study_plans (user_id, exam_id, plan_duration, custom_schedule, created_at, updated_at)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(user_id, exam_id) DO UPDATE SET
            plan_duration = excluded.plan_duration,
            custom_schedule = excluded.custom_schedule,
            updated_at = excluded.updated_at
        """, (user_id, exam_id, duration, json.dumps(schedule), now_str, now_str))
        conn.commit()
        conn.close()


class LearningResourceRepository:
    """Repository for managing verified learning, practice, and training resources in Preparation Hub."""

    @staticmethod
    def _deserialize_row(row: sqlite3.Row) -> Dict[str, Any]:
        d = dict(row)
        for field in ("education_levels", "streams", "branches", "skills", "exams"):
            val = d.get(field)
            if isinstance(val, str):
                try:
                    d[field] = json.loads(val)
                except Exception:
                    d[field] = []
            elif val is None:
                d[field] = []
        return d

    @classmethod
    def get_all(cls, verification_status: Optional[str] = "VERIFIED") -> List[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        if verification_status:
            cursor.execute("SELECT * FROM learning_resources WHERE verification_status = ? ORDER BY name ASC", (verification_status,))
        else:
            cursor.execute("SELECT * FROM learning_resources ORDER BY name ASC")
        rows = cursor.fetchall()
        conn.close()
        return [cls._deserialize_row(r) for r in rows]

    @classmethod
    def get_by_id(cls, resource_id: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM learning_resources WHERE id = ?", (resource_id,))
        row = cursor.fetchone()
        conn.close()
        return cls._deserialize_row(row) if row else None

    @classmethod
    def get_personalized(cls,
                         qualification: Optional[str] = None,
                         stream: Optional[str] = None,
                         branch: Optional[str] = None,
                         career_interests: Optional[List[str]] = None,
                         selected_exam: Optional[str] = None,
                         category: Optional[str] = None,
                         access_type: Optional[str] = None,
                         search_query: Optional[str] = None) -> List[Dict[str, Any]]:
        all_res = cls.get_all(verification_status=None)
        resources = [r for r in all_res if r.get("verification_status") != "INACTIVE"]
        career_interests = [ci.lower() for ci in (career_interests or [])]
        norm_qual = (qualification or "B.Tech").strip()
        norm_branch = (branch or "").strip().lower()
        norm_stream = (stream or "").strip().lower()
        search_terms = [t for t in (search_query or "").lower().strip().split() if t]

        filtered_and_scored: List[Tuple[int, Dict[str, Any]]] = []

        for r in resources:
            r_quals = [q.lower() for q in r.get("education_levels", [])]
            r_branches = [b.lower() for b in r.get("branches", [])]
            r_streams = [s.lower() for s in r.get("streams", [])]
            r_skills = [sk.lower() for sk in r.get("skills", [])]
            r_exams = [e.lower() for e in r.get("exams", [])]

            # 1. Education Level Filtering
            # Strict boundary: 10th students must NOT see B.Tech/GATE/Cloud resources
            if "10th" in norm_qual or "class 10" in norm_qual.lower():
                is_school_compatible = any(q in ["10th", "secondary", "school", "all"] for q in r_quals)
                if not is_school_compatible:
                    continue
            elif "intermediate" in norm_qual.lower() or "10+2" in norm_qual:
                is_inter_compatible = any(q in ["intermediate", "10+2", "11th-12th", "all"] for q in r_quals)
                if not is_inter_compatible:
                    continue
            elif "diploma" in norm_qual.lower() or "polytechnic" in norm_qual.lower():
                is_diploma_compatible = any(q in ["diploma", "polytechnic", "all"] for q in r_quals)
                if not is_diploma_compatible and not any(q in ["b.tech", "degree"] for q in r_quals):
                    continue

            # 2. Category filter
            if category and category.lower() != "all":
                cat_lower = category.lower()
                r_cat = r.get("category", "").lower()
                r_type = r.get("resource_type", "").lower()
                matched_cat = (cat_lower in r_cat or cat_lower in r_type or
                               any(cat_lower in sk for sk in r_skills))
                if not matched_cat:
                    continue

            # 3. Access Type filter
            if access_type and access_type.lower() != "all":
                at_lower = access_type.lower()
                r_at = r.get("access_type", "").lower()
                if at_lower not in r_at:
                    continue

            # 4. Search Query matching
            if search_terms:
                searchable_text = f"{r.get('name', '')} {r.get('description', '')} {r.get('category', '')} {' '.join(r_skills)} {' '.join(r_exams)}".lower()
                if not all(term in searchable_text for term in search_terms):
                    continue

            # 5. Relevance Scoring
            score = 10
            for q in r_quals:
                if q in norm_qual.lower():
                    score += 15

            # Stream / Branch match
            if norm_branch:
                if any(norm_branch in b or b in norm_branch for b in r_branches) or "all" in r_branches or "all branches" in r_branches:
                    score += 15
            if norm_stream:
                if any(norm_stream in s or s in norm_stream for s in r_streams) or "all streams" in r_streams:
                    score += 12

            # Branch-specific bonuses
            if "cse" in norm_branch or "computer" in norm_branch or "it" in norm_branch:
                if any(sk in ["dsa", "programming", "python", "java", "c++", "sql", "web development"] for sk in r_skills):
                    score += 10
            elif "ece" in norm_branch or "electronics" in norm_branch:
                if any(sk in ["digital electronics", "analog electronics", "vlsi", "embedded systems", "circuit theory"] for sk in r_skills):
                    score += 15
            elif "eee" in norm_branch or "electrical" in norm_branch:
                if any(sk in ["power systems", "electrical machines", "circuit theory", "control systems"] for sk in r_skills):
                    score += 15
            elif "mechanical" in norm_branch or "mech" in norm_branch:
                if any(sk in ["thermodynamics", "fluid mechanics", "cad", "manufacturing", "strength of materials"] for sk in r_skills):
                    score += 15
            elif "civil" in norm_branch:
                if any(sk in ["structural engineering", "surveying", "geotechnical", "transportation"] for sk in r_skills):
                    score += 15

            # Stream-specific bonuses for Intermediate
            if "mpc" in norm_stream:
                if any(sk in ["mathematics", "physics", "chemistry", "engineering entrances"] for sk in r_skills):
                    score += 15
            elif "bipc" in norm_stream:
                if any(sk in ["biology", "physics", "chemistry", "medical entrances"] for sk in r_skills):
                    score += 15

            # Career interests match
            for interest in career_interests:
                if any(interest in sk or sk in interest for sk in r_skills):
                    score += 8
                if any(interest in e or e in interest for e in r_exams):
                    score += 8

            # Selected exam match
            if selected_exam:
                norm_exam = selected_exam.lower()
                if any(norm_exam in e or e in norm_exam for e in r_exams):
                    score += 20

            filtered_and_scored.append((score, r))

        filtered_and_scored.sort(key=lambda x: x[0], reverse=True)
        return [item[1] for item in filtered_and_scored]

    @classmethod
    def get_categories_for_qualification(cls, qualification: Optional[str] = None) -> List[str]:
        qual = (qualification or "B.Tech").lower()
        if "10th" in qual or "school" in qual:
            return [
                "All",
                "School & Foundation Learning",
                "School Subjects",
                "Mathematics",
                "Science",
                "Computer Basics",
                "Entrance Exams",
                "Career Exploration"
            ]
        elif "intermediate" in qual or "10+2" in qual:
            return [
                "All",
                "Entrance Exams",
                "Mathematics",
                "Physics & Chemistry",
                "Biology & Medical",
                "Commerce & Economics",
                "Aptitude",
                "Programming"
            ]
        elif "diploma" in qual or "polytechnic" in qual:
            return [
                "All",
                "Core Engineering",
                "Lateral Entry (ECET)",
                "Technical MCQs",
                "Aptitude",
                "Government Exams",
                "Skill Development"
            ]
        else:
            return [
                "All",
                "Coding & CS Fundamentals",
                "Placement Preparation",
                "Aptitude",
                "Reasoning",
                "Verbal Ability",
                "Interview Preparation",
                "SQL",
                "Web Development",
                "AI, ML & Data Science",
                "Core Engineering",
                "GATE",
                "Resume & Interview"
            ]

    @classmethod
    def create_resource(cls, data: Dict[str, Any]) -> str:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        res_id = data.get("id") or f"res_{int(datetime.now().timestamp() * 1000)}"
        cursor.execute("""
        INSERT INTO learning_resources (
            id, name, description, official_url, logo_url, category, resource_type,
            education_levels, streams, branches, skills, exams, access_type,
            free_features, paid_features, language, official_source,
            verification_status, last_verified, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            res_id,
            data.get("name", "Untitled Resource"),
            data.get("description", ""),
            data.get("official_url", ""),
            data.get("logo_url", ""),
            data.get("category", "General"),
            data.get("resource_type", "Learning Platform"),
            json.dumps(data.get("education_levels", [])),
            json.dumps(data.get("streams", [])),
            json.dumps(data.get("branches", [])),
            json.dumps(data.get("skills", [])),
            json.dumps(data.get("exams", [])),
            data.get("access_type", "FREE"),
            data.get("free_features", ""),
            data.get("paid_features", ""),
            data.get("language", "English"),
            data.get("official_source") or data.get("official_url", ""),
            data.get("verification_status", "VERIFIED"),
            data.get("last_verified", now_str[:10]),
            now_str,
            now_str
        ))
        conn.commit()
        conn.close()
        return res_id

    @classmethod
    def update_resource(cls, resource_id: str, data: Dict[str, Any]) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()
        fields = []
        values = []
        for k, v in data.items():
            if k in ("name", "description", "official_url", "logo_url", "category",
                     "resource_type", "access_type", "free_features", "paid_features",
                     "language", "official_source", "verification_status", "last_verified"):
                fields.append(f"{k} = ?")
                values.append(v)
            elif k in ("education_levels", "streams", "branches", "skills", "exams"):
                fields.append(f"{k} = ?")
                values.append(json.dumps(v) if not isinstance(v, str) else v)
        if not fields:
            conn.close()
            return False
        fields.append("updated_at = ?")
        values.append(now_str)
        values.append(resource_id)
        query = f"UPDATE learning_resources SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, tuple(values))
        updated = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return updated

    @classmethod
    def delete_resource(cls, resource_id: str) -> bool:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM learning_resources WHERE id = ?", (resource_id,))
        deleted = cursor.rowcount > 0
        conn.commit()
        conn.close()
        return deleted


# ====================================================
# LEARNING TRACKER REPOSITORY (REAL USER PROGRESS)
# ====================================================

class TrackerRepository:
    """Manages real database-backed learning metrics, study sessions, and topic completion."""

    @classmethod
    def get_progress(cls, user_id: int) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""
        SELECT * FROM learning_progress
        WHERE user_id = ?
        ORDER BY updated_at DESC
        """, (user_id,))
        rows = cursor.fetchall()
        topics = [dict(r) for r in rows] if rows else []

        # Get recent study sessions
        cursor.execute("""
        SELECT * FROM study_sessions
        WHERE user_id = ?
        ORDER BY started_at DESC
        LIMIT 10
        """, (user_id,))
        session_rows = cursor.fetchall()
        sessions = [dict(s) for s in session_rows] if session_rows else []

        conn.close()

        total_tracked = len(topics)
        completed_count = sum(1 for t in topics if t.get("status") == "COMPLETED")
        in_progress_count = sum(1 for t in topics if t.get("status") == "IN_PROGRESS")
        total_study_mins = sum(int(t.get("study_minutes") or 0) for t in topics)
        total_practice_mins = sum(int(t.get("practice_minutes") or 0) for t in topics)
        total_questions = sum(int(t.get("questions_solved") or 0) for t in topics)

        # For brand new users with no tracked topics, overall_progress_percent MUST be 0%
        if total_tracked == 0:
            overall_pct = 0
        else:
            overall_pct = min(100, round((completed_count / total_tracked) * 100))

        # Calculate study streak from unique active days in study_sessions
        unique_dates = sorted({s.get("started_at", "")[:10] for s in sessions if s.get("started_at")}, reverse=True)
        streak = len(unique_dates)

        return {
            "total_topics_tracked": total_tracked,
            "completed_topics_count": completed_count,
            "in_progress_count": in_progress_count,
            "overall_progress_percent": overall_pct,
            "total_study_minutes": total_study_mins,
            "total_practice_minutes": total_practice_mins,
            "total_questions_solved": total_questions,
            "study_streak_days": streak,
            "topics": topics,
            "recent_sessions": sessions
        }

    @classmethod
    def start_topic(cls, user_id: int, topic: str, category: str = "General", resource_id: Optional[str] = None) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()

        cursor.execute("""
        SELECT * FROM learning_progress WHERE user_id = ? AND topic = ?
        """, (user_id, topic))
        existing = cursor.fetchone()

        if existing:
            cursor.execute("""
            UPDATE learning_progress
            SET status = CASE WHEN status = 'COMPLETED' THEN 'COMPLETED' ELSE 'IN_PROGRESS' END,
                updated_at = ?
            WHERE user_id = ? AND topic = ?
            """, (now_str, user_id, topic))
        else:
            cursor.execute("""
            INSERT INTO learning_progress (
                user_id, resource_id, topic, category, status, progress_percent,
                study_minutes, practice_minutes, questions_solved, created_at, updated_at
            ) VALUES (?, ?, ?, ?, 'IN_PROGRESS', 25, 15, 0, 0, ?, ?)
            """, (user_id, resource_id or "", topic, category, now_str, now_str))

        # Log session
        cursor.execute("""
        INSERT INTO study_sessions (
            user_id, topic, category, session_type, duration_minutes, started_at, created_at, notes
        ) VALUES (?, ?, ?, 'STUDY', 15, ?, ?, ?)
        """, (user_id, topic, category, now_str, now_str, f"Started learning: {topic}"))

        conn.commit()
        conn.close()
        return cls.get_progress(user_id)

    @classmethod
    def complete_topic(cls, user_id: int, topic: str, category: str = "General",
                       study_minutes: int = 45, practice_minutes: int = 20,
                       questions_solved: int = 15, quiz_score: float = 90.0) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()

        cursor.execute("""
        SELECT * FROM learning_progress WHERE user_id = ? AND topic = ?
        """, (user_id, topic))
        existing = cursor.fetchone()

        if existing:
            prev_study = int(existing["study_minutes"] or 0)
            prev_practice = int(existing["practice_minutes"] or 0)
            prev_questions = int(existing["questions_solved"] or 0)
            cursor.execute("""
            UPDATE learning_progress
            SET status = 'COMPLETED',
                progress_percent = 100,
                study_minutes = ?,
                practice_minutes = ?,
                questions_solved = ?,
                quiz_score = ?,
                completed_at = ?,
                updated_at = ?
            WHERE user_id = ? AND topic = ?
            """, (
                max(prev_study, study_minutes),
                max(prev_practice, practice_minutes),
                prev_questions + questions_solved,
                quiz_score,
                now_str,
                now_str,
                user_id,
                topic
            ))
        else:
            cursor.execute("""
            INSERT INTO learning_progress (
                user_id, resource_id, topic, category, status, progress_percent,
                study_minutes, practice_minutes, questions_solved, quiz_score,
                completed_at, created_at, updated_at
            ) VALUES (?, '', ?, ?, 'COMPLETED', 100, ?, ?, ?, ?, ?, ?, ?)
            """, (user_id, topic, category, study_minutes, practice_minutes, questions_solved, quiz_score, now_str, now_str, now_str))

        # Log completion session
        cursor.execute("""
        INSERT INTO study_sessions (
            user_id, topic, category, session_type, duration_minutes, started_at, created_at, notes
        ) VALUES (?, ?, ?, 'PRACTICE', ?, ?, ?, ?)
        """, (user_id, topic, category, practice_minutes, now_str, now_str, f"Completed topic and solved {questions_solved} questions"))

        conn.commit()
        conn.close()
        return cls.get_progress(user_id)

    @classmethod
    def log_session(cls, user_id: int, topic: str, duration_minutes: int,
                    session_type: str = "STUDY", notes: Optional[str] = None) -> Dict[str, Any]:
        conn = get_db_connection()
        cursor = conn.cursor()
        now_str = now_ist_iso()

        cursor.execute("""
        INSERT INTO study_sessions (
            user_id, topic, category, session_type, duration_minutes, started_at, created_at, notes
        ) VALUES (?, ?, 'General', ?, ?, ?, ?, ?)
        """, (user_id, topic, session_type, duration_minutes, now_str, now_str, notes or f"Logged {duration_minutes}m session"))

        # Update topic in learning_progress if it exists
        cursor.execute("SELECT * FROM learning_progress WHERE user_id = ? AND topic = ?", (user_id, topic))
        row = cursor.fetchone()
        if row:
            if session_type == "PRACTICE":
                cursor.execute("""
                UPDATE learning_progress
                SET practice_minutes = practice_minutes + ?, updated_at = ?
                WHERE user_id = ? AND topic = ?
                """, (duration_minutes, now_str, user_id, topic))
            else:
                cursor.execute("""
                UPDATE learning_progress
                SET study_minutes = study_minutes + ?, updated_at = ?
                WHERE user_id = ? AND topic = ?
                """, (duration_minutes, now_str, user_id, topic))

        conn.commit()
        conn.close()
        return cls.get_progress(user_id)

    @classmethod
    def get_personalized_study_plan(cls, user_id: int) -> Dict[str, Any]:
        profile = ProfileRepository.get_profile(user_id) or {}
        qual = (profile.get("qualification") or "B.Tech").strip()
        stream = (profile.get("stream") or profile.get("branch") or "CSE").strip()
        interests = profile.get("career_interests") or []
        dream_goal = profile.get("dream_goal") or ""

        # Build qualification and branch tailored modules
        if "10th" in qual:
            modules = [
                {"title": "Mathematics Foundation", "topics": ["Linear Equations & Quadratic Formulas", "Trigonometry Basics", "Coordinate Geometry", "Mensuration & Surface Areas"], "hours": 20},
                {"title": "Science & Tech Literacy", "topics": ["Physics Mechanics & Electricity", "Chemistry Chemical Reactions & Acids", "Biology Life Processes", "Computer Basics & Coding Intro"], "hours": 25},
                {"title": "Competitive Aptitude & NTSE", "topics": ["Mental Ability (MAT)", "Scholastic Aptitude (SAT)", "PolyCET / APRJC Maths & Physics", "English Comprehension"], "hours": 20},
                {"title": "Future Path Exploration", "topics": ["Polytechnic vs Intermediate MPC/BiPC", "ITI Technical Trades", "Armed Forces (NDA / Sailor Prep)", "Scholarship Application Deadlines"], "hours": 15}
            ]
        elif "Intermediate" in qual:
            if "bipc" in stream.lower() or "medical" in stream.lower():
                modules = [
                    {"title": "NEET Biology Masterclass", "topics": ["Human Physiology & Anatomy", "Genetics & Molecular Evolution", "Cell Biology & Division", "Ecology & Plant Diversity"], "hours": 40},
                    {"title": "Physics for Medical Entrances", "topics": ["Kinematics & Newton's Laws", "Electrodynamics & Optics", "Thermodynamics & Heat", "Modern Physics"], "hours": 30},
                    {"title": "Chemistry Foundation", "topics": ["Organic Reaction Mechanisms", "Physical Equilibrium & Electrochemistry", "Inorganic Periodic Trends & Coordination", "NCERT Line-by-Line Practice"], "hours": 35},
                    {"title": "Mock Tests & Revision", "topics": ["Full-Length 720-Mark Mock 1", "Error Analysis & Time Management", "State Counselling & College Selection", "Alternative Allied Medical Careers"], "hours": 25}
                ]
            else: # MPC / General
                modules = [
                    {"title": "Mathematics (JEE / EAPCET)", "topics": ["Calculus (Differential & Integral)", "Vectors & 3D Geometry", "Matrices, Determinants & Complex Numbers", "Coordinate Geometry & Conic Sections"], "hours": 40},
                    {"title": "Physics (Concepts & Problem Solving)", "topics": ["Rotational Dynamics & Mechanics", "Electromagnetism & AC Circuits", "Wave Optics & Ray Optics", "Modern Physics & Semiconductors"], "hours": 35},
                    {"title": "Chemistry (Score Booster)", "topics": ["Organic Carbonyls & Polymers", "Thermodynamics & Kinetics", "P-Block & Transition Elements", "Mock Question Bank & PYQs"], "hours": 30},
                    {"title": "Exam Blueprint & Strategy", "topics": ["JEE Main Speed Drills", "EAPCET / State CET High-Weightage Chapters", "NDA Mathematics & GAT Entry", "Counselling Cutoff Strategies"], "hours": 25}
                ]
        elif "Diploma" in qual:
            modules = [
                {"title": "Lateral Entry B.Tech (ECET)", "topics": ["Engineering Mathematics (Matrices, Differential Eqns, Laplace)", "Physics & Chemistry Core MCQs", "Branch Engineering Subject Test", "Previous 10-Year ECET Paper Analysis"], "hours": 35},
                {"title": "Government JE Exams (RRB & SSC)", "topics": ["Reasoning & General Intelligence", "General Science & Current Affairs", "Core Engineering MCQs (Level 6)", "CBT-1 Speed Practice"], "hours": 30},
                {"title": "Core Industry & NATS Apprenticeship", "topics": ["Hands-on Lab & Plant Operations", "Industrial Safety & Standards", "NATS Portal Registration & PSU Applications", "Technical Interview Questions"], "hours": 20},
                {"title": "IT & Software Skills Bridge", "topics": ["Python Programming & Logic", "Database Basics (SQL)", "Web Development Fundamentals", "Git & GitHub Version Control"], "hours": 25}
            ]
        elif "Degree" in qual:
            modules = [
                {"title": "Civil Services & State PSC (UPSC/Group 1)", "topics": ["Indian Polity & Constitution", "Indian Economy & Budget", "Modern Indian History & Geography", "Current Affairs & CSAT Analytical Reasoning"], "hours": 45},
                {"title": "Banking & Insurance (IBPS/SBI PO)", "topics": ["Quantitative Aptitude (Data Interpretation)", "Logical Reasoning & Puzzles", "English Language Comprehension", "Banking Awareness & Economic News"], "hours": 35},
                {"title": "Management & Higher Studies (CAT/ICET/CUET)", "topics": ["Quantitative Ability (Arithmetic & Algebra)", "Data Interpretation & Logical Reasoning (DILR)", "Verbal Ability & Reading Comprehension (VARC)", "NIMCET / MCA Computer Awareness"], "hours": 35},
                {"title": "Corporate Placements & Skill Portfolio", "topics": ["Excel & Business Analytics", "Communication & Group Discussions", "Resume Building & LinkedIn Optimization", "Campus & Walk-in Interview Preparation"], "hours": 25}
            ]
        elif "Postgraduate" in qual:
            modules = [
                {"title": "Research & Thesis Methodology", "topics": ["Literature Review & Indexing", "IEEE / ACM / Springer Paper Formatting", "Statistical Testing & Analysis", "IPR & Patent Filing Process"], "hours": 30},
                {"title": "UGC-NET / CSIR-NET & JRF", "topics": ["Teaching & Research Aptitude (Paper 1)", "Specialized Subject Domain (Paper 2)", "Higher Education System in India", "Previous Years Solved Papers"], "hours": 40},
                {"title": "Corporate R&D & Specialist Careers", "topics": ["Advanced Algorithm Design / Core Domain", "Domain Consulting & Industry Collaboration", "Ph.D. Entrance (IIT / IISc / Top Universities)", "Statement of Purpose (SOP) & Interview Prep"], "hours": 30}
            ]
        else: # B.Tech / Default
            modules = [
                {"title": "Data Structures & Core CS / Tech", "topics": ["Arrays, Linked Lists, Stacks & Queues", "Trees, Graphs & Dynamic Programming", "Object-Oriented Programming (Java/Python/C++)", "Database Management & SQL Queries"], "hours": 45},
                {"title": "System Design & Modern Tech Stack", "topics": ["RESTful APIs & Backend Architecture", "Frontend Frameworks (React/HTML5)", "Cloud Computing (AWS/Docker) Basics", "Git, Unit Testing & CI/CD Pipelines"], "hours": 35},
                {"title": "Aptitude, Reasoning & Verbal Ability", "topics": ["Quantitative Aptitude (Permutations, Probability, Speed-Distance)", "Logical Reasoning & Critical Thinking", "Verbal Ability & Reading Comprehension", "Company-Specific Mock Rounds (TCS, Infosys, Wipro, Accenture)"], "hours": 30},
                {"title": "GATE / PSU & Core Technical Roadmap", "topics": ["Engineering Mathematics & Discrete Maths", "Branch Core Subjects (Digital Logic, Operating Systems, Networks)", "PSU Recruitment via GATE", "Technical Interview Questions & Coding Challenges"], "hours": 40}
            ]

        progress = cls.get_progress(user_id)
        return {
            "qualification": qual,
            "stream": stream,
            "dream_goal": dream_goal,
            "interests": interests,
            "modules": modules,
            "stats": {
                "overall_progress_percent": progress["overall_progress_percent"],
                "total_study_minutes": progress["total_study_minutes"],
                "total_practice_minutes": progress["total_practice_minutes"],
                "completed_topics_count": progress["completed_topics_count"],
                "study_streak_days": progress["study_streak_days"]
            }
        }

