from aiogram.types import Message
from app.utils.decorators import admin_required

@admin_required
async def admin_help(message: Message, **kwargs):
    await message.answer("Admin panel")

async def admin_forbidden(message: Message):
    text = (
        "🚫 <b>Access Denied</b>\n\n"
        "You don't have permission to use this command.\n"
        "This feature is restricted to administrators only.\n\n"
        "If you believe this is an error, please contact the bot administrators."
    )
    await message.answer(text, parse_mode="HTML")
