/**
 * CareerCompass - FIND YOUR TRUE NORTH
 * Production Client Application Controller
 */

// ==========================================
// 1. STATE & DATA REPOSITORY
// ==========================================
const AppState = {
  currentSection: 'home',
  navHistory: ['home'],
  currentLang: localStorage.getItem('cc_lang') || 'en',
  theme: localStorage.getItem('cc_theme') || 'light',
  datasets: {
    notifications: [],
    careerPaths: {},
    defenceEntries: [],
    govtJobs: [],
    entranceExams: [],
    colleges: [],
    cutoffs: [],
    scholarships: [],
    digitalLibrary: [],
    officialLinks: []
  },
  savedRoadmaps: JSON.parse(localStorage.getItem('cc_roadmaps') || '[]'),
  btechState: {
    mode: 'completed', // 'completed' or 'aspirant'
    branch: 'CSE',
    activePathway: 'job',
    jobCategory: 'all',
    companyType: 'all',
    jobSearch: '',
    selectedRoleId: null
  },
  activeFilters: {
    examCategory: 'All',
    examSearch: '',
    defenceLevel: 'All',
    cutoffSearch: '',
    notifCategory: 'All',
    notifSearch: '',
    librarySearch: '',
    options: {}
  }
};

// ==========================================
// CENTRALIZED OPTIONS CONSTANT (Branches, States, Status, Interests)
// ==========================================
const APP_OPTIONS = {
  btech_branches: [
    "CSE",
    "Information Technology (IT)",
    "ECE",
    "EEE",
    "Mechanical Engineering",
    "Civil Engineering",
    "Chemical Engineering",
    "Biotechnology",
    "Biomedical Engineering",
    "Aerospace / Aeronautical Engineering",
    "Automobile Engineering",
    "Instrumentation & Control",
    "Mechatronics",
    "Robotics",
    "Artificial Intelligence / AI",
    "AI & ML",
    "Data Science",
    "Cyber Security",
    "IoT",
    "CSE (AI)",
    "CSE (Data Science)",
    "CSE (Cyber Security)",
    "Electronics & Instrumentation",
    "Production Engineering",
    "Industrial Engineering",
    "Metallurgical Engineering",
    "Mining Engineering",
    "Petroleum Engineering",
    "Textile Engineering",
    "Agricultural Engineering",
    "Food Technology",
    "Environmental Engineering",
    "Other"
  ],
  branches_by_qual: {
    "B.Tech": [
      "CSE", "Information Technology (IT)", "ECE", "EEE", "Mechanical Engineering", "Civil Engineering",
      "Chemical Engineering", "Biotechnology", "Biomedical Engineering", "Aerospace / Aeronautical Engineering",
      "Automobile Engineering", "Instrumentation & Control", "Mechatronics", "Robotics", "Artificial Intelligence / AI",
      "AI & ML", "Data Science", "Cyber Security", "IoT", "CSE (AI)", "CSE (Data Science)", "CSE (Cyber Security)",
      "Electronics & Instrumentation", "Production Engineering", "Industrial Engineering", "Metallurgical Engineering",
      "Mining Engineering", "Petroleum Engineering", "Textile Engineering", "Agricultural Engineering",
      "Food Technology", "Environmental Engineering", "Other"
    ],
    "Intermediate": ["MPC", "BiPC", "MEC", "CEC", "HEC", "Vocational", "Other"],
    "Diploma": ["CSE", "ECE", "EEE", "Mechanical", "Civil", "Automobile", "Chemical", "Mining", "Other"],
    "Degree": ["B.Sc Computer Science", "B.Sc Data Science", "B.Sc Mathematics", "B.Sc Physics/Chemistry", "B.Com", "BBA", "BCA", "BA", "Other"],
    "10th": ["General", "Science", "Mathematics", "IT"],
    "Postgraduate": ["M.Tech (CSE)", "M.Tech (VLSI)", "M.Tech (Mechanical)", "M.Tech (Civil)", "MBA", "MCA", "M.Sc", "Other"]
  },
  streams_by_qual: {
    "10th": ["General", "Science", "Mathematics", "IT"],
    "Intermediate": ["MPC", "BiPC", "CEC", "MEC", "HEC", "Vocational"],
    "Diploma": ["CSE", "Information Technology", "ECE", "EEE", "Mechanical Engineering", "Civil Engineering", "Chemical Engineering", "Automobile Engineering", "Commercial Practice", "Other"],
    "Degree": ["B.Sc Computer Science", "B.Sc Data Science", "B.Sc Mathematics", "B.Sc Physics/Chemistry", "B.Sc Life Sciences", "B.Com", "BBA", "BCA", "BA", "Other"],
    "B.Tech": [
      "CSE", "Information Technology (IT)", "ECE", "EEE", "Mechanical Engineering", "Civil Engineering",
      "Chemical Engineering", "Biotechnology", "Biomedical Engineering", "Aerospace / Aeronautical Engineering",
      "Automobile Engineering", "Instrumentation & Control", "Mechatronics", "Robotics", "Artificial Intelligence / AI",
      "AI & ML", "Data Science", "Cyber Security", "IoT", "CSE (AI)", "CSE (Data Science)", "CSE (Cyber Security)",
      "Electronics & Instrumentation", "Production Engineering", "Industrial Engineering", "Metallurgical Engineering",
      "Mining Engineering", "Petroleum Engineering", "Textile Engineering", "Agricultural Engineering",
      "Food Technology", "Environmental Engineering", "Other"
    ],
    "Postgraduate": ["M.Tech (CSE)", "M.Tech (VLSI)", "M.Tech (Mechanical)", "M.Tech (Civil)", "MBA", "MCA", "M.Sc", "Other"]
  },
  preferred_career_directions_by_qual: {
    "10th": [
      "Intermediate (MPC / BiPC / CEC / MEC)",
      "Polytechnic Diploma (Engineering)",
      "ITI Trades",
      "Direct Government / Defence Exams (Agniveer, SSC GD)"
    ],
    "Intermediate": [
      "Engineering (B.Tech / B.E.)",
      "Medical & Allied Health Sciences (MBBS, BDS, B.Pharm, Nursing, Agri)",
      "Degree (B.Sc, B.Com, BBA, BA)",
      "Defence (NDA, TES)",
      "Law (CLAT / Integrated Law)",
      "CA / CMA / CS Foundation"
    ],
    "Intermediate_MPC": [
      "Engineering (B.Tech / B.E.)",
      "Architecture (B.Arch)",
      "Computer Science & IT Degrees",
      "Pure Sciences & Research (B.Sc / BS-MS)",
      "Defence Forces (NDA / TES Cadet)",
      "Government Competitive Exams",
      "Commercial Pilot / Aviation"
    ],
    "Intermediate_BiPC": [
      "Medicine & Surgery (MBBS)",
      "Dental Surgery (BDS)",
      "Pharmacy (B.Pharm / Pharm.D)",
      "B.Sc Agriculture & Horticulture",
      "Veterinary Science & Animal Husbandry",
      "Biotechnology & Bioinformatics",
      "Nursing & Allied Health Sciences",
      "Physiotherapy (BPT)"
    ],
    "Intermediate_CEC_MEC": [
      "Chartered Accountancy (CA / CMA / CS)",
      "Commerce & Finance (B.Com / B.Com Hons)",
      "Business Administration & Management (BBA / BMS)",
      "Economics & Statistics",
      "Law (5-Year Integrated BA LLB / BBA LLB)",
      "Banking & Insurance"
    ],
    "Intermediate_HEC": [
      "Civil Services & Public Administration",
      "Law (5-Year Integrated LLB)",
      "Journalism & Mass Communication",
      "Psychology & Social Work",
      "Literature & Humanities (BA)",
      "Teaching & Academia"
    ],
    "Diploma": [
      "Lateral Entry to B.Tech (ECET)",
      "Junior Engineer (JE) Government Exams",
      "Core Technical Industry Jobs",
      "NATS Apprenticeship",
      "Defence Technical Roles"
    ],
    "Degree": [
      "Post Graduation (M.Sc, M.Com, MA, MCA)",
      "MBA / Management",
      "Government Exams (UPSC CSE, SSC CGL, Banking)",
      "Corporate Private Sector Jobs",
      "Defence (CDS, AFCAT)"
    ],
    "B.Tech": [
      "Software / IT Industry",
      "Cyber Security",
      "Core Engineering Jobs",
      "Government Engineering Jobs (IES / ESE, State AE/AEE)",
      "PSUs via GATE",
      "Higher Studies (M.Tech via GATE)",
      "Higher Studies Abroad (MS via GRE/TOEFL)",
      "Management (MBA via CAT)",
      "Defence Technical Entry (TGC, SSC Tech, Navy)",
      "Startups & Entrepreneurship"
    ],
    "Postgraduate": [
      "Ph.D. / Research / Doctoral Fellowships",
      "University Teaching / Assistant Professor (UGC NET)",
      "Senior Corporate R&D / Lead Roles",
      "Government Scientist Roles (DRDO, ISRO, BARC)"
    ]
  },
  states: [
    "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh", "Goa", "Gujarat", "Haryana",
    "Himachal Pradesh", "Jharkhand", "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
    "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab", "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana",
    "Tripura", "Uttar Pradesh", "Uttarakhand", "West Bengal"
  ],
  union_territories: [
    "Andaman and Nicobar Islands", "Chandigarh", "Dadra and Nagar Haveli and Daman and Diu",
    "Delhi", "Jammu and Kashmir", "Ladakh", "Lakshadweep", "Puducherry"
  ],
  scopes: ["All India / National"],
  completion_years: ["2030", "2029", "2028", "2027", "2026", "2025", "2024", "2023", "2022", "2021", "2020", "2019", "2018"],
  completion_statuses: ["Currently Studying", "Final Year", "Completed"]
};
window.APP_OPTIONS = APP_OPTIONS;
AppState.options = APP_OPTIONS;

// ==========================================
// 2. MULTI-LANGUAGE TRANSLATIONS & DICTIONARY
// ==========================================

const DYNAMIC_DICTIONARY = {
  te: {
    // Categories & Streams
    'Engineering': 'ఇంజనీరింగ్',
    'Medical': 'వైద్య రంగం',
    'State Entrance': 'రాష్ట్ర ప్రవేశ పరీక్షలు',
    'Lateral Entry': 'లేటరల్ ఎంట్రీ',
    'Management': 'మేనేజ్‌మెంట్',
    'Law': 'లా (న్యాయశాస్త్రం)',
    'Defence': 'రక్షణ సేవలు',
    'All Categories': 'అన్ని విభాగాలు',
    'All Streams': 'అన్ని రంగాలు',
    'All Defence Entries': 'అన్ని రక్షణ ప్రవేశాలు',
    'After 12th (NDA & 10+2 Cadet)': '12వ తరగతి తర్వాత (NDA & 10+2 క్యాడెట్)',
    'After Graduation (CDS & AFCAT)': 'గ్రాడ్యుయేషన్ తర్వాత (CDS & AFCAT)',
    'Engineering Direct SSB (TGC, SSC Tech)': 'ఇంజనీరింగ్ డైరెక్ట్ SSB (TGC, SSC Tech)',
    'Agniveer Soldier Routes': 'అగ్నివీర్ సైనిక మార్గాలు',
    'Govt Service': 'ప్రభుత్వ సేవ',
    'Verified Scheme': 'ధృవీకరించబడిన పథకం',
    // Status
    'OPEN': 'దరఖాస్తులు ప్రారంభం (OPEN)',
    'LIVE': 'కౌన్సెలింగ్ లైవ్ (LIVE)',
    'CLOSING_SOON': 'గడువు ముగుస్తోంది (CLOSING SOON)',
    'UPCOMING': 'త్వరలో రాబోయేది (UPCOMING)',
    'RESULT': 'ఫలితాలు విడుదల (RESULT)',
    'CLOSED': 'ముగిసింది (CLOSED)',
    'ARCHIVED': 'ఆర్కైవ్ చేయబడింది',
    'VERIFIED_ACTIVE': 'ధృవీకరించబడింది & సక్రియం',
    // Common terms
    'Closes Today': 'ఈరోజే చివరి తేదీ',
    'Days Left': 'రోజులు మిగిలి ఉన్నాయి',
    'Active Cycle': 'సక్రియ సైకిల్',
    'Admissions LIVE': 'ప్రవేశాలు లైవ్',
    'Scheduled': 'నిర్దేశిత తేదీ',
    'Announced': 'ప్రకటించబడింది',
    'See Brochure': 'బ్రోచర్ చూడండి'
  },
  hi: {
    // Categories & Streams
    'Engineering': 'इंजीनियरिंग',
    'Medical': 'चिकित्सा (Medical)',
    'State Entrance': 'राज्य प्रवेश परीक्षाएं',
    'Lateral Entry': 'लेटरल एंट्री',
    'Management': 'प्रबंधन (Management)',
    'Law': 'विधि (Law)',
    'Defence': 'रक्षा सेवाएं',
    'All Categories': 'सभी श्रेणियां',
    'All Streams': 'सभी वर्ग',
    'All Defence Entries': 'सभी रक्षा प्रविष्टियां',
    'After 12th (NDA & 10+2 Cadet)': '12वीं के बाद (NDA & 10+2 कैडेट)',
    'After Graduation (CDS & AFCAT)': 'स्नातक के बाद (CDS & AFCAT)',
    'Engineering Direct SSB (TGC, SSC Tech)': 'इंजीनियरिंग डायरेक्ट SSB (TGC, SSC Tech)',
    'Agniveer Soldier Routes': 'अग्निविर सैनिक मार्ग',
    'Govt Service': 'सरकारी सेवा',
    'Verified Scheme': 'सत्यापित योजना',
    // Status
    'OPEN': 'आवेदन शुरू (OPEN)',
    'LIVE': 'काउंसलिंग जारी (LIVE)',
    'CLOSING_SOON': 'शीघ्र समाप्त (CLOSING SOON)',
    'UPCOMING': 'आगामी (UPCOMING)',
    'RESULT': 'परिणाम घोषित (RESULT)',
    'CLOSED': 'समाप्त (CLOSED)',
    'ARCHIVED': 'अभिलेखागार (Archived)',
    'VERIFIED_ACTIVE': 'सत्यापित एवं सक्रिय',
    // Common terms
    'Closes Today': 'आज अंतिम तिथि',
    'Days Left': 'दिन शेष',
    'Active Cycle': 'सक्रिय चक्र',
    'Admissions LIVE': 'प्रवेश जारी',
    'Scheduled': 'निर्धारित तिथि',
    'Announced': 'घोषित',
    'See Brochure': 'विवरणिका देखें'
  }
};

function t(key, fallback = '') {
  if (!key) return fallback;
  const lang = AppState.currentLang || 'en';
  const dict = (window.LOCALES && window.LOCALES[lang]) || (window.LOCALES && window.LOCALES['en']) || {};
  
  // 1. Direct property lookup
  if (dict[key] !== undefined) return dict[key];

  // 2. Dotted property lookup
  const parts = key.split('.');
  let curr = dict;
  let found = true;
  for (const part of parts) {
    if (curr && typeof curr === 'object' && part in curr) {
      curr = curr[part];
    } else {
      found = false;
      break;
    }
  }
  if (found && curr !== undefined && curr !== null) return curr;

  // 3. Fallback to English dictionary if current language was not English
  if (lang !== 'en' && window.LOCALES && window.LOCALES['en']) {
    let enCurr = window.LOCALES['en'];
    let enFound = true;
    for (const part of parts) {
      if (enCurr && typeof enCurr === 'object' && part in enCurr) {
        enCurr = enCurr[part];
      } else {
        enFound = false;
        break;
      }
    }
    if (enFound && enCurr !== undefined && enCurr !== null) return enCurr;
  }

  // 4. Underscore to dot conversion fallback (e.g. nav_home -> nav.home)
  if (key.includes('_')) {
    const dotKey = key.replace('_', '.');
    return t(dotKey, fallback);
  }

  return fallback || key;
}

function translateDynamic(text) {
  if (!text) return '';
  const lang = AppState.currentLang || 'en';
  if (lang === 'en') return text;
  const map = DYNAMIC_DICTIONARY[lang];
  if (map && map[text]) return map[text];
  return text;
}

// Re-render the active module to reflect newly selected language on all cards
function renderCurrentSection() {
  if (AppState.currentSection === 'career-paths') {
    const activeTab = document.querySelector('.tab-pill.active')?.getAttribute('data-tab') || '10th';
    renderCareerPaths(activeTab);
  } else if (AppState.currentSection === 'entrance-exams') {
    renderEntranceExams();
  } else if (AppState.currentSection === 'govt-jobs') {
    renderGovtEngineering();
  } else if (AppState.currentSection === 'defence') {
    renderDefenceEntries();
  } else if (AppState.currentSection === 'colleges') {
    renderColleges();
  } else if (AppState.currentSection === 'cutoffs') {
    renderCutoffs();
  } else if (AppState.currentSection === 'scholarships') {
    renderScholarships();
  } else if (AppState.currentSection === 'digital-library') {
    renderDigitalLibrary();
  } else if (AppState.currentSection === 'official-links') {
    renderOfficialLinks();
  } else if (AppState.currentSection === 'notifications') {
    renderNotificationsCenter();
  } else if (AppState.currentSection === 'saved-roadmaps') {
    renderSavedRoadmaps();
  }
  if (AppState.currentSection === 'home') {
    refreshRadarMatches();
  }
}

// ==========================================
// 3. INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  try { initTheme(); } catch (e) { console.error('Theme init error:', e); }
  try { initLanguage(); } catch (e) { console.error('Language init error:', e); }
  try { initTicker(); } catch (e) { console.error('Ticker init error:', e); }
  try { loadAllDatasets(); } catch (e) { console.error('Datasets load error:', e); }
  try { renderSavedRoadmaps(); } catch (e) { console.error('Saved roadmaps error:', e); }
  try { initCareerRadar(); } catch (e) { console.error('Radar init error:', e); }
  try { checkAuthStatus(); } catch (e) { console.error('Auth status error:', e); }
  try {
    const urlParams = new URLSearchParams(window.location.search);
    const resetToken = urlParams.get('reset_token') || urlParams.get('token');
    if (resetToken) {
      showAuthView('reset');
      const resetTokenInput = document.getElementById('auth-reset-token');
      if (resetTokenInput) resetTokenInput.value = resetToken;
      verifyResetToken(resetToken);
    }
  } catch (e) { console.error('Reset token check error:', e); }
  try { checkPushBanner(); } catch (e) { console.error('Push banner error:', e); }
  try { refreshIcons(); } catch (e) { console.error('Icons refresh error:', e); }

  // Close menus on outside click
  try {
    document.addEventListener('click', (e) => {
      try {
        const authLangBtn = document.getElementById('auth-lang-btn');
        const authLangMenu = document.getElementById('auth-lang-menu');
        if (authLangMenu && !authLangMenu.contains(e.target) && !authLangBtn?.contains(e.target)) {
          authLangMenu.classList.add('hidden');
        }
        const langBtn = document.getElementById('lang-btn');
        const langMenu = document.getElementById('lang-menu');
        if (langMenu && !langMenu.contains(e.target) && !langBtn?.contains(e.target)) {
          langMenu.classList.add('hidden');
        }
        const bellBtn = document.getElementById('radar-bell-btn');
        const bellDrawer = document.getElementById('radar-alerts-drawer');
        if (bellDrawer && !bellDrawer.contains(e.target) && !bellBtn?.contains(e.target)) {
          bellDrawer.classList.add('hidden');
        }
        const userChipBtn = document.getElementById('user-chip-btn');
        const userDropdown = document.getElementById('user-dropdown-panel');
        if (userDropdown && !userDropdown.contains(e.target) && !userChipBtn?.contains(e.target)) {
          userDropdown.classList.add('hidden');
        }
      } catch (err) {
        console.warn('Click outside handler error:', err);
      }
    });
  } catch (e) {
    console.error('Menu click listener error:', e);
  }
});

function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Theme Handling
function toggleTheme() {
  AppState.theme = AppState.theme === 'light' ? 'dark' : 'light';
  document.documentElement.setAttribute('data-theme', AppState.theme);
  localStorage.setItem('cc_theme', AppState.theme);
  if (currentUser) {
    fetch('/api/auth/preferences', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ theme: AppState.theme })
    }).catch(() => {});
  }
  refreshIcons();
}

function initTheme() {
  document.documentElement.setAttribute('data-theme', AppState.theme);
  const toggleBtn = document.getElementById('theme-toggle-btn');
  if (toggleBtn) {
    toggleBtn.removeEventListener('click', toggleTheme);
    toggleBtn.addEventListener('click', toggleTheme);
  }
  const authToggleBtn = document.getElementById('auth-theme-toggle-btn');
  if (authToggleBtn) {
    authToggleBtn.removeEventListener('click', toggleTheme);
    authToggleBtn.addEventListener('click', toggleTheme);
  }
}

// Language Handling
function initLanguage() {
  const langBtn = document.getElementById('lang-btn');
  const langMenu = document.getElementById('lang-menu');
  if (langBtn && langMenu) {
    langBtn.addEventListener('click', (e) => {
      e.stopPropagation();
      langMenu.classList.toggle('hidden');
    });
  }
  applyLanguage(AppState.currentLang);
}

function changeLanguage(langCode) {
  AppState.currentLang = langCode;
  localStorage.setItem('cc_lang', langCode);
  const langMenu = document.getElementById('lang-menu');
  if (langMenu) langMenu.classList.add('hidden');
  const authLangMenu = document.getElementById('auth-lang-menu');
  if (authLangMenu) authLangMenu.classList.add('hidden');
  applyLanguage(langCode);
}

function applyLanguage(langCode) {
  document.documentElement.setAttribute('lang', langCode);
  const langLabel = document.getElementById('current-lang-label');
  if (langLabel) langLabel.innerText = langCode.toUpperCase();
  const authLangLabel = document.getElementById('auth-current-lang-label');
  if (authLangLabel) authLangLabel.innerText = langCode.toUpperCase();

  // Update active dropdown items in both menus
  document.querySelectorAll('#lang-menu .dropdown-item, #auth-lang-menu .dropdown-item').forEach(item => {
    const onclickStr = item.getAttribute('onclick') || '';
    item.classList.toggle('active', onclickStr.includes(`'${langCode}'`));
  });

  // Apply static translations to all elements with data-i18n
  document.querySelectorAll('[data-i18n]').forEach(elem => {
    const key = elem.getAttribute('data-i18n');
    const translated = t(key);
    if (translated) {
      elem.innerHTML = translated;
    }
  });

  // Apply placeholders to inputs with data-i18n-placeholder
  document.querySelectorAll('[data-i18n-placeholder]').forEach(elem => {
    const key = elem.getAttribute('data-i18n-placeholder');
    const translated = t(key);
    if (translated) {
      elem.placeholder = translated;
    }
  });

  // Re-render active section cards to translate dynamic card labels and metadata
  renderCurrentSection();
  refreshIcons();
}

// Menu Toggle
function toggleMenu() {
  const megaMenu = document.getElementById('mega-menu');
  if (megaMenu) {
    megaMenu.classList.toggle('hidden');
    refreshIcons();
  }
}

document.getElementById('menu-toggle-btn')?.addEventListener('click', toggleMenu);

// Global User-Facing Toast & Retry Alerts
function showAppToast(message, type = 'info', retryCallback = null) {
  let toastContainer = document.getElementById('app-toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.id = 'app-toast-container';
    toastContainer.style.cssText = 'position: fixed; bottom: 20px; right: 20px; z-index: 99999; display: flex; flex-direction: column; gap: 8px; max-width: 360px;';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  const bg = type === 'error' ? '#ef4444' : (type === 'success' ? '#10b981' : '#3b82f6');
  toast.style.cssText = `background: ${bg}; color: white; padding: 12px 16px; border-radius: 8px; box-shadow: 0 4px 12px rgba(0,0,0,0.15); font-size: 0.88rem; display: flex; align-items: center; justify-content: space-between; gap: 10px; animation: slideIn 0.3s ease;`;

  const msgSpan = document.createElement('span');
  msgSpan.textContent = message;
  toast.appendChild(msgSpan);

  if (retryCallback && typeof retryCallback === 'function') {
    const retryBtn = document.createElement('button');
    retryBtn.textContent = 'Retry';
    retryBtn.style.cssText = 'background: rgba(255,255,255,0.25); border: none; color: white; font-weight: bold; padding: 4px 8px; border-radius: 4px; cursor: pointer; font-size: 0.8rem;';
    retryBtn.onclick = () => {
      toast.remove();
      retryCallback();
    };
    toast.appendChild(retryBtn);
  }

  const closeBtn = document.createElement('button');
  closeBtn.innerHTML = '&times;';
  closeBtn.style.cssText = 'background: transparent; border: none; color: white; font-size: 1.2rem; cursor: pointer; padding: 0 4px; line-height: 1;';
  closeBtn.onclick = () => toast.remove();
  toast.appendChild(closeBtn);

  toastContainer.appendChild(toast);
  setTimeout(() => {
    if (toast.parentNode) toast.remove();
  }, 6000);
}
window.showAppToast = showAppToast;

// ==========================================
// 4. LIVE NOTIFICATION TICKER
// ==========================================
async function initTicker() {
  const tickerBar = document.getElementById('ticker-bar');
  const track = document.getElementById('ticker-track');
  const pauseBtn = document.getElementById('ticker-pause-btn');

  try {
    const res = await fetch('/api/notifications');
    const data = await res.json();
    AppState.datasets.notifications = data.notifications || [];

    // Compact horizontal opportunity strip hides if no active verified events exist
    if (!AppState.datasets.notifications || AppState.datasets.notifications.length === 0) {
      if (tickerBar) tickerBar.style.display = 'none';
      return;
    } else {
      if (tickerBar) tickerBar.style.display = 'flex';
    }

    // Double the items for seamless infinite scroll
    const items = [...AppState.datasets.notifications, ...AppState.datasets.notifications];
    track.innerHTML = items.map((notif, idx) => {
      const statusText = notif.display_status || notif.dynamic_status || notif.status;
      const badgeClass = getBadgeClass(statusText);
      return `
        <span class="ticker-item" onclick="openNotifModal('${notif.id}')">
          <span class="badge ${badgeClass}">${escapeHtml(statusText)}</span>
          <strong>${escapeHtml(notif.title)}</strong> — ${escapeHtml(notif.organization)}
        </span>
      `;
    }).join('');

    if (pauseBtn) {
      pauseBtn.addEventListener('click', () => {
        track.classList.toggle('paused');
        const isPaused = track.classList.contains('paused');
        pauseBtn.innerHTML = isPaused ? '<i data-lucide="play" class="icon-sm"></i>' : '<i data-lucide="pause" class="icon-sm"></i>';
        refreshIcons();
      });
    }
  } catch (err) {
    if (track) {
      track.innerHTML = '<span class="ticker-item">Verified notification feed syncing. Please check official portals.</span>';
    }
  }
}

function getBadgeClass(status) {
  if (!status) return 'badge-primary';
  const s = String(status).toUpperCase();
  if (s.includes('LIVE') || s.includes('COUNSELLING')) return 'badge-danger';
  if (s.includes('OPEN') || s.includes('ONGOING')) return 'badge-success';
  if (s.includes('CLOSING') || s.includes('DEADLINE') || s.includes('EXAM SOON')) return 'badge-warning';
  if (s.includes('UPCOMING')) return 'badge-info';
  if (s.includes('RESULT')) return 'badge-primary';
  if (s.includes('CLOSED') || s.includes('ARCHIVED')) return 'badge-secondary';
  return 'badge-primary';
}


// ==========================================
// 5. NAVIGATION CONTROLLER
// ==========================================
function navigateToSection(sectionId) {
  if (sectionId === 'radar') {
    // Navigate to home and smoothly scroll to Career Radar feed
    AppState.navHistory.push('radar');
    AppState.currentSection = 'home';
    document.querySelectorAll('.page-section').forEach(sec => sec.classList.remove('active'));
    document.getElementById('section-home')?.classList.add('active');
    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.toggle('active', link.getAttribute('data-section') === 'radar');
    });
    document.getElementById('breadcrumb-bar')?.classList.add('hidden');
    setTimeout(() => {
      const radarFeed = document.getElementById('radar-feed-container') || document.querySelector('.radar-feed-box');
      if (radarFeed) radarFeed.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }, 150);
    refreshIcons();
    return;
  }

  if (AppState.currentSection === sectionId) return;

  // Add to navigation history stack
  AppState.navHistory.push(sectionId);
  AppState.currentSection = sectionId;

  // Update Section Visibility
  document.querySelectorAll('.page-section').forEach(sec => sec.classList.remove('active'));
  const targetSec = document.getElementById(`section-${sectionId}`);
  if (targetSec) {
    targetSec.classList.add('active');
  }

  // Update Header Nav Links
  document.querySelectorAll('.nav-link').forEach(link => {
    link.classList.toggle('active', link.getAttribute('data-section') === sectionId);
  });

  // Manage Breadcrumb Bar
  const breadcrumbBar = document.getElementById('breadcrumb-bar');
  const breadcrumbTitle = document.getElementById('breadcrumb-title');
  if (sectionId === 'home') {
    breadcrumbBar.classList.add('hidden');
  } else {
    breadcrumbBar.classList.remove('hidden');
    const readableTitles = {
      'career-paths': 'Find My Career Path',
      'entrance-exams': 'Entrance Exams Database',
      'exam-prep': 'Preparation Hub',
      'radar': 'Career Radar',
      'govt-jobs': 'Government Exams for Engineers',
      'defence': 'Defence Forces Roadmaps',
      'colleges': 'Colleges & Courses Explorer',
      'cutoffs': 'Counselling & Historical Cutoffs',
      'scholarships': 'Verified Scholarships',
      'digital-library': 'Legal Digital Library & Resources',
      'ai-guide': 'AI Assistant',
      'notifications': 'Notifications',
      'saved-roadmaps': 'My Saved Roadmaps',
      'official-links': 'Verified Official Portals Directory',
      'about': 'About CareerCompass'
    };
    breadcrumbTitle.innerText = readableTitles[sectionId] || sectionId;
  }

  if (sectionId === 'exam-prep') {
    initPreparationHub();
  }

  // Scroll to top
  window.scrollTo({ top: 0, behavior: 'smooth' });
  refreshIcons();
}

function navigateBack() {
  if (AppState.navHistory.length > 1) {
    AppState.navHistory.pop(); // Remove current
    const previous = AppState.navHistory[AppState.navHistory.length - 1] || 'home';
    AppState.currentSection = previous;

    document.querySelectorAll('.page-section').forEach(sec => sec.classList.remove('active'));
    document.getElementById(`section-${previous}`)?.classList.add('active');

    document.querySelectorAll('.nav-link').forEach(link => {
      link.classList.toggle('active', link.getAttribute('data-section') === previous);
    });

    const breadcrumbBar = document.getElementById('breadcrumb-bar');
    if (previous === 'home') {
      breadcrumbBar.classList.add('hidden');
    } else {
      breadcrumbBar.classList.remove('hidden');
    }
    window.scrollTo({ top: 0, behavior: 'smooth' });
    refreshIcons();
  } else {
    navigateToSection('home');
  }
}

function selectQualification(qualId) {
  navigateToSection('career-paths');
  switchCareerTab(qualId);
}

// Safe JSON fetcher that never rejects and falls back gracefully
async function safeFetchJson(url, defaultVal) {
  try {
    const res = await fetch(url);
    if (!res.ok) {
      console.warn(`Fetch returned status ${res.status} for ${url}`);
      return defaultVal;
    }
    return await res.json();
  } catch (err) {
    console.warn(`Fetch failed for ${url}:`, err);
    return defaultVal;
  }
}

// ==========================================
// 6. DATA LOADER & RENDERING
// ==========================================
async function loadAllDatasets() {
  const [paths, exams, govt, defence, colleges, cutoffs, scholarships, library, links, notifsAll, btechPathwaysRes, btechCompaniesRes, optionsRes] = await Promise.all([
    safeFetchJson('/api/career-paths', {}),
    safeFetchJson('/api/entrance-exams', []),
    safeFetchJson('/api/govt-engineering-jobs', []),
    safeFetchJson('/api/defence-entries', []),
    safeFetchJson('/api/colleges', []),
    safeFetchJson('/api/cutoffs', { cutoffs_reference: [] }),
    safeFetchJson('/api/scholarships', []),
    safeFetchJson('/api/digital-library', []),
    safeFetchJson('/api/official-links', []),
    safeFetchJson('/api/notifications/all', { notifications: [] }),
    safeFetchJson('/api/btech/pathways', { pathways: [] }),
    safeFetchJson('/api/btech/companies', { companies: [] }),
    safeFetchJson('/api/options', APP_OPTIONS)
  ]);

  if (optionsRes && optionsRes.btech_branches) {
    window.APP_OPTIONS = optionsRes;
    AppState.options = optionsRes;
  }

  AppState.datasets.careerPaths = paths || {};
  AppState.datasets.entranceExams = exams || [];
  AppState.datasets.govtJobs = govt || [];
  AppState.datasets.defenceEntries = defence || [];
  AppState.datasets.colleges = colleges || [];
  AppState.datasets.cutoffs = (cutoffs && cutoffs.cutoffs_reference) || [];
  AppState.datasets.scholarships = scholarships || [];
  AppState.datasets.digitalLibrary = library || [];
  AppState.datasets.officialLinks = links || [];
  AppState.datasets.allNotifications = (notifsAll && notifsAll.notifications) || [];
  AppState.datasets.btechPathways = (btechPathwaysRes && btechPathwaysRes.pathways) || [];
  AppState.datasets.companies = (btechCompaniesRes && btechCompaniesRes.companies) || [];

  // Render Initial Views with independent fault tolerance
  try { renderCareerPaths('10th'); } catch (e) { console.error('renderCareerPaths error:', e); }
  try { renderEntranceExams(); } catch (e) { console.error('renderEntranceExams error:', e); }
  try { renderGovtEngineering(); } catch (e) { console.error('renderGovtEngineering error:', e); }
  try { renderDefenceEntries(); } catch (e) { console.error('renderDefenceEntries error:', e); }
  try { renderColleges(); } catch (e) { console.error('renderColleges error:', e); }
  try { renderCutoffs(); } catch (e) { console.error('renderCutoffs error:', e); }
  try { renderScholarships(); } catch (e) { console.error('renderScholarships error:', e); }
  try { renderDigitalLibrary(); } catch (e) { console.error('renderDigitalLibrary error:', e); }
  try { renderOfficialLinks(); } catch (e) { console.error('renderOfficialLinks error:', e); }
  try { renderNotificationsCenter(); } catch (e) { console.error('renderNotificationsCenter error:', e); }

  // Check AI Engine & Refresh icons
  try { checkAIEngine(); } catch (e) { console.warn('checkAIEngine error:', e); }
  try { handleProfileQualChange(); } catch (e) { console.warn('handleProfileQualChange error:', e); }
  try { refreshIcons(); } catch (e) { console.warn('refreshIcons error:', e); }
}

