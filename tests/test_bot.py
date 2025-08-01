"""
Unit tests for bot components.

This module tests bot factory, handlers, and related functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from tests.utils import mock_config, mock_bot, mock_message, mock_update, TestConfig


class TestBotFactory:
    """Test the bot factory module."""
    
    def test_factory_import(self):
        """Test that BotFactory can be imported."""
        from bot.factory import BotFactory
        assert BotFactory is not None
    
    def test_factory_creation(self, mock_config):
        """Test bot factory creates bot and dispatcher correctly."""
        from bot.factory import BotFactory
        
        with patch('bot.factory.Bot') as mock_bot_class, \
             patch('bot.factory.Dispatcher') as mock_dp_class, \
             patch('bot.factory.register_handlers') as mock_register:
            
            mock_bot = Mock()
            mock_dp = Mock()
            mock_bot_class.return_value = mock_bot
            mock_dp_class.return_value = mock_dp
            
            # Test individual creation methods
            bot = BotFactory.create_bot()
            dp = BotFactory.create_dispatcher()
            
            assert bot is not None
            assert dp is not None
            mock_bot_class.assert_called_once()
            mock_dp_class.assert_called_once()
            mock_register.assert_called_once_with(mock_dp)


class TestCommandHandlers:
    """Test command handlers."""
    
    def test_commands_import(self):
        """Test that command handlers can be imported."""
        from bot.handlers.commands import start_command, help_command, status_command
        assert start_command is not None
        assert help_command is not None
        assert status_command is not None
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_message):
        """Test start command handler."""
        from bot.handlers.commands import start_command
        
        await start_command(mock_message)
        
        # Verify response was sent
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args[0]
        assert "Welcome" in call_args[0] or "start" in call_args[0].lower()
    
    @pytest.mark.asyncio
    async def test_help_command(self, mock_message):
        """Test help command handler."""
        from bot.handlers.commands import help_command
        
        await help_command(mock_message)
        
        # Verify response was sent
        mock_message.answer.assert_called_once()
        call_args = mock_message.answer.call_args
        # Check if parse_mode was used
        assert call_args is not None


class TestMessageHandlers:
    """Test message handlers."""
    
    def test_messages_import(self):
        """Test that message handlers can be imported."""
        from bot.handlers.messages import handle_message, handle_photo
        assert handle_message is not None
        assert handle_photo is not None
    
    @pytest.mark.asyncio
    async def test_handle_message(self, mock_message):
        """Test message handler."""
        from bot.handlers.messages import handle_message
        
        mock_message.text = "Hello, bot!"
        
        await handle_message(mock_message)
        
        # Verify some response was sent (implementation dependent)
        mock_message.answer.assert_called_once()


class TestErrorHandlers:
    """Test error handlers."""
    
    def test_errors_import(self):
        """Test that error handlers can be imported."""
        from bot.handlers.errors import error_handler
        
        assert error_handler is not None
    
    @pytest.mark.asyncio
    async def test_error_handler(self, mock_update):
        """Test error handler functionality."""
        from bot.handlers.errors import error_handler
        from aiogram.types import ErrorEvent
        
        error = Exception("Test error")
        error_event = ErrorEvent(update=mock_update, exception=error)
        
        # Should handle error without crashing
        await error_handler(error_event)
        
        # Test passes if no exception is raised