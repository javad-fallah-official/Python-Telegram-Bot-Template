import os
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base

POSTGRES_URL = os.getenv("POSTGRES_URL")
DATABASE_URL = POSTGRES_URL if POSTGRES_URL else "sqlite+aiosqlite:///./dev.db"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)
Base = declarative_base()

async def get_session():
    async with AsyncSessionLocal() as session:
        yield session

async def init_db():
    from app.db.models.user import User
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
