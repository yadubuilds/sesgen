import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # ── Bot Credentials ───────────────────────────────────────
    API_ID    = int(os.environ.get("API_ID", 33013808))
    API_HASH  = os.environ.get("API_HASH", "fa3ab424a80a33bf68a33d6f949fc167")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8965996597:AAEKfHdCY1TP9LVIS1yzhwPj0dDpdkLNl1U")

    # ── Optional ──────────────────────────────────────────────
    # List of admin user IDs who can use /stats
    ADMINS = list(map(int, os.environ.get("ADMINS", "7863489250").split() if os.environ.get("ADMINS") else []))
