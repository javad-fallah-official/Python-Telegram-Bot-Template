"""
Message handlers module.
Contains all message handlers for the Telegram bot.
"""

import logging
from aiogram import types

logger = logging.getLogger(__name__)


async def handle_message(message: types.Message) -> None:
    """Handle regular text messages."""
    user = message.from_user
    message_text = message.text
    
    logger.info(f"User {user.id} sent message: {message_text}")
    
    # Simple echo for demonstration
    response = (
        f"👋 Hi {user.first_name}!\n"
        f"You said: <i>{message_text}</i>\n\n"
        "Try using /help to see available commands!"
    )
    
    await message.answer(response)


async def handle_photo(message: types.Message) -> None:
    """Handle photo messages."""
    user = message.from_user
    logger.info(f"User {user.id} sent a photo")
    
    await message.answer(
        "📸 Nice photo! I received your image.\n"
        "Photo handling features can be implemented here."
    )


async def handle_document(message: types.Message) -> None:
    """Handle document messages."""
    user = message.from_user
    document = message.document
    logger.info(f"User {user.id} sent document: {document.file_name}")
    
    await message.answer(
        f"📄 Document received: {document.file_name}\n"
        "Document processing features can be implemented here."
    )


async def handle_voice(message: types.Message) -> None:
    """Handle voice messages."""
    user = message.from_user
    logger.info(f"User {user.id} sent a voice message")
    
    await message.answer(
        "🎤 Voice message received!\n"
        "Voice processing features can be implemented here."
    )