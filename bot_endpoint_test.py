"""
FreshMinds EAES — Bot Endpoint Investigation

The OpenAPI spec revealed:
  GET /api/v1/results/bot
    Parameters: admission_no (query), first_name (query)
    Summary: "For Telegram Bot"
    NO Turnstile, NO CAPTCHA, NO HMAC signature required

This script tests the bot endpoint with fabricated data
to confirm it's reachable and understand its response structure.

Security:
  - Uses ONLY fabricated test data (1234567 / abebe)
  - Does NOT access real student data
  - Does NOT print sensitive values
"""

import httpx
import json
from datetime import datetime, timezone


API_BASE = "https://api.eaes.et"
BOT_ENDPOINT = f"{API_BASE}/api/v1/results/bot"
SMS_ENDPOINT = f"{API_BASE}/api/v1/results/sms"
CAPTCHA_CONFIG_ENDPOINT = f"{API_BASE}/api/v1/config/captcha"
CAPTCHA_ENDPOINT = f"{API_BASE}/api/v1/captcha"
HEALTH_ENDPOINT = f"{API_BASE}/health"

# Fabricated test data
TEST_ADMISSION = "1234567"
TEST_NAME = "abebe"


def test_endpoint(client, name, method, url, params=None, json_body=None):
    """Test an endpoint and report results."""
    print(f"\n{'='*60}")
    print(f"TEST: {name}")
    print(f"  {method} {url}")
    if params:
        safe_params = {k: v for k, v in params.items()}
        print(f"  Params: {safe_params}")
    if json_body:
        print(f"  Body: {json_body}")
    print("-" * 60)

    try:
        if method == "GET":
            resp = client.get(url, params=params)
        elif method == "POST":
            resp = client.post(url, json=json_body)

        print(f"  Status: {resp.status_code} {resp.reason_phrase}")
        print(f"  Content-Type: {resp.headers.get('content-type', 'N/A')}")
        print(f"  Server: {resp.headers.get('server', 'N/A')}")

        # Print all response headers
        print(f"\n  Response Headers:")
        for name_h, value_h in resp.headers.items():
            # Skip cookie values
            if name_h.lower() in ('set-cookie',):
                print(f"    {name_h}: <REDACTED>")
            else:
                print(f"    {name_h}: {value_h}")

        # Parse body
        try:
            data = resp.json()
            print(f"\n  Response Body (JSON):")
            formatted = json.dumps(data, indent=4, ensure_ascii=False)
            # Truncate if too long but still show structure
            if len(formatted) > 1000:
                print(f"    {formatted[:1000]}")
                print(f"    ... [truncated, total {len(formatted)} chars]")
            else:
                for line in formatted.split('\n'):
                    print(f"    {line}")
        except Exception:
            body = resp.text[:500]
            print(f"\n  Response Body (text):")
            print(f"    {body}")

        return resp.status_code, resp

    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        return None, None


def main():
    print("=" * 60)
    print("EAES Bot & SMS Endpoint Investigation")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print("=" * 60)

    with httpx.Client(timeout=15.0, follow_redirects=True) as client:

        # 1. Health check
        test_endpoint(client, "Health Check", "GET", HEALTH_ENDPOINT)

        # 2. Captcha config — what captcha type is active?
        test_endpoint(client, "Captcha Config", "GET", CAPTCHA_CONFIG_ENDPOINT)

        # 3. Math captcha — can we get one?
        test_endpoint(client, "Get Math Captcha", "GET", CAPTCHA_ENDPOINT)

        # 4. BOT ENDPOINT — the critical test
        test_endpoint(client, "Bot Result Lookup (fabricated data)", "GET", BOT_ENDPOINT,
                      params={"admission_no": TEST_ADMISSION, "first_name": TEST_NAME})

        # 5. SMS ENDPOINT — also no captcha required
        test_endpoint(client, "SMS Result Lookup (fabricated data)", "GET", SMS_ENDPOINT,
                      params={"admission_no": TEST_ADMISSION})

        # 6. Web GET endpoint with math captcha approach
        # First get a captcha
        print("\n\n" + "=" * 60)
        print("INVESTIGATING: Web GET with Math CAPTCHA approach")
        print("=" * 60)

        # Get session
        resp_session = client.get(f"{API_BASE}/api/v1/session/key")
        if resp_session.status_code == 200:
            session_data = resp_session.json()
            print(f"  Session obtained: session_id present={bool(session_data.get('session_id'))}")

        # Get captcha
        resp_captcha = client.get(CAPTCHA_ENDPOINT)
        if resp_captcha.status_code == 200:
            captcha_data = resp_captcha.json()
            print(f"  Captcha response keys: {list(captcha_data.keys()) if isinstance(captcha_data, dict) else 'not a dict'}")
            # Show captcha structure without solving
            print(f"  Captcha data: {json.dumps(captcha_data, indent=2, ensure_ascii=False)[:500]}")

    print("\n" + "=" * 60)
    print("Investigation complete.")
    print("=" * 60)


if __name__ == "__main__":
    main()
