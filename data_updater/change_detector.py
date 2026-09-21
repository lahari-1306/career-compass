"""
Change Detection and Audit Trail Module
Compares incoming verified data with existing notifications and tracks state transitions in data/change_history.json.
"""
import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Tuple

IST = timezone(timedelta(hours=5, minutes=30))
CHANGE_HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "change_history.json")

class ChangeDetector:
    @staticmethod
    def load_history() -> List[Dict[str, Any]]:
        if not os.path.exists(CHANGE_HISTORY_FILE):
            return []
        try:
            with open(CHANGE_HISTORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    @staticmethod
    def log_change(change_entry: Dict[str, Any]) -> None:
        history = ChangeDetector.load_history()
        history.insert(0, change_entry)
        # Retain last 200 change events
        history = history[:200]
        os.makedirs(os.path.dirname(CHANGE_HISTORY_FILE), exist_ok=True)
        with open(CHANGE_HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, indent=2, ensure_ascii=False)

    @staticmethod
    def detect_changes(existing_list: List[Dict[str, Any]], incoming_opp: Dict[str, Any]) -> Tuple[str, List[str]]:
        """
        Returns (change_type, details_list)
        change_type: 'NEW' | 'DEADLINE_CHANGED' | 'EXAM_DATE_CHANGED' | 'STATUS_CHANGED' | 'VERIFICATION_REFRESH' | 'UNCHANGED'
        """
        opp_id = incoming_opp.get("id")
        existing_match = next((item for item in existing_list if item.get("id") == opp_id), None)
        
        if not existing_match:
            return "NEW", [f"Newly announced verified opportunity: '{incoming_opp.get('title')}'"]

        changes = []
        # Check deadline changes
        if existing_match.get("end_datetime") != incoming_opp.get("end_datetime"):
            changes.append(f"Deadline updated from {existing_match.get('end_datetime')} to {incoming_opp.get('end_datetime')}")

        # Check exam date changes
        if existing_match.get("exam_date") != incoming_opp.get("exam_date"):
            changes.append(f"Exam date updated from {existing_match.get('exam_date')} to {incoming_opp.get('exam_date')}")

        # Check status changes
        if existing_match.get("status") != incoming_opp.get("status"):
            changes.append(f"Status changed from {existing_match.get('status')} to {incoming_opp.get('status')}")

        if changes:
            if "Deadline updated" in changes[0]:
                return "DEADLINE_CHANGED", changes
            if "Exam date" in changes[0]:
                return "EXAM_DATE_CHANGED", changes
            if "Status changed" in changes[0]:
                return "STATUS_CHANGED", changes
            return "MODIFIED", changes

        return "UNCHANGED", []
