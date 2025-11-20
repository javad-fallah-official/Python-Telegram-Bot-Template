from app.db.base import get_session
from app.db.models.user import User

async def ban_user(user_id: int):
    async for session in get_session():
        user = await session.get(User, user_id)
        if not user:
            user = User(id=user_id, is_banned=True)
        else:
            user.is_banned = True
        session.add(user)
        await session.commit()

async def unban_user(user_id: int):
    async for session in get_session():
        user = await session.get(User, user_id)
        if not user:
            return
        user.is_banned = False
        session.add(user)
        await session.commit()
