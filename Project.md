# FreshMinds Academy — EAES Entrance Result Bot Investigation & POC

## 1. Project Goal

FreshMinds Academy wants to build a Telegram bot that helps Ethiopian students check their university entrance exam results when results are released.

The intended user flow is:

```text
Student
   ↓
FreshMinds Result Bot
   ↓
Enter Admission Number
   ↓
Enter First Name
   ↓
Check EAES result
   ↓
Display result
   ↓
Invite student to FreshMinds Academy
   ↓
Guide them toward freshman preparation
   ↓
Eventually promote FreshMinds mobile app
```

The bot could become an important acquisition channel for FreshMinds because students are highly motivated to check their results immediately after release.

## 2. Business Context

FreshMinds Academy previously helped many Ethiopian students in 2018 E.C. through free freshman courses and learning resources distributed through YouTube and Telegram.

This year FreshMinds is preparing to launch a structured mobile application for freshman education.

The app is expected to launch approximately two weeks from now because it needs Google Play closed testing before public release.

The current priority is NOT to promote the paid app immediately.

The immediate goal is:

```text
Other Telegram channels
        ↓
FreshMinds Result Bot
        ↓
FreshMinds Telegram Channel
        ↓
Freshman education
        ↓
FreshMinds mobile app
```

## 3. Official EAES Services Observed

The official result ecosystem includes:

* `https://result.eaes.et`
* `https://result.neaea.gov.et`
* Official Telegram bot: `@eaesbot`
* SMS service: `6284`

The official Telegram bot was tested manually.

### Official Telegram Bot Test

Bot:

`@eaesbot`

Observed flow:

```text
/start
    ↓
"Please send me your Admission Number to begin."
    ↓
Admission Number
    ↓
"Great! Now, please enter your First Name:"
    ↓
First Name
    ↓
"Searching for your results, please wait..."
    ↓
Result / result-not-released message
```

Example test:

```text
Admission number: 347484
First name: Fresh
```

Response:

```text
The 2018 result is not released.
```

The official Telegram bot did not ask for a Cloudflare CAPTCHA during this interaction.

Important:

Do NOT automate or impersonate the official Telegram bot through a personal Telegram account unless an explicitly authorized integration exists.

## 4. Official Website Investigation

The official result website uses Cloudflare protection / Turnstile.

The Cloudflare check is automatically handled during the normal browser experience; there is no requirement for the user to manually solve a visual CAPTCHA in the observed flow.

The website communicates with a separate API:

```text
https://api.eaes.et
```

The API appears to be a Python FastAPI/Uvicorn service.

Observed response header:

```text
Server: uvicorn
```

The frontend is hosted at:

```text
https://result.eaes.et
```

and communicates with:

```text
https://api.eaes.et
```

## 5. Discovered Session Endpoint

The first important request observed in Chrome DevTools Network → Fetch/XHR:

```http
GET https://api.eaes.et/api/v1/session/key
```

Response:

```http
200 OK
```

Response content type:

```text
application/json
```

Important response headers included:

```text
Access-Control-Allow-Credentials: true
Access-Control-Allow-Origin: https://result.eaes.et
Server: uvicorn
```

The response body contained:

```json
{
  "session_id": "<REDACTED>",
  "session_secret": "<REDACTED>"
}
```

The actual session values must NEVER be hard-coded or committed.

These are temporary credentials/session values and should be treated as secrets.

## 6. Discovered Result Endpoint

The browser subsequently made this request:

```http
POST https://api.eaes.et/api/v1/results/web
```

The request body was observed to contain:

```json
{
  "admission_no": "<REDACTED>",
  "first_name": "<REDACTED>",
  "turnstileToken": "<REDACTED>"
}
```

The real values must never be stored in source code or logs.

A fabricated test was performed using:

```text
admission_no = 1234567
first_name = abebe
```

The API responded:

```json
{
  "detail": "Student not found with provided details."
}
```

Chrome showed HTTP:

```text
404 Not Found
```

This likely represents an application-level "student not found" response rather than proof that the endpoint itself doesn't exist, because the response is a structured FastAPI-style error.

