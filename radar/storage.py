"""
Storage layer for Radar profiles, notification history, and in-app alerts.
"""
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
PROFILES_FILE = os.path.join(DATA_DIR, "radar_profiles.json")
HISTORY_FILE = os.path.join(DATA_DIR, "notification_history.json")
ALERTS_FILE = os.path.join(DATA_DIR, "user_alerts.json")

class RadarStorage:
    @staticmethod
    def _read_json(filepath: str, default: Any) -> Any:
        if not os.path.exists(filepath):
            return default
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default

    @staticmethod
    def _write_json(filepath: str, data: Any) -> None:
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        temp_path = filepath + ".tmp"
        with open(temp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(temp_path, filepath)

    # ----------------------------------------------------
    # Profile Operations
    # ----------------------------------------------------
    @staticmethod
    def get_profile(profile_id: str) -> Optional[Dict[str, Any]]:
        profiles = RadarStorage._read_json(PROFILES_FILE, {})
        return profiles.get(profile_id)

    @staticmethod
    def save_profile(profile_data: Dict[str, Any]) -> Dict[str, Any]:
        profiles = RadarStorage._read_json(PROFILES_FILE, {})
        profile_id = profile_data.get("profile_id")
        if not profile_id:
            profile_id = "prof_" + datetime.now(IST).strftime("%Y%m%d%H%M%S%f")
            profile_data["profile_id"] = profile_id

        profile_data["updated_at"] = datetime.now(IST).isoformat()
        if "created_at" not in profile_data:
            profile_data["created_at"] = profile_data["updated_at"]

        profiles[profile_id] = profile_data
        RadarStorage._write_json(PROFILES_FILE, profiles)
        return profile_data

    @staticmethod
    def list_all_profiles() -> List[Dict[str, Any]]:
        profiles = RadarStorage._read_json(PROFILES_FILE, {})
        return list(profiles.values())

    # ----------------------------------------------------
    # Duplicate Prevention & Notification History
    # ----------------------------------------------------
    @staticmethod
    def has_notified(profile_id: str, opportunity_id: str, state_fingerprint: str) -> bool:
        history = RadarStorage._read_json(HISTORY_FILE, {})
        user_history = history.get(profile_id, {})
        prev_fingerprint = user_history.get(opportunity_id)
        return prev_fingerprint == state_fingerprint

    @staticmethod
    def record_notification(profile_id: str, opportunity_id: str, state_fingerprint: str) -> None:
        history = RadarStorage._read_json(HISTORY_FILE, {})
        if profile_id not in history:
            history[profile_id] = {}
        history[profile_id][opportunity_id] = state_fingerprint
        RadarStorage._write_json(HISTORY_FILE, history)

    # ----------------------------------------------------
    # In-App Alerts Drawer
    # ----------------------------------------------------
    @staticmethod
    def get_alerts_for_profile(profile_id: str) -> List[Dict[str, Any]]:
        all_alerts = RadarStorage._read_json(ALERTS_FILE, {})
        return all_alerts.get(profile_id, [])

    @staticmethod
    def add_alert_for_profile(profile_id: str, alert_item: Dict[str, Any]) -> None:
        all_alerts = RadarStorage._read_json(ALERTS_FILE, {})
        user_alerts = all_alerts.get(profile_id, [])
        # Prepend to list
        user_alerts.insert(0, alert_item)
        # Limit to 50 active alerts per user
        all_alerts[profile_id] = user_alerts[:50]
        RadarStorage._write_json(ALERTS_FILE, all_alerts)

    @staticmethod
    def mark_alerts_read(profile_id: str, alert_ids: Optional[List[str]] = None) -> int:
        all_alerts = RadarStorage._read_json(ALERTS_FILE, {})
        user_alerts = all_alerts.get(profile_id, [])
        updated_count = 0
        for alert in user_alerts:
            if alert_ids is None or alert.get("alert_id") in alert_ids:
                if not alert.get("is_read"):
                    alert["is_read"] = True
                    updated_count += 1
        all_alerts[profile_id] = user_alerts
        RadarStorage._write_json(ALERTS_FILE, all_alerts)
        return updated_count
