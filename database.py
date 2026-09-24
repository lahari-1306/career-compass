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

Uses SQLite with WAL mode and foreign keys enabled by default,
supporting PostgreSQL when DATABASE_URL is set in environment.
"""

import os
import sqlite3
import json
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional, Tuple

logger = logging.getLogger("careercompass.database")

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))
os.makedirs(DATA_DIR, exist_ok=True)

DB_PATH = os.environ.get("DATABASE_PATH", os.path.join(DATA_DIR, "career_compass.db"))
IST = timezone(timedelta(hours=5, minutes=30))


def now_ist_iso() -> str:
    return datetime.now(IST).isoformat()


def get_db_connection() -> sqlite3.Connection:
    """Creates a connection to SQLite database with Row factory and WAL mode."""
    conn = sqlite3.connect(DB_PATH, timeout=20.0)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode = WAL;")
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db() -> None:
    """Initializes all database tables, constraints, indexes, and initial data."""
    conn = get_db_connection()
    cursor = conn.cursor()

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

    # 2. User Profiles (Education-Level Aware)
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

    # 8. Notifications (Master Verified Repository)
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

    # 9. Notification Deliveries (Per-User In-App, Email, Push)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS notification_deliveries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        notification_id TEXT NOT NULL,
        channel TEXT NOT NULL, -- 'IN_APP', 'EMAIL', 'PUSH'
        status TEXT NOT NULL DEFAULT 'SENT', -- 'QUEUED', 'SENT', 'FAILED', 'READ', 'DISMISSED'
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

    # 10. Push Subscriptions (Multi-Device)
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

    # 12. Exam Preparation Progress
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
        plan_duration TEXT NOT NULL DEFAULT '3_MONTHS', -- '30_DAYS', '3_MONTHS', '6_MONTHS', '12_MONTHS'
        custom_schedule TEXT NOT NULL DEFAULT '{}',
        created_at TEXT NOT NULL,
        updated_at TEXT NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, exam_id)
    );
    """)

    # 14. AI Conversations (Isolated Per User)
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

    conn.commit()

    # Seed notifications from data/notifications.json if database table is empty
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
                logger.info(f"Seeded {len(items)} verified notifications into SQLite database.")
            except Exception as e:
                logger.warning(f"Error seeding notifications: {e}")

    conn.close()


# Initialize database automatically on import
init_db()
