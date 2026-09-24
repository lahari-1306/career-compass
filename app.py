import os
import json
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
import requests

from radar.models import StudentProfile
from radar.matcher import RadarMatcher, BRANCH_FAMILY_MAP
from radar.storage import RadarStorage
from radar.dispatcher import RadarDispatcher
from data_updater.registry import SourceRegistry
from data_updater.change_detector import ChangeDetector
from data_updater.updater import DataUpdater
from ai_engine import AIEngine, get_verified_current_data
from auth import auth_bp, get_current_user, login_required
from services.email_service import EmailService
from services.push_service import PushService
from services.pipeline_service import PipelineService
from db_repository import (
    ProfileRepository, NotificationRepository, PushRepository,
    SavedOpportunitiesRepository, ExamProgressRepository
)

app = Flask(__name__, template_folder="templates", static_folder="static")
app.register_blueprint(auth_bp)

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

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/exam-preparation")
@app.route("/exam-preparation/<exam_id>")
def exam_prep_view(exam_id=None):
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

# ==========================================
# B.TECH COMPLETED CAREER PATHWAYS & JOBS API
# ==========================================

@app.route("/api/btech/pathways")
def get_btech_pathways():
    data = load_json("btech_post_grad_pathways.json") or {}
    branch = request.args.get("branch", "").strip().upper()
    pathway_id = request.args.get("pathway", "").strip().lower()

    pathways = data.get("pathways", [])
    if pathway_id:
        target = next((p for p in pathways if p["id"] == pathway_id), None)
        if not target:
            return jsonify({"status": "error", "message": "Pathway not found"}), 404
        return jsonify({"status": "success", "pathway": target, "branch": branch or "ALL"})

    return jsonify({
        "status": "success",
        "total_pathways": len(pathways),
        "pathways": pathways,
        "branch": branch or "ALL"
    })

@app.route("/api/options")
def get_app_options():
    return jsonify(load_json("options.json"))

@app.route("/api/btech/jobs")
def get_btech_jobs():
    data = load_json("btech_post_grad_pathways.json") or {}
    categories = data.get("job_categories", [])
    
    branch = request.args.get("branch", "").strip().upper()
    cat_filter = request.args.get("category", "").strip().lower()
    search = request.args.get("search", "").strip().lower()

    filtered_categories = []
    total_roles = 0

    for cat in categories:
        if cat_filter and cat_filter != "all" and cat["id"] != cat_filter:
            continue
        
        roles = cat.get("roles", [])
        filtered_roles = []
        for role in roles:
            # Branch filter: role matches if branch in role['branches'] or in branch families or 'Other' in role['branches'] or not branch or branch == 'ALL'
            if branch and branch != "ALL":
                role_branches = [b.upper() for b in role.get("branches", [])]
                families = BRANCH_FAMILY_MAP.get(branch, [branch])
                matches_family = any(f in role_branches for f in families) or branch in role_branches or "OTHER" in role_branches
                if not matches_family:
                    continue
            
            # Search filter
            if search:
                blob = (role.get("name", "") + " " + " ".join(role.get("skills", [])) + " " + role.get("what_they_do", "") + " " + " ".join(role.get("tools", []))).lower()
                if search not in blob:
                    continue

            filtered_roles.append(role)
        
        total_roles += len(filtered_roles)
        cat_copy = dict(cat)
        cat_copy["roles"] = filtered_roles
        filtered_categories.append(cat_copy)

    return jsonify({
        "status": "success",
        "branch": branch or "ALL",
        "total_roles": total_roles,
        "categories": filtered_categories
    })

@app.route("/api/btech/companies")
def get_btech_companies():
    companies = load_json("companies_directory.json") or []
    comp_type = request.args.get("type", "").strip().lower()
    category = request.args.get("category", "").strip().lower()
    search = request.args.get("search", "").strip().lower()

    filtered = []
    for c in companies:
        if comp_type and comp_type != "all" and comp_type not in c.get("type", "").lower():
            continue
        if category and category != "all" and category not in [cat.lower() for cat in c.get("relevant_categories", [])]:
            continue
        if search:
            blob = (c.get("name", "") + " " + c.get("domain", "") + " " + " ".join(c.get("common_roles", [])) + " " + " ".join(c.get("verified_skills", []))).lower()
            if search not in blob:
                continue
        filtered.append(c)

    return jsonify({
        "status": "success",
        "total": len(filtered),
        "companies": filtered
    })

