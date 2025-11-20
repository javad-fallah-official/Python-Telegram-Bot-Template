import re
from aiogram.types import Message
from .services import save_referral

async def start_handler(message: Message):
    match = re.search(r"/start (\d+)", message.text or "")
    if match:
        referrer_id = int(match.group(1))
        await save_referral(message.from_user.id, referrer_id)
    await message.answer("Welcome")

