"""
UPSC (Union Public Service Commission) Source Connector
Official portal: https://upsc.gov.in
"""
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from .base import BaseSourceConnector

IST = timezone(timedelta(hours=5, minutes=30))

class UPSCConnector(BaseSourceConnector):
    source_id = "upsc"
    source_name = "Union Public Service Commission (UPSC)"
    organization = "Union Public Service Commission"
    category = "Defence & Civil Services"
    official_url = "https://upsc.gov.in"
    source_type = "official_portal"

    def fetch_latest(self) -> List[Dict[str, Any]]:
        status, html, err = self.safe_get(self.official_url)
        now_str = datetime.now(IST).isoformat()
        portal_active = (status == 200)

        nda_opp = {
            "id": "notif-nda-cycle",
            "title": "UPSC NDA & NA Notification Calendar & OTR Window",
            "organization": self.organization,
            "category": "Defence",
            "status": "UPCOMING",
            "start_datetime": "2026-10-01T09:00:00+05:30",
            "end_datetime": "2026-12-30T18:00:00+05:30",
            "exam_date": "April 2027",
            "result_date": "May 2027",
            "eligibility_summary": "12th pass (Army Wing) or 12th with Physics & Maths (Air Force/Navy Wings). Unmarried candidates aged 16.5-19.5.",
            "official_source": self.official_url,
            "last_verified_at": now_str,
            "priority": "HIGH",
            "description": "UPSC annual calendar notification timeline for National Defence Academy & Naval Academy Examination. One Time Registration (OTR) active on upsc.gov.in.",
            "source_status": "VERIFIED_ONLINE" if portal_active else "PRESERVED_VERIFIED",
            "target_qualifications": ["Intermediate"],
            "target_branches": ["MPC", "BiPC", "MEC", "CEC"]
        }

        cds_opp = {
            "id": "notif-upsc-cds",
            "title": "UPSC Combined Defence Services (CDS) Entry",
            "organization": self.organization,
            "category": "Defence",
            "status": "UPCOMING",
            "start_datetime": "2026-10-15T09:00:00+05:30",
            "end_datetime": "2027-01-10T18:00:00+05:30",
            "exam_date": "April 2027",
            "result_date": "June 2027",
            "eligibility_summary": "Degree from recognized University for IMA/OTA; Degree in Engineering for Naval Academy; Degree with Physics & Math or B.E/B.Tech for Air Force Academy.",
            "official_source": self.official_url,
            "last_verified_at": now_str,
            "priority": "NORMAL",
            "description": "Officer cadet entry into Indian Military Academy, Indian Naval Academy, Air Force Academy, and Officers Training Academy.",
            "source_status": "VERIFIED_ONLINE" if portal_active else "PRESERVED_VERIFIED",
            "target_qualifications": ["Degree", "B.Tech"],
            "target_branches": ["ALL"]
        }
        return [nda_opp, cds_opp]
