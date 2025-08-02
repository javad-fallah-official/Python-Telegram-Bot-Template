# 🛠️ Utilities API Reference

This document provides a comprehensive API reference for the utility modules, including formatters, keyboards, validators, caching, and file operations.

## Table of Contents

- [Formatters](#formatters)
- [Keyboards](#keyboards)
- [Validators](#validators)
- [Caching](#caching)
- [File Operations](#file-operations)
- [Text Processing](#text-processing)
- [Logging Utilities](#logging-utilities)

## Formatters

### Message Formatters

```python
from utils.formatters import MessageFormatter
from typing import Dict, Any, Optional, List

class MessageFormatter:
    """Utility class for formatting messages and text."""
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """
        Escape special characters for Markdown formatting.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text safe for Markdown
        """
        special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
        
        for char in special_chars:
            text = text.replace(char, f'\\{char}')
        
        return text
    
    @staticmethod
    def escape_html(text: str) -> str:
        """
        Escape special characters for HTML formatting.
        
        Args:
            text: Text to escape
            
        Returns:
            Escaped text safe for HTML
        """
        return (text
                .replace('&', '&amp;')
                .replace('<', '&lt;')
                .replace('>', '&gt;')
                .replace('"', '&quot;')
                .replace("'", '&#x27;'))
    
    @staticmethod
    def format_user_mention(user: Dict[str, Any], parse_mode: str = "Markdown") -> str:
        """
        Format user mention with proper escaping.
        
        Args:
            user: User data dictionary
            parse_mode: Parsing mode ('Markdown' or 'HTML')
            
        Returns:
            Formatted user mention
        """
        first_name = user.get('first_name', 'User')
        user_id = user.get('id')
        
        if parse_mode == "HTML":
            escaped_name = MessageFormatter.escape_html(first_name)
            return f'<a href="tg://user?id={user_id}">{escaped_name}</a>'
        else:
            escaped_name = MessageFormatter.escape_markdown(first_name)
            return f'[{escaped_name}](tg://user?id={user_id})'
    
    @staticmethod
    def format_code_block(code: str, language: str = "") -> str:
        """
        Format code block with syntax highlighting.
        
        Args:
            code: Code to format
            language: Programming language for highlighting
            
        Returns:
            Formatted code block
        """
        return f"```{language}\n{code}\n```"
    
    @staticmethod
    def format_inline_code(code: str) -> str:
        """
        Format inline code.
        
        Args:
            code: Code to format
            
        Returns:
            Formatted inline code
        """
        return f"`{code}`"
    
    @staticmethod
    def format_bold(text: str, parse_mode: str = "Markdown") -> str:
        """
        Format text as bold.
        
        Args:
            text: Text to format
            parse_mode: Parsing mode ('Markdown' or 'HTML')
            
        Returns:
            Bold formatted text
        """
        if parse_mode == "HTML":
            return f"<b>{MessageFormatter.escape_html(text)}</b>"
        else:
            return f"**{MessageFormatter.escape_markdown(text)}**"
    
    @staticmethod
    def format_italic(text: str, parse_mode: str = "Markdown") -> str:
        """
        Format text as italic.
        
        Args:
            text: Text to format
            parse_mode: Parsing mode ('Markdown' or 'HTML')
            
        Returns:
            Italic formatted text
        """
        if parse_mode == "HTML":
            return f"<i>{MessageFormatter.escape_html(text)}</i>"
        else:
            return f"*{MessageFormatter.escape_markdown(text)}*"
    
    @staticmethod
    def format_link(text: str, url: str, parse_mode: str = "Markdown") -> str:
        """
        Format text as a link.
        
        Args:
            text: Link text
            url: URL
            parse_mode: Parsing mode ('Markdown' or 'HTML')
            
        Returns:
            Formatted link
        """
        if parse_mode == "HTML":
            escaped_text = MessageFormatter.escape_html(text)
            return f'<a href="{url}">{escaped_text}</a>'
        else:
            escaped_text = MessageFormatter.escape_markdown(text)
            return f'[{escaped_text}]({url})'
```

### Data Formatters

```python
@staticmethod
def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string
    """
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f} {size_names[i]}"

@staticmethod
def format_duration(seconds: int) -> str:
    """
    Format duration in human-readable format.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted duration string
    """
    if seconds < 60:
        return f"{seconds}s"
    elif seconds < 3600:
        minutes = seconds // 60
        remaining_seconds = seconds % 60
        return f"{minutes}m {remaining_seconds}s"
    else:
        hours = seconds // 3600
        remaining_minutes = (seconds % 3600) // 60
        return f"{hours}h {remaining_minutes}m"

@staticmethod
def format_number(number: int) -> str:
    """
    Format large numbers with thousand separators.
    
    Args:
        number: Number to format
        
    Returns:
        Formatted number string
    """
    return f"{number:,}"

@staticmethod
def format_percentage(value: float, total: float) -> str:
    """
    Format percentage with proper rounding.
    
    Args:
        value: Current value
        total: Total value
        
    Returns:
        Formatted percentage string
    """
    if total == 0:
        return "0%"
    
    percentage = (value / total) * 100
    return f"{percentage:.1f}%"
```

## Keyboards

### Inline Keyboards

```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import List, Tuple, Optional, Dict, Any

class KeyboardBuilder:
    """Utility class for building Telegram keyboards."""
    
    @staticmethod
    def create_inline_keyboard(
        buttons: List[List[Tuple[str, str]]], 
        row_width: int = 2
    ) -> InlineKeyboardMarkup:
        """
        Create inline keyboard from button data.
        
        Args:
            buttons: List of button rows, each containing (text, callback_data) tuples
            row_width: Maximum buttons per row (when auto-arranging)
            
        Returns:
            InlineKeyboardMarkup object
        """
        keyboard = []
        
        for row in buttons:
            keyboard_row = []
            for text, callback_data in row:
                keyboard_row.append(
                    InlineKeyboardButton(text=text, callback_data=callback_data)
                )
            keyboard.append(keyboard_row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_url_keyboard(
        buttons: List[List[Tuple[str, str]]]
    ) -> InlineKeyboardMarkup:
        """
        Create inline keyboard with URL buttons.
        
        Args:
            buttons: List of button rows, each containing (text, url) tuples
            
        Returns:
            InlineKeyboardMarkup object
        """
        keyboard = []
        
        for row in buttons:
            keyboard_row = []
            for text, url in row:
                keyboard_row.append(
                    InlineKeyboardButton(text=text, url=url)
                )
            keyboard.append(keyboard_row)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_pagination_keyboard(
        current_page: int, 
        total_pages: int, 
        callback_prefix: str = "page"
    ) -> InlineKeyboardMarkup:
        """
        Create pagination keyboard.
        
        Args:
            current_page: Current page number (1-based)
            total_pages: Total number of pages
            callback_prefix: Prefix for callback data
            
        Returns:
            InlineKeyboardMarkup object
        """
        keyboard = []
        
        # Navigation row
        nav_row = []
        
        # Previous page button
        if current_page > 1:
            nav_row.append(
                InlineKeyboardButton(
                    text="◀️ Previous", 
                    callback_data=f"{callback_prefix}_{current_page - 1}"
                )
            )
        
        # Page indicator
        nav_row.append(
            InlineKeyboardButton(
                text=f"{current_page}/{total_pages}", 
                callback_data="page_info"
            )
        )
        
        # Next page button
        if current_page < total_pages:
            nav_row.append(
                InlineKeyboardButton(
                    text="Next ▶️", 
                    callback_data=f"{callback_prefix}_{current_page + 1}"
                )
            )
        
        keyboard.append(nav_row)
        
        # Quick navigation (if many pages)
        if total_pages > 5:
            quick_nav = []
            
            # First page
            if current_page > 3:
                quick_nav.append(
                    InlineKeyboardButton(
                        text="1", 
                        callback_data=f"{callback_prefix}_1"
                    )
                )
                if current_page > 4:
                    quick_nav.append(
                        InlineKeyboardButton(
                            text="...", 
                            callback_data="page_info"
                        )
                    )
            
            # Current page range
            start_range = max(1, current_page - 1)
            end_range = min(total_pages + 1, current_page + 2)
            
            for page in range(start_range, end_range):
                if page != current_page:
                    quick_nav.append(
                        InlineKeyboardButton(
                            text=str(page), 
                            callback_data=f"{callback_prefix}_{page}"
                        )
                    )
            
            # Last page
            if current_page < total_pages - 2:
                if current_page < total_pages - 3:
                    quick_nav.append(
                        InlineKeyboardButton(
                            text="...", 
                            callback_data="page_info"
                        )
                    )
                quick_nav.append(
                    InlineKeyboardButton(
                        text=str(total_pages), 
                        callback_data=f"{callback_prefix}_{total_pages}"
                    )
                )
            
            if quick_nav:
                keyboard.append(quick_nav)
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
    
    @staticmethod
    def create_confirmation_keyboard(
        confirm_data: str, 
        cancel_data: str = "cancel"
    ) -> InlineKeyboardMarkup:
        """
        Create confirmation keyboard with Yes/No buttons.
        
        Args:
            confirm_data: Callback data for confirmation
            cancel_data: Callback data for cancellation
            
        Returns:
            InlineKeyboardMarkup object
        """
        keyboard = [[
            InlineKeyboardButton(text="✅ Yes", callback_data=confirm_data),
            InlineKeyboardButton(text="❌ No", callback_data=cancel_data)
        ]]
        
        return InlineKeyboardMarkup(inline_keyboard=keyboard)
```

### Reply Keyboards

```python
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove

@staticmethod
def create_reply_keyboard(
    buttons: List[List[str]], 
    resize_keyboard: bool = True,
    one_time_keyboard: bool = False
) -> ReplyKeyboardMarkup:
    """
    Create reply keyboard from button text.
    
    Args:
        buttons: List of button rows, each containing button text
        resize_keyboard: Whether to resize keyboard
        one_time_keyboard: Whether to hide keyboard after use
        
    Returns:
        ReplyKeyboardMarkup object
    """
    keyboard = []
    
    for row in buttons:
        keyboard_row = []
        for text in row:
            keyboard_row.append(KeyboardButton(text=text))
        keyboard.append(keyboard_row)
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=resize_keyboard,
        one_time_keyboard=one_time_keyboard
    )

@staticmethod
def create_contact_keyboard() -> ReplyKeyboardMarkup:
    """
    Create keyboard with contact sharing button.
    
    Returns:
        ReplyKeyboardMarkup object
    """
    keyboard = [[
        KeyboardButton(text="📱 Share Contact", request_contact=True)
    ]]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

@staticmethod
def create_location_keyboard() -> ReplyKeyboardMarkup:
    """
    Create keyboard with location sharing button.
    
    Returns:
        ReplyKeyboardMarkup object
    """
    keyboard = [[
        KeyboardButton(text="📍 Share Location", request_location=True)
    ]]
    
    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        one_time_keyboard=True
    )

@staticmethod
def remove_keyboard() -> ReplyKeyboardRemove:
    """
    Create keyboard removal object.
    
    Returns:
        ReplyKeyboardRemove object
    """
    return ReplyKeyboardRemove()
```

## Validators

### Input Validators

```python
import re
from typing import Optional, List, Any
from datetime import datetime

class Validator:
    """Utility class for input validation."""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """
        Validate email address format.
        
        Args:
            email: Email address to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """
        Validate phone number format.
        
        Args:
            phone: Phone number to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Remove all non-digit characters
        digits_only = re.sub(r'\D', '', phone)
        
        # Check if it's a valid length (7-15 digits)
        return 7 <= len(digits_only) <= 15
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """
        Validate URL format.
        
        Args:
            url: URL to validate
            
        Returns:
            True if valid, False otherwise
        """
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def is_valid_user_id(user_id: Any) -> bool:
        """
        Validate Telegram user ID.
        
        Args:
            user_id: User ID to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            user_id = int(user_id)
            return 1 <= user_id <= 2147483647  # Telegram user ID range
        except (ValueError, TypeError):
            return False
    
    @staticmethod
    def is_valid_username(username: str) -> bool:
        """
        Validate Telegram username format.
        
        Args:
            username: Username to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not username:
            return False
        
        # Remove @ if present
        if username.startswith('@'):
            username = username[1:]
        
        # Check format: 5-32 characters, alphanumeric and underscores
        pattern = r'^[a-zA-Z0-9_]{5,32}$'
        return re.match(pattern, username) is not None
    
    @staticmethod
    def is_valid_command(command: str) -> bool:
        """
        Validate bot command format.
        
        Args:
            command: Command to validate
            
        Returns:
            True if valid, False otherwise
        """
        if not command:
            return False
        
        # Remove / if present
        if command.startswith('/'):
            command = command[1:]
        
        # Check format: 1-32 characters, lowercase letters, digits, and underscores
        pattern = r'^[a-z0-9_]{1,32}$'
        return re.match(pattern, command) is not None
    
    @staticmethod
    def validate_text_length(text: str, min_length: int = 0, max_length: int = 4096) -> bool:
        """
        Validate text length for Telegram messages.
        
        Args:
            text: Text to validate
            min_length: Minimum allowed length
            max_length: Maximum allowed length
            
        Returns:
            True if valid, False otherwise
        """
        return min_length <= len(text) <= max_length
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Sanitize filename by removing invalid characters.
        
        Args:
            filename: Original filename
            
        Returns:
            Sanitized filename
        """
        # Remove invalid characters
        invalid_chars = r'[<>:"/\\|?*]'
        sanitized = re.sub(invalid_chars, '_', filename)
        
        # Remove leading/trailing dots and spaces
        sanitized = sanitized.strip('. ')
        
        # Ensure it's not empty
        if not sanitized:
            sanitized = 'file'
        
        return sanitized
    
    @staticmethod
    def validate_json(json_string: str) -> bool:
        """
        Validate JSON string format.
        
        Args:
            json_string: JSON string to validate
            
        Returns:
            True if valid, False otherwise
        """
        try:
            import json
            json.loads(json_string)
            return True
        except (ValueError, TypeError):
            return False
```

## Caching

### Memory Cache

```python
import time
from typing import Any, Optional, Dict, Callable
import asyncio
from functools import wraps

class MemoryCache:
    """Simple in-memory cache with TTL support."""
    
    def __init__(self, default_ttl: int = 300):
        """
        Initialize memory cache.
        
        Args:
            default_ttl: Default time-to-live in seconds
        """
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._default_ttl = default_ttl
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Set cache value.
        
        Args:
            key: Cache key
            value: Value to cache
            ttl: Time-to-live in seconds
        """
        if ttl is None:
            ttl = self._default_ttl
        
        expiry = time.time() + ttl if ttl > 0 else None
        
        self._cache[key] = {
            'value': value,
            'expiry': expiry
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get cache value.
        
        Args:
            key: Cache key
            default: Default value if not found
            
        Returns:
            Cached value or default
        """
        if key not in self._cache:
            return default
        
        entry = self._cache[key]
        
        # Check if expired
        if entry['expiry'] and time.time() > entry['expiry']:
            del self._cache[key]
            return default
        
        return entry['value']
    
    def delete(self, key: str) -> bool:
        """
        Delete cache entry.
        
        Args:
            key: Cache key
            
        Returns:
            True if deleted, False if not found
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Clear all cache entries."""
        self._cache.clear()
    
    def cleanup_expired(self) -> int:
        """
        Remove expired entries.
        
        Returns:
            Number of entries removed
        """
        current_time = time.time()
        expired_keys = []
        
        for key, entry in self._cache.items():
            if entry['expiry'] and current_time > entry['expiry']:
                expired_keys.append(key)
        
        for key in expired_keys:
            del self._cache[key]
        
        return len(expired_keys)
    
    def size(self) -> int:
        """
        Get cache size.
        
        Returns:
            Number of cached entries
        """
        return len(self._cache)

# Global cache instance
cache = MemoryCache()

def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """
    Decorator for caching function results.
    
    Args:
        ttl: Time-to-live in seconds
        key_func: Function to generate cache key
    """
    def decorator(func):
        @wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        @wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"
            
            # Try to get from cache
            result = cache.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            cache.set(cache_key, result, ttl)
            
            return result
        
        # Return appropriate wrapper based on function type
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper
    
    return decorator
```

## File Operations

### File Utilities

```python
import os
import aiofiles
from typing import Optional, List, Dict, Any
import mimetypes
from pathlib import Path

class FileUtils:
    """Utility class for file operations."""
    
    @staticmethod
    async def read_file(file_path: str, encoding: str = 'utf-8') -> Optional[str]:
        """
        Read file content asynchronously.
        
        Args:
            file_path: Path to file
            encoding: File encoding
            
        Returns:
            File content or None if error
        """
        try:
            async with aiofiles.open(file_path, 'r', encoding=encoding) as file:
                return await file.read()
        except Exception:
            return None
    
    @staticmethod
    async def write_file(
        file_path: str, 
        content: str, 
        encoding: str = 'utf-8'
    ) -> bool:
        """
        Write content to file asynchronously.
        
        Args:
            file_path: Path to file
            content: Content to write
            encoding: File encoding
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            async with aiofiles.open(file_path, 'w', encoding=encoding) as file:
                await file.write(content)
            return True
        except Exception:
            return False
    
    @staticmethod
    async def append_file(
        file_path: str, 
        content: str, 
        encoding: str = 'utf-8'
    ) -> bool:
        """
        Append content to file asynchronously.
        
        Args:
            file_path: Path to file
            content: Content to append
            encoding: File encoding
            
        Returns:
            True if successful, False otherwise
        """
        try:
            async with aiofiles.open(file_path, 'a', encoding=encoding) as file:
                await file.write(content)
            return True
        except Exception:
            return False
    
    @staticmethod
    def get_file_info(file_path: str) -> Optional[Dict[str, Any]]:
        """
        Get file information.
        
        Args:
            file_path: Path to file
            
        Returns:
            File information dictionary or None if error
        """
        try:
            stat = os.stat(file_path)
            mime_type, _ = mimetypes.guess_type(file_path)
            
            return {
                'name': os.path.basename(file_path),
                'size': stat.st_size,
                'modified': stat.st_mtime,
                'mime_type': mime_type,
                'extension': Path(file_path).suffix.lower()
            }
        except Exception:
            return None
    
    @staticmethod
    def is_safe_path(file_path: str, base_path: str) -> bool:
        """
        Check if file path is safe (within base directory).
        
        Args:
            file_path: File path to check
            base_path: Base directory path
            
        Returns:
            True if safe, False otherwise
        """
        try:
            # Resolve paths to absolute
            abs_file_path = os.path.abspath(file_path)
            abs_base_path = os.path.abspath(base_path)
            
            # Check if file path starts with base path
            return abs_file_path.startswith(abs_base_path)
        except Exception:
            return False
    
    @staticmethod
    def list_files(
        directory: str, 
        pattern: str = "*", 
        recursive: bool = False
    ) -> List[str]:
        """
        List files in directory.
        
        Args:
            directory: Directory path
            pattern: File pattern (glob)
            recursive: Whether to search recursively
            
        Returns:
            List of file paths
        """
        try:
            path = Path(directory)
            
            if recursive:
                return [str(p) for p in path.rglob(pattern) if p.is_file()]
            else:
                return [str(p) for p in path.glob(pattern) if p.is_file()]
        except Exception:
            return []
    
    @staticmethod
    def ensure_directory(directory: str) -> bool:
        """
        Ensure directory exists.
        
        Args:
            directory: Directory path
            
        Returns:
            True if successful, False otherwise
        """
        try:
            os.makedirs(directory, exist_ok=True)
            return True
        except Exception:
            return False
```

## Text Processing

### Text Utilities

```python
import re
from typing import List, Optional, Dict, Any

class TextProcessor:
    """Utility class for text processing."""
    
    @staticmethod
    def extract_mentions(text: str) -> List[str]:
        """
        Extract @mentions from text.
        
        Args:
            text: Text to process
            
        Returns:
            List of mentioned usernames
        """
        pattern = r'@([a-zA-Z0-9_]{5,32})'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_hashtags(text: str) -> List[str]:
        """
        Extract #hashtags from text.
        
        Args:
            text: Text to process
            
        Returns:
            List of hashtags
        """
        pattern = r'#([a-zA-Z0-9_]+)'
        return re.findall(pattern, text)
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """
        Extract URLs from text.
        
        Args:
            text: Text to process
            
        Returns:
            List of URLs
        """
        pattern = r'https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?'
        return re.findall(pattern, text)
    
    @staticmethod
    def clean_text(text: str) -> str:
        """
        Clean text by removing extra whitespace and special characters.
        
        Args:
            text: Text to clean
            
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text
    
    @staticmethod
    def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
        """
        Truncate text to maximum length.
        
        Args:
            text: Text to truncate
            max_length: Maximum length
            suffix: Suffix to add if truncated
            
        Returns:
            Truncated text
        """
        if len(text) <= max_length:
            return text
        
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def word_count(text: str) -> int:
        """
        Count words in text.
        
        Args:
            text: Text to count
            
        Returns:
            Number of words
        """
        return len(text.split())
    
    @staticmethod
    def extract_commands(text: str) -> List[str]:
        """
        Extract bot commands from text.
        
        Args:
            text: Text to process
            
        Returns:
            List of commands
        """
        pattern = r'/([a-zA-Z0-9_]+)'
        return re.findall(pattern, text)
```

## Logging Utilities

### Enhanced Logging

```python
import logging
import json
from typing import Dict, Any, Optional
from datetime import datetime

class StructuredLogger:
    """Enhanced logger with structured logging support."""
    
    def __init__(self, name: str):
        """
        Initialize structured logger.
        
        Args:
            name: Logger name
        """
        self.logger = logging.getLogger(name)
    
    def log_event(
        self, 
        level: str, 
        message: str, 
        event_type: str,
        user_id: Optional[int] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log structured event.
        
        Args:
            level: Log level
            message: Log message
            event_type: Type of event
            user_id: User ID if applicable
            extra_data: Additional data
        """
        log_data = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'message': message,
            'user_id': user_id,
            'extra_data': extra_data or {}
        }
        
        log_message = json.dumps(log_data)
        
        if level.upper() == 'DEBUG':
            self.logger.debug(log_message)
        elif level.upper() == 'INFO':
            self.logger.info(log_message)
        elif level.upper() == 'WARNING':
            self.logger.warning(log_message)
        elif level.upper() == 'ERROR':
            self.logger.error(log_message)
        elif level.upper() == 'CRITICAL':
            self.logger.critical(log_message)
    
    def log_user_action(
        self, 
        user_id: int, 
        action: str, 
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log user action.
        
        Args:
            user_id: User ID
            action: Action performed
            details: Action details
        """
        self.log_event(
            'INFO',
            f'User {user_id} performed action: {action}',
            'user_action',
            user_id=user_id,
            extra_data={'action': action, 'details': details or {}}
        )
    
    def log_error(
        self, 
        error: Exception, 
        context: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log error with context.
        
        Args:
            error: Exception object
            context: Error context
        """
        self.log_event(
            'ERROR',
            str(error),
            'error',
            extra_data={
                'error_type': type(error).__name__,
                'context': context or {}
            }
        )
```

## Usage Examples

### Complete Example

```python
from utils.formatters import MessageFormatter
from utils.keyboards import KeyboardBuilder
from utils.validators import Validator
from utils.cache import cache, cached

# Format user message
user = {'id': 123456789, 'first_name': 'John Doe'}
mention = MessageFormatter.format_user_mention(user)
bold_text = MessageFormatter.format_bold("Important!")

# Create keyboard
keyboard = KeyboardBuilder.create_inline_keyboard([
    [("Button 1", "data_1"), ("Button 2", "data_2")],
    [("Settings", "settings")]
])

# Validate input
email = "user@example.com"
if Validator.is_valid_email(email):
    print("Valid email")

# Use caching
@cached(ttl=300)
async def expensive_operation(param: str) -> str:
    # Simulate expensive operation
    await asyncio.sleep(1)
    return f"Result for {param}"

# File operations
from utils.files import FileUtils

content = await FileUtils.read_file("config.txt")
await FileUtils.write_file("output.txt", "Hello World!")
```

---

*For more examples and implementation details, see the [utils modules](../../utils/) in the source code.*