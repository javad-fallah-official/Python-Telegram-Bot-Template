from sqlalchemy import select
from app.utils.logger import get_logger
from app.db.models.user import User
from app.db.base import get_session

logger = get_logger("referral")

async def save_referral(user_id: int, referrer_id: int):
    async for session in get_session():
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, referred_by=referrer_id)
            session.add(user)
            try:
                await session.commit()
            except Exception as e:
                logger.error(f"DB error on save_referral (create): {e}")
                await session.rollback()
            return
        if user.referred_by is None:
            user.referred_by = referrer_id
            session.add(user)
            try:
                await session.commit()
            except Exception as e:
                logger.error(f"DB error on save_referral (update): {e}")
                await session.rollback()
