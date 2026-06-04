import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Bot Credentials ───────────────────────────────────────
    API_ID    = int(os.environ.get("API_ID", 0))
    API_HASH  = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

    # ── Optional ──────────────────────────────────────────────
    # List of admin user IDs who can use /stats
    ADMINS = list(map(int, os.environ.get("ADMINS", "").split() if os.environ.get("ADMINS") else []))
