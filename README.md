# CAREER COMPASS: FIND YOUR TRUE NORTH

An intelligent, production-quality career-guidance and education-navigation platform designed specifically for Indian students.

CareerCompass guides students from their current qualification:
- Class 10th
- Intermediate / Class 11th–12th
- Diploma / Polytechnic
- Graduation / Degree
- B.Tech / B.E.
- Postgraduate
- Other Qualifications

Toward verified educational pathways, entrance exams, premier colleges, government engineering careers, defence opportunities, scholarships, counselling, cutoffs, and digital library resources.

---

## Key Features

1. **Zero Hallucination Standard**: Grounded in authentic Indian educational portals (NTA, UPSC, SSC, JoSAA, State CETs, IIT/IISc GATE, Join Indian Armed Forces, NSP, NCERT, NPTEL).
2. **Dynamic Notification Ticker**: Compares server date/time against verified `start_datetime` and `end_datetime` to eliminate expired events and display real-time status badges (`LIVE`, `OPEN`, `CLOSING SOON`, `RESULT`).
3. **All 12 Core Modules**:
   - Career Paths Explorer (10th, Inter, Diploma, Degree, B.Tech, PG, Other)
   - Entrance Exam Database with conducting bodies and timelines
   - Government Engineering Jobs (GATE, ISRO, DRDO, BARC, RRB JE, UPSC ESE, Bank SO)
   - Defence Forces Navigation (NDA, CDS, AFCAT, Technical Entries, Agniveer)
   - Colleges & Courses Explorer
   - Counselling & Cutoffs Reference with mandatory disclaimer
   - Scholarships Center (NSP, AICTE Pragati & Saksham, PMSSS, State ePASS)
   - Legal Digital Library (NCERT, NPTEL, GATE & UPSC PYQs)
   - AI Career Guide with dual engine (Google Gemini API + Offline Rule-Based Fallback)
   - Notification Center with detailed modal views
   - My Saved Roadmaps with interactive milestone checklists & progress tracking
   - 40+ Verified Official Links Directory (.gov.in / .nic.in)
4. **Student-Centric Modern Design**:
   - Light and Dark modes with instant toggle and persistence
   - Multi-language UI (English, Hindi, Telugu)
   - Fully responsive on Desktop, Laptop, Tablet, and Mobile (Android & iOS)

---

## Quick Start

### 1. Install Dependencies
```bash
python -m pip install -r requirements.txt
```

### 2. (Optional) Configure Gemini API Key
To enable cloud Gemini AI:
```bash
# Windows PowerShell
$env:GEMINI_API_KEY="your_actual_gemini_api_key"
```
*(If no key is configured, CareerCompass automatically and seamlessly operates on the comprehensive Rule-Based Knowledge Engine).*

### 3. Run the Server
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your web browser.
