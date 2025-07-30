"""
Example demonstrating PostgreSQL usage with the bot template.

This example shows how to:
1. Configure PostgreSQL connection using DATABASE_TYPE
2. Use advanced PostgreSQL features
3. Perform analytics and metrics tracking
4. Handle connection pooling
5. Switch between SQLite and PostgreSQL
"""

import asyncio
import logging
import os
from core.config import Config
from core.db_factory import UnifiedDatabase, DatabaseFactory
from core.postgres import PostgreSQLDatabase

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def database_configuration_example():
    """Demonstrate different ways to configure the database."""
    print("=== Database Configuration Examples ===")
    
    # Method 1: Using DATABASE_TYPE environment variable (recommended)
    print("\n1. Using DATABASE_TYPE environment variable:")
    print("   Set in .env file:")
    print("   DATABASE_TYPE=postgresql")
    print("   DATABASE_URL=postgresql://user:pass@localhost:5432/botdb")
    print("   - OR -")
    print("   DATABASE_TYPE=sqlite")
    print("   DATABASE_URL=bot.db")
    
    # Method 2: Auto-detection from URL
    print("\n2. Auto-detection from DATABASE_URL:")
    print("   DATABASE_TYPE=auto (or omit)")
    print("   DATABASE_URL=postgresql://... -> PostgreSQL")
    print("   DATABASE_URL=bot.db -> SQLite")
    
    # Method 3: Force override
    print("\n3. Force override (useful for testing):")
    print("   DATABASE_TYPE=sqlite")
    print("   DATABASE_URL=postgresql://... -> Still uses SQLite!")
    
    # Show current configuration
    print(f"\nCurrent configuration:")
    print(f"   DATABASE_TYPE: {Config.DATABASE_TYPE}")
    print(f"   DATABASE_URL: {Config.DATABASE_URL}")
    print(f"   Detected type: {DatabaseFactory.get_database_type()}")


async def postgresql_example():
    """Demonstrate PostgreSQL features."""
    
    # Example 1: Using UnifiedDatabase (recommended)
    print("\n=== Example 1: Unified Database Interface ===")
    
    # This will use the database type specified by DATABASE_TYPE or auto-detect from URL
    db = UnifiedDatabase()
    
    try:
        # Connect with connection pooling
        await db.connect()
        
        # Check database type
        db_type = db.database_type
        print(f"Database type: {db_type}")
        
        # Basic operations work the same regardless of backend
        # Save user (using individual parameters - works with both backends)
        success = await db.save_user(
            user_id=123456789,
            username='example_user',
            first_name='John',
            last_name='Doe',
            language_code='en'
        )
        print(f"User saved: {success}")
        
        # Get user
        user = await db.get_user(123456789)
        print(f"Retrieved user: {user}")
        
        # Log activity
        await db.log_activity(123456789, 'example_action', 'User clicked start button')
        
        # Get activity
        activities = await db.get_user_activity(123456789, limit=5)
        print(f"User activities: {len(activities)} found")
        
        # Set settings
        await db.set_setting('welcome_message', 'Hello from the bot!')
        
        # Get setting
        welcome = await db.get_setting('welcome_message')
        print(f"Welcome message: {welcome}")
        
        # PostgreSQL-specific features (gracefully fallback on SQLite)
        print(f"\n=== Database-Specific Features ({db_type}) ===")
        
        if db_type == 'postgresql':
            print("Using PostgreSQL-specific features:")
            
            # Batch operations
            user_ids = [123456789, 987654321, 555666777]
            users = await db.get_users_batch(user_ids)
            print(f"Batch retrieved {len(users)} users")
            
            # Active users count
            active_count = await db.get_active_users_count(days=7)
            print(f"Active users (7 days): {active_count}")
        else:
            print("Using SQLite with fallback implementations:")
            
            # Batch operations (fallback to individual queries)
            user_ids = [123456789, 987654321, 555666777]
            users = await db.get_users_batch(user_ids)
            print(f"Batch retrieved {len(users)} users (via individual queries)")
        
        # Health check
        healthy = await db.health_check()
        print(f"Database health: {'OK' if healthy else 'ERROR'}")
        
    except Exception as e:
        logger.error(f"Database error: {e}")
    finally:
        await db.disconnect()


