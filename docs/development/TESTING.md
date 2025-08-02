# 🧪 Testing Guide

This guide covers testing strategies, tools, and best practices for the Python Telegram Bot Template.

## Overview

### Testing Framework
- **pytest** - Main testing framework
- **pytest-asyncio** - Async testing support
- **unittest.mock** - Mocking and patching
- **aiogram testing utilities** - Bot-specific testing tools

### Test Categories
- **Unit Tests** - Individual component testing
- **Integration Tests** - Component interaction testing
- **End-to-End Tests** - Complete workflow testing
- **Performance Tests** - Load and performance testing

## Quick Start

### Running Tests

```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_bot.py

# Run specific test
uv run pytest tests/test_bot.py::test_start_command

# Run with coverage
uv run pytest --cov=. --cov-report=html
```

### Test Results
```bash
# Expected output
=============== 80 passed, 1 skipped in 3.36s ===============
```

## Test Structure

### Directory Layout
```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── utils.py                 # Test utilities
├── test_bot.py              # Bot component tests
├── test_core.py             # Core module tests
├── test_services.py         # Service tests
├── test_integration.py      # Integration tests
├── test_utils.py            # Utility tests
├── test_database.py         # Database tests
└── test_postgres.py         # PostgreSQL-specific tests
```

### Test Configuration

```python
# conftest.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock

@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mock_bot():
    """Create mock bot instance."""
    bot = AsyncMock()
    bot.id = 123456789
    bot.username = "test_bot"
    return bot

@pytest.fixture
async def mock_message():
    """Create mock message instance."""
    from aiogram.types import Message, User, Chat
    
    message = AsyncMock(spec=Message)
    message.from_user = User(
        id=123456789,
        is_bot=False,
        first_name="Test",
        username="test_user"
    )
    message.chat = Chat(id=123456789, type="private")
    message.text = "/start"
    message.message_id = 1
    return message
```

## Unit Testing

### Testing Bot Handlers

```python
# tests/test_handlers.py
import pytest
from unittest.mock import AsyncMock, patch
from bot.handlers.commands import start_command, help_command

async def test_start_command(mock_message):
    """Test start command handler."""
    await start_command(mock_message)
    
    # Verify response was sent
    mock_message.answer.assert_called_once()
    
    # Check response content
    args = mock_message.answer.call_args[0]
    assert "Hello Test" in args[0]
    assert "Welcome" in args[0]

async def test_help_command(mock_message):
    """Test help command handler."""
    await help_command(mock_message)
    
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "Commands:" in args[0]
    assert "/start" in args[0]

@patch('core.db_factory.DatabaseFactory.create_database')
async def test_user_info_command(mock_db_factory, mock_message):
    """Test user info command with database interaction."""
    # Setup mock database
    mock_db = AsyncMock()
    mock_db.get_user.return_value = {
        'id': 123456789,
        'username': 'test_user',
        'first_name': 'Test'
    }
    mock_db_factory.return_value = mock_db
    
    from bot.handlers.commands import user_info_command
    await user_info_command(mock_message)
    
    # Verify database was called
    mock_db.get_user.assert_called_once_with(123456789)
    
    # Verify response
    mock_message.answer.assert_called_once()
```

### Testing Core Components

```python
# tests/test_core.py
import pytest
from core.config import Config
from core.database import Database

def test_config_loading():
    """Test configuration loading."""
    config = Config()
    
    # Test required fields
    assert hasattr(config, 'BOT_TOKEN')
    assert hasattr(config, 'DATABASE_URL')
    
    # Test defaults
    assert config.BOT_MODE == 'polling'
    assert config.LOG_LEVEL == 'INFO'

async def test_database_connection():
    """Test database connection."""
    db = Database()
    await db.connect()
    
    # Test connection
    assert await db.is_connected()
    
    # Test basic operations
    await db.save_user({
        'id': 123,
        'username': 'test',
        'first_name': 'Test'
    })
    
    user = await db.get_user(123)
    assert user['username'] == 'test'
    
    await db.close()

async def test_database_error_handling():
    """Test database error handling."""
    db = Database()
    
    # Test invalid operations
    with pytest.raises(Exception):
        await db.get_user(999999999)  # Non-existent user
```

