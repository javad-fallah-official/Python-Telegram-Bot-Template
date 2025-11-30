from aiogram.types import Message
from app.utils.decorators import admin_required
from app.utils.router_utils import get_router_commands

@admin_required
async def admin_help(message: Message, **kwargs):
    """Admin panel help"""
    await message.answer("Admin panel")

@admin_required
async def admin_commands_list(message: Message, **kwargs):
    """List available admin commands"""
    from .router import router
    commands = get_router_commands(router)
    text = f"📋 <b>Admin Commands</b>\n\n{commands}"
    await message.answer(text, parse_mode="HTML")

async def admin_forbidden(message: Message):
    """Access denied message"""
    text = (
        "🚫 <b>Access Denied</b>\n\n"
        "You don't have permission to use this command.\n"
        "This feature is restricted to administrators only.\n\n"
        "If you believe this is an error, please contact the bot administrators."
    )
    await message.answer(text, parse_mode="HTML")
