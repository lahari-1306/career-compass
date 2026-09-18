import os
import json
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__, template_folder="templates", static_folder="static")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.environ.get("DATA_DIR", os.path.join(BASE_DIR, "data"))

def load_json(filename):
    filepath = os.path.join(DATA_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def evaluate_notifications(notifications):
    now_dt = datetime.now().astimezone()
    evaluated = []
    for item in notifications:
        item_copy = dict(item)
        try:
            start_dt = datetime.fromisoformat(item_copy["start_datetime"])
            end_dt = datetime.fromisoformat(item_copy["end_datetime"])
            if now_dt < start_dt:
                item_copy["dynamic_status"] = "UPCOMING"
                item_copy["is_active_for_ticker"] = False
            elif now_dt > end_dt:
                item_copy["dynamic_status"] = "CLOSED"
                item_copy["is_active_for_ticker"] = False
            else:
                days_left = (end_dt - now_dt).total_seconds() / 86400
                if days_left <= 5 and item_copy.get("status") != "RESULT":
                    item_copy["dynamic_status"] = "CLOSING_SOON"
                elif item_copy.get("status") == "RESULT":
                    item_copy["dynamic_status"] = "RESULT"
                elif item_copy.get("status") == "LIVE":
                    item_copy["dynamic_status"] = "LIVE"
                else:
                    item_copy["dynamic_status"] = "OPEN"
                item_copy["is_active_for_ticker"] = True
            status_map = {
                "OPEN": "OPEN / ONGOING",
                "CLOSING_SOON": "DEADLINE SOON",
                "LIVE": "COUNSELLING LIVE",
                "RESULT": "RESULT AVAILABLE",
                "UPCOMING": "UPCOMING",
                "CLOSED": "CLOSED",
                "ARCHIVED": "ARCHIVED"
            }
            item_copy["display_status"] = status_map.get(item_copy["dynamic_status"], item_copy["dynamic_status"])
        except Exception:
            item_copy["dynamic_status"] = item_copy.get("status", "OPEN")
            item_copy["display_status"] = item_copy.get("status", "OPEN")
            item_copy["is_active_for_ticker"] = (item_copy["dynamic_status"] != "CLOSED")
        evaluated.append(item_copy)
    return evaluated

@app.after_request
def add_security_and_cors_headers(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "SAMEORIGIN"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

@app.errorhandler(404)
def not_found_handler(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Resource not found", "status": 404}), 404
    return render_template("index.html")

@app.errorhandler(500)
def server_error_handler(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Internal server error", "status": 500}), 500
    return render_template("index.html"), 500

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def index(path=""):
    if path.startswith("api/"):
        return jsonify({"error": "Resource not found", "status": 404}), 404
    return render_template("index.html")


@app.route("/api/notifications")
def get_active_notifications():
    all_notifs = load_json("notifications.json")
    evaluated = evaluate_notifications(all_notifs)
    active = [n for n in evaluated if n.get("is_active_for_ticker", False)]
    return jsonify({
        "server_time": datetime.now().astimezone().isoformat(),
        "total_active": len(active),
        "notifications": active
    })

@app.route("/api/notifications/all")
def get_all_notifications():
    all_notifs = load_json("notifications.json")
    evaluated = evaluate_notifications(all_notifs)
    cat = request.args.get("category")
    if cat and cat != "All":
        evaluated = [n for n in evaluated if n.get("category") == cat]
    return jsonify({
        "server_time": datetime.now().astimezone().isoformat(),
        "total": len(evaluated),
        "notifications": evaluated
    })

@app.route("/api/career-paths")
def get_career_paths():
    return jsonify(load_json("career_paths.json"))

@app.route("/api/defence-entries")
def get_defence_entries():
    return jsonify(load_json("defence_entries.json"))

@app.route("/api/govt-engineering-jobs")
def get_govt_engineering_jobs():
    return jsonify(load_json("govt_engineering.json"))

@app.route("/api/entrance-exams")
def get_entrance_exams():
    data = load_json("entrance_exams.json")
    category = request.args.get("category")
    if category and category != "All":
        data = [e for e in data if e.get("category") == category]
    return jsonify(data)

@app.route("/api/colleges")
def get_colleges():
    data = load_json("colleges_cutoffs.json")
    return jsonify(data.get("colleges", []))

@app.route("/api/cutoffs")
def get_cutoffs():
    return jsonify(load_json("colleges_cutoffs.json"))

@app.route("/api/scholarships")
def get_scholarships():
    return jsonify(load_json("scholarships.json"))

@app.route("/api/digital-library")
def get_digital_library():
    return jsonify(load_json("digital_library.json"))

@app.route("/api/official-links")
def get_official_links():
    return jsonify(load_json("official_links.json"))

def generate_rule_based_recommendation(user_profile, query_text):
    qual = user_profile.get("qualification", "").lower()
    branch = user_profile.get("branch", "").lower()
    ql = query_text.lower()

    if any(k in ql for k in ["defence", "army", "navy", "air force", "nda", "cds", "afcat"]):
        return {
            "mode": "rule_based",
            "title": "Indian Armed Forces Career Roadmap",
            "summary": "Dedicated pathways for Commissioned Officer ranks and technical entries across the Army, Navy, and Air Force.",
            "roadmap": {
                "current_position": qual.upper() if qual else "Aspirant",
                "suitable_options": [
                    "UPSC NDA & NA (After 12th: Army, Navy, Air Force Wings)",
                    "10+2 Technical Entry Scheme (TES Army & Navy B.Tech Cadet)",
                    "UPSC CDS Exam (After Graduation: IMA, INA, AFA, OTA)",
                    "AFCAT (Air Force Common Admission Test for Flying & Ground Duty)",
                    "Direct Engineering SSB entries (Army TGC, SSC Tech, Navy Executive & Technical)",
                    "Agniveer Recruitment (General Duty, Technical, Tradesmen)"
                ],
                "entrance_exams": ["UPSC NDA", "UPSC CDS", "AFCAT", "Direct SSB based on B.Tech / JEE Rank"],
                "courses": ["3-4 Years Academy Cadre Training (Grants JNU B.Sc/B.Tech degree)"],
                "colleges": ["NDA Khadakwasla", "IMA Dehradun", "INA Ezhimala", "AFA Dundigal", "OTA Chennai"],
                "skills": ["Officer Like Qualities (OLQ)", "Physical Stamina (2.4 km running, push-ups)", "Current Affairs & Psychological Stability"],
                "career": "Commissioned as Lieutenant / Sub Lieutenant / Flying Officer (7th CPC Level 10: Rs 56,100 basic + Rs 15,500 MSP)",
                "next_steps": [
                    "Review official height/medical guidelines on joinindianarmy.nic.in.",
                    "Check UPSC annual calendar for upcoming NDA/CDS notification dates.",
                    "Solve previous 5 years NDA / CDS papers in the CareerCompass Digital Library."
                ]
            },
            "disclaimer": "CareerCompass verified guidance. Strict age and physical criteria apply per official gazette."
        }

    if any(k in ql for k in ["10th", "class 10"]) or "10th" in qual:
        return {
            "mode": "rule_based",
            "title": "Career Roadmap After Class 10th",
            "summary": "Broad pathways spanning pre-university Intermediate streams, 3-Year Polytechnic Engineering Diplomas, ITI Trades, and Defence preparation.",
            "roadmap": {
                "current_position": "Class 10th Passed / Secondary School",
                "suitable_options": [
                    "Intermediate MPC (For B.Tech, NDA, Architecture, Pure Sciences)",
                    "Intermediate BiPC (For MBBS, BDS, Pharmacy, Agriculture, Nursing)",
                    "Intermediate MEC / CEC (For CA, CMA, CS, B.Com, BBA, Law)",
                    "Polytechnic Diploma in Engineering (CSE, ECE, EEE, Mech, Civil) with ECET lateral entry into 2nd year B.Tech",
                    "ITI Technical Trades (Electrician, Fitter, COPA) for immediate Railway & PSU technical jobs",
                    "Defence Agniveer Routes (Army GD, Navy MR)"
                ],
                "entrance_exams": ["State POLYCET (for Diploma)", "APRJC / TSRJC (Residential Colleges)", "Army Agniveer CEE"],
                "courses": ["10+2 Intermediate (2 Yrs)", "Polytechnic Diploma (3 Yrs)", "ITI (1-2 Yrs)"],
                "colleges": ["Govt & Aided Junior Colleges, Polytechnic Institutes, ITIs"],
                "skills": ["Basic Mathematics & Science foundations", "English Communication", "Computer Operations"],
                "career": "Professional Graduate, Junior Engineer, State Civil Services, or Armed Forces soldier",
                "next_steps": [
                    "Analyze your academic aptitude (Maths vs Biology vs Commerce/Arts).",
                    "Check state POLYCET dates on polycetap.nic.in if practical engineering is your passion.",
                    "Secure Class 10 original certificates and apply for Intermediate Junior Colleges."
                ]
            },
            "disclaimer": "CareerCompass verified guidance. Admission windows are subject to state education boards."
        }

    if any(k in ql for k in ["diploma", "polytechnic"]) or "diploma" in qual:
        return {
            "mode": "rule_based",
            "title": "Career Roadmap for Polytechnic Diploma Holders",
            "summary": "Immediate lateral entry into 2nd year B.Tech via ECET, central/state Junior Engineer government exams, or core technical industries.",
            "roadmap": {
                "current_position": "Diploma in Engineering (" + (branch.upper() if branch else "Engineering Branch") + ")",
                "suitable_options": [
                    "B.Tech / B.E. Lateral Entry (Direct 2nd Year / 3rd Semester via ECET)",
                    "Central Government Junior Engineer Posts (RRB JE, SSC JE, DRDO CEPTAM, ISRO Tech Assistant)",
                    "Core Industry Engineering Roles (Tata Motors, L&T, BHEL, NTPC, Siemens)",
                    "National Apprenticeship Training Scheme (NATS) with monthly stipend",
                    "Defence Technical Trades (IAF Group X, Navy Sailor, Army Technical)"
                ],
                "entrance_exams": ["State ECET (AP ECET, TS ECET, JELET, LEET)", "RRB JE", "SSC JE", "DRDO CEPTAM"],
                "courses": ["B.Tech Degree (3 Years via lateral entry)", "Advanced CAD/CAM, PLC-SCADA, AWS Cloud"],
                "colleges": ["State University Engineering Colleges, Premier Autonomous Institutes"],
                "skills": ["Core Branch Practical Engineering", "AutoCAD / MATLAB / Python / Circuit Simulation", "General Aptitude for JE exams"],
                "career": "Graduate Engineer, Junior Engineer, Assistant Executive Engineer, Plant Supervisor",
                "next_steps": [
                    "For B.Tech: Prepare for State ECET engineering subject + Maths, Physics, Chemistry.",
                    "For Govt Jobs: Download syllabus for RRB JE / SSC JE and study technical subjects systematically.",
                    "Register on nats.education.gov.in for recognized paid industrial training."
                ]
            },
            "disclaimer": "CareerCompass verified guidance. Lateral entry reservation and eligibility as per AICTE and State Higher Education Councils."
        }

    if any(k in ql for k in ["b.tech", "btech", "engineering", "software", "gate", "cse", "it"]) or "b.tech" in qual:
        return {
            "mode": "rule_based",
            "title": "Career Roadmap for B.Tech / B.E. Engineers",
            "summary": "Top tier software and tech careers, GATE for IIT Master programs & Maharatna PSUs, UPSC Engineering Services (ESE), or direct Defence Technical SSB calls.",
            "roadmap": {
                "current_position": "B.Tech / B.E. (" + (branch.upper() if branch else "Engineering") + ")",
                "suitable_options": [
                    "High-Growth Tech Careers: SDE, Full Stack Developer, DevOps & Cloud, AI/ML, Cyber Security",
                    "GATE Examination: M.Tech at Top IITs (with Rs 12,400/mo stipend) OR Direct PSU Recruitment at ONGC, IOCL, NTPC, BHEL (CTC Rs 15-22 LPA)",
                    "UPSC Engineering Services (ESE / IES) for Class 1 Gazetted Central Engineering Officers",
                    "Defence Technical Entries (Army TGC, SSC Tech, Navy SSC) - Direct 5-Day SSB based on engineering marks",
                    "Higher Studies Abroad (MS via GRE/TOEFL) or Management Leadership (MBA via CAT)"
                ],
                "entrance_exams": ["GATE", "UPSC ESE / IES", "CAT", "GRE & TOEFL", "IBPS SO IT Officer"],
                "courses": ["B.Tech Degree Completion", "M.Tech / MS (Research)", "Cloud & Cyber Security Certifications"],
                "colleges": ["IITs, NITs, IISc Bangalore, IIMs, Global Top Universities"],
                "skills": ["Data Structures & Algorithms (LeetCode)", "System Design", "Git & CI/CD", "Engineering Core Fundamentals"],
                "career": "Software Architect, PSU Executive Trainee, Central Gazetted Officer, Defence Officer",
                "next_steps": [
                    "For Tech: Master 150+ DSA problems and deploy 2 production-quality full stack applications.",
                    "For PSUs/M.Tech: Register for GATE at gate2025.iitr.ac.in and practice 20 years PYQs.",
                    "For Defence: Check cut-off marks on joinindianarmy.nic.in for TGC / SSC Tech entries."
                ]
            },
            "disclaimer": "CareerCompass verified guidance. Recommendations do not guarantee placement outcomes."
        }

    return {
        "mode": "rule_based",
        "title": "Personalized Education & Career Guidance Roadmap",
        "summary": "Based on your profile (" + (qual.upper() if qual else "Student") + " - " + (branch.upper() if branch else "General Stream") + "), here is your step-by-step navigation pathway.",
        "roadmap": {
            "current_position": qual.upper() if qual else "Current Educational Stage",
            "suitable_options": [
                "Higher Specialized Degree Programs (Undergraduate / Postgraduate)",
                "Central & State Government Competitive Exams (UPSC, SSC, State PSC, Banking)",
                "Private Corporate Careers in Growth Sectors",
                "Defence Officer Commissions (CDS, AFCAT, Technical Entries)"
            ],
            "entrance_exams": ["UPSC CSE / SSC CGL", "IBPS Banking Exams", "State CETs", "CAT / GATE / CUET"],
            "courses": ["Recognized University Degree Program", "Industry-aligned Skill Certifications"],
            "colleges": ["Central Universities, State University Colleges, National Institutes"],
            "skills": ["Analytical Reasoning & Quantitative Aptitude", "Professional Communication", "Digital Literacy"],
            "career": "Administrative Officer, Corporate Professional, Banking Officer, Technical Specialist",
            "next_steps": [
                "Clarify your goal: Government Service vs Corporate Industry vs Higher Studies.",
                "Check verified dates in the CareerCompass Notification Center.",
                "Utilize free official resources in the CareerCompass Digital Library."
            ]
        },
        "disclaimer": "CareerCompass verified guidance. Guidance only; not a guaranteed outcome."
    }

@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    req_data = request.get_json() or {}
    message = req_data.get("message", "").strip()
    profile = req_data.get("profile", {})

    if not message:
        return jsonify({"error": "Message is required"}), 400

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if api_key:
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + api_key
            headers = {"Content-Type": "application/json"}
            sys_prompt = (
                "You are CareerCompass AI Career Guide for Indian students. "
                "Provide compassionate, highly accurate educational guidance after 10th, 12th, Diploma, Degree, or B.Tech. "
                "NEVER hallucinate examination dates, application deadlines, cutoffs, or fees. "
                "Structure roadmaps as: CURRENT POSITION -> SUITABLE OPTIONS -> ENTRANCE EXAMS -> COURSES -> COLLEGES -> SKILLS -> CAREER -> NEXT STEPS. "
                "Always remind students that recommendations are guidance only and refer to official government portals."
            )
            payload = {
                "contents": [{"parts": [{"text": sys_prompt + "\n\nStudent Profile: " + json.dumps(profile) + "\nQuestion: " + message}]}],
                "generationConfig": {"temperature": 0.4, "maxOutputTokens": 1200}
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                result_json = resp.json()
                reply_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({
                    "status": "success",
                    "mode": "gemini_ai",
                    "reply": reply_text,
                    "provider": "Google Gemini AI (Secured Server Engine)"
                })
        except Exception as e:
            print("Gemini API error:", e)

    fallback_res = generate_rule_based_recommendation(profile, message)
    return jsonify({
        "status": "success",
        "mode": "rule_based",
        "provider": "CareerCompass Verified Knowledge Engine (Offline/Rule-Based Mode)",
        "data": fallback_res
    })

@app.route("/api/admin/verify", methods=["POST"])
def admin_verify():
    data = request.get_json() or {}
    notif_id = data.get("id")
    new_status = data.get("status")
    notifications = load_json("notifications.json")
    updated = False
    for n in notifications:
        if n["id"] == notif_id:
            if new_status:
                n["status"] = new_status
            n["last_verified_at"] = datetime.now().astimezone().isoformat()
            updated = True
            break
    if updated:
        with open(os.path.join(DATA_DIR, "notifications.json"), "w", encoding="utf-8") as f:
            json.dump(notifications, f, indent=2, ensure_ascii=False)
        return jsonify({"success": True, "message": "Notification " + str(notif_id) + " verified successfully."})
    return jsonify({"success": False, "message": "Notification not found"}), 404

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true")
    print(f"Starting CareerCompass on 0.0.0.0:{port} (Debug: {debug})")
    print(f"Local Access: http://127.0.0.1:{port}")
    print(f"Network Access: http://192.168.1.9:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)