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
  currentLang: 'en',
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
// 2. MULTI-LANGUAGE TRANSLATIONS DICTIONARY
// ==========================================
const i18n = {
  en: {
    ticker_live: "LIVE UPDATES",
    view_all: "All",
    nav_home: "Home",
    nav_career_paths: "Career Paths",
    nav_exams: "Entrance Exams",
    nav_govt_jobs: "Govt Jobs",
    nav_defence: "Defence",
    nav_ai_guide: "AI Career Guide",
    menu: "Menu",
    all_sections: "All CareerCompass Portals",
    back: "← Back",
    hero_badge: "INTELLIGENT EDUCATION & CAREER NAVIGATION FOR INDIA",
    hero_headline: '"Your career journey starts with the right direction."',
    hero_subtext: "Explore education paths, entrance exams, colleges, government careers, defence opportunities, scholarships and personalized guidance — all in one place.",
    btn_find_path: "Find My Career Path",
    btn_ask_ai: "Ask AI Career Guide",
    qual_selector_title: "What is your current qualification?",
    qual_selector_subtitle: "Select your stage to discover instant education paths, exams, and job options",
    pillars_title: "Pillars of CareerCompass",
    pillars_subtitle: "Grounded in 100% verified Indian educational portals, anti-hallucination standards, and real student outcomes."
  },
  hi: {
    ticker_live: "ताज़ा अपडेट",
    view_all: "सभी",
    nav_home: "होम",
    nav_career_paths: "करियर मार्ग",
    nav_exams: "प्रवेश परीक्षाएं",
    nav_govt_jobs: "सरकारी नौकरियां",
    nav_defence: "रक्षा सेवाएं",
    nav_ai_guide: "एआई करियर गाइड",
    menu: "मेन्यू",
    all_sections: "सभी करियर कंपास पोर्टल",
    back: "← वापस",
    hero_badge: "भारतीय छात्रों के लिए सटीक शिक्षा एवं करियर मार्गदर्शन",
    hero_headline: '"आपकी करियर यात्रा सही दिशा से शुरू होती है।"',
    hero_subtext: "शिक्षा मार्ग, प्रवेश परीक्षाएं, कॉलेज, सरकारी नौकरियां, रक्षा सेवाएं, छात्रवृत्तियां और व्यक्तिगत मार्गदर्शन — सब एक ही स्थान पर।",
    btn_find_path: "मेरा करियर मार्ग खोजें",
    btn_ask_ai: "एआई गाइड से पूछें",
    qual_selector_title: "आपकी वर्तमान योग्यता क्या है?",
    qual_selector_subtitle: "शिक्षा और नौकरी के सटीक अवसरों को जानने के लिए अपना स्तर चुनें",
    pillars_title: "करियर कंपास के मुख्य स्तंभ",
    pillars_subtitle: "100% सत्यापित सरकारी पोर्टलों और वास्तविक परीक्षा तिथियों पर आधारित।"
  },
  te: {
    ticker_live: "లైవ్ అప్‌డేట్స్",
    view_all: "అన్నీ",
    nav_home: "హోమ్",
    nav_career_paths: "కెరీర్ మార్గాలు",
    nav_exams: "ప్రవేశ పరీక్షలు",
    nav_govt_jobs: "ప్రభుత్వ ఉద్యోగాలు",
    nav_defence: "డిఫెన్స్ సేవలు",
    nav_ai_guide: "ఏఐ కెరీర్ గైడ్",
    menu: "మెనూ",
    all_sections: "అన్ని కెరీర్ కంపాస్ విభాగాలు",
    back: "← వెనుకకు",
    hero_badge: "భారతీయ విద్యార్థుల కోసం ప్రామాణిక విద్య & కెరీర్ మార్గదర్శనం",
    hero_headline: '"మీ కెరీర్ ప్రయాణం సరైన దిశానిర్దేశంతో ప్రారంభమవుతుంది."',
    hero_subtext: "విద్యా మార్గాలు, ప్రవేశ పరీక్షలు, కళాశాలలు, ప్రభుత్వ ఉద్యోగాలు, రక్షణ సేవలు, స్కాలర్‌షిప్‌లు — అన్నీ ఒకే చోట.",
    btn_find_path: "నా కెరీర్ మార్గాన్ని కనుగొనండి",
    btn_ask_ai: "ఏఐ కెరీర్ గైడ్‌ని అడగండి",
    qual_selector_title: "మీ ప్రస్తుత విద్యార్హత ఏమిటి?",
    qual_selector_subtitle: "మీ విద్యా స్థాయిని ఎంచుకుని సరైన విద్యా మరియు ఉద్యోగ మార్గాలను తెలుసుకోండి",
    pillars_title: "కెరీర్ కంపాస్ ప్రధాన విభాగాలు",
    pillars_subtitle: "100% ధృవీకరించబడిన అధికారిక పోర్టల్స్ ఆధారంగా రూపొందించబడింది."
  }
};

