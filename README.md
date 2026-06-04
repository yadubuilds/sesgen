# 🔐 Telegram Session Generator Bot

A Telegram bot that generates **Pyrogram** and **Telethon** session strings securely through private chat.

---

## ✨ Features

- 🔵 **Pyrogram** session string generation (pyrofork compatible)
- 🟣 **Telethon** session string generation
- 🔐 **2FA support** — handles two-step verification
- 🗑️ **Auto-deletes** OTP and 2FA messages for security
- ⚡ Handles multiple users simultaneously
- 🛑 Cancel anytime with the Cancel button

---

## 🚀 Deployment on EC2

### Step 1 — Clone the repo
```bash
git clone https://github.com/YOURUSERNAME/session-bot.git
cd session-bot
```

### Step 2 — Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -U pip
pip install -U -r requirements.txt
```

### Step 3 — Set up environment variables
```bash
cp .env.example .env
nano .env
```
Fill in your `API_ID`, `API_HASH`, and `BOT_TOKEN`.

### Step 4 — Start with PM2
```bash
npm install -g pm2
pm2 start bot.py --name session-bot --interpreter /path/to/venv/bin/python3
pm2 save
pm2 startup
```

---

## ⚙️ Configuration

| Variable    | Description                              | Required |
|-------------|------------------------------------------|----------|
| `API_ID`    | From [my.telegram.org/apps](https://my.telegram.org/apps) | ✅ |
| `API_HASH`  | From [my.telegram.org/apps](https://my.telegram.org/apps) | ✅ |
| `BOT_TOKEN` | From [@BotFather](https://t.me/BotFather) | ✅ |
| `ADMINS`    | Space-separated admin user IDs           | ❌ |

---

## 🤖 Bot Commands

| Command  | Description          |
|----------|----------------------|
| `/start` | Start session generator |

---

## 🔒 Security Notes

- Sessions are **only generated in private chat**
- OTP and 2FA password messages are **auto-deleted**
- Session strings are **never logged or stored**
- Always keep your `.env` file out of version control

---

## 📦 Requirements

- Python 3.9+
- pyrofork
- tgcrypto
- telethon
- python-dotenv
