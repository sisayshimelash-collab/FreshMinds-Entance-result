"""
FreshMinds Invite Competition Bot — Configuration
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file
_env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(_env_path, override=True)

# Bot & Channel Configuration
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# Target Channel to grow (can be username without @ or numeric ID)
_raw_channel = os.getenv("TARGET_CHANNEL", "freshminds_academy").strip()
if _raw_channel.startswith("@"):
    TARGET_CHANNEL: str = _raw_channel[1:]
else:
    TARGET_CHANNEL: str = _raw_channel

# If channel is username, format with @ for Telegram API
if not TARGET_CHANNEL.startswith("-"):
    TARGET_CHANNEL_ID: str = f"@{TARGET_CHANNEL}"
else:
    TARGET_CHANNEL_ID: str = TARGET_CHANNEL

# Admin User IDs
_raw_admins = os.getenv("ADMIN_IDS", "")
ADMIN_IDS: set[int] = {
    int(x.strip()) for x in _raw_admins.split(",") if x.strip().isdigit()
}

# Competition Information
COMPETITION_TITLE: str = os.getenv(
    "COMPETITION_TITLE", "የ 2018 ዓ.ም የ Freshman ሳምንታዊ የመጋበዝ ውድድር"
)
PRIZE_1ST: str = os.getenv("PRIZE_1ST", "3000 ብር + የ Freshman VIP ኮርሶች")
PRIZE_2ND: str = os.getenv("PRIZE_2ND", "1500 ብር + የ Freshman VIP ኮርሶች")
PRIZE_3RD: str = os.getenv("PRIZE_3RD", "500 ብር + የ Freshman VIP ኮርሶች")
PRIZE_4TH_10TH: str = os.getenv("PRIZE_4TH_10TH", "የሞባይል ካርድ + የ Freshman VIP ኮርሶች")

# Database Path
DB_PATH: Path = Path(__file__).resolve().parent / "invite_competition.db"
