import asyncpg
from typing import Optional, Iterable, Tuple, List
from app.config import settings

def _convert_placeholders(query: str, params_len: int) -> str:
    out = []
    idx = 0
    arg = 1
    while idx < len(query):
        if query[idx] == '?' and arg <= params_len:
            out.append(f"${arg}")
            arg += 1
            idx += 1
        else:
            out.append(query[idx])
            idx += 1
    return ''.join(out)

class PostgresAdapter:
    def __init__(self):
        host = getattr(settings, "POSTGRES_HOST", "localhost")
        port = int(getattr(settings, "POSTGRES_PORT", 5432))
        db = getattr(settings, "POSTGRES_DB", "aiogram_db")
        user = getattr(settings, "POSTGRES_USER", "postgres")
        pwd = getattr(settings, "POSTGRES_PASS", "password")
        self._dsn = f"postgresql://{user}:{pwd}@{host}:{port}/{db}"
        self._pool: Optional[asyncpg.Pool] = None

    async def init(self):
        if self._pool is None:
            self._pool = await asyncpg.create_pool(dsn=self._dsn, min_size=1, max_size=10)

    async def close(self):
        if self._pool:
            await self._pool.close()
            self._pool = None

    async def execute(self, query: str, params: Optional[Iterable] = None) -> int:
        await self.init()
        params = list(params or [])
        q = _convert_placeholders(query, len(params))
        async with self._pool.acquire() as conn:
            res = await conn.execute(q, *params)
            try:
                return int(res.split()[-1])
            except Exception:
                return 0

    async def fetchone(self, query: str, params: Optional[Iterable] = None) -> Optional[dict]:
        await self.init()
        params = list(params or [])
        q = _convert_placeholders(query, len(params))
        async with self._pool.acquire() as conn:
            row = await conn.fetchrow(q, *params)
            return dict(row) if row else None

    async def fetchall(self, query: str, params: Optional[Iterable] = None) -> List[dict]:
        await self.init()
        params = list(params or [])
        q = _convert_placeholders(query, len(params))
        async with self._pool.acquire() as conn:
            rows = await conn.fetch(q, *params)
            return [dict(r) for r in rows]

    async def transaction(self):
        await self.init()
        return _PgTransaction(self._pool)


class _PgTransaction:
    def __init__(self, pool: asyncpg.Pool):
        self._pool = pool
        self._conn: Optional[asyncpg.Connection] = None
        self._tx = None

    async def __aenter__(self):
        self._conn = await self._pool.acquire()
        self._tx = self._conn.transaction()
        await self._tx.start()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        try:
            if exc_type:
                await self._tx.rollback()
            else:
                await self._tx.commit()
        finally:
            if self._conn:
                await self._pool.release(self._conn)
