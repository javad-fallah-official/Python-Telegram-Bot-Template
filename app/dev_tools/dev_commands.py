from aiogram import Router
from aiogram.types import Message
from app.utils.decorators import admin_required

router = Router()

@router.message()
@admin_required
async def dev_info(message: Message):
    thread_id = getattr(message, "message_thread_id", None)
    info = f"Chat ID: {message.chat.id}\nUser ID: {message.from_user.id}"
    if thread_id is not None:
        info += f"\nThread ID: {thread_id}"
    await message.answer(info)
