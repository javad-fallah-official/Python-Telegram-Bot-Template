import asyncio
from typing import Optional, Iterable, Tuple, List
import aioodbc
import pyodbc
from app.config import settings

class MSSQLAdapter:
    _pool: Optional[aioodbc.Pool] = None
    def __init__(self):
        self._timeout = int(getattr(settings, "MSSQL_QUERY_TIMEOUT", 30))

    async def _get_pool(self) -> aioodbc.Pool:
        if self._pool is None:
            dsn = getattr(settings, "MSSQL_DSN", None)
            min_size = int(getattr(settings, "MSSQL_POOL_MIN", 1))
            max_size = int(getattr(settings, "MSSQL_POOL_MAX", 10))
            self._pool = await aioodbc.create_pool(
                dsn=dsn,
                min_size=min_size,
                max_size=max_size,
                loop=asyncio.get_event_loop(),
            )
        return self._pool

    async def execute(self, query: str, params: Optional[Iterable] = None) -> int:
        if bool(getattr(settings, "MSSQL_USE_AIOODBC", True)):
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    return cur.rowcount
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._sync_execute, query, params)

    def _sync_execute(self, query: str, params: Optional[Iterable] = None) -> int:
        dsn = getattr(settings, "MSSQL_DSN", None)
        with pyodbc.connect(dsn, timeout=self._timeout) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                return cur.rowcount

    async def fetchone(self, query: str, params: Optional[Iterable] = None) -> Optional[dict]:
        if bool(getattr(settings, "MSSQL_USE_AIOODBC", True)):
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    row = await cur.fetchone()
                    if row is None:
                        return None
                    cols = [d[0] for d in cur.description]
                    return {cols[i]: row[i] for i in range(len(cols))}
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._sync_fetchone, query, params)

    def _sync_fetchone(self, query: str, params: Optional[Iterable] = None) -> Optional[dict]:
        dsn = getattr(settings, "MSSQL_DSN", None)
        with pyodbc.connect(dsn, timeout=self._timeout) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                row = cur.fetchone()
                if row is None:
                    return None
                cols = [d[0] for d in cur.description]
                return {cols[i]: row[i] for i in range(len(cols))}

    async def fetchall(self, query: str, params: Optional[Iterable] = None) -> List[dict]:
        if bool(getattr(settings, "MSSQL_USE_AIOODBC", True)):
            pool = await self._get_pool()
            async with pool.acquire() as conn:
                async with conn.cursor() as cur:
                    await cur.execute(query, params)
                    rows = await cur.fetchall()
                    if not rows:
                        return []
                    cols = [d[0] for d in cur.description]
                    return [{cols[i]: r[i] for i in range(len(cols))} for r in rows]
        else:
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self._sync_fetchall, query, params)

    def _sync_fetchall(self, query: str, params: Optional[Iterable] = None) -> List[dict]:
        dsn = getattr(settings, "MSSQL_DSN", None)
        with pyodbc.connect(dsn, timeout=self._timeout) as conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
                rows = cur.fetchall()
                if not rows:
                    return []
                cols = [d[0] for d in cur.description]
                return [{cols[i]: r[i] for i in range(len(cols))} for r in rows]

    async def transaction(self):
        if bool(getattr(settings, "MSSQL_USE_AIOODBC", True)):
            pool = await self._get_pool()
            conn = await pool.acquire()
            return _AsyncTransaction(pool, conn)
        else:
            conn = pyodbc.connect(settings.MSSQL_DSN)
            return _SyncTransaction(conn)


class _AsyncTransaction:
    def __init__(self, pool: aioodbc.Pool, conn: aioodbc.Connection):
        self._pool = pool
        self._conn = conn
        self._cur = None

    async def __aenter__(self):
        self._cur = await self._conn.cursor()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self._cur:
            await self._cur.close()
        if self._conn:
            await self._pool.release(self._conn)

    async def execute(self, query: str, params: Optional[Iterable] = None):
        await self._cur.execute(query, params)

    async def commit(self):
        await self._conn.commit()

    async def rollback(self):
        await self._conn.rollback()


class _SyncTransaction:
    def __init__(self, conn: pyodbc.Connection):
        self._conn = conn
        self._cur = None

    def __enter__(self):
        self._cur = self._conn.cursor()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._cur:
            self._cur.close()
        if self._conn:
            self._conn.close()

    def execute(self, query: str, params: Optional[Iterable] = None):
        self._cur.execute(query, params)

    def commit(self):
        self._conn.commit()

    def rollback(self):
        self._conn.rollback()
