import aiosqlite
import os
from typing import Optional, Iterable, Tuple, List
from app.config import settings

class SqliteAdapter:
    def __init__(self):
        self._path = getattr(settings, "SQLITE_PATH", "./data/bot.db")
        self._conn: Optional[aiosqlite.Connection] = None

    async def init(self):
        if self._conn is None:
            dir_path = os.path.dirname(self._path)
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)
            self._conn = await aiosqlite.connect(self._path)
            await self._conn.execute("PRAGMA journal_mode=WAL;")
            await self._conn.execute("PRAGMA foreign_keys=ON;")
            await self._conn.commit()

    async def close(self):
        if self._conn:
            await self._conn.close()
            self._conn = None

    async def execute(self, query: str, params: Optional[Iterable] = None) -> int:
        await self.init()
        async with self._conn.execute(query, params or []) as cur:
            await self._conn.commit()
            return cur.rowcount or 0

    async def fetchone(self, query: str, params: Optional[Iterable] = None) -> Optional[Tuple]:
        await self.init()
        async with self._conn.execute(query, params or []) as cur:
            return await cur.fetchone()

    async def fetchall(self, query: str, params: Optional[Iterable] = None) -> List[Tuple]:
        await self.init()
        async with self._conn.execute(query, params or []) as cur:
            rows = await cur.fetchall()
            return rows or []

    async def transaction(self):
        await self.init()
        return _SqliteTransaction(self._conn)


class _SqliteTransaction:
    def __init__(self, conn: aiosqlite.Connection):
        self._conn = conn

    async def __aenter__(self):
        await self._conn.execute("BEGIN")
        return self

    async def __aexit__(self, exc_type, exc, tb):
        if exc_type:
            await self._conn.execute("ROLLBACK")
        else:
            await self._conn.execute("COMMIT")
