"""PostgreSQL database module using asyncpg for maximum performance."""

try:
    import asyncpg
except ImportError:
    asyncpg = None

import logging
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
import json
from .config import Config

logger = logging.getLogger(__name__)


class PostgreSQLDatabase:
    """High-performance async PostgreSQL database wrapper using asyncpg."""
    
    def __init__(self, url: str = None):
        """
        Initialize PostgreSQL database connection.
        
        Args:
            url: PostgreSQL connection URL (e.g., postgresql://user:pass@host:port/db)
        """
        if asyncpg is None:
            raise ImportError("asyncpg is required for PostgreSQL support. Install with: pip install asyncpg")
        
        self.url = url or Config.DATABASE_URL
        self.pool: Optional[asyncpg.Pool] = None
        self.min_pool_size = getattr(Config, 'DB_POOL_MIN_SIZE', 5)
        self.max_pool_size = getattr(Config, 'DB_POOL_MAX_SIZE', 20)
    
    async def connect(self):
        """Connect to PostgreSQL database with connection pooling."""
        try:
            self.pool = await asyncpg.create_pool(
                self.url,
                min_size=self.min_pool_size,
                max_size=self.max_pool_size,
                command_timeout=60,
                server_settings={
                    'jit': 'off'  # Disable JIT for better performance on small queries
                }
            )
            logger.info(f"Connected to PostgreSQL with pool (size: {self.min_pool_size}-{self.max_pool_size})")
            await self.create_tables()
            
        except Exception as e:
            logger.error(f"Failed to connect to PostgreSQL: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from PostgreSQL database."""
        try:
            if self.pool:
                await self.pool.close()
                logger.info("PostgreSQL connection pool closed")
        except Exception as e:
            logger.error(f"Error disconnecting from PostgreSQL: {e}")
    
    async def create_tables(self):
        """Create necessary tables with PostgreSQL-optimized schema."""
        try:
            async with self.pool.acquire() as conn:
                # Users table with PostgreSQL-specific features
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id BIGINT PRIMARY KEY,
                        username VARCHAR(255),
                        first_name VARCHAR(255),
                        last_name VARCHAR(255),
                        language_code VARCHAR(10),
                        is_bot BOOLEAN DEFAULT FALSE,
                        is_premium BOOLEAN DEFAULT FALSE,
                        metadata JSONB DEFAULT '{}',
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Create indexes for better performance
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_username 
                    ON users(username) WHERE username IS NOT NULL
                """)
                
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_users_created_at 
                    ON users(created_at)
                """)
                
                # User activity table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_activity (
                        id BIGSERIAL PRIMARY KEY,
                        user_id BIGINT NOT NULL,
                        action VARCHAR(100) NOT NULL,
                        data JSONB DEFAULT '{}',
                        timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE CASCADE
                    )
                """)
                
                # Indexes for user activity
                await conn.execute("""
                    CREATE INDEX IF NOT EXISTS idx_user_activity_user_id_timestamp 
                    ON user_activity(user_id, timestamp DESC)
                """)
                
                # Settings table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS settings (
                        key VARCHAR(255) PRIMARY KEY,
                        value JSONB NOT NULL,
                        description TEXT,
                        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                # Bot statistics table
                await conn.execute("""
                    CREATE TABLE IF NOT EXISTS bot_stats (
                        id BIGSERIAL PRIMARY KEY,
                        metric_name VARCHAR(100) NOT NULL,
                        metric_value BIGINT NOT NULL,
                        metadata JSONB DEFAULT '{}',
                        recorded_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
                    )
                """)
                
                logger.info("PostgreSQL tables created/verified")
                
        except Exception as e:
            logger.error(f"Failed to create PostgreSQL tables: {e}")
            raise
    
    async def save_user(self, user_id: int, username: str = None, first_name: str = None, 
                       last_name: str = None, language_code: str = None, metadata: Dict = None) -> bool:
        """Save or update user information with UPSERT."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO users 
                    (user_id, username, first_name, last_name, language_code, metadata, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, NOW())
                    ON CONFLICT (user_id) DO UPDATE SET
                        username = EXCLUDED.username,
                        first_name = EXCLUDED.first_name,
                        last_name = EXCLUDED.last_name,
                        language_code = EXCLUDED.language_code,
                        metadata = EXCLUDED.metadata,
                        updated_at = NOW()
                """, 
                    user_id, username, first_name, last_name, language_code,
                    json.dumps(metadata or {})
                )
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to save user: {e}")
            return False
    
    async def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information by ID."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT * FROM users WHERE user_id = $1", user_id
                )
                
                if row:
                    user_dict = dict(row)
                    # Parse JSON metadata
                    if 'metadata' in user_dict and user_dict['metadata']:
                        user_dict['metadata'] = json.loads(user_dict['metadata']) if isinstance(user_dict['metadata'], str) else user_dict['metadata']
                    return user_dict
                
                return None
                
        except Exception as e:
            logger.error(f"Failed to get user: {e}")
            return None
    
    async def get_users_batch(self, user_ids: List[int]) -> List[Dict[str, Any]]:
        """Get multiple users in a single query for better performance."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(
                    "SELECT * FROM users WHERE user_id = ANY($1)", user_ids
                )
                
                users = []
                for row in rows:
                    user_dict = dict(row)
                    if 'metadata' in user_dict and user_dict['metadata']:
                        user_dict['metadata'] = json.loads(user_dict['metadata']) if isinstance(user_dict['metadata'], str) else user_dict['metadata']
                    users.append(user_dict)
                
                return users
                
        except Exception as e:
            logger.error(f"Failed to get users batch: {e}")
            return []
    
    async def log_activity(self, user_id: int, action: str, data: Dict[str, Any] = None) -> bool:
        """Log user activity with structured data."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO user_activity (user_id, action, data)
                    VALUES ($1, $2, $3)
                """, user_id, action, json.dumps(data or {}))
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to log activity: {e}")
            return False
    
    async def get_user_activity(self, user_id: int, limit: int = 10, offset: int = 0) -> List[Dict[str, Any]]:
        """Get user activity history with pagination."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM user_activity 
                    WHERE user_id = $1 
                    ORDER BY timestamp DESC 
                    LIMIT $2 OFFSET $3
                """, user_id, limit, offset)
                
                activities = []
                for row in rows:
                    activity_dict = dict(row)
                    if 'data' in activity_dict and activity_dict['data']:
                        activity_dict['data'] = json.loads(activity_dict['data']) if isinstance(activity_dict['data'], str) else activity_dict['data']
                    activities.append(activity_dict)
                
                return activities
                
        except Exception as e:
            logger.error(f"Failed to get user activity: {e}")
            return []
    
    async def set_setting(self, key: str, value: Union[str, Dict, List, int, float, bool], description: str = None) -> bool:
        """Set a bot setting with support for complex data types."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO settings (key, value, description, updated_at)
                    VALUES ($1, $2, $3, NOW())
                    ON CONFLICT (key) DO UPDATE SET
                        value = EXCLUDED.value,
                        description = EXCLUDED.description,
                        updated_at = NOW()
                """, key, json.dumps(value), description)
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to set setting: {e}")
            return False
    
    async def get_setting(self, key: str, default: Any = None) -> Any:
        """Get a bot setting with automatic JSON parsing."""
        try:
            async with self.pool.acquire() as conn:
                row = await conn.fetchrow(
                    "SELECT value FROM settings WHERE key = $1", key
                )
                
                if row:
                    return json.loads(row['value']) if isinstance(row['value'], str) else row['value']
                
                return default
                
        except Exception as e:
            logger.error(f"Failed to get setting: {e}")
            return default
    
    async def get_user_count(self) -> int:
        """Get total number of users."""
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval("SELECT COUNT(*) FROM users")
                return count or 0
                
        except Exception as e:
            logger.error(f"Failed to get user count: {e}")
            return 0
    
    async def get_active_users_count(self, days: int = 7) -> int:
        """Get count of users active in the last N days."""
        try:
            async with self.pool.acquire() as conn:
                count = await conn.fetchval("""
                    SELECT COUNT(DISTINCT user_id) 
                    FROM user_activity 
                    WHERE timestamp >= NOW() - INTERVAL '%s days'
                """, days)
                return count or 0
                
        except Exception as e:
            logger.error(f"Failed to get active users count: {e}")
            return 0
    
    async def get_user_activity_stats(self, user_id: int) -> Dict[str, Any]:
        """Get user activity statistics."""
        try:
            async with self.pool.acquire() as conn:
                stats = await conn.fetchrow("""
                    SELECT 
                        COUNT(*) as total_activities,
                        COUNT(DISTINCT action) as unique_actions,
                        MIN(timestamp) as first_activity,
                        MAX(timestamp) as last_activity
                    FROM user_activity 
                    WHERE user_id = $1
                """, user_id)
                
                return dict(stats) if stats else {}
                
        except Exception as e:
            logger.error(f"Failed to get user activity stats: {e}")
            return {}
    
    async def record_metric(self, metric_name: str, value: int, metadata: Dict[str, Any] = None) -> bool:
        """Record a bot metric for analytics."""
        try:
            async with self.pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO bot_stats (metric_name, metric_value, metadata)
                    VALUES ($1, $2, $3)
                """, metric_name, value, json.dumps(metadata or {}))
                
                return True
                
        except Exception as e:
            logger.error(f"Failed to record metric: {e}")
            return False
    
    async def get_metrics(self, metric_name: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical metrics data."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch("""
                    SELECT * FROM bot_stats 
                    WHERE metric_name = $1 
                    ORDER BY recorded_at DESC 
                    LIMIT $2
                """, metric_name, limit)
                
                metrics = []
                for row in rows:
                    metric_dict = dict(row)
                    if 'metadata' in metric_dict and metric_dict['metadata']:
                        metric_dict['metadata'] = json.loads(metric_dict['metadata']) if isinstance(metric_dict['metadata'], str) else metric_dict['metadata']
                    metrics.append(metric_dict)
                
                return metrics
                
        except Exception as e:
            logger.error(f"Failed to get metrics: {e}")
            return []
    
    async def execute_raw_query(self, query: str, *args) -> List[Dict[str, Any]]:
        """Execute a raw SQL query (use with caution)."""
        try:
            async with self.pool.acquire() as conn:
                rows = await conn.fetch(query, *args)
                return [dict(row) for row in rows]
                
        except Exception as e:
            logger.error(f"Failed to execute raw query: {e}")
            return []
    
    async def health_check(self) -> bool:
        """Check if database connection is healthy."""
        try:
            async with self.pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
                return True
                
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False


# Global PostgreSQL database instance
postgres_db = PostgreSQLDatabase()