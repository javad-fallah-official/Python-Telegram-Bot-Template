import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
from app.utils.logger import get_logger

POSTGRES_URL = settings.POSTGRES_URL
DATABASE_URL = POSTGRES_URL if POSTGRES_URL else "sqlite+aiosqlite:///./dev.db"
logger = get_logger("db")

engine = create_async_engine(DATABASE_URL, echo=bool(getattr(settings, "DEBUG", True)), future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    from app.db.models.user import User
    from app.db.models.sponsor_verification import SponsorVerification
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
