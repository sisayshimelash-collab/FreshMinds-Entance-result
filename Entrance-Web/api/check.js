/**
 * Vercel Serverless Function: /api/check
 * 
 * High-performance, low-latency EAES Result Proxy:
 * - 30-second Stampede Shield for 423 Locked
 * - In-memory LRU cache for 200 OK results
 * - Native HTTPS client for maximum connection reliability
 */

const https = require('https');

const EAES_HOST = 'api.eaes.et';
const BOT_PATH = '/api/v1/results/bot';

// ── In-Memory Stampede Cache ─────────────────────────────────────────────────
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

function fetchFromEaes(pathWithQuery) {
  return new Promise((resolve, reject) => {
    const options = {
      hostname: EAES_HOST,
      port: 443,
      path: pathWithQuery,
      method: 'GET',
      headers: {
        'User-Agent': 'FreshMindsResultWeb/1.0 (+https://freshmindsacademy.com)',
        'Accept': 'application/json',
      },
      timeout: 15000,
    };

    const req = https.request(options, (res) => {
      let data = '';
      res.on('data', chunk => { data += chunk; });
      res.on('end', () => {
        resolve({
          statusCode: res.statusCode,
          headers: res.headers,
          body: data,
        });
      });
    });

    req.on('timeout', () => {
      req.destroy(new Error('Connection timeout to EAES'));
    });

    req.on('error', err => reject(err));
    req.end();
  });
}

module.exports = async function handler(req, res) {
  // CORS Headers
  res.setHeader('Access-Control-Allow-Credentials', 'true');
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'GET,OPTIONS,POST');
  res.setHeader(
    'Access-Control-Allow-Headers',
    'X-CSRF-Token, X-Requested-With, Accept, Accept-Version, Content-Length, Content-MD5, Content-Type, Date, X-Api-Version'
  );

  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

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
    const queryPath = `${BOT_PATH}?admission_no=${encodeURIComponent(admissionNo)}&first_name=${encodeURIComponent(firstName)}`;
    const eaesResp = await fetchFromEaes(queryPath);

    // 200 OK: Results Live & Found
    if (eaesResp.statusCode === 200) {
      let data = {};
      try { data = JSON.parse(eaesResp.body); } catch (e) {}

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

      resultCache.set(cacheKey, parsed);
      if (resultCache.size > 1000) {
        const firstKey = resultCache.keys().next().value;
        resultCache.delete(firstKey);
      }

      return res.status(200).json(parsed);
    }

    // 423 Locked: Not Released Yet
    if (eaesResp.statusCode === 423) {
      let detail = 'The 2018 result is not released.';
      try {
        const errData = JSON.parse(eaesResp.body);
        if (errData.detail) detail = errData.detail;
      } catch (e) {}

      globalNotReleasedUntil = Date.now() + 30000;
      globalNotReleasedMsg = detail;

      return res.status(200).json({
        status: 'not_released',
        message: detail,
      });
    }

    // 404: Not Found
    if (eaesResp.statusCode === 404) {
      return res.status(200).json({
        status: 'not_found',
        message: `No student record found for admission number ${admissionNo} and name ${firstName}.`,
      });
    }

    return res.status(200).json({
      status: 'service_error',
      message: 'The EAES result server returned an unexpected response. Please retry in a few moments.',
    });

  } catch (error) {
    console.error('EAES Proxy Error:', error.message || error);
    return res.status(500).json({
      status: 'service_error',
      message: 'Could not connect to EAES result server. Please try again.',
    });
  }
};
