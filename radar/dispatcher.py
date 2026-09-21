"""
Alert Dispatcher for "MY CAREER RADAR"
Dispatches personalized alerts to profiles with strict duplicate prevention and rate limiting.
"""
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
import hashlib

from .models import RadarAlert
from .matcher import RadarMatcher
from .storage import RadarStorage

IST = timezone(timedelta(hours=5, minutes=30))

class RadarDispatcher:
    @staticmethod
    def _create_fingerprint(opp: Dict[str, Any]) -> str:
        raw_key = f"{opp.get('id', '')}_{opp.get('end_datetime', '')}_{opp.get('exam_date', '')}_{opp.get('status', '')}"
        return hashlib.md5(raw_key.encode("utf-8")).hexdigest()

    @staticmethod
    def dispatch_for_profile(profile_data: Dict[str, Any], opportunities: List[Dict[str, Any]]) -> int:
        """
        Evaluates opportunities for a single profile and adds new unread alerts if matched.
        """
        profile_id = profile_data.get("profile_id")
        if not profile_id:
            return 0

        matches = RadarMatcher.match(profile_data, opportunities)
        dispatched_count = 0

        for m in matches:
            opp_id = m.get("opportunity_id")
            fingerprint = RadarDispatcher._create_fingerprint(m)

            # Prevent duplicate alerts
            if RadarStorage.has_notified(profile_id, opp_id, fingerprint):
                continue

            # Determine alert message based on urgency and status
            status = m.get("status", "OPEN")
            urgency = m.get("urgency", "NORMAL")
            days_left = m.get("days_remaining")

            if days_left is not None and days_left <= 5:
                msg = f"URGENT: Application deadline for {m.get('title')} closes in {days_left} days!"
                alert_type = "DEADLINE_APPROACHING"
            elif status == "RESULT":
                msg = f"Official Results / Scorecards declared for {m.get('title')}."
                alert_type = "EXAM_DATE_UPDATE"
            else:
                msg = f"New verified opportunity matching your profile: {m.get('title')}."
                alert_type = "NEW_OPPORTUNITY"

            alert = RadarAlert(
                alert_id=f"alert_{opp_id}_{datetime.now(IST).strftime('%Y%m%d%H%M%S%f')}",
                profile_id=profile_id,
                opportunity_id=opp_id,
                title=m.get("title", ""),
                organization=m.get("organization", ""),
                alert_type=alert_type,
                message=msg,
                official_source=m.get("official_source", ""),
                urgency=urgency,
                created_at=datetime.now(IST).isoformat(),
                is_read=False
            )

            RadarStorage.add_alert_for_profile(profile_id, alert.to_dict())
            RadarStorage.record_notification(profile_id, opp_id, fingerprint)
            dispatched_count += 1

        return dispatched_count

    @staticmethod
    def dispatch_for_all_profiles(opportunities: List[Dict[str, Any]]) -> int:
        """
        Runs batch matching and dispatch across all registered student profiles.
        """
        profiles = RadarStorage.list_all_profiles()
        total_dispatched = 0
        for prof in profiles:
            total_dispatched += RadarDispatcher.dispatch_for_profile(prof, opportunities)
        return total_dispatched
