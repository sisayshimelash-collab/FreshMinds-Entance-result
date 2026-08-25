/**
 * FreshMinds Result Portal — Client Application Logic
 * Supports bilingual switching (Amharic / English), async result fetching,
 * dynamic scorecard generation, and printing.
 */

// ── Translations Dictionary ──────────────────────────────────────────────────
const translations = {
  am: {
    lang_btn: '🇬🇧 English',
    join_channel_btn: 'ቻናል ተቀላቀል',
    badge_text: 'የ 2018 ዓ.ም የፈተና ውጤት መመልከቻ',
    hero_heading: 'የ 2018 ዓ.ም የመግቢያ ፈተና ውጤትህን/ሽን ፈትሽ',
    hero_subheading: 'የምዝገባ ቁጥርህን/ሽን እና የመጀመሪያ ስምህን/ሽን በማስገባት ፈጣን ውጤት ተመልከት',
    label_admission: 'የምዝገባ ቁጥር (Admission No)',
    hint_admission: 'ቁጥሮችን ብቻ ያስገቡ (ለምሳሌ 347484)',
    label_name: 'የመጀመሪያ ስም (First Name)',
    hint_name: 'በእንግሊዝኛ ወይም በአማርኛ ፊደል',
    btn_check: 'ውጤቴን ፈልግ (Check Result)',
    loading_title: 'ውጤትህን/ሽን በማዘጋጀት ላይ ነን...',
    loading_desc: 'ከ EAES ሰርቨር ጋር እየተገናኘን ነው፣ እባክዎ ጥቂት ሴኮንዶች ይጠብቁ።',
    official_result: 'Official EAES Result',
    btn_print: 'አትም (Print)',
    th_subject: 'የትምህርት አይነት (Subject)',
    th_score: 'ውጤት (Score)',
    btn_check_another: '🔄 ሌላ ውጤት ፈልግ',
    btn_join_telegram: 'የ Freshman ትምህርቶችን ተቀላቀል',
    notice_not_released_title: 'የ 2018 ዓ.ም ውጤት ገና አልተለቀቀም!',
    notice_not_released_desc: 'የፈተና ውጤት ሲለቀቅ ወዲያውኑ በቴሌግራም ቻናላችን እናሳውቃለን። ቻናላችንን ተቀላቀሉ!',
    notice_not_found_title: 'ተማሪ አልተገኘም (Student Not Found)',
    notice_not_found_desc: 'ያስገቡት የምዝገባ ቁጥር ወይም ስም አልተገኘም። እባክዎ በትክክል መጻፉን አረጋግጠው ደግመው ይሞክሩ።',
    notice_error_title: 'አገልግሎቱ ለጊዜው አልመለሰም',
    notice_error_desc: 'የውጤት ሰርቨሩ በከፍተኛ መጨናነቅ ላይ ሊሆን ይችላል። እባክዎ ከጥቂት ደቂቃዎች በኋላ ደግመው ይሞክሩ።',
    btn_join_freshminds: 'Join @freshminds_academy',
    btn_try_again: '🔄 ደግመህ ፈትሽ (Try Again)',
    promo_badge: 'Freshman Prep 2018 E.C.',
    promo_title: 'ለዩኒቨርሲቲ Freshman ህይወትህ/ሽ ተዘጋጅተሃል/ሻል?',
    promo_desc: 'ነፃ የ Freshman ኮርሶች፣ የትምህርት ማቴሪያሎች፣ እና የዩኒቨርሲቲ ምደባ መረጃዎችን በ FreshMinds Academy ያግኙ።',
    feat_courses: 'ነፃ የቪዲዮ ኮርሶች',
    feat_exams: 'የፈተና ሞዴሎች',
    feat_app: 'FreshMinds App (በቅርቡ)',
  },
  en: {
    lang_btn: '🇪🇹 አማርኛ',
    join_channel_btn: 'Join Channel',
    badge_text: 'EAES 2018 E.C. Result Portal',
    hero_heading: 'Check Your 2018 E.C. Entrance Exam Result',
    hero_subheading: 'Enter your Admission Number and First Name to view your official score card',
    label_admission: 'Admission Number',
    hint_admission: 'Enter numeric digits only (e.g. 347484)',
    label_name: 'First Name',
    hint_name: 'In English or Amharic letters',
    btn_check: 'Check My Result →',
    loading_title: 'Fetching your exam result...',
    loading_desc: 'Communicating with EAES database. Please wait a moment.',
    official_result: 'Official EAES Result',
    btn_print: 'Print',
    th_subject: 'Subject',
    th_score: 'Score',
    btn_check_another: '🔄 Check Another Result',
    btn_join_telegram: 'Join Freshman Prep Channel',
    notice_not_released_title: '2018 E.C. Results Not Released Yet!',
    notice_not_released_desc: 'Results have not been officially published by EAES. We will broadcast live on our Telegram channel the moment they drop!',
    notice_not_found_title: 'Student Record Not Found',
    notice_not_found_desc: 'No student found with the provided admission number and name. Please verify your details and try again.',
    notice_error_title: 'Service Temporarily Busy',
    notice_error_desc: 'The result server is experiencing high traffic. Please try again in a few moments.',
    btn_join_freshminds: 'Join @freshminds_academy',
    btn_try_again: '🔄 Try Again',
    promo_badge: 'Freshman Prep 2018 E.C.',
    promo_title: 'Ready for Your University Freshman Journey?',
    promo_desc: 'Access free freshman courses, university exam models, and departmental preparation on FreshMinds Academy.',
    feat_courses: 'Free Video Lectures',
    feat_exams: 'Exam Model Banks',
    feat_app: 'FreshMinds Mobile App (Coming Soon)',
  }
};

