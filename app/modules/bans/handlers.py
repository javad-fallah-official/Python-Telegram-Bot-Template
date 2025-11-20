from aiogram.types import Message
from app.utils.decorators import require_join

@require_join
async def bans_info(message: Message):
    await message.answer("Bans module")
