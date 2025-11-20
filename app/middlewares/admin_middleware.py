from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from app.config import settings
import re

class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        original = self._unwrap(handler)
        user_id = getattr(getattr(event, "from_user", None), "id", None)
        is_admin = bool(user_id in settings.ADMIN_IDS) if user_id else False
        data["is_admin"] = is_admin
        requires_admin = bool(getattr(handler, "admin_only", False) or getattr(original, "admin_only", False))
        mod = getattr(original, "__module__", "")
        requires_admin_module = mod.startswith("app.modules.admin")
        requires_admin_command = False
        if isinstance(event, Message):
            text = getattr(event, "text", "") or ""
            requires_admin_command = bool(re.match(r"^/admin(\b|@|$)", text))
        if (requires_admin or requires_admin_module or requires_admin_command) and not is_admin:
            await self._handle_unauthorized_user(event)
            return
        return await handler(event, data)

    async def _handle_unauthorized_user(self, event):
        unauthorized_message = (
            "🚫 <b>Access Denied</b>\n\n"
            "You don't have permission to use this command.\n"
            "This feature is restricted to administrators only.\n\n"
            "If you believe this is an error, please contact the bot administrators."
        )
        try:
            if isinstance(event, Message):
                await event.answer(unauthorized_message, parse_mode="HTML")
            elif isinstance(event, CallbackQuery):
                await event.answer("🚫 Access denied - Admin privileges required", show_alert=True)
                try:
                    await event.message.edit_text(unauthorized_message, parse_mode="HTML")
                except Exception:
                    await event.message.answer(unauthorized_message, parse_mode="HTML")
        except Exception:
            return

    def _unwrap(self, func):
        seen = set()
        while hasattr(func, "__wrapped__") and func not in seen:
            seen.add(func)
            func = getattr(func, "__wrapped__")
        return func
