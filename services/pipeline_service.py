"""
Unified Notification Pipeline Service for CareerCompass.
Executes the exact production flow:
OFFICIAL SOURCE -> FETCH -> VALIDATE -> VERIFY -> STORE OPPORTUNITY ->
MATCH AGAINST USER PROFILES -> CREATE PERSONALIZED NOTIFICATION ->
IN-APP -> EMAIL -> BROWSER PUSH -> TRACK DELIVERY
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone, timedelta

from database import get_db_connection, now_ist_iso, IST
from db_repository import (
    NotificationRepository, SettingsRepository, PushRepository,
    ProfileRepository
)
from radar.matcher import RadarMatcher
from services.email_service import EmailService
from services.push_service import PushService

logger = logging.getLogger("careercompass.pipeline")


class PipelineService:
    @staticmethod
    def run_matching_and_dispatch_for_all_users(opportunities: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """
        Executes personalized matching and multi-channel delivery (In-App, Email, Push)
        for every registered user based on their education-level aware profile.
        """
        if opportunities is None:
            opportunities = NotificationRepository.get_all_active_notifications()

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, name FROM users WHERE is_verified = 1")
        users = [dict(r) for r in cursor.fetchall()]
        conn.close()

        stats = {
            "total_users_processed": len(users),
            "in_app_delivered": 0,
            "emails_sent": 0,
            "pushes_sent": 0,
            "skipped_duplicates": 0
        }

        for user in users:
            u_id = user["id"]
            u_email = user["email"]
            u_name = user["name"]

            profile = ProfileRepository.get_profile(u_id)
            if not profile:
                continue

            settings = SettingsRepository.get_settings(u_id)
            notif_prefs = settings.get("notifications", {})
            user_prefs = settings.get("preferences", {})

            # Match opportunities against this user's profile
            matches = RadarMatcher.match(profile, opportunities)

            for m in matches:
                opp_id = m.get("opportunity_id") or m.get("id")
                title = m.get("title", "")
                org = m.get("organization", "")
                deadline = m.get("end_datetime") or m.get("deadline", "Check official portal")
                days_left = m.get("days_remaining")
                official_url = m.get("official_source") or m.get("official_application_url") or "/"
                reason = m.get("match_reasons", ["Matches your educational stream and target direction"])[0] if m.get("match_reasons") else "Matches your profile"

                # Check if this type of alert is allowed by user preferences
                is_deadline = days_left is not None and days_left <= 5
                if is_deadline and not notif_prefs.get("deadlines", 1):
                    continue
                if not is_deadline and not notif_prefs.get("new_opportunities", 1):
                    continue

                if is_deadline:
                    msg = f"URGENT: Application deadline for {title} closes in {days_left} days!"
                else:
                    msg = f"New verified opportunity matching your profile: {title} ({org})."

                # 1. Channel A: In-App Notification
                if notif_prefs.get("in_app_channel", 1):
                    delivery_id = NotificationRepository.create_delivery(
                        user_id=u_id,
                        notification_id=opp_id,
                        channel="IN_APP",
                        title=title,
                        message=msg,
                        deep_link=f"/#radar-opportunity-{opp_id}",
                        status="SENT"
                    )
                    if delivery_id:
                        stats["in_app_delivered"] += 1
                    else:
                        stats["skipped_duplicates"] += 1

                # 2. Channel B: Email
                if user_prefs.get("email_notifications_enabled", 1) and notif_prefs.get("email_channel", 1):
                    if not NotificationRepository.has_delivered(u_id, opp_id, "EMAIL"):
                        try:
                            if is_deadline:
                                email_res = EmailService.send_deadline_reminder(
                                    to_email=u_email,
                                    user_name=u_name,
                                    opp_title=title,
                                    org=org,
                                    days_left=days_left or 0,
                                    official_url=official_url
                                )
                            else:
                                email_res = EmailService.send_opportunity_alert(
                                    to_email=u_email,
                                    user_name=u_name,
                                    opp_title=title,
                                    org=org,
                                    deadline=deadline,
                                    deep_link=official_url,
                                    reason=reason
                                )
                            
                            status_code = "SENT" if email_res.get("status") in ("sent", "queued_dev_logged") else "FAILED"
                            NotificationRepository.create_delivery(
                                user_id=u_id,
                                notification_id=opp_id,
                                channel="EMAIL",
                                title=title,
                                message=msg,
                                deep_link=official_url,
                                status=status_code
                            )
                            if status_code == "SENT":
                                stats["emails_sent"] += 1
                        except Exception as e:
                            logger.error(f"Failed sending opportunity email to {u_email}: {e}")

                # 3. Channel C: Browser Web Push
                if user_prefs.get("push_notifications_enabled", 1) and notif_prefs.get("push_channel", 1):
                    if not NotificationRepository.has_delivered(u_id, opp_id, "PUSH"):
                        try:
                            push_results = PushService.send_push_to_user(
                                user_id=u_id,
                                title=title,
                                message=msg,
                                deep_link=f"/#radar-opportunity-{opp_id}",
                                tag=f"opp-{opp_id}"
                            )
                            if push_results:
                                NotificationRepository.create_delivery(
                                    user_id=u_id,
                                    notification_id=opp_id,
                                    channel="PUSH",
                                    title=title,
                                    message=msg,
                                    deep_link=f"/#radar-opportunity-{opp_id}",
                                    status="SENT"
                                )
                                stats["pushes_sent"] += len(push_results)
                        except Exception as e:
                            logger.error(f"Failed sending web push to user {u_id}: {e}")

        logger.info(f"Pipeline dispatch complete: {stats}")
        return stats

    @staticmethod
    def check_learning_resource_links(timeout: int = 5) -> Dict[str, Any]:
        """
        Periodically verifies learning resource URLs:
        - URL reachability
        - Redirects
        - HTTPS protocol
        - Marks broken/failing URLs as 'NEEDS_REVIEW' for admin inspection
        """
        import requests
        from db_repository import LearningResourceRepository
        from database import now_ist_iso

        resources = LearningResourceRepository.get_all(verification_status=None)
        results = {
            "total_checked": len(resources),
            "verified_count": 0,
            "needs_review_count": 0,
            "details": []
        }

        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) CareerCompass-LinkValidator/2.0"
        }

        for r in resources:
            r_id = r["id"]
            url = r.get("official_url", "")
            name = r.get("name", "")
            is_https = url.lower().startswith("https://")
            status = "VERIFIED"
            notes = "Reachable"

            if not url or not is_https:
                status = "NEEDS_REVIEW"
                notes = "Non-HTTPS or empty URL"
            else:
                try:
                    resp = requests.head(url, headers=headers, timeout=timeout, allow_redirects=True)
                    if resp.status_code == 405:
                        resp = requests.get(url, headers=headers, timeout=timeout, stream=True)
                    
                    if resp.status_code in (200, 301, 302, 307, 308, 403):
                        status = "VERIFIED"
                        notes = f"HTTP {resp.status_code} - Verified online"
                    else:
                        status = "NEEDS_REVIEW"
                        notes = f"HTTP {resp.status_code} - Requires review"
                except Exception as e:
                    status = "NEEDS_REVIEW"
                    notes = f"Connection error: {str(e)[:60]}"

            today_str = now_ist_iso()[:10]
            LearningResourceRepository.update_resource(r_id, {
                "verification_status": status,
                "last_verified": today_str
            })

            if status == "VERIFIED":
                results["verified_count"] += 1
            else:
                results["needs_review_count"] += 1

            results["details"].append({
                "id": r_id,
                "name": name,
                "url": url,
                "status": status,
                "notes": notes
            })

        logger.info(f"Learning resource link health check complete: {results['verified_count']} verified, {results['needs_review_count']} need review.")
        return results

