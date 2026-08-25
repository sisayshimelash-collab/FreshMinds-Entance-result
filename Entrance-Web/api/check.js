/**
 * Vercel Serverless Function: /api/check
 * 
 * Proxies student result queries to EAES API without CORS restrictions.
 * Zero external dependencies (uses Node.js 18+ built-in fetch & crypto).
 */

const crypto = require('crypto');

const EAES_API_BASE = process.env.EAES_API_BASE || 'https://api.eaes.et';
const BOT_ENDPOINT = `${EAES_API_BASE}/api/v1/results/bot`;
const WEB_ENDPOINT = `${EAES_API_BASE}/api/v1/results/web`;
const SESSION_ENDPOINT = `${EAES_API_BASE}/api/v1/session/key`;

// ── In-Memory Stampede Cache (Vercel Lambda Container Reuse) ─────────────────
let globalNotReleasedUntil = 0;
let globalNotReleasedMsg = '';
const resultCache = new Map();

function sanitizeAdmissionNumber(raw) {
  if (!raw || typeof raw !== 'string') return null;
  const cleaned = raw.replace(/[\s\-_/]+/g, '').trim();
  if (/^\d{3,12}$/.test(cleaned)) return cleaned;
  return null;
}

function sanitizeFirstName(raw) {
  if (!raw || typeof raw !== 'string') return null;
  const trimmed = raw.trim();
  if (!trimmed) return null;
  const tokens = trimmed.split(/[\s\-_,.]+/);
  const first = tokens[0] || '';
  if (!/^[\u1200-\u137Fa-zA-Z']+$/.test(first)) return null;
  if (first.length < 2 || first.length > 40) return null;
  if (/^[\x00-\x7F]+$/.test(first)) {
    return first.charAt(0).toUpperCase() + first.slice(1);
  }
  return first;
}

function computeHmacSha256(secret, message) {
  return crypto.createHmac('sha256', secret).update(message).digest('hex');
}

module.exports = async function handler(req, res) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Credentials', true);
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  // Extract parameters from Query or POST body
  const body = req.body || {};
  const query = req.query || {};
  const rawAdmission = body.admission_no || query.admission_no || body.admissionNo;
  const rawFirstName = body.first_name || query.first_name || body.firstName;

  const admissionNo = sanitizeAdmissionNumber(rawAdmission);
  const firstName = sanitizeFirstName(rawFirstName);

  if (!admissionNo || !firstName) {
    return res.status(400).json({
      status: 'validation_error',
      message: 'Please provide a valid numeric admission number and first name.',
    });
  }

  const cacheKey = `res:${admissionNo}:${firstName.toLowerCase()}`;

  // 1. Check local container LRU cache
  if (resultCache.has(cacheKey)) {
    return res.status(200).json({
      ...resultCache.get(cacheKey),
      from_cache: true,
    });
  }

  // 2. Check 30s global stampede shield
  const now = Date.now();
  if (now < globalNotReleasedUntil) {
    return res.status(200).json({
      status: 'not_released',
      message: globalNotReleasedMsg || 'Results for 2018 E.C. have not been released yet.',
      from_cache: true,
    });
  }

  try {
    // 3. Primary Engine: Call /api/v1/results/bot
    const botUrl = `${BOT_ENDPOINT}?admission_no=${encodeURIComponent(admissionNo)}&first_name=${encodeURIComponent(firstName)}`;
    const eaesResp = await fetch(botUrl, {
      method: 'GET',
      headers: {
        'User-Agent': 'FreshMindsResultWeb/1.0 (+https://freshmindsacademy.com)',
        'Accept': 'application/json',
      },
    });

    // 200 OK: Results are live and found
    if (eaesResp.status === 200) {
      const data = await eaesResp.json();
      const studentInfo = data.studentInfo || {};
      const rawResults = data.results || [];

      const parsed = {
        status: 'success',
        student: {
          full_name: studentInfo.FullName || `${firstName}`,
          admission_no: studentInfo.Admission_No || admissionNo,
          school: studentInfo.School || null,
          stream: studentInfo.Stream || null,
          sex: studentInfo.Sex || null,
          age: studentInfo.Age || null,
        },
        results: rawResults.map(r => ({
          subject: r.Subject || 'Subject',
          result: r.Result || '-',
        })),
      };

      // Cache successful result for 10 minutes in container memory
      resultCache.set(cacheKey, parsed);
      if (resultCache.size > 1000) {
        const firstKey = resultCache.keys().next().value;
        resultCache.delete(firstKey);
      }

      return res.status(200).json(parsed);
    }

    // 423 Locked: Results not yet released
    if (eaesResp.status === 423) {
      const errData = await eaesResp.json().catch(() => ({}));
      const detail = errData.detail || 'The 2018 result is not released.';
      globalNotReleasedUntil = Date.now() + 30000; // 30s shield
      globalNotReleasedMsg = detail;

      return res.status(200).json({
        status: 'not_released',
        message: detail,
      });
    }

    // 404: Student not found
    if (eaesResp.status === 404) {
      return res.status(200).json({
        status: 'not_found',
        message: `No student record found for admission number ${admissionNo} and name ${firstName}.`,
      });
    }

    // Fallback error
    return res.status(200).json({
      status: 'service_error',
      message: 'The EAES result server returned an unexpected response. Please retry in a few moments.',
    });

  } catch (error) {
    console.error('EAES Proxy Error:', error);
    return res.status(500).json({
      status: 'service_error',
      message: 'Could not connect to EAES result server. Please try again.',
    });
  }
};
