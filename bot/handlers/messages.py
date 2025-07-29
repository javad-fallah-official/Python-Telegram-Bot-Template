"""
Message handlers module.
Contains all message handlers for the Telegram bot.
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular text messages."""
    user = update.effective_user
    message_text = update.message.text
    
    logger.info(f"User {user.id} sent message: {message_text}")
    
    # Simple echo for demonstration
    response = (
        f"👋 Hi {user.first_name}!\n"
        f"You said: <i>{message_text}</i>\n\n"
        "Try using /help to see available commands!"
    )
    
    await update.message.reply_html(response)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle photo messages."""
    user = update.effective_user
    logger.info(f"User {user.id} sent a photo")
    
    await update.message.reply_text(
        "📸 Nice photo! I received your image.\n"
        "Photo handling features can be implemented here."
    )


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle document messages."""
    user = update.effective_user
    document = update.message.document
    logger.info(f"User {user.id} sent document: {document.file_name}")
    
    await update.message.reply_text(
        f"📄 Document received: {document.file_name}\n"
        "Document processing features can be implemented here."
    )


async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle voice messages."""
    user = update.effective_user
    logger.info(f"User {user.id} sent a voice message")
    
    await update.message.reply_text(
        "🎤 Voice message received!\n"
        "Voice processing features can be implemented here."
    )