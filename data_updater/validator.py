"""
Data Verification & Sanity Engine
Enforces strict domain whitelisting, chronological consistency, and anti-hallucination validation.
"""
import re
from urllib.parse import urlparse
from datetime import datetime
from typing import Dict, Any, Tuple, List

WHITELISTED_DOMAIN_SUFFIXES = (
    ".gov.in",
    ".nic.in",
    ".ac.in",
    ".edu.in",
    ".cdac.in",
    ".iisc.ac.in",
    ".iitr.ac.in",
    ".iitk.ac.in",
    ".iitb.ac.in",
    ".iitd.ac.in",
    ".iitm.ac.in",
    ".iimcat.ac.in",
    ".isro.gov.in",
    ".upsc.gov.in",
    ".nta.ac.in"
)

PROHIBITED_UNVERIFIED_DOMAINS = (
    "sarkariresult.com",
    "shiksha.com",
    "jagranjosh.com",
    "collegedunia.com",
    "careers360.com",
    "testbook.com",
    "adda247.com",
    "freshersworld.com",
    "indiatoday.in"
)

VALID_STATUSES = {"OPEN", "LIVE", "CLOSING_SOON", "UPCOMING", "RESULT", "CLOSED"}

class DataValidator:
    @staticmethod
    def validate_official_url(url: str) -> Tuple[bool, str]:
        if not url or not isinstance(url, str):
            return False, "Missing or non-string official_source URL"
        parsed = urlparse(url.strip())
        if not parsed.scheme or parsed.scheme not in ("http", "https"):
            return False, f"Invalid URL scheme in '{url}' (must be http or https)"
        
        hostname = parsed.hostname or ""
        hostname = hostname.lower()

        # Check for prohibited scraper blogs
        for prohibited in PROHIBITED_UNVERIFIED_DOMAINS:
            if prohibited in hostname:
                return False, f"Prohibited unverified 3rd-party blog domain '{hostname}'. Must use official authority portal."

        # Check whitelisted suffixes or domains
        is_whitelisted = False
        for suffix in WHITELISTED_DOMAIN_SUFFIXES:
            if hostname == suffix.lstrip(".") or hostname.endswith(suffix):
                is_whitelisted = True
                break
        
        if not is_whitelisted:
            return False, f"Domain '{hostname}' is not in verified official authority whitelist (.gov.in, .nic.in, .ac.in, etc.)"
        
        return True, "Valid official domain"

    @staticmethod
    def validate_opportunity(opp: Dict[str, Any]) -> Tuple[bool, List[str]]:
        errors = []
        
        # Check required fields
        for req_field in ["id", "title", "organization", "category", "status", "official_source"]:
            if not opp.get(req_field):
                errors.append(f"Missing required field: '{req_field}'")
        
        # Validate status
        status = opp.get("status")
        if status and status not in VALID_STATUSES:
            errors.append(f"Invalid status '{status}'. Must be one of {sorted(list(VALID_STATUSES))}")

        # Validate URL
        url_valid, url_msg = DataValidator.validate_official_url(opp.get("official_source", ""))
        if not url_valid:
            errors.append(url_msg)

        # Validate Datetime Chronology
        start_dt = opp.get("start_datetime")
        end_dt = opp.get("end_datetime")
        
        start_parsed = None
        end_parsed = None
        if start_dt:
            try:
                start_parsed = datetime.fromisoformat(start_dt.replace("Z", "+00:00"))
            except Exception:
                errors.append(f"Invalid ISO format for start_datetime: '{start_dt}'")

        if end_dt:
            try:
                end_parsed = datetime.fromisoformat(end_dt.replace("Z", "+00:00"))
            except Exception:
                errors.append(f"Invalid ISO format for end_datetime: '{end_dt}'")

        if start_parsed and end_parsed:
            if start_parsed > end_parsed:
                errors.append(f"Chronology violation: start_datetime ({start_dt}) is after end_datetime ({end_dt})")

        return len(errors) == 0, errors
