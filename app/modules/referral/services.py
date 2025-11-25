from app.utils.logger import get_logger
from app.core.db.adapter import db_adapter

logger = get_logger("referral")

async def save_referral(user_id: int, referrer_id: int):
    try:
        row = await db_adapter.fetchone("SELECT referred_by FROM users WHERE id=?", [user_id])
        if row is None:
            await db_adapter.execute("INSERT INTO users (id, referred_by) VALUES (?, ?)", [user_id, referrer_id])
            return
        current = row[0]
        if current is None:
            await db_adapter.execute("UPDATE users SET referred_by=? WHERE id=?", [referrer_id, user_id])
    except Exception as e:
        logger.error(f"DB error on save_referral: {e}")
