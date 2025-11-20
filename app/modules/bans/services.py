from app.db.base import get_session
from app.utils.logger import get_logger
from app.db.models.user import User

logger = get_logger("bans")

async def ban_user(user_id: int):
    async for session in get_session():
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, is_banned=True)
        else:
            user.is_banned = True
        session.add(user)
        try:
            await session.commit()
        except Exception as e:
            logger.error(f"DB error on ban_user: {e}")
            await session.rollback()

async def unban_user(user_id: int):
    async for session in get_session():
        user = await session.get(User, user_id)
        if not user:
            return
        user.is_banned = False
        session.add(user)
        try:
            await session.commit()
        except Exception as e:
            logger.error(f"DB error on unban_user: {e}")
            await session.rollback()
