import os
import json
from datetime import datetime, timezone
from flask import Flask, render_template, request, jsonify
import requests

from radar.models import StudentProfile
from radar.matcher import RadarMatcher
from radar.storage import RadarStorage
from radar.dispatcher import RadarDispatcher
from data_updater.registry import SourceRegistry
from data_updater.change_detector import ChangeDetector
from data_updater.updater import DataUpdater

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

def generate_rule_based_recommendation(user_profile, query_text, language="en"):
    qual = user_profile.get("qualification", "").lower()
    branch = user_profile.get("branch", "").lower()
    ql = query_text.lower()
    lang = (language or "en").lower().strip()

    # 1. DEFENCE ROADMAP
    if any(k in ql for k in ["defence", "army", "navy", "air force", "nda", "cds", "afcat"]):
        if lang == "te":
            return {
                "mode": "rule_based",
                "title": "భారత సాయుధ దళాల కెరీర్ రోడ్‌మ్యాప్ (Defence Forces)",
                "summary": "ఆర్మీ, నేవీ మరియు ఎయిర్‌ఫోర్స్‌లలో కమీషన్డ్ ఆఫీసర్ హోదాలు మరియు టెక్నికల్ ఎంట్రీల కోసం అధికారిక మార్గదర్శక ప్రణాళిక.",
                "roadmap": {
                    "current_position": qual.upper() if qual else "అభ్యర్థి (Aspirant)",
                    "suitable_options": [
                        "UPSC NDA & NA (12వ తరగతి తర్వాత: ఆర్మీ, నేవీ, ఎయిర్ ఫోర్స్ వింగ్స్)",
                        "10+2 టెక్నికల్ ఎంట్రీ స్కీమ్ (TES Army & Navy B.Tech Cadet - ఉచిత ఇంజనీరింగ్ డిగ్రీ)",
                        "UPSC CDS పరీక్ష (గ్రాడ్యుయేషన్ తర్వాత: IMA, INA, AFA, OTA)",
                        "AFCAT (ఎయిర్ ఫోర్స్ ఫ్లయింగ్ & గ్రౌండ్ డ్యూటీ బ్రాంచ్‌లు)",
                        "డైరెక్ట్ ఇంజనీరింగ్ SSB ఎంట్రీలు (Army TGC, SSC Tech, Navy Executive & Technical)",
                        "అగ్నివీర్ రిక్రూట్‌మెంట్ (జనరల్ డ్యూటీ, టెక్నికల్, ట్రేడ్స్‌మెన్)"
                    ],
                    "entrance_exams": ["UPSC NDA", "UPSC CDS", "AFCAT", "JEE Main ర్యాంక్ ఆధారంగా డైరెక్ట్ SSB"],
                    "courses": ["3-4 సంవత్సరాల అకాడమీ క్యాడెట్ శిక్షణ (JNU B.Sc / B.Tech డిగ్రీ ప్రదానం)"],
                    "colleges": ["NDA ఖడక్‌వాస్లా", "IMA డెహ్రాడూన్", "INA ఎజిమల", "AFA దుండిగల్", "OTA చెన్నై"],
                    "skills": ["ఆఫీసర్ లైక్ క్వాలిటీస్ (OLQ)", "శారీరక సామర్థ్యం (2.4 కి.మీ రన్నింగ్, పుష్-అప్స్)", "కరెంట్ అఫైర్స్ & మానసిక స్థిరత్వం"],
                    "career": "లెఫ్టినెంట్ / సబ్ లెఫ్టినెంట్ / ఫ్లయింగ్ ఆఫీసర్‌గా కమిషన్ (7వ వేతన సంఘం లెవల్ 10: ప్రారంభ మూల వేతనం రూ. 56,100 + రూ. 15,500 MSP)",
                    "next_steps": [
                        "joinindianarmy.nic.in లో అధికారిక ఎత్తు మరియు వైద్య నిబంధనలను తనిఖీ చేయండి.",
                        "రాబోయే NDA/CDS నోటిఫికేషన్ తేదీల కోసం UPSC క్యాలెండర్‌ను చూడండి.",
                        "CareerCompass డిజిటల్ లైబ్రరీలో గత 5 సంవత్సరాల NDA/CDS ప్రశ్నపత్రాలను సాధన చేయండి."
                    ]
                },
                "disclaimer": "CareerCompass ధృవీకరించిన సమాచారం. అధికారిక గెజిట్ ప్రకారం ఖచ్చితమైన వయస్సు మరియు శారీరక ప్రమాణాలు వర్తిస్తాయి."
            }
        elif lang == "hi":
            return {
                "mode": "rule_based",
                "title": "भारतीय सशस्त्र बल करियर रोडमैप (Defence Forces)",
                "summary": "थल सेना, नौसेना और वायु सेना में कमीशन प्राप्त अधिकारी पदों और तकनीकी प्रविष्टियों के लिए समर्पित रोडमैप।",
                "roadmap": {
                    "current_position": qual.upper() if qual else "उम्मीदवार (Aspirant)",
                    "suitable_options": [
                        "UPSC NDA & NA (12वीं के बाद: थल सेना, नौसेना, वायु सेना)",
                        "10+2 तकनीकी प्रविष्टि योजना (TES Army & Navy B.Tech Cadet)",
                        "UPSC CDS परीक्षा (स्नातक के बाद: IMA, INA, AFA, OTA)",
                        "AFCAT (वायु सेना फ्लाइंग और ग्राउंड ड्यूटी शाखाएं)",
                        "डायरेक्ट इंजीनियरिंग SSB प्रविष्टियां (Army TGC, SSC Tech, Navy Executive)",
                        "अग्निवीर भर्ती (जनरल ड्यूटी, टेक्निकल, ट्रेड्समैन)"
                    ],
                    "entrance_exams": ["UPSC NDA", "UPSC CDS", "AFCAT", "B.Tech / JEE रैंक आधारित डायरेक्ट SSB"],
                    "courses": ["3-4 वर्ष का सैन्य प्रशिक्षण (JNU B.Sc/B.Tech डिग्री प्रदान की जाती है)"],
                    "colleges": ["NDA खडकवासला", "IMA देहरादून", "INA एझिमाला", "AFA डुंडीगल", "OTA चेन्नई"],
                    "skills": ["ऑफिसर लाइक क्वालिटीज (OLQ)", "शारीरिक फिटनेस (2.4 किमी दौड़, पुश-अप्स)", "सामान्य ज्ञान एवं मनोवैज्ञानिक स्थिरता"],
                    "career": "लेफ्टिनेंट / सब लेफ्टिनेंट / फ्लाइंग ऑफिसर (7वां वेतन आयोग लेवल 10: मूल वेतन रु 56,100 + रु 15,500 MSP)",
                    "next_steps": [
                        "joinindianarmy.nic.in पर आधिकारिक शारीरिक एवं चिकित्सा नियम देखें।",
                        "आगामी परीक्षाओं के लिए UPSC का वार्षिक कैलेंडर जांचें।",
                        "CareerCompass डिजिटल लाइब्रेरी से पिछले 5 वर्षों के प्रश्नपत्र हल करें।"
                    ]
                },
                "disclaimer": "CareerCompass सत्यापित मार्गदर्शन। आधिकारिक राजपत्र के अनुसार सख्त आयु व चिकित्सा मानदंड लागू।"
            }
        else:
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

    # 2. 10TH ROADMAP
    if any(k in ql for k in ["10th", "class 10"]) or "10th" in qual:
        if lang == "te":
            return {
                "mode": "rule_based",
                "title": "10వ తరగతి తర్వాత విద్యా & కెరీర్ రోడ్‌మ్యాప్",
                "summary": "ఇంటర్మీడియట్ విభాగాలు, 3 సంవత్సరాల పాలిటెక్నిక్ డిప్లొమా, ITI ట్రేడ్‌లు మరియు రక్షణ రంగ అవకాశాల పూర్తి సమాచారం.",
                "roadmap": {
                    "current_position": "10వ తరగతి ఉత్తీర్ణత (Class 10th Passed)",
                    "suitable_options": [
                        "ఇంటర్మీడియట్ MPC (B.Tech, NDA, ఆర్కిటెక్చర్, ప్యూర్ సైన్సెస్ కోసం)",
                        "ఇంటర్మీడియట్ BiPC (MBBS, BDS, ఫార్మసీ, అగ్రికల్చర్, నర్సింగ్ కోసం)",
                        "ఇంటర్మీడియట్ MEC / CEC (CA, CMA, CS, B.Com, లా కోసం)",
                        "ఇంజనీరింగ్ పాలిటెక్నిక్ డిప్లొమా (CSE, ECE, EEE, Mech, Civil) - ECET ద్వారా నేరుగా 2వ సంవత్సరం B.Tech",
                        "ITI టెక్నికల్ ట్రేడ్‌లు (ఎలక్ట్రీషియన్, ఫిట్టర్, COPA) - తక్షణ రైల్వే & PSU ఉద్యోగాల కోసం",
                        "డిఫెన్స్ అగ్నివీర్ మార్గాలు (Army GD, Navy MR)"
                    ],
                    "entrance_exams": ["రాష్ట్ర POLYCET (డిప్లొమా కోసం)", "APRJC / TSRJC (రెసిడెన్షియల్ కాలేజీలు)", "ఆర్మీ అగ్నివీర్ CEE"],
                    "courses": ["10+2 ఇంటర్మీడియట్ (2 సం.)", "పాలిటెక్నిక్ డిప్లొమా (3 సం.)", "ITI (1-2 సం.)"],
                    "colleges": ["ప్రభుత్వ & ప్రైవేట్ జూనియర్ కాలేజీలు, పాలిటెక్నిక్ ఇన్‌స్టిట్యూట్‌లు, ITIలు"],
                    "skills": ["గణితం & సైన్స్ ప్రాథమిక అంశాలు", "ఇంగ్లీష్ కమ్యూనికేషన్", "ప్రాథమిక కంప్యూటర్ పరిజ్ఞానం"],
                    "career": "గ్రాడ్యుయేట్ ప్రొఫెషనల్, జూనియర్ ఇంజనీర్, ప్రభుత్వ ఉద్యోగి లేదా రక్షణ దళాల సైనికుడు",
                    "next_steps": [
                        "మీ ఆసక్తిని విశ్లేషించుకోండి (గణితం vs బయాలజీ vs కామర్స్/ఆర్ట్స్).",
                        "ప్రాక్టికల్ ఇంజనీరింగ్ పట్ల ఆసక్తి ఉంటే polycetap.nic.in లో తేదీలను చూడండి.",
                        "10వ తరగతి సర్టిఫికెట్లతో ఇంటర్మీడియట్ అడ్మిషన్ల కోసం సిద్ధంగా ఉండండి."
                    ]
                },
                "disclaimer": "CareerCompass ధృవీకరించిన సమాచారం. ప్రవేశ గడువులు రాష్ట్ర విద్యా బోర్డుల పరిధిలో ఉంటాయి."
            }
        elif lang == "hi":
            return {
                "mode": "rule_based",
                "title": "10वीं कक्षा के बाद करियर रोडमैप",
                "summary": "इंटरमीडिएट संकाय, 3 वर्षीय पॉलीटेक्निक डिप्लोमा, आईटीआई और रक्षा सेवा प्रविष्टियों का विस्तृत मार्गदर्शन।",
                "roadmap": {
                    "current_position": "10वीं कक्षा उत्तीर्ण (Secondary School)",
                    "suitable_options": [
                        "इंटरमीडिएट MPC (B.Tech, NDA, आर्किटेक्चर, विज्ञान के लिए)",
                        "इंटरमीडिएट BiPC (MBBS, BDS, फार्मेसी, कृषि, नर्सिंग के लिए)",
                        "इंटरमीडिएट MEC / CEC (CA, CMA, CS, B.Com, कानून के लिए)",
                        "पॉलीटेक्निक इंजीनियरिंग डिप्लोमा (CSE, ECE, EEE, Mech, Civil) - ECET द्वारा B.Tech में लेटरल एंट्री",
                        "आईटीआई तकनीकी ट्रेड्स (इलेक्ट्रीशियन, फिटर, कोपा) - रेलवे व PSU नौकरियों के लिए",
                        "रक्षा सेवा अग्निवीर (Army GD, Navy MR)"
                    ],
                    "entrance_exams": ["राज्य POLYCET (डिप्लोमा हेतु)", "APRJC / TSRJC", "आर्मी अग्निवीर CEE"],
                    "courses": ["10+2 इंटरमीडिएट (2 वर्ष)", "पॉलीटेक्निक डिप्लोमा (3 वर्ष)", "आईटीआई (1-2 वर्ष)"],
                    "colleges": ["सरकारी व मान्यता प्राप्त जूनियर कॉलेज, पॉलीटेक्निक संस्थान, आईटीआई"],
                    "skills": ["गणित और विज्ञान के मूल सिद्धांत", "अंग्रेजी संचार", "कंप्यूटर संचालन"],
                    "career": "ग्रेजुएट प्रोफेशनल, कनिष्ठ अभियंता (JE), सिविल सेवा या सेना में सैनिक",
                    "next_steps": [
                        "अपनी शैक्षणिक रुचि का विश्लेषण करें (गणित vs जीव विज्ञान vs वाणिज्य).",
                        "इंजीनियरिंग में रुचि होने पर polycetap.nic.in पर तारीखें देखें।",
                        "कक्षा 10वीं के मूल प्रमाणपत्र तैयार रखें।"
                    ]
                },
                "disclaimer": "CareerCompass सत्यापित मार्गदर्शन। प्रवेश तिथियां संबंधित शिक्षा बोर्डों द्वारा तय की जाती हैं।"
            }
        else:
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

    # 3. DIPLOMA ROADMAP
    if any(k in ql for k in ["diploma", "polytechnic"]) or "diploma" in qual:
        if lang == "te":
            return {
                "mode": "rule_based",
                "title": "పాలిటెక్నిక్ డిప్లొమా విద్యార్థుల కెరీర్ రోడ్‌మ్యాప్",
                "summary": "ECET ద్వారా నేరుగా 2వ సంవత్సరం B.Tech ప్రవేశం, కేంద్ర/రాష్ట్ర జూనియర్ ఇంజనీర్ ప్రభుత్వ ఉద్యోగాలు లేదా కోర్ పరిశ్రమల అవకాశాలు.",
                "roadmap": {
                    "current_position": "ఇంజనీరింగ్ డిప్లొమా (" + (branch.upper() if branch else "ఇంజనీరింగ్ బ్రాంచ్") + ")",
                    "suitable_options": [
                        "B.Tech లాటరల్ ఎంట్రీ (ECET ద్వారా నేరుగా 2వ సంవత్సరం / 3వ సెమిస్టర్)",
                        "కేంద్ర ప్రభుత్వ జూనియర్ ఇంజనీర్ పోస్టులు (RRB JE, SSC JE, DRDO CEPTAM, ISRO టెక్నికల్ అసిస్టెంట్)",
                        "కోర్ పరిశ్రమల ఇంజనీరింగ్ ఉద్యోగాలు (Tata Motors, L&T, BHEL, NTPC, Siemens)",
                        "నెలకు స్టైపెండ్‌తో నేషనల్ అప్రెంటిస్‌షిప్ ట్రైనింగ్ స్కీమ్ (NATS)",
                        "డిఫెన్స్ టెక్నికల్ ట్రేడ్‌లు (IAF గ్రూప్ X, నేవీ సైలర్, ఆర్మీ టెక్నికల్)"
                    ],
                    "entrance_exams": ["రాష్ట్ర ECET (AP ECET, TS ECET, JELET)", "RRB JE", "SSC JE", "DRDO CEPTAM"],
                    "courses": ["B.Tech డిగ్రీ (లాటరల్ ఎంట్రీ ద్వారా 3 సం.)", "అడ్వాన్స్‌డ్ CAD/CAM, PLC-SCADA, AWS క్లౌడ్"],
                    "colleges": ["యూనివర్సిటీ ఇంజనీరింగ్ కళాశాలలు, ప్రముఖ అటానమస్ ఇన్‌స్టిట్యూట్‌లు"],
                    "skills": ["కోర్ బ్రాంచ్ ప్రాక్టికల్ ఇంజనీరింగ్", "AutoCAD / MATLAB / Python / సర్క్యూట్ సిమ్యులేషన్", "JE పరీక్షలకు జనరల్ ఆప్టిట్యూడ్"],
                    "career": "గ్రాడ్యుయేట్ ఇంజనీర్, జూనియర్ ఇంజనీర్, అసిస్టెంట్ ఎగ్జిక్యూటివ్ ఇంజనీర్, ప్లాంట్ సూపర్‌వైజర్",
                    "next_steps": [
                        "B.Tech కొరకు: కోర్ ఇంజనీరింగ్ సబ్జెక్టులతో పాటు మ్యాథ్స్, ఫిజిక్స్, కెమిస్ట్రీ ప్రిపేర్ అవ్వండి.",
                        "ప్రభుత్వ ఉద్యోగాల కొరకు: RRB JE / SSC JE సిలబస్ డౌన్‌లోడ్ చేసుకుని ప్రాక్టీస్ చేయండి.",
                        "చెల్లింపులతో కూడిన పరిశ్రమ శిక్షణ కోసం nats.education.gov.in లో నమోదు చేసుకోండి."
                    ]
                },
                "disclaimer": "CareerCompass ధృవీకరించిన సమాచారం. AICTE మరియు ఉన్నత విద్యా మండలి నిబంధనల ప్రకారం ప్రవేశాలు ఉంటాయి."
            }
        elif lang == "hi":
            return {
                "mode": "rule_based",
                "title": "पॉलीटेक्निक डिप्लोमा धारकों के लिए करियर रोडमैप",
                "summary": "ECET के माध्यम से B.Tech 2nd वर्ष में सीधा प्रवेश, रेलवे/SSC जूनियर इंजीनियर सरकारी नौकरियां या कोर तकनीकी उद्योग।",
                "roadmap": {
                    "current_position": "डिप्लोमा इन इंजीनियरिंग (" + (branch.upper() if branch else "इंजीनियरिंग शाखा") + ")",
                    "suitable_options": [
                        "B.Tech लेटरल एंट्री (ECET द्वारा सीधे द्वितीय वर्ष / तीसरे सेमेस्टर में प्रवेश)",
                        "केंद्र सरकार के कनिष्ठ अभियंता (JE) पद (RRB JE, SSC JE, DRDO CEPTAM, ISRO सहायक)",
                        "प्रमुख कोर उद्योग नौकरियां (Tata Motors, L&T, BHEL, NTPC, Siemens)",
                        "मासिक स्टाइपेंड के साथ नेशनल अप्रेंटिसशिप ट्रेनिंग स्कीम (NATS)",
                        "रक्षा तकनीकी ट्रेड्स (IAF ग्रुप X, नेवी सेलर, आर्मी टेक्निकल)"
                    ],
                    "entrance_exams": ["राज्य ECET (AP ECET, TS ECET, JELET)", "RRB JE", "SSC JE", "DRDO CEPTAM"],
                    "courses": ["B.Tech डिग्री (लेटरल एंट्री द्वारा 3 वर्ष)", "CAD/CAM, PLC-SCADA, AWS Cloud"],
                    "colleges": ["राज्य विश्वविद्यालय इंजीनियरिंग कॉलेज, प्रमुख स्वायत्त संस्थान"],
                    "skills": ["व्यावहारिक इंजीनियरिंग ज्ञान", "AutoCAD / MATLAB / Python", "प्रतियोगी परीक्षाओं के लिए एप्टीट्यूड"],
                    "career": "ग्रेजुएट इंजीनियर, जूनियर इंजीनियर, सहायक कार्यकारी अभियंता, प्लांट सुपरवाइजर",
                    "next_steps": [
                        "B.Tech के लिए: राज्य ECET के मुख्य विषयों और गणित, भौतिकी, रसायन विज्ञान की तैयारी करें।",
                        "सरकारी नौकरियों के लिए: RRB JE / SSC JE का पाठ्यक्रम डाउनलोड कर तकनीकी विषयों का अध्ययन करें।",
                        "सशुल्क औद्योगिक प्रशिक्षण के लिए nats.education.gov.in पर पंजीकरण करें।"
                    ]
                },
                "disclaimer": "CareerCompass सत्यापित मार्गदर्शन। लेटरल एंट्री नियम AICTE एवं संबंधित उच्च शिक्षा परिषदों के अनुसार।"
            }
        else:
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

    # 4. B.TECH / ENGINEERING ROADMAP
    if any(k in ql for k in ["b.tech", "btech", "engineering", "software", "gate", "cse", "it"]) or "b.tech" in qual:
        if lang == "te":
            return {
                "mode": "rule_based",
                "title": "ఇంజనీరింగ్ (B.Tech / B.E.) విద్యార్థుల కెరీర్ రోడ్‌మ్యాప్",
                "summary": "ఉన్నత స్థాయి సాఫ్ట్‌వేర్ టెక్నాలజీ కెరీర్లు, ఐఐటీలలో M.Tech & మహారత్న PSUల కోసం GATE, UPSC ఇంజనీరింగ్ సర్వీసెస్ లేదా డిఫెన్స్ టెక్నికల్ ఆఫీసర్ ఎంట్రీలు.",
                "roadmap": {
                    "current_position": "B.Tech / B.E. (" + (branch.upper() if branch else "ఇంజనీరింగ్") + ")",
                    "suitable_options": [
                        "హై-గ్రోత్ టెక్నాలజీ కెరీర్లు: SDE, ఫుల్ స్టాక్ డెవలపర్, DevOps, AI/ML, సైబర్ సెక్యూరిటీ",
                        "GATE పరీక్ష: టాప్ IITలలో M.Tech (నెలకు రూ. 12,400 స్టైపెండ్‌తో) లేదా ONGC, IOCL, NTPC, BHEL PSUలలో నేరుగా రిక్రూట్‌మెంట్ (CTC రూ. 15-22 LPA)",
                        "UPSC ఇంజనీరింగ్ సర్వీసెస్ (ESE / IES) - క్లాస్ 1 గెజిటెడ్ కేంద్ర ఇంజనీరింగ్ ఆఫీసర్ హోదా",
                        "డిఫెన్స్ టెక్నికల్ ఎంట్రీలు (Army TGC, SSC Tech, Navy SSC) - మార్కుల ఆధారంగా డైరెక్ట్ 5-రోజుల SSB ఇంటర్వ్యూ",
                        "విదేశీ ఉన్నత విద్య (GRE/TOEFL ద్వారా MS) లేదా లీడర్‌షిప్ మేనేజ్‌మెంట్ (CAT ద్వారా MBA)"
                    ],
                    "entrance_exams": ["GATE", "UPSC ESE / IES", "CAT", "GRE & TOEFL", "IBPS SO IT ఆఫీసర్"],
                    "courses": ["B.Tech డిగ్రీ పూర్తి చేయడం", "M.Tech / MS (రీసెర్చ్)", "క్లౌడ్ & సైబర్ సెక్యూరిటీ సర్టిఫికేషన్లు"],
                    "colleges": ["IITలు, NITలు, IISc బెంగళూరు, IIMలు, ప్రపంచ ప్రఖ్యాత యూనివర్సిటీలు"],
                    "skills": ["డేటా స్ట్రక్చర్స్ & అల్గారిథమ్స్ (LeetCode)", "సిస్టమ్ డిజైన్", "Git & CI/CD", "కోర్ ఇంజనీరింగ్ సూత్రాలు"],
                    "career": "సాఫ్ట్‌వేర్ ఆర్కిటెక్ట్, PSU ఎగ్జిక్యూటివ్ ట్రైనీ, కేంద్ర గెజిటెడ్ ఆఫీసర్, డిఫెన్స్ టెక్నికల్ ఆఫీసర్",
                    "next_steps": [
                        "టెక్నాలజీ జాబ్స్ కోసం: 150+ DSA సమస్యలను సాధన చేయండి మరియు 2 నాణ్యమైన ఫుల్-స్టాక్ ప్రాజెక్టులను నిర్మించండి.",
                        "PSUలు/M.Tech కోసం: gate2025.iitr.ac.in లో నమోదు చేసుకుని గత 20 సంవత్సరాల ప్రశ్నపత్రాలను సాధన చేయండి.",
                        "డిఫెన్స్ కోసం: TGC/SSC టెక్నికల్ ఎంట్రీ కటాఫ్ మార్కులను joinindianarmy.nic.in లో పరిశీలించండి."
                    ]
                },
                "disclaimer": "CareerCompass ధృవీకరించిన సమాచారం. సిఫార్సులు మార్గదర్శనం కొరకు మాత్రమే; తుది ఎంపిక మీ నైపుణ్యాలపై ఆధారపడి ఉంటుంది."
            }
        elif lang == "hi":
            return {
                "mode": "rule_based",
                "title": "B.Tech / B.E. इंजीनियरों के लिए करियर रोडमैप",
                "summary": "सॉफ्टवेयर और टेक करियर, शीर्ष IIT में M.Tech व महारत्न PSU के लिए GATE, UPSC इंजीनियरिंग सर्विसेज (ESE) या रक्षा तकनीकी अधिकारी प्रविष्टियां।",
                "roadmap": {
                    "current_position": "B.Tech / B.E. (" + (branch.upper() if branch else "इंजीनियरिंग") + ")",
                    "suitable_options": [
                        "उच्च विकास टेक करियर: SDE, फुल स्टैक डेवलपर, DevOps, AI/ML, साइबर सुरक्षा",
                        "GATE परीक्षा: शीर्ष IIT से M.Tech (रु 12,400/माह वजीफा) या ONGC, IOCL, NTPC में सीधी भर्ती (CTC रु 15-22 LPA)",
                        "UPSC इंजीनियरिंग सर्विसेज (ESE / IES) - प्रथम श्रेणी राजपत्रित केंद्रीय अधिकारी",
                        "रक्षा तकनीकी प्रविष्टियां (Army TGC, SSC Tech, Navy SSC) - इंजीनियरिंग अंकों के आधार पर सीधा 5-दिवसीय SSB",
                        "विदेश में उच्च शिक्षा (GRE/TOEFL द्वारा MS) या प्रबंधन नेतृत्व (CAT द्वारा MBA)"
                    ],
                    "entrance_exams": ["GATE", "UPSC ESE / IES", "CAT", "GRE & TOEFL", "IBPS SO IT ऑफिसर"],
                    "courses": ["B.Tech डिग्री पूर्ण करना", "M.Tech / MS (रिसर्च)", "क्लाउड एवं साइबर सुरक्षा सर्टिफिकेशन"],
                    "colleges": ["IITs, NITs, IISc बैंगलोर, IIMs, वैश्विक शीर्ष विश्वविद्यालय"],
                    "skills": ["डेटा स्ट्रक्चर्स एवं एल्गोरिदम (DSA)", "सिस्टम डिजाइन", "Git और CI/CD", "कोर इंजीनियरिंग सिद्धांत"],
                    "career": "सॉफ्टवेयर आर्किटेक्ट, PSU एग्जीक्यूटिव ट्रेनी, केंद्रीय राजपत्रित अधिकारी, रक्षा अधिकारी",
                    "next_steps": [
                        "टेक नौकरियों के लिए: 150+ DSA प्रश्नों का अभ्यास करें और 2 लाइव फुल-स्टैक प्रोजेक्ट बनाएं।",
                        "PSU/M.Tech के लिए: gate2025.iitr.ac.in पर GATE पंजीकरण करें और 20 वर्षों के पिछले प्रश्न हल करें।",
                        "डिफेंस के लिए: TGC / SSC Tech कट-ऑफ अंक joinindianarmy.nic.in पर देखें।"
                    ]
                },
                "disclaimer": "CareerCompass सत्यापित मार्गदर्शन। सिफारिशें केवल मार्गदर्शन हेतु हैं; अंतिम चयन कौशल पर निर्भर करता है।"
            }
        else:
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

    # 5. GENERAL ROADMAP
    if lang == "te":
        return {
            "mode": "rule_based",
            "title": "వ్యక్తిగత విద్యా మరియు కెరీర్ మార్గదర్శక రోడ్‌మ్యాప్",
            "summary": "మీ ప్రొఫైల్ (" + (qual.upper() if qual else "విద్యార్థి") + " - " + (branch.upper() if branch else "జనరల్ స్ట్రీమ్") + ") ఆధారంగా రూపొందించిన దశలవారీ కెరీర్ ప్రణాళిక.",
            "roadmap": {
                "current_position": qual.upper() if qual else "ప్రస్తుత విద్యా స్థాయి",
                "suitable_options": [
                    "ఉన్నత ప్రత్యేక డిగ్రీ ప్రోగ్రామ్‌లు (గ్రాడ్యుయేషన్ / పోస్ట్ గ్రాడ్యుయేషన్)",
                    "కేంద్ర & రాష్ట్ర ప్రభుత్వ పోటీ పరీక్షలు (UPSC, SSC, బ్యాంకింగ్, స్టేట్ PSC)",
                    "కార్పొరేట్ ప్రైవేట్ రంగ ఉద్యోగాలు",
                    "డిఫెన్స్ ఆఫీసర్ కమిషన్లు (CDS, AFCAT, టెక్నికల్ ఎంట్రీలు)"
                ],
                "entrance_exams": ["UPSC CSE / SSC CGL", "IBPS బ్యాంకింగ్ పరీక్షలు", "రాష్ట్ర CETలు", "CAT / GATE / CUET"],
                "courses": ["గుర్తింపు పొందిన విశ్వవిద్యాలయ డిగ్రీ", "ఇండస్ట్రీ-అలైన్డ్ స్కిల్ సర్టిఫికేషన్లు"],
                "colleges": ["కేంద్ర విశ్వవిద్యాలయాలు, రాష్ట్ర యూనివర్సిటీ కళాశాలలు, జాతీయ ఇన్‌స్టిట్యూట్‌లు"],
                "skills": ["ఎనలిటికల్ రీజనింగ్ & ఆప్టిట్యూడ్", "ప్రొఫెషనల్ కమ్యూనికేషన్", "డిజిటల్ పరిజ్ఞానం"],
                "career": "అడ్మినిస్ట్రేటివ్ ఆఫీసర్, కార్పొరేట్ ప్రొఫెషనల్, బ్యాంకింగ్ ఆఫీసర్, టెక్నికల్ స్పెషలిస్ట్",
                "next_steps": [
                    "మీ స్పష్టమైన లక్ష్యాన్ని ఎంచుకోండి: ప్రభుత్వ ఉద్యోగం vs ప్రైవేట్ రంగం vs ఉన్నత చదువులు.",
                    "CareerCompass నోటిఫికేషన్ సెంటర్‌లో తాజా అధికారిక గడువు తేదీలను చూడండి.",
                    "CareerCompass డిజిటల్ లైబ్రరీలో ఉచిత అధికారిక స్టడీ మెటీరియల్ ఉపయోగించుకోండి."
                ]
            },
            "disclaimer": "CareerCompass ధృవీకరించిన సమాచారం. ఇది కేవలం విద్యా మార్గదర్శనం కొరకు మాత్రమే."
        }
    elif lang == "hi":
        return {
            "mode": "rule_based",
            "title": "व्यक्तिगत शिक्षा और करियर मार्गदर्शन रोडमैप",
            "summary": "आपकी प्रोफाइल (" + (qual.upper() if qual else "छात्र") + " - " + (branch.upper() if branch else "सामान्य संकाय") + ") पर आधारित चरणबद्ध करियर मार्गदर्शन।",
            "roadmap": {
                "current_position": qual.upper() if qual else "वर्तमान शैक्षिक स्तर",
                "suitable_options": [
                    "उच्च विशिष्ट डिग्री पाठ्यक्रम (स्नातक / स्नातकोत्तर)",
                    "केंद्र व राज्य सरकार की प्रतियोगी परीक्षाएं (UPSC, SSC, बैंकिंग, राज्य PSC)",
                    "विकासशील निजी कॉर्पोरेट क्षेत्र में करियर",
                    "रक्षा सेवा अधिकारी कमीशन (CDS, AFCAT, तकनीकी प्रविष्टियां)"
                ],
                "entrance_exams": ["UPSC CSE / SSC CGL", "IBPS बैंकिंग परीक्षाएं", "राज्य CET", "CAT / GATE / CUET"],
                "courses": ["मान्यता प्राप्त विश्वविद्यालय डिग्री", "उद्योग कौशल प्रमाणन पाठ्यक्रम"],
                "colleges": ["केंद्रीय विश्वविद्यालय, राज्य स्तरीय कॉलेज, राष्ट्रीय संस्थान"],
                "skills": ["तार्किक क्षमता एवं एप्टीट्यूड", "व्यावसायिक संचार", "डिजिटल साक्षरता"],
                "career": "प्रशासनिक अधिकारी, कॉर्पोरेट विशेषज्ञ, बैंक अधिकारी, तकनीकी विशेषज्ञ",
                "next_steps": [
                    "अपना स्पष्ट लक्ष्य तय करें: सरकारी सेवा vs कॉर्पोरेट उद्योग vs उच्च शिक्षा।",
                    "CareerCompass अधिसूचना केंद्र में सत्यापित समय-सीमाएं देखें।",
                    "CareerCompass डिजिटल लाइब्रेरी से निःशुल्क अध्ययन सामग्री का लाभ उठाएं।"
                ]
            },
            "disclaimer": "CareerCompass सत्यापित मार्गदर्शन। यह केवल मार्गदर्शन हेतु है।"
        }
    else:
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
    language = (req_data.get("language") or "en").lower().strip()

    if not message:
        return jsonify({"error": "Message is required"}), 400

    api_key = os.environ.get("GEMINI_API_KEY", "").strip()

    if api_key:
        try:
            url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=" + api_key
            headers = {"Content-Type": "application/json"}
            
            lang_instruction = ""
            if language == "te":
                lang_instruction = (
                    "\n\nCRITICAL LOCALIZATION REQUIREMENT: The user has selected Telugu (తెలుగు) as their language. "
                    "You MUST write your entire response in natural, fluent, grammatically sound Telugu. "
                    "Keep standard technical terms and acronyms (like GATE, JEE, UPSC, CSE, B.Tech, Python, ISRO, IIT, NIT) in Latin/English script, "
                    "but write all explanations, descriptions, roadmaps, and career advice thoroughly in natural Telugu."
                )
            elif language == "hi":
                lang_instruction = (
                    "\n\nCRITICAL LOCALIZATION REQUIREMENT: The user has selected Hindi (हिन्दी) as their language. "
                    "You MUST write your entire response in natural, fluent, grammatically sound Hindi. "
                    "Keep standard technical terms and acronyms (like GATE, JEE, UPSC, CSE, B.Tech, Python, ISRO, IIT, NIT) in Latin/English script, "
                    "but write all explanations, descriptions, roadmaps, and career advice thoroughly in natural Hindi."
                )

            sys_prompt = (
                "You are CareerCompass AI Career Guide for Indian students. "
                "Provide compassionate, highly accurate educational guidance after 10th, 12th, Diploma, Degree, or B.Tech. "
                "NEVER hallucinate examination dates, application deadlines, cutoffs, or fees. "
                "Structure roadmaps as: CURRENT POSITION -> SUITABLE OPTIONS -> ENTRANCE EXAMS -> COURSES -> COLLEGES -> SKILLS -> CAREER -> NEXT STEPS. "
                "Always remind students that recommendations are guidance only and refer to official government portals."
                + lang_instruction
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
                    "language": language,
                    "reply": reply_text,
                    "provider": "Google Gemini AI (Secured Server Engine)"
                })
        except Exception as e:
            print("Gemini API error:", e)

    fallback_res = generate_rule_based_recommendation(profile, message, language=language)
    if profile:
        notifs = load_json("notifications.json")
        matches = RadarMatcher.match(profile, notifs)
        if matches:
            fallback_res["radar_matches"] = matches[:3]
    return jsonify({
        "status": "success",
        "mode": "rule_based",
        "language": language,
        "provider": "CareerCompass Verified Knowledge Engine (Offline/Rule-Based Mode)",
        "data": fallback_res
    })

