"""Base service interface for bot services."""

from abc import ABC, abstractmethod
from aiogram import Bot, Dispatcher


class BotService(ABC):
    """Abstract base class for bot services."""
    
    def __init__(self, bot: Bot, dp: Dispatcher):
        self.bot = bot
        self.dp = dp
        self._running = False
    
    @property
    def is_running(self) -> bool:
        """Check if the service is running."""
        return self._running
    
    @abstractmethod
    async def start(self) -> None:
        """Start the service."""
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """Stop the service."""
        pass
    
    async def setup(self) -> None:
        """Setup the service (optional override)."""
        pass
    
    async def cleanup(self) -> None:
        """Cleanup the service (optional override)."""
        pass