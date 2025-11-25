from typing import Optional, Iterable, Tuple, List

class DBDisabledError(Exception):
    pass

class DisabledAdapter:
    async def init(self):
        return None

    async def close(self):
        return None

    async def execute(self, query: str, params: Optional[Iterable] = None) -> int:
        raise DBDisabledError("Database is disabled (DB_TYPE=none)")

    async def fetchone(self, query: str, params: Optional[Iterable] = None) -> Optional[Tuple]:
        raise DBDisabledError("Database is disabled (DB_TYPE=none)")

    async def fetchall(self, query: str, params: Optional[Iterable] = None) -> List[Tuple]:
        raise DBDisabledError("Database is disabled (DB_TYPE=none)")

    async def transaction(self):
        raise DBDisabledError("Database is disabled (DB_TYPE=none)")
