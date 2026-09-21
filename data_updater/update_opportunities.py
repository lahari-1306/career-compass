"""
CLI Entrypoint for Career Compass Official Data Updater
Usage:
    python data_updater/update_opportunities.py [--dry-run] [--source <source_id>] [--verbose]
"""
import sys
import os
import argparse
import json

# Ensure parent directory is on sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from data_updater.updater import DataUpdater

def main():
    parser = argparse.ArgumentParser(description="Career Compass Official Source Data Verification and Update Engine")
    parser.add_argument("--dry-run", action="store_true", help="Simulate update without modifying notifications.json")
    parser.add_argument("--source", type=str, default=None, help="Check only a specific source ID (e.g., gate, nta, upsc, rrb, defence, ap_eapcet, ap_ecet, ap_polycet)")
    parser.add_argument("--verbose", action="store_true", help="Print detailed diagnostic output")
    
    args = parser.parse_args()
    
    print("=" * 65)
    print("CAREER COMPASS — OFFICIAL DATA UPDATE SYSTEM")
    print("Mode:", "DRY RUN (Read Only)" if args.dry_run else "PRODUCTION UPDATE")
    if args.source:
        print(f"Target Source: {args.source}")
    print("=" * 65)

    updater = DataUpdater(dry_run=args.dry_run, verbose=args.verbose)
    report = updater.run_update(target_source_id=args.source)

    print("\n[+] Verification and Update Report:")
    print(f"    - Timestamp:               {report['timestamp']}")
    print(f"    - Official Sources Checked: {report['sources_checked']} ({report['sources_successful']} Success, {report['sources_failed']} Failed)")
    print(f"    - Opportunities Extracted: {report['opportunities_extracted']}")
    print(f"    - Validated (Anti-Halluc.): {report['validated_opportunities']}")
    print(f"    - Newly Announced:         {report['new_count']}")
    print(f"    - Modified / Updated:       {report['modified_count']}")
    print(f"    - Unchanged Verified:      {report['unchanged_count']}")
    print(f"    - Radar Alerts Dispatched: {report['dispatched_radar_alerts']}")
    if "backup_created" in report:
        print(f"    - Backup Snapshot:         {report['backup_created']}")

    if report["validation_failures"]:
        print("\n[!] Validation Warnings/Failures:")
        for failure in report["validation_failures"]:
            print(f"    - Opportunity ID: {failure['id']}")
            for err in failure["errors"]:
                print(f"      * {err}")

    if report["changes_logged"]:
        print("\n[+] State Transitions & Changes:")
        for change in report["changes_logged"]:
            print(f"    - [{change['type']}] {change.get('title')}")
            for d in change.get("details", []):
                print(f"      -> {d}")

    print("=" * 65)
    print("Verification cycle completed successfully.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