### Testing Utilities

```python
# tests/test_utils.py
import pytest
from utils.formatters import MessageFormatter
from utils.keyboards import KeyboardBuilder
from utils.validators import Validator

def test_message_formatter():
    """Test message formatting utilities."""
    # Test markdown escaping
    text = "Text with *special* chars"
    escaped = MessageFormatter.escape_markdown(text)
    assert "*" not in escaped or "\\*" in escaped
    
    # Test user mention formatting
    user = {'first_name': 'John', 'username': 'john_doe'}
    mention = MessageFormatter.format_user_mention(user)
    assert 'John' in mention

def test_keyboard_builder():
    """Test keyboard building utilities."""
    builder = KeyboardBuilder()
    
    # Test inline keyboard
    keyboard = builder.create_inline_keyboard([
        [("Button 1", "data_1")],
        [("Button 2", "data_2")]
    ])
    
    assert keyboard.inline_keyboard
    assert len(keyboard.inline_keyboard) == 2

def test_validators():
    """Test input validation utilities."""
    # Test email validation
    assert Validator.is_valid_email("test@example.com")
    assert not Validator.is_valid_email("invalid-email")
    
    # Test user ID validation
    assert Validator.is_valid_user_id(123456789)
    assert not Validator.is_valid_user_id(-1)
```

## Integration Testing

### Testing Bot Factory

```python
# tests/test_integration.py
import pytest
from unittest.mock import patch, AsyncMock
from bot.factory import BotFactory

@patch('bot.factory.Bot')
@patch('bot.factory.Dispatcher')
async def test_bot_creation(mock_dispatcher, mock_bot):
    """Test bot and dispatcher creation."""
    # Setup mocks
    mock_bot_instance = AsyncMock()
    mock_dp_instance = AsyncMock()
    mock_bot.return_value = mock_bot_instance
    mock_dispatcher.return_value = mock_dp_instance
    
    # Create bot
    bot, dp = BotFactory.create_bot()
    
    # Verify creation
    assert bot == mock_bot_instance
    assert dp == mock_dp_instance
    mock_bot.assert_called_once()
    mock_dispatcher.assert_called_once()

async def test_handler_registration():
    """Test handler registration process."""
    from bot.handlers.registry import register_handlers
    from aiogram import Dispatcher
    
    dp = Dispatcher()
    register_handlers(dp)
    
    # Verify handlers are registered
    assert len(dp.message.handlers) > 0
    assert len(dp.callback_query.handlers) >= 0
```

### Testing Services

```python
# tests/test_services.py
import pytest
from unittest.mock import AsyncMock, patch
from services.polling import PollingService
from services.webhook import WebhookService

async def test_polling_service():
    """Test polling service functionality."""
    mock_bot = AsyncMock()
    mock_dp = AsyncMock()
    
    service = PollingService(mock_bot, mock_dp)
    
    # Test service initialization
    assert service.bot == mock_bot
    assert service.dp == mock_dp
    
    # Test start method exists
    assert hasattr(service, 'start')
    assert callable(service.start)

async def test_webhook_service():
    """Test webhook service functionality."""
    mock_bot = AsyncMock()
    mock_dp = AsyncMock()
    
    service = WebhookService(mock_bot, mock_dp)
    
    # Test service initialization
    assert service.bot == mock_bot
    assert service.dp == mock_dp
    
    # Test configuration
    assert hasattr(service, 'webhook_url')
    assert hasattr(service, 'webhook_port')
```

### Testing Error Handling

```python
async def test_error_handler():
    """Test error handling functionality."""
    from bot.handlers.errors import error_handler
    from aiogram.types import ErrorEvent
    
    # Create mock error event
    mock_event = AsyncMock(spec=ErrorEvent)
    mock_event.exception = Exception("Test error")
    mock_event.update = AsyncMock()
    mock_event.update.message = AsyncMock()
    
    # Test error handler
    await error_handler(mock_event)
    
    # Verify error was handled
    mock_event.update.message.answer.assert_called_once()
```

