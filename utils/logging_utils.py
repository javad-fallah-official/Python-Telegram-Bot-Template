"""
Logging utilities and decorators for the Telegram bot.
Provides convenient functions for common logging patterns.
"""

import time
import functools
from typing import Callable, Any, Dict, Optional
from aiogram.types import Update, Message
from core.config import Config
from core.logger import get_logger, log_user_action, log_error, log_performance

logger = get_logger('utils.logging')


def log_command_execution(command_name: str = None):
    """
    Decorator to automatically log command execution with performance metrics.
    
    Args:
        command_name: Optional command name override
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            start_time = time.time()
            cmd_name = command_name or func.__name__.replace('_command', '').replace('_handler', '')
            
            user = message.from_user
            chat_id = message.chat.id
            
            try:
                # Log command start
                log_user_action(
                    user_id=user.id,
                    action=cmd_name,
                    details=f"Command executed by {user.first_name} ({user.username})",
                    chat_id=chat_id
                )
                
                # Execute the command
                result = await func(message, *args, **kwargs)
                
                # Log successful completion
                duration = time.time() - start_time
                log_performance(f'{cmd_name}_command', duration, {
                    'user_id': user.id,
                    'chat_id': chat_id,
                    'success': True
                })
                
                logger.info(f"Command '{cmd_name}' completed successfully for user {user.id}")
                return result
                
            except Exception as e:
                # Log error
                log_error(e, f'{cmd_name}_command', user_id=user.id)
                
                # Log failed performance
                duration = time.time() - start_time
                log_performance(f'{cmd_name}_command', duration, {
                    'user_id': user.id,
                    'chat_id': chat_id,
                    'success': False,
                    'error': str(e)
                })
                
                # Re-raise the exception
                raise
        
        return wrapper
    return decorator


def log_message_processing(message_type: str = "message"):
    """
    Decorator to log message processing activities.
    
    Args:
        message_type: Type of message being processed
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(message: Message, *args, **kwargs):
            start_time = time.time()
            
            user = message.from_user
            chat_id = message.chat.id
            
            try:
                # Log message processing start
                details = f"Processing {message_type}"
                if message and message.text:
                    details += f" with text length: {len(message.text)}"
                
                log_user_action(
                    user_id=user.id,
                    action=f'process_{message_type}',
                    details=details,
                    chat_id=chat_id
                )
                
                # Execute the handler
                result = await func(message, *args, **kwargs)
                
                # Log successful processing
                duration = time.time() - start_time
                log_performance(f'process_{message_type}', duration, {
                    'user_id': user.id,
                    'chat_id': chat_id,
                    'message_length': len(message.text) if message and message.text else 0
                })
                
                return result
                
            except Exception as e:
                log_error(e, f'process_{message_type}', user_id=user.id)
                raise
        
        return wrapper
    return decorator


def log_database_operation(operation: str):
    """
    Decorator to log database operations with performance metrics.
    
    Args:
        operation: Name of the database operation
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Log successful operation
                duration = time.time() - start_time
                log_performance(f'db_{operation}', duration, {
                    'success': True,
                    'args_count': len(args),
                    'kwargs_count': len(kwargs)
                })
                
                logger.debug(f"Database operation '{operation}' completed in {duration:.3f}s")
                return result
                
            except Exception as e:
                # Log failed operation
                duration = time.time() - start_time
                log_performance(f'db_{operation}', duration, {
                    'success': False,
                    'error': str(e)
                })
                
                log_error(e, f'database_{operation}')
                raise
        
        return wrapper
    return decorator


def log_api_call(api_name: str, endpoint: str = None):
    """
    Decorator to log external API calls.
    
    Args:
        api_name: Name of the API being called
        endpoint: Optional endpoint information
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                
                # Log successful API call
                duration = time.time() - start_time
                details = {'api': api_name, 'success': True}
                if endpoint:
                    details['endpoint'] = endpoint
                
                log_performance(f'api_{api_name}', duration, details)
                
                logger.info(f"API call to {api_name} completed successfully")
                return result
                
            except Exception as e:
                # Log failed API call
                duration = time.time() - start_time
                details = {'api': api_name, 'success': False, 'error': str(e)}
                if endpoint:
                    details['endpoint'] = endpoint
                
                log_performance(f'api_{api_name}', duration, details)
                log_error(e, f'api_{api_name}')
                raise
        
        return wrapper
    return decorator


class LogContext:
    """Context manager for logging operations with automatic timing."""
    
    def __init__(self, operation_name: str, logger_name: str = None, extra_data: Dict[str, Any] = None):
        self.operation_name = operation_name
        self.logger = get_logger(logger_name or 'context')
        self.extra_data = extra_data or {}
        self.start_time = None
    
    async def __aenter__(self):
        self.start_time = time.time()
        self.logger.debug(f"Starting operation: {self.operation_name}")
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start_time
        
        if exc_type is None:
            # Success
            log_performance(self.operation_name, duration, {
                **self.extra_data,
                'success': True
            })
            self.logger.debug(f"Operation '{self.operation_name}' completed successfully in {duration:.3f}s")
        else:
            # Error
            log_performance(self.operation_name, duration, {
                **self.extra_data,
                'success': False,
                'error': str(exc_val)
            })
            log_error(exc_val, self.operation_name)


def get_user_info_for_logging(update: Update) -> Dict[str, Any]:
    """
    Extract user information from update for logging purposes.
    
    Args:
        update: Telegram update object
        
    Returns:
        Dictionary with user information
    """
    if not update or not update.effective_user:
        return {}
    
    user = update.effective_user
    chat = update.effective_chat
    
    return {
        'user_id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'chat_id': chat.id if chat else None,
        'chat_type': chat.type if chat else None,
        'is_bot': user.is_bot
    }


def log_startup_info():
    """Log bot startup information."""
    if not Config.LOGGING_ENABLED:
        return
        
    from core.config import Config
    
    startup_logger = get_logger('startup')
    
    startup_info = {
        'bot_mode': Config.BOT_MODE,
        'debug_mode': Config.DEBUG,
        'log_level': Config.LOG_LEVEL,
        'logging_enabled': Config.LOGGING_ENABLED,
        'webhook_url': Config.WEBHOOK_URL if Config.BOT_MODE == 'webhook' else None,
        'admin_count': len(Config.ADMIN_USER_IDS) if Config.ADMIN_USER_IDS else 0
    }
    
    startup_logger.info("Bot startup completed", extra=startup_info)
    
    # Log configuration details
    startup_logger.info(f"Bot started in {Config.BOT_MODE} mode")
    startup_logger.info(f"Debug mode: {'Enabled' if Config.DEBUG else 'Disabled'}")
    startup_logger.info(f"Log level: {Config.LOG_LEVEL}")
    startup_logger.info(f"Logging: {'Enabled' if Config.LOGGING_ENABLED else 'Disabled'}")
    
    if Config.ADMIN_USER_IDS:
        startup_logger.info(f"Configured {len(Config.ADMIN_USER_IDS)} admin users")


def log_shutdown_info():
    """Log bot shutdown information."""
    if not Config.LOGGING_ENABLED:
        return
        
    shutdown_logger = get_logger('shutdown')
    shutdown_logger.info("Bot shutdown initiated")