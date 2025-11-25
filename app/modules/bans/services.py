from app.core.db.adapter import db_adapter
from app.utils.logger import get_logger

logger = get_logger("bans")

async def ban_user(user_id: int):
    try:
        row = await db_adapter.fetchone("SELECT id FROM users WHERE id=?", [user_id])
        if row is None:
            await db_adapter.execute("INSERT INTO users (id, is_banned) VALUES (?, ?)", [user_id, True])
        else:
            await db_adapter.execute("UPDATE users SET is_banned=? WHERE id=?", [True, user_id])
    except Exception as e:
        logger.error(f"DB error on ban_user: {e}")

async def unban_user(user_id: int):
    try:
        row = await db_adapter.fetchone("SELECT id FROM users WHERE id=?", [user_id])
        if row is None:
            return
        await db_adapter.execute("UPDATE users SET is_banned=? WHERE id=?", [False, user_id])
    except Exception as e:
        logger.error(f"DB error on unban_user: {e}")
