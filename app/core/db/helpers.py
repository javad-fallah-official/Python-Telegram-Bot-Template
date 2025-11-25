from app.config import settings
from app.core.db.adapter import db_adapter

async def ensure_schema():
    db_type = str(getattr(settings, "DB_TYPE", "sqlite")).lower()
    try:
        if db_type == "sqlite":
            await db_adapter.execute(
                "CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY, username TEXT NULL, is_admin BOOLEAN NOT NULL DEFAULT 0, is_banned BOOLEAN NOT NULL DEFAULT 0, referred_by BIGINT NULL)"
            )
            await db_adapter.execute(
                "CREATE TABLE IF NOT EXISTS sponsor_verifications (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id BIGINT NOT NULL, channels_missing TEXT NULL, policy TEXT NOT NULL, success BOOLEAN NOT NULL)"
            )
        elif db_type == "postgres":
            await db_adapter.execute(
                "CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY, username TEXT NULL, is_admin BOOLEAN NOT NULL DEFAULT FALSE, is_banned BOOLEAN NOT NULL DEFAULT FALSE, referred_by BIGINT NULL)"
            )
            await db_adapter.execute(
                "CREATE TABLE IF NOT EXISTS sponsor_verifications (id SERIAL PRIMARY KEY, user_id BIGINT NOT NULL, channels_missing TEXT NULL, policy TEXT NOT NULL, success BOOLEAN NOT NULL)"
            )
        elif db_type == "mssql":
            await db_adapter.execute(
                "IF OBJECT_ID('dbo.users','U') IS NULL CREATE TABLE dbo.users (id BIGINT PRIMARY KEY, username NVARCHAR(255) NULL, is_admin BIT NOT NULL DEFAULT 0, is_banned BIT NOT NULL DEFAULT 0, referred_by BIGINT NULL)"
            )
            await db_adapter.execute(
                "IF OBJECT_ID('dbo.sponsor_verifications','U') IS NULL CREATE TABLE dbo.sponsor_verifications (id INT IDENTITY(1,1) PRIMARY KEY, user_id BIGINT NOT NULL, channels_missing NVARCHAR(255) NULL, policy NVARCHAR(50) NOT NULL, success BIT NOT NULL)"
            )
    except Exception:
        return
