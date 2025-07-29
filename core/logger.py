"""
Comprehensive logging configuration for the Telegram bot.
Provides structured logging with rotation, filtering, and multiple output formats.
"""

import logging
import logging.handlers
import sys
import os
import json
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any
from .config import Config


class ColoredFormatter(logging.Formatter):
    """Colored formatter for console output."""
    
    # Color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }
    
    def format(self, record):
        # Add color to levelname
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        
        return super().format(record)


class JSONFormatter(logging.Formatter):
    """JSON formatter for structured logging."""
    
    def format(self, record):
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        # Add extra fields if present
        if hasattr(record, 'user_id'):
            log_entry['user_id'] = record.user_id
        if hasattr(record, 'chat_id'):
            log_entry['chat_id'] = record.chat_id
        if hasattr(record, 'command'):
            log_entry['command'] = record.command
        if hasattr(record, 'error_type'):
            log_entry['error_type'] = record.error_type
        
        # Add exception info if present
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)


class TelegramLogFilter(logging.Filter):
    """Custom filter for Telegram-specific logging."""
    
    def filter(self, record):
        # Filter out noisy logs from external libraries
        if record.name.startswith('httpx') and record.levelno < logging.WARNING:
            return False
        if record.name.startswith('urllib3') and record.levelno < logging.WARNING:
            return False
        if record.name.startswith('telegram.ext') and record.levelno < logging.INFO:
            return False
        
        return True


class BotLogger:
    """Enhanced logging manager for the Telegram bot."""
    
    def __init__(self, log_level: Optional[str] = None):
        self.log_level = log_level or Config.LOG_LEVEL
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # Create main logger
        self.logger = logging.getLogger('telegram_bot')
        self.logger.setLevel(getattr(logging, self.log_level))
        
        # Clear existing handlers
        self.logger.handlers.clear()
        logging.getLogger().handlers.clear()
        
        self._setup_handlers()
        self._setup_external_loggers()
    
    def _setup_handlers(self):
        """Set up all logging handlers."""
        
        # Console handler with colors
        console_handler = logging.StreamHandler(sys.stdout)
        console_formatter = ColoredFormatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s',
            datefmt='%H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        console_handler.addFilter(TelegramLogFilter())
        self.logger.addHandler(console_handler)
        
        # Main log file with rotation
        main_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'bot.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_formatter = logging.Formatter(
            fmt='%(asctime)s | %(levelname)-8s | %(name)-20s | %(funcName)-15s:%(lineno)-4d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        main_file_handler.setFormatter(main_formatter)
        self.logger.addHandler(main_file_handler)
        
        # Error log file (errors and above only)
        error_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'errors.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(main_formatter)
        self.logger.addHandler(error_file_handler)
        
        # JSON structured log file
        json_file_handler = logging.handlers.RotatingFileHandler(
            self.log_dir / 'bot.json',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=3,
            encoding='utf-8'
        )
        json_file_handler.setFormatter(JSONFormatter())
        self.logger.addHandler(json_file_handler)
        
        # Debug log file (only in debug mode)
        if Config.DEBUG:
            debug_file_handler = logging.handlers.RotatingFileHandler(
                self.log_dir / 'debug.log',
                maxBytes=20*1024*1024,  # 20MB
                backupCount=2,
                encoding='utf-8'
            )
            debug_file_handler.setLevel(logging.DEBUG)
            debug_formatter = logging.Formatter(
                fmt='%(asctime)s | %(levelname)-8s | %(name)-25s | %(funcName)-20s:%(lineno)-4d | %(message)s',
                datefmt='%Y-%m-%d %H:%M:%S'
            )
            debug_file_handler.setFormatter(debug_formatter)
            self.logger.addHandler(debug_file_handler)
    
    def _setup_external_loggers(self):
        """Configure external library loggers."""
        
        # Telegram library
        telegram_logger = logging.getLogger('telegram')
        telegram_logger.setLevel(logging.INFO)
        
        # HTTP libraries
        logging.getLogger('httpx').setLevel(logging.WARNING)
        logging.getLogger('urllib3').setLevel(logging.WARNING)
        logging.getLogger('aiohttp').setLevel(logging.WARNING)
        
        # FastAPI/Uvicorn (for webhook mode)
        logging.getLogger('uvicorn').setLevel(logging.INFO)
        logging.getLogger('fastapi').setLevel(logging.INFO)
        
        # Database
        logging.getLogger('aiosqlite').setLevel(logging.WARNING)
    
    def get_logger(self, name: str = None) -> logging.Logger:
        """Get a logger instance."""
        if name:
            return logging.getLogger(f'telegram_bot.{name}')
        return self.logger
    
    def log_user_action(self, user_id: int, action: str, details: str = None, chat_id: int = None):
        """Log user actions with structured data."""
        logger = self.get_logger('user_actions')
        extra = {
            'user_id': user_id,
            'command': action
        }
        if chat_id:
            extra['chat_id'] = chat_id
        
        message = f"User {user_id} performed action: {action}"
        if details:
            message += f" | Details: {details}"
        
        logger.info(message, extra=extra)
    
    def log_error(self, error: Exception, context: str = None, user_id: int = None):
        """Log errors with structured data."""
        logger = self.get_logger('errors')
        extra = {
            'error_type': type(error).__name__
        }
        if user_id:
            extra['user_id'] = user_id
        
        message = f"Error in {context or 'unknown context'}: {str(error)}"
        logger.error(message, exc_info=error, extra=extra)
    
    def log_performance(self, operation: str, duration: float, details: Dict[str, Any] = None):
        """Log performance metrics."""
        logger = self.get_logger('performance')
        message = f"Operation '{operation}' took {duration:.3f}s"
        if details:
            message += f" | Details: {json.dumps(details)}"
        logger.info(message)
    
    def log_security_event(self, event_type: str, user_id: int, details: str = None):
        """Log security-related events."""
        logger = self.get_logger('security')
        extra = {
            'user_id': user_id,
            'error_type': 'security_event'
        }
        
        message = f"Security event '{event_type}' for user {user_id}"
        if details:
            message += f" | Details: {details}"
        
        logger.warning(message, extra=extra)


