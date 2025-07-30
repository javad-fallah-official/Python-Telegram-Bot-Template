"""
Database factory for choosing between SQLite and PostgreSQL.

This module provides a unified interface for database operations
while allowing easy switching between database backends.
"""

import logging
from typing import Optional, Union
from .config import Config
from .database import Database
from .postgres import PostgreSQLDatabase

logger = logging.getLogger(__name__)


class DatabaseFactory:
    """Factory class for creating database instances based on configuration."""
    
    @staticmethod
    def create_database(database_url: str = None) -> Union[Database, PostgreSQLDatabase]:
        """
        Create a database instance based on the database URL and configuration.
        
        Args:
            database_url: Database connection URL. If None, uses Config.DATABASE_URL
            
        Returns:
            Database instance (SQLite or PostgreSQL)
        """
        url = database_url or Config.DATABASE_URL
        
        # Check if user has explicitly set DATABASE_TYPE
        if Config.DATABASE_TYPE == "postgresql":
            logger.info("Creating PostgreSQL database instance (forced by DATABASE_TYPE)")
            return PostgreSQLDatabase(url)
        elif Config.DATABASE_TYPE == "sqlite":
            logger.info("Creating SQLite database instance (forced by DATABASE_TYPE)")
            return Database(url)
        else:
            # Auto-detect based on URL (default behavior)
            if url.startswith('postgresql://') or url.startswith('postgres://'):
                logger.info("Creating PostgreSQL database instance (auto-detected from URL)")
                return PostgreSQLDatabase(url)
            elif url.startswith('sqlite://') or url.endswith('.db'):
                logger.info("Creating SQLite database instance (auto-detected from URL)")
                return Database(url)
            else:
                # Default to SQLite for backward compatibility
                logger.warning(f"Unknown database URL format: {url}. Defaulting to SQLite.")
                return Database(url)
    
    @staticmethod
    def get_database_type(database_url: str = None) -> str:
        """
        Get the database type from configuration or URL.
        
        Args:
            database_url: Database connection URL
            
        Returns:
            Database type ('postgresql' or 'sqlite')
        """
        # Check if user has explicitly set DATABASE_TYPE
        if Config.DATABASE_TYPE == "postgresql":
            return 'postgresql'
        elif Config.DATABASE_TYPE == "sqlite":
            return 'sqlite'
        else:
            # Auto-detect based on URL
            url = database_url or Config.DATABASE_URL
            if url.startswith('postgresql://') or url.startswith('postgres://'):
                return 'postgresql'
            else:
                return 'sqlite'