let currentLang = 'am';

// ── DOM Elements ─────────────────────────────────────────────────────────────
const langToggleBtn = document.getElementById('langToggleBtn');
const langCurrent = document.getElementById('langCurrent');
const resultForm = document.getElementById('resultForm');
const admissionInput = document.getElementById('admissionInput');
const nameInput = document.getElementById('nameInput');
const submitBtn = document.getElementById('submitBtn');

const formSection = document.getElementById('formSection');
const loadingCard = document.getElementById('loadingCard');
const resultCard = document.getElementById('resultCard');
const noticeCard = document.getElementById('noticeCard');

const resFullName = document.getElementById('resFullName');
const resAdmissionNo = document.getElementById('resAdmissionNo');
const resStream = document.getElementById('resStream');
const resStreamTag = document.getElementById('resStreamTag');
const resSchool = document.getElementById('resSchool');
const resSchoolTag = document.getElementById('resSchoolTag');
const scoresTableBody = document.getElementById('scoresTableBody');

const printBtn = document.getElementById('printBtn');
const checkAnotherBtn = document.getElementById('checkAnotherBtn');
const noticeRetryBtn = document.getElementById('noticeRetryBtn');

const noticeIcon = document.getElementById('noticeIcon');
const noticeTitle = document.getElementById('noticeTitle');
const noticeDesc = document.getElementById('noticeDesc');

// ── Language Toggle Logic ────────────────────────────────────────────────────
function setLanguage(lang) {
  currentLang = lang;
  document.documentElement.lang = lang;
  const dict = translations[lang];

  langCurrent.textContent = dict.lang_btn;

  document.querySelectorAll('[data-i18n]').forEach(el => {
    const key = el.getAttribute('data-i18n');
    if (dict[key]) {
      el.textContent = dict[key];
    }
  });

  // Update input placeholders
  if (lang === 'en') {
    admissionInput.placeholder = 'e.g. 347484';
    nameInput.placeholder = 'e.g. Abebe';
  } else {
    admissionInput.placeholder = 'ምሳሌ 347484';
    nameInput.placeholder = 'ምሳሌ Abebe / አበበ';
  }
}

langToggleBtn.addEventListener('click', () => {
  setLanguage(currentLang === 'am' ? 'en' : 'am');
});

// ── Input Sanitization ───────────────────────────────────────────────────────
function cleanAdmissionNumber(str) {
  return str.replace(/[\s\-_/]+/g, '').trim();
}

function cleanFirstName(str) {
  const trimmed = str.trim();
  const tokens = trimmed.split(/[\s\-_,.]+/);
  const first = tokens[0] || '';
  if (/^[\x00-\x7F]+$/.test(first)) {
    return first.charAt(0).toUpperCase() + first.slice(1);
  }
  return first;
}

// ── UI State Helpers ─────────────────────────────────────────────────────────
function showView(viewName) {
  formSection.classList.add('hidden');
  loadingCard.classList.add('hidden');
  resultCard.classList.add('hidden');
  noticeCard.classList.add('hidden');

  if (viewName === 'form') formSection.classList.remove('hidden');
  if (viewName === 'loading') loadingCard.classList.remove('hidden');
  if (viewName === 'result') resultCard.classList.remove('hidden');
  if (viewName === 'notice') noticeCard.classList.remove('hidden');
}

