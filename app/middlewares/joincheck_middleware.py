from aiogram import BaseMiddleware
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from app.modules.joincheck.services import ensure_joined, bot_is_admin, verify_membership, record_enforcement_message
from app.config import settings
from app.utils.logger import get_logger
from app.core.db.models.sponsor_verification import SponsorVerification
import time

class JoinCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        original = self._unwrap(handler)
        enforce = bool(getattr(settings, "SPONSOR_ENFORCE", True)) and bool(getattr(settings.FEATURES, "join_check", True))
        if not enforce:
            return await handler(event, data)
        user_id = getattr(getattr(event, "from_user", None), "id", None)
        if user_id and user_id in getattr(settings, "ADMIN_IDS", []):
            return await handler(event, data)
        if hasattr(event, "data") and getattr(event, "data", "") == "verify_sponsor_join":
            return await handler(event, data)
        if not user_id:
            return await handler(event, data)
        bot = data.get("bot")
        channels = list(getattr(settings, "REQUIRED_CHANNELS", []))
        if not channels:
            return await handler(event, data)
        for ch in channels:
            admin_ok = await bot_is_admin(bot, ch)
            if not admin_ok:
                text = "⚠️ The bot lacks permission to check membership in {}".format(ch)
                kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=f"🔗 Join {ch}", url=f"https://t.me/{ch.lstrip('@')}"),],[InlineKeyboardButton(text="✅ Verify Membership", callback_data="verify_sponsor_join")]])
                if isinstance(event, Message):
                    msg = await event.answer(text, reply_markup=kb)
                    try:
                        record_enforcement_message(msg.chat.id, event.from_user.id, msg.message_id)
                    except Exception:
                        pass
                return
        ok = await ensure_joined(bot, user_id)
        if ok:
            return await handler(event, data)
        passed, missing = await verify_membership(bot, user_id, channels)
        lines = ["🛡️ Join Sponsor Channels", "", getattr(settings, "JOIN_PROMPT_TEXT", "Please join the required channels")]
        kb_rows = []
        for ck in missing:
            kb_rows.append([InlineKeyboardButton(text=f"🔗 Join @{ck}", url=f"https://t.me/{ck}")])
        kb_rows.append([InlineKeyboardButton(text="✅ Verify Membership", callback_data="verify_sponsor_join")])
        kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
        if isinstance(event, Message):
            msg = await event.answer("\n".join(lines), reply_markup=kb)
            try:
                record_enforcement_message(msg.chat.id, event.from_user.id, msg.message_id)
            except Exception:
                pass
        await self._log_verification(user_id, missing, passed)
        return

    def _unwrap(self, func):
        seen = set()
        while hasattr(func, "__wrapped__") and func not in seen:
            seen.add(func)
            func = getattr(func, "__wrapped__")
        return func

    async def _log_verification(self, user_id: int, missing: list[str], passed: bool):
        try:
            await SponsorVerification.create(user_id, (",".join(missing) if missing else None), "all", passed)
        except Exception:
            return
