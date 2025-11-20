from aiogram import BaseMiddleware
from aiogram.types import Message
from app.modules.joincheck.services import ensure_joined
from app.config import settings

class JoinCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        original = self._unwrap(handler)
        if not (getattr(handler, "require_join", False) or getattr(original, "require_join", False)):
            return await handler(event, data)
        user_id = getattr(getattr(event, "from_user", None), "id", None)
        if not user_id:
            return await handler(event, data)
        bot = data.get("bot")
        ok = await ensure_joined(bot, user_id)
        if ok:
            return await handler(event, data)
        prompt = getattr(settings, "JOIN_PROMPT_TEXT", "Please join required channels")
        if isinstance(event, Message):
            await event.answer(prompt)
        return

    def _unwrap(self, func):
        seen = set()
        while hasattr(func, "__wrapped__") and func not in seen:
            seen.add(func)
            func = getattr(func, "__wrapped__")
        return func