@app.route("/api/radar/profile", methods=["GET", "POST"])
def radar_profile():
    if request.method == "GET":
        prof_id = request.args.get("id", "").strip()
        if not prof_id:
            return jsonify({"status": "error", "message": "Missing profile id parameter"}), 400
        prof = RadarStorage.get_profile(prof_id)
        if not prof:
            return jsonify({"status": "not_found", "profile": None}), 404
        return jsonify({"status": "success", "profile": prof})

    # POST: Save profile and return immediate radar matches
    prof_data = request.get_json() or {}
    saved_profile = RadarStorage.save_profile(prof_data)
    
    # Run immediate matching against verified notifications
    all_notifs = load_json("notifications.json")
    matches = RadarMatcher.match(saved_profile, all_notifs)
    
    # Dispatch any initial unread alerts for this profile
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
    prof_id = request.args.get("id", "").strip()
    if not prof_id:
        return jsonify({"status": "error", "message": "Profile ID required"}), 400
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
    data = request.get_json() or {}
    prof_id = data.get("profile_id", "").strip()
    alert_ids = data.get("alert_ids")  # None or list of ids
    if not prof_id:
        return jsonify({"status": "error", "message": "Profile ID required"}), 400
    count = RadarStorage.mark_alerts_read(prof_id, alert_ids)
    return jsonify({"status": "success", "marked_read": count})

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

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_DEBUG", "0").lower() in ("1", "true")
    print(f"Starting CareerCompass on 0.0.0.0:{port} (Debug: {debug})")
    print(f"Local Access: http://127.0.0.1:{port}")
    print(f"Network Access: http://192.168.1.9:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)