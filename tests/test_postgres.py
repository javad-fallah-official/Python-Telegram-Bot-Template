"""
Tests for PostgreSQL database functionality.

This module tests the PostgreSQL implementation and unified database interface.
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
import os

from core.postgres import PostgreSQLDatabase
from core.db_factory import DatabaseFactory, UnifiedDatabase


class TestPostgreSQLDatabase:
    """Test PostgreSQL database functionality."""
    
    def test_postgres_import(self):
        """Test that PostgreSQL module can be imported."""
        assert PostgreSQLDatabase is not None
    
    def test_postgres_creation(self):
        """Test PostgreSQL database creation."""
        db = PostgreSQLDatabase("postgresql://user:pass@localhost/test")
        assert db.url == "postgresql://user:pass@localhost/test"
        assert db.pool is None
    
    @pytest.mark.asyncio
    async def test_postgres_connection_mock(self):
        """Test PostgreSQL connection with mocked asyncpg."""
        with patch('core.postgres.asyncpg') as mock_asyncpg:
            # Create a proper async mock for the pool
            mock_pool = AsyncMock()
            
            # Make create_pool return the mock pool directly (not a coroutine)
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
            
            db = PostgreSQLDatabase("postgresql://user:pass@localhost/test")
            
            # Mock the create_tables method to avoid pool.acquire() issues
            with patch.object(db, 'create_tables', new_callable=AsyncMock) as mock_create_tables:
                await db.connect()
                
                assert db.pool == mock_pool
                mock_create_tables.assert_called_once()


class TestDatabaseFactory:
    """Test database factory functionality."""
    
    def test_factory_import(self):
        """Test that DatabaseFactory can be imported."""
        assert DatabaseFactory is not None
    
    def test_create_postgresql(self):
        """Test creating PostgreSQL database via factory."""
        db = DatabaseFactory.create_database("postgresql://user:pass@localhost/test")
        assert isinstance(db, PostgreSQLDatabase)
    
    def test_create_sqlite(self):
        """Test creating SQLite database via factory."""
        from core.database import Database
        db = DatabaseFactory.create_database("sqlite:///test.db")
        assert isinstance(db, Database)
    
    def test_detect_postgres_type(self):
        """Test PostgreSQL URL detection."""
        assert DatabaseFactory.get_database_type("postgresql://test") == "postgresql"
        assert DatabaseFactory.get_database_type("postgres://test") == "postgresql"
    
    def test_detect_sqlite_type(self):
        """Test SQLite URL detection."""
        assert DatabaseFactory.get_database_type("sqlite:///test.db") == "sqlite"
    
    def test_database_type_configuration(self):
        """Test DATABASE_TYPE configuration override."""
        import os
        from core.config import Config
        
        # Save original values
        original_db_type = os.getenv("DATABASE_TYPE")
        original_config_type = Config.DATABASE_TYPE
        
        try:
            # Test forcing PostgreSQL
            os.environ["DATABASE_TYPE"] = "postgresql"
            Config.DATABASE_TYPE = "postgresql"
            
            db_type = DatabaseFactory.get_database_type("simple.db")  # SQLite URL
            assert db_type == "postgresql"  # Should be forced to PostgreSQL
            
            # Test forcing SQLite
            os.environ["DATABASE_TYPE"] = "sqlite"
            Config.DATABASE_TYPE = "sqlite"
            
            db_type = DatabaseFactory.get_database_type("postgresql://test@localhost/test")  # PostgreSQL URL
            assert db_type == "sqlite"  # Should be forced to SQLite
            
            # Test auto mode
            os.environ["DATABASE_TYPE"] = "auto"
            Config.DATABASE_TYPE = "auto"
            
            db_type = DatabaseFactory.get_database_type("postgresql://test@localhost/test")
            assert db_type == "postgresql"  # Should auto-detect PostgreSQL
            
            db_type = DatabaseFactory.get_database_type("simple.db")
            assert db_type == "sqlite"  # Should auto-detect SQLite
            
        finally:
            # Restore original values
            if original_db_type is not None:
                os.environ["DATABASE_TYPE"] = original_db_type
            elif "DATABASE_TYPE" in os.environ:
                del os.environ["DATABASE_TYPE"]
            Config.DATABASE_TYPE = original_config_type

    def test_database_creation_with_type_override(self):
        """Test database creation with DATABASE_TYPE override."""
        import os
        from core.config import Config
        
        # Save original values
        original_db_type = os.getenv("DATABASE_TYPE")
        original_config_type = Config.DATABASE_TYPE
        
        try:
            # Test forcing SQLite with PostgreSQL URL
            os.environ["DATABASE_TYPE"] = "sqlite"
            Config.DATABASE_TYPE = "sqlite"
            
            from core.database import Database
            db = DatabaseFactory.create_database("postgresql://test@localhost/test")
            assert isinstance(db, Database)  # Should create SQLite instance
            
            # Test forcing PostgreSQL with SQLite URL
            os.environ["DATABASE_TYPE"] = "postgresql"
            Config.DATABASE_TYPE = "postgresql"
            
            db = DatabaseFactory.create_database("simple.db")
            assert isinstance(db, PostgreSQLDatabase)  # Should create PostgreSQL instance
            
        finally:
            # Restore original values
            if original_db_type is not None:
                os.environ["DATABASE_TYPE"] = original_db_type
            elif "DATABASE_TYPE" in os.environ:
                del os.environ["DATABASE_TYPE"]
            Config.DATABASE_TYPE = original_config_type


class TestUnifiedDatabase:
    """Test unified database interface."""
    
    def test_unified_import(self):
        """Test that UnifiedDatabase can be imported."""
        assert UnifiedDatabase is not None
    
    @pytest.mark.asyncio
    async def test_unified_sqlite_creation(self):
        """Test UnifiedDatabase with SQLite backend."""
        with patch('core.db_factory.Config') as mock_config:
            mock_config.DATABASE_URL = "sqlite:///:memory:"
            
            db = UnifiedDatabase()
            assert db._db is not None
    
    @pytest.mark.asyncio
    async def test_unified_postgresql_creation(self):
        """Test UnifiedDatabase with PostgreSQL backend."""
        with patch('core.db_factory.Config') as mock_config:
            mock_config.DATABASE_URL = "postgresql://user:pass@localhost/test"
            
            db = UnifiedDatabase()
            assert isinstance(db._db, PostgreSQLDatabase)
    
    @pytest.mark.asyncio
    async def test_unified_sqlite_operations(self):
        """Test UnifiedDatabase operations with SQLite."""
        # Use in-memory SQLite database
        db = UnifiedDatabase(":memory:")
        
        try:
            await db.connect()
            
            # Test user operations - use individual parameters for save_user
            success = await db.save_user(
                user_id=123,
                username='test_user',
                first_name='Test User'
            )
            assert success == True
            
            user = await db.get_user(123)
            assert user is not None
            
        finally:
            await db.disconnect()
    
    @pytest.mark.asyncio
    async def test_unified_postgresql_mock(self):
        """Test UnifiedDatabase operations with mocked PostgreSQL."""
        with patch('core.postgres.asyncpg') as mock_asyncpg:
            # Create proper async mock
            mock_pool = AsyncMock()
            
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
            
            db = UnifiedDatabase("postgresql://user:pass@localhost/test")
            
            # Mock the create_tables method to avoid pool.acquire() issues
            with patch.object(db._db, 'create_tables', new_callable=AsyncMock) as mock_create_tables:
                await db.connect()
                
                # Verify connection was established
                assert db._db.pool == mock_pool
                mock_create_tables.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_unified_fallback_operations(self):
        """Test UnifiedDatabase fallback for PostgreSQL-only methods."""
        # Use in-memory SQLite database
        db = UnifiedDatabase(":memory:")
        
        try:
            await db.connect()
            
            # Test PostgreSQL-only methods with SQLite (should return defaults)
            users = await db.get_users_batch([123, 456])
            assert users == []
            
            count = await db.get_active_users_count()
            assert count == 0
            
        finally:
            await db.disconnect()


class TestPostgreSQLIntegration:
    """Integration tests for PostgreSQL (requires real database)."""
    
    @pytest.mark.skipif(
        not os.getenv('POSTGRES_TEST_URL'),
        reason="POSTGRES_TEST_URL not set"
    )
    @pytest.mark.asyncio
    async def test_real_postgres_connection(self):
        """Test real PostgreSQL connection (requires POSTGRES_TEST_URL)."""
        url = os.getenv('POSTGRES_TEST_URL')
        db = PostgreSQLDatabase(url)
        
        try:
            await db.connect()
            await db.create_tables()
            
            # Test basic operations
            success = await db.save_user(
                user_id=999,
                username='test_user',
                first_name='Test User'
            )
            assert success == True
            
            user = await db.get_user(999)
            assert user is not None
            assert user['username'] == "test_user"
            
        finally:
            await db.disconnect()


class TestPerformanceConsiderations:
    """Test performance-related functionality."""
    
    def test_connection_pooling_config(self):
        """Test that connection pooling is properly configured."""
        db = PostgreSQLDatabase("postgresql://user:pass@localhost/test")
        
        # Test default pool settings
        assert hasattr(db, 'min_pool_size')
        assert hasattr(db, 'max_pool_size')
        assert db.min_pool_size >= 1
        assert db.max_pool_size >= db.min_pool_size
    
    def test_batch_operations_interface(self):
        """Test that batch operations interface exists."""
        with patch('core.postgres.asyncpg') as mock_asyncpg:
            # Create proper async mock
            mock_pool = AsyncMock()
            mock_conn = AsyncMock()
            
            # Mock the pool.acquire() context manager properly
            mock_acquire = AsyncMock()
            mock_acquire.__aenter__ = AsyncMock(return_value=mock_conn)
            mock_acquire.__aexit__ = AsyncMock(return_value=None)
            mock_pool.acquire.return_value = mock_acquire
            
            mock_asyncpg.create_pool = AsyncMock(return_value=mock_pool)
            
            db = PostgreSQLDatabase("postgresql://user:pass@localhost/test")
            
            # Check that batch operations exist
            assert hasattr(db, 'get_users_batch')
            assert hasattr(db, 'record_metric')
            assert callable(getattr(db, 'get_users_batch'))
            assert callable(getattr(db, 'record_metric'))