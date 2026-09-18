import json, os

BASE_DIR = r"C:\Users\jagarapu lahari\.gemini\antigravity\scratch\career-compass\data"
os.makedirs(BASE_DIR, exist_ok=True)

# 1. NOTIFICATIONS
notifications = [
  {
    "id": "notif-gate-2027",
    "title": "GATE Registration Portal Active",
    "organization": "IIT / IISc National Coordination Board",
    "category": "Entrance Exams",
    "status": "OPEN",
    "start_datetime": "2026-08-28T10:00:00+05:30",
    "end_datetime": "2026-10-05T23:59:00+05:30",
    "exam_date": "February 2027 (First Two Weekends)",
    "result_date": "Third Week of March 2027",
    "eligibility_summary": "3rd/final year UG students or graduates in Engineering / Technology / Science / Commerce.",
    "official_source": "https://gate2025.iitr.ac.in",
    "last_verified_at": "2026-09-15T09:00:00+05:30",
    "priority": "HIGH",
    "description": "Online application portal is active for Graduate Aptitude Test in Engineering (GATE). Mandatory for M.Tech admissions and major PSU recruitments."
  },
  {
    "id": "notif-cat-2026",
    "title": "CAT Application Window Closing Soon",
    "organization": "Indian Institutes of Management (IIMs)",
    "category": "Entrance Exams",
    "status": "CLOSING_SOON",
    "start_datetime": "2026-08-01T10:00:00+05:30",
    "end_datetime": "2026-09-20T17:00:00+05:30",
    "exam_date": "Last Sunday of November 2026",
    "result_date": "January 2027",
    "eligibility_summary": "Bachelor's Degree with at least 50% marks (45% for SC/ST/PwD). Final year students eligible.",
    "official_source": "https://iimcat.ac.in",
    "last_verified_at": "2026-09-15T11:30:00+05:30",
    "priority": "HIGH",
    "description": "Final days remaining to register for Common Admission Test (CAT) for MBA/PGDM across 21 IIMs and premier B-Schools."
  },
  {
    "id": "notif-nsp-scholarship",
    "title": "National Scholarship Portal (NSP) Applications LIVE",
    "organization": "Ministry of Electronics and Information Technology, Govt. of India",
    "category": "Scholarships",
    "status": "LIVE",
    "start_datetime": "2026-08-15T00:00:00+05:30",
    "end_datetime": "2026-11-30T23:59:00+05:30",
    "exam_date": "N/A (Merit & Means Based Scheme)",
    "result_date": "Phased verification from December 2026",
    "eligibility_summary": "Students enrolled in Class 1 to PG/PhD meeting family income and category guidelines.",
    "official_source": "https://scholarships.gov.in",
    "last_verified_at": "2026-09-15T08:00:00+05:30",
    "priority": "HIGH",
    "description": "Central Sector, AICTE (Pragati/Saksham), and Ministry schemes are actively accepting fresh and renewal applications."
  },
  {
    "id": "notif-eapcet-final",
    "title": "State EAPCET Final Phase Counselling & Allotment LIVE",
    "organization": "State Council of Higher Education (APSCHE / TGCHE)",
    "category": "Counselling",
    "status": "LIVE",
    "start_datetime": "2026-09-10T09:00:00+05:30",
    "end_datetime": "2026-09-22T18:00:00+05:30",
    "exam_date": "Completed",
    "result_date": "Seat Allotment by 25th September",
    "eligibility_summary": "Qualified candidates in State EAPCET/EAMCET with 10+2 MPC / BiPC streams.",
    "official_source": "https://cets.apsche.ap.gov.in",
    "last_verified_at": "2026-09-15T12:00:00+05:30",
    "priority": "HIGH",
    "description": "Final phase web option entry and certificate verification for state engineering, agriculture, and pharmacy colleges."
  },
  {
    "id": "notif-afcat-res",
    "title": "AFCAT 02/2026 Examination Results Declared",
    "organization": "Indian Air Force (IAF)",
    "category": "Results",
    "status": "RESULT",
    "start_datetime": "2026-09-12T12:00:00+05:30",
    "end_datetime": "2026-10-15T23:59:00+05:30",
    "exam_date": "August 2026",
    "result_date": "12th September 2026",
    "eligibility_summary": "Graduates/B.Tech who appeared for AFCAT written examination.",
    "official_source": "https://afcat.cdac.in",
    "last_verified_at": "2026-09-14T16:00:00+05:30",
    "priority": "NORMAL",
    "description": "Individual scorecards and cutoff marks published. Qualified candidates can log in to choose AFSB interview dates."
  },
  {
    "id": "notif-isro-app",
    "title": "ISRO URSC Graduate & Technician Apprentice Applications Open",
    "organization": "Indian Space Research Organisation (ISRO)",
    "category": "Government Jobs",
    "status": "OPEN",
    "start_datetime": "2026-09-02T10:00:00+05:30",
    "end_datetime": "2026-09-28T17:00:00+05:30",
    "exam_date": "Merit Selection / Academic Verification",
    "result_date": "October 2026",
    "eligibility_summary": "B.E./B.Tech or 3-Year Diploma in CSE, ECE, EEE, Mechanical, Civil passed during 2024-2026.",
    "official_source": "https://www.isro.gov.in/Careers.html",
    "last_verified_at": "2026-09-13T14:30:00+05:30",
    "priority": "NORMAL",
    "description": "ISRO U R Rao Satellite Centre invites online applications for one-year graduate and technician apprenticeship."
  },
  {
    "id": "notif-nda-cycle",
    "title": "UPSC NDA & NA I 2027 Notification Timeline Announced",
    "organization": "Union Public Service Commission (UPSC)",
    "category": "Defence",
    "status": "UPCOMING",
    "start_datetime": "2026-10-01T09:00:00+05:30",
    "end_datetime": "2026-12-30T18:00:00+05:30",
    "exam_date": "April 2027",
    "result_date": "May 2027",
    "eligibility_summary": "12th pass (Army) or 12th with Physics & Maths (Air Force/Navy). Unmarried candidates aged 16.5-19.5.",
    "official_source": "https://upsc.gov.in",
    "last_verified_at": "2026-09-15T09:30:00+05:30",
    "priority": "NORMAL",
    "description": "UPSC calendar outlines upcoming NDA & NA notification on upsc.gov.in via One Time Registration (OTR)."
  },
  {
    "id": "notif-jeemain-prev",
    "title": "JEE Main Past Cycle Archived Record",
    "organization": "National Testing Agency (NTA)",
    "category": "Entrance Exams",
    "status": "CLOSED",
    "start_datetime": "2026-01-01T00:00:00+05:30",
    "end_datetime": "2026-03-20T23:59:00+05:30",
    "exam_date": "April 2026",
    "result_date": "May 2026",
    "eligibility_summary": "10+2 passed or appearing with Physics, Chemistry, and Mathematics.",
    "official_source": "https://jeemain.nta.nic.in",
    "last_verified_at": "2026-03-21T10:00:00+05:30",
    "priority": "LOW",
    "description": "Archived cycle record. Next cycle notification scheduled for release in November on jeemain.nta.nic.in."
  }
]

with open(os.path.join(BASE_DIR, "notifications.json"), "w", encoding="utf-8") as f:
    json.dump(notifications, f, indent=2, ensure_ascii=False)

print("Saved notifications.json")
