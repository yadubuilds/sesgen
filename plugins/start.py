from pyrogram import Client, filters
from pyrogram.types import (
    Message, CallbackQuery,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from plugins.store import user_data


# ── Keyboards ────────────────────────────────────────────────────────────────

def main_menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🔵  Pyrogram Session", callback_data="type_pyrogram"),
            InlineKeyboardButton("🟣  Telethon Session",  callback_data="type_telethon"),
        ],
        [InlineKeyboardButton("❌  Cancel", callback_data="cancel")]
    ])

def cancel_btn():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌  Cancel", callback_data="cancel")
    ]])


# ── /start ────────────────────────────────────────────────────────────────────

@Client.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    uid = message.from_user.id

    # Clear any leftover state for this user
    if uid in user_data:
        if "client" in user_data[uid]:
            try:
                await user_data[uid]["client"].disconnect()
            except Exception:
                pass
        user_data.pop(uid, None)

    await message.reply_text(
        "**🔐 Session String Generator**\n\n"
        "Generate session strings for your Telegram userbot accounts.\n\n"
        "**Supported Libraries:**\n"
        "• 🔵 **Pyrogram** — for pyrofork / pyrogram bots\n"
        "• 🟣 **Telethon** — for telethon bots\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ **Security Notice**\n"
        "Session strings give **full access** to your Telegram account.\n"
        "Only use this bot in **private chat** and never share your session.\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "Choose a session type to begin 👇",
        reply_markup=main_menu(),
        disable_web_page_preview=True
    )


# ── Session type selected ────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^type_(pyrogram|telethon)$"))
async def choose_type(client: Client, query: CallbackQuery):
    uid   = query.from_user.id
    stype = query.data.replace("type_", "")   # "pyrogram" or "telethon"

    user_data[uid] = {"type": stype, "state": "get_api_id"}

    label = "🔵 Pyrogram" if stype == "pyrogram" else "🟣 Telethon"

    await query.message.edit_text(
        f"**{label} Session Generator**\n\n"
        "**Step 1 of 4 — API ID**\n\n"
        "Send your **API ID** *(numbers only)*\n\n"
        "📌 Get it from → [my.telegram.org/apps](https://my.telegram.org/apps)\n"
        "1. Log in → App API development tools\n"
        "2. Create an app if needed\n"
        "3. Copy the **App api_id**",
        reply_markup=cancel_btn(),
        disable_web_page_preview=True
    )
    await query.answer()


# ── Cancel ────────────────────────────────────────────────────────────────────

@Client.on_callback_query(filters.regex("^cancel$"))
async def cancel(client: Client, query: CallbackQuery):
    uid = query.from_user.id

    if uid in user_data:
        if "client" in user_data[uid]:
            try:
                await user_data[uid]["client"].disconnect()
            except Exception:
                pass
        user_data.pop(uid, None)

    await query.message.edit_text(
        "❌ **Cancelled.**\n\nSend /start whenever you want to try again.",
    )
    await query.answer("Cancelled")
