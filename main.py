#!/usr/bin/env python3
"""
Telegram Bot Template - Main Entry Point

Simple, single-file entry point that:
- Reads configuration from .env file
- Starts the bot in the configured mode
- Handles graceful shutdown

Usage:
    uv run python main.py
"""

import asyncio
import sys
from core.runner import run_bot
from core.logger import setup_logging
from core.config import Config

logger = setup_logging()


async def main() -> None:
    """Main entry point - reads config from .env and starts the bot."""
    try:
        # Load configuration from .env
        config = Config()
        
        logger.info("🚀 Starting Telegram Bot Template...")
        logger.info(f"📋 Mode: {config.BOT_MODE}")
        logger.info(f"🐛 Debug: {config.DEBUG}")
        logger.info(f"📝 Logging: {'Enabled' if config.LOGGING_ENABLED else 'Disabled'}")
        
        # Start the bot with the configured mode
        await run_bot(config.BOT_MODE)
        
    except KeyboardInterrupt:
        logger.info("🛑 Bot stopped by user")
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
