import time
from typing import Dict, Any

pending_confirmations: Dict[str, Dict[str, Any]] = {}

def create_token(user_id: int, action: str, meta: Dict[str, Any], ttl: int) -> str:
    import secrets
    token = secrets.token_hex(3)
    pending_confirmations[token] = {"user_id": user_id, "action": action, "meta": meta, "expires_at": time.time() + ttl}
    return token

def validate_token(user_id: int, action: str, token: str) -> Dict[str, Any] | None:
    info = pending_confirmations.get(token)
    if not info:
        return None
    if info["user_id"] != user_id:
        return None
    if info["action"] != action:
        return None
    if info["expires_at"] < time.time():
        pending_confirmations.pop(token, None)
        return None
    return info

def consume_token(token: str) -> None:
    pending_confirmations.pop(token, None)
