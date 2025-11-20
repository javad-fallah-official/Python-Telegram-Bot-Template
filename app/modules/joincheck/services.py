import time
from typing import Dict, Tuple, List
from app.config import settings

_cache: Dict[Tuple[int, str], Tuple[bool, float]] = {}
_bot_admin_cache: Dict[str, Tuple[bool, float]] = {}
_enf_msgs: Dict[Tuple[int, int], List[int]] = {}

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

async def is_member_fresh(bot, channel: str, user_id: int) -> bool:
    key = (user_id, channel)
    now = time.time()
    try:
        member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
        status = getattr(member, "status", None)
        joined = status not in ("left", "kicked")
    except Exception:
        joined = False
    _cache[key] = (joined, now + float(getattr(settings, "JOINCHECK_CACHE_TTL", 300)))
    return joined
async def bot_is_admin(bot, channel: str) -> bool:
    key = channel.lstrip("@")
    now = time.time()
    ttl = 600.0
    val = _bot_admin_cache.get(key)
    if val and val[1] > now:
        return val[0]
    try:
        me = await bot.get_me()
        member = await bot.get_chat_member(chat_id=channel, user_id=me.id)
        status = getattr(member, "status", None)
        ok = status in ("administrator", "creator")
    except Exception:
        ok = False
    _bot_admin_cache[key] = (ok, now + ttl)
    return ok

async def ensure_joined(bot, user_id: int) -> bool:
    channels = list(getattr(settings, "REQUIRED_CHANNELS", []))
    if not channels:
        return True
    for ch in channels:
        ok = await is_member_fresh(bot, ch, user_id)
        if not ok:
            return False
    return True

async def verify_membership(bot, user_id: int, channels: List[str], fresh: bool = False) -> Tuple[bool, List[str]]:
    missing: List[str] = []
    for ch in channels:
        ok = await (is_member_fresh(bot, ch, user_id) if fresh else is_member(bot, ch, user_id))
        if not ok:
            missing.append(ch.lstrip("@"))
    passed = len(missing) == 0
    return passed, missing

def record_enforcement_message(chat_id: int, user_id: int, message_id: int) -> None:
    key = (chat_id, user_id)
    lst = _enf_msgs.get(key)
    if lst is None:
        _enf_msgs[key] = [message_id]
    else:
        lst.append(message_id)
        if len(lst) > 10:
            _enf_msgs[key] = lst[-10:]

async def cleanup_enforcement_messages(bot, chat_id: int, user_id: int) -> None:
    key = (chat_id, user_id)
    ids = _enf_msgs.pop(key, [])
    for mid in ids:
        try:
            await bot.delete_message(chat_id=chat_id, message_id=mid)
        except Exception:
            continue
