# 🗄️ Database API Reference

This document provides a comprehensive API reference for the database layer, including both SQLite and PostgreSQL implementations.

## Table of Contents

- [Database Interface](#database-interface)
- [SQLite Implementation](#sqlite-implementation)
- [PostgreSQL Implementation](#postgresql-implementation)
- [Database Factory](#database-factory)
- [User Operations](#user-operations)
- [Activity Logging](#activity-logging)
- [Analytics & Metrics](#analytics--metrics)
- [Connection Management](#connection-management)
- [Error Handling](#error-handling)

## Database Interface

### Base Database Class

```python
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any

class DatabaseInterface(ABC):
    """Abstract base class for database implementations."""
    
    @abstractmethod
    async def connect(self) -> None:
        """Establish database connection."""
        pass
    
    @abstractmethod
    async def close(self) -> None:
        """Close database connection."""
        pass
    
    @abstractmethod
    async def is_connected(self) -> bool:
        """Check if database is connected."""
        pass
    
    @abstractmethod
    async def save_user(self, user_data: Dict[str, Any]) -> None:
        """Save user data to database."""
        pass
    
    @abstractmethod
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve user data by ID."""
        pass
```

### Database Configuration

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    """Database configuration settings."""
    
    database_type: str  # 'sqlite' or 'postgresql'
    database_url: str
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    echo: bool = False
    
    @classmethod
    def from_env(cls) -> 'DatabaseConfig':
        """Create config from environment variables."""
        import os
        
        return cls(
            database_type=os.getenv('DATABASE_TYPE', 'sqlite'),
            database_url=os.getenv('DATABASE_URL', 'bot.db'),
            pool_size=int(os.getenv('DB_POOL_SIZE', '10')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '20')),
            pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30')),
            pool_recycle=int(os.getenv('DB_POOL_RECYCLE', '3600')),
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true'
        )
```

## SQLite Implementation

### SQLite Database Class

```python
import aiosqlite
from typing import Dict, List, Optional, Any
from datetime import datetime

class SQLiteDatabase(DatabaseInterface):
    """SQLite database implementation."""
    
    def __init__(self, database_url: str = "bot.db"):
        """
        Initialize SQLite database.
        
        Args:
            database_url: Path to SQLite database file
        """
        self.database_url = database_url
        self.connection: Optional[aiosqlite.Connection] = None
    
    async def connect(self) -> None:
        """Establish connection to SQLite database."""
        self.connection = await aiosqlite.connect(self.database_url)
        await self._create_tables()
    
    async def close(self) -> None:
        """Close SQLite database connection."""
        if self.connection:
            await self.connection.close()
            self.connection = None
    
    async def is_connected(self) -> bool:
        """Check if database connection is active."""
        if not self.connection:
            return False
        
        try:
            await self.connection.execute("SELECT 1")
            return True
        except Exception:
            return False
    
    async def _create_tables(self) -> None:
        """Create database tables if they don't exist."""
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                last_name TEXT,
                language_code TEXT,
                is_bot BOOLEAN DEFAULT FALSE,
                is_premium BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_activity TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                command_count INTEGER DEFAULT 0,
                message_count INTEGER DEFAULT 0
            )
        """)
        
        await self.connection.execute("""
            CREATE TABLE IF NOT EXISTS user_activities (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                activity_type TEXT NOT NULL,
                activity_data TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_activities_user_id 
            ON user_activities(user_id)
        """)
        
        await self.connection.execute("""
            CREATE INDEX IF NOT EXISTS idx_user_activities_timestamp 
            ON user_activities(timestamp)
        """)
        
        await self.connection.commit()
```

### SQLite User Operations

```python
async def save_user(self, user_data: Dict[str, Any]) -> None:
    """
    Save or update user data in SQLite.
    
    Args:
        user_data: Dictionary containing user information
    """
    query = """
        INSERT OR REPLACE INTO users 
        (id, username, first_name, last_name, language_code, 
         is_bot, is_premium, updated_at, last_activity)
        VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
    """
    
    await self.connection.execute(query, (
        user_data['id'],
        user_data.get('username'),
        user_data.get('first_name'),
        user_data.get('last_name'),
        user_data.get('language_code'),
        user_data.get('is_bot', False),
        user_data.get('is_premium', False)
    ))
    await self.connection.commit()

async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve user data from SQLite.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        User data dictionary or None if not found
    """
    query = "SELECT * FROM users WHERE id = ?"
    
    async with self.connection.execute(query, (user_id,)) as cursor:
        row = await cursor.fetchone()
        
        if row:
            columns = [description[0] for description in cursor.description]
            return dict(zip(columns, row))
        
        return None

async def user_exists(self, user_id: int) -> bool:
    """
    Check if user exists in database.
    
    Args:
        user_id: Telegram user ID
        
    Returns:
        True if user exists, False otherwise
    """
    query = "SELECT 1 FROM users WHERE id = ? LIMIT 1"
    
    async with self.connection.execute(query, (user_id,)) as cursor:
        row = await cursor.fetchone()
        return row is not None

async def update_user_activity(self, user_id: int) -> None:
    """
    Update user's last activity timestamp.
    
    Args:
        user_id: Telegram user ID
    """
    query = """
        UPDATE users 
        SET last_activity = CURRENT_TIMESTAMP 
        WHERE id = ?
    """
    
    await self.connection.execute(query, (user_id,))
    await self.connection.commit()

async def increment_user_counter(self, user_id: int, counter_type: str) -> None:
    """
    Increment user counter (commands or messages).
    
    Args:
        user_id: Telegram user ID
        counter_type: 'command' or 'message'
    """
    if counter_type not in ['command', 'message']:
        raise ValueError("Counter type must be 'command' or 'message'")
    
    column = f"{counter_type}_count"
    query = f"UPDATE users SET {column} = {column} + 1 WHERE id = ?"
    
    await self.connection.execute(query, (user_id,))
    await self.connection.commit()
```

## PostgreSQL Implementation

### PostgreSQL Database Class

```python
import asyncpg
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

class PostgreSQLDatabase(DatabaseInterface):
    """PostgreSQL database implementation with advanced features."""
    
    def __init__(self, database_url: str):
        """
        Initialize PostgreSQL database.
        
        Args:
            database_url: PostgreSQL connection URL
        """
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None
    
    async def connect(self) -> None:
        """Establish connection pool to PostgreSQL."""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=5,
            max_size=20,
            command_timeout=60
        )
        await self._create_tables()
    
    async def close(self) -> None:
        """Close PostgreSQL connection pool."""
        if self.pool:
            await self.pool.close()
            self.pool = None
    
    async def is_connected(self) -> bool:
        """Check if database pool is active."""
        if not self.pool:
            return False
        
        try:
            async with self.pool.acquire() as connection:
                await connection.fetchval("SELECT 1")
            return True
        except Exception:
            return False
    
    async def _create_tables(self) -> None:
        """Create PostgreSQL tables with advanced features."""
        async with self.pool.acquire() as connection:
            # Enable UUID extension
            await connection.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
            
            # Users table with JSONB metadata
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id BIGINT PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    language_code TEXT,
                    is_bot BOOLEAN DEFAULT FALSE,
                    is_premium BOOLEAN DEFAULT FALSE,
                    metadata JSONB DEFAULT '{}',
                    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    last_activity TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    command_count INTEGER DEFAULT 0,
                    message_count INTEGER DEFAULT 0
                )
            """)
            
            # User activities with JSONB data
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS user_activities (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    user_id BIGINT NOT NULL,
                    activity_type TEXT NOT NULL,
                    activity_data JSONB DEFAULT '{}',
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Metrics table for analytics
            await connection.execute("""
                CREATE TABLE IF NOT EXISTS metrics (
                    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
                    metric_name TEXT NOT NULL,
                    metric_value NUMERIC,
                    metric_data JSONB DEFAULT '{}',
                    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                )
            """)
            
            # Create indexes
            await connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_username ON users(username)
            """)
            await connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_users_last_activity ON users(last_activity)
            """)
            await connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_activities_user_id ON user_activities(user_id)
            """)
            await connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_activities_timestamp ON user_activities(timestamp)
            """)
            await connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_user_activities_type ON user_activities(activity_type)
            """)
            await connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_name ON metrics(metric_name)
            """)
            await connection.execute("""
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)
            """)
```

### PostgreSQL Advanced Features

```python
async def save_user_with_metadata(
    self, 
    user_data: Dict[str, Any], 
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Save user with JSONB metadata support.
    
    Args:
        user_data: Basic user information
        metadata: Additional metadata to store as JSONB
    """
    query = """
        INSERT INTO users 
        (id, username, first_name, last_name, language_code, 
         is_bot, is_premium, metadata, updated_at, last_activity)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, NOW(), NOW())
        ON CONFLICT (id) DO UPDATE SET
            username = EXCLUDED.username,
            first_name = EXCLUDED.first_name,
            last_name = EXCLUDED.last_name,
            language_code = EXCLUDED.language_code,
            is_bot = EXCLUDED.is_bot,
            is_premium = EXCLUDED.is_premium,
            metadata = EXCLUDED.metadata,
            updated_at = NOW(),
            last_activity = NOW()
    """
    
    async with self.pool.acquire() as connection:
        await connection.execute(query,
            user_data['id'],
            user_data.get('username'),
            user_data.get('first_name'),
            user_data.get('last_name'),
            user_data.get('language_code'),
            user_data.get('is_bot', False),
            user_data.get('is_premium', False),
            json.dumps(metadata or {})
        )

async def update_user_metadata(
    self, 
    user_id: int, 
    metadata_updates: Dict[str, Any]
) -> None:
    """
    Update user metadata using JSONB operations.
    
    Args:
        user_id: Telegram user ID
        metadata_updates: Metadata fields to update
    """
    query = """
        UPDATE users 
        SET metadata = metadata || $2::jsonb,
            updated_at = NOW()
        WHERE id = $1
    """
    
    async with self.pool.acquire() as connection:
        await connection.execute(query, user_id, json.dumps(metadata_updates))

async def search_users_by_metadata(
    self, 
    search_criteria: Dict[str, Any]
) -> List[Dict[str, Any]]:
    """
    Search users by metadata criteria.
    
    Args:
        search_criteria: JSONB search criteria
        
    Returns:
        List of matching users
    """
    query = """
        SELECT id, username, first_name, last_name, metadata
        FROM users 
        WHERE metadata @> $1::jsonb
    """
    
    async with self.pool.acquire() as connection:
        rows = await connection.fetch(query, json.dumps(search_criteria))
        return [dict(row) for row in rows]

async def record_metric(
    self, 
    metric_name: str, 
    metric_value: Union[int, float], 
    metric_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Record a metric for analytics.
    
    Args:
        metric_name: Name of the metric
        metric_value: Numeric value
        metric_data: Additional metric data
    """
    query = """
        INSERT INTO metrics (metric_name, metric_value, metric_data)
        VALUES ($1, $2, $3)
    """
    
    async with self.pool.acquire() as connection:
        await connection.execute(query,
            metric_name,
            metric_value,
            json.dumps(metric_data or {})
        )

async def get_metrics(
    self, 
    metric_name: str, 
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    Retrieve metrics by name.
    
    Args:
        metric_name: Name of the metric
        limit: Maximum number of records
        
    Returns:
        List of metric records
    """
    query = """
        SELECT metric_name, metric_value, metric_data, timestamp
        FROM metrics 
        WHERE metric_name = $1
        ORDER BY timestamp DESC
        LIMIT $2
    """
    
    async with self.pool.acquire() as connection:
        rows = await connection.fetch(query, metric_name, limit)
        return [dict(row) for row in rows]
```

## Database Factory

### Factory Implementation

```python
from core.config import Config
from typing import Union

class DatabaseFactory:
    """Factory for creating database instances."""
    
    @staticmethod
    def create_database() -> DatabaseInterface:
        """
        Create database instance based on configuration.
        
        Returns:
            Database instance (SQLite or PostgreSQL)
        """
        config = Config()
        
        if config.DATABASE_TYPE.lower() == 'postgresql':
            return PostgreSQLDatabase(config.DATABASE_URL)
        else:
            return SQLiteDatabase(config.DATABASE_URL)
    
    @staticmethod
    async def create_and_connect() -> DatabaseInterface:
        """
        Create and connect database instance.
        
        Returns:
            Connected database instance
        """
        db = DatabaseFactory.create_database()
        await db.connect()
        return db
    
    @staticmethod
    def get_database_type() -> str:
        """
        Get configured database type.
        
        Returns:
            Database type ('sqlite' or 'postgresql')
        """
        config = Config()
        return config.DATABASE_TYPE.lower()
```

## User Operations

### Batch Operations

```python
async def save_users_batch(self, users_data: List[Dict[str, Any]]) -> None:
    """
    Save multiple users in a single transaction.
    
    Args:
        users_data: List of user data dictionaries
    """
    if isinstance(self, PostgreSQLDatabase):
        # PostgreSQL batch insert
        query = """
            INSERT INTO users 
            (id, username, first_name, last_name, language_code, is_bot, is_premium)
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (id) DO UPDATE SET
                username = EXCLUDED.username,
                first_name = EXCLUDED.first_name,
                last_name = EXCLUDED.last_name,
                updated_at = NOW()
        """
        
        async with self.pool.acquire() as connection:
            await connection.executemany(query, [
                (
                    user['id'],
                    user.get('username'),
                    user.get('first_name'),
                    user.get('last_name'),
                    user.get('language_code'),
                    user.get('is_bot', False),
                    user.get('is_premium', False)
                )
                for user in users_data
            ])
    
    else:
        # SQLite batch insert
        query = """
            INSERT OR REPLACE INTO users 
            (id, username, first_name, last_name, language_code, is_bot, is_premium)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """
        
        await self.connection.executemany(query, [
            (
                user['id'],
                user.get('username'),
                user.get('first_name'),
                user.get('last_name'),
                user.get('language_code'),
                user.get('is_bot', False),
                user.get('is_premium', False)
            )
            for user in users_data
        ])
        await self.connection.commit()

async def get_users_by_criteria(
    self, 
    criteria: Dict[str, Any],
    limit: int = 100,
    offset: int = 0
) -> List[Dict[str, Any]]:
    """
    Get users matching specific criteria.
    
    Args:
        criteria: Search criteria
        limit: Maximum number of results
        offset: Number of results to skip
        
    Returns:
        List of matching users
    """
    where_clauses = []
    params = []
    
    for key, value in criteria.items():
        if key in ['id', 'username', 'first_name', 'last_name', 'is_bot', 'is_premium']:
            where_clauses.append(f"{key} = ?")
            params.append(value)
    
    where_clause = " AND ".join(where_clauses) if where_clauses else "1=1"
    
    if isinstance(self, PostgreSQLDatabase):
        # PostgreSQL version
        query = f"""
            SELECT * FROM users 
            WHERE {where_clause.replace('?', '${}').format(*range(1, len(params) + 1))}
            ORDER BY created_at DESC
            LIMIT ${len(params) + 1} OFFSET ${len(params) + 2}
        """
        params.extend([limit, offset])
        
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *params)
            return [dict(row) for row in rows]
    
    else:
        # SQLite version
        query = f"""
            SELECT * FROM users 
            WHERE {where_clause}
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """
        params.extend([limit, offset])
        
        async with self.connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
```

## Activity Logging

### Activity Operations

```python
async def log_activity(
    self, 
    user_id: int, 
    activity_type: str, 
    activity_data: Optional[Dict[str, Any]] = None
) -> None:
    """
    Log user activity.
    
    Args:
        user_id: Telegram user ID
        activity_type: Type of activity
        activity_data: Additional activity data
    """
    if isinstance(self, PostgreSQLDatabase):
        query = """
            INSERT INTO user_activities (user_id, activity_type, activity_data)
            VALUES ($1, $2, $3)
        """
        
        async with self.pool.acquire() as connection:
            await connection.execute(query,
                user_id,
                activity_type,
                json.dumps(activity_data or {})
            )
    
    else:
        query = """
            INSERT INTO user_activities (user_id, activity_type, activity_data)
            VALUES (?, ?, ?)
        """
        
        await self.connection.execute(query,
            user_id,
            activity_type,
            json.dumps(activity_data or {})
        )
        await self.connection.commit()

async def get_user_activities(
    self, 
    user_id: int, 
    activity_type: Optional[str] = None,
    limit: int = 50
) -> List[Dict[str, Any]]:
    """
    Get user activities.
    
    Args:
        user_id: Telegram user ID
        activity_type: Filter by activity type
        limit: Maximum number of activities
        
    Returns:
        List of user activities
    """
    if activity_type:
        where_clause = "user_id = ? AND activity_type = ?"
        params = [user_id, activity_type]
    else:
        where_clause = "user_id = ?"
        params = [user_id]
    
    if isinstance(self, PostgreSQLDatabase):
        query = f"""
            SELECT activity_type, activity_data, timestamp
            FROM user_activities 
            WHERE {where_clause.replace('?', '${}').format(*range(1, len(params) + 1))}
            ORDER BY timestamp DESC
            LIMIT ${len(params) + 1}
        """
        params.append(limit)
        
        async with self.pool.acquire() as connection:
            rows = await connection.fetch(query, *params)
            return [dict(row) for row in rows]
    
    else:
        query = f"""
            SELECT activity_type, activity_data, timestamp
            FROM user_activities 
            WHERE {where_clause}
            ORDER BY timestamp DESC
            LIMIT ?
        """
        params.append(limit)
        
        async with self.connection.execute(query, params) as cursor:
            rows = await cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            return [dict(zip(columns, row)) for row in rows]
```

## Analytics & Metrics

### Analytics Queries

```python
async def get_user_statistics(self) -> Dict[str, Any]:
    """
    Get comprehensive user statistics.
    
    Returns:
        Dictionary containing various user statistics
    """
    if isinstance(self, PostgreSQLDatabase):
        async with self.pool.acquire() as connection:
            # Total users
            total_users = await connection.fetchval("SELECT COUNT(*) FROM users")
            
            # Active users (last 24 hours)
            active_24h = await connection.fetchval("""
                SELECT COUNT(*) FROM users 
                WHERE last_activity > NOW() - INTERVAL '24 hours'
            """)
            
            # Active users (last 7 days)
            active_7d = await connection.fetchval("""
                SELECT COUNT(*) FROM users 
                WHERE last_activity > NOW() - INTERVAL '7 days'
            """)
            
            # Premium users
            premium_users = await connection.fetchval("""
                SELECT COUNT(*) FROM users WHERE is_premium = true
            """)
            
            # Top activity types
            top_activities = await connection.fetch("""
                SELECT activity_type, COUNT(*) as count
                FROM user_activities 
                WHERE timestamp > NOW() - INTERVAL '7 days'
                GROUP BY activity_type
                ORDER BY count DESC
                LIMIT 10
            """)
    
    else:
        # Total users
        async with self.connection.execute("SELECT COUNT(*) FROM users") as cursor:
            total_users = (await cursor.fetchone())[0]
        
        # Active users (last 24 hours)
        async with self.connection.execute("""
            SELECT COUNT(*) FROM users 
            WHERE last_activity > datetime('now', '-24 hours')
        """) as cursor:
            active_24h = (await cursor.fetchone())[0]
        
        # Active users (last 7 days)
        async with self.connection.execute("""
            SELECT COUNT(*) FROM users 
            WHERE last_activity > datetime('now', '-7 days')
        """) as cursor:
            active_7d = (await cursor.fetchone())[0]
        
        # Premium users
        async with self.connection.execute("""
            SELECT COUNT(*) FROM users WHERE is_premium = 1
        """) as cursor:
            premium_users = (await cursor.fetchone())[0]
        
        # Top activity types
        async with self.connection.execute("""
            SELECT activity_type, COUNT(*) as count
            FROM user_activities 
            WHERE timestamp > datetime('now', '-7 days')
            GROUP BY activity_type
            ORDER BY count DESC
            LIMIT 10
        """) as cursor:
            top_activities = await cursor.fetchall()
    
    return {
        'total_users': total_users,
        'active_users_24h': active_24h,
        'active_users_7d': active_7d,
        'premium_users': premium_users,
        'top_activities': [dict(row) for row in top_activities] if isinstance(self, PostgreSQLDatabase) else [{'activity_type': row[0], 'count': row[1]} for row in top_activities]
    }
```

## Connection Management

### Connection Pool Management

```python
class DatabaseManager:
    """Database connection manager with health checks."""
    
    def __init__(self, database: DatabaseInterface):
        self.database = database
        self._health_check_interval = 30  # seconds
        self._last_health_check = 0
    
    async def ensure_connection(self) -> None:
        """Ensure database connection is healthy."""
        import time
        
        current_time = time.time()
        
        if current_time - self._last_health_check > self._health_check_interval:
            if not await self.database.is_connected():
                await self.database.connect()
            
            self._last_health_check = current_time
    
    async def execute_with_retry(
        self, 
        operation: callable, 
        max_retries: int = 3
    ) -> Any:
        """
        Execute database operation with retry logic.
        
        Args:
            operation: Database operation to execute
            max_retries: Maximum number of retry attempts
            
        Returns:
            Operation result
        """
        for attempt in range(max_retries):
            try:
                await self.ensure_connection()
                return await operation()
            
            except Exception as e:
                if attempt == max_retries - 1:
                    raise
                
                # Wait before retry
                await asyncio.sleep(2 ** attempt)
                
                # Try to reconnect
                try:
                    await self.database.close()
                    await self.database.connect()
                except Exception:
                    pass
```

## Error Handling

### Database Exceptions

```python
class DatabaseError(Exception):
    """Base database exception."""
    pass

class ConnectionError(DatabaseError):
    """Database connection error."""
    pass

class QueryError(DatabaseError):
    """Database query error."""
    pass

class TransactionError(DatabaseError):
    """Database transaction error."""
    pass

# Error handling decorator
def handle_database_errors(func):
    """Decorator to handle database errors."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        
        except asyncpg.PostgresError as e:
            logger.error(f"PostgreSQL error in {func.__name__}: {e}")
            raise QueryError(f"Database query failed: {e}")
        
        except aiosqlite.Error as e:
            logger.error(f"SQLite error in {func.__name__}: {e}")
            raise QueryError(f"Database query failed: {e}")
        
        except Exception as e:
            logger.error(f"Unexpected error in {func.__name__}: {e}")
            raise DatabaseError(f"Database operation failed: {e}")
    
    return wrapper
```

## Usage Examples

### Basic Usage

```python
# Create database instance
db = DatabaseFactory.create_database()
await db.connect()

# Save user
user_data = {
    'id': 123456789,
    'username': 'john_doe',
    'first_name': 'John',
    'last_name': 'Doe'
}
await db.save_user(user_data)

# Get user
user = await db.get_user(123456789)
print(f"User: {user['first_name']} {user['last_name']}")

# Log activity
await db.log_activity(123456789, 'command_used', {'command': '/start'})

# Close connection
await db.close()
```

### Advanced PostgreSQL Usage

```python
# PostgreSQL with metadata
db = PostgreSQLDatabase(database_url)
await db.connect()

# Save user with metadata
await db.save_user_with_metadata(
    user_data,
    metadata={'preferences': {'theme': 'dark', 'language': 'en'}}
)

# Update metadata
await db.update_user_metadata(123456789, {'last_command': '/help'})

# Search by metadata
premium_users = await db.search_users_by_metadata({'preferences': {'premium': True}})

# Record metrics
await db.record_metric('command_usage', 1, {'command': '/start'})

# Get analytics
stats = await db.get_user_statistics()
print(f"Total users: {stats['total_users']}")
```

---

*For more examples and implementation details, see the [database modules](../../core/) in the source code.*