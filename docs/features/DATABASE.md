# 🗄️ Database Guide

The Python Telegram Bot Template supports both SQLite and PostgreSQL databases with a unified interface and easy switching capabilities.

## Overview

### Supported Databases
- **SQLite** - Lightweight, file-based database (default)
- **PostgreSQL** - Production-ready, feature-rich database

### Key Features
- **Unified Interface** - Same API works with both databases
- **Automatic Detection** - Chooses database based on configuration
- **Easy Switching** - Change databases without code changes
- **Connection Pooling** - Automatic connection management (PostgreSQL)
- **Async Support** - Fully asynchronous operations

## Quick Start

### Basic Usage
```python
from core.db_factory import DatabaseFactory

# Create database instance (automatically detects type)
db = DatabaseFactory.create_database()
await db.connect()

# Use unified interface
await db.save_user({
    'id': 123456789,
    'username': 'john_doe',
    'first_name': 'John'
})

user = await db.get_user(123456789)
```

### Configuration
```env
# Auto-detection (default)
DATABASE_TYPE=auto
DATABASE_URL=bot.db  # Uses SQLite

# Force specific database
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@localhost:5432/botdb

# Override detection
DATABASE_TYPE=sqlite
DATABASE_URL=postgresql://ignored  # Uses SQLite anyway
```

## Database Types

### SQLite (Default)

**Best for:**
- Development and testing
- Small to medium bots
- Simple deployment
- Single-server applications

**Configuration:**
```env
DATABASE_TYPE=sqlite
DATABASE_URL=bot.db
```

**Features:**
- File-based storage
- No server setup required
- ACID compliance
- Good performance for small datasets

### PostgreSQL

**Best for:**
- Production environments
- High-traffic bots
- Advanced analytics
- Multi-server deployments

**Configuration:**
```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

**Features:**
- Connection pooling
- JSONB support for complex data
- Advanced analytics
- Horizontal scaling
- Full-text search

## Database Operations

### User Management

```python
# Save user
await db.save_user({
    'id': 123456789,
    'username': 'john_doe',
    'first_name': 'John',
    'last_name': 'Doe',
    'language_code': 'en'
})

# Get user
user = await db.get_user(123456789)

# Update user
await db.update_user(123456789, {
    'username': 'new_username',
    'last_seen': datetime.now()
})

# Check if user exists
exists = await db.user_exists(123456789)
```

### Activity Logging

```python
# Log user activity
await db.log_activity(
    user_id=123456789,
    activity_type='command_used',
    details='/start'
)

# Get user activities
activities = await db.get_user_activities(123456789, limit=10)

# Get activity statistics
stats = await db.get_activity_stats(days=7)
```

### Batch Operations

```python
# Get multiple users (PostgreSQL optimized)
user_ids = [123, 456, 789]
users = await db.get_users_batch(user_ids)

# Bulk save users
users_data = [
    {'id': 123, 'username': 'user1'},
    {'id': 456, 'username': 'user2'}
]
await db.save_users_batch(users_data)
```

## PostgreSQL Advanced Features

### JSONB Storage

```python
# Store complex data in PostgreSQL
await db.save_user({
    'id': 123456789,
    'username': 'john_doe',
    'metadata': {
        'preferences': {
            'theme': 'dark',
            'language': 'en',
            'notifications': True
        },
        'subscription': {
            'type': 'premium',
            'expires': '2024-12-31'
        },
        'features': ['analytics', 'export', 'api']
    }
})

# Query JSONB data
premium_users = await db.execute_raw_query("""
    SELECT * FROM users 
    WHERE metadata->>'subscription'->>'type' = 'premium'
""")
```

### Analytics and Metrics

```python
# Record custom metrics (PostgreSQL only)
await db.record_metric('daily_active_users', 1500, {
    'date': '2024-01-01',
    'source': 'telegram'
})

# Get metrics
metrics = await db.get_metrics('daily_active_users', limit=30)

# Get active users count
active_count = await db.get_active_users_count(days=7)

# Get user growth statistics
growth = await db.get_user_growth_stats(days=30)
```

### Connection Pooling

```python
# Configure connection pool (PostgreSQL)
await db.connect(
    pool_size=10,        # Minimum connections
    max_pool_size=50,    # Maximum connections
    pool_timeout=30      # Connection timeout
)

# Check pool status
pool_info = await db.get_pool_info()
print(f"Active connections: {pool_info['active']}")
print(f"Available connections: {pool_info['available']}")
```

## Database Factory

### Automatic Detection

```python
from core.db_factory import DatabaseFactory

# Automatically chooses database based on configuration
db = DatabaseFactory.create_database()

# Check database type
if db.is_postgresql:
    print("Using PostgreSQL")
    # Use PostgreSQL-specific features
    await db.record_metric('performance', 95)
else:
    print("Using SQLite")
    # Standard operations only
