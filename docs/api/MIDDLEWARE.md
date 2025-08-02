# 🔧 Middleware API Reference

This document provides a comprehensive API reference for the middleware system, including authentication, logging, rate limiting, and custom middleware development.

## Table of Contents

- [Middleware Architecture](#middleware-architecture)
- [Authentication Middleware](#authentication-middleware)
- [Logging Middleware](#logging-middleware)
- [Rate Limiting Middleware](#rate-limiting-middleware)
- [Error Handling Middleware](#error-handling-middleware)
- [Custom Middleware Development](#custom-middleware-development)
- [Middleware Registration](#middleware-registration)

## Middleware Architecture

### Base Middleware

```python
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User
from typing import Callable, Dict, Any, Awaitable, Optional
import logging

class BaseCustomMiddleware(BaseMiddleware):
    """Base class for custom middleware."""
    
    def __init__(self, name: str = None):
        """
        Initialize middleware.
        
        Args:
            name: Middleware name for logging
        """
        super().__init__()
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"middleware.{self.name}")
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process middleware.
        
        Args:
            handler: Next handler in chain
            event: Telegram event
            data: Handler data
            
        Returns:
            Handler result
        """
        # Pre-processing
        await self.pre_process(event, data)
        
        try:
            # Call next handler
            result = await handler(event, data)
            
            # Post-processing
            await self.post_process(event, data, result)
            
            return result
        except Exception as e:
            # Error handling
            await self.on_error(event, data, e)
            raise
    
    async def pre_process(self, event: TelegramObject, data: Dict[str, Any]) -> None:
        """
        Pre-process event before handler.
        
        Args:
            event: Telegram event
            data: Handler data
        """
        pass
    
    async def post_process(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        result: Any
    ) -> None:
        """
        Post-process event after handler.
        
        Args:
            event: Telegram event
            data: Handler data
            result: Handler result
        """
        pass
    
    async def on_error(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        error: Exception
    ) -> None:
        """
        Handle errors in middleware.
        
        Args:
            event: Telegram event
            data: Handler data
            error: Exception that occurred
        """
        self.logger.error(f"Error in {self.name}: {error}")
```

## Authentication Middleware

### Admin Authentication

```python
from aiogram.types import Message, CallbackQuery
from typing import Set, List, Union
import os

class AdminMiddleware(BaseCustomMiddleware):
    """Middleware for admin authentication."""
    
    def __init__(self, admin_ids: Union[List[int], Set[int]] = None):
        """
        Initialize admin middleware.
        
        Args:
            admin_ids: List or set of admin user IDs
        """
        super().__init__("AdminMiddleware")
        
        # Get admin IDs from environment or parameter
        if admin_ids:
            self.admin_ids = set(admin_ids)
        else:
            admin_ids_str = os.getenv('ADMIN_IDS', '')
            if admin_ids_str:
                self.admin_ids = set(map(int, admin_ids_str.split(',')))
            else:
                self.admin_ids = set()
        
        self.logger.info(f"Initialized with {len(self.admin_ids)} admin(s)")
    
    async def pre_process(self, event: TelegramObject, data: Dict[str, Any]) -> None:
        """Check if user is admin."""
        user = None
        
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if user and user.id not in self.admin_ids:
            self.logger.warning(f"Non-admin user {user.id} attempted admin action")
            
            # Add admin status to data
            data['is_admin'] = False
            
            # Optionally send unauthorized message
            if isinstance(event, Message):
                await event.answer("❌ You don't have permission to use this command.")
            elif isinstance(event, CallbackQuery):
                await event.answer("❌ You don't have permission to perform this action.", show_alert=True)
            
            # Stop processing
            raise Exception("Unauthorized access")
        
        data['is_admin'] = True
        self.logger.debug(f"Admin user {user.id if user else 'unknown'} authenticated")
    
    def add_admin(self, user_id: int) -> None:
        """
        Add admin user.
        
        Args:
            user_id: User ID to add as admin
        """
        self.admin_ids.add(user_id)
        self.logger.info(f"Added admin: {user_id}")
    
    def remove_admin(self, user_id: int) -> bool:
        """
        Remove admin user.
        
        Args:
            user_id: User ID to remove from admins
            
        Returns:
            True if removed, False if not found
        """
        if user_id in self.admin_ids:
            self.admin_ids.remove(user_id)
            self.logger.info(f"Removed admin: {user_id}")
            return True
        return False
    
    def is_admin(self, user_id: int) -> bool:
        """
        Check if user is admin.
        
        Args:
            user_id: User ID to check
            
        Returns:
            True if admin, False otherwise
        """
        return user_id in self.admin_ids
```

### User Registration Middleware

```python
from core.database import get_database

class UserRegistrationMiddleware(BaseCustomMiddleware):
    """Middleware for automatic user registration."""
    
    def __init__(self, auto_register: bool = True):
        """
        Initialize user registration middleware.
        
        Args:
            auto_register: Whether to automatically register new users
        """
        super().__init__("UserRegistrationMiddleware")
        self.auto_register = auto_register
    
    async def pre_process(self, event: TelegramObject, data: Dict[str, Any]) -> None:
        """Register user if not exists."""
        user = None
        
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if user:
            db = get_database()
            
            # Check if user exists
            existing_user = await db.get_user(user.id)
            
            if not existing_user and self.auto_register:
                # Register new user
                await db.add_user(
                    user_id=user.id,
                    username=user.username,
                    first_name=user.first_name,
                    last_name=user.last_name,
                    language_code=user.language_code
                )
                
                self.logger.info(f"Auto-registered new user: {user.id}")
                data['is_new_user'] = True
            else:
                data['is_new_user'] = False
            
            # Add user data to handler data
            data['user'] = existing_user or {
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'language_code': user.language_code
            }
```

## Logging Middleware

### Activity Logging

```python
import time
from datetime import datetime

class ActivityLoggingMiddleware(BaseCustomMiddleware):
    """Middleware for logging user activities."""
    
    def __init__(self, log_all: bool = True, log_commands_only: bool = False):
        """
        Initialize activity logging middleware.
        
        Args:
            log_all: Whether to log all activities
            log_commands_only: Whether to log only commands
        """
        super().__init__("ActivityLoggingMiddleware")
        self.log_all = log_all
        self.log_commands_only = log_commands_only
    
    async def pre_process(self, event: TelegramObject, data: Dict[str, Any]) -> None:
        """Log activity start."""
        data['start_time'] = time.time()
        
        if isinstance(event, Message):
            user = event.from_user
            
            # Check if should log this message
            should_log = self.log_all
            if self.log_commands_only and not event.text.startswith('/'):
                should_log = False
            
            if should_log:
                activity_data = {
                    'user_id': user.id,
                    'username': user.username,
                    'message_type': 'command' if event.text.startswith('/') else 'message',
                    'content': event.text[:100] if event.text else 'media',
                    'chat_id': event.chat.id,
                    'chat_type': event.chat.type,
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.logger.info(f"User activity: {activity_data}")
                
                # Store in database if available
                try:
                    db = get_database()
                    await db.log_activity(
                        user_id=user.id,
                        activity_type=activity_data['message_type'],
                        details=activity_data
                    )
                except Exception as e:
                    self.logger.error(f"Failed to log activity to database: {e}")
    
    async def post_process(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        result: Any
    ) -> None:
        """Log activity completion."""
        if 'start_time' in data:
            duration = time.time() - data['start_time']
            
            if isinstance(event, Message) and event.from_user:
                self.logger.debug(
                    f"Handler completed for user {event.from_user.id} "
                    f"in {duration:.3f}s"
                )
```

### Performance Monitoring

```python
class PerformanceMiddleware(BaseCustomMiddleware):
    """Middleware for monitoring handler performance."""
    
    def __init__(self, slow_threshold: float = 1.0):
        """
        Initialize performance middleware.
        
        Args:
            slow_threshold: Threshold in seconds for slow handlers
        """
        super().__init__("PerformanceMiddleware")
        self.slow_threshold = slow_threshold
        self.stats = {
            'total_requests': 0,
            'slow_requests': 0,
            'total_time': 0.0,
            'max_time': 0.0,
            'min_time': float('inf')
        }
    
    async def pre_process(self, event: TelegramObject, data: Dict[str, Any]) -> None:
        """Start performance monitoring."""
        data['perf_start'] = time.time()
    
    async def post_process(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        result: Any
    ) -> None:
        """Log performance metrics."""
        if 'perf_start' in data:
            duration = time.time() - data['perf_start']
            
            # Update statistics
            self.stats['total_requests'] += 1
            self.stats['total_time'] += duration
            self.stats['max_time'] = max(self.stats['max_time'], duration)
            self.stats['min_time'] = min(self.stats['min_time'], duration)
            
            if duration > self.slow_threshold:
                self.stats['slow_requests'] += 1
                
                # Log slow request
                handler_name = data.get('handler', {}).get('callback', 'unknown')
                user_id = getattr(event, 'from_user', {})
                user_id = getattr(user_id, 'id', 'unknown') if user_id else 'unknown'
                
                self.logger.warning(
                    f"Slow handler: {handler_name} took {duration:.3f}s "
                    f"for user {user_id}"
                )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get performance statistics.
        
        Returns:
            Performance statistics dictionary
        """
        if self.stats['total_requests'] > 0:
            avg_time = self.stats['total_time'] / self.stats['total_requests']
            slow_percentage = (self.stats['slow_requests'] / self.stats['total_requests']) * 100
        else:
            avg_time = 0.0
            slow_percentage = 0.0
        
        return {
            'total_requests': self.stats['total_requests'],
            'slow_requests': self.stats['slow_requests'],
            'slow_percentage': slow_percentage,
            'average_time': avg_time,
            'max_time': self.stats['max_time'],
            'min_time': self.stats['min_time'] if self.stats['min_time'] != float('inf') else 0.0
        }
```

## Rate Limiting Middleware

### User Rate Limiting

```python
import asyncio
from collections import defaultdict, deque
from typing import DefaultDict, Deque

class RateLimitMiddleware(BaseCustomMiddleware):
    """Middleware for rate limiting user requests."""
    
    def __init__(
        self, 
        max_requests: int = 10, 
        time_window: int = 60,
        block_duration: int = 300
    ):
        """
        Initialize rate limit middleware.
        
        Args:
            max_requests: Maximum requests per time window
            time_window: Time window in seconds
            block_duration: Block duration in seconds for rate limited users
        """
        super().__init__("RateLimitMiddleware")
        self.max_requests = max_requests
        self.time_window = time_window
        self.block_duration = block_duration
        
        # Track requests per user
        self.user_requests: DefaultDict[int, Deque[float]] = defaultdict(deque)
        self.blocked_users: Dict[int, float] = {}
    
    async def pre_process(self, event: TelegramObject, data: Dict[str, Any]) -> None:
        """Check rate limits."""
        user = None
        
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user
        
        if not user:
            return
        
        current_time = time.time()
        user_id = user.id
        
        # Check if user is currently blocked
        if user_id in self.blocked_users:
            if current_time < self.blocked_users[user_id]:
                # User is still blocked
                remaining_time = int(self.blocked_users[user_id] - current_time)
                
                self.logger.warning(f"Rate limited user {user_id} attempted request")
                
                if isinstance(event, Message):
                    await event.answer(
                        f"⚠️ You're sending messages too fast! "
                        f"Please wait {remaining_time} seconds."
                    )
                elif isinstance(event, CallbackQuery):
                    await event.answer(
                        f"⚠️ Too many requests! Wait {remaining_time}s",
                        show_alert=True
                    )
                
                raise Exception("Rate limited")
            else:
                # Block expired, remove user from blocked list
                del self.blocked_users[user_id]
        
        # Clean old requests
        user_requests = self.user_requests[user_id]
        while user_requests and current_time - user_requests[0] > self.time_window:
            user_requests.popleft()
        
        # Check if user exceeds rate limit
        if len(user_requests) >= self.max_requests:
            # Block user
            self.blocked_users[user_id] = current_time + self.block_duration
            
            self.logger.warning(
                f"User {user_id} rate limited: {len(user_requests)} requests "
                f"in {self.time_window}s"
            )
            
            if isinstance(event, Message):
                await event.answer(
                    f"⚠️ Rate limit exceeded! You're blocked for "
                    f"{self.block_duration // 60} minutes."
                )
            elif isinstance(event, CallbackQuery):
                await event.answer(
                    f"⚠️ Rate limit exceeded! Blocked for {self.block_duration // 60}m",
                    show_alert=True
                )
            
            raise Exception("Rate limited")
        
        # Add current request
        user_requests.append(current_time)
    
    def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """
        Get rate limit statistics for user.
        
        Args:
            user_id: User ID
            
        Returns:
            User rate limit statistics
        """
        current_time = time.time()
        user_requests = self.user_requests[user_id]
        
        # Clean old requests
        while user_requests and current_time - user_requests[0] > self.time_window:
            user_requests.popleft()
        
        is_blocked = user_id in self.blocked_users and current_time < self.blocked_users[user_id]
        remaining_block_time = 0
        
        if is_blocked:
            remaining_block_time = int(self.blocked_users[user_id] - current_time)
        
        return {
            'requests_in_window': len(user_requests),
            'max_requests': self.max_requests,
            'time_window': self.time_window,
            'is_blocked': is_blocked,
            'remaining_block_time': remaining_block_time
        }
```

## Error Handling Middleware

### Global Error Handler

```python
import traceback
from aiogram.exceptions import TelegramBadRequest, TelegramForbiddenError

class ErrorHandlingMiddleware(BaseCustomMiddleware):
    """Middleware for global error handling."""
    
    def __init__(self, send_error_messages: bool = True):
        """
        Initialize error handling middleware.
        
        Args:
            send_error_messages: Whether to send error messages to users
        """
        super().__init__("ErrorHandlingMiddleware")
        self.send_error_messages = send_error_messages
    
    async def on_error(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        error: Exception
    ) -> None:
        """Handle errors globally."""
        user_id = None
        chat_id = None
        
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id if event.from_user else None
            chat_id = event.chat.id if hasattr(event, 'chat') else None
        
        # Log error with context
        error_context = {
            'user_id': user_id,
            'chat_id': chat_id,
            'event_type': type(event).__name__,
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc()
        }
        
        self.logger.error(f"Unhandled error: {error_context}")
        
        # Handle specific error types
        if isinstance(error, TelegramBadRequest):
            await self._handle_bad_request(event, error)
        elif isinstance(error, TelegramForbiddenError):
            await self._handle_forbidden_error(event, error)
        elif isinstance(error, Exception) and "Rate limited" in str(error):
            # Rate limit errors are already handled by rate limit middleware
            pass
        elif isinstance(error, Exception) and "Unauthorized access" in str(error):
            # Auth errors are already handled by auth middleware
            pass
        else:
            await self._handle_generic_error(event, error)
    
    async def _handle_bad_request(self, event: TelegramObject, error: TelegramBadRequest) -> None:
        """Handle Telegram bad request errors."""
        if self.send_error_messages and isinstance(event, Message):
            try:
                await event.answer("❌ Invalid request. Please try again.")
            except Exception:
                pass
    
    async def _handle_forbidden_error(self, event: TelegramObject, error: TelegramForbiddenError) -> None:
        """Handle Telegram forbidden errors."""
        self.logger.warning(f"Bot was blocked or restricted: {error}")
        
        # Could implement user blocking logic here
        if isinstance(event, (Message, CallbackQuery)) and event.from_user:
            user_id = event.from_user.id
            # Mark user as blocked in database
            try:
                db = get_database()
                await db.update_user(user_id, is_blocked=True)
            except Exception as e:
                self.logger.error(f"Failed to mark user as blocked: {e}")
    
    async def _handle_generic_error(self, event: TelegramObject, error: Exception) -> None:
        """Handle generic errors."""
        if self.send_error_messages:
            if isinstance(event, Message):
                try:
                    await event.answer(
                        "❌ An error occurred while processing your request. "
                        "Please try again later."
                    )
                except Exception:
                    pass
            elif isinstance(event, CallbackQuery):
                try:
                    await event.answer(
                        "❌ An error occurred. Please try again.",
                        show_alert=True
                    )
                except Exception:
                    pass
```

## Custom Middleware Development

### Template for Custom Middleware

```python
class CustomMiddleware(BaseCustomMiddleware):
    """Template for creating custom middleware."""
    
    def __init__(self, config: Dict[str, Any] = None):
        """
        Initialize custom middleware.
        
        Args:
            config: Middleware configuration
        """
        super().__init__("CustomMiddleware")
        self.config = config or {}
    
    async def pre_process(self, event: TelegramObject, data: Dict[str, Any]) -> None:
        """
        Pre-process logic.
        
        Args:
            event: Telegram event
            data: Handler data
        """
        # Add your pre-processing logic here
        # Example: validation, authentication, data enrichment
        pass
    
    async def post_process(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        result: Any
    ) -> None:
        """
        Post-process logic.
        
        Args:
            event: Telegram event
            data: Handler data
            result: Handler result
        """
        # Add your post-processing logic here
        # Example: logging, cleanup, notifications
        pass
    
    async def on_error(
        self, 
        event: TelegramObject, 
        data: Dict[str, Any], 
        error: Exception
    ) -> None:
        """
        Error handling logic.
        
        Args:
            event: Telegram event
            data: Handler data
            error: Exception that occurred
        """
        # Add your error handling logic here
        # Example: error reporting, recovery, user notification
        await super().on_error(event, data, error)
```

## Middleware Registration

### Registration Methods

```python
from aiogram import Dispatcher
from aiogram.types import Message, CallbackQuery

def register_middleware(dp: Dispatcher) -> None:
    """
    Register all middleware with the dispatcher.
    
    Args:
        dp: Aiogram dispatcher
    """
    # Register middleware in order of execution
    
    # 1. Performance monitoring (should be first)
    dp.message.middleware(PerformanceMiddleware())
    dp.callback_query.middleware(PerformanceMiddleware())
    
    # 2. Rate limiting
    dp.message.middleware(RateLimitMiddleware(max_requests=10, time_window=60))
    dp.callback_query.middleware(RateLimitMiddleware(max_requests=20, time_window=60))
    
    # 3. User registration
    dp.message.middleware(UserRegistrationMiddleware())
    dp.callback_query.middleware(UserRegistrationMiddleware())
    
    # 4. Activity logging
    dp.message.middleware(ActivityLoggingMiddleware())
    dp.callback_query.middleware(ActivityLoggingMiddleware())
    
    # 5. Error handling (should be last)
    dp.message.middleware(ErrorHandlingMiddleware())
    dp.callback_query.middleware(ErrorHandlingMiddleware())

def register_admin_middleware(dp: Dispatcher, admin_handlers: List[str] = None) -> None:
    """
    Register admin middleware for specific handlers.
    
    Args:
        dp: Aiogram dispatcher
        admin_handlers: List of handler names that require admin access
    """
    admin_middleware = AdminMiddleware()
    
    # Register for specific message handlers
    if admin_handlers:
        for handler_name in admin_handlers:
            # This would require custom handler registration logic
            pass
    else:
        # Register for all admin commands (example)
        @dp.message(lambda message: message.text and message.text.startswith('/admin'))
        async def admin_handler_wrapper(message: Message):
            # Admin middleware will be applied automatically
            pass
```

### Conditional Middleware

```python
class ConditionalMiddleware(BaseCustomMiddleware):
    """Middleware that applies conditionally."""
    
    def __init__(self, condition_func: Callable[[TelegramObject], bool]):
        """
        Initialize conditional middleware.
        
        Args:
            condition_func: Function to determine if middleware should apply
        """
        super().__init__("ConditionalMiddleware")
        self.condition_func = condition_func
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """Apply middleware conditionally."""
        if self.condition_func(event):
            return await super().__call__(handler, event, data)
        else:
            # Skip this middleware
            return await handler(event, data)

# Example usage
def is_private_chat(event: TelegramObject) -> bool:
    """Check if event is from private chat."""
    if isinstance(event, Message):
        return event.chat.type == 'private'
    return False

# Register conditional middleware
private_chat_middleware = ConditionalMiddleware(is_private_chat)
dp.message.middleware(private_chat_middleware)
```

## Usage Examples

### Complete Middleware Setup

```python
from aiogram import Bot, Dispatcher
from middleware import *

async def setup_bot():
    """Setup bot with all middleware."""
    bot = Bot(token="YOUR_BOT_TOKEN")
    dp = Dispatcher()
    
    # Register middleware
    register_middleware(dp)
    
    # Register admin middleware for specific commands
    admin_middleware = AdminMiddleware()
    
    @dp.message(lambda msg: msg.text and msg.text.startswith('/admin'))
    async def admin_commands(message: Message):
        # This handler will have admin middleware applied
        await message.answer("Admin command executed!")
    
    # Start polling
    await dp.start_polling(bot)

# Run the bot
if __name__ == "__main__":
    import asyncio
    asyncio.run(setup_bot())
```

---

*For more examples and implementation details, see the [middleware modules](../../middleware/) in the source code.*