// Career Paths Renderer
function switchCareerTab(tabId) {
  document.querySelectorAll('.tab-pill').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabId);
  });
  renderCareerPaths(tabId);
}

function renderCareerPaths(tabId) {
  const container = document.getElementById('career-paths-content');

  // Handle B.Tech separately to distinguish Aspirants vs Completed graduates
  if (tabId === 'btech') {
    renderBTechSection();
    return;
  }

  const sectionData = AppState.datasets.careerPaths[tabId];
  if (!sectionData) {
    container.innerHTML = '<div class="alert-box alert-warning">No data available for this qualification.</div>';
    return;
  }

  let html = `
    <div class="mb-4">
      <h3 style="font-size: 1.4rem; font-weight: 800; color: var(--text-main);">${escapeHtml(sectionData.title)}</h3>
      <p style="color: var(--text-secondary); margin-top: 0.25rem;">${escapeHtml(sectionData.description)}</p>
    </div>
    <div class="cards-grid">
  `;

  // Render sub-branches or paths
  const list = sectionData.streams || sectionData.paths || sectionData.branches || [];
  list.forEach(item => {
    if (item.is_rank_predictor) {
      html += `
        <div class="card rank-predictor-card" id="eamcet-rank-predictor-card">
          <div class="card-header-row">
            <h4 class="card-title" style="display: flex; align-items: center; gap: 0.5rem;">
              <i data-lucide="calculator" class="icon-sm text-primary"></i> ${escapeHtml(item.title || 'Rank Predictor')}
            </h4>
            <span class="badge badge-success">EAMCET / EAPCET</span>
          </div>
          <div class="card-org">AP & TS EAMCET / EAPCET College & Branch Estimator</div>
          <div class="card-body">
            <p style="margin-bottom: 0.75rem; color: var(--text-secondary); line-height: 1.5;">
              ${escapeHtml(item.details)}
            </p>
            <div class="rank-disclaimer-box" style="margin-top: 0.75rem; margin-bottom: 0.5rem; font-size: 0.78rem; color: var(--text-muted); background: var(--bg-surface-muted); padding: 0.65rem 0.85rem; border-radius: var(--radius-sm); border-left: 3px solid var(--accent); line-height: 1.4;">
              <i data-lucide="info" class="icon-xxs" style="vertical-align: -2px; margin-right: 0.25rem;"></i>
              ${escapeHtml(item.disclaimer)}
            </div>
          </div>
          <div class="card-footer" style="margin-top: auto; padding-top: 1rem;">
            <a href="${escapeHtml(item.official_url || 'https://aptsrank.in/')}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="display: inline-flex; align-items: center; gap: 0.45rem; text-decoration: none; font-weight: 600; width: 100%; justify-content: center;">
              <i data-lucide="external-link" class="icon-xs"></i> <span>${escapeHtml(item.button_text || 'Open Rank Predictor')}</span>
            </a>
          </div>
        </div>
      `;
      return;
    }

    html += `
      <div class="card">
        <div class="card-header-row">
          <h4 class="card-title">${escapeHtml(item.name || item.category || item.title || 'Pathway')}</h4>
          ${item.duration ? `<span class="badge badge-info">${escapeHtml(item.duration)}</span>` : ''}
        </div>
        ${item.eligibility ? `<div class="card-org">${t("career.eligibility", "Eligibility")}: ${escapeHtml(item.eligibility)}</div>` : ''}
        <div class="card-body">
          ${item.future_prospects ? `<p><strong>${t("career.prospects", "Prospects")}:</strong> ${escapeHtml(item.future_prospects)}</p>` : ''}
          ${item.career_prospects ? `<p style="margin-top: 0.35rem; color: var(--text-secondary);"><strong>Career Prospects:</strong> ${escapeHtml(item.career_prospects)}</p>` : ''}
          ${item.details ? `<p>${escapeHtml(item.details)}</p>` : ''}
          ${item.sub_branches ? `
            <div style="margin-top: 0.75rem;">
              <strong>${t("career.streams_label", "Streams / Specializations")}:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${(Array.isArray(item.sub_branches) ? item.sub_branches : []).map(sb => `<li><strong>${escapeHtml(sb.name || '')}:</strong> ${escapeHtml(sb.future_prospects || '')}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.roles ? `
            <div style="margin-top: 0.75rem;">
              <strong>${t("career.roles_label", "Key Job Roles")}:</strong>
              ${Array.isArray(item.roles) ? `
                <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                  ${item.roles.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                </ul>
              ` : `<p style="margin-top: 0.25rem; color: var(--text-secondary); font-size: 0.88rem;">${escapeHtml(item.roles)}</p>`}
            </div>
          ` : ''}
          ${item.key_exams ? `
            <div style="margin-top: 0.75rem;">
              <strong>Key Technical & Government Examinations:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${item.key_exams.map(ke => `<li><strong>${escapeHtml(ke.name || '')}:</strong> ${escapeHtml(ke.org || '')} ${ke.scale ? `<span class="badge badge-info" style="font-size: 0.7rem; margin-left: 0.25rem;">${escapeHtml(ke.scale)}</span>` : ''}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.exams ? `
            <div style="margin-top: 0.75rem;">
              <strong>Key Examinations & Career Roles:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${item.exams.map(ex => `<li><strong>${escapeHtml(ex.name || '')}:</strong> ${escapeHtml(ex.roles || ex.org || '')} ${ex.url ? `<a href="${escapeHtml(ex.url)}" target="_blank" rel="noopener noreferrer" style="font-size: 0.75rem; color: var(--primary); margin-left: 0.35rem;">Official Portal ↗</a>` : ''}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.employers ? `
            <div style="margin-top: 0.75rem;">
              <strong>Top Recruiting Employers & PSUs:</strong>
              <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.35rem;">
                ${(Array.isArray(item.employers) ? item.employers : [item.employers]).map(emp => `<span class="badge badge-light" style="font-size: 0.78rem;">${escapeHtml(emp)}</span>`).join('')}
              </div>
            </div>
          ` : ''}
          ${item.salary ? `<div style="margin-top: 0.5rem; font-size: 0.88rem;"><strong>Initial CTC / Salary:</strong> <span class="text-success" style="font-weight: 600;">${escapeHtml(item.salary)}</span></div>` : ''}
          ${item.stipend ? `<div style="margin-top: 0.5rem; font-size: 0.88rem;"><strong>Monthly Stipend:</strong> <span class="text-success" style="font-weight: 600;">${escapeHtml(item.stipend)}</span></div>` : ''}
          ${item.routes ? `
            <div style="margin-top: 0.75rem;">
              <strong>Commission Routes & Entries:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${item.routes.map(rt => {
                  if (typeof rt === 'string') return `<li>${escapeHtml(rt)}</li>`;
                  return `<li><strong>${escapeHtml(rt.name || '')}:</strong> ${escapeHtml(rt.academies || rt.branches || rt.details || '')} ${rt.url ? `<a href="${escapeHtml(rt.url)}" target="_blank" rel="noopener noreferrer" style="font-size: 0.75rem; color: var(--primary); margin-left: 0.35rem;">Official Portal ↗</a>` : ''}</li>`;
                }).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.specializations ? `
            <div style="margin-top: 0.75rem;">
              <strong>Major Specializations:</strong>
              <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.35rem;">
                ${item.specializations.map(sp => `<span class="badge badge-light" style="font-size: 0.78rem;">${escapeHtml(sp)}</span>`).join('')}
              </div>
            </div>
          ` : ''}
          ${item.qualifications ? `
            <div style="margin-top: 0.75rem;">
              <strong>Essential Eligibility & Certifications:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${item.qualifications.map(q => `<li>${escapeHtml(q)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.avenues ? `
            <div style="margin-top: 0.75rem;">
              <strong>Key Business & Technical Avenues:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${item.avenues.map(av => `<li>${escapeHtml(av)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.govt_funding ? `
            <div style="margin-top: 0.5rem; font-size: 0.88rem; background: var(--bg-surface-muted); padding: 0.5rem 0.75rem; border-radius: 6px;">
              <strong>Govt Schemes & Subsidies:</strong> ${escapeHtml(item.govt_funding)}
            </div>
          ` : ''}
          ${item.recommendation ? `
            <div style="margin-top: 0.5rem; font-size: 0.85rem; color: var(--primary); font-style: italic;">
              💡 <strong>Recommendation:</strong> ${escapeHtml(item.recommendation)}
            </div>
          ` : ''}
          ${item.entrance_exams ? `
            <div class="card-meta-list" style="margin-top: 0.75rem;">
              <span class="meta-label">${t("career.exams_label", "Associated Entrance Exams")}:</span>
              <strong>${Array.isArray(item.entrance_exams) ? item.entrance_exams.join(', ') : item.entrance_exams}</strong>
            </div>
          ` : ''}
          ${item.id === 'inter-eamcet' ? `
            <div class="eamcet-predictor-banner" style="margin-top: 0.85rem; padding: 0.85rem; border-radius: var(--radius-sm); background: var(--bg-surface-muted); border: 1px dashed var(--primary); display: flex; flex-direction: column; gap: 0.4rem;">
              <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
                <span style="font-size: 0.88rem; font-weight: 700; color: var(--text-main); display: inline-flex; align-items: center; gap: 0.35rem;">
                  <i data-lucide="calculator" class="icon-xs text-primary"></i> Rank Predictor Tool
                </span>
                <a href="https://aptsrank.in/" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="font-size: 0.78rem; padding: 0.3rem 0.65rem; display: inline-flex; align-items: center; gap: 0.3rem; text-decoration: none;">
                  <i data-lucide="external-link" class="icon-xxs"></i> Open Rank Predictor
                </a>
              </div>
              <p style="font-size: 0.8rem; color: var(--text-secondary); margin: 0; line-height: 1.4;">
                Predict your EAMCET rank and explore colleges based on your rank and previous years' cutoff data. Find colleges and branches that may match your rank.
              </p>
              <div style="font-size: 0.72rem; color: var(--text-muted); font-style: italic; line-height: 1.35; margin-top: 0.25rem;">
                Rank and college predictions are estimates based on historical cutoff data. Actual admission outcomes may vary. Verify information through official counselling websites.
              </div>
            </div>
          ` : ''}
        </div>
        <div class="card-footer">
          ${item.id === 'inter-eamcet' ? `
            <a href="https://aptsrank.in/" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 0.35rem; text-decoration: none;">
              <i data-lucide="calculator" class="icon-xs"></i> <span>Open Rank Predictor</span>
            </a>
          ` : ''}
          ${item.official_url ? `
            <a href="${item.official_url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
              <i data-lucide="external-link" class="icon-xs"></i> ${t("common.official_portal", "Official Portal")}
            </a>
          ` : '<span></span>'}
          <button class="btn btn-primary" onclick="startAIWithTopic('${escapeHtml(item.name || item.category)}')">
            <i data-lucide="sparkles" class="icon-xs"></i> Plan with AI
          </button>
        </div>
      </div>
    `;
  });

  html += '</div>';
  container.innerHTML = html;
  refreshIcons();
}
// ==========================================
// 7. ENTRANCE EXAMS, GOVT JOBS & DEFENCE
// ==========================================
function filterExamCategory(cat) {
  AppState.activeFilters.examCategory = cat;
  document.querySelectorAll('#section-entrance-exams .filter-chip').forEach(btn => {
    btn.classList.toggle('active', btn.innerText.includes(cat) || (cat === 'All' && btn.innerText.includes('All')));
  });
  renderEntranceExams();
}

function filterEntranceExams() {
  AppState.activeFilters.examSearch = document.getElementById('exam-search-input')?.value.toLowerCase() || '';
  renderEntranceExams();
}

function renderEntranceExams() {
  const container = document.getElementById('entrance-exams-grid');
  let list = AppState.datasets.entranceExams || [];

  if (AppState.activeFilters.examCategory !== 'All') {
    list = list.filter(e => e.category === AppState.activeFilters.examCategory);
  }
  if (AppState.activeFilters.examSearch) {
    list = list.filter(e => e.name.toLowerCase().includes(AppState.activeFilters.examSearch) || e.purpose.toLowerCase().includes(AppState.activeFilters.examSearch));
  }

  if (list.length === 0) {
    container.innerHTML = '<div class="alert-box alert-warning">No matching entrance examinations found.</div>';
    return;
  }

  container.innerHTML = list.map(exam => `
    <div class="card">
      <div class="card-header-row">
        <h4 class="card-title">${escapeHtml(exam.name)}</h4>
        <span class="badge badge-primary">${escapeHtml(exam.category)}</span>
      </div>
      <div class="card-org">${t("exams.conducting_body", "Conducting Body")}: ${escapeHtml(exam.conducting_body)}</div>
      <div class="card-body">
        <p><strong>${t("common.purpose", "Purpose")}:</strong> ${escapeHtml(exam.purpose)}</p>
        <div class="card-meta-list">
          <div class="card-meta-item"><span>${t("exams.eligibility_summary", "Eligibility")}:</span> <strong>${escapeHtml(exam.eligibility)}</strong></div>
          <div class="card-meta-item"><span>${t("exams.application_window", "Timeline")}:</span> <strong>${escapeHtml(exam.timeline_status)}</strong></div>
          <div class="card-meta-item"><span>${t("exams.pattern_label", "Subjects")}:</span> <strong>${escapeHtml(Array.isArray(exam.important_subjects) ? exam.important_subjects.join(', ') : exam.important_subjects)}</strong></div>
        </div>
        ${(exam.id === 'exam-eapcet' || (exam.name && exam.name.toLowerCase().includes('eamcet'))) ? `
          <div class="eamcet-predictor-banner" style="margin-top: 0.85rem; padding: 0.85rem; border-radius: var(--radius-sm); background: var(--bg-surface-muted); border: 1px dashed var(--primary); display: flex; flex-direction: column; gap: 0.4rem;">
            <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 0.5rem;">
              <span style="font-size: 0.88rem; font-weight: 700; color: var(--text-main); display: inline-flex; align-items: center; gap: 0.35rem;">
                <i data-lucide="calculator" class="icon-xs text-primary"></i> Rank Predictor Tool
              </span>
              <a href="https://aptsrank.in/" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="font-size: 0.78rem; padding: 0.3rem 0.65rem; display: inline-flex; align-items: center; gap: 0.3rem; text-decoration: none;">
                <i data-lucide="external-link" class="icon-xxs"></i> Open Rank Predictor
              </a>
            </div>
            <p style="font-size: 0.8rem; color: var(--text-secondary); margin: 0; line-height: 1.4;">
              Predict your EAMCET rank and explore colleges based on your rank and previous years' cutoff data. Find colleges and branches that may match your rank.
            </p>
            <div style="font-size: 0.72rem; color: var(--text-muted); font-style: italic; line-height: 1.35; margin-top: 0.25rem;">
              Rank and college predictions are estimates based on historical cutoff data. Actual admission outcomes may vary. Verify information through official counselling websites.
            </div>
          </div>
        ` : ''}
      </div>
      <div class="card-footer">
        ${(exam.id === 'exam-eapcet' || (exam.name && exam.name.toLowerCase().includes('eamcet'))) ? `
          <a href="https://aptsrank.in/" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem; display: inline-flex; align-items: center; gap: 0.35rem; text-decoration: none;">
            <i data-lucide="calculator" class="icon-xs"></i> <span>Open Rank Predictor</span>
          </a>
        ` : ''}
        <a href="${exam.official_website}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> ${t("common.official_portal", "Official Portal")}
        </a>
        <button class="btn btn-secondary" onclick="sendQuickPrompt('Explain ' + '${escapeHtml(exam.name)}' + ' eligibility and syllabus simply.')">
          <i data-lucide="help-circle" class="icon-xs"></i> ${t("notifications.ask_ai", "Ask AI")}
        </button>
      </div>
    </div>
  `).join('');
  refreshIcons();
}

// Government Jobs for Engineers Renderer
function renderGovtEngineering() {
  const container = document.getElementById('govt-engineering-container');
  const list = AppState.datasets.govtJobs || [];

  container.innerHTML = list.map(job => `
    <div class="card">
      <div class="card-header-row">
        <h4 class="card-title">${escapeHtml(job.title)}</h4>
        <span class="badge badge-warning">${translateDynamic("Govt Service")}</span>
      </div>
      <div class="card-org">${escapeHtml(job.organization)}</div>
      <div class="card-body">
        <p><strong>${t("common.purpose", "Purpose")}:</strong> ${escapeHtml(job.purpose)}</p>
        <div class="card-meta-list">
          <div class="card-meta-item"><span>${t("common.eligibility", "Qualification")}:</span> <strong>${escapeHtml(job.qualification)}</strong></div>
          <div class="card-meta-item"><span>${t("jobs.job_roles", "Eligible Branches")}:</span> <strong>${escapeHtml(job.branches_eligible || job.disciplines || 'Core Engineering')}</strong></div>
          <div class="card-meta-item"><span>${t("jobs.age_limit", "Age Limit")}:</span> <strong>${escapeHtml(job.age_limit || 'Per Gazette')}</strong></div>
          <div class="card-meta-item"><span>${t("jobs.pay_scale", "Salary / Scale")}:</span> <strong style="color: var(--status-open);">${escapeHtml(job.salary_pay_scale || '7th CPC Scale')}</strong></div>
        </div>
        ${job.selection_process ? `<p style="font-size: 0.82rem; margin-top: 0.5rem;"><strong>${t("jobs.selection_process", "Selection")}:</strong> ${escapeHtml(job.selection_process)}</p>` : ''}
      </div>
      <div class="card-footer">
        <a href="${job.official_website}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> ${t("jobs.official_notification", "Official Notification Portal")}
        </a>
      </div>
    </div>
  `).join('');
  refreshIcons();
}

// Defence Roadmap Renderer
function filterDefenceLevel(lvl) {
  AppState.activeFilters.defenceLevel = lvl;
  document.querySelectorAll('#section-defence .filter-chip').forEach(btn => {
    btn.classList.toggle('active', btn.innerText.includes(lvl) || (lvl === 'All' && btn.innerText.includes('All')));
  });
  renderDefenceEntries();
}

function renderDefenceEntries() {
  const container = document.getElementById('defence-entries-container');
  let list = AppState.datasets.defenceEntries || [];

  if (AppState.activeFilters.defenceLevel !== 'All') {
    if (AppState.activeFilters.defenceLevel === '12th') {
      list = list.filter(d => d.entry_type.includes('12th'));
    } else if (AppState.activeFilters.defenceLevel === 'Graduate') {
      list = list.filter(d => d.entry_type.includes('Graduate'));
    } else if (AppState.activeFilters.defenceLevel === 'Engineering') {
      list = list.filter(d => d.entry_type.includes('Engineering'));
    } else if (AppState.activeFilters.defenceLevel === 'Agniveer') {
      list = list.filter(d => d.id.includes('agniveer'));
    }
  }

  container.innerHTML = list.map(def => `
    <div class="card">
      <div class="card-header-row">
        <h4 class="card-title">${escapeHtml(def.title)}</h4>
        <span class="badge badge-success">${escapeHtml(def.entry_type)}</span>
      </div>
      <div class="card-org">${escapeHtml(def.organization)}</div>
      <div class="card-body">
        <div class="card-meta-list">
          <div class="card-meta-item"><span>${t("defence.education_req", "Eligibility")}:</span> <strong>${escapeHtml(def.qualification)}</strong></div>
          <div class="card-meta-item"><span>${t("jobs.age_limit", "Age Limit")}:</span> <strong>${escapeHtml(def.age_limit)}</strong></div>
          <div class="card-meta-item"><span>${t("common.gender_marital", "Gender / Marital")}:</span> <strong>${escapeHtml(def.gender_marital || 'Unmarried')}</strong></div>
          <div class="card-meta-item"><span>${t("defence.stipend_pay", "Rank / Pay")}:</span> <strong style="color: var(--status-open);">${escapeHtml(def.rank_on_commission || 'Officer Cadre')} (${escapeHtml(def.pay_scale || 'Level 10')})</strong></div>
        </div>
        ${def.physical_standards ? `<p style="font-size: 0.82rem; margin-top: 0.5rem;"><strong>${t("defence.ssb_prep_title", "Physical Standards")}:</strong> ${escapeHtml(def.physical_standards)}</p>` : ''}
        ${def.selection_stages ? `
          <div style="margin-top: 0.5rem;">
            <strong style="font-size: 0.82rem;">${t("defence.selection_stages", "Selection Stages")}:</strong>
            <ul style="padding-left: 1.25rem; font-size: 0.8rem; margin-top: 0.25rem;">
              ${(Array.isArray(def.selection_stages) ? def.selection_stages : [def.selection_stages]).map(s => `<li>${escapeHtml(s)}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
      <div class="card-footer">
        <a href="${def.official_website}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> ${t("defence.official_recruitment_portal", "Official Defence Portal")}
        </a>
        <button class="btn btn-secondary" onclick="sendQuickPrompt('Explain ' + '${escapeHtml(def.title)}' + ' selection and physical standards.')">
          <i data-lucide="shield" class="icon-xs"></i> Roadmap
        </button>
      </div>
    </div>
  `).join('');
  refreshIcons();
}

// Colleges & Cutoffs Renderers
function renderColleges() {
  const container = document.getElementById('colleges-grid');
  const list = AppState.datasets.colleges || [];

  container.innerHTML = list.map(c => `
    <div class="card">
      <div class="card-header-row">
        <h4 class="card-title">${escapeHtml(c.name)}</h4>
        <span class="badge badge-info">${escapeHtml(c.nirf_rank || 'Top Tier')}</span>
      </div>
      <div class="card-org"><i data-lucide="map-pin" class="icon-xs"></i> ${escapeHtml(c.location)} (${escapeHtml(c.type)})</div>
      <div class="card-body">
        <div class="card-meta-list">
          <div class="card-meta-item"><span>${t("career.exams_label", "Entrance Exams")}:</span> <strong>${escapeHtml(c.accepted_exams?.join(', ') || 'National/State')}</strong></div>
          ${c.fees_per_year ? `<div class="card-meta-item"><span>Fees Structure:</span> <strong>${escapeHtml(c.fees_per_year)}</strong></div>` : ''}
        </div>
        <p style="font-size: 0.82rem;"><strong>${t("colleges.top_branches", "Popular Branches")}:</strong> ${escapeHtml(c.popular_branches?.join(', ') || 'Engineering & Science')}</p>
      </div>
      <div class="card-footer">
        <a href="${c.official_website}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> ${t("common.official_website", "Official Website")}
        </a>
      </div>
    </div>
  `).join('');
  refreshIcons();
}

function filterCutoffs() {
  AppState.activeFilters.cutoffSearch = document.getElementById('cutoff-search-input')?.value.toLowerCase() || '';
  renderCutoffs();
}

function renderCutoffs() {
  const tbody = document.getElementById('cutoffs-tbody');
  let list = AppState.datasets.cutoffs || [];

  if (AppState.activeFilters.cutoffSearch) {
    list = list.filter(c => 
      c.college.toLowerCase().includes(AppState.activeFilters.cutoffSearch) ||
      c.branch.toLowerCase().includes(AppState.activeFilters.cutoffSearch) ||
      c.exam.toLowerCase().includes(AppState.activeFilters.cutoffSearch)
    );
  }

  if (list.length === 0) {
    tbody.innerHTML = '<tr><td colspan="7" class="text-center">No matching cutoff records found.</td></tr>';
    return;
  }

  tbody.innerHTML = list.map(item => `
    <tr>
      <td><strong>${escapeHtml(item.exam)}</strong></td>
      <td>${escapeHtml(item.college)}</td>
      <td><span class="badge badge-primary">${escapeHtml(item.branch)}</span></td>
      <td>${escapeHtml(item.category)}</td>
      <td>${item.opening_rank}</td>
      <td><strong style="color: var(--primary);">${item.closing_rank}</strong></td>
      <td>${escapeHtml(item.year)}</td>
    </tr>
  `).join('');
}

// Scholarships Renderer
function renderScholarships() {
  const container = document.getElementById('scholarships-grid');
  const list = AppState.datasets.scholarships || [];

  container.innerHTML = list.map(sch => `
    <div class="card">
      <div class="card-header-row">
        <h4 class="card-title">${escapeHtml(sch.name)}</h4>
        <span class="badge badge-danger">${translateDynamic("Verified Scheme")}</span>
      </div>
      <div class="card-org">${t("scholarships.portal_name", "Provider")}: ${escapeHtml(sch.provider)}</div>
      <div class="card-body">
        <div class="card-meta-list">
          <div class="card-meta-item"><span>${t("scholarships.benefit_amount", "Award Amount")}:</span> <strong style="color: var(--status-open);">${escapeHtml(sch.amount)}</strong></div>
          <div class="card-meta-item"><span>${t("scholarships.target_beneficiaries", "Target Qualification")}:</span> <strong>${escapeHtml(sch.target_qualification)}</strong></div>
          <div class="card-meta-item"><span>${t("scholarships.family_income", "Income Ceiling")}:</span> <strong>${escapeHtml(sch.income_criteria)}</strong></div>
          ${sch.application_window ? `<div class="card-meta-item"><span>Application Window:</span> <strong>${escapeHtml(sch.application_window)}</strong></div>` : ''}
        </div>
        <p style="font-size: 0.82rem;"><strong>${t("career.eligibility", "Eligibility")}:</strong> ${escapeHtml(sch.eligibility)}</p>
      </div>
      <div class="card-footer">
        <a href="${sch.official_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> ${t("scholarships.apply_link", "Apply on Official Portal")}
        </a>
      </div>
    </div>
  `).join('');
  refreshIcons();
}

// Digital Library Renderer
function filterLibrary() {
  AppState.activeFilters.librarySearch = document.getElementById('library-search-input')?.value.toLowerCase() || '';
  renderDigitalLibrary();
}

function renderDigitalLibrary() {
  const container = document.getElementById('digital-library-grid');
  let list = AppState.datasets.digitalLibrary || [];

  if (AppState.activeFilters.librarySearch) {
    list = list.filter(item => 
      item.title.toLowerCase().includes(AppState.activeFilters.librarySearch) ||
      item.category.toLowerCase().includes(AppState.activeFilters.librarySearch) ||
      item.description.toLowerCase().includes(AppState.activeFilters.librarySearch)
    );
  }

  container.innerHTML = list.map(res => `
    <div class="card">
      <div class="card-header-row">
        <h4 class="card-title">${escapeHtml(res.title)}</h4>
        <span class="badge badge-success">${escapeHtml(res.format)}</span>
      </div>
      <div class="card-org">${escapeHtml(res.source)}</div>
      <div class="card-body">
        <p>${escapeHtml(res.description)}</p>
        <div class="card-meta-list">
          <div class="card-meta-item"><span>License / Access:</span> <strong>${escapeHtml(res.license)}</strong></div>
        </div>
      </div>
      <div class="card-footer">
        <a href="${res.url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> ${t("library.access_resource", "Access Resource")}
        </a>
      </div>
    </div>
  `).join('');
  refreshIcons();
}

// Official Links Directory Renderer
function renderOfficialLinks() {
  const container = document.getElementById('official-links-container');
  const groups = AppState.datasets.officialLinks || [];

  container.innerHTML = groups.map(group => `
    <div class="saved-roadmap-card mb-4">
      <h3 style="font-size: 1.25rem; font-weight: 800; color: var(--text-main); margin-bottom: 1rem;">
        <i data-lucide="shield-check" class="icon-sm text-primary"></i> ${escapeHtml(group.category)}
      </h3>
      <div class="cards-grid">
        ${group.links.map(link => `
          <div class="card" style="padding: 1.15rem;">
            <h4 style="font-size: 1rem; font-weight: 700; margin-bottom: 0.35rem;">${escapeHtml(link.name)}</h4>
            <p style="font-size: 0.82rem; color: var(--text-muted); margin-bottom: 0.85rem;">${escapeHtml(link.description)}</p>
            <a href="${link.url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="padding: 0.4rem 0.75rem; font-size: 0.8rem; width: fit-content;">
              <i data-lucide="external-link" class="icon-xs"></i> Visit Portal
            </a>
          </div>
        `).join('')}
      </div>
    </div>
  `).join('');
  refreshIcons();
}

// Notification Center Renderer
function filterNotifCategory(cat) {
  AppState.activeFilters.notifCategory = cat;
  document.querySelectorAll('#section-notifications .filter-chip').forEach(btn => {
    btn.classList.toggle('active', btn.innerText.includes(cat) || (cat === 'All' && btn.innerText.includes('All')));
  });
  renderNotificationsCenter();
}

function filterNotifications() {
  AppState.activeFilters.notifSearch = document.getElementById('notif-search-input')?.value.toLowerCase() || '';
  renderNotificationsCenter();
}

function renderNotificationsCenter() {
  const container = document.getElementById('notifications-grid');
  let list = AppState.datasets.allNotifications || [];

  if (AppState.activeFilters.notifCategory !== 'All') {
    list = list.filter(n => n.category === AppState.activeFilters.notifCategory);
  }
  if (AppState.activeFilters.notifSearch) {
    list = list.filter(n => 
      n.title.toLowerCase().includes(AppState.activeFilters.notifSearch) ||
      n.organization.toLowerCase().includes(AppState.activeFilters.notifSearch)
    );
  }

  if (list.length === 0) {
    container.innerHTML = '<div class="alert-box alert-warning">No notifications found for the selected category.</div>';
    return;
  }

  container.innerHTML = list.map(notif => {
    const badgeClass = getBadgeClass(notif.dynamic_status || notif.status);
    return `
      <div class="card">
        <div class="card-header-row">
          <h4 class="card-title">${escapeHtml(notif.title)}</h4>
          <span class="badge ${badgeClass}">${notif.dynamic_status || notif.status}</span>
        </div>
        <div class="card-org">${escapeHtml(notif.organization)}</div>
        <div class="card-body">
          <p>${escapeHtml(notif.description)}</p>
          <div class="card-meta-list">
            <div class="card-meta-item"><span>${t("career.eligibility", "Eligibility")}:</span> <strong>${escapeHtml(notif.eligibility_summary)}</strong></div>
            <div class="card-meta-item"><span>${t("common.exam_date", "Exam / Event Date")}:</span> <strong>${escapeHtml(notif.exam_date)}</strong></div>
            <div class="card-meta-item"><span>${t("notifications.last_verified", "Last Verified")}:</span> <strong>${new Date(notif.last_verified_at).toLocaleDateString()}</strong></div>
          </div>
        </div>
        <div class="card-footer">
          <button class="btn btn-secondary" onclick="openNotifModal('${notif.id}')">${t("common.view_details", "View Details")}</button>
          <a href="${notif.official_source}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
            <i data-lucide="external-link" class="icon-xs"></i> ${t("notifications.open_portal", "Official Source")}
          </a>
        </div>
      </div>
    `;
  }).join('');
  refreshIcons();
}

function openNotifModal(id) {
  const notif = (AppState.datasets.allNotifications && AppState.datasets.allNotifications.find(n => n.id === id)) || 
                (AppState.datasets.notifications && AppState.datasets.notifications.find(n => n.id === id));
  if (!notif) return;

  AppState.currentOpportunity = notif;
  const modal = document.getElementById('notif-modal');
  const statusLabel = notif.display_status || notif.dynamic_status || notif.status;
  document.getElementById('modal-badge').innerText = statusLabel;
  document.getElementById('modal-badge').className = `badge ${getBadgeClass(statusLabel)}`;
  document.getElementById('modal-title').innerText = notif.title;
  document.getElementById('modal-org').innerText = notif.organization;
  document.getElementById('modal-desc').innerText = notif.description;
  document.getElementById('modal-eligibility').innerText = notif.eligibility_summary;
  document.getElementById('modal-start').innerText = new Date(notif.start_datetime).toLocaleDateString();
  document.getElementById('modal-end').innerText = new Date(notif.end_datetime).toLocaleDateString();
  document.getElementById('modal-exam').innerText = notif.exam_date || 'N/A';
  document.getElementById('modal-verified').innerText = new Date(notif.last_verified_at).toLocaleDateString();
  document.getElementById('modal-source-btn').href = notif.official_source;

  modal.classList.remove('hidden');
  refreshIcons();
}

function closeNotifModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('close-btn')) return;
  document.getElementById('notif-modal').classList.add('hidden');
}

function askAIAboutCurrentOpportunity() {
  if (AppState.currentOpportunity) {
    askAIAboutOpportunity(AppState.currentOpportunity.id);
  }
}

function askAIAboutOpportunity(id) {
  const notif = (AppState.datasets.allNotifications && AppState.datasets.allNotifications.find(n => n.id === id)) || 
                (AppState.datasets.notifications && AppState.datasets.notifications.find(n => n.id === id)) ||
                AppState.currentOpportunity;
  if (!notif) return;

  closeNotifModal();
  navigateToSection('ai-guide');

  const defaultPrompt = `Tell me about ${notif.title} conducted by ${notif.organization}. Eligibility: ${notif.eligibility_summary}. What is the exam pattern, how should I prepare, and what are the next steps?`;

  const input = document.getElementById('chat-input');
  if (input) {
    input.value = defaultPrompt;
  }

  // Update quick chips to offer tailored one-click questions for this specific opportunity
  const quickChips = document.getElementById('quick-chips');
  if (quickChips) {
    const qualVal = document.getElementById('prof-qual')?.value || 'Student';
    quickChips.innerHTML = `
      <span class="chips-label" style="color: var(--primary); font-weight: 700;">Opportunity Topics:</span>
      <button class="chip-btn" onclick="sendQuickPrompt('Am I eligible for ${escapeHtml(notif.title)}? My qualification is ${escapeHtml(qualVal)}.')">Am I eligible?</button>
      <button class="chip-btn" onclick="sendQuickPrompt('How should I prepare for ${escapeHtml(notif.title)} step-by-step?')">How should I prepare?</button>
      <button class="chip-btn" onclick="sendQuickPrompt('Create a 6-month preparation plan for ${escapeHtml(notif.title)}.')">Create a 6-month preparation plan</button>
      <button class="chip-btn" onclick="sendQuickPrompt('What is the selection process and syllabus for ${escapeHtml(notif.title)}?')">Selection process & syllabus</button>
    `;
  }

  setTimeout(() => {
    input?.focus();
    input?.scrollIntoView({ behavior: 'smooth', block: 'center' });
  }, 200);
}

// ==========================================
// 8. AI CAREER GUIDE & ROADMAP ENGINE
// ==========================================
function handleProfileQualChange() {
  const qualElem = document.getElementById('prof-qual');
  const streamElem = document.getElementById('prof-stream');
  const prefElem = document.getElementById('prof-pref');
  const goalElem = document.getElementById('prof-goal');
  if (!qualElem) return;

  const qual = qualElem.value || 'B.Tech';
  const optData = window.APP_OPTIONS || APP_OPTIONS;

  // 1. Update Stream dropdown
  if (streamElem) {
    const streamsMap = optData.streams_by_qual || optData.branches_by_qual || {};
    let streams = streamsMap[qual] || streamsMap['B.Tech'] || [];
    if (!streams || streams.length === 0) {
      if (qual === '10th') streams = ["General", "Science", "Mathematics", "IT"];
      else if (qual === 'Intermediate') streams = ["MPC", "BiPC", "CEC", "MEC", "HEC", "Vocational"];
      else if (qual === 'Diploma') streams = ["CSE", "Information Technology", "ECE", "EEE", "Mechanical Engineering", "Civil Engineering"];
      else if (qual === 'Degree') streams = ["B.Sc Computer Science", "B.Sc Mathematics", "B.Com", "BBA", "BCA", "BA"];
      else if (qual === 'Postgraduate') streams = ["M.Tech (CSE)", "M.Tech (VLSI)", "MBA", "MCA", "M.Sc"];
      else streams = ["CSE", "ECE", "EEE", "Mechanical Engineering", "Civil Engineering", "Cyber Security", "Data Science", "AI & ML"];
    }
    streamElem.innerHTML = streams.map((s, idx) => `<option value="${escapeHtml(s)}" ${idx === 0 ? 'selected' : ''}>${escapeHtml(s)}</option>`).join('');
  }

  // 2. Update Preferred Career Direction dropdown
  if (prefElem) {
    const dirsMap = optData.preferred_career_directions_by_qual || {};
    let dirs = dirsMap[qual];
    if (!dirs) {
      if (qual === '10th') dirs = dirsMap['10th'];
      else if (qual === 'Intermediate') dirs = dirsMap['Intermediate'];
      else if (qual === 'Diploma') dirs = dirsMap['Diploma'];
      else if (qual === 'Degree') dirs = dirsMap['Degree'];
      else if (qual === 'Postgraduate') dirs = dirsMap['Postgraduate'];
      else dirs = dirsMap['B.Tech'];
    }
    if (!dirs || dirs.length === 0) {
      if (qual === '10th') dirs = ["Intermediate (MPC / BiPC / CEC / MEC)", "Polytechnic Diploma (Engineering)", "ITI Trades", "Direct Government / Defence Exams (Agniveer, SSC GD)"];
      else if (qual === 'Intermediate') dirs = ["Engineering (B.Tech / B.E.)", "Medical & Allied Health Sciences (MBBS, BDS, B.Pharm, Nursing, Agri)", "Degree (B.Sc, B.Com, BBA, BA)", "Defence (NDA, TES)", "Law (CLAT / Integrated Law)", "CA / CMA / CS Foundation"];
      else if (qual === 'Diploma') dirs = ["Lateral Entry to B.Tech (ECET)", "Junior Engineer (JE) Government Exams", "Core Technical Industry Jobs", "NATS Apprenticeship", "Defence Technical Roles"];
      else if (qual === 'Degree') dirs = ["Post Graduation (M.Sc, M.Com, MA, MCA)", "MBA / Management", "Government Exams (UPSC CSE, SSC CGL, Banking)", "Corporate Private Sector Jobs", "Defence (CDS, AFCAT)"];
      else if (qual === 'Postgraduate') dirs = ["Ph.D. / Research / Doctoral Fellowships", "University Teaching / Assistant Professor (UGC NET)", "Senior Corporate R&D / Lead Roles", "Government Scientist Roles (DRDO, ISRO, BARC)"];
      else dirs = ["Software / IT Industry", "Cyber Security", "Core Engineering Jobs", "Government Engineering Jobs (IES / ESE, State AE/AEE)", "PSUs via GATE", "Higher Studies (M.Tech via GATE)", "Higher Studies Abroad (MS via GRE/TOEFL)", "Management (MBA via CAT)", "Defence Technical Entry (TGC, SSC Tech, Navy)"];
    }
    prefElem.innerHTML = dirs.map((d, idx) => `<option value="${escapeHtml(d)}" ${idx === 0 ? 'selected' : ''}>${escapeHtml(d)}</option>`).join('');
  }

  // 3. Update Suggested Goal placeholder and value
  if (goalElem) {
    if (qual === '10th') {
      goalElem.placeholder = 'e.g. 10+2 MPC for Engineering, or NEET BiPC for MBBS';
      goalElem.value = '10+2 Intermediate (MPC for Engineering)';
    } else if (qual === 'Intermediate') {
      goalElem.placeholder = 'e.g. Crack JEE Main for IIT B.Tech, or NEET UG for MBBS';
      goalElem.value = 'B.Tech in Computer Science / IIT JEE';
    } else if (qual === 'Diploma') {
      goalElem.placeholder = 'e.g. ECET State Top Rank for Lateral Entry B.Tech or RRB JE';
      goalElem.value = 'B.Tech Lateral Entry via State ECET';
    } else if (qual === 'Degree') {
      goalElem.placeholder = 'e.g. MBA at Top IIM via CAT, or Bank PO (IBPS), or MCA';
      goalElem.value = 'MBA in Finance / Management';
    } else if (qual === 'Postgraduate') {
      goalElem.placeholder = 'e.g. PMRF Doctoral Fellowship at IIT or UGC NET Assistant Professor';
      goalElem.value = 'Ph.D. Doctoral Fellowship (PMRF / IIT)';
    } else {
      goalElem.placeholder = 'e.g. Cyber Security Specialist, ISRO Scientist, SDE at Google';
      goalElem.value = 'Software Development Engineer';
    }
  }
}

async function checkAIEngine() {
  const statusElem = document.getElementById('ai-engine-status');
  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: 'ping', profile: {} })
    });
    const data = await res.json();
    if (data.mode === 'gemini_ai') {
      statusElem.innerHTML = '<strong>Engine:</strong> Google Gemini AI (Secured Server Cloud)';
    } else {
      statusElem.innerHTML = '<strong>Engine:</strong> CareerCompass Verified Knowledge Engine (Offline/Rule-Based Mode)';
    }
  } catch (err) {
    statusElem.innerText = 'Operating on Local Knowledge Engine';
  }
}

function startAIWithTopic(topic) {
  navigateToSection('ai-guide');
  sendQuickPrompt(`I want to explore the pathway for ${topic}. What exams, colleges, and steps should I take?`);
}

function sendQuickPrompt(promptText) {
  navigateToSection('ai-guide');
  const input = document.getElementById('chat-input');
  if (input) {
    input.value = promptText;
    document.getElementById('chat-form').dispatchEvent(new Event('submit'));
  }
}

async function submitChatMessage(e) {
  e.preventDefault();
  const input = document.getElementById('chat-input');
  const message = input.value.trim();
  if (!message) return;

  const messagesContainer = document.getElementById('chat-messages');

  // Append user message bubble
  messagesContainer.innerHTML += `
    <div class="chat-bubble user-bubble">
      <div class="bubble-header">
        <span class="bubble-sender">You</span>
        <span class="bubble-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
      </div>
      <div class="bubble-body">${escapeHtml(message)}</div>
    </div>
  `;

  input.value = '';
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  // Append thinking bubble
  const typingId = 'typing-' + Date.now();
  messagesContainer.innerHTML += `
    <div id="${typingId}" class="chat-bubble bot-bubble">
      <div class="bubble-header"><span class="bubble-sender">AI Career Guide</span></div>
      <div class="bubble-body"><span class="pulse-indicator"></span> Consulting verified career database...</div>
    </div>
  `;
  messagesContainer.scrollTop = messagesContainer.scrollHeight;

  // Read current profile builder values for contextual intelligence
  const currentProfile = {
    education_level: document.getElementById('prof-qual')?.value || '',
    qualification: document.getElementById('prof-qual')?.value || '',
    stream_or_branch: document.getElementById('prof-stream')?.value || '',
    branch: document.getElementById('prof-stream')?.value || '',
    completion_status: document.getElementById('prof-status')?.value || 'Final Year',
    status: document.getElementById('prof-status')?.value || 'Final Year',
    score: document.getElementById('prof-score')?.value || '',
    age: document.getElementById('prof-age')?.value || '',
    state: document.getElementById('prof-state')?.value || '',
    preferred_career_direction: document.getElementById('prof-pref')?.value || '',
    preference: document.getElementById('prof-pref')?.value || '',
    career_goal: document.getElementById('prof-goal')?.value || '',
    goal: document.getElementById('prof-goal')?.value || ''
  };

  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: message, profile: currentProfile, language: AppState.currentLang })
    });
    const result = await res.json();
    document.getElementById(typingId)?.remove();

    if (result.reply) {
      messagesContainer.innerHTML += `
        <div class="chat-bubble bot-bubble">
          <div class="bubble-header">
            <span class="bubble-sender">${escapeHtml(result.provider || 'AI Career Guide')}</span>
            <span class="bubble-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
          </div>
          <div class="bubble-body">${formatMarkdown(result.reply)}</div>
        </div>
      `;
    }

    if (result.data) {
      const d = result.data;
      const r = d.roadmap || {};
      if (!result.reply) {
        messagesContainer.innerHTML += `
          <div class="chat-bubble bot-bubble">
            <div class="bubble-header">
              <span class="bubble-sender">${escapeHtml(result.provider || 'AI Career Guide')}</span>
              <span class="bubble-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
            </div>
            <div class="bubble-body">
              <h4 style="font-size: 1rem; font-weight: 800; color: var(--primary); margin-bottom: 0.4rem;">${escapeHtml(d.title)}</h4>
              <p style="margin-bottom: 0.75rem;">${escapeHtml(d.summary)}</p>
              <div style="background: var(--bg-surface); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); font-size: 0.85rem;">
                <p><strong>Available Options:</strong></p>
                <ul style="padding-left: 1.25rem; margin-top: 0.25rem;">
                  ${(r.suitable_options || []).map(opt => `<li>${escapeHtml(opt)}</li>`).join('')}
                </ul>
                <p style="margin-top: 0.5rem;"><strong>Recommended Exams:</strong> ${(Array.isArray(r.entrance_exams) ? r.entrance_exams.join(', ') : r.entrance_exams || 'None')}</p>
                <p style="margin-top: 0.5rem;"><strong>Career Opportunities:</strong> ${escapeHtml(r.career_opportunities || r.career || '')}</p>
              </div>
              <p class="disclaimer-mini" style="margin-top: 0.5rem;">${escapeHtml(d.disclaimer || '')}</p>
            </div>
          </div>
        `;
      }
      renderStructuredRoadmap(d, currentProfile);
    }
  } catch (err) {
    document.getElementById(typingId)?.remove();
    messagesContainer.innerHTML += `
      <div class="chat-bubble bot-bubble">
        <div class="bubble-header"><span class="bubble-sender">AI Career Guide</span></div>
        <div class="bubble-body">I encountered a temporary connection issue. Please explore the verified Career Paths and Notification Center tabs for current guidance.</div>
      </div>
    `;
  }
  messagesContainer.scrollTop = messagesContainer.scrollHeight;
  refreshIcons();
}

// 15-Point Profile Builder Form Submission
async function generateProfileRoadmap(e) {
  e.preventDefault();
  const profile = {
    education_level: document.getElementById('prof-qual')?.value || '',
    qualification: document.getElementById('prof-qual')?.value || '',
    stream_or_branch: document.getElementById('prof-stream')?.value || '',
    branch: document.getElementById('prof-stream')?.value || '',
    completion_status: document.getElementById('prof-status')?.value || 'Final Year',
    status: document.getElementById('prof-status')?.value || 'Final Year',
    score: document.getElementById('prof-score')?.value || '',
    age: document.getElementById('prof-age')?.value || '',
    state: document.getElementById('prof-state')?.value || '',
    preferred_career_direction: document.getElementById('prof-pref')?.value || '',
    preference: document.getElementById('prof-pref')?.value || '',
    career_goal: document.getElementById('prof-goal')?.value || '',
    goal: document.getElementById('prof-goal')?.value || ''
  };

  const query = `Create a complete step-by-step career roadmap for a student with qualification: ${profile.qualification}, stream/branch: ${profile.branch}, completion status: ${profile.status}, score: ${profile.score}, age: ${profile.age}, state: ${profile.state}, preferred career direction: ${profile.preference}, and dream career goal: ${profile.goal}.`;

  const container = document.getElementById('ai-roadmap-result');
  container.classList.remove('hidden');
  container.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Generating personalized CareerCompass roadmap for <strong>${escapeHtml(profile.goal || profile.preference)}</strong>...</p>
    </div>
  `;

  try {
    const res = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ message: query, profile: profile, language: AppState.currentLang })
    });
    const data = await res.json();
    if (data.data) {
      renderStructuredRoadmap(data.data, profile);
    } else {
      container.innerHTML = `
        <div class="roadmap-header">
          <div>
            <h3 class="roadmap-title">Personalized Roadmap: ${escapeHtml(profile.goal || profile.preference)}</h3>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Generated by ${data.provider}</p>
          </div>
          <button class="btn btn-secondary" onclick="saveCustomGoal('${escapeHtml(profile.goal || profile.preference)}', 'Active')">Save Roadmap</button>
        </div>
        <div style="font-size: 0.95rem; line-height: 1.6;">${formatMarkdown(data.reply || '')}</div>
      `;
    }
  } catch (err) {
    container.innerHTML = `<div class="alert-box alert-warning">Unable to generate roadmap right now. Please explore the Career Paths section.</div>`;
  }
  refreshIcons();
}

function renderStructuredRoadmap(roadmapData, userProfile = {}) {
  const container = document.getElementById('ai-roadmap-result');
  container.classList.remove('hidden');
  const r = roadmapData.roadmap || {};
  const goalTitle = userProfile.goal || roadmapData.title || 'Personalized Career Direction';

  container.innerHTML = `
    <div class="roadmap-header">
      <div>
        <div class="badge badge-primary" style="margin-bottom: 0.35rem;">MY CAREER ROADMAP</div>
        <h3 class="roadmap-title">${escapeHtml(goalTitle)}</h3>
        <p style="color: var(--text-muted); font-size: 0.85rem;">${escapeHtml(roadmapData.summary || '')}</p>
      </div>
      <div style="display: flex; gap: 0.5rem;">
        <button class="btn btn-secondary" onclick="window.print()"><i data-lucide="printer" class="icon-xs"></i> Print</button>
        <button class="btn btn-primary" onclick="saveRoadmapToStorage('${escapeHtml(goalTitle)}', ${JSON.stringify(r).replace(/"/g, '&quot;')})">
          <i data-lucide="bookmark-check" class="icon-xs"></i> Save to My Roadmaps
        </button>
      </div>
    </div>

    <!-- 9-Stage Milestone Progression Flow (Section 10 Standard) -->
    <div class="roadmap-flow">
      <div class="roadmap-step">
        <div class="step-label">1. CURRENT STAGE</div>
        <div class="step-content"><strong>${escapeHtml(r.current_position || 'Current Stage')}</strong></div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">2. YOUR AVAILABLE NEXT OPTIONS</div>
        <div class="step-content">
          <ul>
            ${(r.suitable_options || []).map(opt => `<li>${escapeHtml(opt)}</li>`).join('')}
          </ul>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">3. OPTION SELECTED</div>
        <div class="step-content">
          <strong style="color: var(--primary);">${escapeHtml(r.option_selected || r.suitable_options?.[0] || 'Target Selected Pathway')}</strong>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">4. ELIGIBILITY</div>
        <div class="step-content">
          <p>${escapeHtml(r.eligibility || 'Standard educational qualification from recognized board/university.')}</p>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">5. WHAT TO STUDY / SKILLS TO BUILD</div>
        <div class="step-content">
          <p>${escapeHtml(r.what_to_study_skills || (Array.isArray(r.skills) ? r.skills.join(', ') : r.skills) || 'Domain syllabus & practical tool mastery.')}</p>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">6. ENTRANCE EXAMS (IF APPLICABLE)</div>
        <div class="step-content">
          <strong>${(Array.isArray(r.entrance_exams) ? r.entrance_exams.join(' | ') : r.entrance_exams) || 'None / Direct merit admission'}</strong>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">7. APPLICATION / ADMISSION PROCESS</div>
        <div class="step-content">
          <p>${escapeHtml(r.admission_process || 'Online portal registration -> Entrance/Merit -> Web Counselling.')}</p>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">8. NEXT EDUCATION OR CAREER STEP</div>
        <div class="step-content">
          <p>${escapeHtml(r.next_education_or_career_step || 'Degree completion / Higher specialized master / Commissioning.')}</p>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">9. CAREER OPPORTUNITIES</div>
        <div class="step-content">
          <strong style="color: var(--primary); font-size: 1.05rem;">${escapeHtml(r.career_opportunities || r.career || r.career_outcome || 'Graduate Professional')}</strong>
        </div>
      </div>

      ${r.next_steps && r.next_steps.length ? `
      <div class="roadmap-step">
        <div class="step-label">IMMEDIATE ACTION STEPS</div>
        <div class="step-content">
          <ol style="padding-left: 1.25rem;">
            ${r.next_steps.map(ns => `<li>${escapeHtml(ns)}</li>`).join('')}
          </ol>
        </div>
      </div>` : ''}
    </div>

    <div class="alert-box alert-warning" style="margin-top: 1.5rem; margin-bottom: 0;">
      <div class="alert-icon"><i data-lucide="info"></i></div>
      <div><strong>Legal Disclaimer:</strong> ${escapeHtml(roadmapData.disclaimer || 'Guidance recommendations only.')}</div>
    </div>
  `;
  container.scrollIntoView({ behavior: 'smooth' });
  refreshIcons();
}

// ==========================================
// 9. SAVED ROADMAPS & PROGRESS CHECKLIST
// ==========================================
function saveRoadmapToStorage(goalTitle, roadmapData) {
  const steps = [
    { title: `Complete required qualification (${roadmapData.current_position || 'Degree'})`, done: false },
    { title: `Register and prepare for target exams (${(roadmapData.entrance_exams || []).slice(0, 2).join(', ')})`, done: false },
    { title: `Master core skills: ${(roadmapData.skills_required || roadmapData.skills || []).slice(0, 2).join(', ')}`, done: false },
    { title: 'Build portfolio / solve previous year question papers', done: false },
    { title: 'Attend counselling / written exam / SSB interview', done: false },
    { title: `Secure admission / appointment in ${goalTitle}`, done: false }
  ];

  const newEntry = {
    id: 'goal-' + Date.now(),
    goal: goalTitle,
    createdAt: new Date().toLocaleDateString(),
    steps: steps
  };

  AppState.savedRoadmaps.unshift(newEntry);
  localStorage.setItem('cc_roadmaps', JSON.stringify(AppState.savedRoadmaps));
  renderSavedRoadmaps();
  alert(`Roadmap for "${goalTitle}" successfully saved to My Saved Roadmaps!`);
  navigateToSection('saved-roadmaps');
}

function renderSavedRoadmaps() {
  const container = document.getElementById('saved-roadmaps-container');
  if (!container) return;

  if (AppState.savedRoadmaps.length === 0) {
    container.innerHTML = `
      <div class="saved-roadmap-card text-center" style="padding: 3rem 1.5rem;">
        <i data-lucide="compass" class="icon-lg text-muted" style="margin: 0 auto 1rem;"></i>
        <h3 style="font-size: 1.2rem; font-weight: 800; margin-bottom: 0.5rem;">No Saved Roadmaps Yet</h3>
        <p style="color: var(--text-muted); max-width: 500px; margin: 0 auto 1.5rem;">
          Generate a roadmap using the AI Career Guide or 15-Point Profile Builder, and click "Save to My Roadmaps" to track your progress.
        </p>
        <button class="btn btn-primary" onclick="navigateToSection('ai-guide')">
          <i data-lucide="sparkles" class="icon-sm"></i> Build a Roadmap
        </button>
      </div>
    `;
    refreshIcons();
    return;
  }

  container.innerHTML = AppState.savedRoadmaps.map((item, roadmapIdx) => {
    const totalSteps = item.steps.length;
    const completedSteps = item.steps.filter(s => s.done).length;
    const progressPercent = Math.round((completedSteps / totalSteps) * 100);

    return `
      <div class="saved-roadmap-card">
        <div style="display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 0.75rem;">
          <div>
            <div class="badge badge-primary">ACTIVE CAREER GOAL</div>
            <h3 style="font-size: 1.3rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">${escapeHtml(item.goal)}</h3>
            <span style="font-size: 0.78rem; color: var(--text-muted);">Saved on ${escapeHtml(item.createdAt)}</span>
          </div>
          <button class="btn btn-secondary" style="padding: 0.35rem 0.65rem; font-size: 0.78rem;" onclick="deleteSavedRoadmap('${item.id}')">
            <i data-lucide="trash-2" class="icon-xs text-danger"></i> Remove
          </button>
        </div>

        <div>
          <div style="display: flex; justify-content: space-between; font-size: 0.85rem; font-weight: 700;">
            <span>Milestone Progress</span>
            <span style="color: var(--primary);">${progressPercent}% Completed</span>
          </div>
          <div class="progress-bar-container">
            <div class="progress-bar-fill" style="width: ${progressPercent}%;"></div>
          </div>
        </div>

        <div style="margin-top: 1rem;">
          <h4 style="font-size: 0.95rem; font-weight: 700; margin-bottom: 0.5rem;">Action Checklist:</h4>
          ${item.steps.map((step, stepIdx) => `
            <label class="checklist-item ${step.done ? 'completed' : ''}">
              <input type="checkbox" ${step.done ? 'checked' : ''} onchange="toggleStep('${item.id}', ${stepIdx})">
              <span>${escapeHtml(step.title)}</span>
            </label>
          `).join('')}
        </div>
      </div>
    `;
  }).join('');
  refreshIcons();
}

function toggleStep(roadmapId, stepIndex) {
  const rm = AppState.savedRoadmaps.find(r => r.id === roadmapId);
  if (rm && rm.steps[stepIndex]) {
    rm.steps[stepIndex].done = !rm.steps[stepIndex].done;
    localStorage.setItem('cc_roadmaps', JSON.stringify(AppState.savedRoadmaps));
    renderSavedRoadmaps();
  }
}

function deleteSavedRoadmap(roadmapId) {
  AppState.savedRoadmaps = AppState.savedRoadmaps.filter(r => r.id !== roadmapId);
  localStorage.setItem('cc_roadmaps', JSON.stringify(AppState.savedRoadmaps));
  renderSavedRoadmaps();
}

// Utilities
function escapeHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#039;');
}

function formatMarkdown(text) {
  if (!text) return '';
  return text
    .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
    .replace(/\*(.*?)\*/g, '<em>$1</em>')
    .replace(/\n\n/g, '<br><br>')
    .replace(/\n- /g, '<br>• ')
    .replace(/\n/g, '<br>');
}

// ==========================================
// 10. ADMIN VERIFICATION CONSOLE
// ==========================================
function openAdminModal() {
  const modal = document.getElementById('admin-modal');
  const tbody = document.getElementById('admin-notifs-tbody');
  const notifs = AppState.datasets.allNotifications || [];
  loadAdminSourcesStatus();

  tbody.innerHTML = notifs.map(n => `
    <tr>
      <td><strong>${escapeHtml(n.title)}</strong><br><small style="color: var(--text-muted);">${escapeHtml(n.organization)}</small></td>
      <td><span class="badge badge-primary">${escapeHtml(n.category)}</span></td>
      <td>
        <select id="status-select-${n.id}" style="padding: 0.2rem 0.4rem; font-size: 0.75rem; border-radius: 4px; border: 1px solid var(--border-color); background: var(--bg-surface); color: var(--text-main);">
          <option value="OPEN" ${n.status === 'OPEN' ? 'selected' : ''}>OPEN</option>
          <option value="LIVE" ${n.status === 'LIVE' ? 'selected' : ''}>LIVE</option>
          <option value="CLOSING_SOON" ${n.status === 'CLOSING_SOON' ? 'selected' : ''}>CLOSING_SOON</option>
          <option value="UPCOMING" ${n.status === 'UPCOMING' ? 'selected' : ''}>UPCOMING</option>
          <option value="RESULT" ${n.status === 'RESULT' ? 'selected' : ''}>RESULT</option>
          <option value="CLOSED" ${n.status === 'CLOSED' ? 'selected' : ''}>CLOSED</option>
        </select>
      </td>
      <td><small>${new Date(n.last_verified_at).toLocaleDateString()}</small></td>
      <td>
        <button class="btn btn-primary" style="padding: 0.25rem 0.55rem; font-size: 0.72rem;" onclick="adminVerifyNotification('${n.id}')">
          <i data-lucide="check" class="icon-xs"></i> Verify Now
        </button>
      </td>
    </tr>
  `).join('');

  modal.classList.remove('hidden');
  refreshIcons();
}

function closeAdminModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('close-btn')) return;
  document.getElementById('admin-modal').classList.add('hidden');
}

async function adminVerifyNotification(id) {
  const selectElem = document.getElementById(`status-select-${id}`);
  const newStatus = selectElem ? selectElem.value : null;

  try {
    const res = await fetch('/api/admin/verify', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id: id, status: newStatus })
    });
    const result = await res.json();
    if (result.success) {
      alert(`Notification verified and timestamp updated successfully! Ticker refreshed.`);
      // Reload notifications & ticker
      const notifsRes = await fetch('/api/notifications/all').then(r => r.json());
      AppState.datasets.allNotifications = notifsRes.notifications || [];
      renderNotificationsCenter();
      initTicker();
      openAdminModal(); // Refresh modal view
    } else {
      alert('Error updating notification: ' + result.message);
    }
  } catch (err) {
    alert('Verification request failed.');
  }
}


// ==========================================
// 11. "MY CAREER RADAR" CONTROLLER
// ==========================================

const DEFAULT_RADAR_PROFILE = {
  profile_id: 'prof_' + Math.random().toString(36).substring(2, 9),
  qualification: 'B.Tech',
  stream_or_branch: 'CSE',
  completion_status: 'Final Year',
  state: 'All India / National',
  completion_year: '2026',
  category: 'General',
  interests: ['Software / IT Roles', 'Higher Studies', 'Government Jobs', 'PSU Careers', 'GATE', 'Scholarships / Financial Aid']
};

function getStoredRadarProfile() {
  if (AppState.radarProfile) return AppState.radarProfile;
  const stored = localStorage.getItem('cc_radar_profile');
  if (stored) {
    try {
      AppState.radarProfile = JSON.parse(stored);
      return AppState.radarProfile;
    } catch (e) {
      return DEFAULT_RADAR_PROFILE;
    }
  }
  return DEFAULT_RADAR_PROFILE;
}

function setStoredRadarProfile(profile) {
  AppState.radarProfile = profile;
  try {
    localStorage.setItem('cc_radar_profile', JSON.stringify(profile));
  } catch (e) {}
}

function initCareerRadar() {
  const profile = getStoredRadarProfile();
  updateRadarProfileChip(profile);
  refreshRadarMatches();
  loadRadarAlerts();
}

function updateRadarProfileChip(profile) {
  const chip = document.getElementById('radar-profile-chip');
  if (chip && profile) {
    const branchPart = profile.stream || profile.branch || profile.stream_or_branch || 'General';
    const statusPart = profile.current_status || profile.completion_status ? ` • ${profile.current_status || profile.completion_status}` : '';
    const statePart = profile.home_state || profile.state || 'All India / National';
    chip.textContent = `${profile.qualification} (${branchPart}${statusPart}) • ${statePart}`;
  }
}

function populateRadarBranchOptions(qual, selectedValue) {
  const branchSelect = document.getElementById('radar-input-branch');
  if (!branchSelect) return;
  const optData = window.APP_OPTIONS || APP_OPTIONS;
  const branches = (optData.branches_by_qual && optData.branches_by_qual[qual]) || optData.btech_branches || ['CSE'];

  branchSelect.innerHTML = branches.map(b => `<option value="${escapeHtml(b)}">${escapeHtml(b)}</option>`).join('');

  if (selectedValue && branches.includes(selectedValue)) {
    branchSelect.value = selectedValue;
  } else if (branches.length > 0) {
    branchSelect.value = branches[0];
  }
}

function openRadarProfileModal() {
  const profile = getStoredRadarProfile();
  const qualSelect = document.getElementById('radar-input-qual');
  const statusSelect = document.getElementById('radar-input-status');
  const stateSelect = document.getElementById('radar-input-state');
  const yearSelect = document.getElementById('radar-input-year');

  const curQual = profile.qualification || 'B.Tech';
  if (qualSelect) qualSelect.value = curQual;
  populateRadarBranchOptions(curQual, profile.stream_or_branch || 'CSE');

  if (statusSelect) statusSelect.value = profile.completion_status || 'Final Year';
  if (stateSelect) stateSelect.value = profile.state || 'All India / National';
  if (yearSelect) yearSelect.value = profile.completion_year || '2026';

  // Check interest checkboxes
  const interestBoxes = document.querySelectorAll('input[name="radar-interest"]');
  const userInterests = Array.isArray(profile.interests) ? profile.interests : [];
  interestBoxes.forEach(box => {
    box.checked = userInterests.includes(box.value);
  });

  const modal = document.getElementById('radar-profile-modal');
  if (modal) modal.classList.remove('hidden');
  refreshIcons();
}

function closeRadarProfileModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('close-btn')) return;
  const modal = document.getElementById('radar-profile-modal');
  if (modal) modal.classList.add('hidden');
}

