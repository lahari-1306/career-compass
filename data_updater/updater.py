"""
Data Updater Orchestrator
Coordinates official connectors, validation, backups, atomic file writes, change logs, and radar dispatch.
"""
import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from .sources import ALL_CONNECTORS
from .registry import SourceRegistry
from .validator import DataValidator
from .change_detector import ChangeDetector
from .backup import BackupManager

IST = timezone(timedelta(hours=5, minutes=30))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NOTIFICATIONS_FILE = os.path.join(BASE_DIR, "data", "notifications.json")

class DataUpdater:
    def __init__(self, dry_run: bool = False, verbose: bool = False):
        self.dry_run = dry_run
        self.verbose = verbose

    def load_existing_notifications(self) -> List[Dict[str, Any]]:
        if not os.path.exists(NOTIFICATIONS_FILE):
            return []
        try:
            with open(NOTIFICATIONS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except Exception:
            return []

    def run_update(self, target_source_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Runs the full verification and update cycle across official sources.
        """
        existing_notifications = self.load_existing_notifications()
        notifications_map = {n.get("id"): dict(n) for n in existing_notifications if n.get("id")}
        
        report = {
            "timestamp": datetime.now(IST).isoformat(),
            "dry_run": self.dry_run,
            "sources_checked": 0,
            "sources_successful": 0,
            "sources_failed": 0,
            "opportunities_extracted": 0,
            "validated_opportunities": 0,
            "validation_failures": [],
            "new_count": 0,
            "modified_count": 0,
            "unchanged_count": 0,
            "changes_logged": [],
            "dispatched_radar_alerts": 0
        }

        connectors = [cls() for cls in ALL_CONNECTORS]
        if target_source_id:
            connectors = [c for c in connectors if c.source_id == target_source_id]

        new_or_updated_items = []

        for connector in connectors:
            report["sources_checked"] += 1
            source_id = connector.source_id
            
            try:
                extracted_items = connector.fetch_latest()
                SourceRegistry.record_attempt(source_id, success=True)
                report["sources_successful"] += 1
            except Exception as e:
                SourceRegistry.record_attempt(source_id, success=False, error_msg=str(e))
                report["sources_failed"] += 1
                if self.verbose:
                    print(f"[-] Connector '{source_id}' failed: {e}")
                continue

            for item in extracted_items:
                report["opportunities_extracted"] += 1
                
                # Validation check
                is_valid, val_errors = DataValidator.validate_opportunity(item)
                if not is_valid:
                    report["validation_failures"].append({
                        "id": item.get("id"),
                        "errors": val_errors
                    })
                    continue

                report["validated_opportunities"] += 1

                # Change detection
                change_type, change_details = ChangeDetector.detect_changes(list(notifications_map.values()), item)
                
                if change_type == "NEW":
                    report["new_count"] += 1
                    report["changes_logged"].append({
                        "id": item.get("id"),
                        "type": "NEW",
                        "title": item.get("title"),
                        "details": change_details
                    })
                    ChangeDetector.log_change({
                        "timestamp": datetime.now(IST).isoformat(),
                        "opportunity_id": item.get("id"),
                        "type": "NEW",
                        "details": change_details
                    })
                    notifications_map[item["id"]] = item
                    new_or_updated_items.append(item)

                elif change_type != "UNCHANGED":
                    report["modified_count"] += 1
                    report["changes_logged"].append({
                        "id": item.get("id"),
                        "type": change_type,
                        "title": item.get("title"),
                        "details": change_details
                    })
                    ChangeDetector.log_change({
                        "timestamp": datetime.now(IST).isoformat(),
                        "opportunity_id": item.get("id"),
                        "type": change_type,
                        "details": change_details
                    })
                    notifications_map[item["id"]] = item
                    new_or_updated_items.append(item)
                else:
                    report["unchanged_count"] += 1
                    # Refresh last_verified_at without marking as new alert
                    existing_item = notifications_map.get(item["id"])
                    if existing_item:
                        existing_item["last_verified_at"] = item.get("last_verified_at")
                        if "target_qualifications" in item:
                            existing_item["target_qualifications"] = item["target_qualifications"]
                        if "target_branches" in item:
                            existing_item["target_branches"] = item["target_branches"]
                        if "target_states" in item:
                            existing_item["target_states"] = item["target_states"]

        # Atomic file write with backup
        if not self.dry_run and (report["new_count"] > 0 or report["modified_count"] > 0 or report["unchanged_count"] > 0):
            backup_file = BackupManager.create_backup()
            report["backup_created"] = backup_file
            
            updated_list = list(notifications_map.values())
            # Atomic write via temp file
            temp_file = NOTIFICATIONS_FILE + ".tmp"
            with open(temp_file, "w", encoding="utf-8") as f:
                json.dump(updated_list, f, indent=2, ensure_ascii=False)
            os.replace(temp_file, NOTIFICATIONS_FILE)

        # Dispatch updates to Radar profiles if any changes occurred
        if new_or_updated_items:
            try:
                from radar.dispatcher import RadarDispatcher
                dispatched = RadarDispatcher.dispatch_for_all_profiles(new_or_updated_items)
                report["dispatched_radar_alerts"] = dispatched
            except ImportError:
                # Radar dispatcher not loaded yet or offline
                pass
            except Exception as e:
                report["dispatcher_error"] = str(e)

        return report
