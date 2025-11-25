
from app.config import settings

if settings.DB_TYPE == 'mssql':
    from app.core.db.mssql import MSSQLAdapter as DatabaseAdapter
elif settings.DB_TYPE == 'postgres' or settings.DB_TYPE == 'sqlite':
    # Placeholder for existing SQLAlchemy implementation
    from app.core.db.sqlalchemy_impl import SQLAlchemyAdapter as DatabaseAdapter
else:
    raise ImportError(f'Unsupported DB_TYPE: {settings.DB_TYPE}')

db_adapter = DatabaseAdapter()

async def init_db_adapter():
    # This function will be called at bot startup
    pass

async def close_db_adapter():
    # This function will be called at bot shutdown
    if hasattr(db_adapter, 'close'):
        await db_adapter.close()
