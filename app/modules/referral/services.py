from app.utils.logger import get_logger
from app.core.db.models.user import User

logger = get_logger("referral")

async def save_referral(user_id: int, referrer_id: int):
    try:
        await User.set_referral(user_id, referrer_id)
    except Exception as e:
        logger.error(f"DB error on save_referral: {e}")
