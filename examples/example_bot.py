"""Example bot demonstrating template usage."""

import asyncio
import logging
import random
from aiogram.types import Message, InlineKeyboardButton
from aiogram.filters import Command

from bot.factory import BotFactory
from core.config import Config
from core.logger import setup_logging
from core.middleware import admin_required, rate_limit, log_user_activity
from utils.formatters import MessageFormatter
from utils.keyboards import KeyboardBuilder
from core.database import Database

setup_logging()
logger = logging.getLogger(__name__)

class ExampleBot:
    """Example bot showing template extension."""
    
    def __init__(self):
        self.db = Database()
    
    async def setup(self):
        """Setup bot with custom handlers."""
        await self.db.connect()
        self.bot, self.dp = BotFactory.create_bot()
        await BotFactory.initialize_bot(self.bot)
        await self.add_custom_handlers()
        logger.info("Example bot setup completed")
    
    async def add_custom_handlers(self):
        """Add custom command handlers."""
        # Register command handlers
        self.dp.message.register(self.weather_command, Command("weather"))
        self.dp.message.register(self.joke_command, Command("joke"))
        self.dp.message.register(self.stats_command, Command("stats"))
        self.dp.message.register(self.menu_command, Command("menu"))
        
        # Register photo handler
        from aiogram import F
        self.dp.message.register(self.photo_handler, F.photo)
    
    @rate_limit(max_requests=5, window_seconds=60)
    @log_user_activity
    async def weather_command(self, message: Message):
        """Weather command with rate limiting."""
        # Parse command arguments
        args = message.text.split()[1:] if message.text else []
        
        if args:
            location = " ".join(args)
            text = f"🌤️ Weather for {MessageFormatter.escape_markdown(location)}:\n\n"
            text += "Temperature: 22°C\nCondition: Sunny\nHumidity: 65%\nWind: 10 km/h"
        else:
            text = "Please provide a location: `/weather London`"
        
        await message.answer(text, parse_mode='MarkdownV2')
    
    @rate_limit(max_requests=10, window_seconds=60)
    @log_user_activity
    async def joke_command(self, message: Message):
        """Random joke command."""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!"
        ]
        
        joke = random.choice(jokes)
        await message.answer(f"😄 {joke}")
    
    @admin_required
    @log_user_activity
    async def stats_command(self, message: Message):
        """Admin-only stats command."""
        try:
            users = await self.db.get_all_users()
            user_count = len(users) if users else 0
            
            recent_activity = await self.db.get_recent_activity(limit=10)
            activity_count = len(recent_activity) if recent_activity else 0
            
            text = f"📊 *Bot Statistics*\n\n"
            text += f"👥 Total Users: {user_count}\n"
            text += f"📈 Recent Activities: {activity_count}\n"
            text += f"🤖 Bot Mode: {Config.BOT_MODE}\n"
            text += f"🐛 Debug Mode: {'On' if Config.DEBUG else 'Off'}"
            
            await message.answer(
                MessageFormatter.escape_markdown(text),
                parse_mode='MarkdownV2'
            )
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await message.answer("❌ Error retrieving statistics.")
    
    @log_user_activity
    async def menu_command(self, message: Message):
        """Command with inline keyboard."""
        buttons = [
            InlineKeyboardButton(text="🌤️ Weather", callback_data="weather_menu"),
            InlineKeyboardButton(text="😄 Joke", callback_data="joke_menu"),
            InlineKeyboardButton(text="📊 Stats", callback_data="stats_menu"),
            InlineKeyboardButton(text="ℹ️ Help", callback_data="help_menu")
        ]
        
        keyboard = KeyboardBuilder.build_menu(buttons, n_cols=2)
        text = "🎛️ *Main Menu*\n\nChoose an option:"
        
        await message.answer(
            MessageFormatter.escape_markdown(text),
            reply_markup=keyboard,
            parse_mode='MarkdownV2'
        )
    
    @log_user_activity
    async def photo_handler(self, message: Message):
        """Handle photo messages."""
        user = message.from_user
        photo = message.photo[-1]
        
        logger.info(f"User {user.id} sent a photo: {photo.file_id}")
        
        text = f"📸 Nice photo, {MessageFormatter.escape_markdown(user.first_name)}!\n\n"
        text += f"Photo size: {photo.width}x{photo.height}\n"
        text += f"File size: ~{photo.file_size // 1024}KB"
        
        await message.answer(text, parse_mode='MarkdownV2')

async def main():
    """Run the example bot."""
    try:
        example_bot = ExampleBot()
        await example_bot.setup()
        
        from core.runner import BotRunner
        runner = BotRunner(example_bot.bot, example_bot.dp)
        await runner.start_polling()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())