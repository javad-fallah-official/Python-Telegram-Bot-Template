#!/usr/bin/env python3
"""
Demo script to test the logging toggle functionality.
This script demonstrates how the LOGGING_ENABLED environment variable controls logging.
"""

import os
import sys
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from core.config import Config
from core.logger import get_logger, log_user_action, log_error, log_performance, log_security_event
from utils.logging_utils import LogContext, log_startup_info, log_shutdown_info


def test_logging_functionality():
    """Test various logging functions."""
    print(f"\n🔧 Testing logging functionality...")
    print(f"LOGGING_ENABLED = {Config.LOGGING_ENABLED}")
    print(f"LOG_LEVEL = {Config.LOG_LEVEL}")
    
    # Get a logger
    logger = get_logger('demo')
    
    # Test basic logging
    logger.info("This is a test info message")
    logger.warning("This is a test warning message")
    logger.error("This is a test error message")
    
    # Test structured logging functions
    log_user_action(
        user_id=12345,
        action='test_action',
        details='Testing logging toggle functionality',
        chat_id=67890
    )
    
    # Test performance logging
    log_performance('test_operation', 0.123, {
        'test_param': 'test_value',
        'success': True
    })
    
    # Test security logging
    log_security_event(
        'test_security_event',
        user_id=12345,
        details='Testing security logging'
    )
    
    # Test error logging
    try:
        raise ValueError("This is a test error")
    except Exception as e:
        log_error(e, 'test_context', user_id=12345)
    
    print("✅ Logging test completed")


async def test_context_manager():
    """Test the LogContext context manager."""
    print("\n🔄 Testing LogContext...")
    
    async with LogContext('test_context_operation', extra_data={'param': 'value'}):
        # Simulate some work
        time.sleep(0.1)
        print("Work completed inside LogContext")
    
    print("✅ LogContext test completed")


def test_startup_shutdown_logging():
    """Test startup and shutdown logging."""
    print("\n🚀 Testing startup/shutdown logging...")
    
    log_startup_info()
    print("Startup logging called")
    
    log_shutdown_info()
    print("Shutdown logging called")
    
    print("✅ Startup/shutdown test completed")


def main():
    """Main demo function."""
    print("=" * 60)
    print("🎯 LOGGING TOGGLE DEMONSTRATION")
    print("=" * 60)
    
    print(f"\n📊 Current Configuration:")
    print(f"  • LOGGING_ENABLED: {Config.LOGGING_ENABLED}")
    print(f"  • LOG_LEVEL: {Config.LOG_LEVEL}")
    print(f"  • DEBUG: {Config.DEBUG}")
    print(f"  • BOT_MODE: {Config.BOT_MODE}")
    
    if Config.LOGGING_ENABLED:
        print(f"\n📁 Log files will be created in: {Path('logs').absolute()}")
        print("  • bot.log - Main application log")
        print("  • errors.log - Error-only log")
        print("  • bot.json - Structured JSON log")
        if Config.DEBUG:
            print("  • debug.log - Debug log (debug mode only)")
    else:
        print("\n🚫 Logging is DISABLED - no log files will be created")
        print("   No console output from logging functions")
    
    # Test all logging functionality
    test_logging_functionality()
    
    # Test context manager (async)
    import asyncio
    asyncio.run(test_context_manager())
    
    # Test startup/shutdown logging
    test_startup_shutdown_logging()
    
    print("\n" + "=" * 60)
    print("🎉 DEMO COMPLETED")
    print("=" * 60)
    
    if Config.LOGGING_ENABLED:
        logs_dir = Path("logs")
        if logs_dir.exists():
            log_files = list(logs_dir.glob("*.log")) + list(logs_dir.glob("*.json"))
            if log_files:
                print(f"\n📋 Generated log files:")
                for log_file in sorted(log_files):
                    size = log_file.stat().st_size
                    print(f"  • {log_file.name} ({size} bytes)")
            else:
                print("\n📋 No log files found (they may not have been created yet)")
        else:
            print("\n📋 Logs directory not found")
    else:
        print("\n📋 No log files created (logging disabled)")
    
    print(f"\n💡 To toggle logging:")
    print(f"   1. Edit your .env file")
    print(f"   2. Set LOGGING_ENABLED=true (to enable) or LOGGING_ENABLED=false (to disable)")
    print(f"   3. Restart the application")


if __name__ == "__main__":
    main()