from aiogram import Router
from aiogram.filters import Command
from .handlers import start_handler

router = Router()
router.message.register(start_handler, Command("start"))
