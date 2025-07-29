"""Error handlers for the Telegram bot.
"""

import traceback
from telegram import Update
from telegram.ext import ContextTypes
from core.logger import get_logger, log_error

logger = get_logger('errors')


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors that occur during bot operation."""
    
    # Get user info if available
    user_id = None
    chat_id = None
    if isinstance(update, Update) and update.effective_user:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id if update.effective_chat else None
    
    # Log the error with structured data
    log_error(
        error=context.error,
        context='telegram_bot_operation',
        user_id=user_id
    )
    
    # Log additional context
    logger.error(
        f"Exception while handling an update: {context.error}",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'update_type': type(update).__name__ if update else 'Unknown',
            'error_type': type(context.error).__name__
        }
    )
    
    # Send user-friendly error message if possible
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Sorry, an error occurred while processing your request. "
                "The issue has been logged and will be investigated."
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message to user: {send_error}")
    
    # Log full traceback for debugging
    if context.error:
        tb_list = traceback.format_exception(
            type(context.error), 
            context.error, 
            context.error.__traceback__
        )
        tb_string = ''.join(tb_list)
        logger.debug(f"Full traceback:\n{tb_string}")


async def timeout_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle timeout errors."""
    logger.warning("Request timeout occurred")
    
    if update.effective_message:
        try:
            await update.effective_message.reply_text(
                "⏱️ Request timed out. Please try again."
            )
        except Exception as e:
            logger.error(f"Failed to send timeout message: {e}")


async def rate_limit_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle rate limiting errors."""
    logger.warning(f"Rate limit hit for user {update.effective_user.id}")
    
    if update.effective_message:
        try:
            await update.effective_message.reply_text(
                "🚫 You're sending messages too quickly. Please slow down."
            )
        except Exception as e:
            logger.error(f"Failed to send rate limit message: {e}")