This needs further investigation.

## 7. Current Known Architecture

Based on observed traffic, the web flow appears approximately:

```text
┌───────────────────────────┐
│ result.eaes.et            │
│ Official Result Frontend  │
└─────────────┬─────────────┘
              │
              │ GET /api/v1/session/key
              ▼
┌───────────────────────────┐
│ api.eaes.et               │
│ FastAPI/Uvicorn Backend   │
└─────────────┬─────────────┘
              │
              ▼
       session_id
       session_secret
              │
              ▼
       Cloudflare Turnstile
              │
              ▼
       turnstileToken
              │
              ▼
POST /api/v1/results/web
              │
              ├── admission_no
              ├── first_name
              └── turnstileToken
              │
              ▼
        Student lookup
              │
              ▼
       Result / not found
```

## 8. Main Technical Question

The key question is NOT:

> "How can we bypass Cloudflare?"

The key question is:

> "Does EAES provide a legitimate, authorized machine-readable integration path that FreshMinds can use?"

The investigation should determine:

1. Whether `/api/v1/results/web` requires a valid Turnstile token.
2. Whether the session_id/session_secret are required for the result request.
3. How the session_secret is used.
4. Whether additional headers are required.
5. Whether the API is intended only for the official website.
6. Whether EAES provides any public API/developer integration.
7. Whether a third-party educational service can obtain permission to use the result service.
8. Whether an alternative official integration is available.

## 9. Security Constraints

Do NOT:

* bypass Cloudflare;
* bypass Turnstile;
* forge Turnstile tokens;
* use CAPTCHA-solving services;
* reuse captured Turnstile tokens;
* steal/replay session secrets;
* rotate fingerprints/user agents to evade anti-bot systems;
* use FlareSolverr to defeat Cloudflare;
* use stealth browser techniques specifically to evade EAES/Cloudflare protections;
* impersonate the official EAES Telegram bot through a personal Telegram account;
* attempt to access another student's result;
* scrape or store student results without a legitimate purpose/appropriate safeguards.

The goal is to investigate and integrate with the service legitimately.

## 10. Safe POC — Phase 1

Build a tiny Python diagnostic client that only tests the public session endpoint.

It should:

```text
GET https://api.eaes.et/api/v1/session/key
```

and report:

* HTTP status
* response headers relevant to CORS
* JSON structure
* whether session_id exists
* whether session_secret exists

Do NOT print the actual secret in logs.

Expected structure:

```json
{
  "session_id": "...",
  "session_secret": "..."
}
```

The POC must not attempt to bypass Turnstile.

## 11. Safe POC — Phase 2

Investigate the official frontend request flow.

Using Chrome DevTools Network → Fetch/XHR, document:

```text
1. /api/v1/session/key
2. Cloudflare/Turnstile interaction
3. /api/v1/results/web
4. Any request after /results/web
```

For each request document only:

* URL
* HTTP method
* non-sensitive header names
* payload field names
* response field names
* HTTP status

Never record:

* real student data
* session_secret
* authentication tokens
* cookies
* Turnstile tokens

## 12. Test Data

Use fabricated data for development:

```text
Admission number:
1234567

First name:
abebe
```

Do not test random real students.

For an actual successful result test, only use data belonging to an authorized test user/student.

## 13. Possible Outcomes

### Outcome A — Official/public API integration exists

Ideal:

```text
FreshMinds Bot
      ↓
FreshMinds Backend
      ↓
Official EAES API
      ↓
Result
```

Then investigate:

* rate limits
* authentication
* usage permissions
* caching
* privacy
* concurrency
* error handling

### Outcome B — Web API requires Turnstile

If every result request requires a fresh valid Turnstile token generated through the official website, do NOT bypass it.

Investigate whether EAES offers an authorized API or integration.

If not, build a guided experience using official EAES services.

### Outcome C — EAES provides a partner/API mechanism

This is preferred.

Contact EAES and request permission/API access for an educational platform helping students check their results.

### Outcome D — No integration available

