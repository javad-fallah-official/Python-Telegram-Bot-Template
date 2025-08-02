# 🤝 Contributing Guide

Thank you for your interest in contributing to the Python Telegram Bot Template! This guide will help you get started with contributing to the project.

## Table of Contents

- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Code Standards](#code-standards)
- [Testing Guidelines](#testing-guidelines)
- [Submitting Changes](#submitting-changes)
- [Issue Guidelines](#issue-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Getting Started

### Prerequisites

Before contributing, ensure you have:
- Python 3.11 or higher
- Git installed and configured
- Basic knowledge of Python and async programming
- Familiarity with Telegram Bot API and aiogram

### Fork and Clone

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/Python-Telegram-Bot-Template.git
   cd Python-Telegram-Bot-Template
   ```

3. **Add upstream remote**:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/Python-Telegram-Bot-Template.git
   ```

## Development Setup

### 1. Install Dependencies

Using `uv` (recommended):
```bash
# Install uv if you haven't already
pip install uv

# Install project dependencies
uv sync

# Install development dependencies
uv sync --dev
```

Using `pip`:
```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. Environment Configuration

Create a `.env` file for development:
```bash
# Copy example environment file
cp .env.example .env

# Edit with your development settings
# You'll need a test bot token from @BotFather
```

### 3. Database Setup

For development, you can use SQLite (default) or PostgreSQL:

**SQLite (Default):**
```bash
# No additional setup required
DATABASE_TYPE=sqlite
DATABASE_URL=bot.db
```

**PostgreSQL (Optional):**
```bash
# Install PostgreSQL locally or use Docker
docker run --name postgres-dev -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres:13

# Update .env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://postgres:password@localhost:5432/bot_dev
```

### 4. Verify Setup

```bash
# Run tests to verify everything works
uv run pytest

# Start the bot in development mode
uv run python main.py
```

## Code Standards

### Code Style

We use several tools to maintain code quality:

#### 1. Black (Code Formatting)
```bash
# Format code
uv run black .

# Check formatting
uv run black --check .
```

#### 2. isort (Import Sorting)
```bash
# Sort imports
uv run isort .

# Check import sorting
uv run isort --check-only .
```

#### 3. flake8 (Linting)
```bash
# Run linting
uv run flake8 .
```

#### 4. mypy (Type Checking)
```bash
# Run type checking
uv run mypy .
```

### Configuration Files

#### pyproject.toml
```toml
[tool.black]
line-length = 88
target-version = ['py311']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.venv
  | build
  | dist
)/
'''

[tool.isort]
profile = "black"
multi_line_output = 3
line_length = 88
known_first_party = ["bot", "core", "services", "utils"]

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true
```

#### .flake8
```ini
[flake8]
max-line-length = 88
extend-ignore = E203, W503
exclude = .git,__pycache__,.venv,build,dist
```

### Coding Conventions

#### 1. Python Style
- Follow PEP 8 guidelines
- Use type hints for all functions and methods
- Write docstrings for public functions and classes
- Use meaningful variable and function names

```python
# Good
async def get_user_by_id(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Retrieve user information by ID.
    
    Args:
        user_id: The Telegram user ID
        
    Returns:
        User data dictionary or None if not found
    """
    return await database.get_user(user_id)

# Bad
async def get_user(id):
    return await db.get(id)
```

#### 2. Async/Await
- Always use `async`/`await` for asynchronous operations
- Don't mix sync and async code unnecessarily
- Use proper exception handling in async functions

```python
# Good
async def send_message(chat_id: int, text: str) -> None:
    try:
        await bot.send_message(chat_id, text)
    except TelegramAPIError as e:
        logger.error(f"Failed to send message: {e}")

# Bad
def send_message(chat_id, text):
    bot.send_message(chat_id, text)  # Missing await
```

#### 3. Error Handling
- Use specific exception types
- Log errors appropriately
- Provide meaningful error messages

```python
# Good
try:
    user = await database.get_user(user_id)
    if not user:
        raise UserNotFoundError(f"User {user_id} not found")
except DatabaseError as e:
    logger.error(f"Database error while fetching user {user_id}: {e}")
    raise

# Bad
try:
    user = database.get_user(user_id)
except:
    pass
```

## Testing Guidelines

### Test Requirements

All contributions must include appropriate tests:

#### 1. Unit Tests
- Test individual functions and methods
- Mock external dependencies
- Cover edge cases and error conditions

```python
async def test_get_user_success():
    """Test successful user retrieval."""
    mock_db = AsyncMock()
    mock_db.get_user.return_value = {"id": 123, "username": "test"}
    
    result = await get_user_by_id(123)
    
    assert result["username"] == "test"
    mock_db.get_user.assert_called_once_with(123)
```

#### 2. Integration Tests
- Test component interactions
- Use test databases
- Verify end-to-end workflows

```python
async def test_user_registration_flow():
    """Test complete user registration process."""
    # Setup test database
    db = await create_test_database()
    
    # Test registration
    await register_user(123, "test_user")
    
    # Verify user was saved
    user = await db.get_user(123)
    assert user["username"] == "test_user"
```

#### 3. Test Coverage
- Aim for >90% test coverage
- Include both positive and negative test cases
- Test error handling paths

```bash
# Run tests with coverage
uv run pytest --cov=. --cov-report=html

# View coverage report
open htmlcov/index.html
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_handlers.py

# Run with verbose output
uv run pytest -v

# Run only failed tests
uv run pytest --lf

# Run tests in parallel
uv run pytest -n auto
```

## Submitting Changes

### Branch Strategy

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Keep branches focused**: One feature or fix per branch

3. **Use descriptive branch names**:
   - `feature/add-user-analytics`
   - `fix/database-connection-error`
   - `docs/update-installation-guide`

### Commit Guidelines

#### Commit Message Format
```
type(scope): brief description

Detailed explanation of the change (if needed)

- List any breaking changes
- Reference issues: Fixes #123
```

#### Commit Types
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

#### Examples
```bash
feat(handlers): add user analytics command

Add /analytics command to show user statistics including:
- Total commands used
- Most active hours
- Favorite features

Fixes #45

fix(database): handle connection timeout gracefully

- Add retry logic for database connections
- Improve error messages for connection failures
- Add connection pooling for PostgreSQL

Breaking change: Database.connect() now returns bool instead of None
```

### Pull Request Process

#### 1. Before Submitting

```bash
# Update your branch with latest changes
git fetch upstream
git rebase upstream/main

# Run all checks
uv run black .
uv run isort .
uv run flake8 .
uv run mypy .
uv run pytest

# Ensure all tests pass
uv run pytest --cov=. --cov-report=term-missing
```

#### 2. Pull Request Template

When creating a PR, include:

```markdown
## Description
Brief description of the changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Tests pass locally
- [ ] New tests added for new functionality
- [ ] Coverage maintained or improved

## Checklist
- [ ] Code follows project style guidelines
- [ ] Self-review completed
- [ ] Documentation updated (if needed)
- [ ] No breaking changes (or clearly documented)

## Related Issues
Fixes #(issue number)
```

#### 3. Review Process

- All PRs require at least one review
- Address review feedback promptly
- Keep discussions constructive and professional
- Update documentation if needed

## Issue Guidelines

### Reporting Bugs

Use the bug report template:

```markdown
**Bug Description**
Clear description of the bug

**Steps to Reproduce**
1. Step one
2. Step two
3. Step three

**Expected Behavior**
What should happen

**Actual Behavior**
What actually happens

**Environment**
- OS: [e.g., Ubuntu 20.04]
- Python version: [e.g., 3.11.0]
- Bot template version: [e.g., 1.0.0]

**Additional Context**
Any other relevant information
```

### Feature Requests

Use the feature request template:

```markdown
**Feature Description**
Clear description of the proposed feature

**Use Case**
Why is this feature needed?

**Proposed Solution**
How should this feature work?

**Alternatives Considered**
Other approaches you've considered

**Additional Context**
Any other relevant information
```

### Issue Labels

- `bug`: Something isn't working
- `enhancement`: New feature or request
- `documentation`: Documentation improvements
- `good first issue`: Good for newcomers
- `help wanted`: Extra attention needed
- `priority:high`: High priority issue
- `priority:low`: Low priority issue

## Documentation

### Documentation Standards

#### 1. Code Documentation
- Write docstrings for all public functions and classes
- Use Google-style docstrings
- Include type hints in function signatures

```python
async def process_user_command(
    message: Message, 
    command: str, 
    args: List[str]
) -> Optional[str]:
    """
    Process a user command and return response.
    
    Args:
        message: The incoming Telegram message
        command: The command name (without /)
        args: List of command arguments
        
    Returns:
        Response message or None if no response needed
        
    Raises:
        CommandError: If command processing fails
        ValidationError: If arguments are invalid
    """
```

#### 2. README Updates
- Update README.md for new features
- Include usage examples
- Update installation instructions if needed

#### 3. Documentation Files
- Create documentation for new features
- Update existing docs for changes
- Include code examples and screenshots

### Documentation Structure

```
docs/
├── README.md                 # Main documentation index
├── setup/
│   ├── INSTALLATION.md       # Installation guide
│   └── CONFIGURATION.md      # Configuration guide
├── features/
│   ├── DATABASE.md           # Database features
│   ├── HANDLERS.md           # Handler system
│   └── MIDDLEWARE.md         # Middleware system
├── migration/
│   ├── AIOGRAM_MIGRATION.md  # Framework migration
│   ├── DATABASE_MIGRATION.md # Database migration
│   └── TEST_MIGRATION.md     # Test migration
├── advanced/
│   ├── POSTGRESQL.md         # PostgreSQL features
│   ├── DEPLOYMENT.md         # Deployment guide
│   └── PERFORMANCE.md        # Performance optimization
├── development/
│   ├── TESTING.md            # Testing guide
│   ├── CONTRIBUTING.md       # This file
│   └── ARCHITECTURE.md       # Architecture overview
└── api/
    ├── HANDLERS.md           # Handler API reference
    ├── DATABASE.md           # Database API reference
    └── UTILITIES.md          # Utility API reference
```

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **GitHub Discussions**: General questions and discussions
- **Pull Requests**: Code review and collaboration

### Code of Conduct

We follow the [Contributor Covenant Code of Conduct](https://www.contributor-covenant.org/version/2/1/code_of_conduct/):

- Be respectful and inclusive
- Welcome newcomers and help them learn
- Focus on constructive feedback
- Respect different viewpoints and experiences

### Getting Help

If you need help:

1. **Check existing documentation** in the `docs/` folder
2. **Search existing issues** for similar problems
3. **Create a new issue** with detailed information
4. **Join discussions** for general questions

### Recognition

Contributors are recognized in:
- `CONTRIBUTORS.md` file
- Release notes for significant contributions
- GitHub contributor statistics

## Development Workflow

### Typical Workflow

1. **Pick an issue** or propose a new feature
2. **Create a branch** from main
3. **Implement changes** following code standards
4. **Write tests** for new functionality
5. **Update documentation** if needed
6. **Run all checks** locally
7. **Submit pull request** with clear description
8. **Address review feedback**
9. **Merge after approval**

### Release Process

1. **Version bumping** follows semantic versioning
2. **Changelog** is updated for each release
3. **Testing** on multiple environments
4. **Documentation** is updated
5. **Release notes** are published

## Quick Reference

### Common Commands

```bash
# Setup
uv sync --dev
cp .env.example .env

# Code quality
uv run black .
uv run isort .
uv run flake8 .
uv run mypy .

# Testing
uv run pytest
uv run pytest --cov=. --cov-report=html

# Git workflow
git checkout -b feature/my-feature
git add .
git commit -m "feat: add my feature"
git push origin feature/my-feature
```

### File Structure

```
Python-Telegram-Bot-Template/
├── bot/                      # Bot implementation
│   ├── handlers/            # Message handlers
│   ├── middleware/          # Middleware components
│   └── factory.py           # Bot factory
├── core/                    # Core functionality
│   ├── config.py           # Configuration
│   ├── database.py         # Database interface
│   └── postgres.py         # PostgreSQL implementation
├── services/               # Service layer
├── utils/                  # Utility functions
├── tests/                  # Test suite
├── docs/                   # Documentation
├── requirements.txt        # Dependencies
├── requirements-dev.txt    # Development dependencies
└── main.py                # Entry point
```

---

Thank you for contributing to the Python Telegram Bot Template! Your contributions help make this project better for everyone. 🚀