"""
Automated Backup and Rollback Manager
Provides zero-data-loss protection before every update.
"""
import os
import shutil
import glob
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
BACKUP_DIR = os.path.join(DATA_DIR, "backups")
NOTIFICATIONS_FILE = os.path.join(DATA_DIR, "notifications.json")

class BackupManager:
    @staticmethod
    def create_backup() -> str:
        os.makedirs(BACKUP_DIR, exist_ok=True)
        if not os.path.exists(NOTIFICATIONS_FILE):
            return ""

        timestamp = datetime.now(IST).strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(BACKUP_DIR, f"notifications_{timestamp}.json")
        shutil.copy2(NOTIFICATIONS_FILE, backup_path)
        BackupManager._rotate_backups(keep=10)
        return backup_path

    @staticmethod
    def _rotate_backups(keep: int = 10):
        backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "notifications_*.json")), reverse=True)
        for stale in backups[keep:]:
            try:
                os.remove(stale)
            except Exception:
                pass

    @staticmethod
    def rollback_latest() -> bool:
        backups = sorted(glob.glob(os.path.join(BACKUP_DIR, "notifications_*.json")), reverse=True)
        if not backups:
            return False
        latest_backup = backups[0]
        shutil.copy2(latest_backup, NOTIFICATIONS_FILE)
        return True
