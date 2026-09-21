"""
Matching Engine for "MY CAREER RADAR"
Performs multi-factor rule-based matching, strict negative filtering, urgency scoring,
and generates transparent "Why am I seeing this?" match explanations.
"""
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any, Optional

IST = timezone(timedelta(hours=5, minutes=30))

# Normalize qualifications
QUAL_HIERARCHY = {
    "10th": ["10th", "SSC", "10", "TENTH"],
    "Intermediate": ["Intermediate", "12th", "10+2", "Plus 2", "Inter"],
    "Diploma": ["Diploma", "Polytechnic"],
    "Degree": ["Degree", "B.Sc", "B.Com", "B.A", "BBA", "BCA", "Bachelor"],
    "B.Tech": ["B.Tech", "B.E", "Engineering", "BTech", "BE"],
    "Postgraduate": ["Postgraduate", "M.Tech", "M.E", "M.Sc", "MBA", "MCA", "Masters"]
}

class RadarMatcher:
    @staticmethod
    def match(profile: Dict[str, Any], opportunities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Filters and scores opportunities against a student's profile.
        Returns a sorted list of matched opportunities with match reasons and urgency.
        """
        user_qual = profile.get("qualification", "").strip()
        user_branch = profile.get("stream_or_branch", "").strip().upper()
        user_state = profile.get("state", "").strip()
        user_interests = [i.strip().lower() for i in profile.get("interests", [])]

        matches = []
        now = datetime.now(IST)

        for opp in opportunities:
            opp_id = opp.get("id", "")
            title = opp.get("title", "")
            cat = opp.get("category", "")
            status = opp.get("status", "")
            eligibility = opp.get("eligibility_summary", "")
            target_quals = opp.get("target_qualifications") or RadarMatcher._infer_quals(opp)
            target_branches = [b.upper() for b in opp.get("target_branches", [])]
            target_states = opp.get("target_states", [])

            # ----------------------------------------------------
            # 1. STRICT NEGATIVE FILTERING (Cross-domain clutter elimination)
            # ----------------------------------------------------
            # A. Qualification mismatch
            if target_quals and user_qual:
                if user_qual not in target_quals and not any(q in target_quals for q in RadarMatcher._expand_qual(user_qual)):
                    # Special check: Degree holders can sometimes write certain jobs, but 10th cannot write GATE/CAT
                    if user_qual == "10th" and any(q in ["B.Tech", "Degree", "Intermediate", "Postgraduate"] for q in target_quals):
                        continue
                    if user_qual == "Intermediate" and any(q in ["B.Tech", "Degree", "Postgraduate"] for q in target_quals):
                        continue
                    if user_qual == "B.Tech" and any(q in ["10th", "Intermediate"] for q in target_quals):
                        continue
                    if user_qual == "Diploma" and any(q in ["10th"] for q in target_quals):
                        continue
                    if user_qual in ["10th", "Intermediate"] and "CAT" in title:
                        continue

            # B. Stream / Branch mismatch
            if target_branches and user_branch and "ALL" not in target_branches and "ALL_ENGINEERING" not in target_branches and "ALL_DIPLOMA" not in target_branches:
                # If target explicitly mentions MPC and user is BiPC or Arts
                if "MPC" in target_branches and user_branch not in ["MPC", "MATHS"]:
                    continue
                if "BIPC" in target_branches and user_branch not in ["BIPC", "BIOLOGY"]:
                    continue

            # C. State mismatch: If opportunity is state-specific and user specified a different state
            if target_states and user_state and user_state not in ["All India", "National"]:
                if user_state not in target_states and "All India" not in target_states:
                    continue

            # ----------------------------------------------------
            # 2. POSITIVE FACTOR MATCHING & REASON GENERATION
            # ----------------------------------------------------
            score = 40  # Base relevance
            reasons = []

            # Qualification alignment
            if target_quals and any(q in target_quals for q in RadarMatcher._expand_qual(user_qual)):
                score += 25
                reasons.append(f"Directly matches your qualification: {user_qual}")
            elif not target_quals:
                # Open or universal (like National Scholarships)
                if "scholarship" in title.lower() or "scholarship" in cat.lower():
                    score += 20
                    reasons.append("Universal scholarship scheme open to students across streams")

            # Stream / Branch alignment
            if target_branches:
                if user_branch in target_branches:
                    score += 20
                    reasons.append(f"Specifically matches your branch / stream: {user_branch}")
                elif "ALL_ENGINEERING" in target_branches and user_qual in ["B.Tech", "Degree"]:
                    score += 15
                    reasons.append(f"Open to all Engineering & Technology specializations including {user_branch}")
                elif "ALL_DIPLOMA" in target_branches and user_qual == "Diploma":
                    score += 15
                    reasons.append(f"Open to 3-Year Diploma holders including {user_branch}")

            # Interest alignment
            matched_interest = False
            for interest in user_interests:
                if ("higher" in interest or "m.tech" in interest or "cat" in interest or "gate" in interest) and cat == "Entrance Exams":
                    score += 15
                    reasons.append("Aligns with your career goal in Higher Studies & Entrance Exams")
                    matched_interest = True
                    break
                elif ("psu" in interest or "govt" in interest or "job" in interest) and (cat in ["Government Jobs", "Entrance Exams"]):
                    score += 15
                    reasons.append("Aligns with your goal for PSU recruitment and Government roles")
                    matched_interest = True
                    break
                elif "defence" in interest and cat in ["Defence", "Results"]:
                    score += 20
                    reasons.append("Aligns with your target in the Indian Armed Forces")
                    matched_interest = True
                    break
                elif "scholarship" in interest and cat == "Scholarships":
                    score += 20
                    reasons.append("Aligns with your interest in Financial Aid & Scholarships")
                    matched_interest = True
                    break
                elif ("counselling" in interest or "admission" in interest) and cat == "Counselling":
                    score += 15
                    reasons.append("Matches your admission and counselling cycle preferences")
                    matched_interest = True
                    break

            if not matched_interest and cat:
                reasons.append(f"Verified official alert in {cat}")

            # State alignment
            if target_states and user_state in target_states:
                score += 10
                reasons.append(f"Active in your designated home state ({user_state})")

            # ----------------------------------------------------
            # 3. DEADLINE & URGENCY CALCULATION
            # ----------------------------------------------------
            end_dt_str = opp.get("end_datetime")
            days_remaining = None
            urgency = "NORMAL"

            if end_dt_str:
                try:
                    end_dt = datetime.fromisoformat(end_dt_str.replace("Z", "+00:00"))
                    diff = (end_dt - now).total_seconds()
                    days_remaining = max(0, int(diff // 86400))
                    
                    if days_remaining <= 5 or status == "CLOSING_SOON":
                        urgency = "HIGH"
                        reasons.insert(0, f"⚠️ Urgent: Application window closes in {days_remaining} days!")
                    elif days_remaining <= 20:
                        urgency = "MEDIUM"
                    else:
                        urgency = "NORMAL"
                except Exception:
                    pass

            if status == "LIVE" or status == "OPEN":
                if urgency != "HIGH":
                    urgency = "MEDIUM"

            score = min(100, score)

            matched_item = {
                "opportunity_id": opp_id,
                "title": title,
                "organization": opp.get("organization", "Official Authority"),
                "category": cat,
                "status": status,
                "start_datetime": opp.get("start_datetime"),
                "end_datetime": end_dt_str,
                "exam_date": opp.get("exam_date"),
                "result_date": opp.get("result_date"),
                "official_source": opp.get("official_source", ""),
                "last_verified_at": opp.get("last_verified_at", ""),
                "eligibility_summary": eligibility,
                "description": opp.get("description", ""),
                "match_score": score,
                "match_reasons": reasons,
                "urgency": urgency,
                "days_remaining": days_remaining,
                "disclaimer": "Eligibility and dates are verified from official portals. Always verify full notification PDF before applying."
            }
            matches.append(matched_item)

        # Sort by urgency (HIGH first) then match_score descending
        urgency_rank = {"HIGH": 3, "MEDIUM": 2, "NORMAL": 1}
        matches.sort(key=lambda m: (urgency_rank.get(m["urgency"], 0), m["match_score"]), reverse=True)
        return matches

    @staticmethod
    def _expand_qual(qual: str) -> List[str]:
        for standard, aliases in QUAL_HIERARCHY.items():
            if qual.lower() == standard.lower() or qual.lower() in [a.lower() for a in aliases]:
                return aliases + [standard]
        return [qual]

    @staticmethod
    def _infer_quals(opp: Dict[str, Any]) -> List[str]:
        text = f"{opp.get('title', '')} {opp.get('eligibility_summary', '')} {opp.get('description', '')}".lower()
        quals = []
        if any(w in text for w in ["bachelor", "degree", "graduate", "b.tech", "b.e.", "cat 20", "gate 20", "afcat", "cds "]):
            quals.extend(["B.Tech", "Degree"])
        if any(w in text for w in ["10+2", "intermediate", "jee main", "eapcet", "eamcet", "nda "]):
            quals.append("Intermediate")
        if any(w in text for w in ["polytechnic", "polycet", "ssc", "10th"]):
            quals.append("10th")
        if any(w in text for w in ["diploma", "ecet", "technician"]):
            quals.append("Diploma")
        if not quals:
            quals = ["All"]
        return quals
