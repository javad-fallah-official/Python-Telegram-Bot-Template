import functools
from aiogram.types import Message
from app.config import settings

def admin_required(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        return await func(*args, **kwargs)
    setattr(wrapper, "admin_only", True)
    setattr(func, "admin_only", True)
    return wrapper

def require_join(func):
    setattr(func, "require_join", True)
    return func

def dev_only(func):
    async def wrapper(message: Message, *args, **kwargs):
        uid = getattr(getattr(message, "from_user", None), "id", None)
        devs = set(getattr(settings, "DEV_USERS", []))
        if uid not in devs:
            await message.answer("Only developers may use this command.")
            return
        return await func(message, *args, **kwargs)
    return wrapper
