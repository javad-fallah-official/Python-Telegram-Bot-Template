
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

db_adapter = DatabaseAdapter()

async def init_db_adapter():
    if hasattr(db_adapter, 'init'):
        await db_adapter.init()

async def close_db_adapter():
    if hasattr(db_adapter, 'close'):
        await db_adapter.close()

def _transform(sql: str, params: dict | None):
    if not params:
        return sql, []
    import re
    names = re.findall(r":([A-Za-z_][A-Za-z0-9_]*)", sql)
    if db_type == 'postgres':
        uniq = []
        for n in names:
            uniq.append(n)
        placeholders = {}
        i = 1
        for n in uniq:
            placeholders[n] = f"${i}"
            i += 1
        sql2 = sql
        for n in uniq:
            sql2 = sql2.replace(f":{n}", placeholders[n])
        ordered = [params.get(n) for n in uniq]
        return sql2, ordered
    else:
        ordered = [params.get(n) for n in names]
        sql2 = sql
        for _ in names:
            sql2 = sql2.replace(f":{_}", "?")
        return sql2, ordered

async def execute(sql: str, params: dict | None = None) -> int:
    s, p = _transform(sql, params)
    return await db_adapter.execute(s, p)

async def fetchone(sql: str, params: dict | None = None):
    s, p = _transform(sql, params)
    return await db_adapter.fetchone(s, p)

async def fetchall(sql: str, params: dict | None = None):
    s, p = _transform(sql, params)
    return await db_adapter.fetchall(s, p)

async def list_tables() -> list[str]:
    if db_type == 'sqlite':
        rows = await fetchall("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        return [str(r.get('name')) for r in rows]
    if db_type == 'postgres':
        rows = await fetchall("SELECT table_name FROM information_schema.tables WHERE table_schema='public' ORDER BY table_name")
        return [str(r.get('table_name')) for r in rows]
    if db_type == 'mssql':
        rows = await fetchall("SELECT name FROM sys.tables ORDER BY name")
        return [str(r.get('name')) for r in rows]
    return []

async def get_table_schema(table: str) -> dict[str, str]:
    if db_type == 'sqlite':
        rows = await fetchall("PRAGMA table_info(:t)", {"t": table})
        out: dict[str, str] = {}
        for r in rows:
            out[str(r.get('name'))] = str(r.get('type'))
        return out
    if db_type == 'postgres':
        rows = await fetchall(
            "SELECT column_name,data_type FROM information_schema.columns WHERE table_schema='public' AND table_name=:t ORDER BY ordinal_position",
            {"t": table},
        )
        return {str(r.get('column_name')): str(r.get('data_type')) for r in rows}
    if db_type == 'mssql':
        rows = await fetchall(
            "SELECT c.name AS column_name, t.name AS data_type FROM sys.columns c JOIN sys.types t ON c.user_type_id=t.user_type_id WHERE c.object_id=OBJECT_ID(:t) ORDER BY c.column_id",
            {"t": table},
        )
        return {str(r.get('column_name')): str(r.get('data_type')) for r in rows}
    return {}

async def drop_all_tables() -> None:
    tables = await list_tables()
    if db_type == 'postgres':
        for t in tables:
            await db_adapter.execute(f"DROP TABLE IF EXISTS public.{t} CASCADE")
    elif db_type == 'sqlite':
        for t in tables:
            await db_adapter.execute(f"DROP TABLE IF EXISTS {t}")
    elif db_type == 'mssql':
        for t in tables:
            await db_adapter.execute(f"IF OBJECT_ID('{t}','U') IS NOT NULL DROP TABLE {t}")

async def clear_all_tables() -> None:
    tables = await list_tables()
    for t in tables:
        await db_adapter.execute(f"DELETE FROM {t}")
