"""
FreshMinds EAES — Exhaustive API Path Discovery

Probes every plausible endpoint and integration path to determine
whether a non-browser result lookup is possible.

Security: Does NOT bypass Turnstile, forge tokens, or access real student data.
Only tests publicly reachable URLs and documents HTTP responses.
"""

import httpx
import json
import sys
from datetime import datetime, timezone


# ─── Configuration ───────────────────────────────────────────────────────────

API_BASE = "https://api.eaes.et"
RESULT_SITE = "https://result.eaes.et"
NEAEA_SITE = "https://result.neaea.gov.et"

# Fabricated test data only
TEST_ADMISSION = "1234567"
TEST_NAME = "abebe"

# Common FastAPI auto-doc paths
FASTAPI_DOC_PATHS = [
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/openapi.json",
    "/api/openapi.json",
]

# Possible alternative result endpoints (educated guesses based on naming patterns)
ALTERNATIVE_RESULT_ENDPOINTS = [
    "/api/v1/results",
    "/api/v1/results/",
    "/api/v1/results/bot",
    "/api/v1/results/telegram",
    "/api/v1/results/api",
    "/api/v1/results/mobile",
    "/api/v1/results/app",
    "/api/v1/results/partner",
    "/api/v1/results/public",
    "/api/v1/results/check",
    "/api/v1/results/lookup",
    "/api/v1/results/query",
    "/api/v1/results/sms",
    "/api/v1/result",
    "/api/v1/result/web",
    "/api/v1/student",
    "/api/v1/student/result",
    "/api/v1/search",
    "/api/v2/results/web",
    "/api/v2/results",
    "/api/results",
    "/results",
    "/result",
]

# Possible session/auth endpoints
SESSION_ENDPOINTS = [
    "/api/v1/session/key",
    "/api/v1/session",
    "/api/v1/session/token",
    "/api/v1/auth",
    "/api/v1/auth/token",
    "/api/v1/token",
    "/api/v1/config",
    "/api/v1/health",
    "/api/v1/status",
    "/api/v1/",
    "/api/v1",
    "/api/",
    "/health",
    "/",
]

HEADERS_BROWSER = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "en-US,en;q=0.9",
    "Origin": "https://result.eaes.et",
    "Referer": "https://result.eaes.et/",
}


def safe_truncate(text: str, max_len: int = 300) -> str:
    """Truncate response body for safe logging."""
    if len(text) <= max_len:
        return text
    return text[:max_len] + f"... [truncated, total {len(text)} chars]"


def redact_sensitive(text: str) -> str:
    """Redact potential sensitive values from response text."""
    # Don't print anything that looks like a token/secret
    import re
    text = re.sub(r'"session_secret"\s*:\s*"[^"]*"', '"session_secret": "<REDACTED>"', text)
    text = re.sub(r'"session_id"\s*:\s*"[^"]*"', '"session_id": "<REDACTED>"', text)
    text = re.sub(r'"token"\s*:\s*"[^"]*"', '"token": "<REDACTED>"', text)
    text = re.sub(r'"secret"\s*:\s*"[^"]*"', '"secret": "<REDACTED>"', text)
    text = re.sub(r'"key"\s*:\s*"[^"]*"', '"key": "<REDACTED>"', text)
    return text


def probe_url(client: httpx.Client, method: str, url: str, json_body=None, label: str = "") -> dict:
    """Probe a URL and return structured result."""
    result = {
        "url": url,
        "method": method,
        "label": label,
        "status": None,
        "content_type": None,
        "server": None,
        "body_preview": None,
        "error": None,
        "interesting": False,
    }

    try:
        if method == "GET":
            resp = client.get(url)
        elif method == "POST":
            resp = client.post(url, json=json_body or {})
        elif method == "OPTIONS":
            resp = client.options(url)
        else:
            result["error"] = f"Unknown method: {method}"
            return result

        result["status"] = resp.status_code
        result["content_type"] = resp.headers.get("content-type", "")
        result["server"] = resp.headers.get("server", "")

        body = redact_sensitive(safe_truncate(resp.text))
        result["body_preview"] = body

        # Mark as interesting if not a standard error
        if resp.status_code not in (403, 404, 405, 301, 302, 308, 503):
            result["interesting"] = True
        # Also interesting if it's a structured JSON error (FastAPI style)
        if resp.status_code in (404, 422) and "application/json" in result["content_type"]:
            result["interesting"] = True

    except httpx.ConnectError as e:
        result["error"] = f"Connection failed: {e}"
    except httpx.TimeoutException:
        result["error"] = "Timeout"
    except Exception as e:
        result["error"] = f"{type(e).__name__}: {e}"

    return result


def print_result(r: dict):
    """Print a single probe result."""
    marker = "[*]" if r["interesting"] else "[ ]"
    status_str = str(r["status"]) if r["status"] else "ERR"
    print(f"  {marker} [{r['method']}] {r['url']}")
    if r["label"]:
        print(f"    Label: {r['label']}")
    if r["error"]:
        print(f"    Error: {r['error']}")
    else:
        print(f"    Status: {status_str} | Content-Type: {r['content_type']} | Server: {r['server']}")
        if r["body_preview"]:
            print(f"    Body: {r['body_preview']}")
    print()


