"""
Error handlers module.
Contains error handling functionality for the Telegram bot.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle errors that occur during bot operation."""
    logger.error(f"Exception while handling an update: {context.error}")
    
    # If we have an update with a message, try to inform the user
    if isinstance(update, Update) and update.effective_message:
        try:
            await update.effective_message.reply_text(
                "❌ Sorry, an error occurred while processing your request. "
                "Please try again later."
            )
        except Exception as e:
            logger.error(f"Failed to send error message to user: {e}")


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