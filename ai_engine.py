"""
CareerCompass AI Career Guide & Knowledge Engine
Provides qualification-aware personalized roadmaps and answers
strictly adapted to student educational stage and stream.
"""
import json
import os
import re
from typing import Dict, Any, List, Optional

def load_data_file(filename: str) -> Any:
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "data", filename)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

STOPWORDS = {
    "what", "when", "where", "which", "with", "from", "that", "this", "their", "there",
    "the", "and", "for", "are", "can", "you", "not", "all", "any", "how", "who", "whom",
    "whose", "why", "our", "your", "his", "her", "its", "been", "being", "have", "has",
    "had", "does", "did", "doing", "would", "could", "should", "shall", "into", "onto",
    "upon", "over", "under", "about", "above", "below", "between", "both", "each", "few",
    "more", "most", "other", "some", "such", "only", "own", "same", "than", "too", "very",
    "will", "just", "now", "much", "many", "application", "applications", "apply", "applying",
    "deadline", "deadlines", "opening", "openings", "date", "dates", "fee", "fees", "cost",
    "vacancy", "vacancies", "exam", "exams", "examination", "test", "tests", "please",
    "tell", "give", "show", "know", "details", "detail", "info", "information", "current",
    "latest", "update", "updates", "eligible", "eligibility", "process", "window", "portal",
    "registration", "admissions", "admission", "online", "form", "forms", "time", "timing",
    "schedule", "random", "want"
}

def get_verified_current_data(query: str) -> List[Dict[str, Any]]:
    """
    Looks up official verified opportunities/notifications in the local database.
    Prevents hallucinating examination dates, application windows, or vacancies.
    """
    q_lower = query.lower()
    tokens = [t.strip("?,.:;!'\"()") for t in q_lower.split()]
    meaningful_terms = [t for t in tokens if len(t) > 2 and t not in STOPWORDS]
    
    if not meaningful_terms:
        return []

    notifs = load_data_file("notifications.json")
    if not isinstance(notifs, list):
        notifs = notifs.get("notifications", []) if isinstance(notifs, dict) else []

    matches = []
    for item in notifs:
        title = item.get("title", "").lower()
        org = item.get("organization", "").lower()
        if any(re.search(r'\b' + re.escape(term) + r'\b', title) or re.search(r'\b' + re.escape(term) + r'\b', org) for term in meaningful_terms):
            matches.append(item)
    return matches[:3]

