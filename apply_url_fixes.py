"""
URL Migration Script for Career Compass
Replaces all dead, outdated, 404, or non-working URLs across all datasets and database tables
with official, permanent, and working HTTPS government/educational URLs.
"""

import os
import glob
import json
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
DB_PATH = os.path.join(DATA_DIR, "career_compass.db")

REPLACEMENTS = {
    # NEET UG: old 404 NTA path -> permanent official NIC portal
    "https://exams.nta.ac.in/NEET": "https://neet.nta.nic.in",

    # DRDO: old 404 careers path -> official Recruitment and Assessment Centre
    "https://www.drdo.gov.in/drdo/careers": "https://rac.gov.in",

    # AICTE Pragati: old 404 path -> National Scholarship Portal
    "https://www.aicte-india.org/schemes/students-development-schemes/Pragati": "https://scholarships.gov.in",

    # AFCAT & Indian Air Force: old 404 CDAC path -> official IAF career portal
    "https://afcat.cdac.in": "https://careerindianairforce.cdac.in",
    "https://airmenselection.cdac.in": "https://careerindianairforce.cdac.in",

    # GATE: old expired/404 syllabus and mock links -> official GATE 2025 portal
    "https://gate2025.iitr.ac.in/mock-test.html": "https://gate2025.iitr.ac.in",
    "https://gate2025.iitr.ac.in/syllabus.html": "https://gate2025.iitr.ac.in",
    "https://gate2023.iitk.ac.in/": "https://gate2025.iitr.ac.in",
    "https://gate2023.iitk.ac.in": "https://gate2025.iitr.ac.in",
    "https://gate2022.iitkgp.ac.in/": "https://gate2025.iitr.ac.in",
    "https://gate2022.iitkgp.ac.in": "https://gate2025.iitr.ac.in",

    # Silberschatz Operating Systems textbook: old Wiley 404 -> Yale official course companion
    "https://www.wiley.com/en-us/Operating+System+Concepts%2C+10th+Edition-p-9781119456339": "https://codex.cs.yale.edu/avi/os-book/OS10/",

    # CUET UG: old domain -> permanent official NTA portal
    "https://cuetug.ntaonline.in": "https://cuet.nta.nic.in",

    # Railway RRB Apply: missing www causes DNS failure on standard resolvers -> www.rrbapply.gov.in
    "https://rrbapply.gov.in": "https://www.rrbapply.gov.in",

    # Join Indian Navy: missing www causes connection reset -> www.joinindiannavy.gov.in
    "https://joinindiannavy.gov.in": "https://www.joinindiannavy.gov.in",

    # AP POLYCET: old polycetap.nic.in DNS error -> official State Board portal
    "https://polycetap.nic.in": "https://apsbtet.ap.gov.in",

    # IIT JAM: old year-specific broken subdomain -> official JAM 2025 portal
    "https://jam.iitd.ac.in": "https://jam2025.iitd.ac.in",

    # SBI Careers: slow/timeout sbi.co.in/careers -> official bank.sbi/careers
    "https://sbi.co.in/careers": "https://bank.sbi/careers",

    # ePathshala: old nic.in -> official NCERT domain
    "https://epathshala.nic.in": "https://epathshala.ncert.gov.in",

    # NCVT MIS: timeout -> Directorate General of Training official portal
    "https://ncvtmis.gov.in": "https://dgt.gov.in",

    # NIMCET: timeout -> permanent official NIC admissions portal
    "https://www.nimcet.in": "https://nimcet.admissions.nic.in",

    # AP SCERT: timeout -> Commissioner of School Education AP
    "https://scert.ap.gov.in": "https://cse.ap.gov.in",

    # ICAR UG: -> CUET UG official portal
    "https://icar.org.in": "https://cuet.nta.nic.in",

    # AICTE Main domain: ensure canonical gov.in
    "https://www.aicte-india.org": "https://www.aicte.gov.in"
}

def update_json_files():
    total_replaced = 0
    files_modified = 0

    json_files = glob.glob(os.path.join(DATA_DIR, "*.json"))
    for file_path in json_files:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        new_content = content
        file_replaced = 0
        for old_url, new_url in REPLACEMENTS.items():
            if old_url in new_content:
                count = new_content.count(old_url)
                new_content = new_content.replace(old_url, new_url)
                file_replaced += count
                print(f"[{os.path.basename(file_path)}] Replaced {count}x: {old_url} -> {new_url}")

        if file_replaced > 0:
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(new_content)
            files_modified += 1
            total_replaced += file_replaced

    print(f"\nJSON Update Complete: {total_replaced} replacements across {files_modified} files.")

def update_database():
    if not os.path.exists(DB_PATH):
        print(f"Database not found at {DB_PATH}, skipping DB table updates.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    db_updated = 0

    # 1. notifications table: official_source column
    try:
        cursor.execute("SELECT id, official_source FROM notifications")
        rows = cursor.fetchall()
        for nid, source in rows:
            if source:
                new_source = source
                for old_url, new_url in REPLACEMENTS.items():
                    if old_url in new_source:
                        new_source = new_source.replace(old_url, new_url)
                if new_source != source:
                    cursor.execute("UPDATE notifications SET official_source = ? WHERE id = ?", (new_source, nid))
                    db_updated += 1
    except Exception as e:
        print(f"Notice on notifications table: {e}")

    # 2. saved_opportunities table: official_url column
    try:
        cursor.execute("SELECT id, official_url FROM saved_opportunities")
        rows = cursor.fetchall()
        for sid, url in rows:
            if url:
                new_url = url
                for old_url, new_url_target in REPLACEMENTS.items():
                    if old_url in new_url:
                        new_url = new_url.replace(old_url, new_url_target)
                if new_url != url:
                    cursor.execute("UPDATE saved_opportunities SET official_url = ? WHERE id = ?", (new_url, sid))
                    db_updated += 1
    except Exception as e:
        print(f"Notice on saved_opportunities table: {e}")

    conn.commit()
    conn.close()
    print(f"Database Update Complete: {db_updated} rows updated in {DB_PATH}.")

if __name__ == "__main__":
    update_json_files()
    update_database()