class UnifiedDatabase:
    """
    Unified database interface that works with both SQLite and PostgreSQL.
    
    This class provides a common interface for database operations,
    automatically choosing the appropriate backend based on configuration.
    """
    
    def __init__(self, database_url: str = None):
        """Initialize unified database with automatic backend selection."""
        self._db = DatabaseFactory.create_database(database_url)
        self.database_type = DatabaseFactory.get_database_type(database_url)
        
    async def connect(self, **kwargs):
        """Connect to the database with backend-specific options."""
        if self.database_type == 'postgresql':
            # PostgreSQL connect method doesn't accept parameters
            await self._db.connect()
        else:
            # SQLite connection
            await self._db.connect()
    
    async def disconnect(self):
        """Disconnect from the database."""
        await self._db.disconnect()
    
    async def save_user(self, user_data=None, user_id=None, username=None, first_name=None, 
                       last_name=None, language_code=None, metadata=None) -> bool:
        """Save or update user information."""
        if self.database_type == 'postgresql':
            # PostgreSQL expects individual parameters
            if user_data is not None:
                # Convert dictionary to individual parameters
                return await self._db.save_user(
                    user_id=user_data.get('id') or user_data.get('user_id'),
                    username=user_data.get('username'),
                    first_name=user_data.get('first_name'),
                    last_name=user_data.get('last_name'),
                    language_code=user_data.get('language_code'),
                    metadata=user_data.get('metadata')
                )
            else:
                # Use individual parameters directly
                return await self._db.save_user(
                    user_id=user_id,
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    language_code=language_code,
                    metadata=metadata
                )
        else:
            # SQLite expects dictionary
            if user_data is not None:
                return await self._db.save_user(user_data)
            else:
                # Convert individual parameters to dictionary
                user_dict = {
                    'id': user_id,
                    'username': username,
                    'first_name': first_name,
                    'last_name': last_name,
                    'language_code': language_code
                }
                if metadata:
                    user_dict.update(metadata)
                return await self._db.save_user(user_dict)
    
    async def get_user(self, user_id: int) -> Optional[dict]:
        """Get user information by ID."""
        return await self._db.get_user(user_id)
    
    async def log_activity(self, user_id: int, action: str, data=None) -> bool:
        """Log user activity."""
        if self.database_type == 'postgresql' and isinstance(data, dict):
            # PostgreSQL supports structured data
            return await self._db.log_activity(user_id, action, data)
        else:
            # SQLite expects string data
            data_str = str(data) if data is not None else None
            return await self._db.log_activity(user_id, action, data_str)
    
    async def get_user_activity(self, user_id: int, limit: int = 10, **kwargs) -> list:
        """Get user activity history."""
        if self.database_type == 'postgresql':
            # PostgreSQL supports pagination
            offset = kwargs.get('offset', 0)
            return await self._db.get_user_activity(user_id, limit, offset)
        else:
            # SQLite basic implementation
            return await self._db.get_user_activity(user_id, limit)
    
    async def set_setting(self, key: str, value, description: str = None) -> bool:
        """Set a bot setting."""
        if self.database_type == 'postgresql':
            # PostgreSQL supports complex data types and descriptions
            return await self._db.set_setting(key, value, description)
        else:
            # SQLite expects string values
            value_str = str(value) if not isinstance(value, str) else value
            return await self._db.set_setting(key, value_str)
    
    async def get_setting(self, key: str, default=None):
        """Get a bot setting."""
        return await self._db.get_setting(key, default)
    
    async def get_user_count(self) -> int:
        """Get total number of users."""
        return await self._db.get_user_count()
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy."""
        if hasattr(self._db, 'health_check'):
            return await self._db.health_check()
        else:
            # Basic health check for SQLite
            try:
                await self.get_user_count()
                return True
            except Exception:
                return False
    
    # PostgreSQL-specific methods (only available when using PostgreSQL)
    async def get_users_batch(self, user_ids: list) -> list:
        """Get multiple users in a single query (PostgreSQL only)."""
        if self.database_type == 'postgresql':
            return await self._db.get_users_batch(user_ids)
        else:
            # Fallback for SQLite: get users one by one
            users = []
            for user_id in user_ids:
                user = await self.get_user(user_id)
                if user:
                    users.append(user)
            return users
    
    async def get_active_users_count(self, days: int = 7) -> int:
        """Get count of users active in the last N days (PostgreSQL only)."""
        if self.database_type == 'postgresql':
            return await self._db.get_active_users_count(days)
        else:
            logger.warning("get_active_users_count not implemented for SQLite")
            return 0
    
    async def record_metric(self, metric_name: str, value: int, metadata: dict = None) -> bool:
        """Record a bot metric for analytics (PostgreSQL only)."""
        if self.database_type == 'postgresql':
            return await self._db.record_metric(metric_name, value, metadata)
        else:
            logger.warning("record_metric not implemented for SQLite")
            return False
    
    async def get_metrics(self, metric_name: str, limit: int = 100) -> list:
        """Get historical metrics data (PostgreSQL only)."""
        if self.database_type == 'postgresql':
            return await self._db.get_metrics(metric_name, limit)
        else:
            logger.warning("get_metrics not implemented for SQLite")
            return []
    
    @property
    def is_postgresql(self) -> bool:
        """Check if using PostgreSQL backend."""
        return self.database_type == 'postgresql'
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite backend."""
        return self.database_type == 'sqlite'


# Global unified database instance
db = UnifiedDatabase()