"""Command handlers for the Telegram bot."""

import logging
import time
from aiogram.types import Message
from core.config import Config
from core.logger import log_user_action, log_performance, log_error

logger = logging.getLogger(__name__)


async def start_command(message: Message) -> None:
    """Handle the /start command."""
    start_time = time.time()
    
    try:
        user = message.from_user
        chat_id = message.chat.id
        
        # Log user action
        log_user_action(
            user_id=user.id,
            action='start',
            details=f"First name: {user.first_name}, Username: {user.username}",
            chat_id=chat_id
        )
        
        welcome_message = (
            f"👋 Hello {user.first_name}!\n\n"
            "Welcome to the Telegram Bot Template! 🤖\n\n"
            "Available commands:\n"
            "• /help - Show help message\n"
            "• /status - Check bot status\n"
            "• /echo <message> - Echo your message\n"
        )
        
        if Config.is_admin(user.id):
            welcome_message += "• /admin - Admin panel (admin only)\n"
        
        await message.answer(welcome_message)
        
        # Log performance
        duration = time.time() - start_time
        log_performance('start_command', duration, {
            'user_id': user.id,
            'chat_id': chat_id,
            'message_length': len(welcome_message)
        })
        
        logger.info(f"Start command executed for user {user.id} ({user.first_name})")
        
    except Exception as e:
        log_error(e, 'start_command', user_id=message.from_user.id if message.from_user else None)
        await message.answer("❌ An error occurred while processing your request.")


async def help_command(message: Message) -> None:
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
    
    await message.answer(help_text, parse_mode='HTML')


async def status_command(message: Message) -> None:
    """Handle the /status command."""
    user = message.from_user
    logger.info(f"User {user.id} requested bot status")
    
    status_message = (
        "🟢 <b>Bot Status</b>\n\n"
        f"• Status: Online ✅\n"
        f"• Mode: {Config.BOT_MODE.title()}\n"
        f"• User ID: <code>{user.id}</code>\n"
        f"• Username: @{user.username or 'N/A'}\n"
        f"• Admin: {'Yes' if Config.is_admin(user.id) else 'No'}\n"
    )
    
    await message.answer(status_message, parse_mode='HTML')


async def echo_command(message: Message) -> None:
    """Handle the /echo command."""
    user = message.from_user
    
    # Extract command arguments from message text
    command_args = message.text.split()[1:] if message.text else []
    
    if not command_args:
        await message.answer(
            "Please provide a message to echo!\n"
            "Usage: /echo <your message>"
        )
        return
    
    message_to_echo = " ".join(command_args)
    logger.info(f"User {user.id} used echo command: {message_to_echo}")
    
    await message.answer(f"🔄 Echo: {message_to_echo}")


async def admin_command(message: Message) -> None:
    """Handle the /admin command (admin only)."""
    start_time = time.time()
    
    try:
        user = message.from_user
        chat_id = message.chat.id
        
        # Check admin permissions
        if not Config.is_admin(user.id):
            logger.warning(f"User {user.first_name} ({user.username}) attempted to access admin panel")
            await message.answer("❌ You don't have permission to use this command.")
            return
        
        # Log admin action
        log_user_action(
            user_id=user.id,
            action='admin_panel_access',
            details="Accessed admin panel",
            chat_id=chat_id
        )
        
        admin_message = (
            "🔧 **Admin Panel**\n\n"
            "Bot Status: ✅ Running\n"
            f"Mode: {Config.BOT_MODE}\n"
            f"Debug: {'Enabled' if Config.DEBUG else 'Disabled'}\n"
            f"Log Level: {Config.LOG_LEVEL}\n\n"
            "Available admin commands:\n"
            "• /status - Detailed bot status\n"
            "• View logs in the logs/ directory\n"
        )
        
        await message.answer(admin_message, parse_mode='Markdown')
        
        # Log performance
        duration = time.time() - start_time
        log_performance('admin_command', duration, {
            'user_id': user.id,
            'chat_id': chat_id,
            'admin_access': True
        })
        
        logger.info(f"Admin panel accessed by user {user.id} ({user.first_name})")
        
    except Exception as e:
        log_error(e, 'admin_command', user_id=message.from_user.id if message.from_user else None)
        await message.answer("❌ An error occurred while processing your request.")


async def unknown_command(message: Message) -> None:
    """Handle unknown commands."""
    await message.answer(
        "❓ Unknown command. Use /help to see available commands."
    )