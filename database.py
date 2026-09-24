"""
Production Persistent Database Layer for CareerCompass.
Implements ACID-compliant relational storage for:
- users
- user_profiles
- user_preferences
- user_sessions
- password_reset_tokens
- email_verifications
- notification_preferences
- notifications
- notification_deliveries
- push_subscriptions
- saved_opportunities
- exam_progress
- study_plans
- ai_conversations
- learning_resources

Supports both:
1. PostgreSQL (via DATABASE_URL, with automatic SSL and %s translation)
2. SQLite (via DATABASE_PATH, with WAL mode, foreign keys, and synchronous=NORMAL)
"""

import os
import sqlite3
import json
import logging
import re
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple, Union

logger = logging.getLogger("careercompass.database")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(DATA_DIR, "career_compass.db"))
os.makedirs(os.path.dirname(os.path.abspath(DB_PATH)), exist_ok=True)

IST = timezone(timedelta(hours=5, minutes=30))


def now_ist_iso() -> str:
    return datetime.now(IST).isoformat()


# ====================================================
# DATABASE ENGINE CONFIGURATION (POSTGRESQL & SQLITE)
# ====================================================

DATABASE_URL = os.environ.get("DATABASE_URL", "").strip()
# Normalize Render's 'postgres://' URI scheme to 'postgresql://' for psycopg2
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

IS_POSTGRES = False
psycopg2 = None

if DATABASE_URL:
    try:
        import psycopg2
        import psycopg2.extras
        # Test connection
        test_conn = psycopg2.connect(DATABASE_URL, connect_timeout=10)
        test_conn.close()
        IS_POSTGRES = True
        logger.info("Successfully connected to PostgreSQL via DATABASE_URL.")
    except Exception as e:
        logger.warning(f"Could not connect to PostgreSQL via DATABASE_URL ({e}). Falling back to SQLite.")
        IS_POSTGRES = False


class PostgresCursorWrapper:
    """Cursor wrapper for PostgreSQL providing parameter marker translation and lastrowid support."""
    def __init__(self, pg_cursor):
        self.cursor = pg_cursor
        self.lastrowid = None

    def execute(self, query: str, params: Optional[Union[tuple, list, dict]] = None):
        # Translate '?' parameter markers to '%s'
        pg_query = query.replace("?", "%s")
        # Remove SQLite specific COLLATE NOCASE
        pg_query = pg_query.replace("COLLATE NOCASE", "")

        stripped = pg_query.strip().upper()
        is_insert = stripped.startswith("INSERT INTO")
        has_returning = "RETURNING" in stripped

        # Tables with SERIAL PRIMARY KEY 'id'
        auto_id_tables = (
            "users", "user_profiles", "user_preferences", "user_sessions",
            "password_reset_tokens", "email_verifications", "notification_preferences",
            "notification_deliveries", "push_subscriptions", "saved_opportunities",
            "exam_progress", "study_plans", "ai_conversations"
        )

        should_return_id = is_insert and not has_returning and any(
            re.search(rf"\bINSERT\s+INTO\s+{tbl}\b", pg_query, re.IGNORECASE)
            for tbl in auto_id_tables
        )

        if should_return_id:
            pg_query = pg_query.rstrip("; \t\n\r") + " RETURNING id;"

        if params is not None:
            self.cursor.execute(pg_query, params)
        else:
            self.cursor.execute(pg_query)

        if should_return_id:
            try:
                ret = self.cursor.fetchone()
                if ret:
                    self.lastrowid = ret["id"] if isinstance(ret, dict) else ret[0]
            except Exception:
                self.lastrowid = None

        return self

    def executemany(self, query: str, params_seq):
        pg_query = query.replace("?", "%s").replace("COLLATE NOCASE", "")
        return self.cursor.executemany(pg_query, params_seq)

    def fetchone(self):
        return self.cursor.fetchone()

    def fetchall(self):
        return self.cursor.fetchall()

    def fetchmany(self, size=None):
        if size is not None:
            return self.cursor.fetchmany(size)
        return self.cursor.fetchmany()

    @property
    def rowcount(self):
        return self.cursor.rowcount

    def close(self):
        self.cursor.close()

    def __iter__(self):
        return iter(self.cursor)


