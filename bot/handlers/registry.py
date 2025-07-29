"""
Handler registry module.
Registers all handlers with the bot application.
"""

import logging
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    CallbackQueryHandler
)

from .commands import (
    start_command,
    help_command,
    status_command,
    echo_command,
    admin_command,
    unknown_command
)
from .messages import (
    handle_message,
    handle_photo,
    handle_document,
    handle_voice
)
from .errors import error_handler

logger = logging.getLogger(__name__)


def register_handlers(application: Application) -> None:
    """Register all handlers with the application."""
    
    # Command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status_command))
    application.add_handler(CommandHandler("echo", echo_command))
    application.add_handler(CommandHandler("admin", admin_command))
    
    # Message handlers
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message)
    )
    application.add_handler(
        MessageHandler(filters.PHOTO, handle_photo)
    )
    application.add_handler(
        MessageHandler(filters.Document.ALL, handle_document)
    )
    application.add_handler(
        MessageHandler(filters.VOICE, handle_voice)
    )
    
    # Unknown command handler (should be last)
    application.add_handler(
        MessageHandler(filters.COMMAND, unknown_command)
    )
    
    # Error handler
    application.add_error_handler(error_handler)
    
    logger.info("All handlers registered with application")