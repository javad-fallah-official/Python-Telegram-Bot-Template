from typing import Any, Dict, Optional, List
from app.core.db import adapter as adp

class BaseModel:
    table_name: str = ""
    pk: str = "id"

    @classmethod
    async def get(cls, **filters) -> Optional[Dict[str, Any]]:
        rows = await cls.select(filters=filters, limit=1)
        return rows[0] if rows else None

    @classmethod
    async def exists(cls, **where) -> bool:
        rows = await cls.select(filters=where, columns=["1"], limit=1)
        return len(rows) > 0

    @classmethod
    async def insert(cls, values: Dict[str, Any]) -> int:
        cols = list(values.keys())
        collist = ", ".join(cols)
        placeholders = ", ".join([f":{c}" for c in cols])
        return await adp.execute(f"INSERT INTO {cls.table_name} ({collist}) VALUES ({placeholders})", values)

    @classmethod
    async def update(cls, filters: Dict[str, Any], values: Dict[str, Any]) -> int:
        setexpr = ", ".join([f"{c} = :{c}" for c in values.keys()])
        cond = " AND ".join([f"{c} = :{c}" for c in filters.keys()])
        params = {**values, **filters}
        return await adp.execute(f"UPDATE {cls.table_name} SET {setexpr} WHERE {cond}", params)

    @classmethod
    async def delete(cls, filters: Dict[str, Any]) -> int:
        cond = " AND ".join([f"{c} = :{c}" for c in filters.keys()])
        return await adp.execute(f"DELETE FROM {cls.table_name} WHERE {cond}", filters)

    @classmethod
    @classmethod
    async def select(cls, filters: Optional[Dict[str, Any]] = None, columns: Optional[List[str]] = None, limit: Optional[int] = None, order_by: Optional[str] = None) -> List[Dict[str, Any]]:
        cols = "*" if not columns else ", ".join(columns)
        where_sql = ""
        params: Dict[str, Any] = {}
        if filters:
            where_sql = " WHERE " + " AND ".join([f"{c} = :{c}" for c in filters.keys()])
            params.update(filters)
        order_sql = f" ORDER BY {order_by}" if order_by else ""
        limit_sql = f" LIMIT :_limit" if limit is not None else ""
        if limit is not None:
            params["_limit"] = int(limit)
        sql = f"SELECT {cols} FROM {cls.table_name}{where_sql}{order_sql}{limit_sql}"
        return await adp.fetchall(sql, params)
