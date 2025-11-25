
import asyncio
import unittest
from app.core.db.adapter import db_adapter

class TestDatabaseAdapter(unittest.TestCase):

    def test_execute(self):
        async def run_test():
            # This is a simple test that assumes the database is running and accessible.
            # In a real-world scenario, you would want to use a dedicated test database.
            result = await db_adapter.execute("CREATE TABLE test (id INT)")
            self.assertGreaterEqual(result, 0)
            result = await db_adapter.execute("DROP TABLE test")
            self.assertGreaterEqual(result, 0)

        asyncio.run(run_test())

    def test_fetchone(self):
        async def run_test():
            await db_adapter.execute("CREATE TABLE test (id INT)")
            await db_adapter.execute("INSERT INTO test VALUES (1)")
            result = await db_adapter.fetchone("SELECT * FROM test")
            self.assertEqual(result[0], 1)
            await db_adapter.execute("DROP TABLE test")

        asyncio.run(run_test())

    def test_fetchall(self):
        async def run_test():
            await db_adapter.execute("CREATE TABLE test (id INT)")
            await db_adapter.execute("INSERT INTO test VALUES (1)")
            await db_adapter.execute("INSERT INTO test VALUES (2)")
            result = await db_adapter.fetchall("SELECT * FROM test")
            self.assertEqual(len(result), 2)
            await db_adapter.execute("DROP TABLE test")

        asyncio.run(run_test())

if __name__ == '__main__':
    unittest.main()
