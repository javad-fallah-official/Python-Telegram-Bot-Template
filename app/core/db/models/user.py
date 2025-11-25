from typing import Optional, Dict, Any
from app.core.db.orm.base_model import BaseModel
from app.core.db.adapter import db_adapter

class User(BaseModel):
    table_name = "users"
    pk = "id"

    @classmethod
    async def ban(cls, user_id: int) -> None:
        row = await db_adapter.fetchone("SELECT id FROM users WHERE id=?", [user_id])
        if row is None:
            await db_adapter.execute("INSERT INTO users (id, is_banned) VALUES (?, ?)", [user_id, True])
        else:
            await db_adapter.execute("UPDATE users SET is_banned=? WHERE id=?", [True, user_id])

    @classmethod
    async def unban(cls, user_id: int) -> None:
        row = await db_adapter.fetchone("SELECT id FROM users WHERE id=?", [user_id])
        if row is None:
            return
        await db_adapter.execute("UPDATE users SET is_banned=? WHERE id=?", [False, user_id])

    @classmethod
    async def set_referral(cls, user_id: int, referrer_id: int) -> None:
        row = await db_adapter.fetchone("SELECT referred_by FROM users WHERE id=?", [user_id])
        if row is None:
            await db_adapter.execute("INSERT INTO users (id, referred_by) VALUES (?, ?)", [user_id, referrer_id])
            return
        current = row[0]
        if current is None:
            await db_adapter.execute("UPDATE users SET referred_by=? WHERE id=?", [referrer_id, user_id])
