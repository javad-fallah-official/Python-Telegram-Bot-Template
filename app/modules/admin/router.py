from aiogram import Router
from aiogram.filters import Command
from .handlers import admin_help, admin_commands_list

router = Router()
router.message.register(admin_help, Command("admin"))
router.message.register(admin_commands_list, Command("admin_commands"))
