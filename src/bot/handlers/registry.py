"""
Handler registry module.
Registers all handlers with the bot dispatcher.
"""

import logging
from aiogram import Dispatcher, F
from aiogram.filters import Command, CommandStart

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


def register_handlers(dp: Dispatcher) -> None:
    """Register all handlers with the dispatcher."""
    
    # Command handlers
    dp.message.register(start_command, CommandStart())
    dp.message.register(help_command, Command("help"))
    dp.message.register(status_command, Command("status"))
    dp.message.register(echo_command, Command("echo"))
    dp.message.register(admin_command, Command("admin"))
    
    # Message handlers
    dp.message.register(handle_message, F.text & ~F.text.startswith("/"))
    dp.message.register(handle_photo, F.photo)
    dp.message.register(handle_document, F.document)
    dp.message.register(handle_voice, F.voice)
    
    # Unknown command handler (should be last)
    dp.message.register(unknown_command, F.text.startswith("/"))
    
    # Error handler
    dp.errors.register(error_handler)
    
    logger.info("All handlers registered with dispatcher")