Build:

```text
FreshMinds Result Assistant
```

that helps students:

* understand when results are released
* navigate official EAES result services
* use the official Telegram bot
* use the official website
* understand result terminology
* find next steps after receiving results
* prepare for freshman year

## 14. Production Bot Concept

If legitimate API access becomes available:

```text
Telegram User
      ↓
/start
      ↓
Privacy explanation
      ↓
Admission Number
      ↓
First Name
      ↓
FreshMinds Backend
      ↓
EAES API
      ↓
Result
      ↓
Formatted Result
      ↓
Freshman Guidance
```

Potential result message:

```text
🎓 Your Entrance Exam Result

Name: [Name]
Admission Number: [Admission Number]

Total Score: [Score]

Congratulations! 🎉

Your entrance exam is only the beginning.

📚 Prepare for your freshman journey with FreshMinds Academy.
```

Do not imply that FreshMinds is an official EAES service.

Use wording such as:

> "FreshMinds Result Assistant — powered by official EAES result information."

Only use such wording if legally/technically accurate and appropriate.

## 15. Scaling Considerations

If legitimate API access is obtained and the bot becomes popular:

Potential architecture:

```text
Telegram
    ↓
Bot API
    ↓
Load Balancer / API
    ↓
Async Worker Queue
    ↓
EAES Integration
    ↓
Redis
    ↓
Result Response
```

Potential technologies:

* Python
* FastAPI
* aiogram or python-telegram-bot
* Redis
* PostgreSQL/MySQL if persistent data is genuinely necessary
* Docker
* VPS/cloud deployment

Use rate limiting and backpressure.

Do not hammer EAES during peak traffic.

## 16. Caching

If permitted by EAES and appropriate for privacy:

```text
User requests result
      ↓
Check short-lived cache
      ↓
If available → return
      ↓
Otherwise → official API
      ↓
Return result
```

Do not retain sensitive student data indefinitely.

Prefer short-lived caching or no persistent result storage unless there is a clear legitimate need.

## 17. Marketing Concept

The bot is primarily a student acquisition tool.

The intended funnel:

```text
Other Telegram channels
        ↓
FreshMinds Result Bot
        ↓
FreshMinds Telegram Channel
        ↓
Result support
        ↓
Freshman guidance
        ↓
FreshMinds Mobile App
```

The first external promotion should NOT focus heavily on the paid app.

The immediate message should be:

> "FreshMinds is here to help students through results day and their freshman journey."

After students join the FreshMinds Telegram channel, the mobile app can be introduced later.

## 18. Product Vision

FreshMinds should not become known merely as a result checker.

The long-term positioning is:

```text
Entrance Exam
      ↓
Result
      ↓
University / Department
      ↓
Freshman Preparation
      ↓
Courses
      ↓
Practice
      ↓
Exams
      ↓
Academic Progress
```

The result bot is the **entry point**, not the final product.

## 19. Immediate Task for the Agent

Do NOT build the complete production bot yet.

First:

1. Analyze the known EAES API flow.
2. Build the safe `/session/key` diagnostic POC.
3. Document the request sequence.
4. Determine what `/results/web` requires.
5. Determine whether the session values are used in subsequent requests.
6. Determine whether Turnstile is mandatory.
7. Search for official EAES API/developer/partner documentation.
8. Identify any legitimate third-party integration path.
9. Produce a technical feasibility report.
10. Only after that, propose the production architecture.

The agent must clearly distinguish:

* **observed facts**
* **inferences**
* **unknowns**
* **assumptions**

Do not assume that an API endpoint being publicly reachable means third-party use is authorized.

## 20. Success Criteria

The investigation is successful if we can answer:

> Can FreshMinds legally and technically provide an automated entrance-result lookup service using official EAES infrastructure without bypassing security controls?

Possible final answer:

```text
YES — official API available
```

or:

```text
YES — integration possible with authorization
```

or:

```text
NO — web API requires protected browser-only flow;
use official EAES channels instead
```

The priority is **reliable, ethical, secure integration**, not bypassing EAES security.
