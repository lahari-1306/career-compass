"""
Data Access Repository for CareerCompass.
Handles all relational queries, user isolation, Argon2id password hashing,
session tokens, and notification tracking with complete parameterization.
"""

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
            INSERT INTO users (email, password_hash, name, role, is_verified, created_at, updated_at)
            VALUES (?, ?, ?, ?, 1, ?, ?)
            """, (email.strip().lower(), pwd_hash, name.strip(), role, now_str, now_str))
            user_id = cursor.lastrowid

            # Initialize empty education-aware profile
            cursor.execute("""
            INSERT INTO user_profiles (user_id, qualification, current_status, created_at, updated_at)
            VALUES (?, 'B.Tech', 'Final Year', ?, ?)
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
        cursor.execute("SELECT id, email, name, role, is_verified, created_at, last_login_at FROM users WHERE id = ?", (user_id,))
        row = cursor.fetchone()
        conn.close()
        return dict(row) if row else None

    @staticmethod
    def get_by_email(email: str) -> Optional[Dict[str, Any]]:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email = ? COLLATE NOCASE", (email.strip().lower(),))
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

        cursor.execute("""
        INSERT INTO user_profiles (
            user_id, qualification, current_status, stream, branch, completion_year,
            home_state, scope, score, age, career_interests, selected_exams, preferred_pathways,
            preferred_language, dream_goal, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
