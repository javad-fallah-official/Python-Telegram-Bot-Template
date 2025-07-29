"""
Command handlers module.
Contains all command handlers for the Telegram bot.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from core.config import Config

logger = logging.getLogger(__name__)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    user = update.effective_user
    logger.info(f"User {user.id} ({user.username}) started the bot")
    
    welcome_message = (
        f"👋 Hello {user.mention_html()}!\n\n"
        "Welcome to this awesome Telegram bot template!\n\n"
        "Available commands:\n"
        "• /start - Show this welcome message\n"
        "• /help - Get help information\n"
        "• /status - Check bot status\n"
        "• /echo <message> - Echo your message\n"
    )
    
    if Config.is_admin(user.id):
        welcome_message += "\n🔧 Admin commands:\n• /admin - Admin panel\n"
    
    await update.message.reply_html(welcome_message)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = (
        "🤖 <b>Bot Help</b>\n\n"
        "<b>Available Commands:</b>\n"
        "• /start - Start the bot and see welcome message\n"
        "• /help - Show this help message\n"
        "• /status - Check bot status\n"
        "• /echo <message> - Echo your message back\n\n"
        "<b>How to use:</b>\n"
        "Simply send any command or message to interact with the bot!\n\n"
        "Need more help? Contact the bot administrator."
    )
    
    await update.message.reply_html(help_text)


async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command."""
    user = update.effective_user
    logger.info(f"User {user.id} requested bot status")
    
    status_message = (
        "🟢 <b>Bot Status</b>\n\n"
        f"• Status: Online ✅\n"
        f"• Mode: {Config.BOT_MODE.title()}\n"
        f"• User ID: <code>{user.id}</code>\n"
        f"• Username: @{user.username or 'N/A'}\n"
        f"• Admin: {'Yes' if Config.is_admin(user.id) else 'No'}\n"
    )
    
    await update.message.reply_html(status_message)


async def echo_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /echo command."""
    user = update.effective_user
    
    if not context.args:
        await update.message.reply_text(
            "Please provide a message to echo!\n"
            "Usage: /echo <your message>"
        )
        return
    
    message_to_echo = " ".join(context.args)
    logger.info(f"User {user.id} used echo command: {message_to_echo}")
    
    await update.message.reply_text(f"🔄 Echo: {message_to_echo}")


async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /admin command (admin only)."""
    user = update.effective_user
    
    if not Config.is_admin(user.id):
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    logger.info(f"Admin {user.id} accessed admin panel")
    
    admin_message = (
        "🔧 <b>Admin Panel</b>\n\n"
        "Welcome to the admin panel!\n\n"
        "<b>Available admin features:</b>\n"
        "• Bot status monitoring\n"
        "• User management\n"
        "• System information\n\n"
        "More admin features can be added here."
    )
    
    await update.message.reply_html(admin_message)


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "❓ Unknown command. Use /help to see available commands."
    )