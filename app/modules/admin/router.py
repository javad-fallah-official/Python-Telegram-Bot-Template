from aiogram import Router
from aiogram.filters import Command
from .handlers import admin_help

router = Router()
router.message.register(admin_help, Command("admin"))
