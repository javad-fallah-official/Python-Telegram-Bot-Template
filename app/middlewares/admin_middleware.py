from aiogram.dispatcher.middlewares.base import BaseMiddleware
from app.config import settings

class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = getattr(getattr(event, "from_user", None), "id", None)
        data["is_admin"] = bool(user_id in settings.ADMIN_IDS) if user_id else False
        return await handler(event, data)