class PostgresConnectionWrapper:
    """Connection wrapper for PostgreSQL providing unified cursor interface."""
    def __init__(self, pg_conn):
        self.conn = pg_conn

    def cursor(self):
        import psycopg2.extras
        real_cursor = self.conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return PostgresCursorWrapper(real_cursor)

    def execute(self, query: str, params=None):
        cur = self.cursor()
        cur.execute(query, params)
        return cur

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.conn.close()


def get_db_connection():
    """
    Returns an active database connection.
    If PostgreSQL is configured and reachable via DATABASE_URL, returns PostgresConnectionWrapper.
    Otherwise, returns a SQLite connection configured with WAL mode, foreign keys, and Row factory.
    """
    if IS_POSTGRES:
        try:
            conn = psycopg2.connect(DATABASE_URL)
            return PostgresConnectionWrapper(conn)
        except Exception as e:
            logger.error(f"PostgreSQL connection error: {e}. Falling back to SQLite.")

    # SQLite fallback / default
    conn = sqlite3.connect(DB_PATH, timeout=30.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.execute("PRAGMA synchronous = NORMAL;")
    return conn


def init_db() -> None:
    """Initializes all database tables, constraints, indexes, and initial verified seed data."""
    conn = get_db_connection()
    cursor = conn.cursor()

    if IS_POSTGRES:
        # PostgreSQL Schema
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            is_verified INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_login_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_users_email_lower ON users (LOWER(email));
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            qualification TEXT NOT NULL DEFAULT 'B.Tech',
            current_status TEXT NOT NULL DEFAULT 'Final Year',
            stream TEXT,
            branch TEXT,
            completion_year INTEGER,
            home_state TEXT DEFAULT 'All India / National',
            scope TEXT DEFAULT 'All India',
            score TEXT,
            age INTEGER,
            career_interests TEXT DEFAULT '[]',
            selected_exams TEXT DEFAULT '[]',
            preferred_pathways TEXT DEFAULT '[]',
            preferred_language TEXT DEFAULT 'en',
            dream_goal TEXT,
            is_onboarded INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            theme TEXT NOT NULL DEFAULT 'light',
            preferred_language TEXT NOT NULL DEFAULT 'en',
            email_notifications_enabled INTEGER NOT NULL DEFAULT 1,
            push_notifications_enabled INTEGER NOT NULL DEFAULT 1,
            weekly_digest_enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id SERIAL PRIMARY KEY,
            session_token TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            ip_address TEXT,
            user_agent TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1
        );
        CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);
        CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_pwd_tokens_token ON password_reset_tokens(token);
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_verifications (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            token TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            verified_at TEXT
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_preferences (
            id SERIAL PRIMARY KEY,
            user_id INTEGER UNIQUE NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            new_opportunities INTEGER NOT NULL DEFAULT 1,
            deadlines INTEGER NOT NULL DEFAULT 1,
            admit_cards INTEGER NOT NULL DEFAULT 1,
            results INTEGER NOT NULL DEFAULT 1,
            counselling INTEGER NOT NULL DEFAULT 1,
            scholarships INTEGER NOT NULL DEFAULT 1,
            email_channel INTEGER NOT NULL DEFAULT 1,
            push_channel INTEGER NOT NULL DEFAULT 1,
            in_app_channel INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'General',
            organization TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'OPEN',
            start_datetime TEXT,
            end_datetime TEXT,
            exam_date TEXT,
            result_date TEXT,
            eligibility_summary TEXT,
            official_source TEXT,
            official_application_url TEXT,
            priority TEXT DEFAULT 'NORMAL',
            description TEXT,
            target_qualifications TEXT DEFAULT '[]',
            target_branches TEXT DEFAULT '[]',
            target_states TEXT DEFAULT '[]',
            last_verified_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications(category);
        CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_deliveries (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            notification_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'SENT',
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            deep_link TEXT,
            is_read INTEGER NOT NULL DEFAULT 0,
            is_saved INTEGER NOT NULL DEFAULT 0,
            delivery_timestamp TEXT NOT NULL,
            read_timestamp TEXT,
            error_message TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_deliveries_user_unread ON notification_deliveries(user_id, is_read);
        CREATE INDEX IF NOT EXISTS idx_deliveries_dedup ON notification_deliveries(user_id, notification_id, channel);
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            endpoint TEXT UNIQUE NOT NULL,
            p256dh_key TEXT NOT NULL,
            auth_key TEXT NOT NULL,
            user_agent TEXT,
            device_label TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            last_used_at TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_push_user_id ON push_subscriptions(user_id);
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_opportunities (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            opportunity_id TEXT NOT NULL,
            title TEXT,
            category TEXT,
            organization TEXT,
            deadline TEXT,
            official_url TEXT,
            notes TEXT,
            saved_at TEXT NOT NULL,
            UNIQUE(user_id, opportunity_id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_progress (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            exam_id TEXT NOT NULL,
            preparation_stage TEXT DEFAULT 'Beginner',
            target_year INTEGER,
            completed_topics TEXT DEFAULT '[]',
            notes TEXT,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, exam_id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            exam_id TEXT NOT NULL,
            plan_duration TEXT NOT NULL DEFAULT '3_MONTHS',
            custom_schedule TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            UNIQUE(user_id, exam_id)
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            title TEXT NOT NULL DEFAULT 'Career Guidance',
            messages TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_resources (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            official_url TEXT NOT NULL,
            logo_url TEXT,
            category TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            education_levels TEXT DEFAULT '[]',
            streams TEXT DEFAULT '[]',
            branches TEXT DEFAULT '[]',
            skills TEXT DEFAULT '[]',
            exams TEXT DEFAULT '[]',
            access_type TEXT NOT NULL DEFAULT 'FREE',
            free_features TEXT,
            paid_features TEXT,
            language TEXT DEFAULT 'English',
            official_source TEXT,
            verification_status TEXT NOT NULL DEFAULT 'VERIFIED',
            last_verified TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_resources_category ON learning_resources(category);
        CREATE INDEX IF NOT EXISTS idx_resources_verification ON learning_resources(verification_status);
        CREATE INDEX IF NOT EXISTS idx_resources_access ON learning_resources(access_type);
        """)

        conn.commit()

        # Seed notifications in PostgreSQL
        cursor.execute("SELECT COUNT(*) AS cnt FROM notifications;")
        row = cursor.fetchone()
        cnt = row["cnt"] if isinstance(row, dict) else (row[0] if row else 0)
        if cnt == 0:
            notifs_path = os.path.join(DATA_DIR, "notifications.json")
            if os.path.exists(notifs_path):
                try:
                    with open(notifs_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    items = data if isinstance(data, list) else data.get("notifications", [])
                    now_str = now_ist_iso()
                    for item in items:
                        cursor.execute("""
                        INSERT INTO notifications (
                            id, title, category, organization, status, start_datetime, end_datetime,
                            exam_date, result_date, eligibility_summary, official_source, official_application_url,
                            priority, description, target_qualifications, target_branches, target_states,
                            last_verified_at, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT (id) DO NOTHING;
                        """, (
                            item.get("id"),
                            item.get("title", ""),
                            item.get("category", "General"),
                            item.get("organization", ""),
                            item.get("status", "OPEN"),
                            item.get("start_datetime"),
                            item.get("end_datetime"),
                            item.get("exam_date"),
                            item.get("result_date"),
                            item.get("eligibility_summary"),
                            item.get("official_source"),
                            item.get("official_application_url") or item.get("official_source"),
                            item.get("priority", "NORMAL"),
                            item.get("description", ""),
                            json.dumps(item.get("target_qualifications", [])),
                            json.dumps(item.get("target_branches", [])),
                            json.dumps(item.get("target_states", [])),
                            item.get("last_verified_at") or now_str,
                            now_str
                        ))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error seeding notifications in PostgreSQL: {e}")

        # Seed learning_resources in PostgreSQL
        cursor.execute("SELECT COUNT(*) AS cnt FROM learning_resources;")
        res_row = cursor.fetchone()
        res_cnt = res_row["cnt"] if isinstance(res_row, dict) else (res_row[0] if res_row else 0)
        if res_cnt == 0:
            res_path = os.path.join(DATA_DIR, "learning_resources.json")
            if os.path.exists(res_path):
                try:
                    with open(res_path, "r", encoding="utf-8") as f:
                        resources = json.load(f)
                    now_str = now_ist_iso()
                    for r in resources:
                        cursor.execute("""
                        INSERT INTO learning_resources (
                            id, name, description, official_url, logo_url, category, resource_type,
                            education_levels, streams, branches, skills, exams, access_type,
                            free_features, paid_features, language, official_source,
                            verification_status, last_verified, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        ON CONFLICT (id) DO NOTHING;
                        """, (
                            r.get("id"),
                            r.get("name"),
                            r.get("description"),
                            r.get("official_url"),
                            r.get("logo_url", ""),
                            r.get("category", "General"),
                            r.get("resource_type", "Practice & Learning Platform"),
                            json.dumps(r.get("education_levels", [])),
                            json.dumps(r.get("streams", [])),
                            json.dumps(r.get("branches", [])),
                            json.dumps(r.get("skills", [])),
                            json.dumps(r.get("exams", [])),
                            r.get("access_type", "FREE"),
                            r.get("free_features", ""),
                            r.get("paid_features", ""),
                            r.get("language", "English"),
                            r.get("official_source", r.get("official_url")),
                            r.get("verification_status", "VERIFIED"),
                            r.get("last_verified", now_str[:10]),
                            r.get("created_at", now_str),
                            r.get("updated_at", now_str)
                        ))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error seeding learning resources in PostgreSQL: {e}")

    else:
        # SQLite Schema
        # 1. Users
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL COLLATE NOCASE,
            password_hash TEXT NOT NULL,
            name TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            is_verified INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_login_at TEXT
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_users_email ON users(email);")

        # 2. User Profiles
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            qualification TEXT NOT NULL DEFAULT 'B.Tech',
            current_status TEXT NOT NULL DEFAULT 'Final Year',
            stream TEXT,
            branch TEXT,
            completion_year INTEGER,
            home_state TEXT DEFAULT 'All India / National',
            scope TEXT DEFAULT 'All India',
            score TEXT,
            age INTEGER,
            career_interests TEXT DEFAULT '[]',
            selected_exams TEXT DEFAULT '[]',
            preferred_pathways TEXT DEFAULT '[]',
            preferred_language TEXT DEFAULT 'en',
            dream_goal TEXT,
            is_onboarded INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        try:
            cursor.execute("ALTER TABLE user_profiles ADD COLUMN is_onboarded INTEGER NOT NULL DEFAULT 0;")
            conn.commit()
        except sqlite3.OperationalError:
            pass  # Column already exists
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id);")

        # 3. User Preferences
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            theme TEXT NOT NULL DEFAULT 'light',
            preferred_language TEXT NOT NULL DEFAULT 'en',
            email_notifications_enabled INTEGER NOT NULL DEFAULT 1,
            push_notifications_enabled INTEGER NOT NULL DEFAULT 1,
            weekly_digest_enabled INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 4. User Sessions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_token TEXT UNIQUE NOT NULL,
            user_id INTEGER NOT NULL,
            ip_address TEXT,
            user_agent TEXT,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            is_active INTEGER NOT NULL DEFAULT 1,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_token ON user_sessions(session_token);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON user_sessions(user_id);")

        # 5. Password Reset Tokens
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS password_reset_tokens (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            used_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_pwd_tokens_token ON password_reset_tokens(token);")

        # 6. Email Verifications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS email_verifications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            token TEXT UNIQUE NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            verified_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 7. Notification Preferences
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE NOT NULL,
            new_opportunities INTEGER NOT NULL DEFAULT 1,
            deadlines INTEGER NOT NULL DEFAULT 1,
            admit_cards INTEGER NOT NULL DEFAULT 1,
            results INTEGER NOT NULL DEFAULT 1,
            counselling INTEGER NOT NULL DEFAULT 1,
            scholarships INTEGER NOT NULL DEFAULT 1,
            email_channel INTEGER NOT NULL DEFAULT 1,
            push_channel INTEGER NOT NULL DEFAULT 1,
            in_app_channel INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 8. Notifications
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notifications (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            category TEXT NOT NULL DEFAULT 'General',
            organization TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'OPEN',
            start_datetime TEXT,
            end_datetime TEXT,
            exam_date TEXT,
            result_date TEXT,
            eligibility_summary TEXT,
            official_source TEXT,
            official_application_url TEXT,
            priority TEXT DEFAULT 'NORMAL',
            description TEXT,
            target_qualifications TEXT DEFAULT '[]',
            target_branches TEXT DEFAULT '[]',
            target_states TEXT DEFAULT '[]',
            last_verified_at TEXT NOT NULL,
            created_at TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_category ON notifications(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);")

        # 9. Notification Deliveries
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS notification_deliveries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            notification_id TEXT NOT NULL,
            channel TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'SENT',
            title TEXT NOT NULL,
            message TEXT NOT NULL,
            deep_link TEXT,
            is_read INTEGER NOT NULL DEFAULT 0,
            is_saved INTEGER NOT NULL DEFAULT 0,
            delivery_timestamp TEXT NOT NULL,
            read_timestamp TEXT,
            error_message TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_user_unread ON notification_deliveries(user_id, is_read);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_deliveries_dedup ON notification_deliveries(user_id, notification_id, channel);")

        # 10. Push Subscriptions
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS push_subscriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            endpoint TEXT UNIQUE NOT NULL,
            p256dh_key TEXT NOT NULL,
            auth_key TEXT NOT NULL,
            user_agent TEXT,
            device_label TEXT,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL,
            last_used_at TEXT,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_push_user_id ON push_subscriptions(user_id);")

        # 11. Saved Opportunities
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS saved_opportunities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            opportunity_id TEXT NOT NULL,
            title TEXT,
            category TEXT,
            organization TEXT,
            deadline TEXT,
            official_url TEXT,
            notes TEXT,
            saved_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, opportunity_id)
        );
        """)

        # 12. Exam Progress
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS exam_progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exam_id TEXT NOT NULL,
            preparation_stage TEXT DEFAULT 'Beginner',
            target_year INTEGER,
            completed_topics TEXT DEFAULT '[]',
            notes TEXT,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, exam_id)
        );
        """)

        # 13. Study Plans
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS study_plans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            exam_id TEXT NOT NULL,
            plan_duration TEXT NOT NULL DEFAULT '3_MONTHS',
            custom_schedule TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            UNIQUE(user_id, exam_id)
        );
        """)

        # 14. AI Conversations
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS ai_conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL DEFAULT 'Career Guidance',
            messages TEXT NOT NULL DEFAULT '[]',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
        """)

        # 15. Learning Resources
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS learning_resources (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT NOT NULL,
            official_url TEXT NOT NULL,
            logo_url TEXT,
            category TEXT NOT NULL,
            resource_type TEXT NOT NULL,
            education_levels TEXT DEFAULT '[]',
            streams TEXT DEFAULT '[]',
            branches TEXT DEFAULT '[]',
            skills TEXT DEFAULT '[]',
            exams TEXT DEFAULT '[]',
            access_type TEXT NOT NULL DEFAULT 'FREE',
            free_features TEXT,
            paid_features TEXT,
            language TEXT DEFAULT 'English',
            official_source TEXT,
            verification_status TEXT NOT NULL DEFAULT 'VERIFIED',
            last_verified TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_category ON learning_resources(category);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_verification ON learning_resources(verification_status);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_resources_access ON learning_resources(access_type);")

        conn.commit()

        # Seed notifications in SQLite if empty
        cursor.execute("SELECT COUNT(*) AS cnt FROM notifications;")
        row = cursor.fetchone()
        if row and row["cnt"] == 0:
            notifs_path = os.path.join(DATA_DIR, "notifications.json")
            if os.path.exists(notifs_path):
                try:
                    with open(notifs_path, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    items = data if isinstance(data, list) else data.get("notifications", [])
                    now_str = now_ist_iso()
                    for item in items:
                        cursor.execute("""
                        INSERT OR IGNORE INTO notifications (
                            id, title, category, organization, status, start_datetime, end_datetime,
                            exam_date, result_date, eligibility_summary, official_source, official_application_url,
                            priority, description, target_qualifications, target_branches, target_states,
                            last_verified_at, created_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            item.get("id"),
                            item.get("title", ""),
                            item.get("category", "General"),
                            item.get("organization", ""),
                            item.get("status", "OPEN"),
                            item.get("start_datetime"),
                            item.get("end_datetime"),
                            item.get("exam_date"),
                            item.get("result_date"),
                            item.get("eligibility_summary"),
                            item.get("official_source"),
                            item.get("official_application_url") or item.get("official_source"),
                            item.get("priority", "NORMAL"),
                            item.get("description", ""),
                            json.dumps(item.get("target_qualifications", [])),
                            json.dumps(item.get("target_branches", [])),
                            json.dumps(item.get("target_states", [])),
                            item.get("last_verified_at") or now_str,
                            now_str
                        ))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error seeding notifications: {e}")

        # Seed learning_resources in SQLite if empty
        cursor.execute("SELECT COUNT(*) AS cnt FROM learning_resources;")
        res_row = cursor.fetchone()
        if res_row and res_row["cnt"] == 0:
            res_path = os.path.join(DATA_DIR, "learning_resources.json")
            if os.path.exists(res_path):
                try:
                    with open(res_path, "r", encoding="utf-8") as f:
                        resources = json.load(f)
                    now_str = now_ist_iso()
                    for r in resources:
                        cursor.execute("""
                        INSERT OR REPLACE INTO learning_resources (
                            id, name, description, official_url, logo_url, category, resource_type,
                            education_levels, streams, branches, skills, exams, access_type,
                            free_features, paid_features, language, official_source,
                            verification_status, last_verified, created_at, updated_at
                        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (
                            r.get("id"),
                            r.get("name"),
                            r.get("description"),
                            r.get("official_url"),
                            r.get("logo_url", ""),
                            r.get("category", "General"),
                            r.get("resource_type", "Practice & Learning Platform"),
                            json.dumps(r.get("education_levels", [])),
                            json.dumps(r.get("streams", [])),
                            json.dumps(r.get("branches", [])),
                            json.dumps(r.get("skills", [])),
                            json.dumps(r.get("exams", [])),
                            r.get("access_type", "FREE"),
                            r.get("free_features", ""),
                            r.get("paid_features", ""),
                            r.get("language", "English"),
                            r.get("official_source", r.get("official_url")),
                            r.get("verification_status", "VERIFIED"),
                            r.get("last_verified", now_str[:10]),
                            r.get("created_at", now_str),
                            r.get("updated_at", now_str)
                        ))
                    conn.commit()
                except Exception as e:
                    logger.warning(f"Error seeding learning resources: {e}")

    conn.close()


# Initialize database automatically on import
init_db()