@app.route("/api/btech/compare")
def get_btech_comparisons():
    data = load_json("btech_post_grad_pathways.json") or {}
    comps = data.get("pathway_comparisons", [])
    comp_id = request.args.get("id", "").strip()
    if comp_id:
        target = next((c for c in comps if c["id"] == comp_id), None)
        if not target:
            return jsonify({"status": "error", "message": "Comparison not found"}), 404
        return jsonify({"status": "success", "comparison": target})
    return jsonify({"status": "success", "total": len(comps), "comparisons": comps})

@app.route("/api/btech/higher-studies")
def get_btech_higher_studies():
    data = load_json("btech_post_grad_pathways.json") or {}
    return jsonify({
        "status": "success",
        "higher_studies": data.get("higher_studies_directory", [])
    })

@app.route("/api/btech/gate")
def get_btech_gate_guide():
    data = load_json("btech_post_grad_pathways.json") or {}
    return jsonify({
        "status": "success",
        "gate_guide": data.get("gate_guide", {})
    })

@app.route("/api/btech/defence")
def get_btech_defence_pathways():
    data = load_json("btech_post_grad_pathways.json") or {}
    return jsonify({
        "status": "success",
        "defence_pathways": data.get("defence_pathways", [])
    })


def generate_rule_based_recommendation(user_profile, query_text, language="en"):
    return AIEngine.generate_qualification_aware_roadmap(user_profile, query_text, language=language)

@app.route("/api/ai/chat", methods=["POST"])
def ai_chat():
    req_data = request.get_json() or {}
    message = req_data.get("message", "").strip()
    profile = req_data.get("profile", {})
    language = (req_data.get("language") or "en").lower().strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if api_key:
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + api_key
            headers = {"Content-Type": "application/json"}
            
            verified_context = get_verified_current_data(message)
            sys_prompt = AIEngine.build_gemini_prompt(profile, message, language=language, verified_context=verified_context)

            payload = {
                "contents": [{"parts": [{"text": sys_prompt + "\n\nStudent Profile: " + json.dumps(profile) + "\nQuestion: " + message}]}],
                "generationConfig": {"temperature": 0.3, "maxOutputTokens": 1500}
            }
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                result_json = resp.json()
                reply_text = result_json["candidates"][0]["content"]["parts"][0]["text"]
                roadmap_obj = AIEngine.generate_qualification_aware_roadmap(profile, message, language=language)
                return jsonify({
                    "status": "success",
                    "mode": "gemini_ai",
                    "language": language,
                    "reply": reply_text,
                    "data": roadmap_obj,
                    "provider": "Google Gemini AI (Secured Server Engine)"
                })
        except Exception as e:
            print("Gemini API error:", e)

    # Local Knowledge Engine & Assistant (Offline / Fallback / Rule-based)
    roadmap_res = AIEngine.generate_qualification_aware_roadmap(profile, message, language=language)
    reply_answer = AIEngine.answer_assistant_question(profile, message, language=language)

    if profile:
        notifs = load_json("notifications.json")
        matches = RadarMatcher.match(profile, notifs)
        if matches:
            roadmap_res["radar_matches"] = matches[:3]

    return jsonify({
        "status": "success",
        "mode": "rule_based",
        "language": language,
        "reply": reply_answer,
        "provider": "CareerCompass Verified Knowledge Engine (Offline/Rule-Based Mode)",
        "data": roadmap_res
    })

@app.route("/api/radar/profile", methods=["GET", "POST"])
def radar_profile():
    user = get_current_user()

    if request.method == "GET":
        if user:
            prof = ProfileRepository.get_profile(user["id"])
            return jsonify({"status": "success", "profile": prof})
        prof_id = request.args.get("id", "").strip()
        if not prof_id:
            return jsonify({"status": "error", "message": "Missing profile id parameter"}), 400
        prof = RadarStorage.get_profile(prof_id)
        if not prof:
            return jsonify({"status": "not_found", "profile": None}), 404
        return jsonify({"status": "success", "profile": prof})

    # POST: Save profile and return immediate radar matches
    prof_data = request.get_json() or {}
    all_notifs = load_json("notifications.json")

    if user:
        saved_profile = ProfileRepository.save_profile(user["id"], prof_data)
        matches = RadarMatcher.match(saved_profile, all_notifs)
        # Dispatch in-app and configured alerts for this logged in user
        try:
            PipelineService.run_matching_and_dispatch_for_all_users(all_notifs)
        except Exception:
            pass
        return jsonify({
            "status": "success",
            "message": "Personal profile saved to your account and radar scan complete",
            "profile": saved_profile,
            "total_matches": len(matches),
            "matches": matches
        })

    # Guest fallback
    saved_profile = RadarStorage.save_profile(prof_data)
    matches = RadarMatcher.match(saved_profile, all_notifs)
    RadarDispatcher.dispatch_for_profile(saved_profile, all_notifs)

    return jsonify({
        "status": "success",
        "message": "Profile saved and radar scan complete",
        "profile": saved_profile,
        "total_matches": len(matches),
        "matches": matches
    })