function handleRadarQualChange() {
  const qual = document.getElementById('radar-input-qual')?.value || 'B.Tech';
  populateRadarBranchOptions(qual);
}

async function saveRadarProfile() {
  const existing = getStoredRadarProfile();
  const qual = document.getElementById('radar-input-qual')?.value || 'B.Tech';
  const branch = document.getElementById('radar-input-branch')?.value?.trim() || 'CSE';
  const status = document.getElementById('radar-input-status')?.value || 'Final Year';
  const state = document.getElementById('radar-input-state')?.value || 'All India / National';
  const year = document.getElementById('radar-input-year')?.value || '2026';

  const selectedInterests = [];
  document.querySelectorAll('input[name="radar-interest"]:checked').forEach(box => {
    selectedInterests.push(box.value);
  });

  const updatedProfile = {
    ...existing,
    qualification: qual,
    stream_or_branch: branch,
    completion_status: status,
    state: state,
    completion_year: year,
    interests: selectedInterests
  };

  setStoredRadarProfile(updatedProfile);
  updateRadarProfileChip(updatedProfile);
  closeRadarProfileModal();

  // Send to backend and scan
  try {
    const res = await fetch('/api/radar/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(updatedProfile)
    });
    const data = await res.json();
    if (data.status === 'success') {
      renderRadarMatches(data.matches || []);
      loadRadarAlerts();
    }
  } catch (err) {
    console.error('Radar profile save error:', err);
    refreshRadarMatches();
  }
}

async function refreshRadarMatches() {
  const profile = getStoredRadarProfile();
  const container = document.getElementById('radar-matches-container');
  const countNum = document.getElementById('radar-count-num');
  
  if (container) {
    container.innerHTML = `
      <div class="radar-loading-state" style="grid-column: 1 / -1; text-align: center; padding: 2rem;">
        <p style="color: var(--text-muted); font-size: 0.9rem;">Scanning verified official portals (.gov.in, .nic.in, .ac.in) for your profile...</p>
      </div>
    `;
  }

  try {
    const res = await fetch('/api/radar/matches', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(profile)
    });
    const data = await res.json();
    if (data.status === 'success') {
      renderRadarMatches(data.matches || []);
      if (countNum) countNum.textContent = data.total_matches || 0;
    }
  } catch (err) {
    console.error('Error scanning radar matches:', err);
    if (container) {
      container.innerHTML = `<p style="grid-column: 1 / -1; color: var(--text-muted); text-align: center; padding: 1.5rem;">Unable to load radar scan. Verify connection.</p>`;
    }
  }
}

