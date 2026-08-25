# FreshMinds EAES Result Portal (Web App)

A modern, high-performance web portal for checking Ethiopian University Entrance Exam (ESSLCE) results, designed for **1-click deployment to Vercel**.

## Features

- ⚡ **Global Edge Performance**: Static pages load in < 50ms on Vercel CDN.
- 🛡️ **Zero CORS Issues**: Vercel Serverless API Route (`/api/check`) proxies requests directly to EAES API.
- 🇪🇹 **Bilingual Support**: Instant toggle between Amharic and English.
- 🎨 **Glassmorphism Dark Theme**: Modern typography (Inter, Outfit, Noto Sans Ethiopic) and smooth micro-animations.
- 🖨️ **Printable Scorecard**: Print / Save PDF official student scorecard.
- 📢 **Acquisition Funnel**: Direct Telegram Channel CTA (`@freshminds_academy`) and FreshMinds Mobile App launch teaser.

---

## 1-Click Deployment to Vercel

### Option 1: Deploy via Vercel CLI

From your terminal inside the `Entrance-Web` folder:

```bash
cd Entrance-Web
npx vercel
```

Follow the prompts (accept default settings) and your site will be live at `https://freshminds-result.vercel.app`!

### Option 2: Deploy via GitHub

1. Push the `Entrance-Web` folder to a GitHub repository.
2. Open [vercel.com](https://vercel.com) and click **"Add New Project"**.
3. Import your GitHub repository.
4. Click **"Deploy"** (no build settings needed!).

---

## Project Structure

```
Entrance-Web/
├── api/
│   └── check.js         # Vercel Serverless Function (EAES Proxy)
├── index.html           # Main Landing Page & Portal
├── style.css            # Glassmorphism Design System & Stylesheet
├── app.js               # Bilingual state, fetch, scorecard rendering
├── vercel.json          # Vercel routing & security headers
├── package.json         # Project metadata
└── README.md            # Documentation
```

## API Architecture

The `/api/check` endpoint runs on Vercel Serverless (Node.js 18+):
1. Sanitizes inputs (removes spaces, formats name).
2. Checks in-memory 30s stampede cache.
3. Queries `GET https://api.eaes.et/api/v1/results/bot?admission_no=...&first_name=...`.
4. Returns clean JSON response to client.
