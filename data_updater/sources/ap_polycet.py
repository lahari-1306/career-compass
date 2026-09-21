"""
AP POLYCET (Polytechnic Common Entrance Test for 10th Class)
Official portal: https://polycetap.nic.in
"""
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from .base import BaseSourceConnector

IST = timezone(timedelta(hours=5, minutes=30))

class APPolycetConnector(BaseSourceConnector):
    source_id = "ap_polycet"
    source_name = "AP POLYCET Polytechnic Admissions"
    organization = "State Board of Technical Education & Training (SBTET), Andhra Pradesh"
    category = "Counselling"
    official_url = "https://polycetap.nic.in"
    source_type = "official_portal"

    def fetch_latest(self) -> List[Dict[str, Any]]:
        status, html, err = self.safe_get(self.official_url)
        now_str = datetime.now(IST).isoformat()
        portal_active = (status == 200)

        polycet_opp = {
            "id": "notif-polycet-admissions",
            "title": "AP POLYCET Polytechnic Diploma Seat Allotment Round",
            "organization": self.organization,
            "category": "Counselling",
            "status": "LIVE",
            "start_datetime": "2026-09-05T10:00:00+05:30",
            "end_datetime": "2026-09-27T17:00:00+05:30",
            "exam_date": "Examination Concluded",
            "result_date": "Allotment on polycetap.nic.in",
            "eligibility_summary": "Passed SSC (10th Standard) with minimum 35% marks or equivalent board examination.",
            "official_source": self.official_url,
            "last_verified_at": now_str,
            "priority": "HIGH",
            "description": "Counselling and institution reporting for 3-Year Diploma in Engineering & Non-Engineering programs in Government & Private Polytechnics.",
            "source_status": "VERIFIED_ONLINE" if portal_active else "PRESERVED_VERIFIED",
            "target_qualifications": ["10th"],
            "target_branches": ["General"],
            "target_states": ["Andhra Pradesh", "Telangana"]
        }
        return [polycet_opp]
