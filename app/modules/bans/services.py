from app.utils.logger import get_logger
from app.core.db.models.user import User

logger = get_logger("bans")

async def ban_user(user_id: int):
    try:
        await User.ban(user_id)
    except Exception as e:
        logger.error(f"DB error on ban_user: {e}")

async def unban_user(user_id: int):
    try:
        await User.unban(user_id)
    except Exception as e:
        logger.error(f"DB error on unban_user: {e}")
