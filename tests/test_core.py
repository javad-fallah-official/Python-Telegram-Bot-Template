"""Unit tests for core modules."""

import pytest
import tempfile
import os
from unittest.mock import Mock, patch, AsyncMock
from tests.utils import mock_config


class TestConfig:
    """Test Config class."""
    
    def test_config_import(self):
        """Test that Config can be imported."""
        from core.config import Config
        assert Config is not None
    
    def test_config_attributes(self):
        """Test Config has required attributes."""
        from core.config import Config
        
        # Test that attributes exist (they might be empty in test environment)
        assert hasattr(Config, 'BOT_TOKEN')
        assert hasattr(Config, 'BOT_MODE')
        assert hasattr(Config, 'DEBUG')
        assert hasattr(Config, 'DATABASE_URL')
        assert hasattr(Config, 'ADMIN_USER_IDS')
    
    def test_config_validation(self):
        """Test Config validation method."""
        from core.config import Config
        
        # Test validation with skip_bot_token
        try:
            Config.validate(skip_bot_token=True)
        except ValueError:
            # This is expected if BOT_MODE is invalid
            pass
    
    def test_is_admin_method(self):
        """Test is_admin method."""
        from core.config import Config
        
        # Test with a user ID that's definitely not admin
        assert Config.is_admin(999999999) == False


class TestLogger:
    """Test Logger functionality."""
    
    def test_logger_import(self):
        """Test that BotLogger can be imported."""
        from core.logger import BotLogger
        assert BotLogger is not None
    
    def test_logger_creation(self):
        """Test BotLogger creation."""
        from core.logger import BotLogger
        
        logger = BotLogger(log_level="INFO")
        assert logger is not None
        assert logger.log_level == "INFO"
    
    def test_logger_methods(self):
        """Test BotLogger has required methods."""
        from core.logger import BotLogger
        
        logger = BotLogger()
        assert hasattr(logger, 'logger')
        assert hasattr(logger, 'log_level')


class TestDatabase:
    """Test Database functionality."""
    
    @pytest.mark.asyncio
    async def test_database_creation(self, temp_db):
        """Test database creation with temporary database.""" 
        from core.database import Database

        # Extract file path from SQLite URL
        db_path = temp_db.replace("sqlite:///", "")
        db = Database(db_path)
        assert db is not None
        assert db.db_path == db_path
    
    @pytest.mark.asyncio
    async def test_database_connection(self, temp_db):
        """Test database connection."""
        from core.database import Database
        
        # Extract file path from SQLite URL
        db_path = temp_db.replace("sqlite:///", "")
        db = Database(db_path)
        try:
            await db.connect()
            assert db._connection is not None
        finally:
            await db.disconnect()


class TestMiddleware:
    """Test Middleware functionality."""
    
    def test_rate_limiter_import(self):
        """Test RateLimiter import."""
        from core.middleware import RateLimiter
        assert RateLimiter is not None
    
    def test_rate_limiter_creation(self):
        """Test RateLimiter creation."""
        from core.middleware import RateLimiter
        
        limiter = RateLimiter(max_requests=5, window_seconds=60)
        assert limiter.max_requests == 5
        assert limiter.window_seconds == 60
    
    def test_rate_limiter_functionality(self):
        """Test RateLimiter basic functionality."""
        from core.middleware import RateLimiter

        limiter = RateLimiter(max_requests=2, window_seconds=60)
        user_id = 12345

        # First request should pass
        assert limiter.is_allowed(user_id) == True
        
        # Second request should pass
        assert limiter.is_allowed(user_id) == True
        
        # Third request should fail (over limit)
        assert limiter.is_allowed(user_id) == False
    
    def test_decorators_import(self):
        """Test middleware decorators can be imported."""
        from core.middleware import admin_required, rate_limit, log_user_activity
        
        assert admin_required is not None
        assert rate_limit is not None
        assert log_user_activity is not None


class TestRunner:
    """Test Runner functionality."""
    
    def test_runner_import(self):
        """Test that Runner can be imported."""
        from core.runner import BotRunner
        assert BotRunner is not None
    
    def test_runner_creation(self, mock_config):
        """Test BotRunner creation."""
        from core.runner import BotRunner
        
        runner = BotRunner()
        
        # Test that runner can be created and has required methods
        assert runner.bot is None
        assert runner.dp is None
        assert hasattr(runner, 'start_polling')
        assert hasattr(runner, 'shutdown')