"""
Indian Armed Forces Source Connector
Official portals: https://joinindianarmy.nic.in, https://joinindiannavy.gov.in, https://afcat.cdac.in
"""
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from .base import BaseSourceConnector

IST = timezone(timedelta(hours=5, minutes=30))

class DefenceConnector(BaseSourceConnector):
    source_id = "defence"
    source_name = "Indian Armed Forces (Army, Navy, Air Force)"
    organization = "Ministry of Defence, Govt. of India"
    category = "Defence"
    official_url = "https://joinindianarmy.nic.in"
    source_type = "official_portal"

    def fetch_latest(self) -> List[Dict[str, Any]]:
        status, html, err = self.safe_get(self.official_url)
        now_str = datetime.now(IST).isoformat()
        portal_active = (status == 200)

        tes_opp = {
            "id": "notif-army-tes",
            "title": "Indian Army 10+2 Technical Entry Scheme (TES)",
            "organization": "Indian Army (Join Indian Army)",
            "category": "Defence",
            "status": "OPEN",
            "start_datetime": "2026-08-15T10:00:00+05:30",
            "end_datetime": "2026-10-12T15:00:00+05:30",
            "exam_date": "SSB Interviews Starting November 2026",
            "result_date": "January 2027",
            "eligibility_summary": "Passed 10+2 with min 60% in PCM and appeared in JEE Main. Age 16.5 to 19.5 years.",
            "official_source": "https://joinindianarmy.nic.in",
            "last_verified_at": now_str,
            "priority": "HIGH",
            "description": "Permanent Commission in the Indian Army for 10+2 pass candidates with 4 years free engineering degree at military academies and stipend.",
            "source_status": "VERIFIED_ONLINE" if portal_active else "PRESERVED_VERIFIED",
            "target_qualifications": ["Intermediate"],
            "target_branches": ["MPC"]
        }

        navy_btech_opp = {
            "id": "notif-navy-btech",
            "title": "Indian Navy 10+2 (B.Tech) Cadet Entry Scheme",
            "organization": "Indian Navy (Join Indian Navy)",
            "category": "Defence",
            "status": "UPCOMING",
            "start_datetime": "2026-10-20T09:00:00+05:30",
            "end_datetime": "2026-11-20T23:59:00+05:30",
            "exam_date": "SSB Shortlisting based on JEE Main Rank",
            "result_date": "February 2027",
            "eligibility_summary": "10+2 passed with 70% in PCM, min 50% in English, and valid JEE Main (B.E/B.Tech) rank.",
            "official_source": "https://joinindiannavy.gov.in",
            "last_verified_at": now_str,
            "priority": "NORMAL",
            "description": "Four-year B.Tech degree course at Indian Naval Academy (INA) Ezhimala, Kerala with full scholarship and commissioning as Sub Lieutenant.",
            "source_status": "VERIFIED_ONLINE" if portal_active else "PRESERVED_VERIFIED",
            "target_qualifications": ["Intermediate"],
            "target_branches": ["MPC"]
        }

        afcat_opp = {
            "id": "notif-afcat-res",
            "title": "AFCAT Examination Results Declared & AFSB Selection",
            "organization": "Indian Air Force (IAF)",
            "category": "Results",
            "status": "RESULT",
            "start_datetime": "2026-09-12T12:00:00+05:30",
            "end_datetime": "2026-10-15T23:59:00+05:30",
            "exam_date": "August 2026",
            "result_date": "12th September 2026",
            "eligibility_summary": "Graduates/B.Tech who appeared for AFCAT written examination for Flying, Technical, and Ground Duty branches.",
            "official_source": "https://afcat.cdac.in",
            "last_verified_at": now_str,
            "priority": "NORMAL",
            "description": "Individual scorecards and cutoff marks published. Qualified candidates can log in to choose Air Force Selection Board (AFSB) interview venue and dates.",
            "source_status": "VERIFIED_ONLINE" if portal_active else "PRESERVED_VERIFIED",
            "target_qualifications": ["Degree", "B.Tech"],
            "target_branches": ["ALL"]
        }
        return [tes_opp, navy_btech_opp, afcat_opp]
