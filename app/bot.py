import asyncio
from aiogram import Bot, Dispatcher
from app.config import settings
from app.modules import admin, bans, joincheck, referral, dev_tools
from app.middlewares import admin_middleware, ban_middleware, joincheck_middleware
from app.db.base import init_db

bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(ban_middleware.BanMiddleware())
dp.message.middleware(joincheck_middleware.JoinCheckMiddleware())
dp.message.middleware(admin_middleware.AdminMiddleware())

plugins = [admin, bans, joincheck, referral, dev_tools]
feature_map = {
    "admin": "admin_tools",
    "bans": "bans",
    "joincheck": "join_check",
    "referral": "referral",
    "dev_tools": "admin_tools",
}
for plugin in plugins:
    plugin_key = plugin.__name__.split(".")[-1].lower()
    feature_name = feature_map.get(plugin_key, None)
    if feature_name and getattr(settings.FEATURES, feature_name, True):
        dp.include_router(plugin.router)

async def main():
    await init_db()
    if settings.BOT_MODE == "polling":
        await dp.start_polling(bot)
    elif settings.BOT_MODE == "webhook":
        await dp.start_webhook(
            bot,
            webhook_path="/webhook",
            on_startup=None,
            on_shutdown=None,
            skip_updates=True,
        )

if __name__ == "__main__":
    asyncio.run(main())
