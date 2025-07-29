"""
Webhook mode entry point for the Telegram bot.
"""

import asyncio
import signal
import sys
import uvicorn
from core.logger import setup_logging
from core.config import Config
from bot import create_bot, BotFactory
from services.webhook import create_webhook_service

# Set up logging
logger = setup_logging()


async def main():
    """Main entry point for webhook mode."""
    try:
        # Validate configuration
        Config.validate()
        
        logger.info("=" * 50)
        logger.info("Starting Telegram Bot in Webhook Mode")
        logger.info("=" * 50)
        
        # Create and initialize bot
        application = create_bot()
        await BotFactory.initialize_bot(application)
        
        # Create webhook service
        webhook_app, webhook_service = create_webhook_service(application)
        
        # Start the application
        await application.start()
        
        # Set up webhook
        await webhook_service.setup_webhook()
        
        logger.info(f"Starting webhook server on {Config.WEBHOOK_HOST}:{Config.WEBHOOK_PORT}")
        
        # Configure uvicorn
        config = uvicorn.Config(
            webhook_app,
            host=Config.WEBHOOK_HOST,
            port=Config.WEBHOOK_PORT,
            log_level="info" if Config.DEBUG else "warning",
            access_log=Config.DEBUG
        )
        
        # Start server
        server = uvicorn.Server(config)
        
        # Set up signal handlers
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, stopping...")
            asyncio.create_task(cleanup())
        
        async def cleanup():
            await webhook_service.remove_webhook()
            await application.stop()
            await BotFactory.shutdown_bot(application)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        logger.info("Bot started successfully in webhook mode")
        await server.serve()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())