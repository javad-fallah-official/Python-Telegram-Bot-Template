from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.config import settings
from app.modules.joincheck.services import verify_membership, record_enforcement_message, cleanup_enforcement_messages
from app.core.db.models.sponsor_verification import SponsorVerification
from app.core.db.adapter import db_adapter

async def verify_sponsor_join(call: CallbackQuery):
    bot = call.bot
    user = call.from_user
    channels = list(getattr(settings, "REQUIRED_CHANNELS", []))
    if not user or not channels:
        await call.answer("Nothing to verify")
        return
    passed, missing = await verify_membership(bot, user.id, channels, fresh=True)
    try:
        await SponsorVerification.create(user.id, (",".join([m.lstrip("@") for m in missing]) if missing else None), "all", passed)
    except Exception:
        pass
    if passed:
        await call.answer("✅ Your membership has been confirmed.", show_alert=True)
        try:
            await call.message.delete()
        except Exception:
            pass
        try:
            await cleanup_enforcement_messages(call.bot, call.message.chat.id, call.from_user.id)
        except Exception:
            pass
        return
    kb_rows = []
    for ck in missing:
        ck = ck.lstrip("@")
        kb_rows.append([InlineKeyboardButton(text=f"🔗 Join @{ck}", url=f"https://t.me/{ck}")])
    kb_rows.append([InlineKeyboardButton(text="✅ Verify Membership", callback_data="verify_sponsor_join")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    msg = await call.message.answer("❌ You have not joined all required channels yet.", reply_markup=kb)
    try:
        record_enforcement_message(msg.chat.id, call.from_user.id, msg.message_id)
    except Exception:
        pass
