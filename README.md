# Career Compass: FIND YOUR TRUE NORTH

An intelligent, production-ready career navigation and education guidance platform built specifically for Indian students across all educational stages.

Career Compass provides zero-hallucination, verified career roadmaps, real-time government and competitive exam notifications, curated preparation hub resources, personalized career radar matching, and AI-driven guidance tailored to each student's current qualification and goals.

---

## Table of Contents

1. [Project Overview](#project-overview)
2. [Key Features](#key-features)
3. [Technology Stack](#technology-stack)
4. [Project Directory Structure](#project-directory-structure)
5. [Installation & Setup](#installation--setup)
6. [Environment Variables](#environment-variables)
7. [Database Architecture & Setup](#database-architecture--setup)
8. [How to Run Locally](#how-to-run-locally)
9. [How AI Career Guide Works](#how-ai-career-guide-works)
10. [How My Career Radar Works](#how-my-career-radar-works)
11. [How the Preparation Hub Works](#how-the-preparation-hub-works)
12. [How Real-Time Notifications Work](#how-real-time-notifications-work)
13. [How Verified Data Updates Work](#how-verified-data-updates-work)
14. [Email & Browser Push Notifications](#email--browser-push-notifications)
15. [How to Deploy to Render](#how-to-deploy-to-render)
16. [Adding & Updating Official Resources](#adding--updating-official-resources)
17. [Running Automated Tests](#running-automated-tests)

---

## 1. Project Overview

Indian students navigating secondary, diploma, undergraduate, and graduate education face fragmented information regarding entrance exams, cutoffs, engineering streams, government opportunities, defence entries, scholarships, and free preparation resources. 

**Career Compass** unifies verified information into an authenticated, qualification-aware single-page application (SPA) backed by a Flask REST API and an ACID-compliant dual-dialect database engine (PostgreSQL & SQLite).

### Supported Educational Stages:
- **Class 10th (Secondary)**: Streams (MPC, BiPC, CEC, MEC, HEC), Polytechnic Diploma, ITI, Apprenticeships, NDA.
- **Intermediate / 10+2 (Higher Secondary)**: Engineering (JEE, State CETs), Medical (NEET), Commerce (CA, CMA, CS), Law (CLAT), Defence (NDA, Navy TES).
- **Diploma (Polytechnic)**: Lateral Entry to B.Tech (ECET), Junior Engineer exams (RRB JE, SSC JE), State PSU technical cadres.
- **Undergraduate / Degree (B.Sc / B.Com / BA / BBA / BCA)**: Post-graduation (MCA, MBA, M.Sc), Government services (UPSC CSE, SSC CGL, Banking PO/Clerk), Defence (CDS, AFCAT).
- **B.Tech / B.E. (Engineering)**: 33 specialized branch pathways, Software/IT, Core Industry, PSUs via GATE, Higher Studies (M.Tech, MS abroad), Defence Direct SSB (TGC, SSC Tech, Navy Executive).
- **Postgraduate (M.Tech / M.Sc / MCA / MBA / Ph.D.)**: UGC NET, CSIR NET, University Assistant Professor, Government Scientist (DRDO, ISRO, BARC), Corporate R&D.

---

## 2. Key Features

### 1. Login-First Security Architecture
- First-time visitors are presented with a clean, branded Sign-In screen. The main dashboard and personal data are strictly isolated behind authentication.
- Secure HttpOnly session cookies (`session_token`) with SameSite=Lax.
- Robust rate-limiting on authentication attempts (maximum 5 failed attempts per 15-minute window).
- Argon2id password hashing (`time_cost=3, memory_cost=65536, parallelism=4`) with zero plaintext storage and zero secret leakage in API payloads.
- Case-insensitive email normalization (`.strip().lower()`) on registration, login, and database queries.
- Instant 1-click transition from duplicate registration conflict (HTTP 409) to sign-in.

### 2. Qualification-Aware Onboarding & Profile Setup
- Guided post-registration setup capturing:
  - Educational Stage (10th, Intermediate, Diploma, B.Tech, Degree, PG)
  - Stream / Branch (dynamically populated based on stage; 33 engineering branches for B.Tech; general foundation curriculum for 10th)
  - Current Status (Currently Studying, Final Year, Completed)
  - Home State / Domicile
  - Dream Goal
- Seamless auto-login upon registration with instant transition to personalized dashboard once onboarded.

### 3. "Preparation Hub" (Free Practice & Training Resources)
- Replaces legacy exam prep labels with a unified, user-friendly **Preparation Hub**.
- Directory of 100% verified, authentic practice and learning platforms (SWAYAM, NPTEL, Virtual Labs, Diksha, PM e-VIDYA, NDLI, LeetCode, HackerRank, GeeksforGeeks, Khan Academy, Coursera Free, edX Free).
- Direct category filters: All Resources, National Learning Initiatives, Coding & Technical Practice, STEM & Virtual Labs, Mock Tests & Question Banks, Video Lectures.
- Resource badges highlighting Free Tiers (`100% Free`, `Free Tier + Optional Cert`), Target Exams (GATE, JEE, UGC NET), and Official Government Sources.

### 4. My Career Radar (Smart Opportunity Matching)
- Autonomous matching engine evaluating active notifications against the student's qualification, branch family, completion status, and state domicile.
- Match score calculation (0–100%) with badges: `HIGH MATCH (90%+)`, `ELIGIBLE (70%+)`, `EXPLORE (50%+)`.
- User alert drawers and unread notification badges.

### 5. Verified Opportunity Notifications & Live Dynamic Ticker
- Real-time comparison between server clock (IST) and verified deadlines (`start_datetime`, `end_datetime`).
- Status indicators: `LIVE`, `OPEN`, `CLOSING SOON` ( $\le 5$ days left), `RESULT`, `UPCOMING`, `CLOSED`.
- Direct links to official `.gov.in`, `.nic.in`, and conducting body application portals.

### 6. AI Career Guide (Dual-Engine Architecture)
- **Primary Cloud Engine**: Google Gemini API (`gemini-1.5-flash` / `gemini-pro`) with grounded system prompts enforcing Indian educational frameworks.
- **Offline Fallback Engine**: Comprehensive rule-based knowledge engine providing deterministic answers even when offline or without an API key.

### 7. Multilingual Localization & Accessibility
- Complete localization in **English**, **Telugu (తెలుగు)**, and **Hindi (हिन्दी)**.
- Dark / Light theme toggle with persistence in localStorage and database preferences.
- WCAG-compliant color contrast, keyboard navigation, and responsive layouts tested from 375px mobile viewports to 4K displays.

---

## 3. Technology Stack

- **Backend**: Python 3.10+, Flask 3.0+, Gunicorn 21.2+, Waitress 3.0+
- **Security & Crypto**: Argon2id (`argon2-cffi`), HttpOnly cookies, CSRF mitigation
- **Database**:
  - Cloud Production: PostgreSQL (via `psycopg2-binary`)
  - Local / Self-Hosted: SQLite 3 with Write-Ahead Logging (`WAL` mode) and foreign keys enabled
- **Frontend**: Vanilla JavaScript (ES6+), Modern Semantic HTML5, Vanilla CSS3 (Custom Design System, Flexbox, CSS Grid)
- **Icons**: Lucide Icons
- **Push & Communications**: Web Push API (`pywebpush`, VAPID, Service Worker `sw.js`), SMTP Email Service
- **Testing**: Python `unittest`, headless browser automation via Chrome DevTools Protocol (CDP)

---

## 4. Project Directory Structure

```
career-compass/
├── .env.example                 # Example environment variables (secrets excluded)
├── .gitignore                   # Git exclusion rules
├── Dockerfile                   # Docker container build definition
├── Procfile                     # Web process definition for Render / Heroku
├── README.md                    # Comprehensive technical documentation
├── requirements.txt             # Python dependencies
├── wsgi.py                      # WSGI entry point for production servers
├── app.py                       # Main Flask web application & REST APIs
├── auth.py                      # Authentication blueprint & session management
├── database.py                  # Dual-dialect database engine (PostgreSQL + SQLite)
├── db_repository.py             # Data access repositories (ACID relational operations)
├── ai_engine.py                 # AI Career Guide (Gemini API + Rule-Based Engine)
├── run_waitress.py              # Production WSGI runner for Windows/Linux
├── run_pipeline.py              # Automated data ingestion & change-detector runner
│
├── data/                        # Verified JSON datasets & SQLite storage
│   ├── btech_post_grad_pathways.json
│   ├── career_paths.json
│   ├── career_paths_10th.json
│   ├── career_compass.db        # SQLite database file (WAL mode)
│   ├── colleges_cutoffs.json
│   ├── companies_directory.json
│   ├── defence_entries.json
│   ├── digital_library.json
│   ├── entrance_exams.json
│   ├── exam_preparation.json
│   ├── govt_engineering.json
│   ├── learning_resources.json  # Preparation Hub verified resources
│   ├── notifications.json       # Master verified opportunities & deadlines
│   ├── official_links.json      # Official conducting bodies & portals
│   ├── options.json             # Qualifications, branches, and statuses
│   ├── source_registry.json     # Scraping registry for government portals
│   └── vapid_keys.json          # Web Push VAPID configuration
│
├── data_updater/                # Automated verification & update pipeline
│   ├── backup.py                # Automated dataset backup manager
│   ├── change_detector.py       # Notification delta detection engine
│   ├── registry.py              # Portal registry metadata
│   ├── updater.py               # Orchestration & update sync
│   ├── validator.py             # Schema & integrity validation
│   └── sources/                 # Scraping adapters for official portals
│       ├── ap_eapcet.py
│       ├── ap_ecet.py
│       ├── ap_polycet.py
│       ├── defence.py
│       ├── gate.py
│       ├── nta.py
│       ├── rrb.py
│       └── upsc.py
│
├── radar/                       # My Career Radar matching subsystem
│   ├── dispatcher.py            # Notification delivery dispatcher
│   ├── matcher.py               # Branch family & qualification matching logic
│   ├── models.py                # StudentProfile & Opportunity domain models
│   └── storage.py               # Profile persistence & retrieval
│
├── services/                    # Background infrastructure services
│   ├── email_service.py         # SMTP email dispatcher (welcome, alerts, resets)
│   ├── pipeline_service.py      # Scheduled verification pipeline runner
│   └── push_service.py          # Web Push notification dispatcher
│
├── templates/
│   └── index.html               # Main SPA HTML structure & all modular views
│
├── static/
│   ├── sw.js                    # Service Worker for browser push notifications
│   ├── css/
│   │   └── styles.css           # Complete responsive CSS design system
│   ├── js/
│   │   ├── app.js               # Application state, SPA router, API handlers
│   │   └── locales.js           # Inline multilingual dictionary
│   └── locales/
│       ├── en.json              # English language strings
│       ├── hi.json              # Hindi translations
│       └── te.json              # Telugu translations
│
└── tests/ (Automated test suites)
    ├── test_auth_persistence.py           # 16-point auth & persistence test suite
    ├── test_production_system.py          # 7-point core production test suite
    ├── test_preparation_hub.py            # 17-point Preparation Hub test suite
    ├── test_login_flow.py                 # 10-point browser login flow test suite
    ├── test_radar.py                      # Radar matcher & profile test suite
    ├── test_localization.py               # Multilingual translation test suite
    └── test_ai_profiles.py                # Qualification-aware AI prompt test suite
```

---

## 5. Installation & Setup

### Prerequisites
- Python 3.10, 3.11, or 3.12
- Git
- (Optional) PostgreSQL 14+ for production deployments

### Step 1: Clone the Repository
```bash
git clone https://github.com/lahari-1306/career-compass.git
cd career-compass
```

### Step 2: Create and Activate a Virtual Environment
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

---

## 6. Environment Variables

Create a `.env` file in the root directory by copying `.env.example`:

```bash
cp .env.example .env
```

| Variable | Description | Default | Example |
| :--- | :--- | :--- | :--- |
| `DATABASE_URL` | PostgreSQL connection URI. If provided, Career Compass automatically uses PostgreSQL. | *None* | `postgresql://user:password@host:5432/dbname` |
| `DATABASE_PATH` | Path to persistent SQLite database when `DATABASE_URL` is unset. | `data/career_compass.db` | `/var/data/career_compass.db` |
| `DATA_DIR` | Directory containing verified JSON files. | `data` | `data` |
| `SECRET_KEY` | Flask session cryptographic secret key. | *Built-in fallback* | `your-secure-random-secret-key` |
| `PORT` | HTTP port for server to listen on. | `5000` | `5000` |
| `FLASK_ENV` | Application environment mode (`development` or `production`). | `production` | `production` |
| `GEMINI_API_KEY` | Google Gemini API key for live AI Career Guide. | *None (uses offline engine)* | `AIzaSy...` |
| `SMTP_HOST` | Outgoing SMTP host for email delivery (Gmail, Brevo, SendGrid, Resend). | *None* | `smtp.gmail.com` |
| `SMTP_PORT` | SMTP port (587 for TLS, 465 for SSL). | `587` | `587` |
| `SMTP_USERNAME` | SMTP account username or API email. | *None* | `your-email@gmail.com` |
| `SMTP_PASSWORD` | SMTP password or Google App Password (16 chars). | *None* | `abcd efgh ijkl mnop` |
| `MAIL_FROM` | Sender display name and email address. | `CareerCompass <noreply@careercompass.org>` | `"CareerCompass <your-email@gmail.com>"` |
| `MAIL_USE_TLS` | Enable STARTTLS encryption. | `true` | `true` |
| `APP_BASE_URL` | Base application URL for generating reset links. Auto-detected on Render. | `https://career-compass.onrender.com` | `https://career-compass.onrender.com` |

---

## 7. Database Architecture & Setup

Career Compass uses a unified database layer in `database.py` with support for both **PostgreSQL** and **SQLite**:

### 1. PostgreSQL (Recommended for Production / Render / Cloud)
- When `DATABASE_URL` is set, the application connects via `psycopg2`.
- Automatically maps parameter markers (`?` $\rightarrow$ `%s`).
- Handles `cursor.lastrowid` using PostgreSQL `RETURNING id`.
- All 15 relational tables and indexes are automatically created on application boot.

### 2. SQLite (Default for Local Development & Persistent Disks)
- Enabled by default when `DATABASE_URL` is omitted.
- Uses Write-Ahead Logging (`PRAGMA journal_mode = WAL;`) for high concurrency.
- Enforces foreign key constraints (`PRAGMA foreign_keys = ON;`).
- Stores data persistently at `DATABASE_PATH` (default: `data/career_compass.db`).

### Schema Tables:
1. `users` (id, email, password_hash, name, role, is_verified, created_at, updated_at, last_login_at)
2. `user_profiles` (id, user_id, qualification, current_status, stream, branch, home_state, dream_goal, is_onboarded, ...)
3. `user_preferences` (id, user_id, theme, preferred_language, email_notifications_enabled, push_notifications_enabled, ...)
4. `user_sessions` (id, session_token, user_id, ip_address, user_agent, created_at, expires_at, is_active)
5. `password_reset_tokens` (id, user_id, token, created_at, expires_at, used_at)
6. `email_verifications` (id, user_id, token, created_at, expires_at, verified_at)
7. `notification_preferences` (id, user_id, new_opportunities, deadlines, admit_cards, results, counselling, ...)
8. `notifications` (id, title, category, organization, status, start_datetime, end_datetime, official_source, ...)
9. `notification_deliveries` (id, user_id, notification_id, channel, status, title, message, is_read, ...)
10. `push_subscriptions` (id, user_id, endpoint, p256dh_key, auth_key, user_agent, device_label, is_active, ...)
11. `saved_opportunities` (id, user_id, opportunity_id, title, category, deadline, official_url, notes, saved_at)
12. `exam_progress` (id, user_id, exam_id, preparation_stage, target_year, completed_topics, notes, updated_at)
13. `study_plans` (id, user_id, exam_id, plan_duration, custom_schedule, created_at, updated_at)
14. `ai_conversations` (id, user_id, title, messages, created_at, updated_at)
15. `learning_resources` (id, name, description, official_url, logo_url, category, resource_type, access_type, ...)

---

## 8. How to Run Locally

### Running the Backend & Web Application:

#### Option A: Direct Flask Runner (Recommended for Development)
```bash
python app.py
```
Server starts on `http://127.0.0.1:5000`.

#### Option B: Production WSGI Runner (Waitress)
```bash
python run_waitress.py
```

#### Option C: Production Gunicorn Runner (Linux / macOS)
```bash
gunicorn wsgi:app --bind 0.0.0.0:5000 --workers 2
```

Open your browser at `http://127.0.0.1:5000`.

---

## 9. How AI Career Guide Works

The AI Career Guide (`ai_engine.py`) operates through a hybrid dual-engine architecture:

1. **Qualification Grounding**:
   When an authenticated student chats with the AI, their profile (educational stage, stream, branch, home state, dream goal) is automatically injected into the system prompt.
   *Example*: A 10th standard student asking about careers receives age-appropriate guidance on Intermediate streams, Diploma options, and NDA entry, with engineering branch jargon filtered out.

2. **Live Verified Knowledge Injection**:
   The engine reads live data from `notifications.json`, `entrance_exams.json`, and `learning_resources.json` to ground answers in verified conducting bodies (NTA, UPSC, IITs) and real deadlines.

3. **Cloud & Offline Seamless Transition**:
   - If `GEMINI_API_KEY` is provided, requests route to Google Gemini models.
   - If `GEMINI_API_KEY` is missing or the network is unavailable, the built-in Rule-Based Knowledge Engine answers instantly with zero errors.

---

## 10. How My Career Radar Works

My Career Radar (`radar/`) delivers personalized opportunity recommendations:

1. **Profile Ingestion**: Ingests student attributes (stage, branch, home state, completion status).
2. **Branch Family Normalization**: Maps 33 specialized branches into standard engineering families (Computer Science & IT, Electronics & Communication, Mechanical & Automobile, Civil & Infrastructure, Electrical, Chemical & Materials).
3. **Multi-Factor Scoring**:
   - Educational stage alignment (40 points)
   - Branch / stream alignment (30 points)
   - Completion status eligibility (20 points)
   - Home state / domicile reservation eligibility (10 points)
4. **Alert Generation**: Opportunities scoring $\ge 50\%$ are matched and stored in `notification_deliveries` and displayed with custom match badges.

---

## 11. How the Preparation Hub Works

The Preparation Hub (`data/learning_resources.json` + `templates/index.html` + `static/js/app.js`):

- Provides curated, verified free learning resources mapped to:
  - **Education Levels**: `10th`, `Intermediate`, `Diploma`, `B.Tech`, `Degree`, `Postgraduate`
  - **Streams & Branches**: `CSE`, `ECE`, `Mechanical`, `Civil`, `BiPC`, `MPC`, etc.
  - **Exams**: `GATE`, `JEE Main`, `JEE Advanced`, `UGC NET`, `NEET`, `SSC JE`, `RRB JE`
  - **Skill Focus**: Data Structures & Algorithms, Competitive Programming, Core Engineering, Verbal Ability, Quantitative Aptitude.
- Features categorized views:
  - *National Learning Initiatives*: SWAYAM, NPTEL, Virtual Labs, Diksha, NDLI
  - *Coding & Technical Practice*: LeetCode, HackerRank, GeeksforGeeks
  - *STEM & Virtual Experimentation*: Virtual Labs (Ministry of Education)
  - *Mock Tests & PYQs*: NTA Abhyas, Gateforum, Official Question Banks

---

## 12. How Real-Time Notifications Work

Notifications (`data/notifications.json` + `database.py`):

1. **Time-Aware Evaluation**:
   Each notification defines `start_datetime` and `end_datetime` in ISO format. The server evaluates:
   - Current time $<$ Start: `UPCOMING`
   - Current time $>$ End: `CLOSED`
   - Difference $\le 5$ days: `CLOSING_SOON`
   - Active results: `RESULT`
   - Normal open window: `OPEN`
2. **Dynamic Dashboard Ticker**:
   Only active notifications (`OPEN`, `CLOSING_SOON`, `LIVE`, `RESULT`) appear on the ticker and home banner. Expired notifications are automatically archived.

---

## 13. How Verified Data Updates Work

The automated update subsystem (`data_updater/`):

- **`SourceRegistry`**: Maintains endpoints and update frequencies for official portals (UPSC, NTA, RRB, GATE, State CETs).
- **`ChangeDetector`**: Computes SHA-256 content hashes of portal responses to detect newly announced notifications without duplicate alerts.
- **`Validator`**: Verifies required fields, valid ISO timestamps, and HTTPS official URLs before publishing.
- **`BackupManager`**: Automatically creates timestamped JSON backups in `data/backups/` before any dataset write.
- **CLI Trigger**:
  ```bash
  python run_pipeline.py
  ```

---

## 14. Email & Browser Push Notifications

### Email Service (`services/email_service.py`)
- Dispatches transactional emails for:
  - Welcome & registration confirmation
  - Urgent deadline reminders (closing in 48 hours)
  - Password reset links (2-hour secure token expiry)
- Automatically switches to safe mock mode (logging to `data/email_logs.json`) when SMTP credentials are not configured.

### Browser Push Notifications (`services/push_service.py` + `static/sw.js`)
- Standard Web Push implementation using VAPID keys (`data/vapid_keys.json`).
- Service Worker (`static/sw.js`) listens for push events and displays native operating system notifications with deep links to matching opportunities.

---

## 15. How to Deploy to Render

Career Compass is fully pre-configured for one-click deployment on Render:

### Step 1: Create a PostgreSQL Database on Render
1. Go to the [Render Dashboard](https://dashboard.render.com).
2. Click **New +** $\rightarrow$ **PostgreSQL**.
3. Name your database (e.g. `career-compass-db`) and create it.
4. Copy the **Internal Database URL** (or External URL).

### Step 2: Create a Web Service on Render
1. Click **New +** $\rightarrow$ **Web Service**.
2. Connect your GitHub repository (`lahari-1306/career-compass`).
3. Set the following settings:
   - **Environment**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn wsgi:app --bind 0.0.0.0:$PORT`
4. Add the following **Environment Variables**:
   - `DATABASE_URL`: Paste the PostgreSQL connection URL from Step 1.
   - `SECRET_KEY`: Enter a random 32-character secret key.
   - `FLASK_ENV`: `production`
   - `GEMINI_API_KEY`: *(Optional)* Your Google Gemini API key.
   - `SMTP_HOST`: *(Optional for live email delivery)* e.g. `smtp.gmail.com` or `smtp-relay.brevo.com`
   - `SMTP_PORT`: `587`
   - `SMTP_USERNAME`: Your email or provider login
   - `SMTP_PASSWORD`: Your 16-character App Password or API Key
   - `MAIL_FROM`: `"CareerCompass <your-email@gmail.com>"`
   *(Note: If SMTP is omitted, password reset tokens are logged to `data/email_logs.json` and rendered directly on-screen with an instant reset button, ensuring users are never blocked).*
5. Click **Create Web Service**.

Render will install dependencies, connect to PostgreSQL, automatically build all database tables and seed verified resources, and launch the website.

---

## 16. Adding & Updating Official Resources

### Adding a Learning Resource:
Append a JSON entry to `data/learning_resources.json`:
```json
{
  "id": "UNIQUE_RESOURCE_ID",
  "name": "Resource Name",
  "description": "Comprehensive description of features and syllabus coverage.",
  "official_url": "https://official-website.gov.in",
  "logo_url": "",
  "category": "Practice & Training",
  "resource_type": "Practice & Learning Platform",
  "education_levels": ["B.Tech", "Degree"],
  "streams": ["Engineering", "Computer Science"],
  "branches": ["CSE", "IT", "ECE"],
  "skills": ["Algorithms", "Data Structures"],
  "exams": ["GATE"],
  "access_type": "FREE",
  "free_features": "Full access to practice problem sets and video modules.",
  "paid_features": "",
  "language": "English",
  "official_source": "Ministry of Education, Govt of India",
  "verification_status": "VERIFIED"
}
```

### Adding a Verified Notification:
Append a JSON entry to `data/notifications.json`:
```json
{
  "id": "NOTIF_2026_EXAM_01",
  "title": "National Exam 2026 Official Registration",
  "category": "Engineering",
  "organization": "National Testing Agency (NTA)",
  "status": "OPEN",
  "start_datetime": "2026-09-01T00:00:00+05:30",
  "end_datetime": "2026-10-31T23:59:59+05:30",
  "exam_date": "2026-11-20",
  "result_date": "2026-12-15",
  "eligibility_summary": "Passed Class 12 / Intermediate with Physics, Mathematics, Chemistry.",
  "official_source": "https://nta.ac.in",
  "official_application_url": "https://exams.nta.ac.in",
  "priority": "HIGH",
  "description": "Official notification for all eligible Indian candidates.",
  "target_qualifications": ["Intermediate"],
  "target_branches": ["MPC"],
  "target_states": ["All India"]
}
```

---

## 17. Running Automated Tests

Run the complete test suite locally to verify authentication, database persistence, Preparation Hub, and UI flows:

```bash
# 1. 16-Point Authentication & Persistence Verification Suite
python test_auth_persistence.py

# 2. Preparation Hub 17-Point Verification Suite
python test_preparation_hub.py

# 3. Core Production System Suite (Argon2id, Rate Limiter, Radar Matcher)
python test_production_system.py

# 4. End-to-End Headless Browser Login Flow Suite
python test_login_flow.py

# 5. Multilingual Localization Suite
python test_localization.py
```

All suites run with zero external dependencies and report 100% pass status.
