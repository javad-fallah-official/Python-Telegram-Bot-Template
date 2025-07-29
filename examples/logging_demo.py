#!/usr/bin/env python3
"""
Example script demonstrating the enhanced logging features.
Run this to see the logging system in action.
"""

import asyncio
import time
from core.logger import setup_logging, get_logger, log_user_action, log_error, log_performance, log_security_event
from utils.logging_utils import log_command_execution, LogContext, log_startup_info


async def demo_basic_logging():
    """Demonstrate basic logging features."""
    logger = get_logger('demo')
    
    logger.info("Starting logging demonstration...")
    logger.debug("This is a debug message")
    logger.warning("This is a warning message")
    logger.error("This is an error message")
    
    print("✅ Basic logging demonstrated")


async def demo_structured_logging():
    """Demonstrate structured logging with user context."""
    print("\n📊 Demonstrating structured logging...")
    
    # Simulate user actions
    log_user_action(
        user_id=12345,
        action='demo_command',
        details='User testing the logging system',
        chat_id=67890
    )
    
    # Simulate performance logging
    log_performance('demo_operation', 0.125, {
        'operation_type': 'demonstration',
        'data_size': 1024
    })
    
    # Simulate security event
    log_security_event(
        'demo_security_event',
        user_id=12345,
        details='Demonstration of security logging'
    )
    
    print("✅ Structured logging demonstrated")


async def demo_error_logging():
    """Demonstrate error logging with context."""
    print("\n🚨 Demonstrating error logging...")
    
    try:
        # Simulate an error
        raise ValueError("This is a demonstration error")
    except Exception as e:
        log_error(e, 'demo_error_context', user_id=12345)
    
    print("✅ Error logging demonstrated")


@log_command_execution('demo_command')
async def demo_decorated_function():
    """Demonstrate automatic logging with decorators."""
    print("\n🎯 Demonstrating decorator logging...")
    
    # Simulate some work
    await asyncio.sleep(0.1)
    
    return "Demo completed successfully"


async def demo_context_manager():
    """Demonstrate context manager logging."""
    print("\n⏱️ Demonstrating context manager logging...")
    
    async with LogContext('demo_context_operation', extra_data={'demo': True}):
        # Simulate some work
        await asyncio.sleep(0.05)
        print("Work completed inside context manager")
    
    print("✅ Context manager logging demonstrated")


async def demo_performance_tracking():
    """Demonstrate performance tracking."""
    print("\n⚡ Demonstrating performance tracking...")
    
    operations = ['fast_operation', 'medium_operation', 'slow_operation']
    durations = [0.01, 0.05, 0.15]
    
    for operation, duration in zip(operations, durations):
        start_time = time.time()
        await asyncio.sleep(duration)
        actual_duration = time.time() - start_time
        
        log_performance(operation, actual_duration, {
            'expected_duration': duration,
            'operation_category': 'demo'
        })
    
    print("✅ Performance tracking demonstrated")


async def main():
    """Main demonstration function."""
    print("🚀 Enhanced Logging System Demonstration")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    
    # Log startup
    log_startup_info()
    
    # Run demonstrations
    await demo_basic_logging()
    await demo_structured_logging()
    await demo_error_logging()
    await demo_decorated_function()
    await demo_context_manager()
    await demo_performance_tracking()
    
    print("\n" + "=" * 50)
    print("🎉 Logging demonstration completed!")
    print("\nCheck the following log files:")
    print("📁 logs/bot.log - Main application log")
    print("📁 logs/errors.log - Error-specific log")
    print("📁 logs/bot.json - Structured JSON log")
    print("\nRun the log analyzer to see insights:")
    print("🔍 python scripts/analyze_logs.py")


if __name__ == "__main__":
    asyncio.run(main())