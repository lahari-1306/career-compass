"""
Data Models for "MY CAREER RADAR" Personalized Notification System
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, timedelta

IST = timezone(timedelta(hours=5, minutes=30))

@dataclass
class StudentProfile:
    profile_id: str = ""
    full_name: str = ""
    qualification: str = "B.Tech"  # '10th', 'Intermediate', 'Diploma', 'Degree', 'B.Tech', 'Postgraduate'
    stream_or_branch: str = "CSE"  # 'CSE', 'ECE', 'Mechanical', 'Civil', 'EEE', 'MPC', 'BiPC', etc.
    completion_year: str = "2026"
    completion_status: str = "Final Year"  # 'Currently Studying', 'Final Year', 'Completed'
    state: str = "Andhra Pradesh"
    category: str = "General"      # 'General', 'OBC', 'SC', 'ST', 'EWS'
    interests: List[str] = field(default_factory=lambda: ["Higher Studies / M.Tech", "PSU / Govt Jobs", "Scholarships"])
    email: Optional[str] = None
    email_alerts_enabled: bool = False
    created_at: str = field(default_factory=lambda: datetime.now(IST).isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now(IST).isoformat())

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "StudentProfile":
        valid_fields = cls.__dataclass_fields__.keys()
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

@dataclass
class RadarMatch:
    opportunity_id: str
    title: str
    organization: str
    category: str
    status: str
    start_datetime: Optional[str]
    end_datetime: Optional[str]
    exam_date: Optional[str]
    result_date: Optional[str]
    official_source: str
    last_verified_at: str
    eligibility_summary: str
    match_score: int              # 0 to 100
    match_reasons: List[str]      # "Why am I seeing this?"
    urgency: str                  # 'HIGH', 'MEDIUM', 'NORMAL'
    days_remaining: Optional[int] = None
    disclaimer: str = "Criteria shown are derived from official notifications. Confirm complete details in the official brochure."

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

@dataclass
class RadarAlert:
    alert_id: str
    profile_id: str
    opportunity_id: str
    title: str
    organization: str
    alert_type: str               # 'NEW_OPPORTUNITY', 'DEADLINE_APPROACHING', 'EXAM_DATE_UPDATE', 'STATUS_CHANGE'
    message: str
    official_source: str
    urgency: str
    created_at: str = field(default_factory=lambda: datetime.now(IST).isoformat())
    is_read: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
