"""
Message formatting utilities.
"""

import re
from datetime import datetime
from aiogram.enums import ParseMode


class MessageFormatter:
    """Utility class for formatting messages."""
    
    @staticmethod
    def escape_markdown(text: str) -> str:
        """Escape markdown special characters."""
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)
    
    @staticmethod
    def format_user_mention(user_id: int, name: str) -> str:
        """Format user mention for HTML."""
        return f'<a href="tg://user?id={user_id}">{name}</a>'
    
    @staticmethod
    def format_code_block(code: str, language: str = "") -> str:
        """Format code block."""
        return f"```{language}\n{code}\n```"
    
    @staticmethod
    def format_time(timestamp: datetime) -> str:
        """Format timestamp to readable string."""
        return timestamp.strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def format_duration(seconds: int) -> str:
        """Format duration in seconds to human readable format."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            return f"{seconds // 60}m {seconds % 60}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"


# Standalone functions for easier usage
def format_user(user) -> str:
    """Format user object to string."""
    if hasattr(user, 'first_name'):
        name = user.first_name
        if hasattr(user, 'last_name') and user.last_name:
            name += f" {user.last_name}"
        if hasattr(user, 'username') and user.username:
            name += f" (@{user.username})"
        return name
    elif hasattr(user, 'username') and user.username:
        return f"@{user.username}"
    else:
        return f"User {user.id}"


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format datetime to string."""
    return dt.strftime(format_str)


def format_file_size(size_bytes: int) -> str:
    """Format file size in bytes to human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"