function renderRadarMatches(matches) {
  const container = document.getElementById('radar-matches-container');
  const countNum = document.getElementById('radar-count-num');
  if (countNum) countNum.textContent = matches.length;

  if (!container) return;

  if (!matches || matches.length === 0) {
    container.innerHTML = `
      <div style="grid-column: 1 / -1; text-align: center; padding: 2.5rem 1rem; background: var(--bg-surface-muted); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
        <i data-lucide="shield-check" class="icon-lg text-primary" style="margin-bottom: 0.5rem;"></i>
        <h4 style="font-size: 1rem; color: var(--text-main); margin-bottom: 0.35rem;">${t("radar.no_matches_title", "No Active Deadlines Currently Pending for Your Profile")}</h4>
        <p style="font-size: 0.82rem; color: var(--text-secondary); max-width: 480px; margin: 0 auto;">${t("radar.no_matches_desc", "In accordance with CareerCompass integrity principles, we only display active windows verified from official portals. Check back or adjust your target career goals in profile settings.")}</p>
        <button class="btn btn-outline-primary btn-sm" style="margin-top: 1rem;" onclick="openRadarProfileModal()">
          <i data-lucide="sliders" class="icon-xs"></i> ${t("radar.adjust_goals", "Adjust Goals / Interests")}
        </button>
      </div>
    `;
    refreshIcons();
    return;
  }

  const hasUrgentOrExam = matches.some(m => (m.urgency && m.urgency.toLowerCase() === 'high') || (m.days_remaining !== null && m.days_remaining <= 30) || m.category === 'Entrance Exam');
  const alertBannerHtml = hasUrgentOrExam ? `
    <div class="radar-prep-alert-banner" style="grid-column: 1 / -1; margin-bottom: 0.75rem; padding: 1rem 1.25rem; background: linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(99, 102, 241, 0.08)); border: 1px solid var(--border-color); border-left: 4px solid var(--primary); border-radius: var(--radius-md); display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
      <div style="display: flex; align-items: center; gap: 0.75rem;">
        <i data-lucide="compass" class="icon-md text-primary"></i>
        <div>
          <strong style="color: var(--text-main); font-size: 0.95rem;">Upcoming Exam & Target Deadlines Detected!</strong>
          <p style="margin: 0; font-size: 0.8rem; color: var(--text-secondary);">Prepare effectively with verified 24-point blueprints, official past papers, and curated practice resources.</p>
        </div>
      </div>
      <button class="btn btn-primary btn-sm" onclick="navigateToSection('exam-prep')" style="display: inline-flex; align-items: center; gap: 0.35rem;">
        <i data-lucide="arrow-right" class="icon-xs"></i> Open Preparation Hub
      </button>
    </div>
  ` : '';

  container.innerHTML = alertBannerHtml + matches.map((m, idx) => {
    const urgencyClass = (m.urgency || 'NORMAL').toLowerCase();
    const daysText = m.days_remaining !== null && m.days_remaining !== undefined 
      ? (m.days_remaining <= 0 ? t('radar.closes_today', 'Closes Today') : `${m.days_remaining} ${t('radar.days_left', 'Days Left')}`)
      : (m.status === 'LIVE' ? translateDynamic('Admissions LIVE') : t('radar.active_cycle', 'Active Cycle'));

    const formattedStart = m.start_datetime ? new Date(m.start_datetime).toLocaleDateString() : 'Announced';
    const formattedEnd = m.end_datetime ? new Date(m.end_datetime).toLocaleDateString() : 'See Brochure';

    return `
      <div class="radar-match-card urgency-${urgencyClass}">
        <div>
          <div class="card-top-row">
            <span class="match-category-tag">${escapeHtml(m.category || 'General')}</span>
            <span class="urgency-pill ${urgencyClass}">
              <i data-lucide="${urgencyClass === 'high' ? 'alert-triangle' : 'clock'}" class="icon-xs"></i>
              ${daysText}
            </span>
          </div>
          
          <h3 class="radar-card-title">${escapeHtml(m.title)}</h3>
          <p class="radar-card-org">
            <i data-lucide="landmark" class="icon-xs text-muted"></i>
            ${escapeHtml(m.organization)}
          </p>

          <!-- Why am I seeing this? -->
          <div class="why-seeing-box">
            <div class="why-seeing-header" onclick="toggleWhySeeing(${idx})">
              <i data-lucide="check-circle-2" class="icon-xs text-success"></i>
              <span>${t("radar.why_seeing", "Why am I seeing this?")}</span>
              <i id="why-icon-${idx}" data-lucide="chevron-down" class="icon-xs" style="margin-left: auto;"></i>
            </div>
            <ul id="why-list-${idx}" class="why-seeing-reasons hidden">
              ${(m.match_reasons || []).map(r => `
                <li class="why-reason-item">
                  <span class="check-icon">✓</span>
                  <span>${escapeHtml(r)}</span>
                </li>
              `).join('')}
            </ul>
          </div>

          <div class="radar-dates-grid">
            <div>
              <span class="date-cell-label">${t("common.deadline", "Deadline / End")}</span>
              <span class="date-cell-val">${formattedEnd}</span>
            </div>
            <div>
              <span class="date-cell-label">${t("common.exam_date", "Exam / Event")}</span>
              <span class="date-cell-val">${escapeHtml(m.exam_date || 'Scheduled')}</span>
            </div>
          </div>
        </div>

        <div class="radar-card-actions">
          <a href="${escapeHtml(m.official_source)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm flex-1" style="display: inline-flex; justify-content: center; align-items: center; gap: 4px;">
            <i data-lucide="external-link" class="icon-xs"></i> ${t("common.official_portal", "Official Portal")}
          </a>
          <button class="btn btn-outline-primary btn-sm" onclick="openPrepHubForOpportunity('${escapeHtml(m.title)}', '${escapeHtml(m.category || '')}')" title="Study & Practice in Preparation Hub">
            <i data-lucide="book-open" class="icon-xs"></i> Prepare
          </button>
          <button class="btn btn-secondary btn-sm" onclick="askAIAboutRadarOpp('${escapeHtml(m.opportunity_id)}')" title="Ask AI About This">
            <i data-lucide="sparkles" class="icon-xs"></i>
          </button>
        </div>
      </div>
    `;
  }).join('');

  refreshIcons();
}

function toggleWhySeeing(idx) {
  const list = document.getElementById(`why-list-${idx}`);
  const icon = document.getElementById(`why-icon-${idx}`);
  if (list) {
    list.classList.toggle('hidden');
  }
}

function askAIAboutRadarOpp(oppId) {
  const notifs = AppState.datasets.allNotifications || [];
  const opp = notifs.find(n => n.id === oppId);
  navigateToSection('ai-guide');
  const input = document.getElementById('ai-chat-input');
  if (input && opp) {
    input.value = `Tell me about the eligibility, preparation strategy, and important milestones for ${opp.title} (${opp.organization}).`;
    input.focus();
  }
}

// ==========================================
// 12. RADAR ALERTS BELL & DRAWER
// ==========================================

function toggleRadarDrawer() {
  const drawer = document.getElementById('radar-alerts-drawer');
  if (!drawer) return;
  drawer.classList.toggle('hidden');
  if (!drawer.classList.contains('hidden')) {
    loadRadarAlerts();
  }
}

async function loadRadarAlerts() {
  const profile = getStoredRadarProfile();
  const url = (profile && profile.profile_id) ? `/api/radar/alerts?id=${encodeURIComponent(profile.profile_id)}` : '/api/radar/alerts';

  try {
    const res = await fetch(url);
    const data = await res.json();
    if (data.status === 'success') {
      renderRadarAlerts(data.alerts || [], data.unread_count || 0);
    }
  } catch (err) {
    console.error('Error fetching radar alerts:', err);
  }
}

function renderRadarAlerts(alerts, unreadCount) {
  const badge = document.getElementById('radar-unread-badge');
  const drawerCount = document.getElementById('drawer-unread-count');
  const listContainer = document.getElementById('radar-alerts-list');

  if (badge) {
    if (unreadCount > 0) {
      badge.textContent = unreadCount > 9 ? '9+' : unreadCount;
      badge.classList.remove('hidden');
    } else {
      badge.classList.add('hidden');
    }
  }

  if (drawerCount) {
    drawerCount.textContent = `${unreadCount} New`;
  }

  if (!listContainer) return;

  if (!alerts || alerts.length === 0) {
    listContainer.innerHTML = `
      <div class="drawer-empty-state">
        <i data-lucide="bell-off" class="icon-lg text-muted" style="margin-bottom: 0.5rem;"></i>
        <p>No new alerts. Configure your Career Radar profile to receive immediate deadline notifications.</p>
      </div>
    `;
    refreshIcons();
    return;
  }

  listContainer.innerHTML = alerts.map(a => `
    <div class="drawer-alert-item ${a.is_read ? '' : 'unread'}" onclick="window.open('${escapeHtml(a.official_source)}', '_blank')">
      <div class="drawer-alert-header">
        <span>${escapeHtml(a.organization)}</span>
        <span>${new Date(a.created_at).toLocaleDateString()}</span>
      </div>
      <h4 class="drawer-alert-title">${escapeHtml(a.title)}</h4>
      <p class="drawer-alert-msg">${escapeHtml(a.message)}</p>
    </div>
  `).join('');

  refreshIcons();
}

async function markAllAlertsRead() {
  const profile = getStoredRadarProfile();
  try {
    await fetch('/api/radar/mark-read', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile_id: profile?.profile_id })
    });
    loadRadarAlerts();
  } catch (err) {
    console.error('Error marking alerts read:', err);
  }
}

// ==========================================
// 13. ADMIN CONSOLE AUTO-UPDATER
// ==========================================

function switchAdminTab(tab) {
  const tabSources = document.getElementById('admin-tab-sources');
  const tabNotifs = document.getElementById('admin-tab-notifs');
  const viewSources = document.getElementById('admin-view-sources');
  const viewNotifs = document.getElementById('admin-view-notifs');

  if (tab === 'sources') {
    tabSources.classList.add('active');
    tabNotifs.classList.remove('active');
    viewSources.classList.remove('hidden');
    viewNotifs.classList.add('hidden');
    loadAdminSourcesStatus();
  } else {
    tabNotifs.classList.add('active');
    tabSources.classList.remove('active');
    viewNotifs.classList.remove('hidden');
    viewSources.classList.add('hidden');
  }
}

async function loadAdminSourcesStatus() {
  const tbody = document.getElementById('admin-sources-tbody');
  const changesList = document.getElementById('admin-changes-list');

  try {
    const res = await fetch('/api/admin/updater-status');
    const data = await res.json();
    if (data.status === 'success') {
      if (tbody) {
        tbody.innerHTML = (data.registry || []).map(s => `
          <tr>
            <td><strong>${escapeHtml(s.source_name)}</strong><br><small style="color: var(--text-muted);">${escapeHtml(s.organization)}</small></td>
            <td><a href="${escapeHtml(s.official_url)}" target="_blank" rel="noopener noreferrer" style="color: var(--primary); font-size: 0.75rem;">${escapeHtml(s.official_url)}</a></td>
            <td><span class="badge badge-primary">${escapeHtml(s.category)}</span></td>
            <td><span class="badge badge-${s.status === 'VERIFIED_ACTIVE' ? 'success' : (s.status === 'DEGRADED' ? 'warning' : 'info')}">${escapeHtml(s.status)}</span></td>
            <td><small>${s.last_checked_at ? new Date(s.last_checked_at).toLocaleTimeString() : 'Never'}</small></td>
          </tr>
        `).join('');
      }

      if (changesList) {
        if (!data.recent_changes || data.recent_changes.length === 0) {
          changesList.innerHTML = '<span style="color: var(--text-muted);">No state transitions logged yet.</span>';
        } else {
          changesList.innerHTML = data.recent_changes.map(c => `
            <div style="padding: 2px 0; border-bottom: 1px solid var(--border-color);">
              <span style="color: #3b82f6;">[${escapeHtml(c.type)}]</span> 
              <span style="color: var(--text-muted); font-size: 0.72rem;">${c.timestamp ? new Date(c.timestamp).toLocaleTimeString() : ''}</span>: 
              ${(c.details || []).map(d => escapeHtml(d)).join('; ')}
            </div>
          `).join('');
        }
      }
    }
  } catch (err) {
    console.error('Error fetching updater status:', err);
  }
}

async function triggerAdminUpdate() {
  const btn = document.getElementById('admin-run-updater-btn');
  const resultDiv = document.getElementById('admin-updater-result');

  if (btn) {
    btn.disabled = true;
    btn.innerHTML = '<div class="loading-spinner" style="width: 14px; height: 14px; display: inline-block;"></div> Running Verification...';
  }

  try {
    const res = await fetch('/api/admin/trigger-update', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({})
    });
    const data = await res.json();
    if (data.status === 'success' && data.report) {
      const rep = data.report;
      if (resultDiv) {
        resultDiv.classList.remove('hidden');
        resultDiv.innerHTML = `
          <strong>Verification Run Complete:</strong> Checked ${rep.sources_checked} official sources (${rep.sources_successful} online, ${rep.sources_failed} offline). 
          Extracted ${rep.opportunities_extracted} items (${rep.validated_opportunities} validated, ${rep.new_count} new, ${rep.modified_count} updated).
          Dispatched ${rep.dispatched_radar_alerts || 0} alerts to student radars.
        `;
      }
      // Refresh notifications, ticker, and radar
      loadAllDatasets();
      refreshRadarMatches();
      loadAdminSourcesStatus();
    }
  } catch (err) {
    alert('Verification run failed.');
  } finally {
    if (btn) {
      btn.disabled = false;
      btn.innerHTML = '<i data-lucide="play" class="icon-xs"></i> Run Verification Cycle Now';
      refreshIcons();
    }
  }
}


// ==========================================
// 6B. B.TECH SPECIALIZED CAREER CONTROLLER
// ==========================================

function switchBTechMode(mode) {
  AppState.btechState.mode = mode;
  renderBTechSection();
}

function switchBTechBranch(branch) {
  AppState.btechState.branch = branch;
  renderBTechSection();
}

function switchBTechPathway(pathwayId) {
  AppState.btechState.activePathway = pathwayId;

  // 1. Update DOM cards directly so active state reflects immediately
  const cards = document.querySelectorAll('.btech-pathway-card');
  cards.forEach(card => {
    const cardPathwayId = card.getAttribute('data-pathway-id');
    const isSelected = (cardPathwayId === pathwayId);

    if (isSelected) {
      card.classList.add('highlighted-card');
      card.style.border = '2px solid var(--primary)';
      card.style.boxShadow = '0 4px 12px rgba(37, 99, 235, 0.15)';
    } else {
      card.classList.remove('highlighted-card');
      card.style.border = '1px solid var(--border-color)';
      card.style.boxShadow = 'none';
    }

    const badge = card.querySelector('.pathway-badge');
    if (badge) {
      badge.className = `badge pathway-badge ${isSelected ? 'badge-primary' : 'badge-info'}`;
    }

    const btn = card.querySelector('.pathway-action-btn');
    if (btn) {
      btn.className = `btn ${isSelected ? 'btn-primary' : 'btn-secondary'} btn-sm w-full pathway-action-btn`;
      const btnSpan = btn.querySelector('span');
      if (btnSpan) {
        btnSpan.textContent = isSelected ? 'Currently Viewing Details ↓' : (typeof t === 'function' ? t('btech_careers.explore_pathway', 'Explore Pathway →') : 'Explore Pathway →');
      }
    }
  });

  // 2. Render details for selected pathway
  renderBTechPathwayDetail();

  // 3. Smoothly scroll down to details
  const el = document.getElementById('btech-pathway-detail-container');
  if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

function filterBTechJobCategory(catId) {
  AppState.btechState.jobCategory = catId;
  renderBTechJobsSection();
}

function filterBTechCompanyType(typeId) {
  AppState.btechState.companyType = typeId;
  renderBTechCompaniesSection();
}

function searchBTechJobs() {
  const input = document.getElementById('btech-job-search-input');
  AppState.btechState.jobSearch = input ? input.value.trim().toLowerCase() : '';
  renderBTechJobsSection();
}

async function renderBTechSection() {
  const container = document.getElementById('career-paths-content');
  if (!container) return;

  const mode = AppState.btechState.mode || 'completed';
  const branch = AppState.btechState.branch || 'CSE';
  const allBranches = (window.APP_OPTIONS && window.APP_OPTIONS.btech_branches) || APP_OPTIONS.btech_branches || [];
  const quickBranches = ['CSE', 'Information Technology (IT)', 'ECE', 'EEE', 'Mechanical Engineering', 'Civil Engineering', 'AI & ML', 'Data Science', 'Cyber Security', 'Chemical Engineering', 'Biotechnology', 'Aerospace / Aeronautical Engineering', 'Other'];

  let html = `
    <!-- B.Tech Context Switcher -->
    <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 1.25rem; margin-bottom: 2rem;">
      <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 1rem; margin-bottom: 1rem;">
        <div>
          <span class="badge badge-primary" style="margin-bottom: 0.35rem;">CONTEXT SELECTOR</span>
          <h3 style="font-size: 1.2rem; font-weight: 800; color: var(--text-main); margin: 0;">What is your current situation?</h3>
        </div>
        <div class="tab-pill-container" style="margin: 0;">
          <button class="tab-pill ${mode === 'completed' ? 'active' : ''}" onclick="switchBTechMode('completed')">
            <i data-lucide="graduation-cap" class="icon-xs"></i> <span>${t('btech_careers.context_completed', '🎓 I have completed B.Tech / Final Year')}</span>
          </button>
          <button class="tab-pill ${mode === 'aspirant' ? 'active' : ''}" onclick="switchBTechMode('aspirant')">
            <i data-lucide="book-open" class="icon-xs"></i> <span>${t('btech_careers.context_aspirant', '📚 Exploring B.Tech as a Degree to Study')}</span>
          </button>
        </div>
      </div>
  `;

  if (mode === 'aspirant') {
    // Aspirant Discipline Guide
    const sectionData = AppState.datasets.careerPaths['btech'];
    const branchItems = sectionData ? (sectionData.branches || []) : [];
    html += `
        <p style="color: var(--text-secondary); font-size: 0.88rem; margin-bottom: 1.25rem;">
          Exploring engineering disciplines for prospective students after 10+2 / Intermediate MPC or Polytechnic Diploma. Learn about core subjects, labs, and prospective outcomes before choosing your college major.
        </p>
      </div>
      <div class="cards-grid">
    `;
    branchItems.forEach(item => {
      html += `
        <div class="card">
          <div class="card-header-row">
            <h4 class="card-title">${escapeHtml(item.name)}</h4>
            <span class="badge badge-info">4-Year Degree</span>
          </div>
          <div class="card-body">
            <p><strong>Prospective Roles:</strong></p>
            <ul style="padding-left: 1.25rem; margin-top: 0.25rem; font-size: 0.85rem;">
              ${(item.roles || []).map(r => `<li>${escapeHtml(r)}</li>`).join('')}
            </ul>
            ${item.gate_prospects ? `<p style="margin-top: 0.75rem; font-size: 0.82rem; color: var(--text-secondary);"><strong>GATE & PSU Pathways:</strong> ${escapeHtml(item.gate_prospects)}</p>` : ''}
          </div>
          <div class="card-footer">
            <button class="btn btn-primary btn-sm" onclick="startAIWithTopic('${escapeHtml(item.name)}')">
              <i data-lucide="sparkles" class="icon-xs"></i> Plan this Branch with AI
            </button>
          </div>
        </div>
      `;
    });
    html += `</div>`;
    container.innerHTML = html;
    refreshIcons();
    return;
  }

  // MODE: COMPLETED B.TECH / FINAL YEAR
  html += `
      <!-- Step 1: Branch Input Selector -->
      <div style="padding-top: 0.75rem; border-top: 1px solid var(--border-color);">
        <div style="display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 0.75rem; margin-bottom: 0.65rem;">
          <label style="font-size: 0.88rem; font-weight: 700; color: var(--primary); display: flex; align-items: center; gap: 0.4rem; margin: 0;">
            <i data-lucide="filter" class="icon-xs"></i>
            <span>${t('btech_careers.branch_prompt', 'What was your B.Tech branch? (Used as filter):')}</span>
            <strong style="color: var(--text-main); font-weight: 800; margin-left: 0.35rem;">[${escapeHtml(branch)}]</strong>
          </label>
          <div style="display: flex; align-items: center; gap: 0.5rem;">
            <label for="btech-branch-select" style="font-size: 0.82rem; color: var(--text-muted); font-weight: 600;">All Branches:</label>
            <select id="btech-branch-select" class="form-select" style="font-size: 0.84rem; padding: 0.35rem 0.65rem; border-radius: 6px; border: 1px solid var(--border-color); background: var(--bg-surface); color: var(--text-main); min-width: 220px;" onchange="switchBTechBranch(this.value)">
              ${allBranches.map(b => `<option value="${escapeHtml(b)}" ${branch === b ? 'selected' : ''}>${escapeHtml(b)}</option>`).join('')}
            </select>
          </div>
        </div>
        <div class="filter-chips" style="margin-bottom: 0;">
          ${quickBranches.map(b => `
            <button class="filter-chip ${branch === b ? 'active' : ''}" onclick="switchBTechBranch('${b}')">${escapeHtml(b)}</button>
          `).join('')}
        </div>
      </div>
    </div>

    <!-- Step 2: "WHAT DO YOU WANT TO DO AFTER B.TECH?" 9 Major Pathways -->
    <div style="margin-bottom: 1.5rem; text-align: center;">
      <h2 style="font-size: 1.45rem; font-weight: 800; color: var(--text-main); margin-bottom: 0.35rem;">
        ${t('btech_careers.what_next_title', 'WHAT DO YOU WANT TO DO AFTER B.TECH?')}
      </h2>
      <p style="color: var(--text-secondary); font-size: 0.9rem; max-width: 680px; margin: 0 auto;">
        ${t('btech_careers.what_next_subtitle', 'Select a major pathway below to explore roles, entrance exams, or higher education tailored to your branch.')}
      </p>
      <div style="margin-top: 0.75rem;">
        <button class="btn btn-outline-primary btn-sm" onclick="openPathwayCompareModal('comp-job-vs-mtech')">
          <i data-lucide="scale" class="icon-xs"></i> <span>${t('btech_careers.compare_btn', '⚖️ Compare Pathways Side-by-Side')}</span>
        </button>
      </div>
    </div>

    <!-- 9 Major Pathway Cards Grid -->
    <div class="cards-grid mb-4">
  `;

  const pathways = AppState.datasets.btechPathways || [];
  pathways.forEach(p => {
    const isSelected = (AppState.btechState.activePathway === p.id);
    html += `
      <div id="pathway-card-${p.id}" data-pathway-id="${p.id}" class="card btech-pathway-card ${isSelected ? 'highlighted-card' : ''}" style="cursor: pointer; transition: all 0.2s ease; border: ${isSelected ? '2px solid var(--primary)' : '1px solid var(--border-color)'}; ${isSelected ? 'box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);' : ''}" onclick="switchBTechPathway('${p.id}')">
        <div class="card-header-row">
          <div style="display: flex; align-items: center; gap: 0.65rem;">
            <div style="width: 36px; height: 36px; border-radius: 8px; background: var(--bg-hover); display: flex; align-items: center; justify-content: center; color: var(--primary);">
              <i data-lucide="${p.icon || 'compass'}" class="icon-sm"></i>
            </div>
            <h4 class="card-title" style="margin: 0; font-size: 1.05rem;">${escapeHtml(p.title)}</h4>
          </div>
          <span class="badge pathway-badge ${isSelected ? 'badge-primary' : 'badge-info'}">${escapeHtml(p.badge)}</span>
        </div>
        <div class="card-body">
          <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.65rem;">${escapeHtml(p.description)}</p>
          ${p.estimated_starting_ctc ? `<div style="font-size: 0.8rem; background: var(--bg-hover); padding: 0.45rem 0.65rem; border-radius: 6px; margin-bottom: 0.65rem;"><strong>Starting Scale:</strong> ${escapeHtml(p.estimated_starting_ctc)}</div>` : ''}
        </div>
        <div class="card-footer" style="padding-top: 0.65rem;">
          <button class="btn ${isSelected ? 'btn-primary' : 'btn-secondary'} btn-sm w-full pathway-action-btn" onclick="event.stopPropagation(); switchBTechPathway('${p.id}')">
            <span>${isSelected ? 'Currently Viewing Details ↓' : t('btech_careers.explore_pathway', 'Explore Pathway →')}</span>
          </button>
        </div>
      </div>
    `;
  });

  html += `
    </div>

    <!-- Dynamic Container for Active Pathway Details -->
    <div id="btech-pathway-detail-container" style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-lg); padding: 1.5rem; margin-top: 2rem;">
      <!-- Populated by renderBTechPathwayDetail() -->
    </div>
  `;

  container.innerHTML = html;
  refreshIcons();
  renderBTechPathwayDetail();
}

async function renderBTechPathwayDetail() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  const pathway = AppState.btechState.activePathway || 'job';
  const branch = AppState.btechState.branch || 'CSE';

  if (pathway === 'job') {
    renderBTechJobsSection();
  } else if (pathway === 'higher_studies') {
    renderBTechHigherStudiesSection();
  } else if (pathway === 'competitive_exams') {
    renderBTechGATEGuideSection();
  } else if (pathway === 'govt_psu') {
    renderBTechGovtPSUSection();
  } else if (pathway === 'defence') {
    renderBTechDefenceSection();
  } else if (pathway === 'entrepreneurship') {
    renderBTechEntrepreneurshipSection();
  } else if (pathway === 'study_abroad') {
    renderBTechStudyAbroadSection();
  } else if (pathway === 'upskilling') {
    renderBTechUpskillingSection();
  } else if (pathway === 'career_change') {
    renderBTechCareerChangeSection();
  }
}

// 1. JOBS SECTION
async function renderBTechJobsSection() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  const branch = AppState.btechState.branch || 'CSE';
  const cat = AppState.btechState.jobCategory || 'all';
  const search = AppState.btechState.jobSearch || '';

  let jobsRes;
  try {
    const res = await fetch(`/api/btech/jobs?branch=${encodeURIComponent(branch)}&category=${encodeURIComponent(cat)}&search=${encodeURIComponent(search)}`);
    jobsRes = await res.json();
  } catch (e) {
    jobsRes = { categories: [], total_roles: 0 };
  }

  const categories = jobsRes.categories || [];

  let html = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1.25rem; margin-bottom: 1.5rem;">
      <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 0.75rem;">
        <div>
          <span class="badge badge-primary">PATHWAY: PRIVATE & CORPORATE JOBS</span>
          <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">
            Job Roles for B.Tech ${escapeHtml(branch)} Graduates
          </h3>
          <p style="color: var(--text-secondary); font-size: 0.85rem; margin-top: 0.25rem;">
            Filtered by your branch (${escapeHtml(branch)}). Showing ${jobsRes.total_roles} verified role profiles across industry categories.
          </p>
        </div>
        <div style="display: flex; gap: 0.5rem;">
          <button class="btn btn-outline-primary btn-sm" onclick="openPathwayCompareModal('comp-job-vs-mtech')">
            <i data-lucide="scale" class="icon-xs"></i> Job vs M.Tech
          </button>
        </div>
      </div>

      <!-- Category Filter Chips -->
      <div style="margin-top: 1rem;">
        <label style="font-size: 0.82rem; font-weight: 700; color: var(--text-secondary); margin-bottom: 0.4rem; display: block;">
          ${t('btech_careers.filter_job_categories', 'Job Category:')}
        </label>
        <div class="filter-chips" style="margin-bottom: 0.75rem;">
          <button class="filter-chip ${cat === 'all' ? 'active' : ''}" onclick="filterBTechJobCategory('all')">${t('btech_careers.all_categories', 'All Categories')}</button>
          <button class="filter-chip ${cat === 'it_software' ? 'active' : ''}" onclick="filterBTechJobCategory('it_software')">IT & Software</button>
          <button class="filter-chip ${cat === 'data_ai' ? 'active' : ''}" onclick="filterBTechJobCategory('data_ai')">Data & AI</button>
          <button class="filter-chip ${cat === 'cyber_security' ? 'active' : ''}" onclick="filterBTechJobCategory('cyber_security')">Cyber Security</button>
          <button class="filter-chip ${cat === 'core_engineering' ? 'active' : ''}" onclick="filterBTechJobCategory('core_engineering')">Core Engineering</button>
          <button class="filter-chip ${cat === 'non_it_business' ? 'active' : ''}" onclick="filterBTechJobCategory('non_it_business')">Business & Consulting</button>
        </div>
      </div>

      <!-- Search Input -->
      <div class="search-box" style="margin-top: 0.75rem;">
        <i data-lucide="search" class="search-icon"></i>
        <input type="text" id="btech-job-search-input" placeholder="Search roles, tools, or skills (e.g. React, Python, VLSI, CAD, SOC, AWS)..." value="${escapeHtml(search)}" oninput="searchBTechJobs()">
      </div>
    </div>

    <!-- Job Roles Grid -->
    <div class="cards-grid mb-4">
  `;

  let renderedAny = false;
  categories.forEach(c => {
    (c.roles || []).forEach(r => {
      renderedAny = true;
      html += `
        <div class="card" style="display: flex; flex-direction: column;">
          <div class="card-header-row">
            <h4 class="card-title" style="font-size: 1.05rem;">${escapeHtml(r.name)}</h4>
            <span class="badge badge-info">${escapeHtml(c.name)}</span>
          </div>
          <div class="card-body" style="flex: 1;">
            <p style="font-size: 0.85rem; color: var(--text-secondary); margin-bottom: 0.65rem;">${escapeHtml(r.what_they_do)}</p>
            <div style="margin-bottom: 0.65rem;">
              <strong style="font-size: 0.8rem; color: var(--primary);">Key Skills:</strong>
              <div style="display: flex; flex-wrap: wrap; gap: 0.35rem; margin-top: 0.3rem;">
                ${(r.skills || []).slice(0, 4).map(s => `<span class="badge badge-secondary" style="font-size: 0.72rem;">${escapeHtml(s)}</span>`).join('')}
              </div>
            </div>
            <div style="font-size: 0.8rem; color: var(--text-muted);">
              <strong>Relevant Branches:</strong> ${(r.branches || []).join(', ')}
            </div>
          </div>
          <div class="card-footer" style="display: flex; justify-content: space-between; align-items: center; gap: 0.5rem;">
            <button class="btn btn-primary btn-sm" onclick="openJobRoleModal('${r.id}')">
              <i data-lucide="file-text" class="icon-xs"></i> <span>${t('btech_careers.view_role_details', 'View Role Blueprint')}</span>
            </button>
            <a href="${escapeHtml(r.official_careers_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" title="Explore Careers">
              <i data-lucide="external-link" class="icon-xs"></i>
            </a>
          </div>
        </div>
      `;
    });
  });

  if (!renderedAny) {
    html += `
      <div style="grid-column: 1 / -1; text-align: center; padding: 2.5rem; background: var(--bg-hover); border-radius: 8px;">
        <i data-lucide="search-x" class="icon-lg text-muted" style="margin-bottom: 0.5rem;"></i>
        <h4 style="font-size: 1rem; color: var(--text-main);">No roles match the selected branch and filter</h4>
        <p style="font-size: 0.82rem; color: var(--text-secondary); margin-top: 0.25rem;">Try selecting "All Categories" or clearing the search keyword.</p>
      </div>
    `;
  }

  html += `
    </div>

    <!-- Verified Company Directory Section -->
    <div id="btech-companies-container" style="border-top: 1px solid var(--border-color); padding-top: 1.5rem; margin-top: 2rem;">
      <!-- Populated by renderBTechCompaniesSection() -->
    </div>
  `;

  container.innerHTML = html;
  refreshIcons();
  renderBTechCompaniesSection();
}

function renderBTechCompaniesSection() {
  const container = document.getElementById('btech-companies-container');
  if (!container) return;

  const typeFilter = AppState.btechState.companyType || 'all';
  const companies = AppState.datasets.companies || [];

  const filtered = companies.filter(c => {
    if (typeFilter === 'all') return true;
    return (c.type || '').toLowerCase().includes(typeFilter.toLowerCase());
  });

  let html = `
    <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.75rem; margin-bottom: 1rem;">
      <div>
        <h4 style="font-size: 1.25rem; font-weight: 800; color: var(--text-main); margin: 0;">
          ${t('btech_careers.company_directory_title', 'Verified Company Directory')}
        </h4>
        <p style="color: var(--text-secondary); font-size: 0.85rem; margin-top: 0.25rem;">
          ${t('btech_careers.company_directory_subtitle', 'Authentic employer profiles with official careers and recruitment portal links.')}
        </p>
      </div>
      <div>
        <label style="font-size: 0.8rem; font-weight: 700; color: var(--text-secondary); margin-right: 0.5rem;">${t('btech_careers.filter_company_type', 'Company Type:')}</label>
        <select class="form-control" style="display: inline-block; width: auto; font-size: 0.8rem; padding: 0.35rem 0.65rem;" onchange="filterBTechCompanyType(this.value)">
          <option value="all" ${typeFilter === 'all' ? 'selected' : ''}>${t('btech_careers.all_company_types', 'All Types')}</option>
          <option value="IT Services" ${typeFilter === 'IT Services' ? 'selected' : ''}>IT Services & Consulting</option>
          <option value="Product" ${typeFilter === 'Product' ? 'selected' : ''}>Global Product MNCs</option>
          <option value="Core Engineering" ${typeFilter === 'Core Engineering' ? 'selected' : ''}>Core Engineering Conglomerates</option>
          <option value="Unicorn" ${typeFilter === 'Unicorn' ? 'selected' : ''}>Tech Startups & Unicorns</option>
          <option value="Government" ${typeFilter === 'Government' ? 'selected' : ''}>Public Sector / Aerospace R&D</option>
        </select>
      </div>
    </div>

    <div class="cards-grid">
  `;

  filtered.forEach(c => {
    html += `
      <div class="card">
        <div class="card-header-row">
          <h4 class="card-title">${escapeHtml(c.name)}</h4>
          <span class="badge badge-primary">${escapeHtml(c.type)}</span>
        </div>
        <div class="card-org">${escapeHtml(c.domain)}</div>
        <div class="card-body">
          <p style="font-size: 0.82rem; margin-bottom: 0.5rem;"><strong>Common Graduate Roles:</strong> ${(c.common_roles || []).slice(0, 3).join(', ')}</p>
          <div style="font-size: 0.8rem; margin-bottom: 0.5rem;">
            <strong>Verified Required Skills:</strong>
            <div style="display: flex; flex-wrap: wrap; gap: 0.3rem; margin-top: 0.25rem;">
              ${(c.verified_skills || []).slice(0, 4).map(s => `<span class="badge badge-secondary" style="font-size: 0.72rem;">${escapeHtml(s)}</span>`).join('')}
            </div>
          </div>
          <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.4rem;"><strong>Locations:</strong> ${(c.locations || []).slice(0, 3).join(', ')}</p>
          <small style="color: var(--text-muted); font-size: 0.72rem;">Last verified: ${escapeHtml(c.last_verified)}</small>
        </div>
        <div class="card-footer">
          <a href="${escapeHtml(c.official_website)}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary btn-sm" style="font-size: 0.78rem;">
            <i data-lucide="globe" class="icon-xs"></i> Official Site
          </a>
          <a href="${escapeHtml(c.official_careers_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm" style="font-size: 0.78rem;">
            <i data-lucide="external-link" class="icon-xs"></i> Careers Portal
          </a>
        </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
  refreshIcons();
}

