from app.core.db.adapter import db_adapter

class SponsorVerification:
    @classmethod
    async def create(cls, user_id: int, channels_missing: str | None, policy: str, success: bool) -> None:
        await db_adapter.execute(
            "INSERT INTO sponsor_verifications (user_id, channels_missing, policy, success) VALUES (?, ?, ?, ?)",
            [user_id, channels_missing, policy, success],
        )
