"""
Text processing utilities.
"""

import re
from typing import List


class TextProcessor:
    """Utility class for text processing."""
    
    @staticmethod
    def extract_command_args(text: str) -> tuple[str, List[str]]:
        """Extract command and arguments from text."""
        parts = text.split()
        command = parts[0] if parts else ""
        args = parts[1:] if len(parts) > 1 else []
        return command, args
    
    @staticmethod
    def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
        """Truncate text to specified length."""
        if len(text) <= max_length:
            return text
        return text[:max_length - len(suffix)] + suffix
    
    @staticmethod
    def clean_text(text: str) -> str:
        """Clean text by removing extra whitespace and special characters."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        # Remove non-printable characters
        text = re.sub(r'[^\x20-\x7E]', '', text)
        return text
    
    @staticmethod
    def extract_urls(text: str) -> List[str]:
        """Extract URLs from text."""
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        return re.findall(url_pattern, text)


# Standalone functions for easier usage
def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """Truncate text to specified length."""
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix


def escape_markdown(text: str) -> str:
    """Escape markdown special characters."""
    escape_chars = r'_*[]()~`>#+-=|{}.!'
    return re.sub(f'([{re.escape(escape_chars)}])', r'\\\1', text)