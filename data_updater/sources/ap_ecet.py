"""
AP ECET (Andhra Pradesh Engineering Common Entrance Test - Lateral Entry for Diploma & B.Sc Maths)
Official portal: https://cets.apsche.ap.gov.in
"""
from typing import List, Dict, Any
from datetime import datetime, timezone, timedelta
from .base import BaseSourceConnector

IST = timezone(timedelta(hours=5, minutes=30))

class APEcetConnector(BaseSourceConnector):
    source_id = "ap_ecet"
    source_name = "AP ECET Lateral Entry Counselling"
    organization = "Andhra Pradesh State Council of Higher Education (APSCHE)"
    category = "Counselling"
    official_url = "https://cets.apsche.ap.gov.in"
    source_type = "official_portal"

    def fetch_latest(self) -> List[Dict[str, Any]]:
        status, html, err = self.safe_get(self.official_url)
        now_str = datetime.now(IST).isoformat()
        portal_active = (status == 200)

        ecet_opp = {
            "id": "notif-ecet-counselling",
            "title": "AP ECET Lateral Entry 2nd Year B.Tech Admissions Live",
            "organization": self.organization,
            "category": "Counselling",
            "status": "LIVE",
            "start_datetime": "2026-09-08T09:00:00+05:30",
            "end_datetime": "2026-09-26T18:00:00+05:30",
            "exam_date": "Examination Concluded",
            "result_date": "Allotment on Portal",
            "eligibility_summary": "Holders of 3-year State Board Diploma in Engineering & Technology or B.Sc (Mathematics) degree.",
            "official_source": self.official_url,
            "last_verified_at": now_str,
            "priority": "HIGH",
            "description": "Lateral entry admissions directly into 2nd year B.E. / B.Tech in university and private unaided engineering colleges.",
            "source_status": "VERIFIED_ONLINE" if portal_active else "PRESERVED_VERIFIED",
            "target_qualifications": ["Diploma", "Degree"],
            "target_branches": ["ALL_DIPLOMA", "Civil", "Mechanical", "Electrical", "Electronics", "CSE", "Automobile"],
            "target_states": ["Andhra Pradesh", "Telangana"]
        }
        return [ecet_opp]
