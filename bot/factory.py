"""Bot factory module for creating and configuring the Telegram bot application."""

import logging
from telegram.ext import Application
from core.config import Config
from .handlers import register_handlers

logger = logging.getLogger(__name__)


class BotFactory:
    """Factory class for creating and configuring the Telegram bot."""
    
    @staticmethod
    def create_application() -> Application:
        """Create and configure the Telegram bot application."""
        application = (
            Application.builder()
            .token(Config.BOT_TOKEN)
            .build()
        )
        
        register_handlers(application)
        
        logger.info("Bot application created and configured")
        return application
    
    @staticmethod
    async def initialize_bot(application: Application) -> None:
        """Initialize the bot and perform startup tasks."""
        try:
            await application.initialize()
            
            bot = application.bot
            bot_info = await bot.get_me()
            
            logger.info(f"Bot initialized: @{bot_info.username} ({bot_info.first_name})")
            logger.info(f"Bot ID: {bot_info.id}")
            
            if not Config.BOT_USERNAME:
                Config.BOT_USERNAME = bot_info.username
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    @staticmethod
    async def shutdown_bot(application: Application) -> None:
        """Shutdown the bot gracefully."""
        try:
            await application.shutdown()
            logger.info("Bot shutdown completed")
        except Exception as e:
            logger.error(f"Error during bot shutdown: {e}")


def create_bot() -> Application:
    """Create a configured Telegram bot application."""
    return BotFactory.create_application()