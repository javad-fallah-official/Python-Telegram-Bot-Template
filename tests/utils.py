"""Test utilities and fixtures for the Telegram Bot Template.

This module provides common test utilities, fixtures, and helper functions
that can be used across all test modules."""

import asyncio
import pytest
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any, Generator
import tempfile
import os

from aiogram import Bot, Dispatcher
from aiogram.types import User, Chat, Message, Update
from core.config import Config


class TestConfig:
    """Test configuration with safe default values."""
    
    BOT_TOKEN = "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    BOT_MODE = "polling"
    DEBUG = True
    DATABASE_URL = "sqlite:///test.db"
    LOG_LEVEL = "DEBUG"
    RATE_LIMIT_MESSAGES = 5
    RATE_LIMIT_WINDOW = 60


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def mock_config():
    """Provide a mock configuration for testing."""
    original_values = {}
    
    # Store original values
    for attr in dir(TestConfig):
        if not attr.startswith('_') and hasattr(Config, attr):
            original_values[attr] = getattr(Config, attr, None)
            setattr(Config, attr, getattr(TestConfig, attr))
    
    yield Config
    
    # Restore original values
    for attr, value in original_values.items():
        setattr(Config, attr, value)


@pytest.fixture
def mock_bot():
    """Provide a mock aiogram Bot instance."""
    bot = AsyncMock(spec=Bot)
    bot.token = TestConfig.BOT_TOKEN
    bot.get_me = AsyncMock(return_value=User(
        id=123456789,
        is_bot=True,
        first_name="TestBot",
        username="test_bot"
    ))
    return bot


@pytest.fixture
def mock_update():
    """Provide a mock Telegram update."""
    update = Mock()
    update.message = Mock()
    update.message.text = "/test"
    update.message.from_user = Mock(id=12345, first_name="TestUser")
    update.message.chat = Mock(id=67890, type="private")
    update.message.reply_text = AsyncMock()
    return update


@pytest.fixture
def temp_db():
    """Provide a temporary database for testing."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as tmp:
        db_path = tmp.name
    
    yield f"sqlite:///{db_path}"
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture
def mock_logger():
    """Provide a mock logger for testing."""
    logger = Mock()
    logger.info = Mock()
    logger.debug = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


class AsyncContextManager:
    """Helper class for testing async context managers."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


def create_mock_context(return_value=None):
    """Create a mock async context manager."""
    return AsyncContextManager(return_value)


def assert_called_with_partial(mock_obj, **expected_kwargs):
    """Assert that a mock was called with at least the specified kwargs."""
    assert mock_obj.called, "Mock was not called"
    
    call_args = mock_obj.call_args
    if call_args is None:
        raise AssertionError("Mock was not called")
    
    actual_kwargs = call_args.kwargs
    for key, expected_value in expected_kwargs.items():
        assert key in actual_kwargs, f"Expected keyword argument '{key}' not found"
        assert actual_kwargs[key] == expected_value, \
            f"Expected {key}={expected_value}, got {actual_kwargs[key]}"


def run_async_test(coro):
    """Helper to run async functions in tests."""
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


# Test data generators
def generate_test_messages():
    """Generate test message data."""
    return [
        {"text": "/start", "expected_response": "Welcome"},
        {"text": "/help", "expected_response": "Available commands"},
        {"text": "Hello", "expected_response": None},  # No specific response
    ]


def generate_test_users():
    """Generate test user data."""
    return [
        {"id": 1, "first_name": "Alice", "username": "alice"},
        {"id": 2, "first_name": "Bob", "username": "bob"},
        {"id": 3, "first_name": "Charlie", "username": None},
    ]


# Decorators for common test patterns
def skip_if_no_token(func):
    """Skip test if no real bot token is available."""
    def wrapper(*args, **kwargs):
        if not os.getenv("BOT_TOKEN"):
            pytest.skip("No BOT_TOKEN available for integration test")
        return func(*args, **kwargs)
    return wrapper


def requires_database(func):
    """Mark test as requiring database."""
    return pytest.mark.asyncio(func)


# Common assertions
def assert_valid_response(response):
    """Assert that a bot response is valid."""
    assert response is not None
    assert isinstance(response, (str, dict))
    if isinstance(response, str):
        assert len(response.strip()) > 0


def assert_valid_config(config):
    """Assert that configuration is valid."""
    assert hasattr(config, 'BOT_TOKEN')
    assert hasattr(config, 'BOT_MODE')
    assert config.BOT_MODE in ['polling', 'webhook']