// 2. HIGHER STUDIES SECTION
async function renderBTechHigherStudiesSection() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  let studies = [];
  try {
    const res = await fetch('/api/btech/higher-studies');
    const data = await res.json();
    studies = data.higher_studies || [];
  } catch (e) {
    studies = [];
  }

  let html = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <span class="badge badge-primary">PATHWAY: HIGHER STUDIES</span>
      <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">
        Master's, MBA & Doctoral Pathways After B.Tech
      </h3>
      <p style="color: var(--text-secondary); font-size: 0.85rem;">
        Detailed admission requirements, entrance examinations, funding stipends, and institutional routes.
      </p>
    </div>

    <div class="cards-grid">
  `;

  studies.forEach(hs => {
    html += `
      <div class="card">
        <div class="card-header-row">
          <h4 class="card-title">${escapeHtml(hs.degree)}</h4>
          <span class="badge badge-success">${escapeHtml(hs.duration)}</span>
        </div>
        <div class="card-body">
          <div class="card-meta-list" style="margin-bottom: 0.75rem;">
            <div class="card-meta-item"><span>Eligibility:</span> <strong>${escapeHtml(hs.eligibility)}</strong></div>
            <div class="card-meta-item"><span>Entrance Exams:</span> <strong>${(hs.entrance_exams || []).join(', ')}</strong></div>
            <div class="card-meta-item"><span>Financial Support:</span> <strong style="color: var(--status-open);">${escapeHtml(hs.financial_support)}</strong></div>
            <div class="card-meta-item"><span>Top Institutes:</span> <strong>${(hs.top_institutes || []).slice(0, 4).join(', ')}</strong></div>
          </div>
          <div style="font-size: 0.82rem; margin-bottom: 0.65rem;">
            <strong>Specializations:</strong> ${(hs.specializations || []).slice(0, 4).join(' • ')}
          </div>
          <p style="font-size: 0.82rem; color: var(--text-secondary);"><strong>Career Outcomes:</strong> ${escapeHtml(hs.career_outcomes)}</p>
        </div>
        <div class="card-footer">
          <a href="${escapeHtml(hs.official_portal)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">
            <i data-lucide="external-link" class="icon-xs"></i> Official Admission Portal
          </a>
          <button class="btn btn-secondary btn-sm" onclick="sendQuickPrompt('Explain ' + '${escapeHtml(hs.degree)}' + ' preparation and admission strategy for B.Tech students.')">
            <i data-lucide="sparkles" class="icon-xs"></i> Plan with AI
          </button>
        </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
  refreshIcons();
}

// 3. GATE DEEP DIVE SECTION
async function renderBTechGATEGuideSection() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  let gate = {};
  try {
    const res = await fetch('/api/btech/gate');
    const data = await res.json();
    gate = data.gate_guide || {};
  } catch (e) {
    gate = {};
  }

  const branch = AppState.btechState.branch || 'CSE';
  const paperRecommended = (gate.papers_map && gate.papers_map[branch]) || "Core Discipline Paper";

  let html = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <span class="badge badge-primary">COMPETITIVE GATEWAY</span>
      <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">
        ${escapeHtml(gate.title || 'Graduate Aptitude Test in Engineering (GATE)')}
      </h3>
      <p style="color: var(--text-secondary); font-size: 0.85rem;">
        ${escapeHtml(gate.conducting_authority || 'Administered jointly by IISc and IITs')}
      </p>
    </div>

    <!-- GATE Overview Grid -->
    <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem; margin-bottom: 1.5rem;">
      <div style="background: var(--bg-hover); padding: 1rem; border-radius: var(--radius-md);">
        <strong style="font-size: 0.85rem; color: var(--primary);">Who Can Apply:</strong>
        <p style="font-size: 0.82rem; margin-top: 0.25rem;">${escapeHtml(gate.who_can_apply || '3rd year or completed B.Tech (No age limit)')}</p>
        <strong style="font-size: 0.85rem; color: var(--primary); margin-top: 0.5rem; display: block;">Paper for Your Branch (${branch}):</strong>
        <p style="font-size: 0.82rem; margin-top: 0.25rem; font-weight: 700; color: var(--status-open);">${escapeHtml(paperRecommended)}</p>
      </div>

      <div style="background: var(--bg-hover); padding: 1rem; border-radius: var(--radius-md);">
        <strong style="font-size: 0.85rem; color: var(--primary);">M.Tech Admission Route:</strong>
        <p style="font-size: 0.82rem; margin-top: 0.25rem;">${escapeHtml(gate.dual_opportunities?.mtech_admissions || 'Direct M.Tech at IISc/IITs with Rs 12,400/mo stipend')}</p>
      </div>

      <div style="background: var(--bg-hover); padding: 1rem; border-radius: var(--radius-md);">
        <strong style="font-size: 0.85rem; color: var(--primary);">PSU Executive Recruitment:</strong>
        <p style="font-size: 0.82rem; margin-top: 0.25rem;">${escapeHtml(gate.dual_opportunities?.psu_recruitments || 'Direct executive posts in Maharatnas (CTC Rs 15-22 LPA)')}</p>
      </div>
    </div>

    <!-- PSUs Hiring Through GATE -->
    <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-md); padding: 1rem; margin-bottom: 1.5rem;">
      <strong style="font-size: 0.9rem; color: var(--text-main); display: block; margin-bottom: 0.5rem;">
        Maharatna & Navratna PSUs Recruiting via GATE:
      </strong>
      <div style="display: flex; flex-wrap: wrap; gap: 0.4rem;">
        ${(gate.psus_hiring_through_gate || []).map(psu => `<span class="badge badge-warning" style="font-size: 0.78rem;">${escapeHtml(psu)}</span>`).join('')}
      </div>
    </div>

    <!-- 4-Phase Preparation Roadmap -->
    <h4 style="font-size: 1.1rem; font-weight: 800; color: var(--text-main); margin-bottom: 0.75rem;">
      Structured 8-Month GATE Preparation Strategy:
    </h4>
    <div class="roadmap-flow mb-4">
      ${(gate.preparation_roadmap_months || []).map((step, idx) => `
        <div class="roadmap-step">
          <div class="step-label">Phase ${idx + 1}: ${escapeHtml(step.phase)}</div>
          <div class="step-content">${escapeHtml(step.focus)}</div>
        </div>
      `).join('')}
    </div>

    <div style="display: flex; gap: 0.75rem; flex-wrap: wrap;">
      <a href="${escapeHtml(gate.official_portal || 'https://gate2025.iitr.ac.in')}" target="_blank" rel="noopener noreferrer" class="btn btn-primary">
        <i data-lucide="external-link" class="icon-xs"></i> Official GATE Organizing Portal
      </a>
      <button class="btn btn-secondary" onclick="sendQuickPrompt('Create a daily study timetable and subject weightage for GATE ' + '${escapeHtml(branch)}' + '.')">
        <i data-lucide="sparkles" class="icon-xs"></i> Build GATE Daily Timetable with AI
      </button>
    </div>
  `;

  container.innerHTML = html;
  refreshIcons();
}

// 4. GOVT & PSU SECTION
function renderBTechGovtPSUSection() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  const branch = AppState.btechState.branch || 'CSE';
  const govtJobs = AppState.datasets.govtJobs || [];

  let html = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <span class="badge badge-warning">PUBLIC SECTOR & CENTRAL GOVERNMENT</span>
      <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">
        Government Engineering & PSU Careers for B.Tech ${escapeHtml(branch)}
      </h3>
      <p style="color: var(--text-secondary); font-size: 0.85rem;">
        Opportunities spanning Maharatna PSUs, ISRO, DRDO, BARC, Indian Railways, and Central Ministries.
      </p>
    </div>

    <div class="cards-grid">
  `;

  govtJobs.forEach(job => {
    html += `
      <div class="card">
        <div class="card-header-row">
          <h4 class="card-title">${escapeHtml(job.title)}</h4>
          <span class="badge badge-warning">Govt Service</span>
        </div>
        <div class="card-org">${escapeHtml(job.organization)}</div>
        <div class="card-body">
          <p style="font-size: 0.85rem; margin-bottom: 0.65rem;">${escapeHtml(job.purpose)}</p>
          <div class="card-meta-list">
            <div class="card-meta-item"><span>Qualification:</span> <strong>${escapeHtml(job.qualification)}</strong></div>
            <div class="card-meta-item"><span>Eligible Branches:</span> <strong>${escapeHtml(job.branches_eligible || job.disciplines || 'Core Engineering')}</strong></div>
            <div class="card-meta-item"><span>Salary / Scale:</span> <strong style="color: var(--status-open);">${escapeHtml(job.salary_pay_scale)}</strong></div>
            <div class="card-meta-item"><span>Selection Process:</span> <strong>${escapeHtml(job.selection_process)}</strong></div>
          </div>
        </div>
        <div class="card-footer">
          <a href="${escapeHtml(job.official_website)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">
            <i data-lucide="external-link" class="icon-xs"></i> Official Notification Portal
          </a>
        </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
  refreshIcons();
}

// 5. DEFENCE COMMISSIONS SECTION
async function renderBTechDefenceSection() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  let defEntries = [];
  try {
    const res = await fetch('/api/btech/defence');
    const data = await res.json();
    defEntries = data.defence_pathways || [];
  } catch (e) {
    defEntries = [];
  }

  let html = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <span class="badge badge-success">ARMED FORCES COMMISSIONS</span>
      <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">
        Direct Engineering Commissions in Armed Forces (Army, Navy, Air Force)
      </h3>
      <p style="color: var(--text-secondary); font-size: 0.85rem;">
        Commission as an Officer (Lieutenant / Sub Lieutenant / Flying Officer) based on B.Tech degree merit and SSB assessment.
      </p>
    </div>

    <div class="cards-grid">
  `;

  defEntries.forEach(d => {
    html += `
      <div class="card">
        <div class="card-header-row">
          <h4 class="card-title">${escapeHtml(d.entry_name)}</h4>
          <span class="badge badge-success">${escapeHtml(d.commission_type)}</span>
        </div>
        <div class="card-body">
          <div class="card-meta-list" style="margin-bottom: 0.65rem;">
            <div class="card-meta-item"><span>Eligibility:</span> <strong>${escapeHtml(d.eligibility)}</strong></div>
            <div class="card-meta-item"><span>Selection Stages:</span> <strong>${escapeHtml(d.selection_process)}</strong></div>
            <div class="card-meta-item"><span>Training Academy:</span> <strong>${escapeHtml(d.training_academy)}</strong></div>
            <div class="card-meta-item"><span>Rank & Pay:</span> <strong style="color: var(--status-open);">${escapeHtml(d.rank_and_pay)}</strong></div>
          </div>
        </div>
        <div class="card-footer">
          <a href="${escapeHtml(d.official_website)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">
            <i data-lucide="external-link" class="icon-xs"></i> Official Recruitment Portal
          </a>
          <button class="btn btn-secondary btn-sm" onclick="sendQuickPrompt('Explain ' + '${escapeHtml(d.entry_name)}' + ' 5-Day SSB procedure and preparation guide.')">
            <i data-lucide="shield" class="icon-xs"></i> SSB Guide
          </button>
        </div>
      </div>
    `;
  });

  html += `</div>`;
  container.innerHTML = html;
  refreshIcons();
}

// 6. ENTREPRENEURSHIP SECTION
function renderBTechEntrepreneurshipSection() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  container.innerHTML = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <span class="badge badge-primary">INNOVATION & STARTUPS</span>
      <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">
        Technology Entrepreneurship & Incubator Support
      </h3>
      <p style="color: var(--text-secondary); font-size: 0.85rem;">
        National startup schemes, DST prototyping grants, and university incubation centers.
      </p>
    </div>

    <div class="cards-grid">
      <div class="card">
        <div class="card-header-row"><h4 class="card-title">Startup India Seed Fund Scheme</h4><span class="badge badge-success">Govt Grant</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">Financial assistance to startups for proof of concept, prototype development, product trials, and market-entry.</p>
          <div class="card-meta-list" style="margin-top: 0.5rem;">
            <div class="card-meta-item"><span>Funding:</span> <strong>Up to Rs 20 Lakhs as grant, and up to Rs 50 Lakhs via debt</strong></div>
            <div class="card-meta-item"><span>Eligibility:</span> <strong>DPIIT-recognized startups incorporated within 2 years</strong></div>
          </div>
        </div>
        <div class="card-footer">
          <a href="https://seedfund.startupindia.gov.in" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm"><i data-lucide="external-link" class="icon-xs"></i> Seed Fund Portal</a>
        </div>
      </div>

      <div class="card">
        <div class="card-header-row"><h4 class="card-title">NIDHI-PRAYAS Prototyping Grant</h4><span class="badge badge-primary">DST Govt of India</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">Supports young engineering innovators to turn technical ideas into physical hardware/software prototypes.</p>
          <div class="card-meta-list" style="margin-top: 0.5rem;">
            <div class="card-meta-item"><span>Grant Amount:</span> <strong>Up to Rs 10 Lakhs non-dilutive prototype grant</strong></div>
            <div class="card-meta-item"><span>Incubator Centers:</span> <strong>T-Hub, IIT Madras Incubation, SINE IIT Bombay</strong></div>
          </div>
        </div>
        <div class="card-footer">
          <a href="https://www.nidhi-prayas.org" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm"><i data-lucide="external-link" class="icon-xs"></i> NIDHI Portal</a>
        </div>
      </div>
    </div>
  `;
  refreshIcons();
}

// 7. STUDY ABROAD SECTION
function renderBTechStudyAbroadSection() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  container.innerHTML = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <span class="badge badge-primary">GLOBAL GRADUATE MOBILITY</span>
      <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">
        Master's Degree Abroad (USA, Germany, UK, Europe)
      </h3>
      <p style="color: var(--text-secondary); font-size: 0.85rem;">
        Comparison of international destinations, standardized testing requirements, and post-study work visas.
      </p>
    </div>

    <div class="cards-grid">
      <div class="card">
        <div class="card-header-row"><h4 class="card-title">United States (USA)</h4><span class="badge badge-info">3-Year STEM OPT</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">Premier research universities (Carnegie Mellon, Purdue, Michigan). Graduates in STEM degrees receive 36 months of official work authorization (F-1 STEM OPT).</p>
          <div class="card-meta-list" style="margin-top: 0.5rem;">
            <div class="card-meta-item"><span>Exams:</span> <strong>GRE (Select universities) + TOEFL/IELTS</strong></div>
            <div class="card-meta-item"><span>Average Starting Pay:</span> <strong>$90,000 - $130,000+ USD / annum</strong></div>
          </div>
        </div>
        <div class="card-footer">
          <a href="https://www.ets.org/gre" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm"><i data-lucide="external-link" class="icon-xs"></i> Official GRE Portal</a>
        </div>
      </div>

      <div class="card">
        <div class="card-header-row"><h4 class="card-title">Germany (TU9 Universities)</h4><span class="badge badge-success">Tuition-Free Education</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">World-class engineering education with virtually zero tuition fees at public universities (TU Munich, RWTH Aachen, TU Berlin). 18-month post-study job seeker visa.</p>
          <div class="card-meta-list" style="margin-top: 0.5rem;">
            <div class="card-meta-item"><span>Exams:</span> <strong>IELTS / TOEFL (GRE required by select TU9s)</strong></div>
            <div class="card-meta-item"><span>Average Starting Pay:</span> <strong>€50,000 - €75,000 EUR / annum</strong></div>
          </div>
        </div>
        <div class="card-footer">
          <a href="https://www.daad.de/en" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm"><i data-lucide="external-link" class="icon-xs"></i> DAAD Germany Portal</a>
        </div>
      </div>
    </div>
  `;
  refreshIcons();
}

