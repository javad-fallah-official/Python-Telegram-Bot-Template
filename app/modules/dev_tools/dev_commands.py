from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from app.utils.decorators import dev_only

router = Router()

@router.message(Command("dev_info"))
@dev_only
async def dev_info(message: Message, **kwargs):
    """Show current chat and user IDs"""
    thread_id = getattr(message, "message_thread_id", None)
    info = f"Chat ID: {message.chat.id}\nUser ID: {message.from_user.id}"
    if thread_id is not None:
        info += f"\nThread ID: {thread_id}"
    await message.answer(info)
