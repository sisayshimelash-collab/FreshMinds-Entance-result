# FreshMinds EAES Result Bot

Telegram bot that checks Ethiopian university entrance exam results via the EAES API and helps students prepare for their freshman journey.

## Quick Start

### 1. Create a Telegram Bot

1. Open [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot`
3. Choose a name: `FreshMinds Result Assistant`
4. Choose a username: `FreshMindsResultBot` (must be unique)
5. Copy the bot token

### 2. Add the Bot to Your Channel

The bot needs to be an **admin** of `@freshminds_academy` to check membership:

1. Open the `@freshminds_academy` channel
2. Go to channel settings → Administrators
3. Add the bot as an administrator
4. The bot only needs the "See Members" permission

### 3. Configure

```bash
cd bot
copy .env.example .env
```

Edit `.env` and set your bot token:

```
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run

```bash
python main.py
```

## How It Works

```
User → /start
  ↓
Channel member? → NO → "Join @freshminds_academy first"
  ↓                         ↓
  YES                   User joins → "I've Joined ✓"
  ↓                         ↓
Admission Number ←──────────┘
  ↓
First Name
  ↓
EAES API: GET /api/v1/results/bot
  ↓
Display Result + FreshMinds Promo
```

## Project Structure

```
bot/
├── main.py           # Entry point
├── config.py         # Environment configuration
├── eaes_client.py    # EAES API client
├── handlers.py       # Telegram conversation handlers
├── messages.py       # Bilingual message templates
├── rate_limiter.py   # Per-user rate limiting
├── requirements.txt  # Dependencies
├── .env.example      # Environment template
└── .env              # Your config (not committed)
```

## EAES API

The bot uses the discovered public endpoint:

```
GET https://api.eaes.et/api/v1/results/bot?admission_no=...&first_name=...
```

This endpoint:
- Requires NO Turnstile / CAPTCHA
- Requires NO authentication
- Returns student info + subject results
- Returns `423 Locked` when results aren't released yet

## Security Notes

- Bot token is loaded from `.env` (never committed)
- No student data is stored or cached
- Rate limiting prevents abuse (3 requests/user/minute)
- Channel membership is verified via Telegram Bot API
