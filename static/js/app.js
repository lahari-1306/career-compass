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
  activeFilters: {
    examCategory: 'All',
    examSearch: '',
    defenceLevel: 'All',
    cutoffSearch: '',
    notifCategory: 'All',
    notifSearch: '',
    librarySearch: ''
  }
};

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
  initTheme();
  initLanguage();
  initTicker();
  loadAllDatasets();
  renderSavedRoadmaps();
  initCareerRadar();
  refreshIcons();

  // Close menus on outside click
  document.addEventListener('click', (e) => {
    const langBtn = document.getElementById('lang-btn');
    const langMenu = document.getElementById('lang-menu');
    if (langMenu && !langMenu.contains(e.target) && !langBtn.contains(e.target)) {
      langMenu.classList.add('hidden');
    }
    const bellBtn = document.getElementById('radar-bell-btn');
    const bellDrawer = document.getElementById('radar-alerts-drawer');
    if (bellDrawer && !bellDrawer.contains(e.target) && !bellBtn.contains(e.target)) {
      bellDrawer.classList.add('hidden');
    }
  });
});

function refreshIcons() {
  if (window.lucide) {
    window.lucide.createIcons();
  }
}

// Theme Handling
function initTheme() {
  document.documentElement.setAttribute('data-theme', AppState.theme);
  const toggleBtn = document.getElementById('theme-toggle-btn');
  if (toggleBtn) {
    toggleBtn.addEventListener('click', () => {
      AppState.theme = AppState.theme === 'light' ? 'dark' : 'light';
      document.documentElement.setAttribute('data-theme', AppState.theme);
      localStorage.setItem('cc_theme', AppState.theme);
      refreshIcons();
    });
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
  applyLanguage(langCode);
}

function applyLanguage(langCode) {
  document.documentElement.setAttribute('lang', langCode);
  const langLabel = document.getElementById('current-lang-label');
  if (langLabel) langLabel.innerText = langCode.toUpperCase();

  // Update active dropdown item
  document.querySelectorAll('#lang-menu .dropdown-item').forEach(item => {
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
});
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
      'career-paths': 'Career Paths & Qualification Roadmaps',
      'entrance-exams': 'Entrance Exams Database',
      'govt-jobs': 'Government Exams for Engineers',
      'defence': 'Defence Forces Roadmaps',
      'colleges': 'Colleges & Courses Explorer',
      'cutoffs': 'Counselling & Historical Cutoffs',
      'scholarships': 'Verified Scholarships',
      'digital-library': 'Legal Digital Library & Resources',
      'ai-guide': 'AI Career Guide',
      'notifications': 'Notification Center',
      'saved-roadmaps': 'My Saved Roadmaps',
      'official-links': 'Verified Official Portals Directory',
      'about': 'About CareerCompass'
    };
    breadcrumbTitle.innerText = readableTitles[sectionId] || sectionId;
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

// ==========================================
// 6. DATA LOADER & RENDERING
// ==========================================
async function loadAllDatasets() {
  try {
    const [paths, exams, govt, defence, colleges, cutoffs, scholarships, library, links, notifsAll] = await Promise.all([
      fetch('/api/career-paths').then(r => r.json()),
      fetch('/api/entrance-exams').then(r => r.json()),
      fetch('/api/govt-engineering-jobs').then(r => r.json()),
      fetch('/api/defence-entries').then(r => r.json()),
      fetch('/api/colleges').then(r => r.json()),
      fetch('/api/cutoffs').then(r => r.json()),
      fetch('/api/scholarships').then(r => r.json()),
      fetch('/api/digital-library').then(r => r.json()),
      fetch('/api/official-links').then(r => r.json()),
      fetch('/api/notifications/all').then(r => r.json())
    ]);

    AppState.datasets.careerPaths = paths;
    AppState.datasets.entranceExams = exams;
    AppState.datasets.govtJobs = govt;
    AppState.datasets.defenceEntries = defence;
    AppState.datasets.colleges = colleges;
    AppState.datasets.cutoffs = cutoffs.cutoffs_reference || [];
    AppState.datasets.scholarships = scholarships;
    AppState.datasets.digitalLibrary = library;
    AppState.datasets.officialLinks = links;
    AppState.datasets.allNotifications = notifsAll.notifications || [];

    // Render Initial Views
    renderCareerPaths('10th');
    renderEntranceExams();
    renderGovtEngineering();
    renderDefenceEntries();
    renderColleges();
    renderCutoffs();
    renderScholarships();
    renderDigitalLibrary();
    renderOfficialLinks();
    renderNotificationsCenter();

    // Check AI Engine
    checkAIEngine();
    refreshIcons();
  } catch (err) {
    console.error('Data loading error:', err);
  }
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
    html += `
      <div class="card">
        <div class="card-header-row">
          <h4 class="card-title">${escapeHtml(item.name || item.category || item.title || 'Pathway')}</h4>
          ${item.duration ? `<span class="badge badge-info">${escapeHtml(item.duration)}</span>` : ''}
        </div>
        ${item.eligibility ? `<div class="card-org">${t("career.eligibility", "Eligibility")}: ${escapeHtml(item.eligibility)}</div>` : ''}
        <div class="card-body">
          ${item.future_prospects ? `<p><strong>${t("career.prospects", "Prospects")}:</strong> ${escapeHtml(item.future_prospects)}</p>` : ''}
          ${item.details ? `<p>${escapeHtml(item.details)}</p>` : ''}
          ${item.sub_branches ? `
            <div style="margin-top: 0.75rem;">
              <strong>${t("career.streams_label", "Streams / Specializations")}:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${item.sub_branches.map(sb => `<li><strong>${escapeHtml(sb.name)}:</strong> ${escapeHtml(sb.future_prospects || '')}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.roles ? `
            <div style="margin-top: 0.75rem;">
              <strong>${t("career.roles_label", "Key Job Roles")}:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${item.roles.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.entrance_exams ? `
            <div class="card-meta-list" style="margin-top: 0.75rem;">
              <span class="meta-label">${t("career.exams_label", "Associated Entrance Exams")}:</span>
              <strong>${Array.isArray(item.entrance_exams) ? item.entrance_exams.join(', ') : item.entrance_exams}</strong>
            </div>
          ` : ''}
        </div>
        <div class="card-footer">
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
      </div>
      <div class="card-footer">
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
    qualification: document.getElementById('prof-qual')?.value || '',
    branch: document.getElementById('prof-stream')?.value || '',
    score: document.getElementById('prof-score')?.value || '',
    age: document.getElementById('prof-age')?.value || '',
    state: document.getElementById('prof-state')?.value || '',
    preference: document.getElementById('prof-pref')?.value || '',
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

    if (result.mode === 'gemini_ai' && result.reply) {
      messagesContainer.innerHTML += `
        <div class="chat-bubble bot-bubble">
          <div class="bubble-header">
            <span class="bubble-sender">AI Career Guide (${result.provider})</span>
            <span class="bubble-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
          </div>
          <div class="bubble-body">${formatMarkdown(result.reply)}</div>
        </div>
      `;
    } else if (result.data) {
      // Structured rule-based roadmap
      const d = result.data;
      const r = d.roadmap || {};
      messagesContainer.innerHTML += `
        <div class="chat-bubble bot-bubble">
          <div class="bubble-header">
            <span class="bubble-sender">${result.provider}</span>
            <span class="bubble-time">${new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}</span>
          </div>
          <div class="bubble-body">
            <h4 style="font-size: 1rem; font-weight: 800; color: var(--primary); margin-bottom: 0.4rem;">${escapeHtml(d.title)}</h4>
            <p style="margin-bottom: 0.75rem;">${escapeHtml(d.summary)}</p>
            <div style="background: var(--bg-surface); padding: 0.75rem; border-radius: var(--radius-md); border: 1px solid var(--border-color); font-size: 0.85rem;">
              <p><strong>Suitable Pathways:</strong></p>
              <ul style="padding-left: 1.25rem; margin-top: 0.25rem;">
                ${(r.suitable_options || []).map(opt => `<li>${escapeHtml(opt)}</li>`).join('')}
              </ul>
              <p style="margin-top: 0.5rem;"><strong>Recommended Exams:</strong> ${(r.entrance_exams || []).join(', ')}</p>
              <p style="margin-top: 0.5rem;"><strong>Expected Career Outcome:</strong> ${escapeHtml(r.career_outcome || r.career || '')}</p>
            </div>
            <p class="disclaimer-mini" style="margin-top: 0.5rem;">${escapeHtml(d.disclaimer || '')}</p>
          </div>
        </div>
      `;
      // Also update full roadmap visualizer
      renderStructuredRoadmap(d);
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
    qualification: document.getElementById('prof-qual').value,
    branch: document.getElementById('prof-stream').value,
    score: document.getElementById('prof-score').value,
    age: document.getElementById('prof-age').value,
    state: document.getElementById('prof-state').value,
    preference: document.getElementById('prof-pref').value,
    goal: document.getElementById('prof-goal').value
  };

  const query = `Create a complete step-by-step career roadmap for a student with qualification ${profile.qualification}, branch ${profile.branch}, score ${profile.score}, age ${profile.age}, state ${profile.state}, preference for ${profile.preference}, and dream goal: ${profile.goal}.`;

  const container = document.getElementById('ai-roadmap-result');
  container.classList.remove('hidden');
  container.innerHTML = `
    <div class="loading-state">
      <div class="spinner"></div>
      <p>Generating personalized CareerCompass roadmap for <strong>${escapeHtml(profile.goal)}</strong>...</p>
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
      // Formatted text response
      container.innerHTML = `
        <div class="roadmap-header">
          <div>
            <h3 class="roadmap-title">Personalized Roadmap: ${escapeHtml(profile.goal)}</h3>
            <p style="color: var(--text-muted); font-size: 0.85rem;">Generated by ${data.provider}</p>
          </div>
          <button class="btn btn-secondary" onclick="saveCustomGoal('${escapeHtml(profile.goal)}', 'Active')">Save Roadmap</button>
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

    <!-- 8-Stage Milestone Progression Flow -->
    <div class="roadmap-flow">
      <div class="roadmap-step">
        <div class="step-label">Step 1: Current Position</div>
        <div class="step-content"><strong>${escapeHtml(r.current_position || 'Current Stage')}</strong></div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">Step 2: Suitable Education Options</div>
        <div class="step-content">
          <ul>
            ${(r.suitable_options || []).map(opt => `<li>${escapeHtml(opt)}</li>`).join('')}
          </ul>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">Step 3: Recommended Entrance Exams</div>
        <div class="step-content">
          <strong>${(r.entrance_exams || []).join(' | ')}</strong>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">Step 4: Target Courses & Degrees</div>
        <div class="step-content">
          ${(Array.isArray(r.courses) ? r.courses.join(', ') : r.courses) || 'Domain degree programs'}
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">Step 5: Target Colleges & Academies</div>
        <div class="step-content">
          ${(Array.isArray(r.colleges) ? r.colleges.join(', ') : r.colleges) || 'National & State Institutes'}
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">Step 6: High-Demand Skills to Master</div>
        <div class="step-content">
          <ul>
            ${(r.skills_required || r.skills || []).map(sk => `<li>${escapeHtml(sk)}</li>`).join('')}
          </ul>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">Step 7: Career Milestone Outcome</div>
        <div class="step-content">
          <strong style="color: var(--primary); font-size: 1.05rem;">${escapeHtml(r.career_outcome || r.career || '')}</strong>
        </div>
      </div>

      <div class="roadmap-step">
        <div class="step-label">Step 8: Actionable Immediate Next Steps</div>
        <div class="step-content">
          <ol style="padding-left: 1.25rem;">
            ${(r.next_steps || []).map(ns => `<li>${escapeHtml(ns)}</li>`).join('')}
          </ol>
        </div>
      </div>
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
  state: 'Andhra Pradesh',
  completion_year: '2026',
  category: 'General',
  interests: ['Higher Studies / M.Tech', 'PSU / Govt Jobs', 'Scholarships']
};

function getStoredRadarProfile() {
  const stored = localStorage.getItem('cc_radar_profile');
  if (stored) {
    try {
      return JSON.parse(stored);
    } catch (e) {
      return DEFAULT_RADAR_PROFILE;
    }
  }
  return DEFAULT_RADAR_PROFILE;
}

function setStoredRadarProfile(profile) {
  localStorage.setItem('cc_radar_profile', JSON.stringify(profile));
}

function initCareerRadar() {
  const profile = getStoredRadarProfile();
  updateRadarProfileChip(profile);
  refreshRadarMatches();
  loadRadarAlerts();
}

function updateRadarProfileChip(profile) {
  const chip = document.getElementById('radar-profile-chip');
  if (chip) {
    chip.textContent = `${profile.qualification} (${profile.stream_or_branch || 'General'}) • ${profile.state || 'All India'}`;
  }
}

function openRadarProfileModal() {
  const profile = getStoredRadarProfile();
  const qualSelect = document.getElementById('radar-input-qual');
  const branchInput = document.getElementById('radar-input-branch');
  const stateSelect = document.getElementById('radar-input-state');
  const yearSelect = document.getElementById('radar-input-year');

  if (qualSelect) qualSelect.value = profile.qualification || 'B.Tech';
  if (branchInput) branchInput.value = profile.stream_or_branch || 'CSE';
  if (stateSelect) stateSelect.value = profile.state || 'Andhra Pradesh';
  if (yearSelect) yearSelect.value = profile.completion_year || '2026';

  // Check interest checkboxes
  const interestBoxes = document.querySelectorAll('input[name="radar-interest"]');
  const userInterests = profile.interests || [];
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
  const qual = document.getElementById('radar-input-qual').value;
  const branchInput = document.getElementById('radar-input-branch');
  if (!branchInput) return;

  if (qual === '10th') {
    branchInput.value = 'General';
  } else if (qual === 'Intermediate') {
    branchInput.value = 'MPC';
  } else if (qual === 'Diploma') {
    branchInput.value = 'CSE';
  } else if (qual === 'B.Tech') {
    branchInput.value = 'CSE';
  } else if (qual === 'Degree') {
    branchInput.value = 'B.Sc Computer Science';
  }
}

async function saveRadarProfile() {
  const existing = getStoredRadarProfile();
  const qual = document.getElementById('radar-input-qual').value;
  const branch = document.getElementById('radar-input-branch').value.trim() || 'General';
  const state = document.getElementById('radar-input-state').value;
  const year = document.getElementById('radar-input-year').value;

  const selectedInterests = [];
  document.querySelectorAll('input[name="radar-interest"]:checked').forEach(box => {
    selectedInterests.push(box.value);
  });

  const updatedProfile = {
    ...existing,
    qualification: qual,
    stream_or_branch: branch,
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

  container.innerHTML = matches.map((m, idx) => {
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
          <a href="${escapeHtml(m.official_source)}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm w-full" style="display: inline-flex; justify-content: center; align-items: center; gap: 4px;">
            <i data-lucide="external-link" class="icon-xs"></i> ${t("common.official_portal", "Official Portal")}
          </a>
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
  if (!profile || !profile.profile_id) return;

  try {
    const res = await fetch(`/api/radar/alerts?id=${profile.profile_id}`);
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
  if (!profile || !profile.profile_id) return;

  try {
    await fetch('/api/radar/mark-read', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ profile_id: profile.profile_id })
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
