/**
 * Local Development Server for Entrance-Web
 * Runs both the static frontend and the /api/check proxy locally with 0 CORS issues!
 */

const http = require('http');
const fs = require('fs');
const path = require('path');
const checkHandler = require('./api/check.js');

const PORT = process.env.PORT || 3000;
const PUBLIC_DIR = __dirname;

const MIME_TYPES = {
  '.html': 'text/html; charset=utf-8',
  '.css': 'text/css; charset=utf-8',
  '.js': 'application/javascript; charset=utf-8',
  '.json': 'application/json',
  '.png': 'image/png',
  '.jpg': 'image/jpeg',
  '.svg': 'image/svg+xml',
  '.ico': 'image/x-icon',
};

const server = http.createServer(async (req, res) => {
  // Polyfill Vercel/Express helper functions on res for local dev
  res.status = function (code) {
    res.statusCode = code;
    return {
      json: function (data) {
        res.setHeader('Content-Type', 'application/json');
        res.writeHead(code);
        res.end(JSON.stringify(data));
      },
      end: function () {
        res.writeHead(code);
        res.end();
      },
    };
  };

  res.json = function (data) {
    res.setHeader('Content-Type', 'application/json');
    res.writeHead(res.statusCode || 200);
    res.end(JSON.stringify(data));
  };

  const urlObj = new URL(req.url, `http://${req.headers.host}`);
  const pathname = urlObj.pathname;

  // 1. Handle /api/check endpoint
  if (pathname === '/api/check') {
    if (req.method === 'POST') {
      let bodyStr = '';
      req.on('data', (chunk) => {
        bodyStr += chunk;
      });
      req.on('end', async () => {
        try {
          req.body = JSON.parse(bodyStr || '{}');
        } catch (e) {
          req.body = {};
        }
        await checkHandler(req, res);
      });
      return;
    } else {
      await checkHandler(req, res);
      return;
    }
  }

  // 2. Serve Static Files (index.html, style.css, app.js)
  let filePath = path.join(PUBLIC_DIR, pathname === '/' ? 'index.html' : pathname);
  const ext = path.extname(filePath).toLowerCase();

  fs.readFile(filePath, (err, content) => {
    if (err) {
      if (err.code === 'ENOENT') {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('404 Not Found');
      } else {
        res.writeHead(500, { 'Content-Type': 'text/plain' });
        res.end('500 Server Error');
      }
      return;
    }

    const contentType = MIME_TYPES[ext] || 'application/octet-stream';
    res.writeHead(200, { 'Content-Type': contentType });
    res.end(content);
  });
});

server.listen(PORT, () => {
  console.log('====================================================');
  console.log(` FreshMinds Result Web running at: http://localhost:${PORT}`);
  console.log(' Open http://localhost:3000 in your browser!');
  console.log('====================================================');
});
