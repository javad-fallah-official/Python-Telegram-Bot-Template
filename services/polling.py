"""Polling service module for running the bot in polling mode."""

import asyncio
import logging
from aiogram import Bot, Dispatcher
from .base import BotService

logger = logging.getLogger(__name__)


class PollingService(BotService):
    """Service for running the bot in polling mode."""
    
    async def start(self) -> None:
        """Start the bot in polling mode."""
        logger.info("Starting bot in polling mode...")
        
        try:
            self._running = True
            logger.info("Bot started successfully in polling mode")
            
            # Start polling
            await self.dp.start_polling(
                self.bot,
                drop_pending_updates=True
            )
                
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
            await self.dp.stop_polling()
            logger.info("Polling service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping polling service: {e}")


def create_polling_service(bot: Bot, dp: Dispatcher) -> PollingService:
    """Create and configure polling service."""
    return PollingService(bot, dp)