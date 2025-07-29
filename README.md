# 🤖 Python Telegram Bot Template

A comprehensive, production-ready async Telegram bot template built with Python, featuring both polling and webhook support, **highly modular architecture**, and extensive utilities.

## ✨ Features

- **🔄 Dual Mode Support**: Both polling and webhook modes
- **⚡ Async/Await**: Fully asynchronous for high performance
- **🏗️ Highly Modular Architecture**: Component-based design with clear separation of concerns
- **🛡️ Security Features**: Rate limiting, admin controls, input validation
- **📊 Database Integration**: SQLite with async support for user management
- **🔧 Configuration Management**: Environment-based configuration with validation
- **📝 Comprehensive Logging**: Structured logging with file and console output
- **🚀 Production Ready**: Error handling, graceful shutdown, health checks
- **🛠️ Developer Friendly**: Type hints, documentation, CLI tools, and utilities
- **🧩 Component Registry**: Dynamic module loading and management

## 🏗️ Modular Project Structure

```
├── 📁 core/                    # Core functionality
│   ├── __init__.py            # Core package initialization
│   ├── config.py              # Configuration management
│   ├── database.py            # Database operations
│   ├── logger.py              # Logging configuration
│   └── middleware.py          # Middleware and decorators
├── 📁 bot/                     # Bot application layer
│   ├── __init__.py            # Bot package initialization
│   ├── factory.py             # Bot factory and creation
│   ├── application.py         # Bot application wrapper
│   └── handlers/              # Handler modules
│       ├── __init__.py        # Handlers package
│       ├── commands.py        # Command handlers
│       ├── messages.py        # Message handlers
│       ├── errors.py          # Error handlers
│       └── registry.py        # Handler registration
├── 📁 services/               # Service layer
│   ├── __init__.py            # Services package
│   ├── polling.py             # Polling service
│   └── webhook.py             # Webhook service
├── 📁 utils/                  # Utility modules
│   ├── __init__.py            # Utils package
│   ├── formatters.py          # Message formatting
│   ├── keyboards.py           # Keyboard builders
│   ├── files.py               # File handling
│   ├── text.py                # Text processing
│   ├── cache.py               # Async caching
│   └── validators.py          # Data validation
├── 📄 main.py                 # Main application runner
├── 📄 run.py                  # Simple entry point
├── 📄 cli.py                  # Command line interface
├── 📄 project.py              # Project configuration & registry
├── 📄 example_bot.py          # Example implementation
├── 📄 .env.example            # Environment template
├── 📄 pyproject.toml          # Project dependencies
└── 📄 README.md               # Documentation
```

## 🚀 Quick Start

### 1. Clone and Setup

```bash
# Clone the repository
git clone <your-repo-url>
cd Python-Telegram-Bot-Template

# Install dependencies using uv
uv sync
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with your bot token and settings
```

### 3. Get Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Create a new bot with `/newbot`
3. Copy the bot token to your `.env` file

### 4. Run the Bot

```bash
# Activate virtual environment
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Simple run
python run.py

# Using CLI (recommended)
python cli.py --mode polling

# Specific mode
python cli.py --mode webhook
```

## ⚙️ Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `BOT_TOKEN` | Your Telegram bot token | - | ✅ |
| `BOT_USERNAME` | Your bot username | - | ❌ |
| `BOT_MODE` | Bot mode: `polling` or `webhook` | `polling` | ❌ |
| `WEBHOOK_URL` | Public URL for webhook | - | ⚠️ (webhook mode) |
| `WEBHOOK_SECRET_TOKEN` | Secret token for webhook security | - | ❌ |
| `WEBHOOK_PORT` | Port for webhook server | `8000` | ❌ |
| `WEBHOOK_HOST` | Host for webhook server | `0.0.0.0` | ❌ |
| `ADMIN_USER_IDS` | Comma-separated admin user IDs | - | ❌ |
| `DATABASE_URL` | Database connection string | `sqlite:///bot.db` | ❌ |
| `DEBUG` | Enable debug mode | `false` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |

### Example .env

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=my_awesome_bot
BOT_MODE=polling
ADMIN_USER_IDS=123456789,987654321
DEBUG=true
LOG_LEVEL=INFO
```

## 🔧 Usage

### Adding New Commands

1. Create handler function in `bot/handlers/commands.py`:

```python
async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /my_command."""
    await update.message.reply_text("Hello from my command!")
```

2. Register handler in `bot/handlers/registry.py`:

```python
from .commands import my_command

def register_handlers(application: Application) -> None:
    """Register all handlers with the application."""
    # Add your new command
    application.add_handler(CommandHandler("my_command", my_command))
```

### Using Middleware

Apply decorators to your handlers:

```python
from core.middleware import admin_required, rate_limit, log_user_activity

@admin_required
@rate_limit(max_requests=5, window_seconds=60)
@log_user_activity
async def admin_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin-only command with rate limiting."""
    await update.message.reply_text("Admin command executed!")
```

### Database Operations

```python
from core.database import Database

db = Database()

# Save user
await db.save_user({
    'id': user.id,
    'username': user.username,
    'first_name': user.first_name
})

# Log activity
await db.log_activity(user.id, 'command_used', '/start')

# Get user
user_data = await db.get_user(user.id)
```

### Using Utilities

```python
from utils.formatters import MessageFormatter
from utils.keyboards import KeyboardBuilder
from utils.cache import AsyncCache
from telegram import InlineKeyboardButton

