"""
Integration tests for the Telegram Bot Template.

This module contains integration tests that test the interaction
between multiple components and end-to-end functionality.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch
import asyncio

from tests.utils import mock_config, mock_bot, mock_update, skip_if_no_token, TestConfig


class TestBotIntegration:
    """Integration tests for bot functionality."""
    
    @pytest.mark.asyncio
    async def test_bot_startup_shutdown(self, mock_config):
        """Test complete bot startup and shutdown cycle."""
        from core.runner import BotRunner
        
        with patch('core.runner.BotFactory') as mock_factory:
            mock_app = Mock()
            mock_app.run_polling = AsyncMock()
            mock_app.stop = AsyncMock()
            mock_factory.create_bot.return_value = mock_app
            
            runner = BotRunner()
            
            # Test that runner can be created and has required methods
            assert hasattr(runner, 'start')
            assert hasattr(runner, 'stop')
    
    @pytest.mark.asyncio
    async def test_command_flow(self, mock_config, mock_update):
        """Test complete command handling flow."""
        from bot.handlers.commands import start_command
        from core.middleware import RateLimiter
        
        # Configure mock for async reply_text
        mock_update.message.reply_text = AsyncMock()
        
        # Provide proper mock data to avoid JSON serialization errors
        mock_update.effective_user.id = 12345
        mock_update.effective_user.first_name = "TestUser"
        mock_update.effective_user.username = "testuser"
        mock_update.effective_chat.id = 67890
        
        # Test rate limiting + command handling
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        user_id = mock_update.effective_user.id
        
        # Should be allowed initially (not async)
        assert limiter.is_allowed(user_id) == True
        
        # Execute command
        context = Mock()
        await start_command(mock_update, context)
        
        # Verify response
        mock_update.message.reply_text.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_error_handling_flow(self, mock_config, mock_update):
        """Test error handling integration."""
        from bot.handlers.errors import error_handler
        
        context = Mock()
        context.error = Exception("Test integration error")
        
        # Should handle error without crashing
        await error_handler(mock_update, context)
        
        # Test passes if no exception is raised


class TestConfigurationIntegration:
    """Integration tests for configuration loading."""
    
    def test_config_loading_chain(self, mock_config):
        """Test that configuration loads through the entire chain."""
        from core.config import Config
        from core.logger import get_logger
        from core.database import Database
        
        # Test config is accessible
        assert Config.BOT_TOKEN == TestConfig.BOT_TOKEN
        
        # Test logger uses config
        logger = get_logger("integration_test")
        assert logger is not None
        
        # Test database uses config
        db = Database(Config.DATABASE_URL)
        assert db.db_path == Config.DATABASE_URL  # Database constructor uses the path as-is when provided
    
    def test_service_configuration(self, mock_config):
        """Test that services are configured correctly."""
        from services.polling import PollingService
        from services.webhook import WebhookService
        
        # Create mock applications
        mock_polling_app = Mock()
        mock_webhook_app = Mock()
        
        # Both services should be creatable with mock applications
        polling_service = PollingService(mock_polling_app)
        webhook_service = WebhookService(mock_webhook_app)
        
        assert polling_service is not None
        assert webhook_service is not None


class TestDatabaseIntegration:
    """Integration tests for database functionality."""
    
    @pytest.mark.asyncio
    async def test_database_lifecycle(self, temp_db):
        """Test database creation and basic operations."""
        from core.database import Database
        
        db = Database(temp_db)
        assert db is not None
        
        # Test database connection (if implemented)
        # This would test actual database operations in a real implementation


class TestMiddlewareIntegration:
    """Integration tests for middleware."""
    
    @pytest.mark.asyncio
    async def test_rate_limiting_integration(self, mock_update):
        """Test rate limiting with actual handlers."""
        from core.middleware import RateLimiter
        from bot.handlers.commands import start_command
        
        # Configure mock for async reply_text
        mock_update.message.reply_text = AsyncMock()
        
        # Provide proper mock data to avoid JSON serialization errors
        mock_update.effective_user.id = 12345
        mock_update.effective_user.first_name = "TestUser"
        mock_update.effective_user.username = "testuser"
        mock_update.effective_chat.id = 67890
        
        limiter = RateLimiter(max_requests=2, window_seconds=60)
        user_id = mock_update.effective_user.id
        
        # First two requests should pass (not async)
        assert limiter.is_allowed(user_id) == True
        context = Mock()
        await start_command(mock_update, context)
        
        assert limiter.is_allowed(user_id) == True
        await start_command(mock_update, context)
        
        # Third should be rate limited
        assert limiter.is_allowed(user_id) == False
        
        # Verify commands were called
        assert mock_update.message.reply_text.call_count == 2


@skip_if_no_token
class TestRealBotIntegration:
    """Integration tests with real bot token (if available)."""
    
    @pytest.mark.asyncio
    async def test_real_bot_creation(self):
        """Test creating bot with real token."""
        import os
        from bot.factory import BotFactory
        
        # Only run if real token is available
        if not os.getenv("BOT_TOKEN"):
            pytest.skip("No real BOT_TOKEN available")
        
        # This would test with real Telegram API
        # Commented out to avoid actual API calls in tests
        # bot = BotFactory.create_bot()
        # assert bot is not None
        pass


class TestUtilityIntegration:
    """Integration tests for utility functions."""
    
    def test_formatter_keyboard_integration(self):
        """Test formatters work with keyboards."""
        from utils.formatters import format_user
        from utils.keyboards import create_inline_keyboard
        
        # Create mock user
        user = type('User', (), {
            'id': 12345,
            'first_name': 'John',
            'username': 'johndoe'
        })()
        
        # Format user
        user_text = format_user(user)
        
        # Create keyboard with user info
        buttons = [[("User Info", f"user_{user.id}")]]
        keyboard = create_inline_keyboard(buttons)
        
        assert user_text is not None
        assert keyboard is not None
        assert hasattr(keyboard, 'inline_keyboard')
    
    def test_validator_formatter_integration(self):
        """Test validators work with formatters."""
        from utils.validators import Validator
        from utils.formatters import format_datetime
        from datetime import datetime
        
        # Test email validation
        email = "test@example.com"
        assert Validator.is_valid_email(email) == True
        
        # Test datetime formatting
        dt = datetime.now()
        formatted_dt = format_datetime(dt)
        assert isinstance(formatted_dt, str)
        assert len(formatted_dt) > 0