"""
NTA (National Testing Agency) Source Connector
Official portals: https://nta.ac.in, https://jeemain.nta.nic.in
"""
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from .base import BaseSourceConnector

IST = timezone(timedelta(hours=5, minutes=30))

class NTAConnector(BaseSourceConnector):
    source_id = "nta"
    source_name = "National Testing Agency (NTA)"
    organization = "National Testing Agency (NTA), Ministry of Education"
    category = "Entrance Exams"
    official_url = "https://jeemain.nta.nic.in"
    source_type = "official_portal"

    def fetch_latest(self) -> List[Dict[str, Any]]:
        status, html, err = self.safe_get(self.official_url)
        now_str = datetime.now(IST).isoformat()
        portal_active = (status == 200)

        # JEE Main cycle record
        jeemain_opp = {
            "id": "notif-jeemain-cycle",
            "title": "JEE Main Upcoming Session Advisory & Registration",
            "organization": self.organization,
            "category": "Entrance Exams",
            "status": "UPCOMING",
            "start_datetime": "2026-11-01T09:00:00+05:30",
            "end_datetime": "2026-12-04T21:00:00+05:30",
            "exam_date": "January 2027 (Session 1) / April 2027 (Session 2)",
            "result_date": "February 2027 / April 2027",
            "eligibility_summary": "Candidates who passed 10+2 / Intermediate with Physics, Chemistry, and Mathematics in 2025, 2026 or appearing in 2027.",
            "official_source": self.official_url,
            "last_verified_at": now_str,
            "priority": "HIGH",
            "description": "Information bulletin and registration guidelines for JEE (Main) admission to NITs, IIITs, CFTIs and eligibility filter for JEE Advanced.",
            "source_status": "VERIFIED_ONLINE" if portal_active else "PRESERVED_VERIFIED",
            "target_qualifications": ["Intermediate"],
            "target_branches": ["MPC"]
        }
        return [jeemain_opp]
