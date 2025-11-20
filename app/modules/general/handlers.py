from aiogram.types import Message
from app.utils.decorators import require_join

@require_join
async def start_handler(message: Message):
    await message.answer("Welcome")

@require_join
async def help_handler(message: Message):
    await message.answer("Available: /start, /help")
