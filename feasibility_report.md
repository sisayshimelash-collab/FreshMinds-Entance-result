# EAES Result Integration — Technical Feasibility Report

**Date:** 2026-08-24  
**Prepared for:** FreshMinds Academy  
**Status:** Investigation Complete

---

## Executive Summary

**FreshMinds cannot directly integrate with the EAES web result API** (`api.eaes.et`) without bypassing Cloudflare Turnstile security, which is prohibited. However, the official EAES **Telegram bot** (`@eaesbot`) offers a legitimate, bot-friendly path that does NOT use Turnstile. The recommended architecture is a **guided-experience bot** (Outcome D from Project.md), with ongoing monitoring for official API access.

---

## 1. Observed Facts

### 1.1 Session Endpoint — `GET /api/v1/session/key`

| Property | Value |
|---|---|
| URL | `https://api.eaes.et/api/v1/session/key` |
| HTTP Status | `200 OK` |
| Server | `uvicorn` (FastAPI) |
| Cloudflare blocking | **None** — responds to plain `httpx` requests |
| CORS headers | **Not present** on non-browser requests |
| Response fields | `session_id` (36 chars, UUID), `session_secret` (64 chars, hex hash) |

> [!NOTE]
> The session endpoint is publicly reachable without browser headers, Cloudflare challenge, or authentication. This is just a session initializer.

### 1.2 Result Endpoint — `POST /api/v1/results/web`

| Property | Value |
|---|---|
| URL | `https://api.eaes.et/api/v1/results/web` |
| Required fields | `admission_no`, `first_name`, `turnstileToken` |
| Turnstile token | **Mandatory** — the frontend enforces it |

### 1.3 Website Frontend — `result.eaes.et`

Evidence from browser investigation (screenshots captured):

**Page structure:**
- Title: "Student Result"
- Subtitle: "Enter credentials to view your exam results."
- Fields: "Admission Number", "First Name"
- Cloudflare Turnstile widget: **Visible and active**
- Button: "Check Result"
- Footer: "© 2026 EAES ICT Teams. All Rights Reserved."

**Turnstile behavior:**
- Widget loads immediately, showing "Verifying..."
- In automated browser context: widget showed **"Verification failed — Troubleshoot"**
- When submitting without valid Turnstile token: **"Please complete the security check."**

**Key evidence screenshot (after submit attempt):**

