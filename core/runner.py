"""Bot runner module for managing bot lifecycle and services."""

import asyncio
import signal
import sys
from typing import Optional
from aiogram import Bot, Dispatcher

from core.config import Config
from core.logger import setup_logging, get_logger
from utils.logging_utils import log_startup_info, log_shutdown_info
from bot.factory import BotFactory
from services.polling import create_polling_service
from services.webhook import create_webhook_service

logger = get_logger('runner')


class BotRunner:
    """Manages the bot lifecycle and services."""
    
    def __init__(self):
        self.bot: Optional[Bot] = None
        self.dp: Optional[Dispatcher] = None
        self.service = None
        self._shutdown_event = asyncio.Event()
        self._setup_signal_handlers()
    
    def _setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown."""
        for sig in (signal.SIGTERM, signal.SIGINT):
            signal.signal(sig, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, initiating shutdown...")
        self._shutdown_event.set()
    
    async def initialize(self) -> None:
        """Initialize the bot and its components."""
        logger.info("Initializing bot...")
        
        try:
            # Create bot and dispatcher
            self.bot, self.dp = BotFactory.create_bot()
            
            # Initialize bot
            await BotFactory.initialize_bot(self.bot)
            
            logger.info("Bot initialization completed successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    async def start_polling(self) -> None:
        """Start the bot in polling mode."""
        if not self.bot or not self.dp:
            await self.initialize()
        
        logger.info("Starting bot in polling mode...")
        
        try:
            self.service = create_polling_service(self.bot, self.dp)
            
            # Start polling in background
            polling_task = asyncio.create_task(self.service.start())
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
            # Cancel polling task
            polling_task.cancel()
            try:
                await polling_task
            except asyncio.CancelledError:
                pass
            
        except Exception as e:
            logger.error(f"Error in polling mode: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def start_webhook(self) -> None:
        """Start the bot in webhook mode."""
        if not self.bot or not self.dp:
            await self.initialize()
        
        logger.info("Starting bot in webhook mode...")
        
        try:
            app, self.service = create_webhook_service(self.bot, self.dp)
            
            # Start webhook in background
            webhook_task = asyncio.create_task(self.service.start())
            
            # Wait for shutdown signal
            await self._shutdown_event.wait()
            
            # Cancel webhook task
            webhook_task.cancel()
            try:
                await webhook_task
            except asyncio.CancelledError:
                pass
            
        except Exception as e:
            logger.error(f"Error in webhook mode: {e}")
            raise
        finally:
            await self.shutdown()
    
    async def shutdown(self) -> None:
        """Shutdown the bot gracefully."""
        logger.info("Shutting down bot...")
        
        try:
            if self.service:
                await self.service.stop()
            
            if self.bot:
                await BotFactory.shutdown_bot(self.bot)
            
            logger.info("Bot shutdown completed successfully")
            
        except Exception as e:
            logger.error(f"Error during shutdown: {e}")
    
    @property
    def is_running(self) -> bool:
        """Check if the bot is running."""
        return not self._shutdown_event.is_set() and (self.service.is_running if self.service else False)


async def run_bot() -> None:
    """Run the bot based on configuration."""
    runner = BotRunner()
    
    try:
        if Config.USE_WEBHOOK:
            await runner.start_webhook()
        else:
            await runner.start_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise


def main() -> None:
    """Main entry point for the bot."""
    setup_logging()
    
    try:
        # Log startup information
        log_startup_info()
        
        # Setup signal handlers for graceful shutdown
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating graceful shutdown...")
            log_shutdown_info()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        asyncio.run(run_bot())
    except KeyboardInterrupt:
        logger.info("Bot interrupted by user")
        log_shutdown_info()
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        log_shutdown_info()
        sys.exit(1)
    finally:
        logger.info("Bot shutdown completed")


if __name__ == "__main__":
    main()