class AIEngine:
    @staticmethod
    def normalize_qualification(qual: str) -> str:
        q = (qual or "").strip().lower()
        if any(k in q for k in ["10", "ssc", "tenth", "metric"]):
            return "10th"
        if any(k in q for k in ["inter", "12", "plus 2", "higher secondary", "mpc", "bipc", "mec", "cec", "hec"]):
            return "Intermediate"
        if any(k in q for k in ["diploma", "polytechnic"]):
            return "Diploma"
        if any(k in q for k in ["b.tech", "btech", "b.e", "be", "engineering"]):
            return "B.Tech"
        if any(k in q for k in ["postgraduate", "m.tech", "mtech", "mba", "mca", "m.sc", "msc", "phd", "doctorate"]):
            return "Postgraduate"
        if any(k in q for k in ["degree", "b.sc", "bsc", "b.com", "bcom", "bba", "bca", "ba", "graduate"]):
            return "Degree"
        return "B.Tech"

    @staticmethod
    def normalize_stream(stream: str, qual: str) -> str:
        s = (stream or "").strip().upper()
        if not s:
            if qual == "10th": return "General"
            if qual == "Intermediate": return "MPC"
            if qual == "Diploma": return "CSE"
            if qual == "B.Tech": return "CSE"
            if qual == "Degree": return "B.Sc Computer Science"
            if qual == "Postgraduate": return "M.Tech (CSE)"
            return "General"
        return s

    @staticmethod
    def generate_qualification_aware_roadmap(profile: Dict[str, Any], query_text: str = "", language: str = "en") -> Dict[str, Any]:
        """
        Generates structured, stage-dependent roadmap.
        Stage rules strictly observed:
        10th != Intermediate != Diploma != Degree != B.Tech != Postgraduate
        """
        raw_qual = profile.get("qualification") or profile.get("education_level") or ""
        qual = AIEngine.normalize_qualification(raw_qual or query_text)
        stream = AIEngine.normalize_stream(profile.get("branch") or profile.get("stream_or_branch") or "", qual)
        status = profile.get("completion_status") or profile.get("status") or "Final Year"
        interests = profile.get("interests") or []
        if isinstance(interests, str):
            interests = [interests]
        pref = profile.get("preferred_career_direction") or profile.get("preference") or ""
        goal = profile.get("career_goal") or profile.get("goal") or ""
        lang = (language or "en").lower().strip()

        combined_context = f"{stream} {pref} {goal} {' '.join(interests)} {query_text}".lower()

        # =========================================================================
        # 0. DEFENCE / ARMED FORCES ROADMAP
        # =========================================================================
        is_defence = any(k in query_text.lower() for k in ["defence", "armed forces", "army", "navy", "air force", "nda", "cds", "afcat"]) or \
                     any(k in pref.lower() for k in ["defence", "armed forces"]) or \
                     any(k in goal.lower() for k in ["defence", "army", "navy", "air force", "nda", "cds", "afcat"])

        if is_defence and (not raw_qual or any(k in query_text.lower() for k in ["defence", "armed forces", "army", "navy", "air force", "nda", "cds", "afcat"])):
            if lang == "te":
                return {
                    "mode": "rule_based",
                    "title": "భారత సాయుధ దళాల కెరీర్ రోడ్‌మ్యాప్ (Defence Forces)",
                    "summary": "ఆర్మీ, నేవీ మరియు ఎయిర్‌ఫోర్స్‌లలో కమీషన్డ్ ఆఫీసర్ హోదాలు మరియు టెక్నికల్ ఎంట్రీల కోసం అధికారిక మార్గదర్శక ప్రణాళిక.",
                    "roadmap": {
                        "current_position": (qual.upper() if qual else "అభ్యర్థి") + " (Defence Aspirant)",
                        "suitable_options": [
                            "UPSC NDA & NA (12వ తరగతి తర్వాత: ఆర్మీ, నేవీ, ఎయిర్ ఫోర్స్ వింగ్స్)",
                            "10+2 టెక్నికల్ ఎంట్రీ స్కీమ్ (TES Army & Navy B.Tech Cadet - ఉచిత ఇంజనీరింగ్ డిగ్రీ)",
                            "UPSC CDS పరీక్ష (గ్రాడ్యుయేషన్ తర్వాత: IMA, INA, AFA, OTA)",
                            "AFCAT (ఎయిర్ ఫోర్స్ ఫ్లయింగ్ & గ్రౌండ్ డ్యూటీ బ్రాంచ్‌లు)",
                            "డైరెక్ట్ ఇంజనీరింగ్ SSB ఎంట్రీలు (Army TGC, SSC Tech, Navy Executive & Technical)",
                            "అగ్నివీర్ రిక్రూట్‌మెంట్ (జనరల్ డ్యూటీ, టెక్నికల్, ట్రేడ్స్‌మెన్)"
                        ],
                        "option_selected": "కమీషన్డ్ ఆఫీసర్ ఎంట్రీ (NDA / CDS / AFCAT / డైరెక్ట్ SSB)",
                        "eligibility": "భారతీయ పౌరసత్వం, నిర్దేశిత వయోపరిమితి (NDA: 16.5-19.5, CDS: 19-24), DGMS మెడికల్ ఫిట్‌నెస్.",
                        "what_to_study_skills": "గణితం, జనరల్ నాలెడ్జ్, ఆఫీసర్ లైక్ క్వాలిటీస్ (OLQ), శారీరక దృఢత్వం (2.4 కి.మీ రన్నింగ్).",
                        "entrance_exams": ["UPSC NDA", "UPSC CDS", "AFCAT", "JEE Main ర్యాంక్ ఆధారంగా డైరెక్ట్ SSB"],
                        "courses": ["3-4 సంవత్సరాల అకాడమీ క్యాడెట్ శిక్షణ (JNU B.Sc / B.Tech డిగ్రీ ప్రదానం)"],
                        "colleges": ["NDA ఖడక్‌వాస్లా", "IMA డెహ్రాడూన్", "INA ఎజిమల", "AFA దుండిగల్", "OTA చెన్నై"],
                        "skills": ["ఆఫీసర్ లైక్ క్వాలిటీస్ (OLQ)", "శారీరక సామర్థ్యం", "మానసిక స్థిరత్వం"],
                        "career": "లెఫ్టినెంట్ / సబ్ లెఫ్టినెంట్ / ఫ్లయింగ్ ఆఫీసర్‌గా కమిషన్",
                        "admission_process": "రాత పరీక్ష -> 5 రోజుల SSB ఇంటర్వ్యూ -> మెడికల్ బోర్డ్ పరీక్ష -> ఆల్ ఇండియా మెరిట్ జాబితా.",
                        "next_education_or_career_step": "NDA / IMA / INA / AFA లో సైనిక శిక్షణ పూర్తిచేయడం.",
                        "career_opportunities": "లెఫ్టినెంట్ / సబ్ లెఫ్టినెంట్ / ఫ్లయింగ్ ఆఫీసర్‌గా కమిషన్ (లెవల్ 10: బేసిక్ రూ. 56,100 + రూ. 15,500 MSP).",
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
                        "current_position": (qual.upper() if qual else "उम्मीदवार") + " (Defence Aspirant)",
                        "suitable_options": [
                            "UPSC NDA & NA (12वीं के बाद: थल सेना, नौसेना, वायु सेना)",
                            "10+2 तकनीकी प्रविष्टि योजना (TES Army & Navy B.Tech Cadet)",
                            "UPSC CDS परीक्षा (स्नातक के बाद: IMA, INA, AFA, OTA)",
                            "AFCAT (वायु सेना फ्लाइंग और ग्राउंड ड्यूटी शाखाएं)",
                            "डायरेक्ट इंजीनियरिंग SSB प्रविष्टियां (Army TGC, SSC Tech, Navy Executive)",
                            "अग्निवीर भर्ती (जनरल ड्यूटी, टेक्निकल, ट्रेड्समैन)"
                        ],
                        "option_selected": "कमीशन प्राप्त अधिकारी प्रविष्टि (NDA / CDS / AFCAT / डायरेक्ट SSB)",
                        "eligibility": "भारतीय नागरिक, आयु सीमा 16.5-19.5 (NDA) या 19-24 (CDS/AFCAT), DGMS चिकित्सा मानक।",
                        "what_to_study_skills": "गणित, सामान्य ज्ञान एवं समसामयिकी, ऑफिसर लाइक क्वालिटीज (OLQ), शारीरिक फिटनेस।",
                        "entrance_exams": ["UPSC NDA", "UPSC CDS", "AFCAT", "B.Tech / JEE रैंक आधारित डायरेक्ट SSB"],
                        "courses": ["3-4 वर्ष का सैन्य प्रशिक्षण (JNU B.Sc/B.Tech डिग्री प्रदान की जाती है)"],
                        "colleges": ["NDA खडकवासला", "IMA देहरादून", "INA एझिमाला", "AFA डुंडीगल", "OTA चेन्नई"],
                        "skills": ["ऑफिसर लाइक क्वालिटीज (OLQ)", "शारीरिक फिटनेस", "मानसिक स्थिरता"],
                        "career": "लेफ्टिनेंट / सब लेफ्टिनेंट / फ्लाइंग ऑफिसर",
                        "admission_process": "लिखित परीक्षा -> 5-दिवसीय एसएसबी (SSB) साक्षात्कार -> मेडिकल बोर्ड -> अखिल भारतीय मेरिट सूची।",
                        "next_education_or_career_step": "एनडीए खड़कवासला / आईएमए देहरादून / एएफए डुंडीगल में सैन्य प्रशिक्षण।",
                        "career_opportunities": "लेफ्टिनेंट / सब लेफ्टिनेंट / फ्लाइंग ऑफिसर (लेवल 10: मूल वेतन रु 56,100 + रु 15,500 MSP)।",
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
                    "title": "Indian Armed Forces Career Roadmap (Defence Forces)",
                    "summary": "Dedicated pathways for Commissioned Officer ranks and technical entries across the Army, Navy, and Air Force.",
                    "roadmap": {
                        "current_position": (qual.upper() if qual else "Aspirant") + " (Defence Aspirant)",
                        "suitable_options": [
                            "UPSC NDA & NA (After 12th: Army, Navy, Air Force Wings)",
                            "10+2 Technical Entry Scheme (TES Army & Navy B.Tech Cadet)",
                            "UPSC CDS Exam (After Graduation: IMA, INA, AFA, OTA)",
                            "AFCAT (Air Force Common Admission Test for Flying & Ground Duty)",
                            "Direct Engineering SSB entries (Army TGC, SSC Tech, Navy Executive & Technical)",
                            "Agniveer Recruitment (General Duty, Technical, Tradesmen)"
                        ],
                        "option_selected": "Commissioned Officer Entry (NDA / CDS / AFCAT / Direct SSB)",
                        "eligibility": "Indian Citizen, Age 16.5-19.5 (NDA) or 19-24 (CDS/AFCAT), Medical Fitness per DGMS standards.",
                        "what_to_study_skills": "Mathematics, General Knowledge & Current Affairs, Officer Like Qualities (OLQ), Physical Fitness (2.4 km running).",
                        "entrance_exams": ["UPSC NDA & NA", "UPSC CDS", "AFCAT", "Direct SSB based on B.Tech / JEE Rank"],
                        "courses": ["3-4 Years Academy Cadre Training (Grants JNU B.Sc/B.Tech degree)"],
                        "colleges": ["NDA Khadakwasla", "IMA Dehradun", "INA Ezhimala", "AFA Dundigal", "OTA Chennai"],
                        "skills": ["Officer Like Qualities (OLQ)", "Physical Stamina", "Current Affairs & Psychological Stability"],
                        "career": "Commissioned as Lieutenant / Sub Lieutenant / Flying Officer (7th CPC Level 10: Rs 56,100 basic + Rs 15,500 MSP)",
                        "admission_process": "Written Exam (UPSC) -> 5-Day SSB Interview -> Medical Board -> All India Merit List.",
                        "next_education_or_career_step": "Pre-Commissioning Training at NDA Khadakwasla / IMA Dehradun / AFA Dundigal / INA Ezhimala.",
                        "career_opportunities": "Commissioned Officer (Lieutenant / Sub Lieutenant / Flying Officer - Level 10: Rs 56,100 basic + Rs 15,500 MSP).",
                        "next_steps": [
                            "Review official height/medical guidelines on joinindianarmy.nic.in.",
                            "Check UPSC annual calendar for upcoming NDA/CDS notification dates.",
                            "Solve previous 5 years NDA / CDS papers in the CareerCompass Digital Library."
                        ]
                    },
                    "disclaimer": "CareerCompass verified guidance. Strict age and physical criteria apply per official gazette."
                }

        # =========================================================================
        # 1. AFTER 10TH ROADMAP (Focus on next-stage: Intermediate, Diploma, ITI)
        # =========================================================================
        if qual == "10th":
            is_medicine = any(k in combined_context for k in ["medicine", "doctor", "health", "mbbs", "bipc", "biology"])
            is_engg = any(k in combined_context for k in ["engineering", "engineer", "tech", "mpc", "math", "software"]) or not is_medicine

            if is_medicine:
                title_en = "Career Roadmap After Class 10th (Medical & Life Sciences Direction)"
                summary_en = "Structured navigation starting with 10+2 Intermediate BiPC for medical admissions (NEET UG for MBBS/BDS/BAMS), Pharmacy, Agriculture, and Allied Health Sciences."
                options_en = [
                    "Intermediate 10+2 (BiPC: Biology, Physics, Chemistry) - Primary gateway for NEET UG (MBBS/BDS/AYUSH)",
                    "4-Year B.Sc Agriculture & Horticulture / Veterinary Science after 10+2 BiPC",
                    "Bachelor of Pharmacy (B.Pharm - 4 Yrs) and Pharm.D (6 Yrs) after BiPC",
                    "Diploma in Allied Health Sciences / Paramedical (Medical Lab Tech, Radiology, Dialysis Tech - 2 to 3 Yrs)",
                    "B.Sc Nursing & Physiotherapy (BPT) after BiPC"
                ]
                sel_en = "Intermediate 10+2 (BiPC Stream)"
                elig_en = "Pass in Class 10th (SSC / CBSE / ICSE) with Science, Mathematics, and English."
                study_en = "NCERT Biology (Botany & Zoology), Organic & Inorganic Chemistry, Physics numerical fundamentals."
                exams_en = ["NEET UG (National Eligibility cum Entrance Test)", "State EAPCET (Agriculture & Pharmacy stream)", "ICAR AIEEA", "AIIMS Nursing"]
                adm_en = "Enroll in recognized Junior College for 10+2 BiPC -> Prepare NCERT syllabus thoroughly -> Register for NEET UG in Class 12."
                next_step_en = "Complete 10+2 BiPC -> Crack NEET UG / State CET -> Gain admission into MBBS, BDS, B.Pharm, or B.Sc Agriculture."
                career_en = "Medical Officer (MBBS), Dental Surgeon, Drug Regulatory Specialist, Agricultural Development Officer, Clinical Researcher."
                steps_en = [
                    "Enroll in a reputable Junior College for 10+2 Intermediate BiPC.",
                    "Focus 100% on mastering NCERT Class 11 and 12 Biology line-by-line.",
                    "Review official NEET examination guidelines at neet.nta.nic.in."
                ]
            else:
                title_en = "Career Roadmap After Class 10th (Engineering & Technical Direction)"
                summary_en = "Structured navigation offering choices between pre-university Intermediate MPC (JEE/EAPCET) or hands-on 3-Year Polytechnic Engineering Diplomas (with ECET lateral entry)."
                options_en = [
                    "Intermediate 10+2 (MPC: Maths, Physics, Chemistry) - Direct route to B.Tech, NDA Defence, Architecture, Pure Sciences",
                    "3-Year Polytechnic Diploma in Engineering (CSE, ECE, Mech, Civil) with direct 2nd-year B.Tech lateral entry via ECET",
                    "Intermediate MEC / CEC (Maths/Commerce, Economics, Civics) - Route for CA, CMA, CS, B.Com, BBA, Law",
                    "2-Year ITI Technical Trades (Electrician, Fitter, COPA) for immediate Railway & PSU technical recruitment",
                    "Indian Armed Forces Agniveer Recruitment (Army GD, Navy MR) after 10th"
                ]
                sel_en = "Intermediate 10+2 (MPC Stream) OR 3-Year Polytechnic Engineering Diploma"
                elig_en = "Class 10th Pass with minimum qualifying marks in Mathematics and General Science."
                study_en = "Advanced Mathematics (Trigonometry, Coordinate Geometry, Calculus), Physics (Mechanics, Electricity), Chemistry basics."
                exams_en = ["State POLYCET (for Polytechnic Diploma)", "APRJC / TSRJC (Residential Junior Colleges)", "State Board / CBSE 11th admissions"]
                adm_en = "Apply for State POLYCET for Government Polytechnic seats OR apply for Junior College 10+2 admissions based on 10th GPA."
                next_step_en = "If Intermediate: 10+2 MPC -> JEE Main / State EAPCET -> 4-Year B.Tech. If Diploma: 3-Year Polytechnic -> State ECET -> 2nd-year B.Tech."
                career_en = "Graduate Software/Core Engineer, Junior Engineer (Govt/PSU), Technical Specialist, Defence Technical Officer."
                steps_en = [
                    "Evaluate whether you prefer theoretical/competitive studies (Intermediate MPC) or hands-on practical engineering (Polytechnic Diploma).",
                    "Check state POLYCET dates on official polycet portals (e.g. polycetap.nic.in).",
                    "Secure Class 10 original pass certificates and school transfer certificate (TC)."
                ]

            if lang == "te":
                return {
                    "mode": "rule_based",
                    "title": "10వ తరగతి తర్వాత కెరీర్ రోడ్‌మ్యాప్ (" + ("వైద్య & లైఫ్ సైన్సెస్" if is_medicine else "ఇంజనీరింగ్ & సాంకేతిక విభాగం") + ")",
                    "summary": "10వ తరగతి పూర్తయిన తర్వాత ఇంటర్మీడియట్ (MPC/BiPC/CEC), 3 సంవత్సరాల పాలిటెక్నిక్ డిప్లొమా మరియు ITI మార్గాల దశలవారీ విశ్లేషణ.",
                    "roadmap": {
                        "current_position": "10వ తరగతి ఉత్తీర్ణత (Class 10th Passed)",
                        "suitable_options": [
                            "ఇంటర్మీడియట్ BiPC (MBBS, BDS, ఫార్మసీ, అగ్రికల్చర్, నర్సింగ్)" if is_medicine else "ఇంటర్మీడియట్ MPC (B.Tech, NDA, ఆర్కిటెక్చర్, ప్యూర్ సైన్సెస్)",
                            "3 సంవత్సరాల ఇంజనీరింగ్ పాలిటెక్నిక్ డిప్లొమా (ECET ద్వారా 2వ సంవత్సరం B.Tech)",
                            "ఇంటర్మీడియట్ MEC / CEC (CA, CS, B.Com, మేనేజ్‌మెంట్, లా)",
                            "ITI సాంకేతిక కోర్సులు (ఎలక్ట్రీషియన్, ఫిట్టర్ - రైల్వే/PSU ఉద్యోగాలకు)",
                            "డిఫెన్స్ అగ్నివీర్ ఎంట్రీలు (ఆర్మీ GD, నేవీ MR)"
                        ],
                        "option_selected": sel_en,
                        "eligibility": elig_en,
                        "what_to_study_skills": study_en,
                        "entrance_exams": exams_en,
                        "admission_process": adm_en,
                        "next_education_or_career_step": next_step_en,
                        "career_opportunities": career_en,
                        "next_steps": [
                            "మీ ఆసక్తిని విశ్లేషించుకోండి (గణితం vs బయాలజీ vs ప్రాక్టికల్ డిప్లొమా).",
                            "పాలిటెక్నిక్ ప్రవేశాల కోసం రాష్ట్ర POLYCET అధికారిక వెబ్‌సైట్ పరిశీలించండి.",
                            "10వ తరగతి మార్కుల జాబితా మరియు TC సిద్ధం చేసుకోండి."
                        ]
                    },
                    "disclaimer": "CareerCompass ధృవీకరించిన సమాచారం. ప్రవేశ గడువులు రాష్ట్ర విద్యా బోర్డుల పరిధిలో ఉంటాయి."
                }
            elif lang == "hi":
                return {
                    "mode": "rule_based",
                    "title": "10वीं कक्षा के बाद करियर रोडमैप (" + ("चिकित्सा व जीवन विज्ञान" if is_medicine else "इंजीनियरिंग व तकनीकी संकाय") + ")",
                    "summary": "कक्षा 10वीं के बाद इंटरमीडिएट (MPC/BiPC), 3 वर्षीय पॉलीटेक्निक डिप्लोमा व आईटीआई के लिए चरणबद्ध मार्गदर्शन।",
                    "roadmap": {
                        "current_position": "10वीं कक्षा उत्तीर्ण (Secondary School Examination)",
                        "suitable_options": [
                            "इंटरमीडिएट BiPC (MBBS, BDS, फार्मेसी, कृषि)" if is_medicine else "इंटरमीडिएट MPC (B.Tech, NDA, वास्तुकला, विज्ञान)",
                            "3-वर्षीय पॉलीटेक्निक इंजीनियरिंग डिप्लोमा (ECET द्वारा B.Tech में लेटरल एंट्री)",
                            "इंटरमीडिएट MEC / CEC (वाणिज्य, CA, B.Com, कानून)",
                            "आईटीआई तकनीकी ट्रेड्स (इलेक्ट्रीशियन, फिटर)",
                            "रक्षा सेवा अग्निवीर भर्ती (Army GD, Navy MR)"
                        ],
                        "option_selected": sel_en,
                        "eligibility": elig_en,
                        "what_to_study_skills": study_en,
                        "entrance_exams": exams_en,
                        "admission_process": adm_en,
                        "next_education_or_career_step": next_step_en,
                        "career_opportunities": career_en,
                        "next_steps": [
                            "अपनी रुचि तय करें (गणित vs जीव विज्ञान vs प्रायोगिक डिप्लोमा).",
                            "पॉलीटेक्निक प्रवेश के लिए राज्य POLYCET पोर्टल देखें।",
                            "कक्षा 10वीं के मूल प्रमाणपत्र तैयार रखें।"
                        ]
                    },
                    "disclaimer": "CareerCompass सत्यापित मार्गदर्शन। प्रवेश तिथियां संबंधित शिक्षा बोर्डों द्वारा तय की जाती हैं।"
                }
            else:
                return {
                    "mode": "rule_based",
                    "title": title_en,
                    "summary": summary_en,
                    "roadmap": {
                        "current_position": "Class 10th Passed / Secondary School",
                        "suitable_options": options_en,
                        "option_selected": sel_en,
                        "eligibility": elig_en,
                        "what_to_study_skills": study_en,
                        "entrance_exams": exams_en,
                        "admission_process": adm_en,
                        "next_education_or_career_step": next_step_en,
                        "career_opportunities": career_en,
                        "next_steps": steps_en
                    },
                    "disclaimer": "CareerCompass verified guidance. Admission dates per state secondary education boards."
                }

        # =========================================================================
        # 2. INTERMEDIATE / 12TH ROADMAP (Stream-aware: MPC vs BiPC vs CEC/MEC)
        # =========================================================================
        if qual == "Intermediate":
            is_bipc = "BIPC" in stream or any(k in combined_context for k in ["bipc", "biology", "neet", "mbbs", "medicine", "pharmacy"])
            is_commerce = any(k in stream for k in ["CEC", "MEC", "COMMERCE"]) or any(k in combined_context for k in ["ca ", "cma", "b.com", "bba", "commerce", "law"])

            if is_bipc:
                title_en = "Career Roadmap for Intermediate BiPC (Biology, Physics, Chemistry)"
                summary_en = "Dedicated medical and allied healthcare progression: NEET UG for MBBS/BDS/AYUSH, Pharmacy (B.Pharm/Pharm.D), Agriculture, Nursing, and Biotech degrees."
                options_en = [
                    "MBBS / BDS / AYUSH (BAMS, BHMS) via National Eligibility cum Entrance Test (NEET UG)",
                    "Bachelor of Pharmacy (B.Pharm - 4 Yrs) and Doctor of Pharmacy (Pharm.D - 6 Yrs)",
                    "4-Year B.Sc (Hons) Agriculture / Horticulture / Forestry via ICAR AIEEA & State EAPCET",
                    "4-Year B.Sc Nursing and Bachelor of Physiotherapy (BPT)",
                    "3-Year B.Sc in Biotechnology, Microbiology, Genetics, or Biochemistry",
                    "Bachelor of Veterinary Science & Animal Husbandry (B.V.Sc & AH)"
                ]
                sel_en = "Medicine (MBBS/BDS) / Pharmacy / Agricultural Sciences"
                elig_en = "10+2 with Physics, Chemistry, Biology/Biotechnology with min 50% aggregate (40% for SC/ST/OBC)."
                study_en = "NCERT Biology line-by-line, Organic Chemistry reaction mechanisms, Physical Chemistry numericals, Physics conceptual problem-solving."
                exams_en = ["NEET UG", "State EAPCET (Agri & Medical)", "ICAR AIEEA", "AIIMS B.Sc Nursing Entrance"]
                adm_en = "Score competitive percentile in NEET UG -> Register for MCC All India Quota Counselling (15%) and State Quota Counselling (85%)."
                next_step_en = "5.5 Years MBBS Degree (including 1-yr rotational internship) -> NEXT / NEET PG for Specialist MD/MS qualification."
                career_en = "Registered Medical Practitioner, Specialist Surgeon, Drug Safety Associate, Agricultural Development Officer, Clinical Research Scientist."
                steps_en = [
                    "Complete 100% revision of Class 11 and 12 NCERT Biology textbooks.",
                    "Solve past 10 years NEET UG chapter-wise questions under timed conditions.",
                    "Monitor official National Testing Agency portal at neet.nta.nic.in for admit cards and application deadlines."
                ]
            elif is_commerce:
                title_en = "Career Roadmap for Intermediate CEC / MEC (Commerce & Economics)"
                summary_en = "Pathways for finance, business, accounting, and legal careers: CA Foundation, CMA, CS, B.Com (Hons), BBA, and 5-Year Integrated Law (CLAT)."
                options_en = [
                    "Chartered Accountancy (CA Foundation via ICAI)",
                    "Company Secretary (CSEET via ICSI) / Cost & Management Accountant (CMA via ICMAI)",
                    "5-Year Integrated BA LLB / BBA LLB via Common Law Admission Test (CLAT)",
                    "B.Com (Hons) / B.Com in Banking, Taxation, or Computer Applications",
                    "Bachelor of Business Administration (BBA / BMS) via IPMAT / CUET UG",
                    "Central & State Government Administrative exams (SSC CHSL, Banking, State PSC)"
                ]
                sel_en = "Chartered Accountancy (CA) / Corporate Law (CLAT) / B.Com / BBA"
                elig_en = "10+2 Intermediate with Commerce, Economics, Accountancy, or Mathematics."
                study_en = "Principles of Accounting, Business Laws, Economics, Quantitative Aptitude & Logical Reasoning."
                exams_en = ["CA Foundation (ICAI)", "CLAT (Common Law Admission Test)", "CUET UG", "IPMAT (IIM Indore/Rohtak)", "CSEET"]
                adm_en = "Register with ICAI for CA Foundation OR appear for CLAT/CUET for National Law Universities and Central Universities."
                next_step_en = "Pass CA Foundation -> CA Intermediate -> 3 Years Articleship -> CA Final OR 5-Year LLB -> Bar Council Enrollment."
                career_en = "Chartered Accountant (CA), Corporate Lawyer, Investment Banker, Financial Analyst, Civil Servant."
                steps_en = [
                    "Register for CA Foundation on official icai.org portal if pursuing accounting excellence.",
                    "Prepare Legal Reasoning and Current Affairs for CLAT on consortiumofnlus.ac.in.",
                    "Apply for Central University admissions via cuetug.nta.nic.in."
                ]
            else:
                # MPC Stream
                title_en = "Career Roadmap for Intermediate MPC (Maths, Physics, Chemistry)"
                summary_en = "Comprehensive technical and defence progression: 4-Year B.Tech via JEE/CET, UPSC NDA & NA Officer Commission, Architecture, and Pure Sciences."
                options_en = [
                    "4-Year B.Tech / B.E. (CSE, ECE, EEE, Mechanical, Civil, AI/ML, Data Science) via JEE Main & State CETs",
                    "National Defence Academy (UPSC NDA & NA - Army, Navy, Air Force Cadet)",
                    "10+2 Technical Entry Scheme (TES Army & Navy B.Tech Cadet - Direct SSB via JEE Main rank)",
                    "5-Year Bachelor of Architecture (B.Arch via JEE Main Paper 2 / NATA)",
                    "5-Year Integrated BS-MS at Premier Institutes (IISc Bangalore, IISERs, NISER)",
                    "Commercial Pilot License (DGCA CPL) / Aviation Ground School"
                ]
                sel_en = "4-Year B.Tech Engineering Degree / UPSC NDA Defence Cadet"
                elig_en = "10+2 with Physics, Mathematics, and Chemistry with min 50-75% aggregate per institution."
                study_en = "Calculus, Vectors, Coordinate Geometry, Mechanics, Electrodynamics, Physical/Organic Chemistry, Analytical Speed."
                exams_en = ["JEE Main", "JEE Advanced", "State EAPCET / CET", "UPSC NDA & NA", "BITSAT", "NATA"]
                adm_en = "Appear for JEE Main & State CETs -> JoSAA / CSAB Central Counselling or State CET Web Options for seat allotment."
                next_step_en = "Complete 4-Year B.Tech -> Campus Placements in Software/Core Industry OR GATE for Top IITs/PSUs."
                career_en = "Software Development Engineer, Core Systems Engineer, Defence Commissioned Officer (Lieutenant), Scientific Officer."
                steps_en = [
                    "Practice 15 full-length JEE Main mock tests in timed CBT mode.",
                    "Track official JoSAA counselling portal at josaa.nic.in.",
                    "If interested in Armed Forces, verify physical eligibility and height standards on joinindianarmy.nic.in."
                ]

            if lang == "te":
                return {
                    "mode": "rule_based",
                    "title": "ఇంటర్మీడియట్ " + stream + " విద్యార్థుల కెరీర్ రోడ్‌మ్యాప్",
                    "summary": "ఇంటర్మీడియట్ " + stream + " ఉత్తీర్ణులైన విద్యార్థులకు ఉన్నత విద్యా కోర్సులు, ప్రవేశ పరీక్షలు మరియు ఉద్యోగ అవకాశాల సమగ్ర ప్రణాళిక.",
                    "roadmap": {
                        "current_position": "ఇంటర్మీడియట్ 10+2 (" + stream + " స్ట్రీమ్)",
                        "suitable_options": options_en,
                        "option_selected": sel_en,
                        "eligibility": elig_en,
                        "what_to_study_skills": study_en,
                        "entrance_exams": exams_en,
                        "admission_process": adm_en,
                        "next_education_or_career_step": next_step_en,
                        "career_opportunities": career_en,
                        "next_steps": steps_en
                    },
                    "disclaimer": "CareerCompass ధృవీకరించిన సమాచారం. జాతీయ మరియు రాష్ట్ర ప్రవేశ పరీక్షల నిబంధనల ప్రకారం ప్రవేశాలు ఉంటాయి."
                }
            elif lang == "hi":
                return {
                    "mode": "rule_based",
                    "title": "इंटरमीडिएट " + stream + " छात्रों के लिए करियर रोडमैप",
                    "summary": "10+2 " + stream + " संकाय के छात्रों के लिए उच्च शिक्षा, राष्ट्रीय प्रवेश परीक्षाओं और करियर संभावनाओं का विस्तृत रोडमैप।",
                    "roadmap": {
                        "current_position": "इंटरमीडिएट 10+2 (" + stream + " संकाय)",
                        "suitable_options": options_en,
                        "option_selected": sel_en,
                        "eligibility": elig_en,
                        "what_to_study_skills": study_en,
                        "entrance_exams": exams_en,
                        "admission_process": adm_en,
                        "next_education_or_career_step": next_step_en,
                        "career_opportunities": career_en,
                        "next_steps": steps_en
                    },
                    "disclaimer": "CareerCompass सत्यापित मार्गदर्शन। प्रवेश परीक्षा नियम संबंधित राष्ट्रीय व राज्य एजेंसियों के अनुसार।"
                }
            else:
                return {
                    "mode": "rule_based",
                    "title": title_en,
                    "summary": summary_en,
                    "roadmap": {
                        "current_position": "Intermediate 10+2 (" + stream + " Stream)",
                        "suitable_options": options_en,
                        "option_selected": sel_en,
                        "eligibility": elig_en,
                        "what_to_study_skills": study_en,
                        "entrance_exams": exams_en,
                        "admission_process": adm_en,
                        "next_education_or_career_step": next_step_en,
                        "career_opportunities": career_en,
                        "next_steps": steps_en
                    },
                    "disclaimer": "CareerCompass verified guidance. Admissions per NTA, State CETs, and university guidelines."
                }

        # =========================================================================
        # 3. DIPLOMA ROADMAP (Branch-aware: CSE vs Mechanical vs Civil vs ECE)
        # =========================================================================
        if qual == "Diploma":
            is_mech = any(k in stream for k in ["MECH", "AUTOMOBILE", "PRODUCTION"]) or "mechanical" in combined_context
            is_civil = "CIVIL" in stream or "civil" in combined_context
            is_cse = any(k in stream for k in ["CSE", "COMPUTER", "IT"]) or any(k in combined_context for k in ["software", "cse", "web", "coding"]) or (not is_mech and not is_civil)

            if is_mech:
                title_en = "Career Roadmap for Diploma in Mechanical Engineering"
                summary_en = "Pathways designed specifically for Mechanical Diploma holders: Lateral Entry to B.Tech 2nd year via ECET, Central Government Junior Engineer (RRB JE, SSC JE), and core manufacturing industries."
                options_en = [
                    "B.Tech Mechanical Lateral Entry: Direct admission into 2nd year (3rd semester) B.Tech via State ECET / JELET / LEET (save 1 full year)",
                    "Central Government Junior Engineer Posts: RRB JE (Mechanical), SSC JE (CPWD, MES, Border Roads), DRDO CEPTAM, ISRO Technical Assistant",
                    "Core Automotive & Heavy Manufacturing: Junior Engineer Trainee (JET) at Tata Motors, L&T, BHEL, Mahindra, NTPC, Siemens",
                    "National Apprenticeship Training Scheme (NATS) with monthly government-stipend in public sector undertakings",
                    "Defence Technical Trades: Indian Air Force Group X (Mechanical), Indian Navy Sailor Artificer, Army Technical Entry"
                ]
                sel_en = "B.Tech Mechanical Lateral Entry via ECET OR Central Govt Junior Engineer (SSC / RRB JE)"
                elig_en = "3-Year Diploma in Mechanical Engineering from AICTE-recognized State Technical Board (min 50% marks)."
                study_en = "Thermodynamics, Fluid Mechanics, Strength of Materials, Manufacturing Processes, AutoCAD / SolidWorks, Engineering Mathematics for ECET."
                exams_en = ["State ECET (Lateral Entry B.Tech)", "SSC JE (Junior Engineer)", "RRB JE (Railway Recruitment Board)", "DRDO CEPTAM"]
                adm_en = "For B.Tech: Appear for State ECET -> Web Counselling -> Direct admission to 2nd year B.Tech; For Govt JE: Appear for SSC/RRB CBT exams."
                next_step_en = "Complete 3-Year Lateral Entry B.Tech -> Core Engineering Graduate OR Commission as Junior Engineer in CPWD / Indian Railways."
                career_en = "Plant Operations Supervisor, Design Engineer (CAD/CAM), Assistant Executive Engineer (State Govt), Railway Junior Engineer (Pay Level 6)."
                steps_en = [
                    "Master Engineering Mechanics, Thermal Engineering, and Mathematics from State Technical Board syllabus.",
                    "Practice previous 5 years SSC JE Mechanical papers available in CareerCompass Digital Library.",
                    "Register on official National Apprenticeship portal at nats.education.gov.in."
                ]
            elif is_civil:
                title_en = "Career Roadmap for Diploma in Civil Engineering"
                summary_en = "Pathways for Civil Diploma holders: Lateral Entry B.Tech Civil, State & Central Junior Engineer roles (SSC JE, RRB JE, State Irrigation/R&B), and infrastructure construction firms."
                options_en = [
                    "B.Tech Civil Engineering Lateral Entry: Direct admission to 2nd year B.Tech via State ECET / JELET",
                    "Central Government Junior Engineer: SSC JE (CPWD, Military Engineer Services, Central Water Commission), RRB JE (Civil)",
                    "State Govt Public Works: Assistant Engineer / Overseer in State PWD, Irrigation, Municipal Corporations",
                    "Infrastructure & Real Estate Companies: Site Supervisor / Quality Control Engineer (L&T Construction, Afcons, Shapoorji Pallonji)",
                    "NATS Apprenticeship & Government Contractor Licensing"
                ]
                sel_en = "B.Tech Civil Lateral Entry via ECET OR SSC JE / State PWD Overseer"
                elig_en = "3-Year Diploma in Civil Engineering (min 50% aggregate)."
                study_en = "Surveying, Strength of Materials, Concrete Technology, Hydraulics, Estimating & Costing, AutoCAD Civil, Structural Engineering basics."
                exams_en = ["State ECET", "SSC JE (Civil)", "RRB JE (Civil)", "State PSC Junior Technical Officer"]
                adm_en = "Appear for State ECET for university engineering seats OR apply for SSC JE computer-based recruitment test."
                next_step_en = "2nd Year B.Tech Civil -> Core Infrastructure Consultant OR Junior Engineer in Central/State Government."
                career_en = "Site Engineer, Junior Engineer (Govt Pay Level 6), Structural Draughtsman, Estimation & Billing Specialist."
                steps_en = [
                    "Prepare for State ECET Civil Engineering questions and Mathematics.",
                    "Learn AutoCAD 2D/3D and MS Excel for construction estimation.",
                    "Track official SSC JE annual notification calendar on ssc.gov.in."
                ]
            else:
                # CSE / IT Diploma
                title_en = "Career Roadmap for Diploma in Computer Science & Engineering"
                summary_en = "Specialized pathways for Diploma CSE holders: Direct Lateral Entry into 2nd year B.Tech CSE via ECET, Junior Software Roles in IT firms, and Government Technical Assistant positions."
                options_en = [
                    "B.Tech CSE Lateral Entry: Direct admission into 2nd year (3rd semester) B.Tech via State ECET / JELET / LEET (save 1 full year)",
                    "Junior Software Developer / Web Developer in IT companies, Software Services, and Startups",
                    "Central & State Government Technical Jobs: RRB Junior Engineer (IT), DRDO CEPTAM (Computer Science), ISRO Technical Assistant, NIC Assistant",
                    "National Apprenticeship Training Scheme (NATS) with stipend in IT & Telecom public enterprises",
                    "Industry Certifications: AWS Certified Cloud Practitioner, Red Hat Linux (RHCSA), Cisco Certified Network Associate (CCNA)"
                ]
                sel_en = "Lateral Entry to B.Tech CSE via ECET OR Junior Software Developer / RRB JE"
                elig_en = "3-Year Diploma in Computer Engineering / IT from recognized State Technical Board (min 45-50% marks)."
                study_en = "Data Structures, Database Management Systems (SQL), Computer Networks, Operating Systems, C/Java/Python, Engineering Mathematics."
                exams_en = ["State ECET (Lateral Entry)", "RRB JE (IT)", "DRDO CEPTAM", "ISRO Technical Assistant (CS)"]
                adm_en = "Register for State ECET -> Secure State Engineering Rank -> Web counselling for 2nd year B.Tech seat in autonomous/university colleges."
                next_step_en = "Join 2nd Year B.Tech CSE -> Complete 3 Years of Degree -> Campus Placements in Top Tech Companies OR GATE CSE."
                career_en = "Software Developer, Full Stack Engineer, Junior Engineer (IT) in Railways, Cloud Infrastructure Technician."
                steps_en = [
                    "Download official State ECET syllabus for Computer Science and Engineering Mathematics.",
                    "Build 2 live portfolio projects in Python / JavaScript and deploy them on GitHub.",
                    "Register on nats.education.gov.in for verified industrial apprentice programs."
                ]

            if lang == "te":
                return {
                    "mode": "rule_based",
                    "title": "పాలిటెక్నిక్ డిప్లొమా (" + stream + ") విద్యార్థుల కెరీర్ రోడ్‌మ్యాప్",
                    "summary": stream + " డిప్లొమా పూర్తి చేసిన విద్యార్థులకు ECET ద్వారా 2వ సంవత్సరం B.Tech ప్రవేశం, ప్రభుత్వ JE ఉద్యోగాలు మరియు కోర్ పరిశ్రమల ప్రణాళిక.",
                    "roadmap": {
                        "current_position": "ఇంజనీరింగ్ డిప్లొమా (" + stream + " బ్రాంచ్)",
                        "suitable_options": options_en,
                        "option_selected": sel_en,
                        "eligibility": elig_en,
                        "what_to_study_skills": study_en,
                        "entrance_exams": exams_en,
                        "admission_process": adm_en,
                        "next_education_or_career_step": next_step_en,
                        "career_opportunities": career_en,
                        "next_steps": steps_en
                    },
                    "disclaimer": "CareerCompass ధృవీకరించిన సమాచారం. AICTE మరియు రాష్ట్ర సాంకేతిక విద్యా మండలి నిబంధనల ప్రకారం ప్రవేశాలు ఉంటాయి."
                }
            elif lang == "hi":
                return {
                    "mode": "rule_based",
                    "title": "पॉलीटेक्निक डिप्लोमा (" + stream + ") छात्रों के लिए करियर रोडमैप",
                    "summary": stream + " डिप्लोमा धारकों के लिए ECET द्वारा सीधे B.Tech 2nd वर्ष में प्रवेश, जूनियर इंजीनियर (JE) और उद्योग करियर का रोडमैप।",
                    "roadmap": {
                        "current_position": "डिप्लोमा इन इंजीनियरिंग (" + stream + " शाखा)",
                        "suitable_options": options_en,
                        "option_selected": sel_en,
                        "eligibility": elig_en,
                        "what_to_study_skills": study_en,
                        "entrance_exams": exams_en,
                        "admission_process": adm_en,
                        "next_education_or_career_step": next_step_en,
                        "career_opportunities": career_en,
                        "next_steps": steps_en
                    },
                    "disclaimer": "CareerCompass सत्यापित मार्गदर्शन। लेटरल एंट्री नियम AICTE एवं राज्य तकनीकी बोर्डों के अनुसार।"
                }
            else:
                return {
                    "mode": "rule_based",
                    "title": title_en,
                    "summary": summary_en,
                    "roadmap": {
                        "current_position": "Diploma in " + stream + " (3-Year Polytechnic)",
                        "suitable_options": options_en,
                        "option_selected": sel_en,
                        "eligibility": elig_en,
                        "what_to_study_skills": study_en,
                        "entrance_exams": exams_en,
                        "admission_process": adm_en,
                        "next_education_or_career_step": next_step_en,
                        "career_opportunities": career_en,
                        "next_steps": steps_en
                    },
                    "disclaimer": "CareerCompass verified guidance. Lateral entry as per State Technical Education Board policies."
                }

        # =========================================================================
        # 4. DEGREE ROADMAP (Non-engineering: B.Sc, B.Com, BA, BCA, BBA)
        # =========================================================================
        if qual == "Degree":
            title_en = f"Career Roadmap for Degree Graduates ({stream})"
            summary_en = "Step-by-step pathways across Master's degrees (M.Sc/MCA/MBA), Central & State Government examinations (UPSC, SSC CGL, Banking), and corporate career roles."
            options_en = [
                "Master's Degree in Core Discipline (M.Sc, MA, M.Com, MCA via CUET PG / State PGCET)",
                "Master of Business Administration (MBA via CAT, XAT, MAT, State ICET) for corporate leadership",
                "Central Government Administrative Services: UPSC Civil Services (IAS/IPS/IFS), SSC CGL (Group B/C Gazetted & Non-Gazetted)",
                "Banking & Financial Services: IBPS PO / Clerk, SBI PO / Clerk, RBI Grade B Officer",
                "Information Technology & Corporate Careers: Data Analyst, Business Analyst, Software Associate (especially for BCA / B.Sc CS)",
                "Defence Services Officer Commission: UPSC Combined Defence Services (CDS Exam) for IMA, INA, AFA, OTA",
                "State Civil Services: State Public Service Commission Group-1 and Group-2 Executive Officers"
            ]
            sel_en = "MBA via CAT OR Central Govt Recruitment (SSC CGL / Banking) OR Master's (MCA/M.Sc)"
            elig_en = "Recognized 3-Year Bachelor's Degree (B.Sc, B.Com, BA, BCA, BBA) with min 50% marks."
            study_en = "Quantitative Aptitude, Logical Reasoning, General Awareness, English Verbal Ability, and Core Subject Specialization."
            exams_en = ["UPSC CSE / CDS", "SSC CGL", "IBPS PO / SBI PO", "CAT / State ICET / CUET PG"]
            adm_en = "Appear for target entrance exam -> Clear CBT / Mains / Interview rounds -> Secure university seat or central appointment."
            next_step_en = "Postgraduate Degree / Direct Probationary Officer Appointment -> Growth to Functional Manager or Senior Administrative Officer."
            career_en = "Probationary Banking Officer, Corporate Manager, Administrative Officer (UPSC/SSC), Data Analyst."
            steps_en = [
                "Choose between Corporate Placement (MBA / IT Certifications) vs Government Service (SSC CGL / Banking).",
                "Practice daily quantitative aptitude and current affairs from verified standards.",
                "Review notification dates on ssc.gov.in and ibps.in."
            ]

            return {
                "mode": "rule_based",
                "title": title_en,
                "summary": summary_en,
                "roadmap": {
                    "current_position": f"Bachelor's Degree ({stream})",
                    "suitable_options": options_en,
                    "option_selected": sel_en,
                    "eligibility": elig_en,
                    "what_to_study_skills": study_en,
                    "entrance_exams": exams_en,
                    "admission_process": adm_en,
                    "next_education_or_career_step": next_step_en,
                    "career_opportunities": career_en,
                    "next_steps": steps_en
                },
                "disclaimer": "CareerCompass verified guidance. Eligibility criteria as per respective recruiting bodies."
            }

        # =========================================================================
        # 5. POSTGRADUATE ROADMAP (M.Tech, MBA, M.Sc, MCA)
        # =========================================================================
        if qual == "Postgraduate":
            title_en = f"Career Roadmap for Postgraduate Degree Holders ({stream})"
            summary_en = "Advanced career acceleration for Postgraduates: Ph.D. & Doctoral Research (PMRF / CSIR JRF), University Teaching (UGC NET), Scientific & R&D positions, and High-Tech Corporate Leadership."
            options_en = [
                "Doctoral Research (Ph.D.): Prime Minister's Research Fellowship (PMRF - Rs 70,000-80,000/mo stipend) or IIT/CSIR Ph.D.",
                "University Teaching & Academia: Assistant Professor at State and Central Universities via UGC NET / CSIR NET / State SET",
                "Government Scientific & R&D Organizations: ISRO Scientist-SC, DRDO Scientist-B, BARC Scientific Officer, NIELIT Scientist",
                "Corporate High-Tech & Strategic Leadership: Principal Engineer, Lead Data Scientist, Senior Product Manager, VP of Engineering",
                "Specialized Technical Consulting & Patent Examination (Office of Controller General of Patents)"
            ]
            sel_en = "Ph.D. Doctoral Fellowship (PMRF / IIT) OR UGC NET Assistant Professorship OR Senior Corporate R&D Lead"
            elig_en = "Master's Degree (M.Tech, M.Sc, MBA, MCA, MA) with min 55% aggregate (50% for reserved categories)."
            study_en = "Advanced Research Methodology, Domain Specialization, High-Impact Journal Paper Writing (IEEE/Springer), UGC NET Paper 1 & 2."
            exams_en = ["UGC NET / CSIR NET (for JRF & Assistant Professorship)", "GATE (for Ph.D. admissions & PMRF nomination)", "BARC OCES/DGFS", "ISRO Scientist Centralised Recruitment"]
            adm_en = "Qualify UGC/CSIR NET with Junior Research Fellowship (JRF) -> Interview at premier research lab OR University Selection Board."
            next_step_en = "Ph.D. Completion / Assistant Professorship (Academic Level 10: Rs 57,700 - 1,82,400) -> Associate Professor / Principal Scientist."
            career_en = "University Professor, Chief Scientist, Senior Director of R&D, Government Technical Advisor."
            steps_en = [
                "Review upcoming UGC NET / CSIR NET dates on official NTA portal at ugcnet.nta.nic.in.",
                "Draft your Ph.D. research proposal focusing on high-impact domain problems.",
                "Review PMRF direct entry and lateral entry guidelines on official pmrf.in portal."
            ]

            return {
                "mode": "rule_based",
                "title": title_en,
                "summary": summary_en,
                "roadmap": {
                    "current_position": f"Postgraduate Degree Holder ({stream})",
                    "suitable_options": options_en,
                    "option_selected": sel_en,
                    "eligibility": elig_en,
                    "what_to_study_skills": study_en,
                    "entrance_exams": exams_en,
                    "admission_process": adm_en,
                    "next_education_or_career_step": next_step_en,
                    "career_opportunities": career_en,
                    "next_steps": steps_en
                },
                "disclaimer": "CareerCompass verified guidance. Academic qualifications governed by UGC / AICTE regulations."
            }

        # =========================================================================
        # 6. B.TECH / B.E. ROADMAP (Branch & Status Aware: CSE vs Cyber vs Mech vs Civil)
        # =========================================================================
        is_cyber = any(k in stream for k in ["CYBER", "SECURITY", "INFO SEC"]) or "cyber" in combined_context
        is_mech = any(k in stream for k in ["MECHANICAL", "AUTOMOBILE", "PRODUCTION", "MECH"]) or "mechanical" in combined_context
        is_civil = "CIVIL" in stream or "civil" in combined_context
        is_ece = any(k in stream for k in ["ECE", "EEE", "ELECTRONIC", "ELECTRICAL"])
        is_cse = (not is_cyber and not is_mech and not is_civil and not is_ece) or "cse" in stream or "computer" in stream

        stage_label = f"B.Tech in {stream} ({status})"

        if is_cyber:
            title_en = f"Career Roadmap for B.Tech Cyber Security ({status})"
            summary_en = "Specialized cybersecurity progression: SOC Analyst & Security Engineering in enterprise and product companies, CERT-In / DRDO cyber defense, and advanced security certifications."
            options_en = [
                "Specialized Enterprise Security Roles: Security Operations Center (SOC) Analyst, Security Engineer, Vulnerability Assessor & Pen-Tester",
                "Government Cyber Defense & Intelligence: CERT-In (Computer Emergency Response Team), NTRO, DRDO Cyber Command, IB ACIO (Cyber)",
                "Industry Certifications: CompTIA Security+, Certified Ethical Hacker (CEH), OSCP (Offensive Security), CISSP Associate",
                "GATE (CS / Data Science & AI): M.Tech in Information Security / Cyber Systems at IIT Bombay, IIT Madras, IIIT Delhi",
                "Higher Studies Abroad: MS in Cybersecurity / Digital Forensics in USA, UK, Germany",
                "Armed Forces Cyber Operations: Technical entries for Army/Navy/Air Force Cyber Cells"
            ]
            sel_en = "Security Engineer / SOC Analyst / CERT-In Specialist / M.Tech Cyber Security"
            elig_en = "B.Tech in Cyber Security, CSE, or Allied IT with solid foundations in networking, Linux, and security architecture."
            study_en = "Network Security (TCP/IP, Firewalls, Wireshark), Linux Administration, Python/Bash scripting, SIEM tools (Splunk), OWASP Top 10, Cryptography."
            exams_en = ["GATE CS / DA", "CERT-In Scientist Recruitment", "NIELIT Scientist-B", "DRDO CEPTAM"]
            adm_en = "Build practical security portfolio (TryHackMe / HackTheBox badges) -> Technical assessments & coding -> Security technical interview."
            next_step_en = "Junior SOC Analyst / Security Engineer -> Senior Penetration Tester -> Chief Information Security Officer (CISO)."
            career_en = "Cybersecurity Analyst (Rs 6 - 25 LPA), Ethical Hacker, Government Cyber Defense Officer, Security Architect."
            steps_en = [
                "Complete hands-on security labs on TryHackMe (Pre-Security and SOC Level 1 paths).",
                "Earn an entry-level recognized credential such as CompTIA Security+ or CEH.",
                "Review open technical vacancies on official cert-in.org.in and nielit.gov.in portals."
            ]
        elif is_mech:
            title_en = f"Career Roadmap for B.Tech Mechanical Engineering ({status})"
            summary_en = "Core engineering and PSU pathways: GATE for Maharatna PSUs (ONGC, IOCL, NTPC, BHEL) and IIT M.Tech, UPSC Engineering Services (ESE), Automotive R&D, and Defence Technical entries."
            options_en = [
                "PSU Recruitment via GATE ME: Maharatna & Navratna PSUs (ONGC, IOCL, NTPC, BHEL, SAIL, GAIL, HPCL - CTC Rs 14-22 LPA)",
                "UPSC Engineering Services Examination (ESE / IES) for Class-1 Gazetted Central Engineering Officers",
                "Core Automotive & Heavy Machinery Industry: Design & R&D Engineer at Tata Motors, Mahindra, L&T, Hyundai, Thermax, Godrej",
                "Defence Technical Officer Commission: Army TGC, SSC Tech, Navy SSC (Direct 5-Day SSB based on B.Tech marks)",
                "Higher Studies (M.Tech via GATE with Rs 12,400/mo stipend at IITs or MS in Germany/US in Automotive/Robotics)",
                "Techno-Commercial & Management Leadership: MBA via CAT for Supply Chain & Operations Leadership"
            ]
            sel_en = "PSU Executive Trainee via GATE / UPSC ESE / Core Automotive Engineer / Defence Technical Officer"
            elig_en = "B.Tech in Mechanical Engineering (min 60% or 6.5 CGPA, no active backlogs)."
            study_en = "Thermodynamics, Heat Transfer, Fluid Mechanics, Strength of Materials, Theory of Machines, CAD/CAE tools (SolidWorks, ANSYS, CATIA), Aptitude & Mathematics."
            exams_en = ["GATE ME", "UPSC ESE (Engineering Services)", "State PSC Assistant Executive Engineer", "CAT"]
            adm_en = "Register for GATE at official IIT portal -> Score high percentile -> Apply to individual PSUs or participate in COAP for IIT M.Tech."
            next_step_en = "Executive Trainee in Maharatna PSU / Class-1 Gazetted Central Officer -> Chief Plant Engineer / General Manager."
            career_en = "PSU Executive Trainee (Class-A officer), Central Gazetted Officer (IES), Design & Simulation Engineer, Defence Officer."
            steps_en = [
                "Practice 25 years of GATE ME previous papers with intensive focus on Thermal and Design streams.",
                "Check TGC and SSC Tech cut-off marks on official joinindianarmy.nic.in.",
                "Master FEA simulation using ANSYS or Altair for core industrial R&D hiring."
            ]
        else:
            # CSE / General Engineering
            title_en = f"Career Roadmap for B.Tech {stream} Engineers ({status})"
            summary_en = "Comprehensive tech and post-B.Tech pathways: Software Engineering across Product & IT MNCs, GATE for IIT Master's & PSUs (ISRO, DRDO, BARC), Higher Studies abroad (MS), or Management (MBA)."
            options_en = [
                "Software & High-Growth Tech Careers: SDE (Software Development Engineer), Full Stack Developer, DevOps & Cloud, AI/ML, Data Engineer",
                "Product-Based Companies (Google, Microsoft, Amazon, Atlassian) vs IT Services & Consulting (TCS, Infosys, Wipro, Accenture)",
                "GATE Examination: M.Tech at Top IITs (with Rs 12,400/mo stipend) OR Direct PSU Recruitment (ISRO, DRDO, BARC, IOCL, NIC)",
                "Higher Studies Abroad (MS in Computer Science via GRE/TOEFL) or Management Leadership (MBA via CAT)",
                "Defence Technical Officer (Army TGC, SSC Tech, Navy SSC - Direct 5-Day SSB based on engineering marks)"
            ]
            sel_en = "Software Engineering / GATE CS M.Tech & PSU / Technical Officer"
            elig_en = f"B.Tech in {stream} with minimum 60% aggregate or 6.5 CGPA."
            study_en = "Data Structures & Algorithms (LeetCode), System Design (HLD/LLD), OS, DBMS, Networks, Docker/Kubernetes, Spring Boot / React / Node.js."
            exams_en = ["GATE CS", "CAT (for MBA)", "GRE & TOEFL / IELTS (for MS)", "UPSC CDS"]
            adm_en = "Online coding rounds -> Technical screening -> System design & problem-solving rounds -> Managerial / HR interview."
            next_step_en = "SDE-1 / M.Tech Graduate / Scientist-B -> SDE-2, Technical Lead, Engineering Manager."
            career_en = "Software Development Engineer (CTC Rs 8 - 45 LPA), PSU Executive Trainee, Research Scientist, Technical Lead."
            steps_en = [
                "Solve 150+ DSA problems covering Trees, Graphs, DP on LeetCode.",
                "Deploy two scalable full-stack applications with CI/CD on cloud infrastructure.",
                "If targeting GATE / PSUs, register at official GATE portal and solve 15 years previous papers."
            ]

        if lang == "te":
            return {
                "mode": "rule_based",
                "title": f"B.Tech ({stream}) ఇంజనీర్ల కెరీర్ రోడ్‌మ్యాప్ ({status})",
                "summary": f"B.Tech {stream} పూర్తి చేసిన విద్యార్థులకు సాఫ్ట్‌వేర్, GATE PSU రిక్రూట్‌మెంట్, కోర్ పరిశ్రమలు మరియు ఉన్నత విద్య యొక్క స్పష్టమైన ప్రణాళిక.",
                "roadmap": {
                    "current_position": stage_label,
                    "suitable_options": options_en,
                    "option_selected": sel_en,
                    "eligibility": elig_en,
                    "what_to_study_skills": study_en,
                    "entrance_exams": exams_en,
                    "admission_process": adm_en,
                    "next_education_or_career_step": next_step_en,
                    "career_opportunities": career_en,
                    "next_steps": steps_en
                },
                "disclaimer": "CareerCompass ధృవీకరించిన సమాచారం. సిఫార్సులు మార్గదర్శనం కొరకు మాత్రమే; తుది ఎంపిక మీ నైపుణ్యాలపై ఆధారపడి ఉంటుంది."
            }
        elif lang == "hi":
            return {
                "mode": "rule_based",
                "title": f"B.Tech ({stream}) इंजीनियरों के लिए करियर रोडमैप ({status})",
                "summary": f"B.Tech {stream} छात्रों के लिए सॉफ्टवेयर टेक करियर, GATE द्वारा PSU व IIT प्रवेश, कोर उद्योग व रक्षा तकनीकी प्रविष्टियों का विस्तृत रोडमैप।",
                "roadmap": {
                    "current_position": stage_label,
                    "suitable_options": options_en,
                    "option_selected": sel_en,
                    "eligibility": elig_en,
                    "what_to_study_skills": study_en,
                    "entrance_exams": exams_en,
                    "admission_process": adm_en,
                    "next_education_or_career_step": next_step_en,
                    "career_opportunities": career_en,
                    "next_steps": steps_en
                },
                "disclaimer": "CareerCompass सत्यापित मार्गदर्शन। सिफारिशें केवल मार्गदर्शन हेतु हैं; अंतिम चयन कौशल पर निर्भर करता है।"
            }
        else:
            return {
                "mode": "rule_based",
                "title": title_en,
                "summary": summary_en,
                "roadmap": {
                    "current_position": stage_label,
                    "suitable_options": options_en,
                    "option_selected": sel_en,
                    "eligibility": elig_en,
                    "what_to_study_skills": study_en,
                    "entrance_exams": exams_en,
                    "admission_process": adm_en,
                    "next_education_or_career_step": next_step_en,
                    "career_opportunities": career_en,
                    "next_steps": steps_en
                },
                "disclaimer": "CareerCompass verified guidance. Recommendations do not guarantee placement outcomes."
            }

    @staticmethod
    def answer_assistant_question(profile: Dict[str, Any], message: str, language: str = "en") -> str:
        """
        Direct conversational answer generator for CareerCompass Assistant.
        Addresses user's specific question FIRST, informed by student's exact stage.
        Never invents unverified dates, fees, vacancies, or cutoffs.
        """
        raw_qual = profile.get("qualification") or profile.get("education_level") or ""
        qual = AIEngine.normalize_qualification(raw_qual or message)
        stream = AIEngine.normalize_stream(profile.get("branch") or profile.get("stream_or_branch") or "", qual)
        status = profile.get("completion_status") or "Final Year"
        msg_lower = message.lower()
        lang = (language or "en").lower().strip()

        # Check for date / deadline / vacancy queries to prevent hallucinations
        is_date_or_vacancy_query = any(k in msg_lower for k in ["when", "date", "deadline", "fee", "vacancy", "vacancies", "opening", "last date", "counselling date"])
        if is_date_or_vacancy_query:
            verified = get_verified_current_data(message)
            if verified:
                v = verified[0]
                title = v.get("title", "Official Opportunity")
                org = v.get("organization", "Official Authority")
                source = v.get("official_source", "official portal")
                start = v.get("start_datetime", "Check notification")
                end = v.get("end_datetime", "Check notification")
                fee = v.get("application_fee", "Refer to official prospectus")
                
                if lang == "te":
                    return (
                        f"**ధృవీకరించబడిన తాజా సమాచారం ({org}):**\n\n"
                        f"• **నోటిఫికేషన్:** {title}\n"
                        f"• **దరఖాస్తు ప్రారంభం:** {start}\n"
                        f"• **చివరి తేదీ:** {end}\n"
                        f"• **ఫీజు వివరాలు:** {fee}\n"
                        f"• **అధికారిక మూలం:** [{source}]({source})\n\n"
                        f"*దయచేసి దరఖాస్తు చేసుకునే ముందు అధికారిక పోర్టల్ నుండి పూర్తి నోటిఫికేషన్ PDFని సరిచూసుకోండి.*"
                    )
                elif lang == "hi":
                    return (
                        f"**सत्यापित वर्तमान जानकारी ({org}):**\n\n"
                        f"• **अधिसूचना:** {title}\n"
                        f"• **आवेदन प्रारंभ:** {start}\n"
                        f"• **अंतिम तिथि:** {end}\n"
                        f"• **शुल्क:** {fee}\n"
                        f"• **आधिकारिक स्रोत:** [{source}]({source})\n\n"
                        f"*कृपया आवेदन करने से पहले आधिकारिक वेबसाइट से विस्तृत अधिसूचना PDF की जांच अवश्य करें।*"
                    )
                else:
                    return (
                        f"**Verified Official Update ({org}):**\n\n"
                        f"• **Notification:** {title}\n"
                        f"• **Application Window:** {start} to {end}\n"
                        f"• **Fee Details:** {fee}\n"
                        f"• **Official Source:** [{source}]({source})\n\n"
                        f"*Always verify the complete notification PDF directly on the official authority portal before submitting your application.*"
                    )
            else:
                if lang == "te":
                    return "నేను ఈ సమాచారం కోసం ధృవీకరించిన ప్రస్తుత అప్‌డేట్‌ను కలిగి లేను. దయచేసి సంబంధిత అధికారిక పోర్టల్‌లో అధికారిక నోటిఫికేషన్‌ను చూడండి."
                elif lang == "hi":
                    return "मेरे पास इस जानकारी का कोई सत्यापित वर्तमान अपडेट नहीं है। कृपया संबंधित आधिकारिक पोर्टल पर आधिकारिक अधिसूचना देखें।"
                else:
                    return "I don't have a verified current update for this information. Please check the official notification on the relevant official authority portal."

        # Question: "What can I do after Diploma CSE?"
        if "diploma" in msg_lower and any(k in msg_lower for k in ["cse", "computer"]):
            if lang == "te":
                return (
                    "**డిప్లొమా CSE తర్వాత మీ ముఖ్యమైన అవకాశాలు:**\n\n"
                    "1. **B.Tech 2వ సంవత్సరం లాటరల్ ఎంట్రీ (ECET):** రాష్ట్ర ECET పరీక్ష ద్వారా నేరుగా B.Tech 2వ సంవత్సరం (3వ సెమిస్టర్) లో చేరవచ్చు. ఇది అత్యంత ప్రాధాన్యత కలిగిన మార్గం.\n"
                    "2. **జూనియర్ సాఫ్ట్‌వేర్ ఉద్యోగాలు:** వెబ్ డెవలప్‌మెంట్ (HTML/CSS/JS, Python/Java) నైపుణ్యాలతో IT స్టార్టప్‌లలో జూనియర్ డెవలపర్ లేదా సపోర్ట్ ఇంజనీర్‌గా చేరవచ్చు.\n"
                    "3. **కేంద్ర ప్రభుత్వ సాంకేతిక ఉద్యోగాలు:** రైల్వేస్ RRB JE (IT), DRDO CEPTAM, ISRO టెక్నికల్ అసిస్టెంట్ పోస్టులకు దరఖాస్తు చేసుకోవచ్చు.\n"
                    "4. **NATS అప్రెంటిస్‌షిప్:** ప్రభుత్వ స్టైపెండ్‌తో పరిశ్రమల శిక్షణ పొందవచ్చు (nats.education.gov.in)."
                )
            elif lang == "hi":
                return (
                    "**डिप्लोमा CSE के बाद आपके प्रमुख विकल्प:**\n\n"
                    "1. **B.Tech लेटरल एंट्री (ECET):** राज्य ECET के माध्यम से सीधे B.Tech द्वितीय वर्ष (तीसरे सेमेस्टर) में प्रवेश लेकर 1 वर्ष बचा सकते हैं।\n"
                    "2. **जूनियर सॉफ्टवेयर नौकरियां:** वेब डेवलपमेंट (Python, Java, React) सीखकर सॉफ्टवेयर कंपनियों व स्टार्टअप्स में जूनियर इंजीनियर बन सकते हैं।\n"
                    "3. **सरकारी नौकरियां:** रेलवे RRB JE (IT), DRDO CEPTAM, ISRO तकनीकी सहायक में डिप्लोमा CSE धारक सीधे पात्र हैं।\n"
                    "4. **NATS अप्रेंटिसशिप:** मासिक स्टाइपेंड के साथ nats.education.gov.in पर पंजीकृत होकर औद्योगिक अनुभव प्राप्त करें।"
                )
            else:
                return (
                    "**Key Pathways After Diploma in CSE:**\n\n"
                    "1. **Lateral Entry to B.Tech (Direct 2nd Year via State ECET):** This is the highest-ROI pathway. You enter the 3rd semester of B.Tech CSE directly, saving an entire academic year.\n"
                    "2. **Junior Software / Web Developer:** With practical skills in Python, Java, or MERN stack, you can secure entry-level roles in tech startups and IT services.\n"
                    "3. **Central Government Technical Jobs:** Eligible for RRB JE (IT) in Indian Railways, DRDO CEPTAM, and ISRO Technical Assistant (Level-6 / Level-7 pay scale).\n"
                    "4. **NATS Apprenticeship:** Paid industrial training through the National Apprenticeship Training Scheme (nats.education.gov.in)."
                )

        # Question: "What can I do after 10th?"
        if any(k in msg_lower for k in ["after 10th", "after class 10", "10th completed", "10th class"]):
            if lang == "te":
                return (
                    "**10వ తరగతి తర్వాత ముఖ్యమైన విద్యా మార్గాలు:**\n\n"
                    "1. **ఇంటర్మీడియట్ (11-12వ తరగతి):**\n"
                    "   • **MPC:** ఇంజనీరింగ్ (B.Tech), NDA డిఫెన్స్, ఆర్కిటెక్చర్ కొరకు.\n"
                    "   • **BiPC:** మెడిసిన్ (MBBS/BDS/AYUSH), ఫార్మసీ, అగ్రికల్చర్, నర్సింగ్ కొరకు.\n"
                    "   • **MEC / CEC:** CA, CMA, CS, B.Com, BBA, కార్పొరేట్ లా కొరకు.\n"
                    "2. **పాలిటెక్నిక్ డిప్లొమా (3 సం.):** POLYCET ద్వారా CSE, Mech, Civil, ECE ఇంజనీరింగ్. ఆ తర్వాత ECET తో 2వ సంవత్సరం B.Tech.\n"
                    "3. **ITI టెక్నికల్ ట్రేడ్స్ (1-2 సం.):** ఎలక్ట్రీషియన్, ఫిట్టర్ కోర్సులు (తక్షణ రైల్వే/PSU ఉద్యోగాలకు)."
                )
            elif lang == "hi":
                return (
                    "**कक्षा 10वीं के बाद प्रमुख विकल्प:**\n\n"
                    "1. **इंटरमीडिएट (11वीं-12वीं):**\n"
                    "   • **MPC:** इंजीनियरिंग (B.Tech), NDA सेना, विज्ञान के लिए।\n"
                    "   • **BiPC:** डॉक्टरी (NEET UG / MBBS), फार्मेसी, कृषि के लिए।\n"
                    "   • **MEC / CEC:** सीए (CA), वाणिज्य, प्रबंधन और कानून के लिए।\n"
                    "2. **पॉलीटेक्निक डिप्लोमा (3 वर्ष):** POLYCET द्वारा इंजीनियरिंग डिप्लोमा, तत्पश्चात B.Tech लेटरल एंट्री।\n"
                    "3. **आईटीआई ट्रेड्स (1-2 वर्ष):** इलेक्ट्रीशियन, फिटर (रेलवे व रक्षा तकनीशियन पदों हेतु)।"
                )
            else:
                return (
                    "**Educational Pathways After Class 10th:**\n\n"
                    "1. **Intermediate / Higher Secondary (10+2):**\n"
                    "   • **MPC (Maths, Physics, Chemistry):** Ideal for B.Tech, NDA Defence Officer, Architecture, Pure Sciences.\n"
                    "   • **BiPC (Biology, Physics, Chemistry):** Foundation for NEET UG (MBBS/BDS), Pharmacy, Agriculture, Nursing.\n"
                    "   • **MEC / CEC:** Foundation for Chartered Accountancy (CA), B.Com, BBA, Corporate Law.\n"
                    "2. **Polytechnic Diploma (3 Years via State POLYCET):** Hands-on engineering with direct lateral entry into 2nd year B.Tech via ECET.\n"
                    "3. **ITI Trades (1 to 2 Years):** Practical vocational certifications in Electrician, Fitter, Motor Mechanic for immediate PSU/Railway recruitment."
                )

        # Question: Defence / Armed Forces specific query
        if any(k in msg_lower for k in ["defence", "army", "navy", "air force", "join defence", "nda", "cds", "afcat"]):
            if lang == "te":
                return (
                    "**భారత సాయుధ దళాల ప్రవేశ మార్గాలు:**\n\n"
                    "1. **12వ తరగతి తర్వాత:** UPSC NDA & NA (ఆర్మీ, నేవీ, ఎయిర్ ఫోర్స్ వింగ్స్) మరియు 10+2 TES (B.Tech క్యాడెట్).\n"
                    "2. **గ్రాడ్యుయేషన్ తర్వాత:** UPSC CDS పరీక్ష (IMA, INA, AFA, OTA) మరియు AFCAT (ఎయిర్ ఫోర్స్ ఫ్లయింగ్/గ్రౌండ్ డ్యూటీ).\n"
                    "3. **B.Tech ఇంజనీరింగ్ తర్వాత:** TGC మరియు SSC Tech (రాత పరీక్ష లేకుండా మార్కుల ఆధారంగా డైరెక్ట్ 5-రోజుల SSB ఇంటర్వ్యూ).\n"
                    "4. **10వ/12వ తర్వాత ఇతర ఎంట్రీలు:** ఆర్మీ, నేవీ, ఎయిర్ ఫోర్స్ అగ్నివీర్ రిక్రూట్‌మెంట్.\n\n"
                    "*మరిన్ని వివరాలకు joinindianarmy.nic.in పరిశీలించండి.*"
                )
            elif lang == "hi":
                return (
                    "**भारतीय सशस्त्र बलों में करियर के प्रमुख अवसर:**\n\n"
                    "1. **12वीं के बाद:** UPSC NDA & NA (थल, नौसेना, वायु सेना) और 10+2 तकनीकी प्रविष्टि (TES B.Tech कैडेट)।\n"
                    "2. **स्नातक के बाद:** UPSC CDS परीक्षा (IMA, INA, AFA, OTA) और AFCAT (वायु सेना)।\n"
                    "3. **B.Tech के बाद:** TGC और SSC Tech (इंजीनियरिंग अंकों के आधार पर बिना लिखित परीक्षा सीधा SSB साक्षात्कार)।\n"
                    "4. **10वीं/12वीं के बाद:** तीनों सेनाओं में अग्निवीर भर्ती योजना।\n\n"
                    "*सत्यापित विवरण हेतु joinindianarmy.nic.in देखें।*"
                )
            else:
                return (
                    "**Key Pathways to Join the Indian Armed Forces (Defence):**\n\n"
                    "1. **After 12th (MPC):** UPSC NDA & NA (National Defence Academy for Army, Navy, Air Force) and 10+2 Technical Entry Scheme (TES - Army & Navy B.Tech Cadet).\n"
                    "2. **After Graduation (Degree / B.Tech):** UPSC Combined Defence Services (CDS) for IMA, INA, AFA, OTA, and AFCAT for Air Force.\n"
                    "3. **After B.Tech (Direct Technical Entry):** Army TGC (Technical Graduate Course) & SSC Tech, and Navy SSC (Direct 5-Day SSB based on engineering percentage without a written exam).\n"
                    "4. **After 10th / 12th:** Agniveer Recruitment Schemes in Army, Navy, and Air Force.\n\n"
                    "*Always verify physical and age standards at joinindianarmy.nic.in or upsc.gov.in.*"
                )

        # Question: "What exams can I write?"
        if any(k in msg_lower for k in ["which exams", "what exams", "exams can i write", "competitive exams"]):
            if qual == "10th":
                exams_list = "• State POLYCET (for Polytechnic Diploma)\n• APRJC / TSRJC (Residential Junior Colleges)\n• Army Agniveer CEE (General Duty & Tradesmen)"
            elif qual == "Intermediate":
                if "BIPC" in stream:
                    exams_list = "• NEET UG (MBBS, BDS, AYUSH, B.Sc Nursing)\n• State EAPCET (Agriculture & Pharmacy)\n• ICAR AIEEA (Central Agricultural Universities)"
                else:
                    exams_list = "• JEE Main & JEE Advanced (IITs, NITs, IIITs)\n• State EAPCET / CET (State Engineering Colleges)\n• UPSC NDA & NA (Army, Navy, Air Force Officer Cadet)\n• BITSAT (BITS Pilani Campuses)\n• NATA (Architecture)"
            elif qual == "Diploma":
                exams_list = "• State ECET / JELET / LEET (Direct Lateral Entry to 2nd Year B.Tech)\n• SSC JE (Staff Selection Commission Junior Engineer)\n• RRB JE (Railway Recruitment Board Junior Engineer)\n• DRDO CEPTAM & ISRO Technical Assistant"
            elif qual == "Postgraduate":
                exams_list = "• UGC NET / CSIR NET (for JRF & Assistant Professorship)\n• GATE (for Ph.D. admissions & PMRF nomination)\n• ISRO Scientist-SC & DRDO Scientist-B Centralised Recruitments"
            else:
                # B.Tech
                exams_list = "• GATE (M.Tech at IITs with stipend & PSU recruitments at ONGC, IOCL, NTPC)\n• CAT / XAT (for MBA at IIMs & premier B-Schools)\n• UPSC Engineering Services Examination (ESE / IES)\n• UPSC CDS / AFCAT (Defence Technical Officer entries)\n• GRE / TOEFL / IELTS (for Master's abroad)"

            return f"**Official Entrance & Competitive Examinations for {qual} ({stream}):**\n\n{exams_list}\n\n*Always consult verified notifications in the CareerCompass Notification Center before registering.*"

        # Question: "What skills should I learn?"
        if any(k in msg_lower for k in ["what skills", "skills should i learn", "skills to learn", "skills needed"]):
            if qual == "10th":
                skills_list = "• Strong conceptual foundations in Class 9-10 Mathematics & Science\n• Professional English reading and verbal comprehension\n• Fundamental computer operations and touch-typing\n• Analytical reasoning and logical problem solving"
            elif qual == "Intermediate":
                skills_list = "• Speed and accuracy in numerical problem solving\n• Time management under negative-marking exam conditions\n• Deep NCERT conceptual clarity\n• Scientific calculators and spatial visualization"
            elif qual == "Diploma":
                if "CSE" in stream:
                    skills_list = "• Core Programming: Python, Java, or C++\n• Web Development: HTML, CSS, JavaScript, and React basics\n• Database fundamentals: SQL & Relational modeling\n• Linux CLI & Git version control"
                else:
                    skills_list = "• 2D/3D Computer Aided Design (AutoCAD, SolidWorks, CATIA)\n• Industrial instruments, measurement, and quality tolerances\n• Workshop safety protocols and electrical/mechanical schematics\n• General Aptitude for SSC/RRB Junior Engineer tests"
            elif "CYBER" in stream:
                skills_list = "• Networking protocols (TCP/IP, OSI layers, DNS, routing)\n• Linux terminal administration and Bash scripting\n• Security tools: Wireshark, Nmap, Burp Suite\n• Practical labs: TryHackMe Pre-Security and SOC Level 1"
            elif "MECH" in stream:
                skills_list = "• CAD modeling (SolidWorks / Creo) & FEA simulation (ANSYS)\n• Thermodynamics, Fluid Machinery, and Strength of Materials\n• GD&T (Geometric Dimensioning and Tolerancing)\n• Engineering Mathematics and GATE problem-solving speed"
            else:
                skills_list = "• Data Structures & Algorithms (Arrays, Trees, Graphs, DP on LeetCode)\n• System Design: High-Level and Low-Level architecture principles\n• Modern frameworks: Spring Boot / React / Node.js\n• Cloud fundamentals (AWS or Google Cloud) & Docker containerization"

            return f"**Recommended Skills to Master for {qual} ({stream}):**\n\n{skills_list}\n\n*Start with 1-2 core skills and build practical projects to demonstrate verified ability.*"

        # Question: "Can I go for higher studies?"
        if any(k in msg_lower for k in ["higher studies", "master", "phd", "m.tech", "study abroad"]):
            if qual == "10th":
                return "After Class 10th, your primary next step is 10+2 Intermediate (MPC / BiPC / CEC) or a 3-Year Polytechnic Diploma. Once you complete Intermediate or Diploma, you can progress to Bachelor's Degree programs (like B.Tech, MBBS, B.Sc, B.Com)."
            elif qual == "Diploma":
                return "Yes! Diploma holders have a dedicated higher-study gateway called **Lateral Entry B.Tech**. By clearing your State ECET (or JELET/LEET), you enter directly into the 2nd year (3rd semester) of B.Tech without losing time."
            elif qual == "Degree":
                return f"Yes! As a Bachelor's degree holder in {stream}, you are eligible for Master's programs: M.Sc in your discipline via CUET PG, MBA via CAT/MAT/State ICET for management leadership, or MCA if you have mathematics foundations."
            elif qual == "Postgraduate":
                return "Yes! As a postgraduate, your next higher academic step is a **Ph.D. / Doctoral Fellowship**. You can apply for the prestigious Prime Minister's Research Fellowship (PMRF) or IIT/CSIR doctoral admissions with stipends up to Rs 70,000-80,000/month."
            else:
                return f"Yes! After B.Tech ({stream}), top higher-study options include:\n1. **M.Tech at IITs/NITs via GATE** with Rs 12,400/month stipend.\n2. **MS Abroad** (USA, Germany, UK, Canada) via GRE and TOEFL/IELTS.\n3. **MBA at IIMs** via CAT for techno-commercial and product management leadership."

        # Default fallback: generate structured roadmap for their exact profile
        roadmap_res = AIEngine.generate_qualification_aware_roadmap(profile, message, language=lang)
        r = roadmap_res.get("roadmap", {})
        return (
            f"**{roadmap_res.get('title', 'Educational Guidance')}**\n\n"
            f"{roadmap_res.get('summary', '')}\n\n"
            f"• **Current Stage:** {r.get('current_position', qual)}\n"
            f"• **Recommended Pathways:**\n"
            + "\n".join([f"  - {opt}" for opt in r.get("suitable_options", [])[:4]])
            + f"\n\n• **Recommended Exams:** {', '.join(r.get('entrance_exams', []))}\n"
            f"• **Target Outcomes:** {r.get('career_opportunities', '')}\n\n"
            f"*{roadmap_res.get('disclaimer', '')}*"
        )

    @staticmethod
    def build_gemini_prompt(profile: Dict[str, Any], message: str, language: str = "en", verified_context: Optional[List[Dict[str, Any]]] = None) -> str:
        """
        Builds strict qualification-aware system prompt for Gemini LLM.
        """
        raw_qual = profile.get("qualification") or profile.get("education_level") or "B.Tech"
        qual = AIEngine.normalize_qualification(raw_qual)
        stream = AIEngine.normalize_stream(profile.get("branch") or profile.get("stream_or_branch") or "", qual)
        status = profile.get("completion_status") or "Final Year"
        interests = profile.get("interests") or []

        ver_text = ""
        if verified_context:
            ver_text = "\n\nVERIFIED DATABASE UPDATES (Cite these if asked about dates/deadlines):\n" + json.dumps(verified_context, indent=2)

        lang_instruction = ""
        if language == "te":
            lang_instruction = (
                "\nCRITICAL LOCALIZATION: Write the ENTIRE response in natural, fluent Telugu (తెలుగు). "
                "Keep standard acronyms (GATE, JEE, UPSC, CSE, B.Tech, Python, M.Tech, ECET, NEET) in Latin/English script."
            )
        elif language == "hi":
            lang_instruction = (
                "\nCRITICAL LOCALIZATION: Write the ENTIRE response in natural, fluent Hindi (हिन्दी). "
                "Keep standard acronyms (GATE, JEE, UPSC, CSE, B.Tech, Python, M.Tech, ECET, NEET) in Latin/English script."
            )

        prompt = (
            f"You are the CareerCompass AI Career Guide for Indian students.\n"
            f"The student's EXACT educational stage is: {qual}, Stream/Branch: {stream}, Status: {status}.\n"
            f"Interests: {interests}.\n\n"
            f"CRITICAL STAGE RULES (STRICT COMPLIANCE REQUIRED):\n"
            f"1. After 10th != Intermediate != Diploma != Degree != B.Tech != Postgraduate. Never generate the same roadmap.\n"
            f"2. If student is After 10th: Focus STRICTLY on NEXT-STAGE choices: Intermediate (MPC, BiPC, CEC, MEC, HEC), 3-Year Polytechnic Diploma (via POLYCET), ITI, Vocational. Never assume software job or B.Tech career!\n"
            f"3. If student is Intermediate: Tailor to stream (MPC -> Engineering/B.Sc/NDA; BiPC -> Medicine/NEET, Pharmacy, Agri, Biotech; CEC/MEC -> CA, B.Com, BBA, Law).\n"
            f"4. If student is Diploma: Focus on Lateral Entry into 2nd year B.Tech via ECET, Junior Engineer government exams (RRB JE, SSC JE), and core industry roles. Branch matters (CSE != Mech != Civil).\n"
            f"5. If student is Degree: Non-engineering graduates (B.Sc, B.Com, BA, BCA, BBA) -> Higher studies (M.Sc, MCA, MBA), govt exams (UPSC, Banking), corporate roles.\n"
            f"6. If student is B.Tech: Distinguish status ({status}) and branch ({stream}). Show post-B.Tech pathways: Software/IT, Cyber Security, Core Engineering, PSUs via GATE, M.Tech, MS abroad, MBA, Defence. Do NOT show CSE/ECE as next options!\n"
            f"7. If student is Postgraduate: Focus on PhD, Research, Academia (UGC NET), High-Tech leadership.\n"
            f"8. ANSWER THE USER'S SPECIFIC QUESTION FIRST before providing roadmaps or general advice.\n"
            f"9. NEVER HALLUCINATE OR INVENT current dates, deadlines, fees, cutoffs, or vacancies. If verified data is not provided in context, state: 'I don't have a verified current update for this information. Please check the official notification.' and cite official portal.\n"
            f"{ver_text}"
            f"{lang_instruction}"
        )
        return prompt

    @staticmethod
    def get_study_practice_guidance(profile: Dict[str, Any], question: str, language: str = "en") -> Dict[str, Any]:
        """
        Provides qualification-aware personalized study & practice guidance,
        grounded strictly in the verified learning resource database.
        Never hallucinates fake courses or arbitrary random URLs.
        """
        raw_qual = profile.get("qualification") or profile.get("education_level") or "B.Tech"
        qual = AIEngine.normalize_qualification(raw_qual)
        stream = AIEngine.normalize_stream(profile.get("branch") or profile.get("stream_or_branch") or "", qual)
        interests = profile.get("interests") or profile.get("career_interests") or []
        selected_exam = profile.get("selected_exam") or ""

        # Load verified resources from learning_resources.json
        all_res = load_data_file("learning_resources.json")
        if not isinstance(all_res, list):
            all_res = []

        q_lower = (question or "").lower()

        # Qualification-specific study guidance
        if qual == "10th":
            # Filter strictly for school resources
            relevant_resources = [r for r in all_res if any(q in ["10th", "secondary", "school", "all"] for q in [x.lower() for x in r.get("education_levels", [])])]
            topics = [
                "Mathematics: Real Numbers, Polynomials, Linear Equations, Quadratic Equations, Trigonometry",
                "Science (Physics & Chemistry): Light Reflection/Refraction, Chemical Reactions, Electricity",
                "Biology: Life Processes, Control & Coordination, Heredity",
                "Social Science: History, Geography, Democratic Politics, Economics",
                "Computer Basics: Elementary Programming, Digital Literacy, Productivity Tools"
            ]
            advice = (
                f"### 🎯 Foundational Study Strategy for Class 10 Students\n\n"
                f"As a 10th standard student, your #1 focus is building unshakable subject fundamentals in **Mathematics and Science**. "
                f"Advanced engineering frameworks, cloud computing, and collegiate placement DSA are **not** applicable at this stage.\n\n"
                f"**What you should focus on right now:**\n"
                f"1. **Master the NCERT Textbook:** Read line-by-line and solve every single end-of-chapter exercise.\n"
                f"2. **Practice Visual Understanding:** Use **Khan Academy India** for step-by-step conceptual mastery in algebra and physics.\n"
                f"3. **Solve State/CBSE Exemplar Problems:** Access official digital worksheets on the **DIKSHA Portal**.\n"
                f"4. **Explore Future Directions:** Understand the key differences between 10+2 Intermediate (MPC vs BiPC vs Commerce) and Polytechnic Diploma (POLYCET) before your board exams conclude."
            )

        elif qual == "Intermediate":
            norm_s = stream.lower()
            if "bipc" in norm_s or "medical" in norm_s:
                relevant_resources = [r for r in all_res if any(q in ["intermediate", "10+2", "all"] for q in [x.lower() for x in r.get("education_levels", [])]) and any(s in ["bipc", "sciences", "all streams"] for s in [x.lower() for x in r.get("streams", [])])]
                topics = [
                    "Biology (Botany & Zoology): Human Physiology, Genetics & Evolution, Cell Structure, Plant Physiology",
                    "Chemistry: Organic Chemistry Mechanisms, Chemical Bonding, Coordination Compounds, Solutions",
                    "Physics: Mechanics, Thermodynamics, Optics, Modern Physics",
                    "Mock Tests: Full-length NTA Abhyas NEET Mock Test series"
                ]
                advice = (
                    f"### 🩺 Pre-Medical & Science Study Strategy for Intermediate (BiPC)\n\n"
                    f"For Intermediate BiPC students aiming for **NEET UG**, Pharmacy, or Allied Health Sciences:\n\n"
                    f"1. **Biology NCERT Mastery:** Over 85% of NEET biology questions originate directly from NCERT textbook diagrams and lines.\n"
                    f"2. **Timed Mock Practice:** Practice full 3-hour 20-minute speed tests on the official **National Test Abhyas (NTA)** app.\n"
                    f"3. **Physical Chemistry & Physics Numerical Drills:** Dedicate at least 90 minutes daily exclusively to formula derivation and problem solving."
                )
            elif "commerce" in norm_s or "cec" in norm_s or "mec" in norm_s:
                relevant_resources = [r for r in all_res if any(q in ["intermediate", "10+2", "degree", "all"] for q in [x.lower() for x in r.get("education_levels", [])])]
                topics = [
                    "Accountancy: Double Entry Bookkeeping, Ledger Accounts, Financial Statements",
                    "Economics: Microeconomics, Macroeconomics, Indian Economic Development",
                    "Business Studies / Commerce: Trade, Banking, Principles of Management",
                    "Aptitude & Logical Foundations: Quantitative Aptitude, Data Interpretation for CUET / CA Foundation"
                ]
                advice = (
                    f"### 💼 Commerce & Economics Study Strategy for Intermediate (MEC/CEC)\n\n"
                    f"For Intermediate Commerce students preparing for **CA Foundation**, **CUET UG**, or undergraduate business degrees:\n\n"
                    f"1. **Accounting Clarity:** Master ledger balancing, depreciation accounting, and partnership fundamentals on **SWAYAM**.\n"
                    f"2. **Economics Analysis:** Practice graphs and macroeconomic indicators using official NCERT ePathshala modules.\n"
                    f"3. **Quantitative Skills:** Solidify basic commercial mathematics and reasoning for upcoming university entrance tests."
                )
            else: # MPC
                relevant_resources = [r for r in all_res if any(q in ["intermediate", "10+2", "all"] for q in [x.lower() for x in r.get("education_levels", [])]) and any(s in ["mpc", "engineering", "all streams"] for s in [x.lower() for x in r.get("streams", [])])]
                topics = [
                    "Mathematics: Calculus (Integration & Derivatives), Vectors, 3D Geometry, Matrices, Probability",
                    "Physics: Mechanics, Electromagnetism, Modern Physics, Wave Optics",
                    "Chemistry: Organic Chemistry Reaction Pathways, Periodic Trends, Chemical Kinetics",
                    "Entrance Test Strategy: JEE Main & State EAPCET chapter-wise speed solving"
                ]
                advice = (
                    f"### 📐 Engineering Entrance Study Strategy for Intermediate (MPC)\n\n"
                    f"For Intermediate MPC students targeting **JEE Main, JEE Advanced, and State EAPCET**:\n\n"
                    f"1. **Concept-to-Problem Transition:** Use **Khan Academy India** to review difficult concepts in calculus and electromagnetism.\n"
                    f"2. **Official Mock Tests:** Take computer-based simulated tests on the **National Test Abhyas (NTA)** platform to master negative marking discipline.\n"
                    f"3. **PYQ Solving:** Analyze at least 5 years of JEE Main / EAPCET papers to identify recurring multi-concept questions."
                )

        elif qual == "Diploma":
            relevant_resources = [r for r in all_res if any(q in ["diploma", "polytechnic", "all"] for q in [x.lower() for x in r.get("education_levels", [])])]
            topics = [
                f"{stream} Core Fundamentals: Key technical theorems, schematics, and design standards",
                "Lateral Entry (ECET) Syllabus: Mathematics (Differential Equations, Matrices), Analytical Chemistry & Physics",
                "Hands-on Lab Simulation: Virtual engineering experiments on Virtual Labs (IITs / MoE)",
                "Technical Aptitude: Objective MCQs on IndiaBIX for RRB JE, SSC JE, and state power utilities",
                "Practical Software: Computer-Aided Design (AutoCAD/FreeCAD) & Programming on Spoken Tutorial"
            ]
            advice = (
                f"### ⚙️ Technical Mastery & Lateral Entry Strategy for Diploma ({stream})\n\n"
                f"For Polytechnic Diploma students balancing final semester exams, **State ECET lateral entry to B.Tech**, and Junior Engineer recruitments:\n\n"
                f"1. **Focus on Mathematics for ECET:** 50 marks in ECET come from engineering mathematics (matrices, calculus, differential equations). Prioritize this daily.\n"
                f"2. **Practice Technical MCQs:** Use **IndiaBIX** to solve branch-specific objective questions ({stream}) for both ECET and RRB JE.\n"
                f"3. **Interactive Lab Practice:** Run remote experimental simulations on **Virtual Labs (vlab.co.in)** to solidify real-world apparatus knowledge.\n"
                f"4. **Open-Source Software Certifications:** Complete free workshops on **Spoken Tutorial (IIT Bombay)** in CAD, Linux, or Python."
            )

        elif qual in ["B.Tech", "Degree"]:
            is_cs_it = any(k in stream.lower() for k in ["cse", "computer", "it", "ai", "data science", "software"])
            if is_cs_it:
                relevant_resources = [r for r in all_res if any(q in ["b.tech", "degree", "all"] for q in [x.lower() for x in r.get("education_levels", [])]) and any(b in ["cse", "it", "all engineering", "all branches"] for b in [x.lower() for x in r.get("branches", [])])]
                topics = [
                    "Data Structures & Algorithms: Arrays, Linked Lists, Trees, Graphs, Dynamic Programming, Binary Search",
                    "Core Computer Science: Operating Systems (Process Scheduling, Deadlocks, Memory Management), DBMS (SQL Queries, Normalization, ACID), Computer Networks",
                    "Quantitative Aptitude & Reasoning: Speed Math, Permutation & Combination, Syllogisms, Reading Comprehension",
                    "Practical Projects: Full-Stack Web Development, REST APIs, Git Version Control, Cloud Deployment",
                    "Company Preparation: Technical Interview Rounds, System Design basics, HR Behavioral Scenarios"
                ]
                advice = (
                    f"### 💻 Campus Placement & Software Engineering Practice Blueprint (B.Tech {stream})\n\n"
                    f"For B.Tech {stream} students targeting product engineering roles, IT MNC drives, or GATE CSE:\n\n"
                    f"1. **Structured DSA Practice:** Solve 2-3 algorithmic problems daily on **LeetCode** and **CodeChef**, beginning with arrays, strings, and hash maps before moving to trees and dynamic programming.\n"
                    f"2. **CS Core Fundamentals:** Review operating systems, database queries, and networking protocols on **GeeksforGeeks** — these form 60%+ of technical interview questions.\n"
                    f"3. **Aptitude Drills:** Clear placement aptitude cutoffs by practicing on **PrepInsta** and **PlacementPreparation.io**.\n"
                    f"4. **Code Quality & Verification:** Obtain accredited skill badges on **HackerRank** to demonstrate verifiable problem-solving proficiency on your resume."
                )
            else:
                relevant_resources = [r for r in all_res if any(q in ["b.tech", "degree", "all"] for q in [x.lower() for x in r.get("education_levels", [])])]
                topics = [
                    f"{stream} Core Theory: In-depth understanding of standard university syllabus on NPTEL",
                    "Quantitative & Logical Aptitude: Campus recruitment written tests and PSU qualifying rounds on IndiaBIX",
                    "Engineering Tools & Simulations: Virtual Labs and software packages relevant to {stream}",
                    "GATE Preparation: Previous 15-year questions and comprehensive solutions on GATE Overflow",
                    "Programming Fundamentals: Python and SQL foundations for automation and engineering data analysis"
                ]
                advice = (
                    f"### 🛠️ Core Engineering & PSU Practice Blueprint (B.Tech {stream})\n\n"
                    f"For B.Tech {stream} students aiming for core industry roles, Maharatna PSUs (ISRO, DRDO, IOCL, NTPC), or GATE:\n\n"
                    f"1. **Authoritative University Lectures:** Watch semester modules delivered by IIT faculties on **NPTEL (IITs & IISc)**.\n"
                    f"2. **Simulate Industrial Laboratories:** Use **Virtual Labs (vlab.co.in)** to practice experimental methods and equipment configurations.\n"
                    f"3. **Aptitude & Technical MCQs:** Practice daily on **IndiaBIX** for company placement exams and state engineering tests.\n"
                    f"4. **GATE Question Analysis:** Solve topic-wise previous year questions on **GATE Overflow** to understand theoretical depth and numerical question types."
                )

        else: # Postgraduate
            relevant_resources = [r for r in all_res if any(q in ["postgraduate", "degree", "all"] for q in [x.lower() for x in r.get("education_levels", [])])]
            topics = [
                "Advanced Research Methodology: Literature Review, Experimental Design, Statistical Analysis",
                "Academic Literature Search: Citation analysis and state-of-the-art papers on Google Scholar and arXiv",
                "National Electronic Theses: Review completed doctoral dissertations on Shodhganga (UGC)",
                "Teaching & Research Eligibility: Paper 1 & Paper 2 preparation on the official UGC NET Portal"
            ]
            advice = (
                f"### 🎓 Academic Research & Advanced Practice Blueprint (Postgraduate)\n\n"
                f"For Postgraduate and doctoral scholars focusing on research excellence, industry R&D, or academic career pathways:\n\n"
                f"1. **Comprehensive Literature Review:** Access 500,000+ accredited Indian Ph.D. dissertations on **Shodhganga (INFLIBNET)**.\n"
                f"2. **Preprint & Open Access Research:** Stay ahead of breakthrough findings on **arXiv.org** and **Google Scholar**.\n"
                f"3. **Curate Digital Primary Sources:** Leverage the **National Digital Library of India (NDLI)** for rare monographs and academic references.\n"
                f"4. **National Eligibility Testing:** Practice official previous year question papers on the **UGC NET Online Portal**."
            )

        # Fallback to top 4 resources
        if not relevant_resources:
            relevant_resources = all_res[:4]

        # Formatting response
        cards = []
        for r in relevant_resources[:5]:
            cards.append({
                "id": r.get("id"),
                "name": r.get("name"),
                "description": r.get("description"),
                "official_url": r.get("official_url"),
                "category": r.get("category"),
                "access_type": r.get("access_type"),
                "free_features": r.get("free_features"),
                "skills": r.get("skills", [])[:4]
            })

        return {
            "status": "success",
            "qualification": qual,
            "stream": stream,
            "guidance_html": advice,
            "recommended_topics": topics,
            "verified_resources": cards,
            "total_resources": len(cards)
        }

