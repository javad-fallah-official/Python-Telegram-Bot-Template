from aiogram.types import Message
from app.utils.decorators import admin_required

@admin_required
async def admin_help(message: Message):
    await message.answer("Admin panel")
