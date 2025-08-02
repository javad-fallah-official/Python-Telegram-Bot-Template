# ⚙️ Configuration Guide

This guide covers all configuration options for the Python Telegram Bot Template.

## Environment Variables

All configuration is done through environment variables in the `.env` file.

### Required Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `BOT_TOKEN` | Your Telegram bot token from @BotFather | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` |

### Bot Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `BOT_USERNAME` | Your bot's username (without @) | `None` | `my_awesome_bot` |
| `BOT_MODE` | Bot operation mode | `polling` | `polling` or `webhook` |
| `DEBUG` | Enable debug mode | `false` | `true` or `false` |

### Database Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `DATABASE_TYPE` | Database type override | `auto` | `auto`, `sqlite`, or `postgresql` |
| `DATABASE_URL` | Database connection string | `bot.db` | See [Database Examples](#database-examples) |

### Webhook Configuration (Webhook Mode Only)

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `WEBHOOK_URL` | Public URL for webhook | `None` | `https://yourdomain.com` |
| `WEBHOOK_SECRET_TOKEN` | Secret token for webhook security | `None` | `your_secret_token_here` |
| `WEBHOOK_HOST` | Host for webhook server | `0.0.0.0` | `0.0.0.0` |
| `WEBHOOK_PORT` | Port for webhook server | `8000` | `8000` |

### Logging Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `LOGGING_ENABLED` | Enable/disable logging | `true` | `true` or `false` |

### Security Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `ADMIN_USER_IDS` | Comma-separated admin user IDs | `None` | `123456789,987654321` |

## Configuration Examples

### Basic Setup (.env)

```env
# Required
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz

# Optional
BOT_USERNAME=my_awesome_bot
BOT_MODE=polling
DEBUG=false
LOG_LEVEL=INFO
```

### Production Setup (.env)

```env
# Bot Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=production_bot
BOT_MODE=webhook

# Database
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://botuser:secure_password@localhost:5432/botdb

# Webhook
WEBHOOK_URL=https://yourdomain.com
WEBHOOK_SECRET_TOKEN=your_very_secure_secret_token
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000

# Security
ADMIN_USER_IDS=123456789,987654321

# Logging
LOG_LEVEL=INFO
LOGGING_ENABLED=true
DEBUG=false
```

### Development Setup (.env)

```env
# Bot Configuration
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=dev_bot
BOT_MODE=polling

# Database (SQLite for development)
DATABASE_TYPE=sqlite
DATABASE_URL=dev_bot.db

# Security
ADMIN_USER_IDS=123456789

# Logging (Verbose for development)
LOG_LEVEL=DEBUG
LOGGING_ENABLED=true
DEBUG=true
```

## Database Examples

### SQLite (Default)
```env
DATABASE_TYPE=auto
DATABASE_URL=bot.db
```

### PostgreSQL
```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

### Force SQLite (Override)
```env
DATABASE_TYPE=sqlite
DATABASE_URL=postgresql://user:pass@localhost/db  # Ignored
```

### Auto-Detection
```env
DATABASE_TYPE=auto
DATABASE_URL=postgresql://user:pass@localhost/db  # Uses PostgreSQL
```

## Bot Mode Configuration

### Polling Mode (Default)
```env
BOT_MODE=polling
# No additional configuration needed
```

### Webhook Mode
```env
BOT_MODE=webhook
WEBHOOK_URL=https://yourdomain.com
WEBHOOK_SECRET_TOKEN=your_secret_token
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000
```

## Security Best Practices

### 1. Bot Token Security
- **Never commit** your bot token to version control
- Use environment variables or secure secret management
- Rotate tokens regularly in production

### 2. Webhook Security
- Always use HTTPS for webhook URLs
- Set a strong `WEBHOOK_SECRET_TOKEN`
- Validate webhook requests in production

### 3. Admin Controls
- Set `ADMIN_USER_IDS` to restrict admin commands
- Use Telegram user IDs, not usernames
- Regularly review admin access

### 4. Database Security
- Use strong passwords for PostgreSQL
- Restrict database access to necessary IPs
- Enable SSL for database connections in production

## Configuration Validation

### Manual Validation
```bash
# Test configuration loading
uv run python -c "from core.config import Config; config = Config(); print('✅ Configuration valid')"
```

### Using CLI Tool
```bash
# Validate all configuration
uv run python cli.py validate

# Test specific components
uv run python cli.py test
```

### Environment File Validation
```bash
# Check if .env file exists and is readable
ls -la .env

# Verify environment variables are loaded
uv run python -c "import os; print('BOT_TOKEN' in os.environ)"
```

## Troubleshooting

### Common Configuration Issues

#### 1. Missing .env File
```bash
# Error: Configuration not found
# Solution: Copy template and configure
cp .env.example .env
# Edit .env with your values
```

#### 2. Invalid Bot Token
```bash
# Error: Unauthorized (401)
# Solution: Check token format and validity
# Format: 1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```

#### 3. Database Connection Failed
```bash
# Error: Database connection failed
# Solution: Check DATABASE_URL format
# SQLite: bot.db or /path/to/database.db
# PostgreSQL: postgresql://user:pass@host:port/db
```

#### 4. Webhook Configuration Issues
```bash
# Error: Webhook setup failed
# Solution: Verify WEBHOOK_URL is publicly accessible
# Test: curl https://yourdomain.com/webhook
```

#### 5. Permission Denied
```bash
# Error: Permission denied for admin commands
# Solution: Add your user ID to ADMIN_USER_IDS
# Get your ID: Send /start to @userinfobot
```

### Configuration Testing

#### Test Database Connection
```bash
uv run python examples/database_switching_demo.py
```

#### Test Bot Token
```bash
uv run python -c "
from bot.factory import BotFactory
import asyncio

async def test():
    bot = BotFactory.create_bot()
dp = BotFactory.create_dispatcher()
    me = await bot.get_me()
    print(f'✅ Bot connected: @{me.username}')
    await bot.session.close()

asyncio.run(test())
"
```

#### Test Webhook URL
```bash
# Test webhook endpoint accessibility
curl -X POST https://yourdomain.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'
```

## Advanced Configuration

### Custom Configuration Files
```python
# Load configuration from custom file
from core.config import Config
config = Config(_env_file='custom.env')
```

### Environment-Specific Configs
```bash
# Development
cp .env.example .env.dev

# Production
cp .env.example .env.prod

# Load specific environment
export ENV_FILE=.env.prod
```

### Configuration Inheritance
```env
# Base configuration (.env.base)
LOG_LEVEL=INFO
LOGGING_ENABLED=true

# Environment-specific (.env)
include .env.base
BOT_TOKEN=your_token_here
```

## Next Steps

After configuring your bot:

1. **Test Configuration**: Run validation commands
2. **Start Bot**: Follow the [Quick Start Guide](../../QUICKSTART.md)
3. **Explore Features**: Check [Features Documentation](../features/)
4. **Deploy**: See [Deployment Guide](../advanced/DEPLOYMENT.md)

---

*Having configuration issues? Check our [troubleshooting section](#troubleshooting) or review the [Installation Guide](INSTALLATION.md).*