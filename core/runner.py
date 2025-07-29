"""Unified bot runner for managing bot services."""

import asyncio
import signal
import sys
from typing import Optional

from core.config import Config
from core.logger import setup_logging, get_logger
from utils.logging_utils import log_startup_info, log_shutdown_info
from bot import create_bot, BotFactory
from services.polling import create_polling_service
from services.webhook import create_webhook_service
from services.base import BotService

logger = get_logger('runner')


class BotRunner:
    """Unified bot runner that manages different service modes."""
    
    def __init__(self):
        self.application = None
        self.service: Optional[BotService] = None
        self._running = False
        self._setup_signal_handlers()
    
    async def start(self, mode: Optional[str] = None) -> None:
        """Start the bot in the specified mode."""
        mode = mode or Config.BOT_MODE
        
        try:
            Config.validate()
            
            logger.info("=" * 50)
            logger.info("Starting Telegram Bot")
            logger.info(f"Mode: {mode}")
            logger.info(f"Debug: {Config.DEBUG}")
            logger.info("=" * 50)
            
            # Create and initialize bot
            self.application = create_bot()
            await BotFactory.initialize_bot(self.application)
            
            # Create appropriate service
            if mode == "polling":
                self.service = create_polling_service(self.application)
            elif mode == "webhook":
                self.service = create_webhook_service(self.application)[1]  # Get service, not app
            else:
                raise ValueError(f"Invalid bot mode: {mode}")
            
            self._running = True
            
            # Start the service
            await self.service.start()
            
        except Exception as e:
            logger.error(f"Failed to start bot: {e}")
            await self.stop()
            raise
    
    async def stop(self) -> None:
        """Stop the bot gracefully."""
        if not self._running:
            return
        
        logger.info("Stopping bot...")
        self._running = False
        
        try:
            if self.service:
                await self.service.stop()
            
            if self.application:
                await BotFactory.shutdown_bot(self.application)
            
            logger.info("Bot stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping bot: {e}")
    
    def _setup_signal_handlers(self) -> None:
        """Set up signal handlers for graceful shutdown."""
        def signal_handler(signum, frame):
            logger.info(f"Received signal {signum}, initiating shutdown...")
            self._running = False
            
            # Create task to stop the bot
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    loop.create_task(self.stop())
                else:
                    asyncio.run(self.stop())
            except RuntimeError:
                # If no event loop is running, create a new one
                asyncio.run(self.stop())
        
        # Register signal handlers
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        if sys.platform != "win32":
            signal.signal(signal.SIGHUP, signal_handler)
    
    @property
    def is_running(self) -> bool:
        """Check if the bot is running."""
        return self._running and (self.service.is_running if self.service else False)


async def run_bot(mode: Optional[str] = None) -> None:
    """Run the bot with the specified mode."""
    runner = BotRunner()
    
    try:
        await runner.start(mode)
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
    finally:
        await runner.stop()


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