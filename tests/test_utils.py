"""
Unit tests for utility modules.

This module tests formatters, keyboards, validators, and other utilities.
"""

import pytest
from datetime import datetime

from tests.utils import TestConfig


class TestFormatters:
    """Test the formatters module."""
    
    def test_formatters_import(self):
        """Test that formatters can be imported."""
        from utils.formatters import format_user, format_datetime, format_file_size
        assert format_user is not None
        assert format_datetime is not None
        assert format_file_size is not None
    
    def test_format_user(self):
        """Test user formatting."""
        from utils.formatters import format_user
        
        user = type('User', (), {
            'id': 12345,
            'first_name': 'John',
            'last_name': 'Doe',
            'username': 'johndoe'
        })()
        
        result = format_user(user)
        assert isinstance(result, str)
        assert 'John' in result
    
    def test_format_datetime(self):
        """Test datetime formatting."""
        from utils.formatters import format_datetime
        
        dt = datetime(2024, 1, 15, 12, 30, 45)
        result = format_datetime(dt)
        assert isinstance(result, str)
        assert '2024' in result
    
    def test_format_file_size(self):
        """Test file size formatting."""
        from utils.formatters import format_file_size
        
        # Test various sizes
        assert format_file_size(1024) == "1.0 KB"
        assert format_file_size(1048576) == "1.0 MB"
        assert format_file_size(500) == "500 B"


class TestKeyboards:
    """Test the keyboards module."""
    
    def test_keyboards_import(self):
        """Test that keyboards can be imported."""
        from utils.keyboards import create_inline_keyboard, create_reply_keyboard
        assert create_inline_keyboard is not None
        assert create_reply_keyboard is not None
    
    def test_create_inline_keyboard(self):
        """Test inline keyboard creation."""
        from utils.keyboards import create_inline_keyboard
        
        buttons = [
            [("Button 1", "data1"), ("Button 2", "data2")],
            [("Button 3", "data3")]
        ]
        
        keyboard = create_inline_keyboard(buttons)
        assert keyboard is not None
        # Verify it's a proper keyboard structure
        assert hasattr(keyboard, 'inline_keyboard')
    
    def test_create_reply_keyboard(self):
        """Test reply keyboard creation."""
        from utils.keyboards import create_reply_keyboard
        
        buttons = [["Option 1", "Option 2"], ["Option 3"]]
        
        keyboard = create_reply_keyboard(buttons)
        assert keyboard is not None
        # Verify it's a proper keyboard structure
        assert hasattr(keyboard, 'keyboard')


class TestValidators:
    """Test the validators module."""
    
    def test_validators_import(self):
        """Test that Validator can be imported."""
        from utils.validators import Validator
        assert Validator is not None
    
    def test_email_validation(self):
        """Test email validation."""
        from utils.validators import Validator
        
        # Valid emails
        assert Validator.is_valid_email("test@example.com") == True
        assert Validator.is_valid_email("user.name@domain.co.uk") == True
        
        # Invalid emails
        assert Validator.is_valid_email("invalid-email") == False
        assert Validator.is_valid_email("@domain.com") == False
        assert Validator.is_valid_email("user@") == False
    
    def test_url_validation(self):
        """Test URL validation."""
        from utils.validators import Validator
        
        # Valid URLs
        assert Validator.is_valid_url("https://example.com") == True
        assert Validator.is_valid_url("http://test.org/path") == True
        
        # Invalid URLs
        assert Validator.is_valid_url("not-a-url") == False
        assert Validator.is_valid_url("ftp://invalid") == False
    
    def test_phone_validation(self):
        """Test phone number validation."""
        from utils.validators import Validator
        
        # Valid phone numbers (basic format)
        assert Validator.is_valid_phone("+1234567890") == True
        assert Validator.is_valid_phone("1234567890") == True
        
        # Invalid phone numbers
        assert Validator.is_valid_phone("123") == False
        assert Validator.is_valid_phone("abc123") == False


class TestCache:
    """Test the cache module."""
    
    def test_cache_import(self):
        """Test that cache can be imported."""
        from utils.cache import MemoryCache
        assert MemoryCache is not None
    
    def test_memory_cache_basic(self):
        """Test basic cache operations."""
        from utils.cache import MemoryCache
        
        cache = MemoryCache()
        
        # Test set and get
        cache.set("key1", "value1")
        assert cache.get("key1") == "value1"
        
        # Test non-existent key
        assert cache.get("nonexistent") is None
        
        # Test with default
        assert cache.get("nonexistent", "default") == "default"


class TestFiles:
    """Test the files module."""
    
    def test_files_import(self):
        """Test that file utilities can be imported."""
        from utils.files import ensure_directory, get_file_extension
        assert ensure_directory is not None
        assert get_file_extension is not None
    
    def test_get_file_extension(self):
        """Test file extension extraction."""
        from utils.files import get_file_extension
        
        assert get_file_extension("test.txt") == ".txt"
        assert get_file_extension("image.png") == ".png"
        assert get_file_extension("document.pdf") == ".pdf"
        assert get_file_extension("noextension") == ""


class TestText:
    """Test the text module."""
    
    def test_text_import(self):
        """Test that text utilities can be imported."""
        from utils.text import truncate_text, escape_markdown
        assert truncate_text is not None
        assert escape_markdown is not None
    
    def test_truncate_text(self):
        """Test text truncation."""
        from utils.text import truncate_text
        
        long_text = "This is a very long text that should be truncated"
        
        # Test truncation
        result = truncate_text(long_text, 20)
        assert len(result) <= 23  # 20 + "..." = 23
        assert result.endswith("...")
        
        # Test short text (no truncation)
        short_text = "Short"
        result = truncate_text(short_text, 20)
        assert result == short_text
    
    def test_escape_markdown(self):
        """Test markdown escaping."""
        from utils.text import escape_markdown
        
        text_with_markdown = "This has *bold* and _italic_ text"
        result = escape_markdown(text_with_markdown)
        
        # Should escape markdown characters
        assert "*" not in result or "\\*" in result
        assert "_" not in result or "\\_" in result