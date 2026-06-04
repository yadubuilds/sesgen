import logging

from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import (
    PhoneNumberInvalid, PhoneCodeInvalid, PhoneCodeExpired,
    SessionPasswordNeeded, FloodWait, ApiIdInvalid,
    PhoneNumberBanned, PhoneNumberUnoccupied
)

from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import (
    PhoneNumberInvalidError, PhoneCodeInvalidError,
    PhoneCodeExpiredError, SessionPasswordNeededError,
    FloodWaitError, ApiIdInvalidError
)

from plugins.store import user_data, GET_API_ID, GET_API_HASH, GET_PHONE, GET_OTP, GET_2FA

logger = logging.getLogger(__name__)


def cancel_btn():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("❌  Cancel", callback_data="cancel")
    ]])


def done_btn():
    return InlineKeyboardMarkup([[
        InlineKeyboardButton("🔄  Generate Another", callback_data=None),
    ]])


# ─────────────────────────────────────────────────────────────────────────────
#  Single handler for all text messages in private chat
# ─────────────────────────────────────────────────────────────────────────────

@Client.on_message(
    filters.private & filters.text & ~filters.command(["start"])
)
async def handle_input(bot: Client, message: Message):
    uid   = message.from_user.id
    text  = message.text.strip()

    # Not in a session flow
    if uid not in user_data:
        await message.reply("👋 Send /start to generate a session string.")
        return

    state  = user_data[uid].get("state")
    stype  = user_data[uid].get("type")        # "pyrogram" | "telethon"
    label  = "🔵 Pyrogram" if stype == "pyrogram" else "🟣 Telethon"

    # ── STEP 1: API ID ────────────────────────────────────────────────────────
    if state == GET_API_ID:
        if not text.isdigit():
            await message.reply(
                "❌ API ID must contain **numbers only**.\n"
                "Example: `22384016`\n\nTry again:"
            )
            return

        user_data[uid]["api_id"] = int(text)
        user_data[uid]["state"]  = GET_API_HASH

        await message.reply(
            f"**{label} Session Generator**\n\n"
            "✅ API ID saved!\n\n"
            "**Step 2 of 4 — API Hash**\n\n"
            "Send your **API Hash** *(32-character string)*\n\n"
            "📌 From the same [my.telegram.org/apps](https://my.telegram.org/apps) page",
            reply_markup=cancel_btn(),
            disable_web_page_preview=True
        )

    # ── STEP 2: API HASH ──────────────────────────────────────────────────────
    elif state == GET_API_HASH:
        if len(text) != 32:
            await message.reply(
                "❌ API Hash must be exactly **32 characters**.\n\nTry again:"
            )
            return

        user_data[uid]["api_hash"] = text
        user_data[uid]["state"]    = GET_PHONE

        await message.reply(
            f"**{label} Session Generator**\n\n"
            "✅ API Hash saved!\n\n"
            "**Step 3 of 4 — Phone Number**\n\n"
            "Send your **phone number** with country code\n\n"
            "Example: `+919876543210`",
            reply_markup=cancel_btn()
        )

    # ── STEP 3: PHONE NUMBER ──────────────────────────────────────────────────
    elif state == GET_PHONE:
        phone = text if text.startswith("+") else "+" + text

        api_id   = user_data[uid]["api_id"]
        api_hash = user_data[uid]["api_hash"]

        progress = await message.reply("⏳ Sending OTP to your Telegram...")

        try:
            if stype == "pyrogram":
                # ── Pyrogram client ───────────────────────────────────────────
                pyro = Client(
                    f":memory:",
                    api_id=api_id,
                    api_hash=api_hash,
                    in_memory=True
                )
                await pyro.connect()
                sent = await pyro.send_code(phone)

                user_data[uid]["client"]          = pyro
                user_data[uid]["phone_code_hash"] = sent.phone_code_hash

            else:
                # ── Telethon client ───────────────────────────────────────────
                tele = TelegramClient(StringSession(), api_id, api_hash)
                await tele.connect()
                sent = await tele.send_code_request(phone)

                user_data[uid]["client"]          = tele
                user_data[uid]["phone_code_hash"] = sent.phone_code_hash

            user_data[uid]["phone"] = phone
            user_data[uid]["state"] = GET_OTP

            await progress.edit_text(
                f"**{label} Session Generator**\n\n"
                "✅ OTP sent to your Telegram app!\n\n"
                "**Step 4 of 4 — OTP Code**\n\n"
                "Open your Telegram app → check messages from **Telegram**\n"
                "Send the OTP here\n\n"
                "Format: `12345` or `1 2 3 4 5`",
                reply_markup=cancel_btn()
            )

        except (PhoneNumberInvalid, PhoneNumberInvalidError):
            await progress.edit_text(
                "❌ **Invalid phone number.**\n\n"
                "Make sure to include the country code.\n"
                "Example: `+919876543210`\n\n"
                "Send /start to try again."
            )
            _cleanup(uid)

        except (ApiIdInvalid, ApiIdInvalidError):
            await progress.edit_text(
                "❌ **Invalid API ID or API Hash.**\n\n"
                "Double-check your credentials at "
                "[my.telegram.org](https://my.telegram.org/apps)\n\n"
                "Send /start to try again.",
                disable_web_page_preview=True
            )
            _cleanup(uid)

        except (FloodWait, FloodWaitError) as e:
            wait = getattr(e, "value", getattr(e, "seconds", 60))
            await progress.edit_text(
                f"⏳ **Flood wait!** Telegram asks to wait **{wait} seconds**.\n\n"
                "Send /start and try again after the wait."
            )
            _cleanup(uid)

        except PhoneNumberBanned:
            await progress.edit_text(
                "❌ **This phone number is banned** by Telegram.\n\n"
                "Send /start to try with a different number."
            )
            _cleanup(uid)

        except Exception as e:
            logger.exception("Phone step error")
            await progress.edit_text(
                f"❌ **Unexpected error:**\n`{e}`\n\nSend /start to try again."
            )
            _cleanup(uid)

    # ── STEP 4: OTP ───────────────────────────────────────────────────────────
    elif state == GET_OTP:
        otp             = text.replace(" ", "")
        phone           = user_data[uid]["phone"]
        phone_code_hash = user_data[uid]["phone_code_hash"]
        cli             = user_data[uid]["client"]

        # Auto-delete the OTP message for security
        try:
            await message.delete()
        except Exception:
            pass

        progress = await bot.send_message(uid, "⏳ Verifying OTP...")

        try:
            if stype == "pyrogram":
                await cli.sign_in(phone, phone_code_hash, otp)
                session = await cli.export_session_string()
                await cli.disconnect()
                await _send_session(progress, label, "Pyrogram", session)

            else:
                await cli.sign_in(phone, otp, phone_code_hash=phone_code_hash)
                session = cli.session.save()
                await cli.disconnect()
                await _send_session(progress, label, "Telethon", session)

            user_data.pop(uid, None)

        except SessionPasswordNeeded:
            user_data[uid]["state"] = GET_2FA
            await progress.edit_text(
                f"**{label} Session Generator**\n\n"
                "🔐 **Two-Step Verification (2FA) Enabled**\n\n"
                "Your account has a 2FA cloud password set.\n"
                "Please send your **Telegram 2FA password** below:\n\n"
                "⚠️ *Your message will be auto-deleted for security*",
                reply_markup=cancel_btn()
            )

        except SessionPasswordNeededError:
            user_data[uid]["state"] = GET_2FA
            await progress.edit_text(
                f"**{label} Session Generator**\n\n"
                "🔐 **Two-Step Verification (2FA) Enabled**\n\n"
                "Please send your **Telegram 2FA password**:\n\n"
                "⚠️ *Your message will be auto-deleted for security*",
                reply_markup=cancel_btn()
            )

        except (PhoneCodeInvalid, PhoneCodeInvalidError,
                PhoneCodeExpired, PhoneCodeExpiredError):
            await progress.edit_text(
                "❌ **OTP is invalid or expired.**\n\n"
                "Please send /start and request a new OTP."
            )
            _cleanup(uid)

        except (FloodWait, FloodWaitError) as e:
            wait = getattr(e, "value", getattr(e, "seconds", 60))
            await progress.edit_text(
                f"⏳ **Flood wait!** Please wait **{wait} seconds** then try again."
            )
            _cleanup(uid)

        except Exception as e:
            logger.exception("OTP step error")
            await progress.edit_text(
                f"❌ **Error verifying OTP:**\n`{e}`\n\nSend /start to try again."
            )
            _cleanup(uid)

    # ── STEP 5: 2FA PASSWORD ──────────────────────────────────────────────────
    elif state == GET_2FA:
        password = text
        cli      = user_data[uid]["client"]

        # Auto-delete the password message for security
        try:
            await message.delete()
        except Exception:
            pass

        progress = await bot.send_message(uid, "⏳ Verifying 2FA password...")

        try:
            if stype == "pyrogram":
                await cli.check_password(password)
                session = await cli.export_session_string()
                await cli.disconnect()
                await _send_session(progress, label, "Pyrogram", session)

            else:
                await cli.sign_in(password=password)
                session = cli.session.save()
                await cli.disconnect()
                await _send_session(progress, label, "Telethon", session)

            user_data.pop(uid, None)

        except Exception as e:
            logger.exception("2FA step error")
            await progress.edit_text(
                f"❌ **Wrong 2FA password.**\n`{e}`\n\nSend /start to try again."
            )
            _cleanup(uid)


# ─────────────────────────────────────────────────────────────────────────────
#  Helpers
# ─────────────────────────────────────────────────────────────────────────────

async def _send_session(progress_msg, label: str, lib_name: str, session: str):
    """Edit the progress message to display the generated session string."""
    await progress_msg.edit_text(
        f"**✅ {label} Session Generated Successfully!**\n\n"
        f"**Library:** `{lib_name}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        f"`{session}`\n"
        "━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 **Copy the string above** and paste it into your `config.py`\n\n"
        "⚠️ **Keep this secret!**\n"
        "This string gives **full access** to your Telegram account.\n"
        "Never share it with anyone.\n\n"
        "🔄 Send /start to generate another session."
    )


def _cleanup(uid: int):
    """Disconnect and remove user data."""
    if uid in user_data:
        cli = user_data[uid].get("client")
        if cli:
            try:
                import asyncio
                asyncio.get_event_loop().create_task(cli.disconnect())
            except Exception:
                pass
        user_data.pop(uid, None)
