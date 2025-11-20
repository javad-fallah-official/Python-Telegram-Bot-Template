from aiogram import Router
from .handlers import admin_help

router = Router()
router.message.register(admin_help, commands=["admin"])

