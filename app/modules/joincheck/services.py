import time
from typing import Dict, Tuple
from app.config import settings

_cache: Dict[Tuple[int, str], Tuple[bool, float]] = {}

async def is_member(bot, channel: str, user_id: int) -> bool:
    key = (user_id, channel)
    ttl = int(getattr(settings, "JOINCHECK_CACHE_TTL", 300))
    now = time.time()
    val = _cache.get(key)
    if val and val[1] > now:
        return val[0]
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        status = getattr(member, "status", None)
        joined = status not in ("left", "kicked")
    except Exception:
        joined = False
    _cache[key] = (joined, now + ttl)
    return joined

async def ensure_joined(bot, user_id: int) -> bool:
    channels = list(getattr(settings, "REQUIRED_CHANNELS", []))
    if not channels:
        return True
    for ch in channels:
        ok = await is_member(bot, ch, user_id)
        if not ok:
            return False
    return True
