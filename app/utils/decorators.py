import functools
from aiogram.types import Message
from app.config import settings

def admin_required(func):
    @functools.wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        if not message.from_user or not message.from_user.id:
            return
        if message.from_user.id not in settings.ADMIN_IDS:
            return
        return await func(message, *args, **kwargs)
    return wrapper

def require_join(func):
    setattr(func, "require_join", True)
    return func
