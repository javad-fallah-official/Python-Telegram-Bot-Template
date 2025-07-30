#!/usr/bin/env python3
"""
Database Switching Demo

This example demonstrates how to use the new DATABASE_TYPE environment variable
to switch between SQLite and PostgreSQL databases.
"""

import asyncio
import os
import sys
import tempfile
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import Config
from core.db_factory import DatabaseFactory, UnifiedDatabase


async def demo_database_switching():
    """Demonstrate database switching functionality."""
    print("=== Database Switching Demo ===\n")
    
    # Save original environment
    original_db_type = os.getenv("DATABASE_TYPE")
    original_db_url = os.getenv("DATABASE_URL")
    
    try:
        # Demo 1: Auto-detection (default behavior)
        print("1. Auto-detection mode (DATABASE_TYPE=auto)")
        os.environ["DATABASE_TYPE"] = "auto"
        os.environ["DATABASE_URL"] = "demo.db"
        
        # Reload config to pick up changes
        Config.DATABASE_TYPE = os.getenv("DATABASE_TYPE", "auto").lower()
        Config.DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
        
        db_type = DatabaseFactory.get_database_type()
        print(f"   Detected database type: {db_type}")
        print(f"   Database URL: {Config.DATABASE_URL}")
        
        # Demo 2: Force SQLite
        print("\n2. Force SQLite mode (DATABASE_TYPE=sqlite)")
        os.environ["DATABASE_TYPE"] = "sqlite"
        os.environ["DATABASE_URL"] = "postgresql://fake:fake@localhost/fake"  # PostgreSQL URL
        
        Config.DATABASE_TYPE = os.getenv("DATABASE_TYPE", "auto").lower()
        Config.DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
        
        db_type = DatabaseFactory.get_database_type()
        print(f"   Forced database type: {db_type}")
        print(f"   Database URL: {Config.DATABASE_URL}")
        print("   Note: Even with PostgreSQL URL, SQLite is used because DATABASE_TYPE=sqlite")
        
        # Demo 3: Force PostgreSQL
        print("\n3. Force PostgreSQL mode (DATABASE_TYPE=postgresql)")
        os.environ["DATABASE_TYPE"] = "postgresql"
        os.environ["DATABASE_URL"] = "simple.db"  # SQLite URL
        
        Config.DATABASE_TYPE = os.getenv("DATABASE_TYPE", "auto").lower()
        Config.DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
        
        db_type = DatabaseFactory.get_database_type()
        print(f"   Forced database type: {db_type}")
        print(f"   Database URL: {Config.DATABASE_URL}")
        print("   Note: Even with SQLite URL, PostgreSQL is used because DATABASE_TYPE=postgresql")
        
        # Demo 4: Practical SQLite usage
        print("\n4. Practical SQLite usage")
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as tmp_file:
            temp_db_path = tmp_file.name
        
        os.environ["DATABASE_TYPE"] = "sqlite"
        os.environ["DATABASE_URL"] = temp_db_path
        
        Config.DATABASE_TYPE = os.getenv("DATABASE_TYPE", "auto").lower()
        Config.DATABASE_URL = os.getenv("DATABASE_URL", "bot.db")
        
        print(f"   Using temporary SQLite database: {temp_db_path}")
        
        # Create and test database
        unified_db = UnifiedDatabase()
        await unified_db.connect()
        
        # Test basic operations
        print("   Testing database operations...")
        
        # Save a test user
        result = await unified_db.save_user(
            user_id=12345,
            username="demo_user",
            first_name="Demo",
            last_name="User"
        )
        print(f"   User saved: {result}")
        
        # Retrieve the user
        user = await unified_db.get_user(12345)
        if user:
            print(f"   Retrieved user: {user['username']} ({user['first_name']} {user['last_name']})")
        
        # Log activity
        await unified_db.log_activity(12345, "demo_action", "Testing database switching")
        
        # Get user count
        count = await unified_db.get_user_count()
        print(f"   Total users in database: {count}")
        
        await unified_db.disconnect()
        
        # Clean up
        os.unlink(temp_db_path)
        print("   Temporary database cleaned up")
        
        print("\n=== Demo completed successfully! ===")
        print("\nTo use database switching in your bot:")
        print("1. Set DATABASE_TYPE in your .env file:")
        print("   - DATABASE_TYPE=auto     (auto-detect from URL)")
        print("   - DATABASE_TYPE=sqlite   (force SQLite)")
        print("   - DATABASE_TYPE=postgresql (force PostgreSQL)")
        print("2. Set DATABASE_URL to your database connection string")
        print("3. The UnifiedDatabase will automatically use the correct backend")
        
    except Exception as e:
        print(f"Error during demo: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Restore original environment
        if original_db_type is not None:
            os.environ["DATABASE_TYPE"] = original_db_type
        elif "DATABASE_TYPE" in os.environ:
            del os.environ["DATABASE_TYPE"]
            
        if original_db_url is not None:
            os.environ["DATABASE_URL"] = original_db_url
        elif "DATABASE_URL" in os.environ:
            del os.environ["DATABASE_URL"]


if __name__ == "__main__":
    asyncio.run(demo_database_switching())