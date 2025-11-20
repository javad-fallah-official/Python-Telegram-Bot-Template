from aiogram import Router
from aiogram.filters import Command
from .handlers import bans_info

router = Router()
router.message.register(bans_info, Command("bans"))
