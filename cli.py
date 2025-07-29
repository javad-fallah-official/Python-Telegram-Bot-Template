#!/usr/bin/env python3
"""
Command Line Interface for the Telegram Bot Template.
Provides commands for running, testing, and managing the bot.
"""

import sys
import asyncio
import argparse
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from core.config import Config
from core.logger import setup_logging


def create_parser():
    """Create the command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Telegram Bot Template CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s run                    # Run bot with default settings
  %(prog)s run --mode polling     # Run in polling mode
  %(prog)s run --mode webhook     # Run in webhook mode
  %(prog)s test                   # Test bot configuration
  %(prog)s validate               # Validate environment setup
        """
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Run command
    run_parser = subparsers.add_parser('run', help='Run the bot')
    run_parser.add_argument(
        '--mode', 
        choices=['polling', 'webhook'], 
        help='Bot mode (overrides BOT_MODE env var)'
    )
    run_parser.add_argument(
        '--debug', 
        action='store_true', 
        help='Enable debug mode'
    )
    
    # Test command
    test_parser = subparsers.add_parser('test', help='Test bot configuration')
    test_parser.add_argument(
        '--quick', 
        action='store_true', 
        help='Quick test without full initialization'
    )
    
    # Validate command
    validate_parser = subparsers.add_parser('validate', help='Validate environment setup')
    
    # Version command
    version_parser = subparsers.add_parser('version', help='Show version information')
    
    return parser


async def run_bot(mode=None, debug=False):
    """Run the bot with specified options."""
    # Override config if specified
    if mode:
        Config.BOT_MODE = mode
    if debug:
        Config.DEBUG = True
    
    # Import and run main
    from main import main
    await main()


async def test_bot(quick=False):
    """Test bot configuration and connectivity."""
    logger = setup_logging()
    
    try:
        logger.info("🧪 Testing bot configuration...")
        
        # Validate config
        Config.validate()
        logger.info("✅ Configuration is valid")
        
        if not quick:
            # Test bot connection
            from bot import create_bot, BotFactory
            
            logger.info("🤖 Testing bot connection...")
            application = create_bot()
            await BotFactory.initialize_bot(application)
            
            # Get bot info
            bot_info = await application.bot.get_me()
            logger.info(f"✅ Bot connected: @{bot_info.username}")
            
            # Cleanup
            await BotFactory.shutdown_bot(application)
        
        logger.info("🎉 All tests passed!")
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    
    return True


def validate_environment():
    """Validate environment setup."""
    logger = setup_logging()
    
    logger.info("🔍 Validating environment setup...")
    
    issues = []
    
    # Check required environment variables
    required_vars = ['BOT_TOKEN']
    for var in required_vars:
        if not getattr(Config, var, None):
            issues.append(f"Missing required environment variable: {var}")
    
    # Check optional but recommended variables
    recommended_vars = ['ADMIN_USER_IDS', 'BOT_MODE']
    for var in recommended_vars:
        if not getattr(Config, var, None):
            logger.warning(f"⚠️  Recommended environment variable not set: {var}")
    
    # Check webhook-specific variables
    if Config.BOT_MODE == "webhook":
        webhook_vars = ['WEBHOOK_URL', 'WEBHOOK_HOST', 'WEBHOOK_PORT']
        for var in webhook_vars:
            if not getattr(Config, var, None):
                issues.append(f"Missing webhook environment variable: {var}")
    
    # Report results
    if issues:
        logger.error("❌ Environment validation failed:")
        for issue in issues:
            logger.error(f"  • {issue}")
        return False
    else:
        logger.info("✅ Environment validation passed!")
        return True


def show_version():
    """Show version and system information."""
    import platform
    import telegram
    
    print("🤖 Telegram Bot Template")
    print("=" * 40)
    print(f"Python: {platform.python_version()}")
    print(f"Platform: {platform.system()} {platform.release()}")
    print(f"python-telegram-bot: {telegram.__version__}")
    print(f"Bot Mode: {Config.BOT_MODE}")
    print(f"Debug: {Config.DEBUG}")


async def main():
    """Main CLI entry point."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == 'run':
            await run_bot(mode=args.mode, debug=args.debug)
        
        elif args.command == 'test':
            success = await test_bot(quick=args.quick)
            sys.exit(0 if success else 1)
        
        elif args.command == 'validate':
            success = validate_environment()
            sys.exit(0 if success else 1)
        
        elif args.command == 'version':
            show_version()
        
        else:
            parser.print_help()
    
    except KeyboardInterrupt:
        print("\n🛑 Operation cancelled by user")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())