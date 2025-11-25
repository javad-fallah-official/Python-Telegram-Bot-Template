import asyncio
import os
import unittest

os.environ["DB_TYPE"] = os.environ.get("DB_TYPE", "sqlite")

from app.core.db.adapter import db_adapter, init_db_adapter, close_db_adapter

class TestAdapterBasic(unittest.TestCase):
    def test_execute_fetch_cycle(self):
        async def run():
            await init_db_adapter()
            await db_adapter.execute("CREATE TABLE IF NOT EXISTS unit_test_kv (k TEXT PRIMARY KEY, v TEXT)")
            await db_adapter.execute("INSERT INTO unit_test_kv (k, v) VALUES (?, ?)", ["foo", "bar"])
            row = await db_adapter.fetchone("SELECT v FROM unit_test_kv WHERE k=?", ["foo"])
            self.assertIsNotNone(row)
            self.assertEqual(row[0], "bar")
            rows = await db_adapter.fetchall("SELECT k, v FROM unit_test_kv")
            self.assertTrue(len(rows) >= 1)
            await db_adapter.execute("DROP TABLE unit_test_kv")
            await close_db_adapter()
        asyncio.run(run())

if __name__ == "__main__":
    unittest.main()