![EAES result page showing Turnstile verification failed and security check required](file:///C:/Users/sisay/.gemini/antigravity-ide/brain/b4423e2e-b9ab-4ad9-8dfb-d47495bf69da/eaes_after_submit_1787521418405.png)

### 1.4 Official EAES Services

| Channel | Turnstile Required? | Bot-Friendly? |
|---|---|---|
| `result.eaes.et` (website) | ✅ Yes | ❌ No |
| `@eaesbot` (Telegram bot) | ❌ No | ✅ Yes (tested manually) |
| SMS `6284` | ❌ No | ❌ (carrier integration) |

### 1.5 EAES GitHub

- Organization: [EAES-Ethiopia](https://github.com/EAES-Ethiopia)
- Description: "All tools and software being developed in MoE EAES are managed on this account."
- **No public API documentation, SDK, or developer integration guides found.**

### 1.6 EAES Contact Information

| Property | Value |
|---|---|
| Email | `aeaa2025@eaes.et` |
| Phone | +251 11-1-23-28-90 |
| Address | King George VI St, 5 Kilo, Addis Ababa |
| ICT Team | EAES ICT Team & Hawassa University ICT Team |

---

## 2. Inferences

### 2.1 Turnstile is mandatory for web API

The `POST /api/v1/results/web` endpoint requires a valid `turnstileToken`. The endpoint name itself (`/results/web`) suggests it was designed specifically for the browser-based flow. The website explicitly blocks submission without a valid Turnstile token.

### 2.2 No public third-party API exists

Multiple searches across:
- EAES official website
- EAES GitHub organization
- NEAEA/government portals
- Ethiopian edtech ecosystem
- Developer communities

All confirm: **No public API, developer portal, or third-party integration mechanism is documented.**

### 2.3 The official Telegram bot operates independently

The `@eaesbot` on Telegram does NOT use Cloudflare Turnstile. It appears to use a different backend path to query results. This is a legitimate, first-party channel built by the same EAES ICT team.

### 2.4 Session values are likely used for request context

The `session_id` (UUID) and `session_secret` (64-char hex) are likely used to:
- Associate the Turnstile challenge with the result request
- Prevent replay attacks
- Rate limit per-session

However, even with valid session values, the Turnstile token remains required.

---

## 3. Unknowns

| Unknown | Impact |
|---|---|
| Whether EAES has an internal API without Turnstile | Could enable Outcome A — but no evidence exists |
| Whether EAES would grant API access to an edtech partner | Could enable Outcome C — requires formal inquiry |
| Whether the official `@eaesbot` has rate limits | Affects whether directing users there is sustainable |
| How `session_secret` is validated server-side | Doesn't change the conclusion since Turnstile blocks us |
| Whether results have been released for 2018 E.C. | Affects immediate testing, not architecture |

---

## 4. Assumptions

| # | Assumption |
|---|---|
| 1 | The `/results/web` endpoint is the only result endpoint (no undiscovered `/results/api` or `/results/partner`) |
| 2 | EAES Turnstile enforcement is intentional anti-bot protection, not a misconfiguration |
| 3 | The official Telegram bot is maintained and will remain operational during result season |
| 4 | FreshMinds does not currently have a formal relationship with EAES |

---

## 5. Recommendation

### Primary: **Outcome D — FreshMinds Result Assistant (Guided Experience)**

Build a FreshMinds Telegram bot that:

```text
Student joins FreshMinds Bot
         ↓
Bot explains how to check results
         ↓
Direct link to @eaesbot + result.eaes.et
         ↓
"Did you get your result?"
         ↓
YES → Congratulations! Freshman guidance
         ↓
NO  → Help troubleshooting + "Check back soon"
         ↓
Invite to FreshMinds Telegram channel
         ↓
Freshman preparation content
         ↓
Eventually: FreshMinds mobile app
```

**Why this works:**
- ✅ No Turnstile bypass needed
- ✅ No legal/ethical concerns
- ✅ Still captures the student at the critical "results day" moment
- ✅ Builds trust by being genuinely helpful
- ✅ The funnel (bot → channel → app) still works
- ✅ Can be built and deployed within days

### Secondary: **Pursue Outcome C — Formal EAES Partnership**

In parallel, send a formal inquiry to `aeaa2025@eaes.et` requesting:
1. Whether EAES provides API access for authorized educational platforms
2. Whether a partner/institutional integration path exists
3. Terms and conditions for third-party result lookup services

If EAES grants API access, upgrade to Outcome A architecture later.

---

## 6. Outcome Classification

Referring to Project.md §13:

| Outcome | Status |
|---|---|
| **A** — Official/public API | ❌ Does not exist |
| **B** — Web API requires Turnstile | ✅ **Confirmed** |
| **C** — Partner/API mechanism | ❓ Unknown — requires formal inquiry |
| **D** — No integration available | ✅ **Current reality — recommended path** |

---

## 7. Final Answer

> **Can FreshMinds legally and technically provide an automated entrance-result lookup service using official EAES infrastructure without bypassing security controls?**

```text
NO — the web API requires a Cloudflare Turnstile token
that can only be generated through the official browser flow.

HOWEVER — the official @eaesbot Telegram bot provides
a legitimate, non-Turnstile result lookup service.

RECOMMENDED — build a guided-experience bot that directs
students to official channels while capturing them into
the FreshMinds funnel.

PARALLEL — contact EAES ICT Directorate (aeaa2025@eaes.et)
to inquire about formal API/partner access.
```
