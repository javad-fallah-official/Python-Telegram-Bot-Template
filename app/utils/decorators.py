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
