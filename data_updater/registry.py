"""
Official Source Registry Manager
Maintains audit trail and connectivity status for all official sources in data/source_registry.json
"""
import os
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List

IST = timezone(timedelta(hours=5, minutes=30))
REGISTRY_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "source_registry.json")

DEFAULT_REGISTRY = [
    {
        "source_id": "gate",
        "source_name": "GATE Organizing Institute Portal",
        "organization": "IIT / IISc National Coordination Board",
        "official_url": "https://gate2025.iitr.ac.in",
        "category": "Entrance Exams",
        "check_interval_hours": 12,
        "last_checked_at": None,
        "last_success_at": None,
        "status": "INITIALIZED",
        "error_count": 0,
        "notes": "Organized on rotation by IITs / IISc. Whitelisted domain .ac.in"
    },
    {
        "source_id": "nta",
        "source_name": "National Testing Agency (JEE Main Portal)",
        "organization": "National Testing Agency (NTA)",
        "official_url": "https://jeemain.nta.nic.in",
        "category": "Entrance Exams",
        "check_interval_hours": 12,
        "last_checked_at": None,
        "last_success_at": None,
        "status": "INITIALIZED",
        "error_count": 0,
        "notes": "Central government agency. Whitelisted domain .nic.in / .ac.in"
    },
    {
        "source_id": "upsc",
        "source_name": "Union Public Service Commission Examination Portal",
        "organization": "UPSC",
        "official_url": "https://upsc.gov.in",
        "category": "Defence & Civil Services",
        "check_interval_hours": 12,
        "last_checked_at": None,
        "last_success_at": None,
        "status": "INITIALIZED",
        "error_count": 0,
        "notes": "Constitutional authority. Whitelisted domain .gov.in"
    },
    {
        "source_id": "rrb",
        "source_name": "Railway Recruitment Boards Centralized Portal",
        "organization": "Ministry of Railways",
        "official_url": "https://rrbcdg.gov.in",
        "category": "Government Jobs",
        "check_interval_hours": 12,
        "last_checked_at": None,
        "last_success_at": None,
        "status": "INITIALIZED",
        "error_count": 0,
        "notes": "Central government railway recruitment. Whitelisted domain .gov.in"
    },
    {
        "source_id": "defence",
        "source_name": "Indian Armed Forces Official Portals",
        "organization": "Ministry of Defence",
        "official_url": "https://joinindianarmy.nic.in",
        "category": "Defence",
        "check_interval_hours": 12,
        "last_checked_at": None,
        "last_success_at": None,
        "status": "INITIALIZED",
        "error_count": 0,
        "notes": "Armed forces recruitment portals. Whitelisted domains .nic.in / .gov.in / .cdac.in"
    },
    {
        "source_id": "ap_eapcet",
        "source_name": "AP EAPCET State Admissions Portal",
        "organization": "APSCHE",
        "official_url": "https://cets.apsche.ap.gov.in",
        "category": "Counselling",
        "check_interval_hours": 6,
        "last_checked_at": None,
        "last_success_at": None,
        "status": "INITIALIZED",
        "error_count": 0,
        "notes": "State Council of Higher Education Andhra Pradesh. Whitelisted domain .gov.in"
    },
    {
        "source_id": "ap_ecet",
        "source_name": "AP ECET Lateral Entry Admissions Portal",
        "organization": "APSCHE",
        "official_url": "https://cets.apsche.ap.gov.in",
        "category": "Counselling",
        "check_interval_hours": 6,
        "last_checked_at": None,
        "last_success_at": None,
        "status": "INITIALIZED",
        "error_count": 0,
        "notes": "Lateral entry for Diploma holders. Whitelisted domain .gov.in"
    },
    {
        "source_id": "ap_polycet",
        "source_name": "AP POLYCET Polytechnic Admissions Portal",
        "organization": "SBTET Andhra Pradesh",
        "official_url": "https://polycetap.nic.in",
        "category": "Counselling",
        "check_interval_hours": 6,
        "last_checked_at": None,
        "last_success_at": None,
        "status": "INITIALIZED",
        "error_count": 0,
        "notes": "State Board of Technical Education. Whitelisted domain .nic.in"
    }
]

class SourceRegistry:
    @staticmethod
    def load() -> List[Dict[str, Any]]:
        if not os.path.exists(REGISTRY_FILE):
            SourceRegistry.save(DEFAULT_REGISTRY)
            return DEFAULT_REGISTRY
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else DEFAULT_REGISTRY
        except Exception:
            return DEFAULT_REGISTRY

    @staticmethod
    def save(registry_data: List[Dict[str, Any]]) -> None:
        os.makedirs(os.path.dirname(REGISTRY_FILE), exist_ok=True)
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry_data, f, indent=2, ensure_ascii=False)

    @staticmethod
    def record_attempt(source_id: str, success: bool, error_msg: str = None) -> None:
        entries = SourceRegistry.load()
        now_str = datetime.now(IST).isoformat()
        for entry in entries:
            if entry.get("source_id") == source_id:
                entry["last_checked_at"] = now_str
                if success:
                    entry["last_success_at"] = now_str
                    entry["status"] = "VERIFIED_ACTIVE"
                    entry["error_count"] = 0
                    entry["last_error"] = None
                else:
                    entry["error_count"] = entry.get("error_count", 0) + 1
                    entry["status"] = "DEGRADED" if entry["error_count"] < 3 else "SOURCE_UNAVAILABLE"
                    entry["last_error"] = error_msg
                break
        SourceRegistry.save(entries)