# Global logger instance
_bot_logger: Optional[BotLogger] = None


def setup_logging(level: Optional[str] = None) -> logging.Logger:
    """
    Set up comprehensive logging configuration for the bot.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        
    Returns:
        Configured logger instance
    """
    global _bot_logger
    
    if _bot_logger is None:
        _bot_logger = BotLogger(level)
    
    return _bot_logger.get_logger()


def get_logger(name: str = None) -> logging.Logger:
    """
    Get a logger instance.
    
    Args:
        name: Logger name (will be prefixed with 'telegram_bot.')
        
    Returns:
        Logger instance
    """
    global _bot_logger
    
    if _bot_logger is None:
        _bot_logger = BotLogger()
    
    return _bot_logger.get_logger(name)


def log_user_action(user_id: int, action: str, details: str = None, chat_id: int = None):
    """Log user actions with structured data."""
    global _bot_logger
    if _bot_logger:
        _bot_logger.log_user_action(user_id, action, details, chat_id)


def log_error(error: Exception, context: str = None, user_id: int = None):
    """Log errors with structured data."""
    global _bot_logger
    if _bot_logger:
        _bot_logger.log_error(error, context, user_id)


def log_performance(operation: str, duration: float, details: Dict[str, Any] = None):
    """Log performance metrics."""
    global _bot_logger
    if _bot_logger:
        _bot_logger.log_performance(operation, duration, details)


def log_security_event(event_type: str, user_id: int, details: str = None):
    """Log security-related events."""
    global _bot_logger
    if _bot_logger:
        _bot_logger.log_security_event(event_type, user_id, details)