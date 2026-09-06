# 🏆 FreshMinds Invite & Referral Competition Bot

An automated Telegram referral bot that generates **unique direct channel invite links (`t.me/+...`)**, tracks real-time member joins to `@freshminds_academy`, delivers ready-to-forward promotional marketing posts, and maintains a live weekly leaderboard with anti-cheat protection.

---

## ✨ Features

- **Direct Channel Invite Links**: Friends click and join `@freshminds_academy` directly without touching the bot.
- **Ready-to-Forward Promotional Post**: Generates an attractive, formatted Amharic marketing post targeting 2019 E.C. freshman students with embedded unique join links.
- **1-Tap Copyable URL & Share Button**: Monospace link block + `[ 🚀 ለጓደኞች አጋራ ]` button.
- **Username-Free Support**: 100% functional for students with or without a `@username`.
- **Instant Join & Leave Notifications**: Pings the referrer immediately when someone joins (`+1 point`) or leaves (`-1 point`).
- **Live Leaderboard**: Real-time Top 10 rankings with medals (`🥇 1st`, `🥈 2nd`, `🥉 3rd`).
- **Anti-Cheat & Fraud Prevention**: 1 credit per lifetime account, self-referral blocked, leave deduction.
- **Admin Control Center**: `/broadcast`, `/admin_stats`, `/audit <user_id>`, and `/reset_week <Cycle Name>`.

---

## 🚀 Setup & Deployment

### 1. Telegram Channel Configuration
1. Open Telegram and go to your channel: **`@freshminds_academy`**.
2. Go to **Channel Settings ➜ Administrators ➜ Add Administrator**.
3. Search for your Bot username and grant the following permissions:
   - ✅ **Invite Users via Link**
   - ✅ **Manage Chat / Members** (allows the bot to receive `ChatMemberUpdated` events)

### 2. Configure Environment (`.env`)
Create a `.env` file in the `invite_bot/` directory:

```env
BOT_TOKEN=123456789:ABCDefghIJKlmnoPQRstuvWXyz
TARGET_CHANNEL=freshminds_academy
ADMIN_IDS=12345678,98765432
COMPETITION_TITLE=የ 2019 ዓ.ም የ Freshman ሳምንታዊ የመጋበዝ ውድድር
PRIZE_1ST=3000 ብር + የ Freshman VIP ኮርሶች
PRIZE_2ND=1500 ብር + የ Freshman VIP ኮርሶች
PRIZE_3RD=500 ብር + የ Freshman VIP ኮርሶች
PRIZE_4TH_10TH=የሞባይል ካርድ + የ Freshman VIP ኮርሶች
```

---

### 3. Running Locally
```bash
cd invite_bot
pip install -r requirements.txt
python main.py
```

---

### 4. Running with Docker on Cloud VPS
```bash
cd /root/FreshMinds-Repo/invite_bot
docker build -t freshminds_invite_bot .
docker run -d --name freshminds_invite_bot --restart unless-stopped --env-file .env freshminds_invite_bot
```

To view logs:
```bash
docker logs -f freshminds_invite_bot
```

---

## 🛠️ Admin Commands

- `/admin_stats`: View total bot users, total channel joins generated, active members, and churn rate.
- `/broadcast <message>`: Send announcements to all registered bot participants.
- `/audit <user_id>`: View the detailed join logs of all members invited by a specific user.
- `/reset_week <Cycle Name>`: Archive current week's winners to database and reset points for a new week.
