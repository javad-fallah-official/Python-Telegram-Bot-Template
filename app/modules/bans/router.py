from aiogram import Router
from .handlers import bans_info

router = Router()
router.message.register(bans_info, commands=["bans"])