## Database Testing

### SQLite Testing

```python
# tests/test_database.py
import pytest
import tempfile
import os
from core.database import Database

@pytest.fixture
async def temp_database():
    """Create temporary database for testing."""
    # Create temporary file
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    # Create database instance
    db = Database(database_url=path)
    await db.connect()
    
    yield db
    
    # Cleanup
    await db.close()
    os.unlink(path)

async def test_user_operations(temp_database):
    """Test user CRUD operations."""
    db = temp_database
    
    # Test save user
    user_data = {
        'id': 123456789,
        'username': 'test_user',
        'first_name': 'Test',
        'last_name': 'User'
    }
    await db.save_user(user_data)
    
    # Test get user
    user = await db.get_user(123456789)
    assert user['username'] == 'test_user'
    assert user['first_name'] == 'Test'
    
    # Test update user
    await db.update_user(123456789, {'username': 'updated_user'})
    updated_user = await db.get_user(123456789)
    assert updated_user['username'] == 'updated_user'
    
    # Test user exists
    assert await db.user_exists(123456789)
    assert not await db.user_exists(999999999)

async def test_activity_logging(temp_database):
    """Test activity logging functionality."""
    db = temp_database
    
    # Save user first
    await db.save_user({'id': 123, 'username': 'test'})
    
    # Log activity
    await db.log_activity(123, 'command_used', '/start')
    
    # Get activities
    activities = await db.get_user_activities(123)
    assert len(activities) == 1
    assert activities[0]['activity_type'] == 'command_used'
```

### PostgreSQL Testing

```python
# tests/test_postgres.py
import pytest
from core.postgres import PostgreSQLDatabase

@pytest.mark.skipif(
    not os.getenv('TEST_POSTGRESQL_URL'),
    reason="PostgreSQL test URL not provided"
)
async def test_postgresql_connection():
    """Test PostgreSQL connection."""
    db = PostgreSQLDatabase()
    await db.connect()
    
    assert await db.is_connected()
    await db.close()

@pytest.mark.skipif(
    not os.getenv('TEST_POSTGRESQL_URL'),
    reason="PostgreSQL test URL not provided"
)
async def test_postgresql_features():
    """Test PostgreSQL-specific features."""
    db = PostgreSQLDatabase()
    await db.connect()
    
    # Test JSONB storage
    await db.save_user({
        'id': 123,
        'username': 'test',
        'metadata': {'premium': True, 'features': ['analytics']}
    })
    
    # Test metrics
    await db.record_metric('test_metric', 100, {'source': 'test'})
    metrics = await db.get_metrics('test_metric')
    assert len(metrics) > 0
    
    await db.close()
```

## Performance Testing

### Load Testing

```python
# tests/test_performance.py
import pytest
import asyncio
import time
from concurrent.futures import ThreadPoolExecutor

async def test_database_performance():
    """Test database performance under load."""
    from core.db_factory import DatabaseFactory
    
    db = DatabaseFactory.create_database()
    await db.connect()
    
    # Test concurrent user saves
    start_time = time.time()
    
    tasks = []
    for i in range(100):
        task = db.save_user({
            'id': i,
            'username': f'user_{i}',
            'first_name': f'User{i}'
        })
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Should complete within reasonable time
    assert duration < 5.0  # 5 seconds for 100 operations
    
    await db.close()

async def test_handler_performance():
    """Test handler performance."""
    from bot.handlers.commands import start_command
    from tests.utils import create_mock_message
    
    # Test multiple handler calls
    start_time = time.time()
    
    tasks = []
    for i in range(50):
        message = create_mock_message()
        task = start_command(message)
        tasks.append(task)
    
    await asyncio.gather(*tasks)
    
    end_time = time.time()
    duration = end_time - start_time
    
    # Should handle 50 commands quickly
    assert duration < 2.0  # 2 seconds for 50 commands
```

## Test Utilities

### Mock Factories

