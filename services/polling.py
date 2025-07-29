"""
Polling service module for running the bot in polling mode.
"""

import asyncio
import logging
from telegram.ext import Application

logger = logging.getLogger(__name__)


class PollingService:
    """Service for running the bot in polling mode."""
    
    def __init__(self, application: Application):
        self.application = application
        self.running = False
    
    async def start(self):
        """Start the bot in polling mode."""
        logger.info("Starting bot in polling mode...")
        
        try:
            # Start the application
            await self.application.start()
            
            # Start polling
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
    
    async def stop(self):
        """Stop the polling service."""
        if not self.running:
            return
            
        logger.info("Stopping polling service...")
        self.running = False
        
        try:
            if self.application.updater.running:
                await self.application.updater.stop()
            
            await self.application.stop()
            logger.info("Polling service stopped successfully")
            
        except Exception as e:
            logger.error(f"Error stopping polling service: {e}")
    
    def is_running(self) -> bool:
        """Check if the service is running."""
        return self.running


def create_polling_service(application: Application) -> PollingService:
    """Create and configure polling service."""
    return PollingService(application)