# Format message
formatted = MessageFormatter.escape_markdown("Special *text*")

# Build keyboard
buttons = [
    InlineKeyboardButton("Button 1", callback_data="btn1"),
    InlineKeyboardButton("Button 2", callback_data="btn2")
]
keyboard = KeyboardBuilder.build_menu(buttons, n_cols=2)

# Use cache
cache = AsyncCache()
await cache.set("key", "value", ttl=300)
value = await cache.get("key")
```

### Creating Custom Services

```python
# Create custom service in services/
from services.polling import PollingService

class CustomService(PollingService):
    """Custom service extending polling functionality."""
    
    async def start(self):
        """Start with custom initialization."""
        await self.custom_setup()
        await super().start()
    
    async def custom_setup(self):
        """Custom setup logic."""
        pass
```

### Using the Module Registry

```python
from project import get_registry

registry = get_registry()

# List available modules
modules = registry.list_modules()

# Get module components
components = registry.list_components("utils")

# Import component dynamically
formatter_module = registry.import_component("utils", "formatters")
```

## 🌐 Webhook Mode

### Local Development with ngrok

```bash
# Install ngrok
# Start your bot in webhook mode
python cli.py run --mode webhook

# In another terminal, expose local port
ngrok http 8000

# Update WEBHOOK_URL in .env with ngrok URL
WEBHOOK_URL=https://abc123.ngrok.io
```

### Production Deployment

1. Deploy to your server (VPS, cloud, etc.)
2. Set up reverse proxy (nginx, Apache)
3. Configure SSL certificate
4. Update `WEBHOOK_URL` with your domain
5. Set `BOT_MODE=webhook`

## 📊 Logging

The template includes a comprehensive logging system with multiple output formats and advanced features:

### Log Files

All logs are stored in the `logs/` directory:

- **`bot.log`** - Main application log with detailed information
- **`errors.log`** - Error-only log for quick issue identification  
- **`bot.json`** - Structured JSON logs for analysis and monitoring
- **`debug.log`** - Detailed debug information (only in debug mode)

### Log Features

- **Colored Console Output** - Easy-to-read colored logs in the terminal
- **Log Rotation** - Automatic rotation when files reach size limits
- **Structured Logging** - JSON format with user IDs, commands, and context
- **Performance Tracking** - Automatic timing of operations
- **Security Logging** - Track unauthorized access attempts
- **User Action Logging** - Track all user interactions with context

### Using Enhanced Logging

```python
from core.logger import get_logger, log_user_action, log_error, log_performance
from utils.logging_utils import log_command_execution, LogContext

# Get a logger
logger = get_logger('my_module')

# Log user actions with context
log_user_action(user_id=123, action='custom_command', details='Additional info')

# Log errors with context
try:
    # Some operation
    pass
except Exception as e:
    log_error(e, 'operation_context', user_id=123)

# Log performance metrics
log_performance('database_query', 0.150, {'query_type': 'SELECT'})

# Use decorators for automatic logging
@log_command_execution('my_command')
async def my_command_handler(update, context):
    # Command logic here
    pass

# Use context manager for operation timing
async with LogContext('complex_operation', extra_data={'param': 'value'}):
    # Your operation here
    pass
```

### Log Analysis

Analyze your bot's performance and usage with the built-in log analyzer:

```bash
# Analyze last 24 hours
python scripts/analyze_logs.py

# Analyze last 7 days  
python scripts/analyze_logs.py --hours 168

# Save report to file
python scripts/analyze_logs.py --output report.txt
```

The analyzer provides:
- User activity statistics
- Command usage patterns  
- Performance metrics
- Error analysis
- Hourly activity distribution

## 📊 Monitoring

### Health Check

When running in webhook mode, access:
- `GET /health` - Health check endpoint
- `GET /` - Basic info endpoint

### Log Levels

Supported log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

## 🛡️ Security Features

- **Rate Limiting**: Prevent spam and abuse
- **Admin Controls**: Restrict sensitive commands
- **Input Validation**: Sanitize user inputs
- **Secret Token**: Webhook security
- **Session Management**: Track user sessions
- **Activity Logging**: Monitor user actions

## 🔄 Adding Dependencies

Use `uv add` instead of editing `pyproject.toml` directly:

```bash
# Add new dependency
uv add requests

# Add development dependency
uv add --dev pytest

# Add optional dependency
uv add --optional redis
```

## 🧪 Testing

```bash
# Install test dependencies
uv add --dev pytest pytest-asyncio

# Run tests
pytest
```

## 📦 Deployment

### Docker (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.13-slim

WORKDIR /app
COPY . .

RUN pip install uv
RUN uv sync --frozen

CMD ["python", "main.py"]
```

### Systemd Service

Create `/etc/systemd/system/telegram-bot.service`:

```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=bot
WorkingDirectory=/path/to/bot
ExecStart=/path/to/bot/.venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- 📖 [python-telegram-bot Documentation](https://docs.python-telegram-bot.org/)
- 🤖 [Telegram Bot API](https://core.telegram.org/bots/api)
- 💬 [Telegram Bot Support](https://t.me/BotSupport)

## 🙏 Acknowledgments

- [python-telegram-bot](https://github.com/python-telegram-bot/python-telegram-bot) - The amazing library this template is built on
- [FastAPI](https://fastapi.tiangolo.com/) - For webhook server implementation
- [uv](https://github.com/astral-sh/uv) - For fast Python package management

---

**Happy Bot Building! 🚀**