@app.route("/api/radar/matches", methods=["POST"])
def radar_matches():
    profile_data = request.get_json() or {}
    all_notifs = load_json("notifications.json")
    matches = RadarMatcher.match(profile_data, all_notifs)
    return jsonify({
        "status": "success",
        "total_matches": len(matches),
        "matches": matches
    })

@app.route("/api/radar/alerts", methods=["GET"])
def radar_alerts():
    user = get_current_user()
    if user:
        alerts = NotificationRepository.get_user_notifications(user["id"])
        unread = NotificationRepository.get_unread_count(user["id"])
        return jsonify({
            "status": "success",
            "user_id": user["id"],
            "total_alerts": len(alerts),
            "unread_count": unread,
            "alerts": alerts
        })

    prof_id = request.args.get("id", "").strip()
    if not prof_id:
        return jsonify({"status": "error", "message": "Profile ID or login required"}), 400
    alerts = RadarStorage.get_alerts_for_profile(prof_id)
    unread = sum(1 for a in alerts if not a.get("is_read"))
    return jsonify({
        "status": "success",
        "profile_id": prof_id,
        "total_alerts": len(alerts),
        "unread_count": unread,
        "alerts": alerts
    })

@app.route("/api/radar/mark-read", methods=["POST"])
def radar_mark_read():
    user = get_current_user()
    data = request.get_json() or {}
    if user:
        delivery_id = data.get("delivery_id")
        count = NotificationRepository.mark_as_read(user["id"], delivery_id)
        return jsonify({"status": "success", "marked_read": count})

    prof_id = data.get("profile_id", "").strip()
    alert_ids = data.get("alert_ids")
    if not prof_id:
        return jsonify({"status": "error", "message": "Profile ID required"}), 400
    count = RadarStorage.mark_alerts_read(prof_id, alert_ids)
    return jsonify({"status": "success", "marked_read": count})

# ====================================================
# EXAM PREPARATION HUB REST APIs
# ====================================================

@app.route("/api/exam-prep", methods=["GET"])
@app.route("/api/exam-prep/list", methods=["GET"])
def get_exam_prep_list():
    prep_data = load_json("exam_preparation.json")
    exams = prep_data.get("exams", []) if isinstance(prep_data, dict) else []
    
    qual = request.args.get("qualification", "").strip()
    branch = request.args.get("branch", "").strip().upper()
    search = request.args.get("search", "").strip().lower()

    filtered = []
    for e in exams:
        if qual:
            target_quals = e.get("target_qualifications", [])
            if target_quals and not any(q.lower() in qual.lower() or qual.lower() in q.lower() for q in target_quals):
                continue
        if branch and branch != "ALL":
            target_branches = [b.upper() for b in e.get("target_branches", [])]
            if target_branches and "ALL" not in target_branches and "NONE" not in target_branches:
                if not any(b in branch or branch in b for b in target_branches):
                    continue
        if search:
            blob = (e.get("name", "") + " " + e.get("full_title", "") + " " + e.get("overview", "")).lower()
            if search not in blob:
                continue
        filtered.append(e)

    return jsonify({
        "status": "success",
        "total": len(filtered),
        "exams": filtered
    })

