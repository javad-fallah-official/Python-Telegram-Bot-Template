"""
Polling mode entry point for the Telegram bot.
"""

import asyncio
import signal
import sys
from core.logger import setup_logging
from core.config import Config
from bot import create_bot, BotFactory
from services.polling import create_polling_service

# Set up logging
logger = setup_logging()


async def main():
    """Main entry point for polling mode."""
    try:
        # Validate configuration
        Config.validate()
        
        logger.info("=" * 50)
        logger.info("Starting Telegram Bot in Polling Mode")
        logger.info("=" * 50)
        
        # Create and initialize bot
        application = create_bot()
        await BotFactory.initialize_bot(application)
        
        # Create polling service
        polling_service = create_polling_service(application)
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, stopping...")
            asyncio.create_task(polling_service.stop())
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Start polling
        await polling_service.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())