"""Bot factory module for creating and configuring the Telegram bot application."""

import logging
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from src.core.config import Config
from .handlers import register_handlers

logger = logging.getLogger(__name__)


class BotFactory:
    """Factory class for creating and configuring the Telegram bot."""
    
    @staticmethod
    def create_bot() -> Bot:
        """Create and configure the Telegram bot instance."""
        bot = Bot(
            token=Config.BOT_TOKEN,
            default=DefaultBotProperties(parse_mode=ParseMode.HTML)
        )
        
        logger.info("Bot instance created and configured")
        return bot
    
    @staticmethod
    def create_dispatcher() -> Dispatcher:
        """Create and configure the dispatcher."""
        dp = Dispatcher()
        register_handlers(dp)
        
        logger.info("Dispatcher created and configured")
        return dp
    
    @staticmethod
    async def initialize_bot(bot: Bot) -> None:
        """Initialize the bot and perform startup tasks."""
        try:
            bot_info = await bot.get_me()
            
            logger.info(f"Bot initialized: @{bot_info.username} ({bot_info.first_name})")
            logger.info(f"Bot ID: {bot_info.id}")
            
            if not Config.BOT_USERNAME:
                Config.BOT_USERNAME = bot_info.username
            
        except Exception as e:
            logger.error(f"Failed to initialize bot: {e}")
            raise
    
    @staticmethod
    async def shutdown_bot(bot: Bot) -> None:
        """Shutdown the bot gracefully."""
        try:
            await bot.session.close()
            logger.info("Bot shutdown completed")
        except Exception as e:
            logger.error(f"Error during bot shutdown: {e}")


def create_bot() -> tuple[Bot, Dispatcher]:
    """Create a configured Telegram bot and dispatcher."""
    bot = BotFactory.create_bot()
    dp = BotFactory.create_dispatcher()
    return bot, dp