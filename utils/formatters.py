"""
Message formatting utilities.
"""

import re
from datetime import datetime
from telegram.constants import ParseMode


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