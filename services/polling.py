"""Polling service module for running the bot in polling mode."""

import asyncio
import logging
from telegram.ext import Application
from .base import BotService

logger = logging.getLogger(__name__)


class PollingService(BotService):
    """Service for running the bot in polling mode."""
    
    async def start(self) -> None:
        """Start the bot in polling mode."""
        logger.info("Starting bot in polling mode...")
        
        try:
            await self.application.start()
            
            await self.application.updater.start_polling(
                drop_pending_updates=True,
                allowed_updates=None
            )
            
            self._running = True
            logger.info("Bot started successfully in polling mode")
            
            while self._running:
                await asyncio.sleep(1)
                
        except Exception as e:
            logger.error(f"Error in polling mode: {e}")
            raise
        finally:
            await self.stop()
    
    async def stop(self) -> None:
        """Stop the polling service."""
        if not self._running:
            return
            
        logger.info("Stopping polling service...")
        self._running = False
        
        try:
            if self.application.updater.running:
                await self.application.updater.stop()
            
            await self.application.stop()
            logger.info("Polling service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping polling service: {e}")


def create_polling_service(application: Application) -> PollingService:
    """Create and configure polling service."""
    return PollingService(application)