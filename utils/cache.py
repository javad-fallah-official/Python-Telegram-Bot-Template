"""
Async cache utilities.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta


class AsyncCache:
    """Simple async cache implementation."""
    
    def __init__(self, default_ttl: int = 300):  # 5 minutes default
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.default_ttl = default_ttl
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        if key in self.cache:
            item = self.cache[key]
            if datetime.now() < item['expires']:
                return item['value']
            else:
                del self.cache[key]
        return None
    
    async def set(self, key: str, value: Any, ttl: int = None) -> None:
        """Set value in cache."""
        ttl = ttl or self.default_ttl
        expires = datetime.now() + timedelta(seconds=ttl)
        self.cache[key] = {
            'value': value,
            'expires': expires
        }
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    async def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()
    
    async def cleanup_expired(self) -> None:
        """Remove expired items from cache."""
        now = datetime.now()
        expired_keys = [
            key for key, item in self.cache.items()
            if now >= item['expires']
        ]
        for key in expired_keys:
            del self.cache[key]


class MemoryCache:
    """Simple synchronous memory cache for testing."""
    
    def __init__(self):
        self.cache: Dict[str, Any] = {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get value from cache."""
        return self.cache.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set value in cache."""
        self.cache[key] = value
    
    def delete(self, key: str) -> bool:
        """Delete value from cache."""
        if key in self.cache:
            del self.cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache."""
        self.cache.clear()