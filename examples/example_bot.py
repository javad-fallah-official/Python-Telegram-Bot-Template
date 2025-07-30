"""Example bot demonstrating template usage."""

import asyncio
import logging
import random
from telegram import Update, InlineKeyboardButton
from telegram.ext import CommandHandler, MessageHandler, filters, ContextTypes

from bot import BotFactory, create_bot
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
        self.application = create_bot()
        await BotFactory.initialize_bot(self.application)
        await self.add_custom_handlers()
        logger.info("Example bot setup completed")
    
    async def add_custom_handlers(self):
        """Add custom command handlers."""
        handlers = [
            CommandHandler("weather", self.weather_command),
            CommandHandler("joke", self.joke_command),
            CommandHandler("stats", self.stats_command),
            CommandHandler("menu", self.menu_command),
            MessageHandler(filters.PHOTO, self.photo_handler)
        ]
        
        for handler in handlers:
            self.application.add_handler(handler)
    
    @rate_limit(max_requests=5, window_seconds=60)
    @log_user_activity
    async def weather_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Weather command with rate limiting."""
        if context.args:
            location = " ".join(context.args)
            message = f"🌤️ Weather for {MessageFormatter.escape_markdown(location)}:\n\n"
            message += "Temperature: 22°C\nCondition: Sunny\nHumidity: 65%\nWind: 10 km/h"
        else:
            message = "Please provide a location: `/weather London`"
        
        await update.message.reply_text(message, parse_mode='MarkdownV2')
    
    @rate_limit(max_requests=10, window_seconds=60)
    @log_user_activity
    async def joke_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Random joke command."""
        jokes = [
            "Why don't scientists trust atoms? Because they make up everything!",
            "Why did the scarecrow win an award? He was outstanding in his field!",
            "Why don't eggs tell jokes? They'd crack each other up!",
            "What do you call a fake noodle? An impasta!",
            "Why did the math book look so sad? Because it had too many problems!"
        ]
        
        joke = random.choice(jokes)
        await update.message.reply_text(f"😄 {joke}")
    
    @admin_required
    @log_user_activity
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Admin-only stats command."""
        try:
            users = await self.db.get_all_users()
            user_count = len(users) if users else 0
            
            recent_activity = await self.db.get_recent_activity(limit=10)
            activity_count = len(recent_activity) if recent_activity else 0
            
            message = f"📊 *Bot Statistics*\n\n"
            message += f"👥 Total Users: {user_count}\n"
            message += f"📈 Recent Activities: {activity_count}\n"
            message += f"🤖 Bot Mode: {Config.BOT_MODE}\n"
            message += f"🐛 Debug Mode: {'On' if Config.DEBUG else 'Off'}"
            
            await update.message.reply_text(
                MessageFormatter.escape_markdown(message),
                parse_mode='MarkdownV2'
            )
            
        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            await update.message.reply_text("❌ Error retrieving statistics.")
    
    @log_user_activity
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Command with inline keyboard."""
        buttons = [
            InlineKeyboardButton("🌤️ Weather", callback_data="weather_menu"),
            InlineKeyboardButton("😄 Joke", callback_data="joke_menu"),
            InlineKeyboardButton("📊 Stats", callback_data="stats_menu"),
            InlineKeyboardButton("ℹ️ Help", callback_data="help_menu")
        ]
        
        keyboard = KeyboardBuilder.build_menu(buttons, n_cols=2)
        message = "🎛️ *Main Menu*\n\nChoose an option:"
        
        await update.message.reply_text(
            MessageFormatter.escape_markdown(message),
            reply_markup=keyboard,
            parse_mode='MarkdownV2'
        )
    
    @log_user_activity
    async def photo_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo messages."""
        user = update.effective_user
        photo = update.message.photo[-1]
        
        logger.info(f"User {user.id} sent a photo: {photo.file_id}")
        
        message = f"📸 Nice photo, {MessageFormatter.escape_markdown(user.first_name)}!\n\n"
        message += f"Photo size: {photo.width}x{photo.height}\n"
        message += f"File size: ~{photo.file_size // 1024}KB"
        
        await update.message.reply_text(message, parse_mode='MarkdownV2')

async def main():
    """Run the example bot."""
    try:
        example_bot = ExampleBot()
        await example_bot.setup()
        
        from core.runner import BotRunner
        runner = BotRunner(example_bot.application)
        await runner.start()
        
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())