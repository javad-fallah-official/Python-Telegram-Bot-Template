from aiogram import Router, F
from aiogram.filters import Command
from .handlers import start_handler, help_handler

router = Router()
router.message.register(start_handler, F.text.regexp(r"^/start(@\w+)?$"))
router.message.register(help_handler, Command("help"))
