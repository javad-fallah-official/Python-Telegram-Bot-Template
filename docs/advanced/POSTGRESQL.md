# PostgreSQL Module for Telegram Bot Template

This module adds high-performance PostgreSQL support to your Telegram bot using `asyncpg`, the fastest PostgreSQL library for Python.

## Features

### 🚀 **Performance**
- **asyncpg**: The fastest PostgreSQL driver for Python
- **Connection Pooling**: Automatic connection pool management
- **Batch Operations**: Efficient bulk operations
- **Optimized Queries**: PostgreSQL-specific optimizations

### 📊 **Advanced Features**
- **JSONB Support**: Store complex data structures efficiently
- **Full-Text Search**: Built-in search capabilities
- **Analytics**: Built-in metrics and statistics tracking
- **Partitioning Ready**: Designed for large-scale deployments

### 🔄 **Compatibility**
- **Unified Interface**: Same API works with SQLite and PostgreSQL
- **Automatic Detection**: Chooses backend based on DATABASE_URL
- **Migration Ready**: Easy to switch from SQLite to PostgreSQL

## Quick Start

### 1. Install Dependencies
```bash
# Dependencies are automatically added to pyproject.toml
pip install asyncpg
```

### 2. Configure Database URL
```bash
# In your .env file:
DATABASE_URL=postgresql://username:password@localhost:5432/botdb
```

### 3. Use in Your Bot
```python
from core.db_factory import UnifiedDatabase

# Automatically chooses PostgreSQL based on DATABASE_URL
db = UnifiedDatabase()

async def setup():
    await db.connect(pool_size=10, max_pool_size=20)
    
    # Same API works for both SQLite and PostgreSQL
    await db.save_user({
        'id': 123456789,
        'username': 'john_doe',
        'metadata': {'premium': True}  # JSONB in PostgreSQL
    })
```

## Database Modules

### 1. `core/postgres.py`
- **PostgreSQLDatabase**: High-performance PostgreSQL implementation
- **Connection Pooling**: Automatic pool management
- **Advanced Features**: JSONB, analytics, metrics

### 2. `core/db_factory.py`
- **UnifiedDatabase**: Works with both SQLite and PostgreSQL
- **DatabaseFactory**: Automatic backend selection
- **Compatibility Layer**: Unified API

### 3. `examples/postgresql_example.py`
- **Usage Examples**: Complete examples and tutorials
- **Performance Comparison**: SQLite vs PostgreSQL benchmarks
- **Advanced Features**: Analytics, metrics, JSONB queries

## PostgreSQL vs SQLite

| Feature | SQLite | PostgreSQL |
|---------|--------|------------|
| **Performance** | Good for small apps | Excellent for production |
| **Concurrency** | Limited | Excellent |
| **Data Types** | Basic | Rich (JSONB, Arrays, etc.) |
| **Analytics** | Basic | Advanced |
| **Scaling** | Single file | Horizontal scaling |
| **Connection Pooling** | N/A | Built-in |

## Advanced PostgreSQL Features

### 1. **JSONB Storage**
```python
# Store complex data efficiently
await db.save_user({
    'id': 123,
    'metadata': {
        'preferences': {'theme': 'dark', 'lang': 'en'},
        'subscription': {'type': 'premium', 'expires': '2024-12-31'},
        'features': ['analytics', 'export', 'api']
    }
})

# Query JSONB data
users = await db.execute_raw_query("""
    SELECT * FROM users 
    WHERE metadata->>'subscription'->>'type' = 'premium'
""")
```

### 2. **Analytics & Metrics**
```python
# Record metrics
await db.record_metric('daily_active_users', 1500, {
    'date': '2024-01-01',
    'source': 'telegram'
})

# Get analytics
metrics = await db.get_metrics('daily_active_users', limit=30)
active_users = await db.get_active_users_count(days=7)
```

### 3. **Batch Operations**
```python
# Efficient batch operations
user_ids = [123, 456, 789]
users = await db.get_users_batch(user_ids)  # Single query
```

### 4. **Connection Pooling**
```python
# Automatic connection pooling
await db.connect(
    pool_size=10,      # Minimum connections
    max_pool_size=50   # Maximum connections
)
```

## Migration from SQLite

### 1. **Zero Code Changes**
```python
# This code works with both SQLite and PostgreSQL
db = UnifiedDatabase()  # Automatically detects database type
await db.connect()
await db.save_user(user_data)  # Same API
```

### 2. **Update Configuration**
```bash
# Change from:
DATABASE_URL=bot.db

# To:
DATABASE_URL=postgresql://user:pass@localhost:5432/botdb
```

### 3. **Optional: Use PostgreSQL Features**
```python
if db.is_postgresql:
    # Use PostgreSQL-specific features
    await db.record_metric('performance', 95)
    users = await db.get_users_batch([1, 2, 3])
```

## Performance Tips

### 1. **Connection Pooling**
- Use connection pools for better performance
- Adjust pool size based on your load
- Monitor pool usage

### 2. **Batch Operations**
- Use `get_users_batch()` instead of multiple `get_user()` calls
- Batch inserts when possible
- Use transactions for related operations

### 3. **Indexing**
- Indexes are automatically created for common queries
- Add custom indexes for your specific use cases
- Monitor query performance

### 4. **JSONB Optimization**
- Use JSONB for complex data structures
- Create GIN indexes for JSONB queries
- Avoid deep nesting in JSONB

## Production Deployment

### 1. **Database Setup**
```sql
-- Create database
CREATE DATABASE botdb;

-- Create user
CREATE USER botuser WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE botdb TO botuser;
```

### 2. **Connection String**
```bash
DATABASE_URL=postgresql://botuser:secure_password@localhost:5432/botdb
```

### 3. **Environment Variables**
```bash
# Optional: Connection pool settings
DB_POOL_MIN_SIZE=5
DB_POOL_MAX_SIZE=20
```

## Monitoring & Health Checks

```python
# Health check
healthy = await db.health_check()

# Connection pool status (PostgreSQL only)
if db.is_postgresql:
    pool_size = db._db._pool.get_size()
    idle_connections = db._db._pool.get_idle_size()
```

## Error Handling

```python
try:
    await db.connect()
    # Database operations
except asyncpg.PostgresError as e:
    logger.error(f"PostgreSQL error: {e}")
except Exception as e:
    logger.error(f"Database error: {e}")
finally:
    await db.disconnect()
```

## Best Practices

1. **Use Connection Pooling**: Always use pools in production
2. **Handle Errors**: Implement proper error handling
3. **Monitor Performance**: Track query performance and pool usage
4. **Use Transactions**: Group related operations
5. **Optimize Queries**: Use indexes and efficient queries
6. **Regular Backups**: Implement backup strategies
7. **Security**: Use strong passwords and SSL connections

## Examples

See `examples/postgresql_example.py` for complete usage examples including:
- Basic operations
- Advanced PostgreSQL features
- Performance comparisons
- Analytics and metrics
- Error handling

## Support

- **SQLite**: Continues to work as before
- **PostgreSQL**: Full feature support with asyncpg
- **Migration**: Seamless transition between backends
- **Performance**: Optimized for production workloads