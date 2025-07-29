"""
Database module for the Telegram bot.
Provides simple database operations using SQLite with async support.
"""

import aiosqlite
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime
from .config import Config

logger = logging.getLogger(__name__)


class Database:
    """Simple async database wrapper for SQLite."""
    
    def __init__(self, db_path: str = None):
        self.db_path = db_path or Config.DATABASE_URL.replace('sqlite:///', '')
        self._connection = None
    
    async def connect(self):
        """Connect to the database."""
        try:
            self._connection = await aiosqlite.connect(self.db_path)
            await self._connection.execute("PRAGMA foreign_keys = ON")
            await self.create_tables()
            logger.info(f"Connected to database: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from the database."""
        if self._connection:
            await self._connection.close()
            logger.info("Disconnected from database")
    
    async def create_tables(self):
        """Create necessary tables."""
        try:
            # Users table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    is_bot BOOLEAN DEFAULT FALSE,
                    is_premium BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # User activity table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS user_activity (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    action TEXT,
                    data TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Settings table
            await self._connection.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            await self._connection.commit()
            logger.info("Database tables created/verified")
            
        except Exception as e:
            logger.error(f"Failed to create tables: {e}")
            raise
    
    async def save_user(self, user_data: Dict[str, Any]) -> bool:
        """Save or update user information."""
        try:
            await self._connection.execute("""
                INSERT OR REPLACE INTO users 
                (id, username, first_name, last_name, language_code, is_bot, is_premium, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (
                user_data.get('id'),
                user_data.get('username'),
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('language_code'),
                user_data.get('is_bot', False),
                user_data.get('is_premium', False)
            ))
            
            await self._connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to save user: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by ID."""
        try:
            cursor = await self._connection.execute(
                "SELECT * FROM users WHERE id = ?", (user_id,)
            )
            row = await cursor.fetchone()
            
            if row:
                columns = [description[0] for description in cursor.description]
                return dict(zip(columns, row))
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    async def log_activity(self, user_id: int, action: str, data: str = None) -> bool:
        """Log user activity."""
        try:
            await self._connection.execute("""
                INSERT INTO user_activity (user_id, action, data)
                VALUES (?, ?, ?)
            """, (user_id, action, data))
            
            await self._connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            return False
    
    async def get_user_activity(self, user_id: int, limit: int = 10) -> List[Dict[str, Any]]:
        """Get user activity history."""
        try:
            cursor = await self._connection.execute("""
                SELECT * FROM user_activity 
                WHERE user_id = ? 
                ORDER BY timestamp DESC 
                LIMIT ?
            """, (user_id, limit))
            
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            
            return [dict(zip(columns, row)) for row in rows]
            
        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            return []
    
    async def set_setting(self, key: str, value: str) -> bool:
        """Set a bot setting."""
        try:
            await self._connection.execute("""
                INSERT OR REPLACE INTO settings (key, value, updated_at)
                VALUES (?, ?, CURRENT_TIMESTAMP)
            """, (key, value))
            
            await self._connection.commit()
            return True
            
        except Exception as e:
            logger.error(f"Failed to set setting: {e}")
            return False
    
    async def get_setting(self, key: str, default: str = None) -> Optional[str]:
        """Get a bot setting."""
        try:
            cursor = await self._connection.execute(
                "SELECT value FROM settings WHERE key = ?", (key,)
            )
            row = await cursor.fetchone()
            
            return row[0] if row else default
            
        except Exception as e:
            logger.error(f"Failed to get setting: {e}")
            return default
    
    async def get_user_count(self) -> int:
        """Get total number of users."""
        try:
            cursor = await self._connection.execute("SELECT COUNT(*) FROM users")
            row = await cursor.fetchone()
            return row[0] if row else 0
            
        except Exception as e:
            logger.error(f"Failed to get user count: {e}")
            return 0


# Global database instance
db = Database()