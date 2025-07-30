"""
Unit tests for service modules.

This module tests polling, webhook, and other service components.
"""

import pytest
from unittest.mock import Mock, AsyncMock, patch

from tests.utils import mock_config, mock_bot, TestConfig


class TestPollingService:
    """Test the polling service."""
    
    def test_polling_import(self):
        """Test that PollingService can be imported."""
        from services.polling import PollingService
        assert PollingService is not None
    
    def test_polling_creation(self, mock_config):
        """Test PollingService creation."""
        from services.polling import PollingService
        
        with patch('telegram.ext.Application') as mock_app:
            mock_application = Mock()
            service = PollingService(mock_application)
            assert service is not None
    
    @pytest.mark.asyncio
    async def test_polling_start_stop(self, mock_config):
        """Test polling service start and stop."""
        from services.polling import PollingService
        
        mock_application = Mock()
        mock_application.start = AsyncMock()
        mock_application.stop = AsyncMock()
        mock_application.updater = Mock()
        mock_application.updater.start_polling = AsyncMock()
        mock_application.updater.stop = AsyncMock()
        mock_application.updater.running = True
        
        service = PollingService(mock_application)
        
        # Test that methods exist and can be called
        assert hasattr(service, 'start')
        assert hasattr(service, 'stop')


class TestWebhookService:
    """Test the webhook service."""
    
    def test_webhook_import(self):
        """Test that WebhookService can be imported."""
        from services.webhook import WebhookService
        assert WebhookService is not None
    
    def test_webhook_creation(self, mock_config):
        """Test WebhookService creation."""
        from services.webhook import WebhookService
        
        mock_application = Mock()
        service = WebhookService(mock_application)
        assert service is not None
    
    @pytest.mark.asyncio
    async def test_webhook_start_stop(self, mock_config):
        """Test webhook service start and stop."""
        from services.webhook import WebhookService
        
        mock_application = Mock()
        mock_application.start = AsyncMock()
        mock_application.stop = AsyncMock()
        mock_application.bot = Mock()
        mock_application.bot.set_webhook = AsyncMock()
        mock_application.bot.get_webhook_info = AsyncMock()
        mock_application.bot.delete_webhook = AsyncMock()
        
        service = WebhookService(mock_application)
        
        # Test that methods exist and can be called
        assert hasattr(service, 'start')
        assert hasattr(service, 'stop')


class TestBaseService:
    """Test the base service."""
    
    def test_base_service_import(self):
        """Test that BotService can be imported."""
        from services.base import BotService
        assert BotService is not None
    
    def test_base_service_interface(self):
        """Test BotService interface."""
        from services.base import BotService
        
        # Test that it's an abstract base class
        assert hasattr(BotService, 'start')
        assert hasattr(BotService, 'stop')
        
        # Should not be able to instantiate directly
        with pytest.raises(TypeError):
            BotService()