// ==========================================
// 3. INITIALIZATION
// ==========================================
document.addEventListener('DOMContentLoaded', () => {
  initTheme();
  initLanguage();
  initTicker();
  loadAllDatasets();
  renderSavedRoadmaps();
  refreshIcons();

  // Close menus on outside click
  document.addEventListener('click', (e) => {
    const langBtn = document.getElementById('lang-btn');
    const langMenu = document.getElementById('lang-menu');
    if (langMenu && !langMenu.contains(e.target) && !langBtn.contains(e.target)) {
      langMenu.classList.add('hidden');
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
  document.getElementById('current-lang-label').innerText = langCode.toUpperCase();
  document.querySelectorAll('.dropdown-item').forEach(item => {
    item.classList.toggle('active', item.innerText.toLowerCase().includes(langCode));
  });
  const langMenu = document.getElementById('lang-menu');
  if (langMenu) langMenu.classList.add('hidden');
  applyLanguage(langCode);
}

function applyLanguage(langCode) {
  const dict = i18n[langCode] || i18n.en;
  document.querySelectorAll('[data-i18n]').forEach(elem => {
    const key = elem.getAttribute('data-i18n');
    if (dict[key]) {
      elem.innerText = dict[key];
    }
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
        ${item.eligibility ? `<div class="card-org">Eligibility: ${escapeHtml(item.eligibility)}</div>` : ''}
        <div class="card-body">
          ${item.future_prospects ? `<p><strong>Prospects:</strong> ${escapeHtml(item.future_prospects)}</p>` : ''}
          ${item.details ? `<p>${escapeHtml(item.details)}</p>` : ''}
          ${item.sub_branches ? `
            <div style="margin-top: 0.75rem;">
              <strong>Streams / Specializations:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${item.sub_branches.map(sb => `<li><strong>${escapeHtml(sb.name)}:</strong> ${escapeHtml(sb.future_prospects || '')}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.roles ? `
            <div style="margin-top: 0.75rem;">
              <strong>Key Job Roles:</strong>
              <ul style="padding-left: 1.25rem; margin-top: 0.35rem;">
                ${item.roles.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${item.entrance_exams ? `
            <div class="card-meta-list" style="margin-top: 0.75rem;">
              <span class="meta-label">Associated Entrance Exams:</span>
              <strong>${Array.isArray(item.entrance_exams) ? item.entrance_exams.join(', ') : item.entrance_exams}</strong>
            </div>
          ` : ''}
        </div>
        <div class="card-footer">
          ${item.official_url ? `
            <a href="${item.official_url}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
              <i data-lucide="external-link" class="icon-xs"></i> Official Portal
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
      <div class="card-org">Conducting Body: ${escapeHtml(exam.conducting_body)}</div>
      <div class="card-body">
        <p><strong>Purpose:</strong> ${escapeHtml(exam.purpose)}</p>
        <div class="card-meta-list">
          <div class="card-meta-item"><span>Eligibility:</span> <strong>${escapeHtml(exam.eligibility)}</strong></div>
          <div class="card-meta-item"><span>Timeline:</span> <strong>${escapeHtml(exam.timeline_status)}</strong></div>
          <div class="card-meta-item"><span>Subjects:</span> <strong>${escapeHtml(Array.isArray(exam.important_subjects) ? exam.important_subjects.join(', ') : exam.important_subjects)}</strong></div>
        </div>
      </div>
      <div class="card-footer">
        <a href="${exam.official_website}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> Official Portal
        </a>
        <button class="btn btn-secondary" onclick="sendQuickPrompt('Explain ' + '${escapeHtml(exam.name)}' + ' eligibility and syllabus simply.')">
          <i data-lucide="help-circle" class="icon-xs"></i> Ask AI
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
        <span class="badge badge-warning">Govt Service</span>
      </div>
      <div class="card-org">${escapeHtml(job.organization)}</div>
      <div class="card-body">
        <p><strong>Purpose:</strong> ${escapeHtml(job.purpose)}</p>
        <div class="card-meta-list">
          <div class="card-meta-item"><span>Qualification:</span> <strong>${escapeHtml(job.qualification)}</strong></div>
          <div class="card-meta-item"><span>Eligible Branches:</span> <strong>${escapeHtml(job.branches_eligible || job.disciplines || 'Core Engineering')}</strong></div>
          <div class="card-meta-item"><span>Age Limit:</span> <strong>${escapeHtml(job.age_limit || 'Per Gazette')}</strong></div>
          <div class="card-meta-item"><span>Salary / Scale:</span> <strong style="color: var(--status-open);">${escapeHtml(job.salary_pay_scale || '7th CPC Scale')}</strong></div>
        </div>
        ${job.selection_process ? `<p style="font-size: 0.82rem; margin-top: 0.5rem;"><strong>Selection:</strong> ${escapeHtml(job.selection_process)}</p>` : ''}
      </div>
      <div class="card-footer">
        <a href="${job.official_website}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> Official Notification Portal
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
          <div class="card-meta-item"><span>Eligibility:</span> <strong>${escapeHtml(def.qualification)}</strong></div>
          <div class="card-meta-item"><span>Age Limit:</span> <strong>${escapeHtml(def.age_limit)}</strong></div>
          <div class="card-meta-item"><span>Gender / Marital:</span> <strong>${escapeHtml(def.gender_marital || 'Unmarried')}</strong></div>
          <div class="card-meta-item"><span>Rank / Pay:</span> <strong style="color: var(--status-open);">${escapeHtml(def.rank_on_commission || 'Officer Cadre')} (${escapeHtml(def.pay_scale || 'Level 10')})</strong></div>
        </div>
        ${def.physical_standards ? `<p style="font-size: 0.82rem; margin-top: 0.5rem;"><strong>Physical Standards:</strong> ${escapeHtml(def.physical_standards)}</p>` : ''}
        ${def.selection_stages ? `
          <div style="margin-top: 0.5rem;">
            <strong style="font-size: 0.82rem;">Selection Stages:</strong>
            <ul style="padding-left: 1.25rem; font-size: 0.8rem; margin-top: 0.25rem;">
              ${(Array.isArray(def.selection_stages) ? def.selection_stages : [def.selection_stages]).map(s => `<li>${escapeHtml(s)}</li>`).join('')}
            </ul>
          </div>
        ` : ''}
      </div>
      <div class="card-footer">
        <a href="${def.official_website}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> Official Defence Portal
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
          <div class="card-meta-item"><span>Entrance Exams:</span> <strong>${escapeHtml(c.accepted_exams?.join(', ') || 'National/State')}</strong></div>
          ${c.fees_per_year ? `<div class="card-meta-item"><span>Fees Structure:</span> <strong>${escapeHtml(c.fees_per_year)}</strong></div>` : ''}
        </div>
        <p style="font-size: 0.82rem;"><strong>Popular Branches:</strong> ${escapeHtml(c.popular_branches?.join(', ') || 'Engineering & Science')}</p>
      </div>
      <div class="card-footer">
        <a href="${c.official_website}" target="_blank" rel="noopener noreferrer" class="btn btn-secondary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> Official Website
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
        <span class="badge badge-danger">Verified Scheme</span>
      </div>
      <div class="card-org">Provider: ${escapeHtml(sch.provider)}</div>
      <div class="card-body">
        <div class="card-meta-list">
          <div class="card-meta-item"><span>Award Amount:</span> <strong style="color: var(--status-open);">${escapeHtml(sch.amount)}</strong></div>
          <div class="card-meta-item"><span>Target Qualification:</span> <strong>${escapeHtml(sch.target_qualification)}</strong></div>
          <div class="card-meta-item"><span>Income Ceiling:</span> <strong>${escapeHtml(sch.income_criteria)}</strong></div>
          ${sch.application_window ? `<div class="card-meta-item"><span>Application Window:</span> <strong>${escapeHtml(sch.application_window)}</strong></div>` : ''}
        </div>
        <p style="font-size: 0.82rem;"><strong>Eligibility:</strong> ${escapeHtml(sch.eligibility)}</p>
      </div>
      <div class="card-footer">
        <a href="${sch.official_url}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
          <i data-lucide="external-link" class="icon-xs"></i> Apply on Official Portal
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
          <i data-lucide="external-link" class="icon-xs"></i> Access Resource
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
            <div class="card-meta-item"><span>Eligibility:</span> <strong>${escapeHtml(notif.eligibility_summary)}</strong></div>
            <div class="card-meta-item"><span>Exam / Event Date:</span> <strong>${escapeHtml(notif.exam_date)}</strong></div>
            <div class="card-meta-item"><span>Last Verified:</span> <strong>${new Date(notif.last_verified_at).toLocaleDateString()}</strong></div>
          </div>
        </div>
        <div class="card-footer">
          <button class="btn btn-secondary" onclick="openNotifModal('${notif.id}')">View Details</button>
          <a href="${notif.official_source}" target="_blank" rel="noopener noreferrer" class="btn btn-primary" style="padding: 0.45rem 0.85rem; font-size: 0.8rem;">
            <i data-lucide="external-link" class="icon-xs"></i> Official Source
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
      body: JSON.stringify({ message: message, profile: currentProfile })
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
      body: JSON.stringify({ message: query, profile: profile })
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
