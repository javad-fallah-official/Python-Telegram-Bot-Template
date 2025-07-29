"""
Bot application wrapper for enhanced functionality.
"""

import logging
from typing import Optional
from telegram.ext import Application
from .factory import BotFactory

logger = logging.getLogger(__name__)


class BotApplication:
    """Enhanced bot application wrapper with additional functionality."""
    
    def __init__(self):
        self.application: Optional[Application] = None
        self.is_initialized = False
        self.is_running = False
    
    async def create(self) -> Application:
        """Create the bot application."""
        if self.application is None:
            self.application = BotFactory.create_application()
        return self.application
    
    async def initialize(self) -> None:
        """Initialize the bot application."""
        if not self.application:
            await self.create()
        
        if not self.is_initialized:
            await BotFactory.initialize_bot(self.application)
            self.is_initialized = True
    
    async def start(self) -> None:
        """Start the bot application."""
        if not self.is_initialized:
            await self.initialize()
        
        await self.application.start()
        self.is_running = True
        logger.info("Bot application started")
    
    async def stop(self) -> None:
        """Stop the bot application."""
        if self.application and self.is_running:
            await self.application.stop()
            await BotFactory.shutdown_bot(self.application)
            self.is_running = False
            logger.info("Bot application stopped")
    
    def get_application(self) -> Optional[Application]:
        """Get the underlying application instance."""
        return self.application