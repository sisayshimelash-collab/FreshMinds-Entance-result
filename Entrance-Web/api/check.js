/**
 * Vercel Serverless Function: /api/check
 * 
 * High-performance, low-latency EAES Result Proxy:
 * - Queries active EAES results endpoint
 * - Parses both SMS & JSON official result payloads
 * - 30-second Stampede Shield & In-memory LRU cache
 */

const https = require('https');

const EAES_HOST = 'api.eaes.et';
const SMS_PATH = '/api/v1/results/sms';
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
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
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

function parseSmsResult(text, admissionNo, firstName) {
  const nameMatch = text.match(/Name:\s*([^;]+);/i);
  const fullName = nameMatch ? nameMatch[1].trim() : firstName;

  const admMatch = text.match(/Admission\s*No:\s*([^;]+);/i);
  const parsedAdm = admMatch ? admMatch[1].trim() : admissionNo;

  const resMatch = text.match(/Results:\s*([^;]+);/i);
  const results = [];
  if (resMatch) {
    const entries = resMatch[1].split(',');
    for (let e of entries) {
      e = e.trim();
      if (e) {
        const lastSpace = e.lastIndexOf(' ');
        if (lastSpace !== -1) {
          results.push({
            subject: e.substring(0, lastSpace).trim(),
            result: e.substring(lastSpace + 1).trim(),
          });
        } else {
          results.push({ subject: e, result: '-' });
        }
      }
    }
  }

  const totalMatch = text.match(/Total\s*([\d.]+)/i);
  if (totalMatch) {
    results.push({ subject: 'Total', result: totalMatch[1].trim().replace(/\.$/, '') });
  }

  const avgMatch = text.match(/Average\s*([\d.]+)/i);
  if (avgMatch) {
    results.push({ subject: 'Average', result: avgMatch[1].trim().replace(/\.$/, '') });
  }

  return {
    status: 'success',
    student: {
      full_name: fullName,
      admission_no: parsedAdm,
      school: null,
      stream: null,
      sex: null,
      age: null,
    },
    results: results,
  };
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
    // 3. Query the active, high-speed EAES SMS endpoint
    const queryPath = `${SMS_PATH}?admission_no=${encodeURIComponent(admissionNo)}&first_name=${encodeURIComponent(firstName)}`;
    const eaesResp = await fetchFromEaes(queryPath);

    // 200 OK: Results Live & Found
    if (eaesResp.statusCode === 200) {
      let parsed;
      const textBody = eaesResp.body || '';

      if (textBody.includes('{SMS:TEXT}') || textBody.includes('Name:')) {
        parsed = parseSmsResult(textBody, admissionNo, firstName);
      } else {
        try {
          const data = JSON.parse(textBody);
          const studentInfo = data.studentInfo || {};
          const rawResults = data.results || [];
          parsed = {
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
        } catch (e) {
          parsed = parseSmsResult(textBody, admissionNo, firstName);
        }
      }

      resultCache.set(cacheKey, parsed);
      if (resultCache.size > 1000) {
        const firstKey = resultCache.keys().next().value;
        resultCache.delete(firstKey);
      }

      return res.status(200).json(parsed);
    }

    // 404: Not Found
    if (eaesResp.statusCode === 404) {
      return res.status(200).json({
        status: 'not_found',
        message: `No student record found for admission number ${admissionNo} and name ${firstName}.`,
      });
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
