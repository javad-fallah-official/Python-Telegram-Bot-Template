"""Core modules for the Telegram bot."""

from .config import Config
from .logger import BotLogger, get_logger
from .db_factory import UnifiedDatabase, DatabaseFactory
from .database import Database  # Keep for backward compatibility
from .postgres import PostgreSQLDatabase
from .middleware import RateLimiter, admin_required, rate_limit
from .runner import BotRunner

# Use unified database as default
db = UnifiedDatabase()

__all__ = [
    'Config',
    'BotLogger',
    'get_logger',
    'UnifiedDatabase',
    'DatabaseFactory',
    'Database',
    'PostgreSQLDatabase',
    'RateLimiter',
    'admin_required',
    'rate_limit',
    'BotRunner',
    'db'
]