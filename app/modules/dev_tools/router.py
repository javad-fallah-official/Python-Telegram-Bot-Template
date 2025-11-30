from aiogram import Router, F
from aiogram.filters import Command
from .handlers import show_tables, show_table, drop_tables, clear_tables, sql_exec, confirm_handler, dev_commands_list
from . import dev_commands as legacy

router = legacy.router

router.message.register(show_tables, Command("show_tables"))
router.message.register(show_table, Command("show_table"))
router.message.register(drop_tables, Command("drop_tables"))
router.message.register(clear_tables, Command("clear_tables"))
router.message.register(sql_exec, Command("sql"))
router.message.register(confirm_handler, F.text.startswith("CONFIRM"))
router.message.register(dev_commands_list, Command("dev_commands"))
