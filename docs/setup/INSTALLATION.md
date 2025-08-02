# 🚀 Installation Guide

This guide will walk you through setting up the Python Telegram Bot Template on your system.

## Prerequisites

### System Requirements
- **Python 3.8+** (Python 3.9+ recommended)
- **Git** for cloning the repository
- **uv** package manager (recommended) or pip

### Optional Requirements
- **PostgreSQL** (if using PostgreSQL database)
- **Docker** (for containerized deployment)

## Installation Methods

### Method 1: Using uv (Recommended)

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Python-Telegram-Bot-Template

# 2. Install dependencies with uv
uv sync

# 3. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Method 2: Using pip

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd Python-Telegram-Bot-Template

# 2. Create virtual environment
python -m venv .venv

# 3. Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# 4. Install dependencies
pip install -r requirements.txt
```

### Method 3: Development Installation

```bash
# For development with additional tools
uv sync --dev

# Or with pip
pip install -r requirements-dev.txt
```

## Dependency Overview

### Core Dependencies
- **aiogram** - Modern Telegram Bot framework
- **asyncpg** - PostgreSQL async driver
- **aiosqlite** - SQLite async driver
- **fastapi** - Web framework for webhook mode
- **uvicorn** - ASGI server for webhook mode
- **pydantic** - Data validation and settings
- **python-dotenv** - Environment variable management

### Development Dependencies
- **pytest** - Testing framework
- **pytest-asyncio** - Async testing support
- **black** - Code formatting
- **flake8** - Code linting
- **mypy** - Type checking

## Verification

### 1. Check Installation
```bash
# Verify Python version
python --version

# Verify dependencies
uv run python -c "import aiogram; print('aiogram installed successfully')"
```

### 2. Run Tests
```bash
# Run the test suite
uv run pytest

# Expected output: 80 passed, 1 skipped
```

### 3. Validate Configuration
```bash
# Test configuration loading
uv run python -c "from core.config import Config; print('Config loaded successfully')"
```

## Platform-Specific Notes

### Windows
- Use PowerShell or Command Prompt
- Virtual environment activation: `.venv\Scripts\activate`
- Path separators: Use backslashes `\` or forward slashes `/`

### macOS/Linux
- Use Terminal or your preferred shell
- Virtual environment activation: `source .venv/bin/activate`
- Path separators: Use forward slashes `/`

### Docker (Optional)
```dockerfile
# Example Dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync

CMD ["uv", "run", "python", "main.py"]
```

## Troubleshooting

### Common Issues

#### 1. Python Version Error
```bash
# Error: Python 3.8+ required
# Solution: Install Python 3.8 or higher
python --version
```

#### 2. uv Not Found
```bash
# Install uv
curl -LsSf https://astral.sh/uv/install.sh | sh
# Or on Windows:
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

#### 3. Permission Errors
```bash
# On macOS/Linux, use sudo if needed
sudo pip install uv

# Or install in user directory
pip install --user uv
```

#### 4. Virtual Environment Issues
```bash
# Remove and recreate virtual environment
rm -rf .venv
uv sync
```

#### 5. PostgreSQL Connection Issues
```bash
# Install PostgreSQL development headers
# Ubuntu/Debian:
sudo apt-get install libpq-dev

# macOS:
brew install postgresql

# Windows: Install PostgreSQL from official website
```

### Getting Help

If you encounter issues not covered here:

1. Check the [Configuration Guide](CONFIGURATION.md)
2. Review the [Quick Start Guide](../../QUICKSTART.md)
3. Look at the [examples/](../../examples/) directory
4. Open an issue on GitHub

## Next Steps

After successful installation:

1. **Configure Environment**: See [Configuration Guide](CONFIGURATION.md)
2. **Get Bot Token**: Create a bot with [@BotFather](https://t.me/BotFather)
3. **Run Your Bot**: Follow the [Quick Start Guide](../../QUICKSTART.md)
4. **Explore Features**: Check out the [Features Documentation](../features/)

---

*Need help? Check our [troubleshooting section](#troubleshooting) or open an issue on GitHub.*