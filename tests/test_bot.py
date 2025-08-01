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
        """Test BotFactory bot creation."""
        from bot.factory import BotFactory
        
        with patch('aiogram.Bot') as mock_bot_class:
            with patch('aiogram.Dispatcher') as mock_dispatcher_class:
                mock_bot = Mock()
                mock_dp = Mock()
                mock_bot_class.return_value = mock_bot
                mock_dispatcher_class.return_value = mock_dp
                
                with patch('bot.factory.register_handlers'):
                    bot, dp = BotFactory.create_bot()
                    assert bot is not None
                    assert dp is not None


class TestCommandHandlers:
    """Test command handlers."""
    
    def test_commands_import(self):
        """Test that command handlers can be imported."""
        from bot.handlers.commands import start_command, help_command, status_command
        assert start_command is not None
        assert help_command is not None
        assert status_command is not None
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_update):
        """Test start command handler."""
        from bot.handlers.commands import start_command
        
        # Configure mock for async reply_text
        mock_update.message.reply_text = AsyncMock()
        
        # Provide proper mock data to avoid JSON serialization errors
        mock_update.effective_user.id = 12345
        mock_update.effective_user.first_name = "TestUser"
        mock_update.effective_user.username = "testuser"
        mock_update.effective_chat.id = 67890
        
        context = Mock()
        await start_command(mock_update, context)
        
        # Verify response was sent
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0]
        assert "Welcome" in call_args[0] or "start" in call_args[0].lower()
    
    @pytest.mark.asyncio
    async def test_help_command(self, mock_update):
        """Test help command handler."""
        from bot.handlers.commands import help_command
        
        # Configure mock for async reply_html
        mock_update.message.reply_html = AsyncMock()
        
        # Provide proper mock data to avoid JSON serialization errors
        mock_update.effective_user.id = 12345
        mock_update.effective_user.first_name = "TestUser"
        mock_update.effective_user.username = "testuser"
        mock_update.effective_chat.id = 67890
        
        context = Mock()
        await help_command(mock_update, context)
        
        # Verify response was sent
        mock_update.message.reply_html.assert_called_once()
        call_args = mock_update.message.reply_html.call_args[0]
        assert "help" in call_args[0].lower() or "command" in call_args[0].lower()


class TestMessageHandlers:
    """Test message handlers."""
    
    def test_messages_import(self):
        """Test that message handlers can be imported."""
        from bot.handlers.messages import handle_message, handle_photo
        assert handle_message is not None
        assert handle_photo is not None
    
    @pytest.mark.asyncio
    async def test_handle_message(self, mock_update):
        """Test message handler."""
        from bot.handlers.messages import handle_message
        
        # Configure mock for async reply_html
        mock_update.message.reply_html = AsyncMock()
        
        # Provide proper mock data to avoid JSON serialization errors
        mock_update.effective_user.id = 12345
        mock_update.effective_user.first_name = "TestUser"
        mock_update.effective_user.username = "testuser"
        mock_update.effective_chat.id = 67890
        
        context = Mock()
        mock_update.message.text = "Hello, bot!"
        
        await handle_message(mock_update, context)
        
        # Verify some response was sent (implementation dependent)
        mock_update.message.reply_html.assert_called_once()


class TestErrorHandlers:
    """Test error handlers."""
    
    def test_errors_import(self):
        """Test that error handlers can be imported."""
        from bot.handlers.errors import error_handler, timeout_handler
        assert error_handler is not None
        assert timeout_handler is not None
    
    @pytest.mark.asyncio
    async def test_error_handler(self, mock_update):
        """Test error handler."""
        from bot.handlers.errors import error_handler
        
        context = Mock()
        context.error = Exception("Test error")
        
        await error_handler(mock_update, context)
        
        # Verify handler doesn't crash with errors