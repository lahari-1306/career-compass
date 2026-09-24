"""
Production Standalone Background Pipeline Runner for CareerCompass.
Designed for Render Cron Jobs, scheduled workers, or CLI execution.
Executes:
1. Official Source Fetch & Validation (DataUpdater)
2. Verified Change Detection & Backup
3. Multi-User Opportunity Matching (RadarMatcher)
4. Multi-Channel Notification Dispatch (In-App, SMTP Email, VAPID Web Push)
"""

import sys
import json
import logging
from datetime import datetime, timezone, timedelta

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("careercompass.cron")

from database import init_db
from data_updater.updater import DataUpdater
from services.pipeline_service import PipelineService
from app import load_json


def main():
    logger.info("=== Starting CareerCompass Scheduled Verification & Dispatch Pipeline ===")
    init_db()

    # Step 1: Run Data Updater across all registered official sources
    updater = DataUpdater(dry_run=False, verbose=True)
    update_report = updater.run_update()
    logger.info(f"DataUpdater complete: {update_report['sources_successful']}/{update_report['sources_checked']} sources succeeded. New: {update_report['new_count']}, Modified: {update_report['modified_count']}")

    # Step 2: Run personalized matching & multi-channel notification dispatch
    all_notifs = load_json("notifications.json")
    dispatch_report = PipelineService.run_matching_and_dispatch_for_all_users(all_notifs)
    logger.info(f"Dispatch complete: Processed {dispatch_report['total_users_processed']} users. In-App: {dispatch_report['in_app_delivered']}, Emails: {dispatch_report['emails_sent']}, Push: {dispatch_report['pushes_sent']}")

    logger.info("=== Pipeline run completed successfully ===")


if __name__ == "__main__":
    main()