// 8. UPSKILLING SECTION
function renderBTechUpskillingSection() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  container.innerHTML = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <span class="badge badge-primary">INDUSTRY ACCREDITATION</span>
      <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">
        Professional Certifications & Skill Accelerators
      </h3>
      <p style="color: var(--text-secondary); font-size: 0.85rem;">
        Targeted industry credentials that significantly increase resume visibility and interview shortlists.
      </p>
    </div>

    <div class="cards-grid">
      <div class="card">
        <div class="card-header-row"><h4 class="card-title">AWS Certified Solutions Architect</h4><span class="badge badge-info">Cloud Computing</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">Validates knowledge of designing distributed systems on AWS, high availability, security architectures, and cost optimization.</p>
        </div>
        <div class="card-footer"><a href="https://aws.amazon.com/certification" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm"><i data-lucide="external-link" class="icon-xs"></i> AWS Certification Portal</a></div>
      </div>

      <div class="card">
        <div class="card-header-row"><h4 class="card-title">Certified Kubernetes Administrator (CKA)</h4><span class="badge badge-primary">DevOps & Containers</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">100% performance-based exam demonstrating container orchestration, networking, cluster architecture, and troubleshooting.</p>
        </div>
        <div class="card-footer"><a href="https://www.cncf.io/certification/cka" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm"><i data-lucide="external-link" class="icon-xs"></i> CNCF Portal</a></div>
      </div>

      <div class="card">
        <div class="card-header-row"><h4 class="card-title">IIT NPTEL Swayam Certifications</h4><span class="badge badge-success">Govt of India Accredited</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">Free online video courses by IIT professors with proctored physical examinations recognized by AICTE and top Indian employers.</p>
        </div>
        <div class="card-footer"><a href="https://nptel.ac.in" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm"><i data-lucide="external-link" class="icon-xs"></i> NPTEL Portal</a></div>
      </div>
    </div>
  `;
  refreshIcons();
}

// 9. CAREER TRANSITION SECTION
function renderBTechCareerChangeSection() {
  const container = document.getElementById('btech-pathway-detail-container');
  if (!container) return;

  container.innerHTML = `
    <div style="border-bottom: 1px solid var(--border-color); padding-bottom: 1rem; margin-bottom: 1.5rem;">
      <span class="badge badge-primary">INTERDISCIPLINARY CAREER TRANSITION</span>
      <h3 style="font-size: 1.35rem; font-weight: 800; color: var(--text-main); margin-top: 0.25rem;">
        Transitioning from Engineering to Leadership, Design & Policy
      </h3>
      <p style="color: var(--text-secondary); font-size: 0.85rem;">
        Structured routes to pivot analytical engineering skills into Product, Management, Design, or Civil Services.
      </p>
    </div>

    <div class="cards-grid">
      <div class="card">
        <div class="card-header-row"><h4 class="card-title">B.Tech → Product Management (APM)</h4><span class="badge badge-primary">Tech Leadership</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">Direct transition into Associate Product Manager roles at companies like Swiggy, Razorpay, and Microsoft. Focus on product sense, wireframing, and user metrics.</p>
        </div>
        <div class="card-footer"><button class="btn btn-secondary btn-sm" onclick="sendQuickPrompt('How can a B.Tech graduate transition into an Associate Product Manager role?')"><i data-lucide="sparkles" class="icon-xs"></i> Plan APM Transition with AI</button></div>
      </div>

      <div class="card">
        <div class="card-header-row"><h4 class="card-title">B.Tech → Management Consulting via MBA</h4><span class="badge badge-warning">IIMs / CAT</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">Engineers with strong CAT scores transition into top management consulting firms (McKinsey, BCG, Bain) and investment banks via 2-year MBA.</p>
        </div>
        <div class="card-footer"><a href="https://iimcat.ac.in" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm"><i data-lucide="external-link" class="icon-xs"></i> IIM CAT Portal</a></div>
      </div>

      <div class="card">
        <div class="card-header-row"><h4 class="card-title">B.Tech → Civil Services (UPSC CSE)</h4><span class="badge badge-danger">IAS / IPS / IFS</span></div>
        <div class="card-body">
          <p style="font-size: 0.85rem;">Leverage disciplined analytical study habits for UPSC Civil Services Examination. Option to choose engineering subjects or humanities optionals (Geography, PSIR, Public Admin).</p>
        </div>
        <div class="card-footer"><a href="https://upsc.gov.in" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm"><i data-lucide="external-link" class="icon-xs"></i> UPSC Portal</a></div>
      </div>
    </div>
  `;
  refreshIcons();
}

// JOB ROLE BLUEPRINT MODAL
async function openJobRoleModal(roleId) {
  const modal = document.getElementById('job-role-modal');
  if (!modal) return;

  AppState.btechState.selectedRoleId = roleId;

  // Find role from datasets
  let foundRole = null;
  const categories = (await fetch('/api/btech/jobs').then(r => r.json())).categories || [];
  for (const c of categories) {
    for (const r of c.roles || []) {
      if (r.id === roleId) {
        foundRole = r;
        break;
      }
    }
    if (foundRole) break;
  }

  if (!foundRole) return;

  document.getElementById('role-modal-title').textContent = foundRole.name;
  document.getElementById('role-modal-desc').textContent = foundRole.what_they_do;
  document.getElementById('role-modal-badge').textContent = foundRole.category.toUpperCase().replace('_', ' ');

  const respUl = document.getElementById('role-modal-responsibilities');
  if (respUl) {
    respUl.innerHTML = (foundRole.responsibilities || []).map(res => `<li>${escapeHtml(res)}</li>`).join('');
  }

  const skillsDiv = document.getElementById('role-modal-skills');
  if (skillsDiv) {
    skillsDiv.innerHTML = (foundRole.skills || []).map(s => `<span class="badge badge-primary">${escapeHtml(s)}</span>`).join('');
  }

  const toolsDiv = document.getElementById('role-modal-tools');
  if (toolsDiv) {
    toolsDiv.innerHTML = (foundRole.tools || []).map(t => `<span class="badge badge-info">${escapeHtml(t)}</span>`).join('');
  }

  const roadP = document.getElementById('role-modal-roadmap');
  if (roadP) {
    roadP.textContent = foundRole.beginner_roadmap || 'Learn core concepts -> Build 3 projects -> Polish resume.';
  }

  const projUl = document.getElementById('role-modal-projects');
  if (projUl) {
    projUl.innerHTML = (foundRole.projects_to_build || []).map(p => `<li>${escapeHtml(p)}</li>`).join('');
  }

  const certsDiv = document.getElementById('role-modal-certs');
  if (certsDiv) {
    certsDiv.innerHTML = (foundRole.certifications || []).map(c => `• ${escapeHtml(c)}`).join('<br>');
  }

  const compsDiv = document.getElementById('role-modal-companies');
  if (compsDiv) {
    compsDiv.innerHTML = (foundRole.companies || []).map(c => `<span class="badge badge-warning">${escapeHtml(c)}</span>`).join('');
  }

  modal.classList.remove('hidden');
  refreshIcons();
}

function closeJobRoleModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('close-btn')) return;
  const modal = document.getElementById('job-role-modal');
  if (modal) modal.classList.add('hidden');
}

function askAIAboutJobRole() {
  const title = document.getElementById('role-modal-title')?.textContent || 'this role';
  closeJobRoleModal();
  navigateToSection('ai-guide');
  sendQuickPrompt(`I am a B.Tech graduate interested in becoming a ${title}. What exact skills should I learn first, what projects should I build, and how can I prepare for interviews?`);
}

// PATHWAY COMPARISON MODAL
async function openPathwayCompareModal(scenarioId = 'comp-job-vs-mtech') {
  const modal = document.getElementById('pathway-compare-modal');
  if (!modal) return;

  const select = document.getElementById('compare-select');
  if (select) select.value = scenarioId;

  await loadAndRenderComparison(scenarioId);
  modal.classList.remove('hidden');
  refreshIcons();
}

function closePathwayCompareModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('close-btn')) return;
  const modal = document.getElementById('pathway-compare-modal');
  if (modal) modal.classList.add('hidden');
}

function handleComparisonChange() {
  const select = document.getElementById('compare-select');
  if (select) {
    loadAndRenderComparison(select.value);
  }
}

async function loadAndRenderComparison(scenarioId) {
  const container = document.getElementById('compare-matrix-container');
  if (!container) return;

  try {
    const res = await fetch(`/api/btech/compare?id=${encodeURIComponent(scenarioId)}`);
    const data = await res.json();
    const c = data.comparison;
    if (!c) {
      container.innerHTML = '<p>Comparison data not found.</p>';
      return;
    }

    container.innerHTML = `
      <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
        <div style="background: var(--bg-hover); padding: 1.15rem; border-radius: var(--radius-md); border-top: 3px solid var(--primary);">
          <h4 style="font-size: 1.05rem; font-weight: 800; color: var(--primary); margin-bottom: 0.75rem;">${escapeHtml(c.left.title)}</h4>
          <div style="display: flex; flex-direction: column; gap: 0.65rem; font-size: 0.82rem;">
            ${c.left.time_horizon ? `<div><strong>Time Horizon:</strong><br>${escapeHtml(c.left.time_horizon)}</div>` : ''}
            ${c.left.financial_aspect ? `<div><strong>Financial Aspect:</strong><br>${escapeHtml(c.left.financial_aspect)}</div>` : ''}
            ${c.left.skill_acquisition ? `<div><strong>Skill Acquisition:</strong><br>${escapeHtml(c.left.skill_acquisition)}</div>` : ''}
            ${c.left.career_trajectory ? `<div><strong>Career Trajectory:</strong><br>${escapeHtml(c.left.career_trajectory)}</div>` : ''}
            ${c.left.best_suited_for ? `<div><strong style="color: var(--status-open);">Best Suited For:</strong><br>${escapeHtml(c.left.best_suited_for)}</div>` : ''}
          </div>
        </div>

        <div style="background: var(--bg-hover); padding: 1.15rem; border-radius: var(--radius-md); border-top: 3px solid #10b981;">
          <h4 style="font-size: 1.05rem; font-weight: 800; color: #10b981; margin-bottom: 0.75rem;">${escapeHtml(c.right.title)}</h4>
          <div style="display: flex; flex-direction: column; gap: 0.65rem; font-size: 0.82rem;">
            ${c.right.time_horizon ? `<div><strong>Time Horizon:</strong><br>${escapeHtml(c.right.time_horizon)}</div>` : ''}
            ${c.right.financial_aspect ? `<div><strong>Financial Aspect:</strong><br>${escapeHtml(c.right.financial_aspect)}</div>` : ''}
            ${c.right.skill_acquisition ? `<div><strong>Skill Acquisition:</strong><br>${escapeHtml(c.right.skill_acquisition)}</div>` : ''}
            ${c.right.career_trajectory ? `<div><strong>Career Trajectory:</strong><br>${escapeHtml(c.right.career_trajectory)}</div>` : ''}
            ${c.right.best_suited_for ? `<div><strong style="color: var(--status-open);">Best Suited For:</strong><br>${escapeHtml(c.right.best_suited_for)}</div>` : ''}
          </div>
        </div>
      </div>
    `;
  } catch (err) {
    container.innerHTML = '<p>Unable to load comparison.</p>';
  }
}

// ==========================================
// 14. AUTHENTICATION & USER SESSIONS
// ==========================================
let currentUser = null;

function toggleAuthLangMenu(event) {
  if (event) event.stopPropagation();
  const menu = document.getElementById('auth-lang-menu');
  if (menu) menu.classList.toggle('hidden');
}

function showAuthView(viewName) {
  const views = {
    'login': document.getElementById('auth-view-login'),
    'signup': document.getElementById('auth-view-signup'),
    'forgot': document.getElementById('auth-view-forgot'),
    'reset': document.getElementById('auth-view-reset'),
    'profile_setup': document.getElementById('auth-view-profile-setup')
  };

  Object.values(views).forEach(v => {
    if (v) v.classList.add('hidden');
  });

  const alerts = [
    document.getElementById('auth-login-error'),
    document.getElementById('auth-signup-error'),
    document.getElementById('auth-forgot-status'),
    document.getElementById('auth-reset-status'),
    document.getElementById('setup-error-msg')
  ];
  alerts.forEach(a => {
    if (a) {
      a.classList.add('hidden');
      a.textContent = '';
    }
  });

  const targetView = views[viewName] || views['login'];
  if (targetView) {
    targetView.classList.remove('hidden');
  }

  if (viewName === 'profile_setup') {
    handleSetupStageChange();
  }

  if (viewName === 'reset') {
    document.getElementById('auth-screen')?.classList.remove('hidden');
    document.getElementById('app-shell')?.classList.add('hidden');
  }

  refreshIcons();
}

function togglePasswordVisibility(inputId, btn) {
  const input = document.getElementById(inputId);
  if (!input) return;
  const isPass = input.type === 'password';
  input.type = isPass ? 'text' : 'password';
  const icon = btn.querySelector('i');
  if (icon) {
    icon.setAttribute('data-lucide', isPass ? 'eye-off' : 'eye');
  }
  refreshIcons();
}

async function checkAuthStatus() {
  const authScreen = document.getElementById('auth-screen');
  const appShell = document.getElementById('app-shell');

  try {
    const res = await fetch('/api/auth/me');
    const data = await res.json();
    if (data.authenticated && data.user) {
      currentUser = data.user;
      
      const isProfileComplete = data.profile && (data.profile.is_onboarded === 1 || data.profile.is_onboarded === '1' || data.profile.is_onboarded === true);

      if (isProfileComplete) {
        // Authenticated and profile is completed: show personalized dashboard directly
        if (authScreen) authScreen.classList.add('hidden');
        if (appShell) appShell.classList.remove('hidden');
        renderUserAuthUI(data.user);
        setStoredRadarProfile(data.profile);
        updateRadarProfileChip(data.profile);
        loadRadarAlerts();
        loadTrackerProgress();
      } else {
        // Authenticated but profile setup is pending: show Profile Setup screen
        if (appShell) appShell.classList.add('hidden');
        if (authScreen) authScreen.classList.remove('hidden');
        showAuthView('profile_setup');
      }

      if (typeof data.user?.unread_notifications === 'number') {
        const badge = document.getElementById('radar-unread-badge');
        const drawerCount = document.getElementById('drawer-unread-count');
        if (badge) {
          if (data.user.unread_notifications > 0) {
            badge.textContent = data.user.unread_notifications > 9 ? '9+' : data.user.unread_notifications;
            badge.classList.remove('hidden');
          } else {
            badge.classList.add('hidden');
          }
        }
        if (drawerCount) {
          drawerCount.textContent = `${data.user.unread_notifications} New`;
        }
      }
    } else {
      // Unauthenticated: Show Sign-In screen first, keep dashboard hidden
      currentUser = null;
      if (appShell) appShell.classList.add('hidden');
      if (authScreen) authScreen.classList.remove('hidden');
      showAuthView('login');
      renderGuestAuthUI();
    }
  } catch (err) {
    console.warn('Auth check fallback to guest:', err);
    currentUser = null;
    if (appShell) appShell.classList.add('hidden');
    if (authScreen) authScreen.classList.remove('hidden');
    showAuthView('login');
    renderGuestAuthUI();
  }
}

function handleSetupStageChange() {
  const stage = document.getElementById('setup-stage')?.value || 'B.Tech';
  const branchSelect = document.getElementById('setup-branch');
  const branchLabel = document.getElementById('setup-branch-label');
  const notice10th = document.getElementById('setup-10th-notice');
  const optData = window.APP_OPTIONS || APP_OPTIONS;

  if (stage === '10th') {
    // 10th Standard: DO NOT SHOW ANY ENGINEERING BRANCHES!
    if (branchSelect) {
      branchSelect.innerHTML = '<option value="General" selected>General / All Subjects (Secondary School Foundation)</option>';
      branchSelect.classList.add('hidden');
    }
    if (branchLabel) branchLabel.classList.add('hidden');
    if (notice10th) notice10th.classList.remove('hidden');
  } else {
    if (notice10th) notice10th.classList.add('hidden');
    if (branchLabel) branchLabel.classList.remove('hidden');
    if (branchSelect) {
      branchSelect.classList.remove('hidden');
      const branches = (optData.branches_by_qual && optData.branches_by_qual[stage]) ||
                       (optData.streams_by_qual && optData.streams_by_qual[stage]) ||
                       optData.btech_branches || ['CSE'];
      branchSelect.innerHTML = branches.map(b => `<option value="${escapeHtml(b)}">${escapeHtml(b)}</option>`).join('');
    }
  }

  // Populate dynamic interests tailored to qualification
  const interestsContainer = document.getElementById('setup-interests-container');
  if (interestsContainer) {
    let directions = [];
    if (stage === '10th') {
      directions = [
        'Intermediate (MPC / BiPC / CEC / MEC)', 'Polytechnic Diploma', 'ITI Technical Trades',
        'Government / Defence Entries (Agniveer, SSC GD)', 'Foundational Science & Mathematics', 'Computer Basics & Digital Skills'
      ];
    } else if (stage === 'Intermediate') {
      directions = [
        'Engineering (B.Tech / B.E.)', 'Medical & Healthcare (MBBS, BDS, Pharma)', 'General Degrees (B.Sc, B.Com, BBA, BA)',
        'Defence Cadet Entries (NDA, TES)', 'Law & Legal Studies (CLAT)', 'Chartered Accountancy (CA / CMA)'
      ];
    } else if (stage === 'Diploma') {
      directions = [
        'Lateral Entry to B.Tech (ECET)', 'Junior Engineer (JE) Government Exams', 'Core Technical Industry Jobs',
        'NATS Apprenticeship', 'Defence Technical Roles', 'Entrepreneurship & Startups'
      ];
    } else if (stage === 'Degree') {
      directions = [
        'Post Graduation (M.Sc, M.Com, MA, MCA)', 'MBA / Business Management', 'Civil Services (UPSC CSE, State PSC)',
        'Banking & Insurance (IBPS, SBI PO)', 'Corporate Private Sector Jobs', '3-Year LLB / Law', 'Defence (CDS, AFCAT)'
      ];
    } else if (stage === 'Postgraduate') {
      directions = [
        'Ph.D. / Doctoral Research', 'University Assistant Professor (UGC NET)', 'Senior Corporate R&D Roles',
        'Government Scientist (DRDO, ISRO, BARC)', 'Executive Leadership'
      ];
    } else {
      directions = (optData.preferred_career_directions_by_qual && optData.preferred_career_directions_by_qual[stage]) || [
        'Software / IT Industry', 'Cyber Security & Cloud', 'Core Engineering Jobs', 'PSUs & Govt Engineering (GATE, IES/ESE)',
        'Higher Studies (M.Tech via GATE)', 'Higher Studies Abroad (MS via GRE)', 'Management (MBA via CAT)', 'Defence Technical Entry (TGC, SSC Tech)'
      ];
    }

    interestsContainer.innerHTML = directions.map(dir => `
      <label class="checkbox-pill-label" style="display:flex; align-items:center; gap:0.4rem; padding:0.35rem 0.6rem; background:var(--bg-surface); border:1px solid var(--border-color); border-radius:4px; font-size:0.8rem; cursor:pointer;">
        <input type="checkbox" name="setup-interest" value="${escapeHtml(dir)}" checked>
        <span>${escapeHtml(dir)}</span>
      </label>
    `).join('');
  }

  refreshIcons();
}

async function handleAuthLoginSubmit(e) {
  e.preventDefault();
  const emailInput = document.getElementById('auth-login-email');
  const passwordInput = document.getElementById('auth-login-password');
  const errBox = document.getElementById('auth-login-error');
  const submitBtn = document.getElementById('auth-login-btn-submit');
  const btnText = submitBtn?.querySelector('.btn-text');
  const btnSpinner = submitBtn?.querySelector('.btn-spinner');

  const email = emailInput?.value?.trim() || '';
  const password = passwordInput?.value || '';

  if (errBox) errBox.classList.add('hidden');

  if (!email || !email.includes('@') || !email.includes('.')) {
    if (errBox) {
      errBox.textContent = t('auth.validation_email', 'Please enter a valid email address.');
      errBox.classList.remove('hidden');
    }
    emailInput?.focus();
    return;
  }

  if (!password) {
    if (errBox) {
      errBox.textContent = t('auth.validation_password', 'Please enter your password.');
      errBox.classList.remove('hidden');
    }
    passwordInput?.focus();
    return;
  }

  if (submitBtn) submitBtn.disabled = true;
  if (btnText) btnText.textContent = t('auth.signing_in', 'Signing in...');
  if (btnSpinner) btnSpinner.classList.remove('hidden');

  try {
    const res = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password })
    });
    const data = await res.json();
    if (res.ok && (data.status === 'success' || data.success === true)) {
      currentUser = data.user;
      const isProfileComplete = data.profile && (data.profile.is_onboarded === 1 || data.profile.is_onboarded === '1' || data.profile.is_onboarded === true);

      if (isProfileComplete) {
        document.getElementById('auth-screen')?.classList.add('hidden');
        document.getElementById('app-shell')?.classList.remove('hidden');
        renderUserAuthUI(data.user);
        setStoredRadarProfile(data.profile);
        updateRadarProfileChip(data.profile);
        loadRadarAlerts();
        loadTrackerProgress();
        navigateToSection('home');
        window.scrollTo({ top: 0, behavior: 'smooth' });
      } else {
        showAuthView('profile_setup');
      }
    } else {
      if (errBox) {
        errBox.textContent = data.message || t('auth.invalid_credentials', 'Invalid email or password. Please try again.');
        errBox.classList.remove('hidden');
      }
    }
  } catch (err) {
    if (errBox) {
      errBox.textContent = t('auth.server_error', 'Unable to sign in right now. Please try again.');
      errBox.classList.remove('hidden');
    }
  } finally {
    if (submitBtn) submitBtn.disabled = false;
    if (btnText) btnText.textContent = t('auth.sign_in_btn', 'SIGN IN');
    if (btnSpinner) btnSpinner.classList.add('hidden');
  }
}

async function handleAuthSignupSubmit(e) {
  e.preventDefault();
  const nameInput = document.getElementById('auth-signup-name');
  const emailInput = document.getElementById('auth-signup-email');
  const passwordInput = document.getElementById('auth-signup-password');
  const confirmInput = document.getElementById('auth-signup-confirm');
  const errBox = document.getElementById('auth-signup-error');
  const submitBtn = document.getElementById('auth-signup-btn-submit');
  const btnText = submitBtn?.querySelector('.btn-text');
  const btnSpinner = submitBtn?.querySelector('.btn-spinner');

  const fullName = nameInput?.value?.trim() || '';
  const email = emailInput?.value?.trim() || '';
  const password = passwordInput?.value || '';
  const confirmPassword = confirmInput?.value || '';

  if (errBox) errBox.classList.add('hidden');

  if (!fullName) {
    if (errBox) {
      errBox.textContent = t('auth.validation_name', 'Please enter your full name.');
      errBox.classList.remove('hidden');
    }
    nameInput?.focus();
    return;
  }

  if (!email || !email.includes('@') || !email.includes('.')) {
    if (errBox) {
      errBox.textContent = t('auth.validation_email', 'Please enter a valid email address.');
      errBox.classList.remove('hidden');
    }
    emailInput?.focus();
    return;
  }

  if (password.length < 8) {
    if (errBox) {
      errBox.textContent = t('auth.validation_password_length', 'Password must be at least 8 characters long.');
      errBox.classList.remove('hidden');
    }
    passwordInput?.focus();
    return;
  }

  if (password !== confirmPassword) {
    if (errBox) {
      errBox.textContent = t('auth.validation_password_match', 'Passwords do not match.');
      errBox.classList.remove('hidden');
    }
    confirmInput?.focus();
    return;
  }

  if (submitBtn) submitBtn.disabled = true;
  if (btnText) btnText.textContent = t('auth.creating_account', 'Creating Account...');
  if (btnSpinner) btnSpinner.classList.remove('hidden');

  try {
    const res = await fetch('/api/auth/signup', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        full_name: fullName,
        email: email,
        password: password
      })
    });
    const data = await res.json();
    if (res.ok && (data.status === 'success' || data.success === true)) {
      currentUser = data.user;
      // Post-registration: Show Profile Setup wizard
      showAuthView('profile_setup');
    } else {
      if (errBox) {
        let msg = data.message || 'Unable to create account. Please try a different email.';
        if (res.status === 409) {
          msg = (data.message || 'An account with this email already exists. Please sign in.') +
                ' <a href="#" onclick="showAuthView(\'login\'); return false;" style="text-decoration: underline; font-weight: bold; margin-left: 6px;">Sign In Here &rarr;</a>';
          errBox.innerHTML = msg;
        } else {
          errBox.textContent = msg;
        }
        errBox.classList.remove('hidden');
      }
    }
  } catch (err) {
    if (errBox) {
      errBox.textContent = t('auth.server_error', 'Connection failed. Please try again.');
      errBox.classList.remove('hidden');
    }
  } finally {
    if (submitBtn) submitBtn.disabled = false;
    if (btnText) btnText.textContent = t('auth.create_account_btn', 'CREATE ACCOUNT');
    if (btnSpinner) btnSpinner.classList.add('hidden');
  }
}

async function verifyResetToken(token) {
  const statusBox = document.getElementById('auth-reset-status');
  const submitBtn = document.getElementById('auth-reset-btn-submit');
  const pwdInput = document.getElementById('auth-reset-password');
  const confirmInput = document.getElementById('auth-reset-confirm');

  if (!token) {
    if (statusBox) {
      statusBox.innerHTML = 'Reset token is required or reset link is invalid. <button type="button" class="auth-link-btn" onclick="showAuthView(\'forgot\')" style="text-decoration:underline;margin-left:6px;font-weight:600;">Request a new link</button>';
      statusBox.className = 'auth-alert-box alert-danger';
      statusBox.classList.remove('hidden');
    }
    if (submitBtn) submitBtn.disabled = true;
    return;
  }

  try {
    const res = await fetch(`/api/auth/verify-reset-token?token=${encodeURIComponent(token)}`);
    const data = await res.json();
    if (res.ok && data.status === 'success') {
      if (statusBox) {
        statusBox.innerHTML = `<span>Resetting password for <strong>${data.email || 'your account'}</strong>. Enter your new password below.</span>`;
        statusBox.className = 'auth-alert-box alert-info';
        statusBox.classList.remove('hidden');
      }
      if (submitBtn) submitBtn.disabled = false;
      if (pwdInput) pwdInput.disabled = false;
      if (confirmInput) confirmInput.disabled = false;
    } else {
      if (statusBox) {
        statusBox.innerHTML = `<span>${data.message || 'This password reset link is invalid or has expired.'}</span> <button type="button" class="auth-link-btn" onclick="showAuthView(\'forgot\')" style="text-decoration:underline;margin-left:8px;font-weight:600;">Request a new reset link</button>`;
        statusBox.className = 'auth-alert-box alert-danger';
        statusBox.classList.remove('hidden');
      }
      if (submitBtn) submitBtn.disabled = true;
      if (pwdInput) pwdInput.disabled = true;
      if (confirmInput) confirmInput.disabled = true;
    }
  } catch (err) {
    console.error('Token verification error:', err);
  }
}

async function handleAuthForgotSubmit(e) {
  e.preventDefault();
  const emailInput = document.getElementById('auth-forgot-email');
  const statusBox = document.getElementById('auth-forgot-status');
  const submitBtn = document.getElementById('auth-forgot-btn-submit');
  const btnText = submitBtn?.querySelector('.btn-text');
  const btnSpinner = submitBtn?.querySelector('.btn-spinner');

  const email = emailInput?.value?.trim() || '';

  if (statusBox) statusBox.classList.add('hidden');

  if (!email || !email.includes('@') || !email.includes('.')) {
    if (statusBox) {
      statusBox.textContent = t('auth.validation_email', 'Please enter a valid email address.');
      statusBox.className = 'auth-alert-box alert-danger';
      statusBox.classList.remove('hidden');
    }
    emailInput?.focus();
    return;
  }

  if (submitBtn) submitBtn.disabled = true;
  if (btnText) btnText.textContent = t('auth.sending_reset', 'Sending reset link...');
  if (btnSpinner) btnSpinner.classList.remove('hidden');

  try {
    const res = await fetch('/api/auth/forgot-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email })
    });
    const data = await res.json();
    if (res.ok && data.status === 'success') {
      if (statusBox) {
        if (data.reset_url) {
          statusBox.innerHTML = `
            <div style="font-size:13.5px;line-height:1.5;">
              <p style="margin:0 0 8px 0;font-weight:600;">✓ Password Reset Ready</p>
              <p style="margin:0 0 10px 0;">${data.message}</p>
              <div style="margin:10px 0 8px 0;">
                <a href="${data.reset_url}" class="btn btn-primary" style="display:inline-block;padding:8px 16px;border-radius:6px;color:#fff;text-decoration:none;font-weight:600;font-size:13px;text-align:center;">
                  Proceed to Reset Password &rarr;
                </a>
              </div>
              <p style="margin:8px 0 0 0;font-size:12px;opacity:0.85;">
                Direct URL: <code style="word-break:break-all;background:rgba(0,0,0,0.08);padding:2px 4px;border-radius:3px;">${data.reset_url}</code>
              </p>
            </div>
          `;
          statusBox.className = 'auth-alert-box alert-success';
          statusBox.classList.remove('hidden');
        } else {
          statusBox.innerHTML = `
            <div style="font-size:13.5px;line-height:1.5;">
              <p style="margin:0 0 6px 0;font-weight:600;">✓ Reset Email Dispatched</p>
              <p style="margin:0;">${data.message || 'Please check your registered email inbox (and spam folder) for instructions to set your new password.'}</p>
            </div>
          `;
          statusBox.className = 'auth-alert-box alert-success';
          statusBox.classList.remove('hidden');
        }
      }
    } else {
      if (statusBox) {
        statusBox.textContent = data.message || 'Unable to send reset request. Please contact administrator.';
        statusBox.className = 'auth-alert-box alert-danger';
        statusBox.classList.remove('hidden');
      }
    }
  } catch (err) {
    if (statusBox) {
      statusBox.textContent = 'Unable to send reset request right now. Please try again later.';
      statusBox.className = 'auth-alert-box alert-danger';
      statusBox.classList.remove('hidden');
    }
  } finally {
    if (submitBtn) submitBtn.disabled = false;
    if (btnText) btnText.textContent = t('auth.send_reset_link', 'SEND RESET LINK');
    if (btnSpinner) btnSpinner.classList.add('hidden');
  }
}

async function handleAuthResetSubmit(e) {
  e.preventDefault();
  const token = document.getElementById('auth-reset-token')?.value?.trim();
  const password = document.getElementById('auth-reset-password')?.value;
  const confirmPassword = document.getElementById('auth-reset-confirm')?.value;
  const statusBox = document.getElementById('auth-reset-status');
  const submitBtn = document.getElementById('auth-reset-btn-submit');
  const btnText = submitBtn?.querySelector('.btn-text');
  const btnSpinner = submitBtn?.querySelector('.btn-spinner');

  if (statusBox) statusBox.classList.add('hidden');

  if (!token) {
    if (statusBox) {
      statusBox.textContent = 'Reset token is required or reset link is invalid.';
      statusBox.className = 'auth-alert-box alert-danger';
      statusBox.classList.remove('hidden');
    }
    return;
  }

  if (!password || password.length < 8) {
    if (statusBox) {
      statusBox.textContent = 'Password must be at least 8 characters long.';
      statusBox.className = 'auth-alert-box alert-danger';
      statusBox.classList.remove('hidden');
    }
    return;
  }

  if (password !== confirmPassword) {
    if (statusBox) {
      statusBox.textContent = 'Passwords do not match.';
      statusBox.className = 'auth-alert-box alert-danger';
      statusBox.classList.remove('hidden');
    }
    return;
  }

  if (submitBtn) submitBtn.disabled = true;
  if (btnText) btnText.textContent = 'UPDATING...';
  if (btnSpinner) btnSpinner.classList.remove('hidden');

  try {
    const res = await fetch('/api/auth/reset-password', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ token, new_password: password })
    });
    const data = await res.json();
    if (res.ok && data.status === 'success') {
      if (statusBox) {
        statusBox.textContent = data.message || 'Password successfully updated! You can now sign in.';
        statusBox.className = 'auth-alert-box alert-success';
        statusBox.classList.remove('hidden');
      }
      setTimeout(() => {
        showAuthView('login');
      }, 2000);
    } else {
      if (statusBox) {
        statusBox.textContent = data.message || 'Failed to reset password. Token may be invalid or expired.';
        statusBox.className = 'auth-alert-box alert-danger';
        statusBox.classList.remove('hidden');
      }
    }
  } catch (err) {
    if (statusBox) {
      statusBox.textContent = 'Server communication error. Please try again.';
      statusBox.className = 'auth-alert-box alert-danger';
      statusBox.classList.remove('hidden');
    }
  } finally {
    if (submitBtn) submitBtn.disabled = false;
    if (btnText) btnText.textContent = t('tracker.reset_btn', 'UPDATE PASSWORD');
    if (btnSpinner) btnSpinner.classList.add('hidden');
  }
}

async function handleProfileSetupSubmit(e) {
  e.preventDefault();
  const stage = document.getElementById('setup-stage')?.value || 'B.Tech';
  const branchSelect = document.getElementById('setup-branch');
  const branch = (stage === '10th') ? 'General' : (branchSelect?.value || 'CSE');
  const status = document.getElementById('setup-status')?.value || 'Final Year';
  const state = document.getElementById('setup-state')?.value || 'All India / National';
  const dreamGoal = document.getElementById('setup-dream-goal')?.value?.trim() || '';
  const checkedInterests = Array.from(document.querySelectorAll('#setup-interests-container input[name="setup-interest"]:checked')).map(cb => cb.value);
  const errBox = document.getElementById('setup-error-msg');
  const submitBtn = document.getElementById('setup-submit-btn');
  const btnText = submitBtn?.querySelector('.btn-text');
  const btnSpinner = submitBtn?.querySelector('.btn-spinner');

  if (errBox) errBox.classList.add('hidden');
  if (submitBtn) submitBtn.disabled = true;
  if (btnText) btnText.textContent = t('auth.saving_profile', 'Setting up your compass...');
  if (btnSpinner) btnSpinner.classList.remove('hidden');

  try {
    const payload = {
      qualification: stage,
      stream: stage === 'Intermediate' ? branch : '',
      branch: branch,
      current_status: status,
      home_state: state,
      dream_goal: dreamGoal,
      career_interests: checkedInterests,
      is_onboarded: 1
    };

    const res = await fetch('/api/radar/profile', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
    const data = await res.json();
    if (res.ok && data.status === 'success') {
      if (data.profile) {
        setStoredRadarProfile(data.profile);
        updateRadarProfileChip(data.profile);
      }
      if (currentUser) {
        currentUser.profile = data.profile;
        renderUserAuthUI(currentUser);
      }
      loadTrackerProgress();
      // Successfully onboarded: transition into personalized dashboard!
      document.getElementById('auth-screen')?.classList.add('hidden');
      document.getElementById('app-shell')?.classList.remove('hidden');
      loadRadarAlerts();
      navigateToSection('home');
      window.scrollTo({ top: 0, behavior: 'smooth' });
    } else {
      if (errBox) {
        errBox.textContent = data.message || 'Error saving profile setup. Please try again.';
        errBox.classList.remove('hidden');
      }
    }
  } catch (err) {
    if (errBox) {
      errBox.textContent = 'Server communication error. Please try again.';
      errBox.classList.remove('hidden');
    }
  } finally {
    if (submitBtn) submitBtn.disabled = false;
    if (btnText) btnText.textContent = t('auth.continue_to_cc', 'CONTINUE TO CAREER COMPASS');
    if (btnSpinner) btnSpinner.classList.add('hidden');
  }
}

function renderUserAuthUI(user) {
  const userMenu = document.getElementById('user-profile-menu');
  const avatarInitials = document.getElementById('user-avatar-initials');
  const displayName = document.getElementById('user-display-name');
  const dropdownName = document.getElementById('dropdown-user-name');
  const dropdownEmail = document.getElementById('dropdown-user-email');

  if (userMenu) userMenu.classList.remove('hidden');

  const rawName = user.full_name || user.name || 'Student';
  const names = rawName.trim().split(' ');
  const initials = names.length > 1 ? (names[0][0] + names[names.length - 1][0]).toUpperCase() : names[0].substring(0, 2).toUpperCase();

  if (avatarInitials) avatarInitials.textContent = initials;
  if (displayName) displayName.textContent = rawName.split(' ')[0] || 'Account';
  if (dropdownName) dropdownName.textContent = rawName;
  if (dropdownEmail) dropdownEmail.textContent = user.email || '';
}

function renderGuestAuthUI() {
  const userMenu = document.getElementById('user-profile-menu');
  if (userMenu) userMenu.classList.add('hidden');
}

function toggleUserDropdown() {
  const panel = document.getElementById('user-dropdown-panel');
  if (panel) panel.classList.toggle('hidden');
}

async function logoutUser() {
  try {
    await fetch('/api/auth/logout', { method: 'POST' });
  } catch (e) {}
  currentUser = null;
  AppState.radarProfile = null;
  try {
    localStorage.removeItem('cc_radar_profile');
  } catch (e) {}
  const userDropdown = document.getElementById('user-dropdown-panel');
  if (userDropdown) userDropdown.classList.add('hidden');
  renderGuestAuthUI();
  // Transition back to first screen: Sign-In
  const appShell = document.getElementById('app-shell');
  const authScreen = document.getElementById('auth-screen');
  if (appShell) appShell.classList.add('hidden');
  if (authScreen) authScreen.classList.remove('hidden');
  showAuthView('login');
}

// Backward-compatible modal helpers (if referenced anywhere)
function openAuthModal(initialTab = 'login') {
  showAuthView(initialTab === 'signup' ? 'signup' : 'login');
  document.getElementById('app-shell')?.classList.add('hidden');
  document.getElementById('auth-screen')?.classList.remove('hidden');
}

function closeAuthModal() {
  // no-op for full-screen auth
}

function switchAuthTab(tab) {
  showAuthView(tab);
}

function handleSignupQualChange() {
  handleSetupStageChange();
}

// ==========================================
// 15. USER SETTINGS & PREFERENCES
// ==========================================
async function openSettingsModal() {
  const modal = document.getElementById('settings-modal');
  const dropdown = document.getElementById('user-dropdown-panel');
  if (dropdown) dropdown.classList.add('hidden');

  try {
    const res = await fetch('/api/auth/me');
    const data = await res.json();
    if (data.preferences) {
      const p = data.preferences;
      const inApp = document.getElementById('setting-inapp');
      const email = document.getElementById('setting-email');
      const push = document.getElementById('setting-push');
      const freq = document.getElementById('setting-email-freq');
      if (inApp) inApp.checked = p.in_app_enabled;
      if (email) email.checked = p.email_enabled;
      if (push) push.checked = p.push_enabled;
      if (freq && p.email_frequency) freq.value = p.email_frequency;
    }
  } catch (e) {}

  if (modal) modal.classList.remove('hidden');
  refreshIcons();
}

function closeSettingsModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('close-btn')) return;
  const modal = document.getElementById('settings-modal');
  if (modal) modal.classList.add('hidden');
}

async function saveUserSettings() {
  const statusBox = document.getElementById('settings-status-msg');
  const inApp = document.getElementById('setting-inapp')?.checked ?? true;
  const email = document.getElementById('setting-email')?.checked ?? true;
  const push = document.getElementById('setting-push')?.checked ?? false;
  const freq = document.getElementById('setting-email-freq')?.value || 'instant';

  try {
    const res = await fetch('/api/auth/settings', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        in_app_enabled: inApp,
        email_enabled: email,
        push_enabled: push,
        email_frequency: freq
      })
    });
    const data = await res.json();
    if (statusBox) {
      statusBox.textContent = data.message || 'Preferences updated successfully.';
      statusBox.style.background = '#ecfdf5';
      statusBox.style.color = '#065f46';
      statusBox.classList.remove('hidden');
      setTimeout(() => statusBox.classList.add('hidden'), 3500);
    }
  } catch (err) {
    if (statusBox) {
      statusBox.textContent = 'Failed to update preferences.';
      statusBox.style.background = '#fef2f2';
      statusBox.style.color = '#b91c1c';
      statusBox.classList.remove('hidden');
    }
  }
}

async function promptDeleteAccount() {
  if (!confirm('Are you sure you want to permanently delete your account, saved preferences, study plans, and notifications? This action cannot be reversed.')) {
    return;
  }
  try {
    const res = await fetch('/api/auth/delete-account', { method: 'POST' });
    if (res.ok) {
      alert('Your account has been deleted.');
      window.location.reload();
    }
  } catch (e) {
    alert('Account deletion failed.');
  }
}

// ==========================================
// 16. WEB PUSH NOTIFICATIONS
// ==========================================
function checkPushBanner() {
  const banner = document.getElementById('push-permission-banner');
  if (!banner) return;
  if (!('Notification' in window) || Notification.permission === 'granted' || Notification.permission === 'denied' || localStorage.getItem('cc_dismiss_push') === '1') {
    banner.classList.add('hidden');
  } else {
    banner.classList.remove('hidden');
  }
}

function dismissPushBanner() {
  localStorage.setItem('cc_dismiss_push', '1');
  const banner = document.getElementById('push-permission-banner');
  if (banner) banner.classList.add('hidden');
}

function urlB64ToUint8Array(base64String) {
  const padding = '='.repeat((4 - base64String.length % 4) % 4);
  const base64 = (base64String + padding).replace(/\-/g, '+').replace(/_/g, '/');
  const rawData = window.atob(base64);
  const outputArray = new Uint8Array(rawData.length);
  for (let i = 0; i < rawData.length; ++i) {
    outputArray[i] = rawData.charCodeAt(i);
  }
  return outputArray;
}

async function enablePushNotifications() {
  if (!('serviceWorker' in navigator) || !('PushManager' in window)) {
    alert('Web Push Notifications are not supported by this browser.');
    return;
  }

  try {
    const permission = await Notification.requestPermission();
    if (permission !== 'granted') {
      alert('Notification permission was not granted.');
      return;
    }

    const reg = await navigator.serviceWorker.register('/static/sw.js');
    await navigator.serviceWorker.ready;

    const keyRes = await fetch('/api/push/vapid-public-key');
    const keyData = await keyRes.json();
    if (!keyData.public_key) {
      console.warn('VAPID public key unavailable.');
      return;
    }

    const sub = await reg.pushManager.subscribe({
      userVisibleOnly: true,
      applicationServerKey: urlB64ToUint8Array(keyData.public_key)
    });

    const subJSON = sub.toJSON();
    await fetch('/api/push/subscribe', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        endpoint: sub.endpoint,
        keys: subJSON.keys
      })
    });

    dismissPushBanner();
    alert('Push Notifications enabled! You will now receive verified opportunity and deadline alerts.');
  } catch (err) {
    console.error('Push notification registration error:', err);
    alert('Could not subscribe for push notifications: ' + err.message);
  }
}

// ==========================================
// 17. SAVED OPPORTUNITIES & BOOKMARKS
// ==========================================
async function openSavedOpportunitiesModal() {
  const modal = document.getElementById('saved-opps-modal');
  const dropdown = document.getElementById('user-dropdown-panel');
  if (dropdown) dropdown.classList.add('hidden');
  if (modal) modal.classList.remove('hidden');
  refreshIcons();
  await loadSavedOpportunities();
}

function closeSavedOpportunitiesModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('close-btn')) return;
  const modal = document.getElementById('saved-opps-modal');
  if (modal) modal.classList.add('hidden');
}

async function loadSavedOpportunities() {
  const container = document.getElementById('saved-opps-list');
  if (!container) return;
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';

  try {
    const res = await fetch('/api/opportunities/saved');
    if (res.status === 401) {
      container.innerHTML = '<div class="empty-state" style="text-align: center; padding: 2rem;"><p>Please <a href="#" onclick="openAuthModal(\'login\'); return false;" style="color: var(--primary); font-weight: 600;">Sign In</a> to save and track opportunity deadlines.</p></div>';
      return;
    }
    const data = await res.json();
    const saved = data.saved_opportunities || [];
    if (saved.length === 0) {
      container.innerHTML = '<div class="empty-state" style="text-align: center; padding: 2rem;"><p style="color: var(--text-secondary);">No saved opportunities yet. Click the bookmark icon on any exam or job card to save it here.</p></div>';
      return;
    }

    container.innerHTML = saved.map(opp => `
      <div style="background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: 8px; padding: 1rem; display: flex; justify-content: space-between; align-items: center; gap: 1rem;">
        <div>
          <span class="badge badge-primary" style="font-size: 0.7rem; text-transform: uppercase;">${escapeHtml(opp.category || 'OPPORTUNITY')}</span>
          <h4 style="font-size: 0.98rem; font-weight: 700; margin: 0.35rem 0 0.2rem; color: var(--text-main);">${escapeHtml(opp.title)}</h4>
          <p style="font-size: 0.8rem; color: var(--text-secondary); margin: 0;">${escapeHtml(opp.organization || '')} • Deadline: <strong>${escapeHtml(opp.deadline || 'Ongoing')}</strong></p>
        </div>
        <div style="display: flex; gap: 0.5rem; flex-shrink: 0;">
          ${opp.link ? `<a href="${escapeHtml(opp.link)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-primary"><i data-lucide="external-link" class="icon-xs"></i> Visit</a>` : ''}
          <button class="btn btn-sm btn-outline-danger" onclick="removeSavedOpportunity('${escapeHtml(opp.opportunity_id)}')"><i data-lucide="trash-2" class="icon-xs"></i></button>
        </div>
      </div>
    `).join('');
    refreshIcons();
  } catch (err) {
    container.innerHTML = '<p class="text-danger">Unable to load saved opportunities.</p>';
  }
}

async function removeSavedOpportunity(oppId) {
  try {
    const res = await fetch('/api/opportunities/unsave', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ opportunity_id: oppId })
    });
    if (res.ok) {
      await loadSavedOpportunities();
    }
  } catch (e) {
    console.error('Error removing saved opportunity:', e);
  }
}

async function saveOpportunity(oppId, title, org, cat, deadline, link) {
  try {
    const res = await fetch('/api/opportunities/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        opportunity_id: oppId,
        title: title,
        organization: org,
        category: cat,
        deadline: deadline,
        link: link
      })
    });
    if (res.status === 401) {
      openAuthModal('login');
      return;
    }
    const data = await res.json();
    alert(data.message || 'Saved to your bookmarks!');
  } catch (e) {
    console.error('Error saving opportunity:', e);
  }
}

// ==========================================
// 18. PREPARATION HUB & FREE PRACTICE & TRAINING RESOURCES
// ==========================================
let currentExamDetailData = null;
let currentExamProgress = { completed_topics: [] };
let currentExamDetailTab = 'overview';
let currentSelectedResourceCategory = 'All';

async function initPreparationHub() {
  updatePrepHubUserSummary();
  const activeTab = AppState.currentPrepHubTab || 'practice';
  switchPrepHubTab(activeTab);
  loadTrackerProgress();
}

function updatePrepHubUserSummary() {
  const card = document.getElementById('prep-hub-user-summary');
  if (!card) return;

  const profile = (currentUser && currentUser.profile) ? currentUser.profile : getStoredRadarProfile();
  const qual = (currentUser && currentUser.qualification) || (profile && (profile.qualification || profile.education_level)) || 'B.Tech';
  const stream = (currentUser && currentUser.stream) || (profile && (profile.stream || profile.branch || profile.stream_or_branch)) || 'Computer Science & Engineering';
  const exam = (profile && profile.target_exam) || (qual.toLowerCase().includes('10th') ? 'School Boards & NTSE' : (qual.toLowerCase().includes('inter') ? (stream.toLowerCase().includes('bipc') ? 'NEET UG' : 'JEE Main') : (qual.toLowerCase().includes('diploma') ? 'ECET / Lateral Entry' : 'GATE / Campus Placements')));

  const qualEl = document.getElementById('prep-summary-qual');
  const streamEl = document.getElementById('prep-summary-stream');
  const examEl = document.getElementById('prep-summary-exam');
  const pctEl = document.getElementById('prep-summary-pct');
  const barFillEl = document.getElementById('prep-summary-bar-fill');

  if (qualEl) qualEl.textContent = qual;
  if (streamEl) streamEl.textContent = stream;
  if (examEl) examEl.textContent = exam;

  const completedCount = (currentExamProgress?.completed_topics || []).length;
  const pct = completedCount > 0 ? Math.min(100, Math.round((completedCount / 12) * 100)) : 0;
  if (pctEl) pctEl.textContent = `${pct}%`;
  if (barFillEl) barFillEl.style.width = `${pct}%`;
}

let currentTrackerSession = null;
let trackerSessionStartTime = null;

async function loadTrackerProgress() {
  const panel = document.getElementById('tracker-dashboard-panel');
  if (!panel) return;

  try {
    const [progRes, planRes] = await Promise.all([
      fetch('/api/tracker/progress'),
      fetch('/api/tracker/study-plan')
    ]);

    if (progRes.ok) {
      const progData = await progRes.json();
      const summary = progData.summary || {};

      const pctEl = document.getElementById('tracker-overall-stat');
      if (pctEl) pctEl.textContent = `${summary.overall_completion_pct || 0}%`;

      const topicsEl = document.getElementById('tracker-topics-count');
      if (topicsEl) topicsEl.textContent = summary.completed_topics_count || 0;

      const studyEl = document.getElementById('tracker-study-mins');
      if (studyEl) studyEl.textContent = `${((summary.total_study_minutes || 0) / 60).toFixed(1)} hrs`;

      const practiceEl = document.getElementById('tracker-practice-mins');
      if (practiceEl) practiceEl.textContent = `${((summary.total_practice_minutes || 0) / 60).toFixed(1)} hrs`;

      const qEl = document.getElementById('tracker-questions-count');
      if (qEl) qEl.textContent = summary.total_questions_solved || 0;

      const streakEl = document.getElementById('tracker-streak-count');
      if (streakEl) streakEl.textContent = `${summary.current_streak_days || 0} Days`;

      // Update the mini progress bar in prep-summary card
      const prepPctEl = document.getElementById('prep-summary-pct');
      const prepBarFillEl = document.getElementById('prep-summary-bar-fill');
      const progressVal = summary.overall_completion_pct || 0;
      if (prepPctEl) prepPctEl.textContent = `${progressVal}%`;
      if (prepBarFillEl) prepBarFillEl.style.width = `${progressVal}%`;
    }

    if (planRes.ok) {
      const planData = await planRes.json();
      const plan = planData.plan || {};
      if (plan.topics && plan.topics.length > 0) {
        const activeTopic = plan.topics[0];
        const topicEl = document.getElementById('tracker-active-topic');
        const descEl = document.getElementById('tracker-active-desc');
        const badgeEl = document.getElementById('tracker-topic-badge');
        if (topicEl) topicEl.textContent = activeTopic.topic;
        if (descEl) descEl.textContent = `${plan.target_focus || 'Core Preparation'} • Est: ${activeTopic.estimated_hours}h • Stage 1 Priority`;
        if (badgeEl) badgeEl.textContent = plan.target_focus || 'Target Plan';
      }
    }
  } catch (err) {
    console.error('Error loading tracker progress:', err);
  }
}

async function handleTrackerStartTopic() {
  const topicEl = document.getElementById('tracker-active-topic');
  const topic = topicEl?.textContent || 'Core Concepts';
  const startBtn = document.getElementById('btn-tracker-start');

  try {
    if (startBtn) {
      startBtn.disabled = true;
      startBtn.innerHTML = '<i data-lucide="loader" class="icon-xs spin"></i> Starting...';
    }
    const res = await fetch('/api/tracker/start-topic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ subject: 'General', topic: topic })
    });
    const data = await res.json();
    if (res.ok && data.status === 'success') {
      currentTrackerSession = data.session_id;
      trackerSessionStartTime = Date.now();
      if (startBtn) {
        startBtn.classList.remove('btn-primary');
        startBtn.classList.add('btn-success');
        startBtn.innerHTML = '<i data-lucide="check" class="icon-xs"></i> Learning Active';
      }
      refreshIcons();
    }
  } catch (err) {
    console.error('Error starting topic:', err);
  } finally {
    if (startBtn) startBtn.disabled = false;
    refreshIcons();
  }
}

async function handleTrackerCompleteTopic() {
  const topicEl = document.getElementById('tracker-active-topic');
  const topic = topicEl?.textContent || 'Core Concepts';
  const compBtn = document.getElementById('btn-tracker-complete');
  const duration = trackerSessionStartTime ? Math.max(1, Math.round((Date.now() - trackerSessionStartTime) / 60000)) : 30;

  try {
    if (compBtn) {
      compBtn.disabled = true;
      compBtn.innerHTML = '<i data-lucide="loader" class="icon-xs spin"></i> Saving...';
    }
    const res = await fetch('/api/tracker/complete-topic', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        subject: 'General',
        topic: topic,
        duration_minutes: duration,
        questions_solved: 5,
        score_pct: 100
      })
    });
    const data = await res.json();
    if (res.ok && data.status === 'success') {
      trackerSessionStartTime = null;
      currentTrackerSession = null;
      await loadTrackerProgress();
      if (compBtn) {
        compBtn.innerHTML = '<i data-lucide="check-circle" class="icon-xs"></i> Completed!';
        setTimeout(() => {
          compBtn.innerHTML = '<i data-lucide="check-circle" class="icon-xs"></i> Mark Complete';
          refreshIcons();
        }, 2000);
      }
    }
  } catch (err) {
    console.error('Error completing topic:', err);
  } finally {
    if (compBtn) compBtn.disabled = false;
    refreshIcons();
  }
}

function switchPrepHubTab(tabName) {
  AppState.currentPrepHubTab = tabName;

  document.querySelectorAll('.prep-tab-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-tab') === tabName);
  });

  document.querySelectorAll('.prep-subview').forEach(view => {
    if (view.id === `prep-subview-${tabName}`) {
      view.classList.remove('hidden');
      view.classList.add('active');
    } else {
      view.classList.remove('active');
      view.classList.add('hidden');
    }
  });

  if (tabName === 'practice') {
    loadLearningResources();
  } else if (tabName === 'exams') {
    loadExamPrepHub();
  } else if (tabName === 'study-materials') {
    loadStudyMaterialsTab();
  } else if (tabName === 'books') {
    loadBooksTab();
  } else if (tabName === 'pyqs') {
    loadPyqsTab();
  } else if (tabName === 'mocks') {
    loadMocksTab();
  } else if (tabName === 'plans') {
    loadPlansTab();
  } else if (tabName === 'ai') {
    const input = document.getElementById('ai-study-input');
    if (input) setTimeout(() => input.focus(), 150);
  }

  refreshIcons();
}

// ====================================================
// PRACTICE & TRAINING: TOPICS, QUIZ & LEARNING PLATFORMS
// ====================================================

let currentSelectedResourceCategory = 'All';
let currentPracticeTopics = [];
let currentQuizQuestions = [];
let currentQuizIndex = 0;
let quizAnswerState = {}; // { question_id: { selected_index, is_correct } }
let quizScore = 0;
let activePracticeViewMode = 'topics';

function matchPracticeCategory(resourceCategory, selectedCategory) {
  if (!selectedCategory || selectedCategory === 'All' || selectedCategory === 'All Categories') return true;
  if (!resourceCategory) return false;
  const rCat = resourceCategory.toLowerCase().trim();
  const sCat = selectedCategory.toLowerCase().trim();
  if (rCat === sCat) return true;

  const aliasMap = {
    'aptitude': ['aptitude & technical practice', 'aptitude', 'quantitative aptitude', 'quantitative', 'math'],
    'reasoning': ['reasoning', 'logical reasoning', 'analytical reasoning', 'aptitude & technical practice', 'mental ability'],
    'coding and cs fundamentals': ['coding & cs fundamentals', 'coding & programming', 'coding & interview preparation', 'coding & skills certification', 'gate preparation & cs fundamentals', 'computer science'],
    'coding & cs fundamentals': ['coding and cs fundamentals', 'coding & programming', 'coding & interview preparation', 'coding & skills certification', 'gate preparation & cs fundamentals', 'computer science'],
    'placement preparation': ['placement preparation', 'resume & interview skills', 'coding & interview preparation', 'aptitude & technical practice'],
    'interview preparation': ['interview preparation', 'resume & interview skills', 'coding & interview preparation'],
    'engineering preparation': ['core engineering', 'core engineering (ece / eee)', 'core engineering (mechanical / civil)', 'core engineering lab simulations', 'core engineering & higher education', 'engineering'],
    'core engineering': ['core engineering', 'core engineering (ece / eee)', 'core engineering (mechanical / civil)', 'core engineering lab simulations', 'core engineering & higher education', 'engineering preparation'],
    'skill development': ['skill development', 'technical & diploma skill building', 'professional skills & certifications'],
    'web development': ['web development & programming', 'web development', 'programming'],
    'ai and data science': ['ai, ml & data science', 'ai and data science', 'data science', 'ai & data science', 'machine learning'],
    'ai & data science': ['ai, ml & data science', 'ai and data science', 'data science', 'ai & data science', 'machine learning'],
    'ai, ml & data science': ['ai, ml & data science', 'ai and data science', 'data science', 'ai & data science', 'machine learning'],
    'school & foundation learning': ['school & foundation learning', 'school subjects & textbooks', 'school subjects'],
    'school subjects': ['school & foundation learning', 'school subjects & textbooks', 'school subjects'],
    'entrance exams': ['official mock tests & entrance exams', 'entrance exams', 'academic courses & certification'],
    'lateral entry (ecet)': ['technical & diploma skill building', 'core engineering lab simulations', 'lateral entry (ecet)']
  };

  if (aliasMap[sCat]) {
    for (const a of aliasMap[sCat]) {
      if (rCat.includes(a) || a.includes(rCat)) return true;
    }
  }

  return rCat.includes(sCat) || sCat.includes(rCat);
}

async function loadLearningResources() {
  const container = document.getElementById('prep-resource-grid');
  if (!container) return;
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';

  const profile = (currentUser && currentUser.profile) ? currentUser.profile : getStoredRadarProfile();
  const qual = (currentUser && currentUser.qualification) || (profile && (profile.qualification || profile.education_level)) || 'B.Tech';
  const stream = (currentUser && currentUser.stream) || (profile && (profile.stream || profile.branch)) || '';

  // 1. Load qualification-adapted category chips
  await loadResourceCategories(qual, stream);

  // 2. Load structured practice topics & quiz
  await loadPracticeTopics(currentSelectedResourceCategory, qual, stream);

  // 3. Load verified platforms
  try {
    const url = `/api/resources?qualification=${encodeURIComponent(qual)}&stream=${encodeURIComponent(stream)}`;
    const res = await fetch(url);
    const data = await res.json();
    window.LEARNING_RESOURCES_DATA = data.resources || [];
    filterLearningResources();
  } catch (err) {
    console.error('Error loading learning resources:', err);
    container.innerHTML = '<div class="empty-state text-danger"><p>Unable to load learning resources. Please try again.</p></div>';
  }
}

async function loadResourceCategories(qual, stream) {
  const container = document.getElementById('prep-resource-category-chips');
  if (!container) return;

  try {
    const url = `/api/practice-training/categories?qualification=${encodeURIComponent(qual || '')}&stream=${encodeURIComponent(stream || '')}`;
    const res = await fetch(url);
    const data = await res.json();
    const categories = data.categories || [];

    window.PRACTICE_CATEGORIES_METADATA = categories;

    container.innerHTML = categories.map(c => {
      const catName = typeof c === 'string' ? c : (c.name || c.id);
      const icon = (typeof c === 'object' && c.icon) ? c.icon : 'book';
      const isActive = currentSelectedResourceCategory === catName || (currentSelectedResourceCategory === 'All' && (catName === 'All' || catName === 'All Categories'));
      const countPill = (c.count && c.count > 0) ? `<span style="opacity: 0.7; font-size: 0.72rem; margin-left: 0.25rem;">(${c.count})</span>` : '';
      return `
        <button class="filter-chip ${isActive ? 'active' : ''}" onclick="filterLearningResourcesByCategory('${escapeHtml(catName)}')">
          <i data-lucide="${escapeHtml(icon)}" class="icon-xxs"></i>
          <span>${escapeHtml(catName)}</span>
          ${countPill}
        </button>
      `;
    }).join('');

    refreshIcons();
  } catch (err) {
    console.warn('Error loading resource categories:', err);
  }
}

async function loadPracticeTopics(category, qual, stream) {
  const topicsContainer = document.getElementById('practice-topics-container');
  if (!topicsContainer) return;

  topicsContainer.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';

  try {
    const query = (document.getElementById('prep-resource-search')?.value || '').trim();
    const url = `/api/practice-training/topics?category=${encodeURIComponent(category || 'All')}&qualification=${encodeURIComponent(qual || '')}&stream=${encodeURIComponent(stream || '')}&q=${encodeURIComponent(query)}`;
    const res = await fetch(url);
    const data = await res.json();
    currentPracticeTopics = data.topics || [];

    // Render Banner
    renderPracticeCategoryBanner(category, currentPracticeTopics);

    // Render Topics Accordion
    renderPracticeTopics(currentPracticeTopics);

    // Initialize Quiz from topics
    initPracticeQuiz(currentPracticeTopics);
  } catch (err) {
    console.error('Error loading practice topics:', err);
    topicsContainer.innerHTML = '<div class="empty-state text-danger"><p>Unable to load preparation topics. Please try again.</p></div>';
  }
}

function renderPracticeCategoryBanner(selectedCat, topics) {
  const banner = document.getElementById('practice-category-banner');
  if (!banner) return;

  const metaList = window.PRACTICE_CATEGORIES_METADATA || [];
  const meta = metaList.find(m => m.name === selectedCat || m.id === selectedCat) || {};

  const iconName = meta.icon || (selectedCat === 'All' || selectedCat === 'All Categories' ? 'layers' : 'book-open');
  const catTitle = (selectedCat === 'All' || selectedCat === 'All Categories') ? 'All Categories' : selectedCat;
  const description = meta.description || 'Comprehensive curriculum, formulas, cheatsheets, and verified interactive practice questions.';
  const questionCount = topics.reduce((sum, t) => sum + (t.practice_questions ? t.practice_questions.length : 0), 0);

  banner.innerHTML = `
    <div class="practice-cat-banner-header">
      <div class="practice-cat-banner-title">
        <span class="resource-icon-wrap" style="background: var(--primary-light); color: var(--primary);"><i data-lucide="${escapeHtml(iconName)}" class="icon-sm"></i></span>
        <div>
          <h3>${escapeHtml(catTitle)}</h3>
          <p class="practice-cat-banner-desc">${escapeHtml(description)}</p>
        </div>
      </div>
      <div class="practice-cat-banner-stats">
        <span class="practice-stat-pill"><i data-lucide="book" class="icon-xxs"></i> ${topics.length} Study Topics</span>
        <span class="practice-stat-pill"><i data-lucide="help-circle" class="icon-xxs"></i> ${questionCount} Practice Questions</span>
        <span class="practice-stat-pill"><i data-lucide="shield-check" class="icon-xxs" style="color: #059669;"></i> Verified Free Resources</span>
      </div>
    </div>
  `;

  refreshIcons();
}

function renderPracticeTopics(topics) {
  const container = document.getElementById('practice-topics-container');
  if (!container) return;

  if (!topics || topics.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="padding: 2.5rem 1rem; text-align: center; border: 1px dashed var(--border-color); border-radius: var(--radius-lg);">
        <i data-lucide="book-open" class="icon-md text-muted" style="margin-bottom: 0.5rem;"></i>
        <h4>No topics match your current search</h4>
        <p style="color: var(--text-secondary); font-size: 0.85rem;">Try clearing your search query or selecting a different category.</p>
        <button class="btn btn-outline-primary btn-sm" onclick="resetResourceFilters()"><i data-lucide="rotate-ccw" class="icon-xs"></i> Reset Filters</button>
      </div>
    `;
    refreshIcons();
    return;
  }

  container.innerHTML = topics.map(t => {
    const level = (t.level || 'Intermediate').toLowerCase();
    const concepts = Array.isArray(t.key_concepts) ? t.key_concepts : [];
    const materials = Array.isArray(t.learning_materials) ? t.learning_materials : [];
    const questions = Array.isArray(t.practice_questions) ? t.practice_questions : [];

    return `
      <div class="practice-topic-card" id="topic-card-${escapeHtml(t.id)}">
        <div class="topic-top-bar">
          <div class="topic-title-group">
            <h4>${escapeHtml(t.title)}</h4>
            <div class="topic-meta-badges">
              <span class="topic-level-badge ${escapeHtml(level)}">${escapeHtml(t.level || 'Intermediate')}</span>
              <span class="topic-time-pill"><i data-lucide="clock" class="icon-xxs"></i> ${escapeHtml(t.estimated_time || '30 mins')}</span>
              <span class="resource-pill" style="font-size: 0.72rem;">${escapeHtml(t.category_name || 'General')}</span>
            </div>
          </div>
          <button class="btn btn-primary btn-sm" style="display: inline-flex; align-items: center; gap: 0.35rem;" onclick="startTopicQuiz('${escapeHtml(t.id)}')">
            <i data-lucide="sparkles" class="icon-xs"></i> <span>Practice Quiz (${questions.length} Qs)</span>
          </button>
        </div>

        <p class="topic-short-desc">${escapeHtml(t.short_description || '')}</p>

        ${concepts.length > 0 ? `
          <div class="topic-cheat-sheet">
            <div class="topic-cheat-sheet-title">
              <i data-lucide="zap" class="icon-xxs"></i> Key Concepts & Formulas Cheat Sheet
            </div>
            <ul class="topic-concepts-list">
              ${concepts.map(c => `<li>${escapeHtml(c)}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        <div id="topic-notes-${escapeHtml(t.id)}" class="topic-notes-drawer hidden">
          <h5 style="font-size: 0.95rem; font-weight: 700; color: var(--text-main); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem;">
            <i data-lucide="book-marked" class="icon-xs text-primary"></i> Comprehensive Study Guide & Examples
          </h5>
          <p style="margin: 0; white-space: pre-line;">${escapeHtml(t.study_notes || 'No extended notes available.')}</p>
        </div>

        ${materials.length > 0 ? `
          <div class="topic-materials-row">
            <span style="font-size: 0.75rem; font-weight: 700; color: var(--text-muted); display: inline-flex; align-items: center; gap: 0.25rem;">
              <i data-lucide="external-link" class="icon-xxs"></i> Verified Tutorials:
            </span>
            ${materials.map(m => `
              <a href="${escapeHtml(m.url)}" target="_blank" rel="noopener noreferrer" class="topic-material-link">
                <span>${escapeHtml(m.title)}</span> <i data-lucide="arrow-up-right" class="icon-xxs"></i>
              </a>
            `).join('')}
          </div>
        ` : ''}

        <div class="topic-footer-actions">
          <button class="btn btn-outline-secondary btn-sm" id="btn-toggle-${escapeHtml(t.id)}" onclick="toggleTopicNotes('${escapeHtml(t.id)}')">
            <i data-lucide="book-open" class="icon-xs"></i> <span>View Detailed Study Notes</span>
          </button>
          <span style="font-size: 0.78rem; color: var(--text-muted); display: inline-flex; align-items: center; gap: 0.35rem;">
            <i data-lucide="check-circle-2" class="icon-xxs text-primary"></i> Official Free Learning Modules
          </span>
        </div>
      </div>
    `;
  }).join('');

  refreshIcons();
}

function toggleTopicNotes(topicId) {
  const drawer = document.getElementById(`topic-notes-${topicId}`);
  const btn = document.getElementById(`btn-toggle-${topicId}`);
  if (!drawer || !btn) return;

  const isHidden = drawer.classList.contains('hidden');
  if (isHidden) {
    drawer.classList.remove('hidden');
    btn.innerHTML = '<i data-lucide="chevron-up" class="icon-xs"></i> <span>Hide Study Notes</span>';
  } else {
    drawer.classList.add('hidden');
    btn.innerHTML = '<i data-lucide="book-open" class="icon-xs"></i> <span>View Detailed Study Notes</span>';
  }
  refreshIcons();
}

function switchPracticeViewMode(mode) {
  activePracticeViewMode = mode;
  document.querySelectorAll('.practice-switch-btn').forEach(btn => {
    btn.classList.toggle('active', btn.getAttribute('data-view') === mode);
  });

  const topicsWrap = document.getElementById('practice-topics-wrapper');
  const quizWrap = document.getElementById('practice-quiz-wrapper');
  const platformsWrap = document.getElementById('practice-platforms-wrapper');

  if (mode === 'topics') {
    if (topicsWrap) topicsWrap.classList.remove('hidden');
    if (quizWrap) quizWrap.classList.add('hidden');
    if (platformsWrap) platformsWrap.classList.remove('hidden');
  } else if (mode === 'quiz') {
    if (topicsWrap) topicsWrap.classList.add('hidden');
    if (quizWrap) quizWrap.classList.remove('hidden');
    if (platformsWrap) platformsWrap.classList.add('hidden');
    renderPracticeQuiz();
  } else if (mode === 'platforms') {
    if (topicsWrap) topicsWrap.classList.add('hidden');
    if (quizWrap) quizWrap.classList.add('hidden');
    if (platformsWrap) platformsWrap.classList.remove('hidden');
  }
  refreshIcons();
}

function initPracticeQuiz(topics) {
  currentQuizQuestions = [];
  topics.forEach(t => {
    if (Array.isArray(t.practice_questions)) {
      t.practice_questions.forEach(q => {
        currentQuizQuestions.push({
          ...q,
          topic_id: t.id,
          topic_title: t.title,
          category_name: t.category_name
        });
      });
    }
  });

  currentQuizIndex = 0;
  quizAnswerState = {};
  quizScore = 0;

  renderPracticeQuiz();
}

function startTopicQuiz(topicId) {
  const filtered = [];
  currentPracticeTopics.forEach(t => {
    if (t.id === topicId && Array.isArray(t.practice_questions)) {
      t.practice_questions.forEach(q => {
        filtered.push({
          ...q,
          topic_id: t.id,
          topic_title: t.title,
          category_name: t.category_name
        });
      });
    }
  });

  if (filtered.length > 0) {
    currentQuizQuestions = filtered;
    currentQuizIndex = 0;
    quizAnswerState = {};
    quizScore = 0;
  }

  switchPracticeViewMode('quiz');
  const quizSection = document.getElementById('practice-quiz-wrapper');
  if (quizSection) {
    quizSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }
}

function renderPracticeQuiz() {
  const container = document.getElementById('practice-quiz-container');
  if (!container) return;

  if (!currentQuizQuestions || currentQuizQuestions.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="padding: 2.5rem; text-align: center; border: 1px dashed var(--border-color); border-radius: var(--radius-lg); background: var(--bg-surface);">
        <i data-lucide="help-circle" class="icon-lg text-muted" style="margin-bottom: 0.75rem;"></i>
        <h4>No practice questions found for this topic</h4>
        <p style="color: var(--text-secondary); font-size: 0.85rem; margin-bottom: 1rem;">Select a different category or topic to take interactive quizzes.</p>
        <button class="btn btn-outline-primary btn-sm" onclick="switchPracticeViewMode('topics')"><i data-lucide="book-open" class="icon-xs"></i> Browse Topics</button>
      </div>
    `;
    refreshIcons();
    return;
  }

  const q = currentQuizQuestions[currentQuizIndex];
  const qState = quizAnswerState[q.id];
  const isAnswered = !!qState;
  const letters = ['A', 'B', 'C', 'D'];

  const answeredCount = Object.keys(quizAnswerState).length;
  const scorePercent = answeredCount > 0 ? Math.round((quizScore / answeredCount) * 100) : 0;

  container.innerHTML = `
    <div class="quiz-card">
      <div class="quiz-header">
        <div class="quiz-question-counter">
          <span class="badge badge-primary" style="font-size: 0.75rem;">Question ${currentQuizIndex + 1} of ${currentQuizQuestions.length}</span>
          <span style="font-size: 0.85rem; color: var(--text-muted);">|</span>
          <span style="font-size: 0.85rem; color: var(--text-secondary); font-weight: 600;">${escapeHtml(q.topic_title || q.category_name || 'Practice Question')}</span>
        </div>
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span class="quiz-score-pill"><i data-lucide="award" class="icon-xxs"></i> Score: ${quizScore}/${answeredCount} (${scorePercent}%)</span>
          <button class="btn btn-outline-secondary btn-sm" onclick="resetPracticeQuiz()" title="Reset Quiz"><i data-lucide="rotate-ccw" class="icon-xs"></i></button>
        </div>
      </div>

      <div class="quiz-question-text">${escapeHtml(q.question)}</div>

      <div class="quiz-options-list">
        ${q.options.map((opt, idx) => {
          let optionClass = '';
          let iconMark = '';
          if (isAnswered) {
            if (idx === q.correct_index) {
              optionClass = 'correct';
              iconMark = '<i data-lucide="check" class="icon-xs" style="color: #059669; margin-left: auto;"></i>';
            } else if (idx === qState.selected_index) {
              optionClass = 'incorrect';
              iconMark = '<i data-lucide="x" class="icon-xs" style="color: #dc2626; margin-left: auto;"></i>';
            }
          }
          return `
            <button class="quiz-option-btn ${optionClass} ${isAnswered ? 'disabled' : ''}" onclick="selectQuizOption('${escapeHtml(q.id)}', ${idx})" ${isAnswered ? 'disabled' : ''}>
              <span class="quiz-option-letter">${letters[idx]}</span>
              <span>${escapeHtml(opt)}</span>
              ${iconMark}
            </button>
          `;
        }).join('')}
      </div>

      ${isAnswered ? `
        <div class="quiz-explanation-box">
          <h5><i data-lucide="${qState.is_correct ? 'check-circle' : 'alert-circle'}" class="icon-xs"></i> ${qState.is_correct ? 'Correct! Step-by-Step Solution:' : 'Incorrect. Step-by-Step Solution:'}</h5>
          <p>${escapeHtml(q.explanation || 'Solution explained above.')}</p>
        </div>
      ` : ''}

      <div class="quiz-controls-row">
        <button class="btn btn-outline-secondary btn-sm" onclick="prevQuizQuestion()" ${currentQuizIndex === 0 ? 'disabled' : ''}>
          <i data-lucide="arrow-left" class="icon-xs"></i> Previous
        </button>
        <span style="font-size: 0.8rem; color: var(--text-muted);">
          ${isAnswered ? 'Answer verified. Proceed to next question.' : 'Select an option to check your answer.'}
        </span>
        <button class="btn btn-primary btn-sm" onclick="nextQuizQuestion()" ${currentQuizIndex >= currentQuizQuestions.length - 1 ? 'disabled' : ''}>
          Next Question <i data-lucide="arrow-right" class="icon-xs"></i>
        </button>
      </div>
    </div>
  `;

  refreshIcons();
}

function selectQuizOption(questionId, optionIndex) {
  const q = currentQuizQuestions[currentQuizIndex];
  if (!q || q.id !== questionId) return;
  if (quizAnswerState[questionId]) return; // Already answered

  const isCorrect = optionIndex === q.correct_index;
  if (isCorrect) {
    quizScore++;
  }

  quizAnswerState[questionId] = {
    selected_index: optionIndex,
    is_correct: isCorrect
  };

  // Record progress via backend API
  if (currentUser) {
    try {
      fetch('/api/practice-training/submit-quiz', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          topic_id: q.topic_id || 'general',
          score: quizScore,
          total: Object.keys(quizAnswerState).length,
          practice_minutes: 5
        })
      }).catch(() => {});
    } catch (e) {}
  }

  renderPracticeQuiz();
}

function nextQuizQuestion() {
  if (currentQuizIndex < currentQuizQuestions.length - 1) {
    currentQuizIndex++;
    renderPracticeQuiz();
  }
}

function prevQuizQuestion() {
  if (currentQuizIndex > 0) {
    currentQuizIndex--;
    renderPracticeQuiz();
  }
}

function resetPracticeQuiz() {
  quizAnswerState = {};
  quizScore = 0;
  currentQuizIndex = 0;
  renderPracticeQuiz();
}

function renderLearningResourceCards(resources) {
  const container = document.getElementById('prep-resource-grid');
  if (!container) return;

  if (!resources || resources.length === 0) {
    container.innerHTML = `
      <div class="empty-state" style="grid-column: 1 / -1; text-align: center; padding: 3rem 1.5rem; background: var(--bg-surface-muted); border-radius: var(--radius-lg); border: 1px dashed var(--border-color);">
        <i data-lucide="compass" class="icon-lg text-muted" style="margin-bottom: 0.75rem;"></i>
        <h4>No learning resources found for the selected filter</h4>
        <p style="color: var(--text-secondary); font-size: 0.85rem; max-width: 450px; margin: 0.5rem auto 1rem;">Try clearing your search query or selecting "All Access Types" / "All Categories".</p>
        <button class="btn btn-outline-primary btn-sm" onclick="resetResourceFilters()"><i data-lucide="rotate-ccw" class="icon-xs"></i> Reset Filters</button>
      </div>
    `;
    refreshIcons();
    return;
  }

  container.innerHTML = resources.map(r => {
    let accessBadgeClass = 'badge-free';
    let accessIcon = 'check-circle';
    let accessLabel = r.access_type || 'FREE';
    if (r.access_type === 'OFFICIAL FREE RESOURCE') {
      accessBadgeClass = 'badge-official';
      accessIcon = 'shield-check';
      accessLabel = 'Official Free Resource';
    } else if (r.access_type === 'FREE + PAID') {
      accessBadgeClass = 'badge-freemium';
      accessIcon = 'layers';
      accessLabel = 'Free + Paid';
    } else if (r.access_type === 'FREE') {
      accessBadgeClass = 'badge-free';
      accessIcon = 'check-circle';
      accessLabel = 'Free';
    } else if (r.access_type === 'PAID') {
      accessBadgeClass = 'badge-paid';
      accessIcon = 'lock';
      accessLabel = 'Paid';
    }

    const freeFeatures = Array.isArray(r.free_features) ? r.free_features.slice(0, 3) : [];
    const skills = Array.isArray(r.skills) ? r.skills.slice(0, 3) : [];

    return `
      <div class="resource-card">
        <div>
          <div class="resource-card-header">
            <span class="resource-badge-access ${accessBadgeClass}">
              <i data-lucide="${accessIcon}" class="icon-xs"></i> ${escapeHtml(accessLabel)}
            </span>
            <span class="resource-category-tag">${escapeHtml(r.category || 'General')}</span>
          </div>

          <div style="display: flex; align-items: center; gap: 0.5rem; margin-top: 0.6rem;">
            <h3 class="resource-card-title">${escapeHtml(r.name)}</h3>
            ${r.verification_status === 'VERIFIED' ? `
              <span class="verified-icon-chip" title="Verified Resource Platform">
                <i data-lucide="badge-check" class="icon-xs" style="color: #059669;"></i>
              </span>
            ` : ''}
          </div>

          <p class="resource-card-desc">${escapeHtml(r.description || '')}</p>

          ${freeFeatures.length > 0 ? `
            <div class="resource-features-list">
              <span class="features-label">Free Features:</span>
              ${freeFeatures.map(f => `
                <span class="resource-pill"><i data-lucide="check" class="icon-xxs"></i> ${escapeHtml(f)}</span>
              `).join('')}
            </div>
          ` : ''}

          ${skills.length > 0 ? `
            <div class="resource-skills-row">
              ${skills.map(s => `<span class="resource-tag-skill">${escapeHtml(s)}</span>`).join('')}
            </div>
          ` : ''}
        </div>

        <div class="resource-card-footer">
          <a href="${escapeHtml(r.official_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm flex-1" style="display: inline-flex; justify-content: center; align-items: center; gap: 0.4rem;">
            <i data-lucide="external-link" class="icon-xs"></i> <span>Visit Official Platform</span>
          </a>
          <button class="btn btn-outline-secondary btn-sm" title="Bookmark resource" onclick="saveOpportunity('${escapeHtml(r.id)}', '${escapeHtml(r.name)}', '${escapeHtml(r.category)}', 'Learning Resource', 'Practice Resource', '${escapeHtml(r.official_url)}')">
            <i data-lucide="bookmark" class="icon-xs"></i>
          </button>
        </div>
      </div>
    `;
  }).join('');

  refreshIcons();
}

function filterPracticeTopics() {
  const query = (document.getElementById('prep-resource-search')?.value || '').toLowerCase().trim();
  if (!currentPracticeTopics || currentPracticeTopics.length === 0) return;

  if (!query) {
    renderPracticeTopics(currentPracticeTopics);
    return;
  }

  const filtered = currentPracticeTopics.filter(t => {
    const matchTitle = t.title && t.title.toLowerCase().includes(query);
    const matchDesc = t.short_description && t.short_description.toLowerCase().includes(query);
    const matchConcepts = Array.isArray(t.key_concepts) && t.key_concepts.some(c => c.toLowerCase().includes(query));
    const matchCat = t.category_name && t.category_name.toLowerCase().includes(query);
    return matchTitle || matchDesc || matchConcepts || matchCat;
  });

  renderPracticeTopics(filtered);
}

function filterLearningResources() {
  const query = (document.getElementById('prep-resource-search')?.value || '').toLowerCase().trim();
  const accessFilter = document.getElementById('prep-resource-access-filter')?.value || 'All';
  const allResources = window.LEARNING_RESOURCES_DATA || [];

  const filtered = allResources.filter(r => {
    if (accessFilter !== 'All' && r.access_type !== accessFilter) {
      return false;
    }
    if (currentSelectedResourceCategory !== 'All' && currentSelectedResourceCategory !== 'All Categories') {
      if (!matchPracticeCategory(r.category, currentSelectedResourceCategory)) {
        return false;
      }
    }
    if (query) {
      const matchName = r.name && r.name.toLowerCase().includes(query);
      const matchDesc = r.description && r.description.toLowerCase().includes(query);
      const matchCat = r.category && r.category.toLowerCase().includes(query);
      const matchSkills = Array.isArray(r.skills) && r.skills.some(s => s.toLowerCase().includes(query));
      const matchExams = Array.isArray(r.exams) && r.exams.some(e => e.toLowerCase().includes(query));
      if (!matchName && !matchDesc && !matchCat && !matchSkills && !matchExams) {
        return false;
      }
    }
    return true;
  });

  renderLearningResourceCards(filtered);
  filterPracticeTopics();
}

function filterLearningResourcesByCategory(cat) {
  currentSelectedResourceCategory = cat;
  document.querySelectorAll('#prep-resource-category-chips .filter-chip').forEach(btn => {
    const labelSpan = btn.querySelector('span');
    const labelText = labelSpan ? labelSpan.textContent.trim() : btn.textContent.trim();
    const isTarget = labelText === cat || (cat === 'All' && (labelText === 'All' || labelText.includes('All')));
    btn.classList.toggle('active', isTarget);
  });

  const profile = (currentUser && currentUser.profile) ? currentUser.profile : getStoredRadarProfile();
  const qual = (currentUser && currentUser.qualification) || (profile && (profile.qualification || profile.education_level)) || 'B.Tech';
  const stream = (currentUser && currentUser.stream) || (profile && (profile.stream || profile.branch)) || '';

  loadPracticeTopics(cat, qual, stream);
  filterLearningResources();
}

function resetResourceFilters() {
  const searchInput = document.getElementById('prep-resource-search');
  const accessSelect = document.getElementById('prep-resource-access-filter');
  if (searchInput) searchInput.value = '';
  if (accessSelect) accessSelect.value = 'All';
  currentSelectedResourceCategory = 'All';
  document.querySelectorAll('#prep-resource-category-chips .filter-chip').forEach(btn => {
    const labelSpan = btn.querySelector('span');
    const labelText = labelSpan ? labelSpan.textContent.trim() : btn.textContent.trim();
    btn.classList.toggle('active', labelText === 'All' || labelText.includes('All'));
  });

  const profile = (currentUser && currentUser.profile) ? currentUser.profile : getStoredRadarProfile();
  const qual = (currentUser && currentUser.qualification) || (profile && (profile.qualification || profile.education_level)) || 'B.Tech';
  const stream = (currentUser && currentUser.stream) || (profile && (profile.stream || profile.branch)) || '';

  loadPracticeTopics('All', qual, stream);
  filterLearningResources();
}

async function ensureExamPrepDataLoaded() {
  if (window.EXAM_PREP_DATA && window.EXAM_PREP_DATA.length > 0) return window.EXAM_PREP_DATA;
  try {
    const res = await fetch('/api/exam-prep/list');
    const data = await res.json();
    window.EXAM_PREP_DATA = data.exams || [];
    return window.EXAM_PREP_DATA;
  } catch (e) {
    return [];
  }
}

async function loadStudyMaterialsTab() {
  const container = document.getElementById('prep-materials-grid');
  if (!container) return;
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';
  const exams = await ensureExamPrepDataLoaded();

  const materials = [];
  exams.forEach(exam => {
    if (exam.study_materials && Array.isArray(exam.study_materials)) {
      exam.study_materials.forEach(m => {
        materials.push({ ...m, exam_name: exam.name, exam_id: exam.id });
      });
    }
    if (exam.official_syllabus_url) {
      materials.push({
        title: `Official ${exam.name} Syllabus PDF`,
        type: 'Official Syllabus Document',
        url: exam.official_syllabus_url,
        source: exam.conducting_body,
        exam_name: exam.name,
        exam_id: exam.id
      });
    }
  });

  if (materials.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>No study materials available.</p></div>';
    return;
  }

  container.innerHTML = materials.map(m => `
    <div class="card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid var(--border-color); border-radius: var(--radius-md); background: var(--bg-surface);">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <span class="badge badge-primary" style="font-size: 0.72rem;">${escapeHtml(m.exam_name)}</span>
          <span style="font-size: 0.75rem; color: var(--text-secondary);">${escapeHtml(m.type || 'Study Notes')}</span>
        </div>
        <h4 style="font-size: 0.95rem; font-weight: 600; color: var(--text-main); margin-bottom: 0.35rem;">${escapeHtml(m.title)}</h4>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;"><i data-lucide="landmark" class="icon-xxs"></i> ${escapeHtml(m.source || 'Authorized Educational Portal')}</p>
      </div>
      <div style="display: flex; gap: 0.5rem;">
        <a href="${escapeHtml(m.url || '#')}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm flex-1" style="display: inline-flex; justify-content: center; align-items: center; gap: 0.35rem;">
          <i data-lucide="download" class="icon-xs"></i> Download / View Notes
        </a>
        <button class="btn btn-outline-secondary btn-sm" onclick="openExamDetailModal('${escapeHtml(m.exam_id)}')">Blueprint</button>
      </div>
    </div>
  `).join('');

  refreshIcons();
}

async function loadBooksTab() {
  const container = document.getElementById('prep-books-grid');
  if (!container) return;
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';
  const exams = await ensureExamPrepDataLoaded();

  const books = [];
  const seenTitles = new Set();

  exams.forEach(exam => {
    if (exam.recommended_books && Array.isArray(exam.recommended_books)) {
      exam.recommended_books.forEach(b => {
        const title = b.book_name || b.title;
        if (title && !seenTitles.has(title)) {
          seenTitles.add(title);
          books.push({ ...b, title, exam_name: exam.name, exam_id: exam.id });
        }
      });
    }
  });

  if (books.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>No standard reference books listed.</p></div>';
    return;
  }

  container.innerHTML = books.map(b => `
    <div class="card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid var(--border-color); border-radius: var(--radius-md); background: var(--bg-surface);">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <span class="badge badge-success" style="font-size: 0.72rem;"><i data-lucide="book" class="icon-xxs"></i> ${escapeHtml(b.subject || 'Standard Text')}</span>
          <span style="font-size: 0.75rem; color: var(--text-secondary);">${escapeHtml(b.exam_name)}</span>
        </div>
        <h4 style="font-size: 0.95rem; font-weight: 600; color: var(--text-main); margin-bottom: 0.35rem;">${escapeHtml(b.title)}</h4>
        <p style="font-size: 0.8rem; font-weight: 500; color: var(--primary); margin-bottom: 0.4rem;">Author: ${escapeHtml(b.author || 'Renowned Subject Authority')}</p>
        <p style="font-size: 0.8rem; color: var(--text-secondary); line-height: 1.4; margin-bottom: 1rem;">${escapeHtml(b.purpose || b.description || 'Recommended for foundational concepts and in-depth problem solving.')}</p>
      </div>
      <div style="display: flex; gap: 0.5rem;">
        <a href="${escapeHtml(b.verified_link || b.url || b.buy_link || '#')}" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary btn-sm flex-1" style="display: inline-flex; justify-content: center; align-items: center; gap: 0.35rem;">
          <i data-lucide="external-link" class="icon-xs"></i> View Book Details
        </a>
        <button class="btn btn-outline-secondary btn-sm" onclick="navigateToSection('digital-library')" title="Search Digital Library">
          <i data-lucide="library" class="icon-xs"></i>
        </button>
      </div>
    </div>
  `).join('');

  refreshIcons();
}

async function loadPyqsTab() {
  const container = document.getElementById('prep-pyqs-grid');
  if (!container) return;
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';
  const exams = await ensureExamPrepDataLoaded();

  const pyqs = [];
  exams.forEach(exam => {
    if (exam.previous_year_papers && Array.isArray(exam.previous_year_papers)) {
      exam.previous_year_papers.forEach(p => {
        pyqs.push({ ...p, exam_name: exam.name, exam_id: exam.id });
      });
    }
  });

  if (pyqs.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>No previous year question papers available.</p></div>';
    return;
  }

  container.innerHTML = pyqs.map(p => `
    <div class="card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid var(--border-color); border-radius: var(--radius-md); background: var(--bg-surface);">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <span class="badge badge-primary" style="font-size: 0.72rem;">${escapeHtml(p.exam_name)}</span>
          <span style="font-size: 0.78rem; font-weight: 600; color: var(--text-secondary);">${escapeHtml(p.year || 'Official')}</span>
        </div>
        <h4 style="font-size: 0.95rem; font-weight: 600; color: var(--text-main); margin-bottom: 0.35rem;">${escapeHtml(p.title || `${p.year} Official Question Paper`)}</h4>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;">Includes official questions and verified answer keys from authorized portal.</p>
      </div>
      <div style="display: flex; gap: 0.5rem;">
        <a href="${escapeHtml(p.url || p.official_pdf_url || '#')}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm flex-1" style="display: inline-flex; justify-content: center; align-items: center; gap: 0.35rem;">
          <i data-lucide="file-text" class="icon-xs"></i> Official Paper PDF
        </a>
        ${p.answer_key_url ? `
          <a href="${escapeHtml(p.answer_key_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-outline-secondary btn-sm" style="display: inline-flex; align-items: center; gap: 0.25rem;">
            <i data-lucide="check" class="icon-xs"></i> Key
          </a>
        ` : ''}
      </div>
    </div>
  `).join('');

  refreshIcons();
}

async function loadMocksTab() {
  const container = document.getElementById('prep-mocks-grid');
  if (!container) return;
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';
  const exams = await ensureExamPrepDataLoaded();

  const mocks = [];
  exams.forEach(exam => {
    if (exam.mock_tests && Array.isArray(exam.mock_tests)) {
      exam.mock_tests.forEach(m => {
        mocks.push({ ...m, exam_name: exam.name, exam_id: exam.id });
      });
    }
  });

  const resources = window.LEARNING_RESOURCES_DATA || [];
  resources.filter(r => r.category === 'Mock Tests & Exam Simulation' || (r.skills && r.skills.includes('Mock Tests'))).forEach(r => {
    mocks.push({
      title: `${r.name} Official Practice Platform`,
      portal_name: r.name,
      url: r.official_url,
      provider: r.official_source || 'Verified Platform',
      exam_name: 'Practice Simulator'
    });
  });

  if (mocks.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>No official mock tests currently listed.</p></div>';
    return;
  }

  container.innerHTML = mocks.map(m => `
    <div class="card" style="padding: 1.25rem; display: flex; flex-direction: column; justify-content: space-between; border: 1px solid var(--border-color); border-radius: var(--radius-md); background: var(--bg-surface);">
      <div>
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
          <span class="badge badge-primary" style="font-size: 0.72rem;">${escapeHtml(m.exam_name || 'CBT Mock')}</span>
          <span class="badge badge-success" style="font-size: 0.7rem;"><i data-lucide="play" class="icon-xxs"></i> Live Simulator</span>
        </div>
        <h4 style="font-size: 0.95rem; font-weight: 600; color: var(--text-main); margin-bottom: 0.35rem;">${escapeHtml(m.title || m.name || 'Official Exam Mock')}</h4>
        <p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 1rem;"><i data-lucide="monitor" class="icon-xxs"></i> Provider: ${escapeHtml(m.provider || m.portal_name || 'National Testing Authority')}</p>
      </div>
      <a href="${escapeHtml(m.url || '#')}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm w-full" style="display: inline-flex; justify-content: center; align-items: center; gap: 0.4rem;">
        <i data-lucide="play-circle" class="icon-xs"></i> <span>Launch Test Simulator</span>
      </a>
    </div>
  `).join('');

  refreshIcons();
}

async function loadPlansTab() {
  const container = document.getElementById('prep-plans-grid');
  if (!container) return;
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';
  const exams = await ensureExamPrepDataLoaded();

  if (exams.length === 0) {
    container.innerHTML = '<div class="empty-state"><p>No preparation plans found.</p></div>';
    return;
  }

  container.innerHTML = exams.map(exam => {
    const plans = exam.study_plans || {};
    const plan6 = plans['6_months'] || plans['6_month'] || 'Structured foundational phase covering 100% standard syllabus.';
    const plan3 = plans['3_months'] || plans['3_month'] || 'Intensive revision with topic-wise PYQs and high-weightage chapters.';
    const plan1 = plans['30_days'] || plans['30_day'] || 'Full-length CBT mock tests, error analysis, and formula revision.';

    function formatText(p) {
      if (typeof p === 'string') return escapeHtml(p);
      if (Array.isArray(p)) return p.map(item => `<div>• <strong>${escapeHtml(item.period || item.week || 'Phase')}:</strong> ${escapeHtml(item.focus || '')}</div>`).join('');
      return 'Plan details under curation.';
    }

    return `
      <div class="card" style="padding: 1.5rem; border: 1px solid var(--border-color); border-radius: var(--radius-md); background: var(--bg-surface); grid-column: 1 / -1;">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem;">
          <div>
            <h3 style="font-size: 1.1rem; font-weight: 700; color: var(--text-main); margin: 0 0 0.25rem;">${escapeHtml(exam.name)} Preparation Strategy</h3>
            <span style="font-size: 0.8rem; color: var(--primary); font-weight: 500;">${escapeHtml(exam.conducting_body)}</span>
          </div>
          <button class="btn btn-outline-primary btn-sm" onclick="openExamDetailModal('${escapeHtml(exam.id)}')">
            <i data-lucide="list-checks" class="icon-xs"></i> Full 24-Point Blueprint
          </button>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 1rem;">
          <div class="study-plan-card" style="border-left: 4px solid var(--primary); padding: 0.85rem; background: var(--bg-surface-muted); border-radius: 4px;">
            <h5 style="margin: 0 0 0.4rem; color: var(--primary); font-size: 0.9rem;">🗓️ 6-Month Comprehensive Plan</h5>
            <div style="font-size: 0.82rem; line-height: 1.5; color: var(--text-secondary);">${formatText(plan6)}</div>
          </div>
          <div class="study-plan-card" style="border-left: 4px solid #f59e0b; padding: 0.85rem; background: var(--bg-surface-muted); border-radius: 4px;">
            <h5 style="margin: 0 0 0.4rem; color: #d97706; font-size: 0.9rem;">⚡ 3-Month Fast-Track Sprint</h5>
            <div style="font-size: 0.82rem; line-height: 1.5; color: var(--text-secondary);">${formatText(plan3)}</div>
          </div>
          <div class="study-plan-card" style="border-left: 4px solid #ef4444; padding: 0.85rem; background: var(--bg-surface-muted); border-radius: 4px;">
            <h5 style="margin: 0 0 0.4rem; color: #dc2626; font-size: 0.9rem;">🔥 30-Day Final Blitz</h5>
            <div style="font-size: 0.82rem; line-height: 1.5; color: var(--text-secondary);">${formatText(plan1)}</div>
          </div>
        </div>
      </div>
    `;
  }).join('');

  refreshIcons();
}

function askAIStudySuggestion(query) {
  const input = document.getElementById('ai-study-input');
  if (input) {
    input.value = query;
  }
  submitAIStudyQuestion();
}

async function submitAIStudyQuestion() {
  const input = document.getElementById('ai-study-input');
  const submitBtn = document.getElementById('ai-study-submit-btn');
  const responseArea = document.getElementById('ai-study-response-area');
  if (!input || !responseArea) return;

  const question = input.value.trim();
  if (!question) {
    input.focus();
    return;
  }

  const profile = (currentUser && currentUser.profile) ? currentUser.profile : getStoredRadarProfile();
  const qual = (currentUser && currentUser.qualification) || (profile && profile.qualification) || 'B.Tech';
  const stream = (currentUser && currentUser.stream) || (profile && (profile.stream || profile.branch)) || '';
  const exam = (profile && profile.target_exam) || '';

  responseArea.classList.remove('hidden');
  responseArea.innerHTML = `
    <div class="ai-study-loading" style="padding: 1.5rem; text-align: center;">
      <div class="spinner"></div>
      <p style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 0.75rem;">Antigravity AI is formulating verified study guidance tailored to ${escapeHtml(qual)}...</p>
    </div>
  `;
  if (submitBtn) submitBtn.disabled = true;

  try {
    const res = await fetch('/api/ai/study-guidance', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ question, qualification: qual, stream, target_exam: exam })
    });
    const data = await res.json();
    if (!res.ok || data.error) {
      responseArea.innerHTML = `<p class="text-danger" style="padding: 1rem;">${escapeHtml(data.error || 'Failed to fetch AI guidance.')}</p>`;
      return;
    }

    const guidance = data.guidance || '';
    const recs = data.recommended_resources || [];

    let formattedText = escapeHtml(guidance)
      .replace(/^### (.*$)/gim, '<h4 style="color: var(--primary); margin: 0.85rem 0 0.35rem;">$1</h4>')
      .replace(/^## (.*$)/gim, '<h3 style="color: var(--text-main); margin: 1rem 0 0.5rem; font-size: 1.05rem;">$1</h3>')
      .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
      .replace(/^\* (.*$)/gim, '<li style="margin-bottom: 0.35rem;">$1</li>')
      .replace(/^- (.*$)/gim, '<li style="margin-bottom: 0.35rem;">$1</li>');

    formattedText = formattedText.replace(/\n\n/g, '<br><br>');

    responseArea.innerHTML = `
      <div class="ai-response-box" style="padding: 1.5rem; background: var(--bg-surface); border: 1px solid var(--border-color); border-radius: var(--radius-md);">
        <div class="ai-response-header" style="display: flex; align-items: center; gap: 0.5rem; border-bottom: 1px solid var(--border-color); padding-bottom: 0.75rem;">
          <i data-lucide="bot" class="icon-sm text-primary"></i>
          <span style="font-weight: 600; font-size: 0.92rem;">Verified Study Plan & Recommendations</span>
          <span class="badge badge-success" style="margin-left: auto; font-size: 0.7rem;"><i data-lucide="shield-check" class="icon-xxs"></i> Grounded in Official Portals</span>
        </div>
        <div class="ai-response-body" style="font-size: 0.88rem; line-height: 1.7; color: var(--text-main); margin-top: 0.85rem;">
          ${formattedText}
        </div>
        ${recs.length > 0 ? `
          <div class="ai-recs-section" style="margin-top: 1.25rem; border-top: 1px solid var(--border-color); padding-top: 1rem;">
            <h5 style="margin: 0 0 0.5rem; font-size: 0.82rem; color: var(--text-secondary); text-transform: uppercase;">Direct Resource Links:</h5>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem;">
              ${recs.map(r => `
                <a href="${escapeHtml(r.official_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-outline-primary btn-sm" style="display: inline-flex; align-items: center; gap: 0.35rem;">
                  <i data-lucide="external-link" class="icon-xxs"></i> <span>${escapeHtml(r.name)}</span>
                </a>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;
    refreshIcons();
  } catch (err) {
    console.error('AI study guidance error:', err);
    responseArea.innerHTML = '<p class="text-danger" style="padding: 1rem;">Error connecting to AI guidance service.</p>';
  } finally {
    if (submitBtn) submitBtn.disabled = false;
  }
}

function continueUserPreparation() {
  const profile = (currentUser && currentUser.profile) ? currentUser.profile : getStoredRadarProfile();
  const exam = (profile && profile.target_exam) || '';
  if (exam) {
    switchPrepHubTab('exams');
    const searchInput = document.getElementById('exam-prep-search-input');
    if (searchInput) {
      searchInput.value = exam;
      filterExamPrepCards();
    }
  } else {
    switchPrepHubTab('practice');
  }
}

function openPrepHubForOpportunity(title, category) {
  navigateToSection('exam-prep');
  if (category === 'Entrance Exam') {
    switchPrepHubTab('exams');
    const searchInput = document.getElementById('exam-prep-search-input');
    if (searchInput) {
      searchInput.value = title;
      filterExamPrepCards();
    }
  } else {
    switchPrepHubTab('practice');
    const searchInput = document.getElementById('prep-resource-search');
    if (searchInput) {
      searchInput.value = title;
      filterLearningResources();
    }
  }
}

async function loadExamPrepHub() {
  const container = document.getElementById('exam-prep-grid');
  if (!container) return;
  container.innerHTML = '<div class="loading-state"><div class="spinner"></div></div>';

  try {
    const res = await fetch('/api/exam-prep/list');
    const data = await res.json();
    window.EXAM_PREP_DATA = data.exams || [];
    renderExamPrepCards(window.EXAM_PREP_DATA);
  } catch (err) {
    container.innerHTML = '<p class="text-danger">Unable to load exam preparation blueprints.</p>';
  }
}

function renderExamPrepCards(exams) {
  const container = document.getElementById('exam-prep-grid');
  if (!container) return;

  if (!exams || exams.length === 0) {
    container.innerHTML = '<div class="empty-state" style="grid-column: 1 / -1; text-align: center; padding: 3rem;"><p>No examination blueprints matched your criteria.</p></div>';
    return;
  }

  container.innerHTML = exams.map(e => `
    <div class="exam-prep-card">
      <div>
        <span class="exam-card-badge">${escapeHtml(e.level || 'All India Exam')} • ${escapeHtml(e.frequency || 'Annual')}</span>
        <h3 class="exam-card-title">${escapeHtml(e.name)}</h3>
        <p style="font-size: 0.8rem; font-weight: 600; color: var(--primary); margin-bottom: 0.5rem;">${escapeHtml(e.conducting_body)}</p>
        <p class="exam-card-overview">${escapeHtml(e.overview || '')}</p>
        <div class="exam-card-tags">
          <span class="exam-tag"><i data-lucide="book" class="icon-xs"></i> ${e.total_syllabus_topics || 12} Topics</span>
          <span class="exam-tag"><i data-lucide="book-open" class="icon-xs"></i> ${e.standard_books_count || 4} Books</span>
          <span class="exam-tag"><i data-lucide="file-text" class="icon-xs"></i> ${e.pyq_papers_count || 5}+ PYQs</span>
        </div>
      </div>
      <div style="display: flex; gap: 0.5rem; margin-top: 1rem;">
        <button class="btn btn-primary btn-sm w-full" onclick="openExamDetailModal('${escapeHtml(e.id)}')">
          <i data-lucide="list-checks" class="icon-xs"></i> <span>24-Point Blueprint</span>
        </button>
        <button class="btn btn-outline-secondary btn-sm" title="Bookmark exam" onclick="saveOpportunity('${escapeHtml(e.id)}', '${escapeHtml(e.name)}', '${escapeHtml(e.conducting_body)}', 'Entrance Exam', 'See Blueprint', '${escapeHtml(e.official_website || '')}')">
          <i data-lucide="bookmark" class="icon-xs"></i>
        </button>
      </div>
    </div>
  `).join('');
  refreshIcons();
}

function filterExamPrepCards() {
  const query = (document.getElementById('exam-prep-search-input')?.value || '').toLowerCase().trim();
  const exams = window.EXAM_PREP_DATA || [];
  if (!query) {
    renderExamPrepCards(exams);
    return;
  }
  const filtered = exams.filter(e => 
    (e.name && e.name.toLowerCase().includes(query)) ||
    (e.conducting_body && e.conducting_body.toLowerCase().includes(query)) ||
    (e.target_qualification && e.target_qualification.toLowerCase().includes(query)) ||
    (Array.isArray(e.target_qualifications) && e.target_qualifications.some(q => q.toLowerCase().includes(query))) ||
    (e.overview && e.overview.toLowerCase().includes(query))
  );
  renderExamPrepCards(filtered);
}

function filterExamPrepCategory(cat) {
  document.querySelectorAll('#exam-prep-filter-chips .filter-chip').forEach(btn => {
    btn.classList.toggle('active', btn.textContent.includes(cat) || (cat === 'All' && btn.textContent.includes('All')));
  });

  const exams = window.EXAM_PREP_DATA || [];
  if (cat === 'All') {
    renderExamPrepCards(exams);
    return;
  }

  const filtered = exams.filter(e => {
    const qual = (e.target_qualification || '').toLowerCase();
    const id = e.id.toLowerCase();
    if (cat === 'Engineering') return id.includes('gate') || id.includes('jee') || id.includes('ecet');
    if (cat === 'Medical') return id.includes('neet');
    if (cat === 'Diploma') return id.includes('polycet') || id.includes('ecet');
    if (cat === 'Government') return id.includes('upsc') || id.includes('ssc');
    if (cat === 'Higher Studies') return id.includes('ugc') || id.includes('gate');
    return true;
  });
  renderExamPrepCards(filtered);
}

async function openExamDetailModal(examId) {
  const modal = document.getElementById('exam-detail-modal');
  const header = document.getElementById('exam-detail-header');
  const body = document.getElementById('exam-detail-body');
  const linkBtn = document.getElementById('exam-official-link-btn');
  if (modal) modal.classList.remove('hidden');

  if (header) header.innerHTML = '<div class="spinner"></div>';
  if (body) body.innerHTML = '<div class="spinner"></div>';

  try {
    const res = await fetch(`/api/exam-prep/${encodeURIComponent(examId)}`);
    const data = await res.json();
    const exam = data.exam;
    currentExamDetailData = exam;

    try {
      const progRes = await fetch(`/api/exam-prep/${encodeURIComponent(examId)}/progress`);
      if (progRes.ok) {
        const progData = await progRes.json();
        currentExamProgress = progData.progress || { completed_topics: [] };
      } else {
        currentExamProgress = { completed_topics: [] };
      }
    } catch (pe) {
      currentExamProgress = { completed_topics: [] };
    }

    if (linkBtn) {
      linkBtn.href = exam.official_website || '#';
    }

    if (header) {
      header.innerHTML = `
        <div style="display: flex; justify-content: space-between; align-items: flex-start; flex-wrap: wrap; gap: 0.75rem;">
          <div>
            <span class="badge badge-primary">${escapeHtml(exam.level)} • ${escapeHtml(exam.frequency)}</span>
            <h2 style="font-size: 1.5rem; font-weight: 800; margin: 0.35rem 0 0.2rem; color: var(--text-main);">${escapeHtml(exam.name)}</h2>
            <p style="font-size: 0.88rem; color: var(--primary); font-weight: 600; margin: 0;">${escapeHtml(exam.conducting_body)}</p>
          </div>
          <div style="text-align: right;">
            <span class="badge badge-warning" style="font-size: 0.8rem;">Target: ${escapeHtml(exam.target_qualification)}</span>
          </div>
        </div>
      `;
    }

    switchExamDetailTab('overview');
    refreshIcons();
  } catch (err) {
    if (body) body.innerHTML = '<p class="text-danger">Unable to load examination blueprint.</p>';
  }
}

function closeExamDetailModal(e) {
  if (e && e.target !== e.currentTarget && !e.target.classList.contains('close-btn')) return;
  const modal = document.getElementById('exam-detail-modal');
  if (modal) modal.classList.add('hidden');
}

function switchExamDetailTab(tab) {
  currentExamDetailTab = tab;
  ['overview', 'syllabus', 'books', 'pyqs', 'strategy'].forEach(t => {
    const btn = document.getElementById(`exam-tab-${t}`);
    if (btn) btn.classList.toggle('active', t === tab);
  });

  const body = document.getElementById('exam-detail-body');
  const footerStats = document.getElementById('exam-footer-stats');
  const exam = currentExamDetailData;
  if (!body || !exam) return;

  if (tab === 'overview') {
    body.innerHTML = `
      <div class="exam-point-block">
        <h4 class="exam-point-title"><i data-lucide="info" class="icon-xs"></i> 1. Examination Overview & Purpose</h4>
        <p style="font-size: 0.88rem; line-height: 1.6; color: var(--text-secondary);">${escapeHtml(exam.overview || '')}</p>
      </div>

      <div class="exam-point-block">
        <h4 class="exam-point-title"><i data-lucide="user-check" class="icon-xs"></i> 2. Eligibility & Academic Qualifications</h4>
        <div style="background: var(--bg-hover); padding: 1rem; border-radius: 8px; font-size: 0.85rem; line-height: 1.6;">
          <p><strong>Qualifying Degree / Exam:</strong> ${escapeHtml(exam.eligibility?.qualification || '')}</p>
          <p><strong>Minimum Marks:</strong> ${escapeHtml(exam.eligibility?.minimum_percentage || 'Passing marks as per regulations')}</p>
          <p><strong>Age Limits:</strong> ${escapeHtml(exam.eligibility?.age_criteria || 'No upper age limit for general eligibility')}</p>
          <p><strong>Number of Attempts:</strong> ${escapeHtml(exam.eligibility?.attempts || 'Unlimited attempts permitted')}</p>
        </div>
      </div>

      <div class="exam-point-block">
        <h4 class="exam-point-title"><i data-lucide="layout-grid" class="icon-xs"></i> 3. Exam Pattern & Marking Scheme</h4>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; font-size: 0.85rem;">
          <div style="background: var(--bg-hover); padding: 0.85rem; border-radius: 6px;">
            <strong>Mode:</strong><br>${escapeHtml(exam.pattern?.mode || 'Computer Based Test (CBT)')}
          </div>
          <div style="background: var(--bg-hover); padding: 0.85rem; border-radius: 6px;">
            <strong>Duration:</strong><br>${escapeHtml(exam.pattern?.duration || '180 Minutes (3 Hours)')}
          </div>
          <div style="background: var(--bg-hover); padding: 0.85rem; border-radius: 6px;">
            <strong>Total Marks:</strong><br>${escapeHtml(exam.pattern?.total_marks ? exam.pattern.total_marks.toString() : '100')} Marks
          </div>
          <div style="background: var(--bg-hover); padding: 0.85rem; border-radius: 6px;">
            <strong>Negative Marking:</strong><br>${escapeHtml(exam.pattern?.negative_marking || 'Applicable as per official brochure')}
          </div>
        </div>
      </div>
    `;
  } else if (tab === 'syllabus') {
    const completed = new Set(currentExamProgress?.completed_topics || []);
    let sections = [];
    if (Array.isArray(exam.subjects) && exam.subjects.length > 0) {
      sections = exam.subjects.map(subj => {
        const raw = (exam.topic_wise_syllabus && exam.topic_wise_syllabus[subj]) || '';
        let subtopics = [];
        if (typeof raw === 'string' && raw.trim()) {
          subtopics = raw.split(/,\s*|\.\s*/).map(s => s.trim()).filter(s => s.length > 2);
          if (subtopics.length === 0) subtopics = [subj];
        } else if (Array.isArray(raw)) {
          subtopics = raw;
        } else {
          subtopics = [subj];
        }
        return { name: subj, topics: subtopics.slice(0, 8) };
      });
    } else if (exam.syllabus?.sections) {
      sections = exam.syllabus.sections;
    }

    let allTopicsCount = 0;
    const sectionsHtml = sections.map((sec) => {
      const topics = sec.topics || [sec.name];
      allTopicsCount += topics.length;
      return `
        <div style="margin-bottom: 1.25rem;">
          <h5 style="font-size: 0.95rem; font-weight: 700; color: var(--primary); margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.4rem;">
            <i data-lucide="folder" class="icon-xs"></i> ${escapeHtml(sec.name)}
          </h5>
          <div style="display: flex; flex-direction: column; gap: 0.35rem; padding-left: 0.5rem;">
            ${topics.map((t) => {
              const topicKey = `${sec.name}:::${t}`;
              const isChecked = completed.has(topicKey) || completed.has(t);
              return `
                <label class="topic-checklist-item" style="cursor: pointer;">
                  <input type="checkbox" onchange="toggleTopicProgress('${escapeHtml(exam.id)}', '${escapeHtml(topicKey)}', this)" ${isChecked ? 'checked' : ''}>
                  <span class="${isChecked ? 'text-muted' : ''}" style="${isChecked ? 'text-decoration: line-through;' : ''}">${escapeHtml(t)}</span>
                </label>
              `;
            }).join('')}
          </div>
        </div>
      `;
    }).join('');

    body.innerHTML = `
      <div class="exam-point-block">
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.75rem;">
          <h4 class="exam-point-title" style="margin: 0;"><i data-lucide="check-square" class="icon-xs"></i> 4. Official Syllabus & Interactive Checklist</h4>
          <span style="font-size: 0.8rem; font-weight: 600; color: var(--primary);">${completed.size} / ${allTopicsCount} Completed</span>
        </div>
        <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 1rem;">
          Track your preparation mastery. Check off topics as you complete theory and standard problem-solving. Progress is saved directly to your account.
        </p>
        ${sectionsHtml || '<p>Detailed syllabus module breakdown coming soon.</p>'}
      </div>
    `;

    if (footerStats) {
      const pct = allTopicsCount > 0 ? Math.round((completed.size / allTopicsCount) * 100) : 0;
      footerStats.innerHTML = `<span><strong>Progress:</strong> ${completed.size} of ${allTopicsCount} topics checked (${pct}%)</span>`;
    }
  } else if (tab === 'books') {
    const books = exam.recommended_books || exam.verified_books || [];
    body.innerHTML = `
      <div class="exam-point-block">
        <h4 class="exam-point-title"><i data-lucide="book-open" class="icon-xs"></i> 5. Verified Accredited Textbooks (Zero Fake Books)</h4>
        <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 1rem;">
          Standard accredited reference books utilized by professors, GATE/JEE paper-setters, and top rankers. Verified with official publisher references and standard libraries.
        </p>
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 1rem;">
          ${books.map(b => {
            const title = b.book_name || b.title || 'Standard Textbook';
            const author = b.author || 'Renowned Author';
            const edition = b.edition || 'Standard Edition';
            const purpose = b.purpose || b.why_recommended || '';
            const link = b.verified_link || b.official_publisher_link || '';
            return `
              <div class="book-card">
                <span class="badge badge-secondary" style="font-size: 0.68rem; margin-bottom: 0.4rem;">${escapeHtml(b.subject || 'Standard Reference')}</span>
                <div class="book-card-title">${escapeHtml(title)}</div>
                <div class="book-meta"><strong>Author:</strong> ${escapeHtml(author)} • ${escapeHtml(edition)}</div>
                ${purpose ? `<p style="font-size: 0.8rem; color: var(--text-secondary); margin-bottom: 0.75rem;">${escapeHtml(purpose)}</p>` : ''}
                ${link ? `
                  <a href="${escapeHtml(link)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-primary" style="font-size: 0.75rem;">
                    <i data-lucide="external-link" class="icon-xs"></i> Official Reference
                  </a>
                ` : ''}
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  } else if (tab === 'pyqs') {
    const pyqs = exam.previous_year_papers || exam.previous_year_questions || exam.pyqs || [];
    const mocks = exam.mock_tests || exam.mock_test_portals || [];
    body.innerHTML = `
      <div class="exam-point-block">
        <h4 class="exam-point-title"><i data-lucide="file-text" class="icon-xs"></i> 6. Official Previous Year Question Papers (PYQs) & Answer Keys</h4>
        <p style="font-size: 0.82rem; color: var(--text-secondary); margin-bottom: 1rem;">
          Direct verified links to official master question papers with final answer keys released by the conducting institute.
        </p>
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          ${pyqs.map(p => {
            const yr = p.year ? p.year.toString() : 'Official';
            const desc = p.title || p.description || `${yr} Question Paper with Official Answer Key`;
            const url = p.url || p.official_pdf_url || p.download_url || '#';
            return `
              <div style="background: var(--bg-hover); padding: 0.75rem 1rem; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <strong>${escapeHtml(yr)} Paper & Official Key</strong>
                  <div style="font-size: 0.75rem; color: var(--text-secondary);">${escapeHtml(desc)}</div>
                </div>
                <div style="display: flex; gap: 0.4rem;">
                  <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-primary">
                    <i data-lucide="download" class="icon-xs"></i> Official PDF
                  </a>
                  ${p.answer_key_url ? `
                    <a href="${escapeHtml(p.answer_key_url)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-outline-secondary">
                      <i data-lucide="check" class="icon-xs"></i> Key
                    </a>
                  ` : ''}
                </div>
              </div>
            `;
          }).join('')}
        </div>
      </div>

      <div class="exam-point-block">
        <h4 class="exam-point-title"><i data-lucide="monitor" class="icon-xs"></i> 7. Official Mock Tests & CBT Simulation</h4>
        <div style="display: flex; flex-direction: column; gap: 0.5rem;">
          ${mocks.map(m => {
            const name = m.title || m.name || m.portal_name || 'Official CBT Mock';
            const url = m.url || m.official_url || '#';
            const details = m.provider || m.type || m.details || 'Official NTA / IIT CBT exam interface simulator';
            return `
              <div style="background: var(--bg-hover); padding: 0.75rem 1rem; border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                <div>
                  <strong>${escapeHtml(name)}</strong>
                  <div style="font-size: 0.75rem; color: var(--text-secondary);">${escapeHtml(details)}</div>
                </div>
                <a href="${escapeHtml(url)}" target="_blank" rel="noopener noreferrer" class="btn btn-sm btn-primary">
                  <i data-lucide="play" class="icon-xs"></i> Launch Simulator
                </a>
              </div>
            `;
          }).join('')}
        </div>
      </div>
    `;
  } else if (tab === 'strategy') {
    const plans = exam.study_plans || exam.study_strategy || {};
    const tips = (exam.toppers_strategy && exam.toppers_strategy.length > 0) ? exam.toppers_strategy : 
                 (exam.topper_tips && exam.topper_tips.length > 0) ? exam.topper_tips :
                 (exam.preparation_strategy ? [exam.preparation_strategy] : [
                   "Focus heavily on concept mastery from standard textbooks rather than rote memorization.",
                   "Solve previous 25-30 years of official question papers topic-wise.",
                   "Dedicate the final 4-6 weeks strictly to timed computer-based test full mocks."
                 ]);
    const mistakes = exam.pitfalls_to_avoid || [
      "Referring to multiple contradictory coaching booklets instead of standard accredited textbooks.",
      "Postponing full-length mock tests until the final two weeks.",
      "Neglecting negative marking and virtual calculator time penalties."
    ];

    function formatPlan(p) {
      if (!p) return 'Structured multi-week milestone plan under active curation.';
      if (Array.isArray(p)) {
        return p.map(item => `<div><strong>${escapeHtml(item.period || item.week || item.month || 'Phase')}:</strong> ${escapeHtml(item.focus || '')}</div>`).join('');
      }
      return escapeHtml(p);
    }

    body.innerHTML = `
      <div class="exam-point-block">
        <h4 class="exam-point-title"><i data-lucide="calendar" class="icon-xs"></i> 8. Multi-Phase Preparation Roadmaps</h4>
        <div style="display: flex; flex-direction: column; gap: 0.75rem;">
          <div class="study-plan-card">
            <h5 style="margin: 0 0 0.35rem; color: var(--primary);">🗓️ 6-Month Comprehensive Mastery Plan</h5>
            <div style="font-size: 0.82rem; margin: 0; line-height: 1.5; color: var(--text-secondary);">${formatPlan(plans['6_months'])}</div>
          </div>
          <div class="study-plan-card" style="border-left-color: #f59e0b;">
            <h5 style="margin: 0 0 0.35rem; color: #d97706;">⚡ 3-Month Fast-Track Sprint</h5>
            <div style="font-size: 0.82rem; margin: 0; line-height: 1.5; color: var(--text-secondary);">${formatPlan(plans['3_months'])}</div>
          </div>
          <div class="study-plan-card" style="border-left-color: #ef4444;">
            <h5 style="margin: 0 0 0.35rem; color: #dc2626;">🔥 30-Day Final Exam Blitz</h5>
            <div style="font-size: 0.82rem; margin: 0; line-height: 1.5; color: var(--text-secondary);">${formatPlan(plans['30_days'])}</div>
          </div>
        </div>
      </div>

      <div class="exam-point-block">
        <h4 class="exam-point-title"><i data-lucide="award" class="icon-xs"></i> 9. Proven Ranker Strategies & Advice</h4>
        <ul style="padding-left: 1.25rem; font-size: 0.84rem; line-height: 1.7; color: var(--text-secondary);">
          ${tips.map(t => `<li>${escapeHtml(t)}</li>`).join('')}
        </ul>
      </div>

      <div class="exam-point-block" style="border-bottom: none;">
        <h4 class="exam-point-title" style="color: #dc2626;"><i data-lucide="alert-triangle" class="icon-xs"></i> 10. Critical Pitfalls to Avoid</h4>
        <ul style="padding-left: 1.25rem; font-size: 0.84rem; line-height: 1.7; color: var(--text-secondary);">
          ${mistakes.map(m => `<li>${escapeHtml(m)}</li>`).join('')}
        </ul>
      </div>
    `;
  }

  refreshIcons();
}

async function toggleTopicProgress(examId, topicKey, checkbox) {
  if (!currentUser) {
    alert('Please sign in to save your checklist progress across sessions.');
    checkbox.checked = !checkbox.checked;
    openAuthModal('login');
    return;
  }

  const completed = new Set(currentExamProgress?.completed_topics || []);
  if (checkbox.checked) {
    completed.add(topicKey);
  } else {
    completed.delete(topicKey);
  }

  currentExamProgress.completed_topics = Array.from(completed);

  try {
    await fetch(`/api/exam-prep/${encodeURIComponent(examId)}/progress`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ completed_topics: currentExamProgress.completed_topics })
    });
    const footerStats = document.getElementById('exam-footer-stats');
    if (footerStats) {
      footerStats.innerHTML = `<span><strong>Updated:</strong> ${completed.size} topics completed</span>`;
    }
  } catch (err) {
    console.error('Error saving topic progress:', err);
  }
}
