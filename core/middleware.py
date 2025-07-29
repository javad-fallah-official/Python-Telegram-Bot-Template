"""Middleware module for the Telegram bot."""

import logging
import time
from typing import Dict, Set
from functools import wraps
from telegram import Update
from telegram.ext import ContextTypes
from .config import Config

logger = logging.getLogger(__name__)


class RateLimiter:
    """Simple rate limiter for bot commands."""
    
    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.user_requests: Dict[int, list] = {}
    
    def is_allowed(self, user_id: int) -> bool:
        """Check if user is allowed to make a request."""
        now = time.time()
        
        # Initialize user if not exists
        if user_id not in self.user_requests:
            self.user_requests[user_id] = []
        
        # Clean old requests
        self.user_requests[user_id] = [
            req_time for req_time in self.user_requests[user_id]
            if now - req_time < self.window_seconds
        ]
        
        # Check if under limit
        if len(self.user_requests[user_id]) < self.max_requests:
            self.user_requests[user_id].append(now)
            return True
        
        return False


# Global rate limiter instance
rate_limiter = RateLimiter()


def admin_required(func):
    """Decorator to require admin privileges for a command."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        
        if not Config.is_admin(user.id):
            logger.warning(f"Non-admin user {user.id} tried to access admin command")
            await update.message.reply_text(
                "❌ You don't have permission to use this command."
            )
            return
        
        return await func(update, context)
    
    return wrapper


def rate_limit(max_requests: int = 5, window_seconds: int = 60):
    """Decorator to rate limit commands."""
    def decorator(func):
        @wraps(func)
        async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
            user = update.effective_user
            
            # Create rate limiter for this command
            limiter = RateLimiter(max_requests, window_seconds)
            
            if not limiter.is_allowed(user.id):
                logger.warning(f"Rate limit exceeded for user {user.id}")
                await update.message.reply_text(
                    f"⏰ Rate limit exceeded. Please wait {window_seconds} seconds before trying again."
                )
                return
            
            return await func(update, context)
        
        return wrapper
    
    return decorator


def log_user_activity(func):
    """Decorator to log user activity."""
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        user = update.effective_user
        command = update.message.text.split()[0] if update.message.text else "unknown"
        
        logger.info(
            f"User activity - ID: {user.id}, Username: @{user.username or 'N/A'}, "
            f"Name: {user.full_name}, Command: {command}"
        )
        
        return await func(update, context)
    
    return wrapper


async def logging_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Middleware for logging all updates."""
    user = update.effective_user
    chat = update.effective_chat
    
    if update.message:
        logger.debug(
            f"Message from user {user.id} (@{user.username}) in chat {chat.id}: "
            f"{update.message.text[:100]}..."
        )
    elif update.callback_query:
        logger.debug(
            f"Callback query from user {user.id} (@{user.username}): "
            f"{update.callback_query.data}"
        )


async def security_middleware(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Middleware for basic security checks."""
    user = update.effective_user
    
    # Check for banned users (you can implement your own logic)
    banned_users: Set[int] = set()  # Add banned user IDs here
    
    if user.id in banned_users:
        logger.warning(f"Banned user {user.id} tried to interact with bot")
        return  # Don't process the update
    
    # Check for suspicious activity
    if update.message and update.message.text:
        suspicious_patterns = ['spam', 'scam', 'hack']  # Add your patterns
        text_lower = update.message.text.lower()
        
        if any(pattern in text_lower for pattern in suspicious_patterns):
            logger.warning(f"Suspicious message from user {user.id}: {update.message.text}")
            # You can add additional actions here


class UserSession:
    """Simple user session management."""
    
    def __init__(self):
        self.sessions: Dict[int, Dict] = {}
    
    def get_session(self, user_id: int) -> Dict:
        """Get user session data."""
        if user_id not in self.sessions:
            self.sessions[user_id] = {
                'created_at': time.time(),
                'last_activity': time.time(),
                'data': {}
            }
        
        self.sessions[user_id]['last_activity'] = time.time()
        return self.sessions[user_id]
    
    def set_session_data(self, user_id: int, key: str, value):
        """Set session data for user."""
        session = self.get_session(user_id)
        session['data'][key] = value
    
    def get_session_data(self, user_id: int, key: str, default=None):
        """Get session data for user."""
        session = self.get_session(user_id)
        return session['data'].get(key, default)
    
    def clear_session(self, user_id: int):
        """Clear user session."""
        if user_id in self.sessions:
            del self.sessions[user_id]


# Global session manager
session_manager = UserSession()