@app.route("/api/exam-prep/<exam_id>", methods=["GET"])
def get_exam_prep_detail(exam_id):
    prep_data = load_json("exam_preparation.json")
    exams = prep_data.get("exams", []) if isinstance(prep_data, dict) else []
    target = next((e for e in exams if e.get("id") == exam_id), None)
    if not target:
        return jsonify({"status": "error", "message": f"Exam '{exam_id}' not found in preparation repository."}), 404
    
    # Check if logged in user has progress/study plan for this exam
    user = get_current_user()
    user_progress = None
    user_plan = None
    if user:
        user_progress = ExamProgressRepository.get_progress(user["id"], exam_id)
        user_plan = ExamProgressRepository.get_study_plan(user["id"], exam_id)

    return jsonify({
        "status": "success",
        "exam": target,
        "user_progress": user_progress,
        "user_study_plan": user_plan
    })

@app.route("/api/exam-prep/progress", methods=["GET", "POST"])
@app.route("/api/exam-prep/<exam_id>/progress", methods=["GET", "POST"])
@login_required
def exam_prep_progress(exam_id=None):
    from flask import g
    user_id = g.user["id"]

    if request.method == "GET":
        target_exam_id = exam_id or request.args.get("exam_id", "").strip()
        if not target_exam_id:
            return jsonify({"status": "error", "message": "exam_id is required"}), 400
        progress = ExamProgressRepository.get_progress(user_id, target_exam_id)
        return jsonify({"status": "success", "progress": progress})

    data = request.get_json() or {}
    target_exam_id = exam_id or (data.get("exam_id") or "").strip()
    if not target_exam_id:
        return jsonify({"status": "error", "message": "exam_id is required"}), 400

    stage = data.get("preparation_stage", "In Progress")
    target_year = data.get("target_year")
    topics = data.get("completed_topics") or []
    notes = data.get("notes", "")

    ExamProgressRepository.save_progress(user_id, target_exam_id, stage, target_year, topics, notes)
    updated = ExamProgressRepository.get_progress(user_id, target_exam_id)
    return jsonify({
        "status": "success",
        "message": "Preparation progress saved successfully.",
        "progress": updated
    })

@app.route("/api/exam-prep/study-plan", methods=["GET", "POST"])
@login_required
def exam_study_plan():
    from flask import g
    user_id = g.user["id"]

    if request.method == "GET":
        exam_id = request.args.get("exam_id", "").strip()
        if not exam_id:
            return jsonify({"status": "error", "message": "exam_id is required"}), 400
        plan = ExamProgressRepository.get_study_plan(user_id, exam_id)
        return jsonify({"status": "success", "study_plan": plan})

    data = request.get_json() or {}
    exam_id = (data.get("exam_id") or "").strip()
    duration = data.get("duration", "3_MONTHS")
    schedule = data.get("schedule") or {}

    if not exam_id:
        return jsonify({"status": "error", "message": "exam_id is required"}), 400

    ExamProgressRepository.save_study_plan(user_id, exam_id, duration, schedule)
    saved = ExamProgressRepository.get_study_plan(user_id, exam_id)
    return jsonify({
        "status": "success",
        "message": "Study plan saved successfully.",
        "study_plan": saved
    })

# ====================================================
# WEB PUSH REST APIs
# ====================================================

@app.route("/api/push/vapid-public-key", methods=["GET"])
def push_vapid_key():
    key = PushService.get_public_key()
    return jsonify({"status": "success", "public_key": key})

@app.route("/api/push/subscribe", methods=["POST"])
@login_required
def push_subscribe():
    from flask import g
    user_id = g.user["id"]
    data = request.get_json() or {}
    endpoint = data.get("endpoint")
    keys = data.get("keys") or {}
    p256dh = keys.get("p256dh")
    auth = keys.get("auth")

    if not endpoint or not p256dh or not auth:
        return jsonify({"status": "error", "message": "Valid PushSubscription payload required."}), 400

    ua = request.headers.get("User-Agent", "")
    device_label = data.get("device_label") or ("Mobile" if "Mobi" in ua else "Desktop")

    PushRepository.save_subscription(user_id, endpoint, p256dh, auth, ua, device_label)
    return jsonify({"status": "success", "message": "Push notification subscription registered successfully."})

@app.route("/api/push/unsubscribe", methods=["POST"])
@login_required
def push_unsubscribe():
    data = request.get_json() or {}
    endpoint = data.get("endpoint")
    if endpoint:
        PushRepository.deactivate_subscription(endpoint)
    return jsonify({"status": "success", "message": "Push subscription deactivated."})

