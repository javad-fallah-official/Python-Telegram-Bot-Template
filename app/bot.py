import asyncio
from aiogram import Bot, Dispatcher
from app.config import settings
from app.modules import admin, bans, joincheck, referral, dev_tools, general
from app.middlewares import admin_middleware, ban_middleware, joincheck_middleware
from app.db.base import init_db, DATABASE_URL
from app.utils.logger import get_logger

logger = get_logger("app")
logger.info("🚀 Starting Telegram Bot")
logger.info(f"⚙️ Mode: {settings.BOT_MODE}")
logger.info(f"🗄️ Database: {DATABASE_URL.split('://')[0]}")
logger.info(f"👤 Admins: {settings.ADMIN_IDS}")
logger.info(f"📢 Required channels: {getattr(settings, 'REQUIRED_CHANNELS', [])}")
bot = Bot(token=settings.BOT_TOKEN)
dp = Dispatcher()

dp.message.middleware(ban_middleware.BanMiddleware())
dp.message.middleware(joincheck_middleware.JoinCheckMiddleware())
dp.message.middleware(admin_middleware.AdminMiddleware())
dp.callback_query.middleware(joincheck_middleware.JoinCheckMiddleware())

plugins = [admin, bans, joincheck, referral, dev_tools, general]
feature_map = {
    "admin": "admin_tools",
    "bans": "bans",
    "joincheck": "join_check",
    "referral": "referral",
    "dev_tools": "admin_tools",
    "general": "general",
}
GREEN = "\033[32m"
RED = "\033[31m"
RESET = "\033[0m"
module_states = []
for plugin in plugins:
    plugin_key = plugin.__name__.split(".")[-1].lower()
    feature_name = feature_map.get(plugin_key, None)
    enabled = bool(feature_name and getattr(settings.FEATURES, feature_name, True))
    module_states.append((plugin_key, enabled))
    if enabled:
        dp.include_router(plugin.router)
labels = ", ".join([f"{k}:{GREEN}on{RESET}" if v else f"{k}:{RED}off{RESET}" for k, v in module_states])
logger.info("🔌 Modules: " + labels)

async def main():
    logger.info("🧱 Initializing database...")
    await init_db()
    logger.info("✅ Database initialized")
    if settings.BOT_MODE == "polling":
        logger.info("📡 Starting polling")
        await dp.start_polling(bot)
    elif settings.BOT_MODE == "webhook":
        logger.info("🔗 Starting webhook")
        await dp.start_webhook(
            bot,
            webhook_path="/webhook",
            on_startup=None,
            on_shutdown=None,
            skip_updates=True,
        )

if __name__ == "__main__":
    asyncio.run(main())