```python
# tests/utils.py
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import Message, User, Chat, Update

def create_mock_user(user_id=123456789, username="test_user", first_name="Test"):
    """Create mock user object."""
    return User(
        id=user_id,
        is_bot=False,
        first_name=first_name,
        username=username
    )

def create_mock_message(text="/start", user_id=123456789):
    """Create mock message object."""
    message = AsyncMock(spec=Message)
    message.from_user = create_mock_user(user_id)
    message.chat = Chat(id=user_id, type="private")
    message.text = text
    message.message_id = 1
    return message

def create_mock_update(message_text="/start"):
    """Create mock update object."""
    update = AsyncMock(spec=Update)
    update.message = create_mock_message(message_text)
    update.update_id = 1
    return update

async def create_test_database():
    """Create test database instance."""
    import tempfile
    import os
    
    fd, path = tempfile.mkstemp(suffix='.db')
    os.close(fd)
    
    from core.database import Database
    db = Database(database_url=path)
    await db.connect()
    
    return db, path
```

### Test Decorators

```python
# tests/decorators.py
import pytest
import functools

def requires_database(func):
    """Decorator for tests that require database."""
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        db, path = await create_test_database()
        try:
            result = await func(db, *args, **kwargs)
        finally:
            await db.close()
            os.unlink(path)
        return result
    return wrapper

def skip_if_no_postgres(func):
    """Skip test if PostgreSQL not available."""
    return pytest.mark.skipif(
        not os.getenv('TEST_POSTGRESQL_URL'),
        reason="PostgreSQL test URL not provided"
    )(func)
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_DB: test_db
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.11'
    
    - name: Install uv
      run: pip install uv
    
    - name: Install dependencies
      run: uv sync
    
    - name: Run tests
      run: uv run pytest --cov=. --cov-report=xml
      env:
        TEST_POSTGRESQL_URL: postgresql://postgres:postgres@localhost:5432/test_db
    
    - name: Upload coverage
      uses: codecov/codecov-action@v1
```

## Test Configuration

### pytest.ini

```ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --strict-markers
    --disable-warnings
    --tb=short
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    postgres: marks tests that require PostgreSQL
asyncio_mode = auto
```

### Coverage Configuration

```ini
# .coveragerc
[run]
source = .
omit = 
    tests/*
    .venv/*
    */migrations/*
    */venv/*
    */env/*

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
```

## Best Practices

### 1. Test Organization
- Group related tests in classes
- Use descriptive test names
- Follow AAA pattern (Arrange, Act, Assert)
- Keep tests independent

### 2. Mocking Strategy
- Mock external dependencies
- Use appropriate mock types (AsyncMock for async)
- Verify mock calls and arguments
- Reset mocks between tests

### 3. Test Data
- Use fixtures for reusable test data
- Create factory functions for complex objects
- Use temporary databases for isolation
- Clean up resources after tests

### 4. Performance
- Run fast tests frequently
- Separate slow tests with markers
- Use parallel test execution
- Monitor test execution time

## Troubleshooting

### Common Issues

#### 1. Async Test Failures
```python
# Wrong: Missing async/await
def test_async_function():
    result = async_function()  # Returns coroutine

# Correct: Proper async test
async def test_async_function():
    result = await async_function()
```

#### 2. Mock Configuration
```python
# Wrong: Incorrect mock spec
mock_message = MagicMock()

# Correct: Proper spec
mock_message = AsyncMock(spec=Message)
```

#### 3. Database Test Isolation
```python
# Wrong: Shared database state
db = Database()  # Global instance

# Correct: Isolated test database
@pytest.fixture
async def test_db():
    # Create temporary database
    pass
```

### Running Specific Tests

```bash
# Run unit tests only
uv run pytest -m unit

# Run integration tests
uv run pytest -m integration

# Run PostgreSQL tests
uv run pytest -m postgres

# Run with specific pattern
uv run pytest -k "test_user"

# Run failed tests only
uv run pytest --lf
```

## Examples

See the [tests/](../../tests/) directory for:
- Complete test suite examples
- Mock object patterns
- Integration test strategies
- Performance testing approaches

---

*Need help with testing? Check the [pytest documentation](https://docs.pytest.org/) or review our [test examples](../../tests/).*