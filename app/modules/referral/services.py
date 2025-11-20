from sqlalchemy import select
from app.db.models.user import User
from app.db.base import get_session

async def save_referral(user_id: int, referrer_id: int):
    async for session in get_session():
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, referred_by=referrer_id)
            session.add(user)
            await session.commit()
            return
        if user.referred_by is None:
            user.referred_by = referrer_id
            session.add(user)
            await session.commit()
