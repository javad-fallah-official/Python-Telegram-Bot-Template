
from app.config import settings

db_type = str(getattr(settings, "DB_TYPE", "sqlite")).lower()
if db_type == 'sqlite':
    from app.core.db.engines.sqlite import SqliteAdapter as DatabaseAdapter
elif db_type == 'postgres':
    from app.core.db.engines.postgres import PostgresAdapter as DatabaseAdapter
elif db_type == 'mssql':
    from app.core.db.engines.mssql import MSSQLAdapter as DatabaseAdapter
elif db_type == 'none':
    from app.core.db.engines.disabled import DisabledAdapter as DatabaseAdapter
else:
    raise ImportError(f'Unsupported DB_TYPE: {db_type}')

db_adapter = DatabaseAdapter()

async def init_db_adapter():
    if hasattr(db_adapter, 'init'):
        await db_adapter.init()

async def close_db_adapter():
    if hasattr(db_adapter, 'close'):
        await db_adapter.close()
