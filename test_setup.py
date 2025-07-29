"""
Simple test script to verify the bot template setup.
Run this to check if all modules can be imported and basic functionality works.
"""

import asyncio
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_imports():
    """Test if all modules can be imported."""
    print("🧪 Testing module imports...")
    
    try:
        import config
        print("✅ config module imported")
        
        import logger
        print("✅ logger module imported")
        
        import handlers
        print("✅ handlers module imported")
        
        import bot
        print("✅ bot module imported")
        
        import webhook
        print("✅ webhook module imported")
        
        import middleware
        print("✅ middleware module imported")
        
        import database
        print("✅ database module imported")
        
        import utils
        print("✅ utils module imported")
        
        print("\n🎉 All modules imported successfully!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

async def test_config():
    """Test configuration loading."""
    print("\n🧪 Testing configuration...")
    
    try:
        from core.config import Config
        
        # Test basic config access (skip BOT_TOKEN validation for testing)
        print(f"Bot mode: {Config.BOT_MODE}")
        print(f"Debug mode: {Config.DEBUG}")
        print(f"Log level: {Config.LOG_LEVEL}")
        
        # Test validation with skip_bot_token=True
        Config.validate(skip_bot_token=True)
        print("✅ Configuration loaded successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

async def test_utilities():
    """Test utility functions."""
    print("\n🧪 Testing utilities...")
    
    try:
        from utils import formatter, text_processor, validator
        
        # Test text formatting
        escaped = formatter.escape_markdown("Test *text* with _special_ chars")
        print(f"Escaped text: {escaped}")
        
        # Test text processing
        command, args = text_processor.extract_command_args("/start arg1 arg2")
        print(f"Command: {command}, Args: {args}")
        
        # Test validation
        is_valid_email = validator.is_valid_email("test@example.com")
        print(f"Email validation: {is_valid_email}")
        
        print("✅ Utilities working correctly!")
        return True
        
    except Exception as e:
        print(f"❌ Utilities error: {e}")
        return False

async def test_database():
    """Test database functionality."""
    print("\n🧪 Testing database...")
    
    try:
        from database import Database
        
        # Create test database
        db = Database(":memory:")  # Use in-memory database for testing
        await db.connect()
        
        # Test user operations
        test_user = {
            'id': 123456789,
            'username': 'testuser',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        await db.save_user(test_user)
        user = await db.get_user(123456789)
        
        if user and user['username'] == 'testuser':
            print("✅ Database operations working!")
        else:
            print("❌ Database test failed")
            return False
        
        await db.disconnect()
        return True
        
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

async def main():
    """Run all tests."""
    print("🚀 Starting bot template tests...\n")
    
    tests = [
        test_imports,
        test_config,
        test_utilities,
        test_database
    ]
    
    results = []
    for test in tests:
        try:
            result = await test()
            results.append(result)
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            results.append(False)
    
    print(f"\n📊 Test Results: {sum(results)}/{len(results)} passed")
    
    if all(results):
        print("🎉 All tests passed! Your bot template is ready to use.")
        print("\n📝 Next steps:")
        print("1. Copy .env.example to .env")
        print("2. Add your BOT_TOKEN to .env")
        print("3. Run: python main.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())