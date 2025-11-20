from aiogram import Router
from .handlers import start_handler

router = Router()
router.message.register(start_handler, commands=["start"])