def main():
    print("=" * 70)
    print("EAES Exhaustive API Path Discovery")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 70)
    print()

    interesting_results = []

    with httpx.Client(timeout=12.0, follow_redirects=True, headers=HEADERS_BROWSER) as client:

        # ─── Part 1: FastAPI auto-documentation ──────────────────────────
        print("=" * 50)
        print("PART 1: FastAPI Auto-Documentation Endpoints")
        print("=" * 50)
        for path in FASTAPI_DOC_PATHS:
            url = f"{API_BASE}{path}"
            r = probe_url(client, "GET", url, label="FastAPI docs")
            print_result(r)
            if r["interesting"]:
                interesting_results.append(r)

        # ─── Part 2: Session/Auth endpoints ──────────────────────────────
        print("=" * 50)
        print("PART 2: Session & Auth Endpoints")
        print("=" * 50)
        for path in SESSION_ENDPOINTS:
            url = f"{API_BASE}{path}"
            r = probe_url(client, "GET", url, label="Session/Auth")
            print_result(r)
            if r["interesting"]:
                interesting_results.append(r)

        # ─── Part 3: Alternative result endpoints (GET) ──────────────────
        print("=" * 50)
        print("PART 3: Alternative Result Endpoints (GET)")
        print("=" * 50)
        for path in ALTERNATIVE_RESULT_ENDPOINTS:
            url = f"{API_BASE}{path}"
            r = probe_url(client, "GET", url, label="Alt result (GET)")
            print_result(r)
            if r["interesting"]:
                interesting_results.append(r)

        # ─── Part 4: Alternative result endpoints (POST with test data) ──
        print("=" * 50)
        print("PART 4: Alternative Result Endpoints (POST, fabricated data)")
        print("=" * 50)

        # Test different payload shapes
        payloads = [
            {
                "label": "web-style (no turnstile)",
                "body": {"admission_no": TEST_ADMISSION, "first_name": TEST_NAME},
            },
            {
                "label": "web-style (empty turnstile)",
                "body": {"admission_no": TEST_ADMISSION, "first_name": TEST_NAME, "turnstileToken": ""},
            },
            {
                "label": "bot-style guess",
                "body": {"admission_number": TEST_ADMISSION, "first_name": TEST_NAME},
            },
            {
                "label": "minimal",
                "body": {"admission_no": TEST_ADMISSION, "name": TEST_NAME},
            },
        ]

        post_paths = [
            "/api/v1/results/web",
            "/api/v1/results/bot",
            "/api/v1/results/telegram",
            "/api/v1/results/api",
            "/api/v1/results/mobile",
            "/api/v1/results/check",
            "/api/v1/results",
            "/api/v1/result",
            "/api/v1/student/result",
        ]

        for path in post_paths:
            url = f"{API_BASE}{path}"
            for payload in payloads:
                r = probe_url(client, "POST", url, json_body=payload["body"],
                              label=f"POST {payload['label']}")
                print_result(r)
                if r["interesting"]:
                    interesting_results.append(r)

        # ─── Part 5: OPTIONS (CORS preflight) on key endpoints ───────────
        print("=" * 50)
        print("PART 5: CORS Preflight (OPTIONS)")
        print("=" * 50)
        cors_paths = [
            "/api/v1/results/web",
            "/api/v1/session/key",
            "/api/v1/results",
        ]
        for path in cors_paths:
            url = f"{API_BASE}{path}"
            r = probe_url(client, "OPTIONS", url, label="CORS preflight")
            print_result(r)
            if r["interesting"]:
                interesting_results.append(r)

        # ─── Part 6: NEAEA alternative domain ────────────────────────────
        print("=" * 50)
        print("PART 6: NEAEA Alternative Domain")
        print("=" * 50)
        neaea_paths = [
            "/",
            "/api/v1/session/key",
            "/api/v1/results/web",
        ]
        for path in neaea_paths:
            url = f"{NEAEA_SITE}{path}"
            r = probe_url(client, "GET", url, label="NEAEA domain")
            print_result(r)
            if r["interesting"]:
                interesting_results.append(r)

        # ─── Part 7: Check if result.eaes.et has an API proxy ────────────
        print("=" * 50)
        print("PART 7: Frontend Domain API Proxy Check")
        print("=" * 50)
        proxy_paths = [
            "/api/v1/session/key",
            "/api/v1/results/web",
            "/api/",
        ]
        for path in proxy_paths:
            url = f"{RESULT_SITE}{path}"
            r = probe_url(client, "GET", url, label="Frontend proxy")
            print_result(r)
            if r["interesting"]:
                interesting_results.append(r)

    # ─── Summary ─────────────────────────────────────────────────────────
    print()
    print("=" * 70)
    print(f"SUMMARY — {len(interesting_results)} interesting responses found")
    print("=" * 70)
    for r in interesting_results:
        status_str = str(r["status"]) if r["status"] else "ERR"
        print(f"  [*] {r['method']} {r['url']} -> {status_str} ({r['label']})")
    print()
    print("=" * 70)
    print("Discovery complete.")
    print("=" * 70)


if __name__ == "__main__":
    main()