@app.route("/api/push/test", methods=["POST"])
@login_required
def push_test():
    from flask import g
    user_id = g.user["id"]
    results = PushService.send_push_to_user(
        user_id,
        title="🧭 CareerCompass Test Alert",
        message="Web Push notifications are active and verified for your device!",
        deep_link="/",
        tag="test-alert"
    )
    return jsonify({
        "status": "success",
        "message": f"Test push sent to {len(results)} device(s).",
        "results": results
    })

# ====================================================
# USER NOTIFICATIONS & SAVED OPPORTUNITIES REST APIs
# ====================================================

@app.route("/api/notifications/user", methods=["GET"])
@login_required
def get_user_notifications_route():
    from flask import g
    user_id = g.user["id"]
    deliveries = NotificationRepository.get_user_notifications(user_id)
    unread = NotificationRepository.get_unread_count(user_id)
    return jsonify({
        "status": "success",
        "total": len(deliveries),
        "unread_count": unread,
        "notifications": deliveries
    })

@app.route("/api/notifications/dismiss", methods=["POST"])
@login_required
def dismiss_notification_route():
    from flask import g
    user_id = g.user["id"]
    data = request.get_json() or {}
    delivery_id = data.get("delivery_id")
    if not delivery_id:
        return jsonify({"status": "error", "message": "delivery_id is required"}), 400
    success = NotificationRepository.dismiss(user_id, delivery_id)
    return jsonify({"status": "success", "dismissed": success})

@app.route("/api/opportunities/saved", methods=["GET"])
@login_required
def get_saved_opportunities_route():
    from flask import g
    user_id = g.user["id"]
    items = SavedOpportunitiesRepository.get_saved(user_id)
    return jsonify({"status": "success", "total": len(items), "saved_opportunities": items})

@app.route("/api/opportunities/save", methods=["POST"])
@login_required
def save_opportunity_route():
    from flask import g
    user_id = g.user["id"]
    data = request.get_json() or {}
    opp_id = data.get("opportunity_id")
    if not opp_id:
        return jsonify({"status": "error", "message": "opportunity_id is required"}), 400
    
    title = data.get("title", "")
    category = data.get("category", "")
    org = data.get("organization", "")
    deadline = data.get("deadline", "")
    url = data.get("official_url", "")

    success = SavedOpportunitiesRepository.save(user_id, opp_id, title, category, org, deadline, url)
    return jsonify({"status": "success", "saved": success})

@app.route("/api/opportunities/remove", methods=["POST"])
@login_required
def remove_saved_opportunity_route():
    from flask import g
    user_id = g.user["id"]
    data = request.get_json() or {}
    opp_id = data.get("opportunity_id")
    if not opp_id:
        return jsonify({"status": "error", "message": "opportunity_id is required"}), 400
    removed = SavedOpportunitiesRepository.remove(user_id, opp_id)
    return jsonify({"status": "success", "removed": removed})

# ====================================================
# ADMIN DATA UPDATER & REGISTRY REST APIs
# ====================================================

@app.route("/api/admin/updater-status", methods=["GET"])
def admin_updater_status():
    registry = SourceRegistry.load()
    history = ChangeDetector.load_history()
    return jsonify({
        "status": "success",
        "total_sources": len(registry),
        "registry": registry,
        "recent_changes": history[:20]
    })

@app.route("/api/admin/trigger-update", methods=["POST"])
def admin_trigger_update():
    data = request.get_json() or {}
    source_id = data.get("source_id")
    updater = DataUpdater(dry_run=False)
    report = updater.run_update(target_source_id=source_id)
    return jsonify({
        "status": "success",
        "report": report
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

@app.route("/api/admin/run-pipeline", methods=["POST"])
def admin_run_pipeline():
    updater = DataUpdater(dry_run=False)
    update_report = updater.run_update()
    all_notifs = load_json("notifications.json")
    dispatch_report = PipelineService.run_matching_and_dispatch_for_all_users(all_notifs)
    return jsonify({
        "status": "success",
        "update_report": update_report,
        "dispatch_report": dispatch_report
    })

# ====================================================
# CLIENT-SIDE WILDCARD ROUTE (MUST BE LAST)
# ====================================================

@app.route("/<path:path>")
def client_route_fallback(path=""):
    if path.startswith("api/"):
        return jsonify({"error": "Resource not found", "status": 404}), 404
    return render_template("index.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true")
    print(f"Starting CareerCompass on 0.0.0.0:{port} (Debug: {debug})")
    print(f"Local Access: http://127.0.0.1:{port}")
    print(f"Network Access: http://192.168.1.9:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)