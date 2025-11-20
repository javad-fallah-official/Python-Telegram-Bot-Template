"""Error handlers for the Telegram bot.
"""

import logging
import traceback
from aiogram import types
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

logger = logging.getLogger(__name__)


async def error_handler(event: types.ErrorEvent) -> None:
    """Handle errors that occur during bot operation."""
    
    # Get user info if available
    user_id = None
    chat_id = None
    if event.update and hasattr(event.update, 'message') and event.update.message:
        if event.update.message.from_user:
            user_id = event.update.message.from_user.id
        if event.update.message.chat:
            chat_id = event.update.message.chat.id
    elif event.update and hasattr(event.update, 'callback_query') and event.update.callback_query:
        if event.update.callback_query.from_user:
            user_id = event.update.callback_query.from_user.id
        if event.update.callback_query.message and event.update.callback_query.message.chat:
            chat_id = event.update.callback_query.message.chat.id
    
    # Log the error with structured data
    logger.error(
        f"Exception while handling an update: {event.exception}",
        extra={
            'user_id': user_id,
            'chat_id': chat_id,
            'update_type': type(event.update).__name__ if event.update else 'Unknown',
            'error_type': type(event.exception).__name__
        }
    )
    
    # Handle specific error types
    if isinstance(event.exception, TelegramRetryAfter):
        logger.warning(f"Rate limit hit, retry after {event.exception.retry_after} seconds")
        return
    
    if isinstance(event.exception, TelegramBadRequest):
        logger.warning(f"Bad request: {event.exception}")
        return
    
    # Send user-friendly error message if possible
    if (event.update and hasattr(event.update, 'message') and 
        event.update.message and event.update.message.chat):
        try:
            await event.update.message.answer(
                "❌ Sorry, an error occurred while processing your request. "
                "The issue has been logged and will be investigated."
            )
        except Exception as send_error:
            logger.error(f"Failed to send error message to user: {send_error}")
    
    # Log full traceback for debugging
    if event.exception:
        tb_list = traceback.format_exception(
            type(event.exception), 
            event.exception, 
            event.exception.__traceback__
        )
        tb_string = ''.join(tb_list)
        logger.debug(f"Full traceback:\n{tb_string}")