async def switching_demo():
    """Demonstrate switching between database types."""
    print("\n=== Database Switching Demo ===")
    
    # Save original configuration
    original_db_type = os.getenv("DATABASE_TYPE")
    original_db_url = os.getenv("DATABASE_URL")
    
    try:
        # Test 1: Force SQLite
        print("\n1. Testing with forced SQLite:")
        os.environ["DATABASE_TYPE"] = "sqlite"
        os.environ["DATABASE_URL"] = ":memory:"
        
        # Reload config
        Config.DATABASE_TYPE = os.getenv("DATABASE_TYPE", "auto").lower()
        Config.DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
        
        db = UnifiedDatabase()
        await db.connect()
        print(f"   Database type: {db.database_type}")
        
        # Test basic operation
        await db.save_user(user_id=1, username="sqlite_user", first_name="SQLite")
        user = await db.get_user(1)
        print(f"   Test user: {user['username'] if user else 'Not found'}")
        
        await db.disconnect()
        
        # Test 2: Try PostgreSQL (if available)
        print("\n2. Testing PostgreSQL configuration:")
        os.environ["DATABASE_TYPE"] = "postgresql"
        os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/testdb"
        
        Config.DATABASE_TYPE = os.getenv("DATABASE_TYPE", "auto").lower()
        Config.DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
        
        print(f"   Would use database type: {DatabaseFactory.get_database_type()}")
        print("   (Connection not attempted - requires real PostgreSQL server)")
        
    finally:
        # Restore original configuration
        if original_db_type is not None:
            os.environ["DATABASE_TYPE"] = original_db_type
            Config.DATABASE_TYPE = original_db_type
        elif "DATABASE_TYPE" in os.environ:
            del os.environ["DATABASE_TYPE"]
            Config.DATABASE_TYPE = "auto"
            
        if original_db_url is not None:
            os.environ["DATABASE_URL"] = original_db_url
            Config.DATABASE_URL = original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]
            Config.DATABASE_URL = "bot.db"


async def main():
    """Run all examples."""
    await database_configuration_example()
    await postgresql_example()
    await switching_demo()
    
    print("\n=== Setup Instructions ===")
    print("To use PostgreSQL in your bot:")
    print("1. Install PostgreSQL and create a database")
    print("2. Install asyncpg: pip install asyncpg")
    print("3. Set environment variables in .env:")
    print("   DATABASE_TYPE=postgresql")
    print("   DATABASE_URL=postgresql://username:password@localhost:5432/your_db")
    print("4. Optionally configure connection pooling:")
    print("   DB_POOL_MIN_SIZE=5")
    print("   DB_POOL_MAX_SIZE=20")
    print("\nTo switch back to SQLite:")
    print("   DATABASE_TYPE=sqlite")
    print("   DATABASE_URL=bot.db")


if __name__ == "__main__":
    asyncio.run(main())


async def performance_comparison():
    """Compare SQLite vs PostgreSQL performance."""
    print("\n=== Performance Comparison ===")
    
    # This is just a demonstration - actual performance depends on your setup
    import time
    
    # SQLite test
    sqlite_db = UnifiedDatabase("sqlite:///test_performance.db")
    await sqlite_db.connect()
    
    start_time = time.time()
    for i in range(100):
        await sqlite_db.save_user({
            'id': i,
            'username': f'user_{i}',
            'first_name': f'User{i}'
        })
    sqlite_time = time.time() - start_time
    
    await sqlite_db.disconnect()
    print(f"SQLite: 100 user inserts in {sqlite_time:.3f}s")
    
    # PostgreSQL test (only if configured)
    if Config.DATABASE_URL.startswith('postgresql://'):
        pg_db = UnifiedDatabase()
        await pg_db.connect()
        
        start_time = time.time()
        for i in range(100, 200):
            await pg_db.save_user({
                'id': i,
                'username': f'user_{i}',
                'first_name': f'User{i}'
            })
        pg_time = time.time() - start_time
        
        await pg_db.disconnect()
        print(f"PostgreSQL: 100 user inserts in {pg_time:.3f}s")
        
        if pg_time < sqlite_time:
            print(f"PostgreSQL is {sqlite_time/pg_time:.1f}x faster")
        else:
            print(f"SQLite is {pg_time/sqlite_time:.1f}x faster")
    else:
        print("PostgreSQL not configured for performance comparison")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(postgresql_example())
    asyncio.run(performance_comparison())