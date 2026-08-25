"""
FreshMinds EAES Session Diagnostic — Phase 1 POC

This script tests ONLY the public session endpoint:
    GET https://api.eaes.et/api/v1/session/key

It reports:
  - HTTP status code
  - CORS-related response headers
  - JSON structure (field names only)
  - Whether session_id and session_secret fields exist

Security:
  - Does NOT print actual session_id or session_secret values
  - Does NOT attempt any Turnstile bypass
  - Does NOT attempt any result lookup
"""

import httpx
import json
import sys
from datetime import datetime, timezone


API_BASE = "https://api.eaes.et"
SESSION_ENDPOINT = f"{API_BASE}/api/v1/session/key"

# Headers that are safe to log (non-sensitive)
CORS_HEADERS = [
    "access-control-allow-origin",
    "access-control-allow-credentials",
    "access-control-allow-methods",
    "access-control-allow-headers",
    "access-control-expose-headers",
    "access-control-max-age",
]

INTERESTING_HEADERS = CORS_HEADERS + [
    "server",
    "content-type",
    "x-powered-by",
    "x-request-id",
    "cf-ray",
    "cf-cache-status",
]


def redact_value(key: str, value) -> str:
    """Return 'present (type)' for sensitive fields, actual value for safe fields."""
    sensitive_keys = {"session_id", "session_secret", "token", "secret", "key", "password"}
    if key.lower() in sensitive_keys:
        return f"<PRESENT — type: {type(value).__name__}, length: {len(str(value))}>"
    return str(value)


def describe_json_structure(data, indent=0) -> list[str]:
    """Recursively describe JSON structure without revealing sensitive values."""
    lines = []
    prefix = "  " * indent
    if isinstance(data, dict):
        for k, v in data.items():
            if isinstance(v, (dict, list)):
                lines.append(f"{prefix}{k}: ({type(v).__name__})")
                lines.extend(describe_json_structure(v, indent + 1))
            else:
                lines.append(f"{prefix}{k}: {redact_value(k, v)}")
    elif isinstance(data, list):
        lines.append(f"{prefix}[array of {len(data)} items]")
        if data:
            lines.extend(describe_json_structure(data[0], indent + 1))
    else:
        lines.append(f"{prefix}{redact_value('unknown', data)}")
    return lines


def run_diagnostic():
    """Run the session endpoint diagnostic."""
    print("=" * 60)
    print("FreshMinds EAES Session Diagnostic")
    print(f"Timestamp: {datetime.now(timezone.utc).isoformat()}")
    print(f"Endpoint:  {SESSION_ENDPOINT}")
    print("=" * 60)
    print()

    try:
        with httpx.Client(timeout=15.0, follow_redirects=True) as client:
            response = client.get(SESSION_ENDPOINT)

            # 1. HTTP Status
            print(f"[1] HTTP Status: {response.status_code} {response.reason_phrase}")
            print()

            # 2. Relevant Response Headers
            print("[2] Response Headers (non-sensitive):")
            for header_name in INTERESTING_HEADERS:
                value = response.headers.get(header_name)
                if value is not None:
                    print(f"    {header_name}: {value}")
            print()

            # 3. Additional headers (names only)
            print("[3] All Response Header Names:")
            for name in response.headers.keys():
                print(f"    - {name}")
            print()

            # 4. JSON Structure
            print("[4] Response Body Analysis:")
            try:
                data = response.json()
                print("    Content is valid JSON: YES")
                print("    Top-level type: " + type(data).__name__)
                print()
                print("    Structure:")
                for line in describe_json_structure(data, indent=2):
                    print(line)
                print()

                # 5. Key field checks
                print("[5] Key Field Checks:")
                if isinstance(data, dict):
                    has_session_id = "session_id" in data
                    has_session_secret = "session_secret" in data
                    print(f"    session_id present:     {has_session_id}")
                    print(f"    session_secret present: {has_session_secret}")
                    print(f"    Total fields:           {len(data)}")
                    print(f"    Field names:            {list(data.keys())}")
                else:
                    print("    Response is not a JSON object (dict).")

            except json.JSONDecodeError as e:
                print(f"    Content is valid JSON: NO")
                print(f"    Parse error: {e}")
                print(f"    Raw content (first 200 chars): {response.text[:200]}")

    except httpx.ConnectError as e:
        print(f"[ERROR] Connection failed: {e}")
        print("  The API server may be unreachable or blocking non-browser requests.")
    except httpx.TimeoutException as e:
        print(f"[ERROR] Request timed out: {e}")
    except Exception as e:
        print(f"[ERROR] Unexpected error: {type(e).__name__}: {e}")

    print()
    print("=" * 60)
    print("Diagnostic complete.")
    print("=" * 60)


if __name__ == "__main__":
    run_diagnostic()
