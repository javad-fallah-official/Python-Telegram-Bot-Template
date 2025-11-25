from typing import Any, Dict, Optional
from app.core.db.adapter import db_adapter

class BaseModel:
    table_name: str = ""
    pk: str = "id"

    @classmethod
    async def get(cls, pk_value: Any) -> Optional[Dict[str, Any]]:
        row = await db_adapter.fetchone(f"SELECT * FROM {cls.table_name} WHERE {cls.pk}=?", [pk_value])
        if row is None:
            return None
        return cls._row_to_dict(row)

    @classmethod
    async def exists(cls, **where) -> bool:
        cols = list(where.keys())
        vals = list(where.values())
        cond = " AND ".join([f"{c}=?" for c in cols])
        row = await db_adapter.fetchone(f"SELECT 1 FROM {cls.table_name} WHERE {cond} LIMIT 1", vals)
        return row is not None

    @classmethod
    async def create(cls, **fields) -> int:
        cols = list(fields.keys())
        vals = list(fields.values())
        placeholders = ", ".join(["?" for _ in cols])
        collist = ", ".join(cols)
        return await db_adapter.execute(f"INSERT INTO {cls.table_name} ({collist}) VALUES ({placeholders})", vals)

    @classmethod
    async def update(cls, pk_value: Any, **fields) -> int:
        cols = list(fields.keys())
        vals = list(fields.values())
        setexpr = ", ".join([f"{c}=?" for c in cols])
        return await db_adapter.execute(f"UPDATE {cls.table_name} SET {setexpr} WHERE {cls.pk}=?", vals + [pk_value])

    @classmethod
    async def delete(cls, pk_value: Any) -> int:
        return await db_adapter.execute(f"DELETE FROM {cls.table_name} WHERE {cls.pk}=?", [pk_value])

    @classmethod
    def _row_to_dict(cls, row) -> Dict[str, Any]:
        return {"id": row[0], "username": row[1] if len(row) > 1 else None}
