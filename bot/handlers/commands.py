"""
Command handlers module.
Contains all
Command handlers for the Telegram bot.
"""

import time
from telegram import Update
from telegram.ext import ContextTypes
from core.config import Config
from core.logger import get_logger, log_user_action, log_error, log_performance, log_security_event

logger = get_logger('commands')


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command."""
    start_time = time.time()
    
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        
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
        
        await update.message.reply_text(welcome_message)
        
        # Log performance
        duration = time.time() - start_time
        log_performance('start_command', duration, {
            'user_id': user.id,
            'chat_id': chat_id,
            'message_length': len(welcome_message)
        })
        
        logger.info(f"Start command executed for user {user.id} ({user.first_name})")
        
    except Exception as e:
        log_error(e, 'start_command', user_id=update.effective_user.id if update.effective_user else None)
        await update.message.reply_text("❌ An error occurred while processing your request.")


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
    start_time = time.time()
    
    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Check admin permissions
        if not Config.is_admin(user.id):
            log_security_event(
                'unauthorized_admin_access',
                user_id=user.id,
                details=f"User {user.first_name} ({user.username}) attempted to access admin panel"
            )
            await update.message.reply_text("❌ You don't have permission to use this command.")
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
        
        await update.message.reply_text(admin_message, parse_mode='Markdown')
        
        # Log performance
        duration = time.time() - start_time
        log_performance('admin_command', duration, {
            'user_id': user.id,
            'chat_id': chat_id,
            'admin_access': True
        })
        
        logger.info(f"Admin panel accessed by user {user.id} ({user.first_name})")
        
    except Exception as e:
        log_error(e, 'admin_command', user_id=update.effective_user.id if update.effective_user else None)
        await update.message.reply_text("❌ An error occurred while processing your request.")


async def unknown_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle unknown commands."""
    await update.message.reply_text(
        "❓ Unknown command. Use /help to see available commands."
    )