// ── API Result Fetcher ───────────────────────────────────────────────────────
async function fetchResult(admissionNo, firstName) {
  showView('loading');

  try {
    // 1. Try Vercel Serverless Endpoint (/api/check)
    let response;
    try {
      response = await fetch('/api/check', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ admission_no: admissionNo, first_name: firstName }),
      });
    } catch (err) {
      // Local dev fallback if running without serverless proxy
      response = await fetch(`https://api.eaes.et/api/v1/results/bot?admission_no=${encodeURIComponent(admissionNo)}&first_name=${encodeURIComponent(firstName)}`);
    }

    // Parse response
    let data;
    if (response.ok) {
      data = await response.json();
    } else if (response.status === 423) {
      data = { status: 'not_released', message: 'Results not released yet.' };
    } else if (response.status === 404) {
      data = { status: 'not_found' };
    } else {
      data = { status: 'service_error' };
    }

    handleApiResponse(data, admissionNo, firstName);

  } catch (error) {
    console.error('Fetch error:', error);
    showNotice(
      '⚠️',
      translations[currentLang].notice_error_title,
      translations[currentLang].notice_error_desc
    );
  }
}

// ── Handle Response Types ────────────────────────────────────────────────────
function handleApiResponse(data, admissionNo, firstName) {
  const dict = translations[currentLang];

  // 1. SUCCESS: Display Result Card
  if (data.status === 'success' && data.student) {
    renderScorecard(data.student, data.results || []);
    showView('result');
    return;
  }

  // 2. NOT RELEASED YET
  if (data.status === 'not_released') {
    showNotice(
      '⏳',
      dict.notice_not_released_title,
      dict.notice_not_released_desc
    );
    return;
  }

  // 3. NOT FOUND
  if (data.status === 'not_found') {
    showNotice(
      '❌',
      dict.notice_not_found_title,
      dict.notice_not_found_desc
    );
    return;
  }

  // 4. ERROR / SERVICE DOWN
  showNotice(
    '⚠️',
    dict.notice_error_title,
    dict.notice_error_desc
  );
}

function showNotice(icon, title, desc) {
  noticeIcon.textContent = icon;
  noticeTitle.textContent = title;
  noticeDesc.textContent = desc;
  showView('notice');
}

// ── Render Scorecard ─────────────────────────────────────────────────────────
function renderScorecard(student, results) {
  resFullName.textContent = student.full_name || 'Student';
  resAdmissionNo.textContent = student.admission_no || '--';

  if (student.stream) {
    resStream.textContent = student.stream;
    resStreamTag.classList.remove('hidden');
  } else {
    resStreamTag.classList.add('hidden');
  }

  if (student.school) {
    resSchool.textContent = student.school;
    resSchoolTag.classList.remove('hidden');
  } else {
    resSchoolTag.classList.add('hidden');
  }

  // Build subject table rows
  scoresTableBody.innerHTML = '';
  results.forEach(r => {
    const row = document.createElement('tr');
    row.innerHTML = `
      <td><strong>${escapeHtml(r.subject)}</strong></td>
      <td class="text-right"><span class="score-value">${escapeHtml(r.result)}</span></td>
    `;
    scoresTableBody.appendChild(row);
  });
}

function escapeHtml(text) {
  const div = document.createElement('div');
  div.textContent = text;
  return div.innerHTML;
}

// ── Form Submission ──────────────────────────────────────────────────────────
resultForm.addEventListener('submit', (e) => {
  e.preventDefault();

  const rawAdmission = admissionInput.value;
  const rawName = nameInput.value;

  const admissionNo = cleanAdmissionNumber(rawAdmission);
  const firstName = cleanFirstName(rawName);

  if (!admissionNo || admissionNo.length < 3) {
    alert(translations[currentLang].hint_admission);
    admissionInput.focus();
    return;
  }

  if (!firstName || firstName.length < 2) {
    alert(translations[currentLang].hint_name);
    nameInput.focus();
    return;
  }

  fetchResult(admissionNo, firstName);
});

// ── Reset & Check Another ────────────────────────────────────────────────────
checkAnotherBtn.addEventListener('click', () => {
  showView('form');
  admissionInput.value = '';
  nameInput.value = '';
  admissionInput.focus();
});

noticeRetryBtn.addEventListener('click', () => {
  showView('form');
  admissionInput.focus();
});

// ── Print Scorecard ──────────────────────────────────────────────────────────
printBtn.addEventListener('click', () => {
  window.print();
});

// Initialize default language
setLanguage('am');
