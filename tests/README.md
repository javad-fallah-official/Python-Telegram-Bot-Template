# Testing

This directory contains all unit tests for the Telegram Bot Template.

## Structure

```
tests/
├── __init__.py              # Package initialization
├── utils.py                 # Test utilities and fixtures
├── test_core.py            # Core module tests
├── test_bot.py             # Bot component tests
├── test_utils.py           # Utility module tests
├── test_services.py        # Service module tests
└── test_integration.py     # Integration tests
```

## Running Tests

### Quick Start
```bash
# Run all tests
python run_tests.py

# Run specific test type
python run_tests.py --type unit
python run_tests.py --type integration
python run_tests.py --type core
```

### Using pytest directly
```bash
# Run all tests
uv run pytest

# Run with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_core.py

# Run with coverage
uv run pytest --cov=. --cov-report=html
```

### Test Types

- **Setup Tests**: `python test_setup.py` - Verify project setup
- **Unit Tests**: Test individual modules in isolation
- **Integration Tests**: Test component interactions
- **Core Tests**: Test core functionality (config, logger, database)
- **Bot Tests**: Test bot components (factory, handlers)
- **Utils Tests**: Test utility functions
- **Services Tests**: Test service components

## Test Utilities

The `tests/utils.py` module provides:

### Fixtures
- `mock_config`: Mock configuration for testing
- `mock_bot`: Mock Telegram bot instance
- `mock_update`: Mock Telegram update
- `mock_logger`: Mock logger instance
- `temp_db`: Temporary database for testing

### Helper Functions
- `assert_called_with_partial()`: Assert mock called with specific kwargs
- `run_async_test()`: Run async functions in tests
- `assert_valid_response()`: Assert bot response is valid
- `assert_valid_config()`: Assert configuration is valid

### Test Data Generators
- `generate_test_messages()`: Generate test message data
- `generate_test_users()`: Generate test user data

### Decorators
- `@skip_if_no_token`: Skip test if no real bot token
- `@requires_database`: Mark test as requiring database

## Writing Tests

### Basic Test Structure
```python
import pytest
from tests.utils import mock_config, mock_bot

class TestMyModule:
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Your test code here
        assert True
    
    @pytest.mark.asyncio
    async def test_async_functionality(self, mock_config):
        """Test async functionality."""
        # Your async test code here
        assert True
```

### Using Fixtures
```python
def test_with_config(mock_config):
    """Test using mock configuration."""
    from core.config import Config
    assert Config.BOT_TOKEN == "123456789:ABCDEFGHIJKLMNOPQRSTUVWXYZ"

@pytest.mark.asyncio
async def test_with_bot(mock_bot, mock_update):
    """Test using mock bot and update."""
    # Test bot interaction
    await mock_bot.send_message(chat_id=123, text="Test")
    mock_bot.send_message.assert_called_once()
```

## Best Practices

1. **Organize by Module**: Group tests by the module they're testing
2. **Use Descriptive Names**: Test names should describe what they test
3. **Mock External Dependencies**: Use mocks for external services
4. **Test Edge Cases**: Include tests for error conditions
5. **Keep Tests Independent**: Each test should be able to run in isolation
6. **Use Fixtures**: Leverage pytest fixtures for common setup
7. **Document Complex Tests**: Add docstrings for complex test logic

## Coverage

Generate coverage reports:
```bash
# HTML coverage report
uv run pytest --cov=. --cov-report=html

# Terminal coverage report
uv run pytest --cov=. --cov-report=term

# Both
python run_tests.py --coverage
```

Coverage reports help identify untested code and ensure comprehensive test coverage.