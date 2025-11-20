from aiogram import Router
from aiogram.filters import CommandStart
from .handlers import start_handler

router = Router()
router.message.register(start_handler, CommandStart())
