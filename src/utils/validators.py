"""
Data validation utilities.
"""

import re


class Validator:
    """Utility class for data validation."""
    
    @staticmethod
    def is_valid_email(email: str) -> bool:
        """Validate email address."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None
    
    @staticmethod
    def is_valid_url(url: str) -> bool:
        """Validate URL."""
        pattern = r'^https?://(?:[-\w.])+(?:\:[0-9]+)?(?:/(?:[\w/_.])*(?:\?(?:[\w&=%.])*)?(?:\#(?:[\w.])*)?)?$'
        return re.match(pattern, url) is not None
    
    @staticmethod
    def is_valid_phone(phone: str) -> bool:
        """Validate phone number (basic validation)."""
        # Remove spaces and dashes
        clean_phone = phone.replace(' ', '').replace('-', '')
        # Must be at least 7 digits, can start with + followed by country code
        pattern = r'^\+?[1-9]\d{6,14}$'
        return re.match(pattern, clean_phone) is not None