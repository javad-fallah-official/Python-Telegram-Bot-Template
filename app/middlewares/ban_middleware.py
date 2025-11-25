from aiogram import BaseMiddleware
from app.core.db.adapter import db_adapter

class BanMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        user_id = getattr(getattr(event, "from_user", None), "id", None)
        if not user_id:
            return await handler(event, data)
        try:
            row = await db_adapter.fetchone("SELECT is_banned FROM users WHERE id=?", [user_id])
            if row and bool(row[0]):
                return
        except Exception:
            pass
        return await handler(event, data)
