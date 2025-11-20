from aiogram.dispatcher.middlewares.base import BaseMiddleware
from app.db.base import get_session
from app.db.models.user import User

class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = getattr(getattr(event, "from_user", None), "id", None)
        if not user_id:
            return await handler(event, data)
        async for session in get_session():
            user = await session.get(User, user_id)
            if user and user.is_banned:
                return
        return await handler(event, data)
