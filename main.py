"""
Main module for running the Telegram bot.
Supports both polling and webhook modes with graceful shutdown.
"""

import asyncio
import signal
import sys
import uvicorn
from contextlib import asynccontextmanager
from typing import Optional

from core.logger import setup_logging
from core.config import Config
from bot import create_bot, BotFactory
from services.webhook import create_webhook_service

# Set up logging
logger = setup_logging()


class BotRunner:
    """Main bot runner class that handles both polling and webhook modes."""
    
    def __init__(self):
        self.application = None
        self.webhook_server = None
        self.running = False
    
    async def start_polling(self):
        """Start the bot in polling mode."""
        logger.info("Starting bot in polling mode...")
        
        try:
            # Create and initialize bot
            self.application = create_bot()
            await BotFactory.initialize_bot(self.application)
            
            # Start polling
            await self.application.start()
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=None
            )
            
            self.running = True
            logger.info("Bot started successfully in polling mode")
            
            # Keep running until stopped
            while self.running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in polling mode: {e}")
            raise
        finally:
            await self.stop()
    
    async def start_webhook(self):
        """Start the bot in webhook mode."""
        logger.info("Starting bot in webhook mode...")
        
        try:
            # Create and initialize bot
            self.application = create_bot()
            await BotFactory.initialize_bot(self.application)
            
            # Create webhook app
            webhook_app, self.webhook_server = create_webhook_service(self.application)
            
            # Start the application
            await self.application.start()
            
            # Set up webhook
            await self.webhook_server.setup_webhook()
            
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
            self.running = True
            
            logger.info("Bot started successfully in webhook mode")
            await server.serve()
            
        except Exception as e:
            logger.error(f"Error in webhook mode: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self):
        """Stop the bot gracefully."""
        if not self.running:
            return
            
        logger.info("Stopping bot...")
        self.running = False
        
        try:
            if self.application:
                # Remove webhook if in webhook mode
                if Config.BOT_MODE == "webhook" and self.webhook_server:
                    await self.webhook_server.remove_webhook()
                
                # Stop application
                await self.application.stop()
                await BotFactory.shutdown_bot(self.application)
                
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self.running = False
            
            # Create new event loop if needed
            try:
                loop = asyncio.get_event_loop()
            except RuntimeError:
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
            
            # Schedule stop coroutine
            loop.create_task(self.stop())
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if sys.platform != "win32":
            signal.signal(signal.SIGHUP, signal_handler)


async def main():
    """Main entry point for the bot."""
    try:
        # Validate configuration
        Config.validate()
        
        logger.info("=" * 50)
        logger.info("Starting Telegram Bot Template")
        logger.info(f"Mode: {Config.BOT_MODE}")
        logger.info(f"Debug: {Config.DEBUG}")
        logger.info("=" * 50)
        
        # Create bot runner
        runner = BotRunner()
        runner.setup_signal_handlers()
        
        # Start bot based on mode
        if Config.BOT_MODE == "polling":
            await runner.start_polling()
        elif Config.BOT_MODE == "webhook":
            await runner.start_webhook()
        else:
            raise ValueError(f"Invalid bot mode: {Config.BOT_MODE}")
            
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Run the bot
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        sys.exit(1)
