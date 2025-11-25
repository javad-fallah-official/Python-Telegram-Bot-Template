from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
from app.core.db.adapter import db_adapter
from app.utils.logger import get_logger

logger = get_logger("db")
db_type = str(getattr(settings, "DB_TYPE", "sqlite")).lower()
POSTGRES_URL = getattr(settings, "POSTGRES_URL", None)

engine = None
AsyncSessionLocal = None
Base = declarative_base()

if db_type == "postgres":
    url = POSTGRES_URL
    if not url:
        host = getattr(settings, "POSTGRES_HOST", "localhost")
        port = int(getattr(settings, "POSTGRES_PORT", 5432))
        db = getattr(settings, "POSTGRES_DB", "aiogram_db")
        user = getattr(settings, "POSTGRES_USER", "postgres")
        pwd = getattr(settings, "POSTGRES_PASS", "password")
        url = f"postgresql+asyncpg://{user}:{pwd}@{host}:{port}/{db}"
    engine = create_async_engine(url, echo=bool(getattr(settings, "DEBUG", True)), future=True)
    AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

async def get_session():
    if AsyncSessionLocal is None:
        return
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    if db_type == "postgres":
        from app.db.models.user import User
        from app.db.models.sponsor_verification import SponsorVerification
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        return
    if db_type in ("sqlite", "mssql"):
        try:
            await db_adapter.execute(
                "CREATE TABLE IF NOT EXISTS users (id BIGINT PRIMARY KEY, username TEXT NULL, is_admin BOOLEAN NOT NULL DEFAULT 0, is_banned BOOLEAN NOT NULL DEFAULT 0, referred_by BIGINT NULL)"
                if db_type == "sqlite"
                else "IF OBJECT_ID('dbo.users','U') IS NULL CREATE TABLE dbo.users (id BIGINT PRIMARY KEY, username NVARCHAR(255) NULL, is_admin BIT NOT NULL DEFAULT 0, is_banned BIT NOT NULL DEFAULT 0, referred_by BIGINT NULL)"
            )
        except Exception:
            pass
        try:
            await db_adapter.execute(
                "CREATE TABLE IF NOT EXISTS sponsor_verifications (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id BIGINT NOT NULL, channels_missing TEXT NULL, policy TEXT NOT NULL, success BOOLEAN NOT NULL)"
                if db_type == "sqlite"
                else "IF OBJECT_ID('dbo.sponsor_verifications','U') IS NULL CREATE TABLE dbo.sponsor_verifications (id INT IDENTITY(1,1) PRIMARY KEY, user_id BIGINT NOT NULL, channels_missing NVARCHAR(255) NULL, policy NVARCHAR(50) NOT NULL, success BIT NOT NULL)"
            )
        except Exception:
            pass
