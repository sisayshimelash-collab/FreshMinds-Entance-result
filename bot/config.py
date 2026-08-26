"""
FreshMinds Result Bot — Configuration

Loads settings from environment variables / .env file.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from the bot directory
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)


# ── Telegram ─────────────────────────────────────────────────────────────────

BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# ── EAES API ─────────────────────────────────────────────────────────────────

EAES_API_BASE: str = os.getenv("EAES_API_BASE", "https://api.eaes.et")
EAES_SMS_ENDPOINT: str = f"{EAES_API_BASE}/api/v1/results/sms"
EAES_BOT_ENDPOINT: str = f"{EAES_API_BASE}/api/v1/results/bot"
REQUEST_TIMEOUT: int = int(os.getenv("REQUEST_TIMEOUT", "15"))

# ── FreshMinds Channel & Web ────────────────────────────────────────────────
FRESHMINDS_CHANNEL: str = os.getenv("FRESHMINDS_CHANNEL", "freshminds_academy")
FRESHMINDS_CHANNEL_LINK: str = f"https://t.me/{FRESHMINDS_CHANNEL}"
FRESHMINDS_WEB_URL: str = os.getenv("FRESHMINDS_WEB_URL", "https://fresh-minds-entance-result.vercel.app")

# ── Rate Limiting ────────────────────────────────────────────────────────────

RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "3"))
RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))
