/**
 * FreshMinds Result Portal — Client Application Logic
 * 
 * Supports:
 * - Bilingual switching (Amharic / English)
 * - Clean async result fetching via backend proxy
 * - Dynamic student scorecard rendering and printing
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
    hint_name: 'በእንግሊዝኛ ፊደል ብቻ (English only, e.g. Abebe)',
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
    btn_try_again: '🔄 ደግመው ይሞክሩ (Try Again)',
    promo_badge: 'Freshman Prep 2018 E.C.',
    promo_title: 'ለዩኒቨርሲቲ Freshman ህይወትህ/ሽ ተዘጋጅተሃል/ሻል?',
    promo_desc: 'ነፃ የ Freshman ኮርሶች፣ የትምህርት ማቴሪያሎች፣ እና የዩኒቨርሲቲ ምደባ መረጃዎችን በ FreshMinds Academy ያግኙ።',
    pass_title: 'እንኳን ደስ አለዎት! ፈተናውን አልፈዋል!',
    pass_desc: 'ውጤትዎ 50% እና ከዚያ በላይ ነው! ለዩኒቨርሲቲ ምደባ ብቁ ነዎት።',
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
    hint_name: 'In English letters only (e.g. Abebe)',
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
    pass_title: 'Congratulations! You Passed!',
    pass_desc: 'You scored 50% or above and qualify for University Placement.',
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

  if (lang === 'en') {
    admissionInput.placeholder = 'e.g. 347484';
    nameInput.placeholder = 'e.g. Abebe';
  } else {
    admissionInput.placeholder = 'ምሳሌ 347484';
    nameInput.placeholder = 'ምሳሌ Abebe';
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

// ── Web Result Fetcher ───────────────────────────────────────────────────────
async function fetchResult(admissionNo, firstName) {
  showView('loading');

  try {
    const response = await fetch('/api/check', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        admission_no: admissionNo,
        first_name: firstName,
      }),
    });

    let data;
    if (response.ok) {
      data = await response.json();
    } else if (response.status === 423) {
      data = { status: 'not_released' };
    } else if (response.status === 404) {
      data = { status: 'not_found' };
    } else {
      data = await response.json().catch(() => ({ status: 'service_error' }));
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

const passCelebrationBanner = document.getElementById('passCelebrationBanner');
const downloadStoryBtn = document.getElementById('downloadStoryBtn');

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

  // Calculate or extract Average & Total
  let avgVal = null;
  let totalVal = null;

  scoresTableBody.innerHTML = '';
  results.forEach(r => {
    const sName = r.subject.trim();
    if (sName.toLowerCase() === 'average') {
      avgVal = parseFloat(r.result);
    } else if (sName.toLowerCase() === 'total') {
      totalVal = r.result;
    }

    const row = document.createElement('tr');
    row.innerHTML = `
      <td><strong>${escapeHtml(r.subject)}</strong></td>
      <td class="text-right"><span class="score-value">${escapeHtml(r.result)}</span></td>
    `;
    scoresTableBody.appendChild(row);
  });

  // Fallback calculate average if not explicitly given
  if (avgVal === null) {
    const numericSubs = results.filter(r => !['total', 'average'].includes(r.subject.toLowerCase()) && !isNaN(parseFloat(r.result)));
    if (numericSubs.length > 0) {
      const sum = numericSubs.reduce((acc, x) => acc + parseFloat(x.result), 0);
      avgVal = sum / numericSubs.length;
    }
  }

  // ── Show Story Card button & Celebration for 50%+ ──────────────────────────
  downloadStoryBtn.classList.remove('hidden');
  downloadStoryBtn.onclick = () => {
    generateStoryCard(student, results, avgVal || 0, totalVal);
  };

  if (avgVal !== null && avgVal >= 50.0) {
    passCelebrationBanner.classList.remove('hidden');
  } else {
    passCelebrationBanner.classList.add('hidden');
  }
}

// ── HTML5 Canvas Mobile Story Card Generator (1080 x 1920) ───────────────────
function generateStoryCard(student, results, avgVal, totalVal) {
  const canvas = document.createElement('canvas');
  canvas.width = 1080;
  canvas.height = 1920;
  const ctx = canvas.getContext('2d');

  // 1. Background Gradient
  const bgGrad = ctx.createLinearGradient(0, 0, 1080, 1920);
  bgGrad.addColorStop(0, '#0a0d1a');
  bgGrad.addColorStop(0.35, '#17112e');
  bgGrad.addColorStop(0.7, '#0e172e');
  bgGrad.addColorStop(1, '#080a14');
  ctx.fillStyle = bgGrad;
  ctx.fillRect(0, 0, 1080, 1920);

  // 2. Glow Accents
  ctx.save();
  const glow1 = ctx.createRadialGradient(200, 200, 0, 200, 200, 450);
  glow1.addColorStop(0, 'rgba(139, 92, 246, 0.45)');
  glow1.addColorStop(1, 'rgba(139, 92, 246, 0)');
  ctx.fillStyle = glow1;
  ctx.beginPath();
  ctx.arc(200, 200, 450, 0, Math.PI * 2);
  ctx.fill();

  const glow2 = ctx.createRadialGradient(900, 1600, 0, 900, 1600, 500);
  glow2.addColorStop(0, 'rgba(6, 182, 212, 0.4)');
  glow2.addColorStop(1, 'rgba(6, 182, 212, 0)');
  ctx.fillStyle = glow2;
  ctx.beginPath();
  ctx.arc(900, 1600, 500, 0, Math.PI * 2);
  ctx.fill();
  ctx.restore();

  // 3. Sparkle Stars
  ctx.fillStyle = '#ffffff';
  for (let i = 0; i < 40; i++) {
    const sx = Math.sin(i * 99) * 500 + 540;
    const sy = Math.cos(i * 77) * 900 + 960;
    const size = (i % 3) + 1.5;
    ctx.globalAlpha = 0.3 + (i % 5) * 0.15;
    ctx.beginPath();
    ctx.arc(sx, sy, size, 0, Math.PI * 2);
    ctx.fill();
  }
  ctx.globalAlpha = 1.0;

  // 4. Header Branding (FreshMinds Academy)
  ctx.textAlign = 'center';
  
  // Brand Pill
  ctx.fillStyle = 'rgba(139, 92, 246, 0.2)';
  roundRect(ctx, 340, 120, 400, 55, 28);
  ctx.fill();
  ctx.strokeStyle = 'rgba(139, 92, 246, 0.6)';
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.font = 'bold 24px Inter, sans-serif';
  ctx.fillStyle = '#c4b5fd';
  ctx.fillText('🎓 FRESHMINDS ACADEMY', 540, 156);

  ctx.font = 'bold 44px Outfit, Inter, sans-serif';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('2018 E.C. ENTRANCE RESULT', 540, 230);

  // 5. Celebration Gold / Emerald Badge (or Scorecard Badge)
  const isPassed = avgVal >= 50.0;
  const badgeGrad = ctx.createLinearGradient(190, 280, 890, 370);
  if (isPassed) {
    badgeGrad.addColorStop(0, '#f59e0b');
    badgeGrad.addColorStop(0.5, '#10b981');
    badgeGrad.addColorStop(1, '#06b6d4');
  } else {
    badgeGrad.addColorStop(0, '#6366f1');
    badgeGrad.addColorStop(0.5, '#8b5cf6');
    badgeGrad.addColorStop(1, '#06b6d4');
  }
  ctx.fillStyle = badgeGrad;
  roundRect(ctx, 190, 280, 700, 80, 40);
  ctx.fill();

  ctx.font = 'bold 34px Outfit, Inter, sans-serif';
  ctx.fillStyle = '#ffffff';
  ctx.fillText(isPassed ? '🌟 UNIVERSITY ENTRANCE PASSED 🌟' : '🎓 OFFICIAL 2018 ESSLCE RESULT 🎓', 540, 334);

  // 6. Student Info Glass Card
  ctx.fillStyle = 'rgba(25, 33, 64, 0.75)';
  roundRect(ctx, 90, 400, 900, 1280, 36);
  ctx.fill();
  ctx.strokeStyle = 'rgba(255, 255, 255, 0.15)';
  ctx.lineWidth = 2;
  ctx.stroke();

  // Student Avatar
  ctx.font = '70px Inter, sans-serif';
  ctx.fillText('🎓', 540, 490);

  // Student Full Name
  ctx.font = 'bold 46px Outfit, Inter, sans-serif';
  ctx.fillStyle = '#ffffff';
  ctx.fillText(student.full_name.toUpperCase(), 540, 560);

  // Admission Number Pill
  ctx.fillStyle = 'rgba(255, 255, 255, 0.08)';
  roundRect(ctx, 360, 595, 360, 48, 24);
  ctx.fill();
  ctx.font = '500 24px Inter, sans-serif';
  ctx.fillStyle = '#94a3b8';
  ctx.fillText(`Admission No: ${student.admission_no}`, 540, 628);

  // 7. Highlights Boxes (Average & Total)
  // Left Box - Average
  const box1Grad = ctx.createLinearGradient(130, 680, 510, 850);
  box1Grad.addColorStop(0, 'rgba(139, 92, 246, 0.25)');
  box1Grad.addColorStop(1, 'rgba(99, 102, 241, 0.1)');
  ctx.fillStyle = box1Grad;
  roundRect(ctx, 130, 680, 390, 170, 24);
  ctx.fill();
  ctx.strokeStyle = 'rgba(139, 92, 246, 0.5)';
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.font = '600 22px Inter, sans-serif';
  ctx.fillStyle = '#c4b5fd';
  ctx.fillText('AVERAGE SCORE', 325, 725);

  ctx.font = 'bold 64px Outfit, Inter, sans-serif';
  ctx.fillStyle = '#38bdf8';
  ctx.fillText(`${avgVal.toFixed(2)}%`, 325, 805);

  // Right Box - Total Score
  const box2Grad = ctx.createLinearGradient(570, 680, 950, 850);
  box2Grad.addColorStop(0, 'rgba(16, 185, 129, 0.25)');
  box2Grad.addColorStop(1, 'rgba(6, 182, 212, 0.1)');
  ctx.fillStyle = box2Grad;
  roundRect(ctx, 570, 680, 380, 170, 24);
  ctx.fill();
  ctx.strokeStyle = 'rgba(16, 185, 129, 0.5)';
  ctx.lineWidth = 2;
  ctx.stroke();

  ctx.font = '600 22px Inter, sans-serif';
  ctx.fillStyle = '#6ee7b7';
  ctx.fillText('TOTAL SCORE', 760, 725);

  ctx.font = 'bold 64px Outfit, Inter, sans-serif';
  ctx.fillStyle = '#34d399';
  ctx.fillText(totalVal || `${(avgVal * 6).toFixed(0)}`, 760, 805);

  // 8. Subject Breakdown Grid
  const subjectList = results.filter(r => !['total', 'average'].includes(r.subject.toLowerCase()));
  const startY = 900;
  const rowHeight = 70;

  ctx.textAlign = 'left';
  subjectList.forEach((sub, idx) => {
    if (idx >= 8) return;
    const y = startY + idx * rowHeight;

    ctx.fillStyle = 'rgba(255, 255, 255, 0.04)';
    roundRect(ctx, 130, y, 820, 56, 14);
    ctx.fill();
    ctx.strokeStyle = 'rgba(255, 255, 255, 0.08)';
    ctx.lineWidth = 1;
    ctx.stroke();

    ctx.font = '600 26px Inter, sans-serif';
    ctx.fillStyle = '#e2e8f0';
    ctx.fillText(`📖  ${sub.subject}`, 160, y + 38);

    ctx.textAlign = 'right';
    ctx.font = 'bold 30px Outfit, Inter, sans-serif';
    ctx.fillStyle = '#38bdf8';
    ctx.fillText(sub.result, 920, y + 38);
    ctx.textAlign = 'left';
  });

  // 9. Footer CTA / Watermark
  ctx.textAlign = 'center';
  ctx.font = 'bold 28px Outfit, Inter, sans-serif';
  ctx.fillStyle = '#ffffff';
  ctx.fillText('🚀 Ready for University Freshman Year?', 540, 1530);

  ctx.font = '500 24px Inter, sans-serif';
  ctx.fillStyle = '#94a3b8';
  ctx.fillText('Join free courses on Telegram: @freshminds_academy', 540, 1575);

  ctx.fillStyle = 'rgba(34, 158, 217, 0.2)';
  roundRect(ctx, 300, 1610, 480, 50, 25);
  ctx.fill();
  ctx.font = 'bold 22px Inter, sans-serif';
  ctx.fillStyle = '#38bdf8';
  ctx.fillText('📱 FreshMinds Mobile App Coming Soon', 540, 1642);

  // 10. Trigger Instant Download
  const link = document.createElement('a');
  link.download = `FreshMinds_Result_${student.admission_no || 'Scorecard'}.png`;
  link.href = canvas.toDataURL('image/png');
  link.click();
}

// Canvas Helper: Rounded Rectangle
function roundRect(ctx, x, y, width, height, radius) {
  ctx.beginPath();
  ctx.moveTo(x + radius, y);
  ctx.lineTo(x + width - radius, y);
  ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
  ctx.lineTo(x + width, y + height - radius);
  ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
  ctx.lineTo(x + radius, y + height);
  ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
  ctx.lineTo(x, y + radius);
  ctx.quadraticCurveTo(x, y, x + radius, y);
  ctx.closePath();
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