```

### Manual Creation

```python
from core.database import Database
from core.postgres import PostgreSQLDatabase

# Force SQLite
sqlite_db = Database()

# Force PostgreSQL
postgres_db = PostgreSQLDatabase()
```

### Unified Interface

```python
from core.db_factory import UnifiedDatabase

# Works with both SQLite and PostgreSQL
db = UnifiedDatabase()
await db.connect()

# Same methods work regardless of backend
await db.save_user(user_data)
user = await db.get_user(user_id)
```

## Migration Between Databases

### From SQLite to PostgreSQL

1. **Export SQLite data:**
```bash
uv run python scripts/export_sqlite.py --output users.json
```

2. **Update configuration:**
```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@localhost:5432/botdb
```

3. **Import data to PostgreSQL:**
```bash
uv run python scripts/import_postgresql.py --input users.json
```

### From PostgreSQL to SQLite

1. **Export PostgreSQL data:**
```bash
uv run python scripts/export_postgresql.py --output users.json
```

2. **Update configuration:**
```env
DATABASE_TYPE=sqlite
DATABASE_URL=bot.db
```

3. **Import data to SQLite:**
```bash
uv run python scripts/import_sqlite.py --input users.json
```

## Performance Optimization

### SQLite Optimization

```python
# Enable WAL mode for better concurrency
await db.execute_raw_query("PRAGMA journal_mode=WAL")

# Optimize for performance
await db.execute_raw_query("PRAGMA synchronous=NORMAL")
await db.execute_raw_query("PRAGMA cache_size=10000")
```

### PostgreSQL Optimization

```python
# Use connection pooling
await db.connect(pool_size=20, max_pool_size=100)

# Use batch operations
users = await db.get_users_batch(user_ids)

# Use prepared statements for repeated queries
await db.prepare_statement("get_user_by_username", 
    "SELECT * FROM users WHERE username = $1")
```

## Monitoring and Maintenance

### Database Health Checks

```python
# Check database connection
is_connected = await db.is_connected()

# Get database statistics
stats = await db.get_database_stats()
print(f"Total users: {stats['user_count']}")
print(f"Database size: {stats['size_mb']} MB")

# Check table integrity
integrity = await db.check_integrity()
```

### Backup and Recovery

```bash
# SQLite backup
cp bot.db bot_backup_$(date +%Y%m%d).db

# PostgreSQL backup
pg_dump botdb > backup_$(date +%Y%m%d).sql

# Restore PostgreSQL
psql botdb < backup_20240101.sql
```

## Testing

### Database Testing

```python
import pytest
from core.db_factory import DatabaseFactory

@pytest.fixture
async def test_db():
    """Create test database instance."""
    db = DatabaseFactory.create_database()
    await db.connect()
    yield db
    await db.close()

async def test_user_operations(test_db):
    """Test user CRUD operations."""
    # Test save user
    await test_db.save_user({
        'id': 123,
        'username': 'test_user'
    })
    
    # Test get user
    user = await test_db.get_user(123)
    assert user['username'] == 'test_user'
```

### Running Database Tests

```bash
# Run all database tests
uv run pytest tests/test_database.py

# Run PostgreSQL-specific tests
uv run pytest tests/test_postgres.py

# Run with database switching
uv run python examples/database_switching_demo.py
```

## Troubleshooting

### Common Issues

#### 1. Connection Failed
```bash
# Check database URL format
# SQLite: bot.db or /path/to/file.db
# PostgreSQL: postgresql://user:pass@host:port/db
```

#### 2. Permission Denied
```bash
# SQLite: Check file permissions
chmod 644 bot.db

# PostgreSQL: Check user permissions
GRANT ALL PRIVILEGES ON DATABASE botdb TO botuser;
```

#### 3. Database Locked (SQLite)
```bash
# Check for other processes using the database
lsof bot.db

# Enable WAL mode for better concurrency
```

#### 4. Connection Pool Exhausted (PostgreSQL)
```python
# Increase pool size
await db.connect(pool_size=20, max_pool_size=100)

# Check for connection leaks
pool_info = await db.get_pool_info()
```

### Getting Help

For database-related issues:

1. Check the [Configuration Guide](../setup/CONFIGURATION.md)
2. Review [PostgreSQL Setup](../advanced/POSTGRESQL.md)
3. Run the database switching demo: `uv run python examples/database_switching_demo.py`
4. Check the test suite: `uv run pytest tests/test_database.py`

## Examples

See the [examples/](../../examples/) directory for:
- `database_switching_demo.py` - Database switching demonstration
- `postgresql_example.py` - PostgreSQL-specific features
- `database_migration.py` - Migration between databases

---

*Need help with database setup? Check the [PostgreSQL Setup Guide](../advanced/POSTGRESQL.md) or [Configuration Guide](../setup/CONFIGURATION.md).*