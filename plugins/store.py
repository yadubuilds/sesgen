# ─────────────────────────────────────────────────
#  Shared in-memory store for all active sessions
#  user_data[user_id] = {
#      "type"            : "pyrogram" | "telethon",
#      "state"           : one of the STATE constants,
#      "api_id"          : int,
#      "api_hash"        : str,
#      "phone"           : str,
#      "phone_code_hash" : str,
#      "client"          : <pyrogram/telethon Client>
#  }
# ─────────────────────────────────────────────────

user_data: dict = {}

# ── States ────────────────────────────────────────
GET_API_ID   = "get_api_id"
GET_API_HASH = "get_api_hash"
GET_PHONE    = "get_phone"
GET_OTP      = "get_otp"
GET_2FA      = "get_2fa"
