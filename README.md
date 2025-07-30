# 🤖 Python Telegram Bot Template

A comprehensive, production-ready async Telegram bot template built with Python, featuring both polling and webhook support, **highly modular architecture**, and extensive utilities.

## ✨ Features

- **🔄 Dual Mode Support**: Both polling and webhook modes
- **⚡ Async/Await**: Fully asynchronous for high performance
- **🏗️ Highly Modular Architecture**: Component-based design with clear separation of concerns
- **🛡️ Security Features**: Rate limiting, admin controls, input validation
- **📊 Database Integration**: SQLite and PostgreSQL support with switchable backends
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
│   ├── database.py            # SQLite database operations
│   ├── postgres.py            # PostgreSQL database operations
│   ├── db_factory.py          # Database factory and switching logic
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
├── 📄 polling.py              # Polling mode entry point
├── 📄 webhook.py              # Webhook mode entry point
├── 📁 examples/               # Example scripts and demos
│   ├── example_bot.py         # Example implementation
│   ├── database_switching_demo.py # Database switching demo
│   ├── postgresql_example.py  # PostgreSQL usage example
│   └── logging_demo.py        # Logging features demo
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
python cli.py run

# Specific mode
python cli.py run --mode polling
python cli.py run --mode webhook

# Test configuration
python cli.py test

# Validate environment
python cli.py validate
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
| `DATABASE_TYPE` | Database type: `auto`, `sqlite`, `postgresql` | `auto` | ❌ |
| `DEBUG` | Enable debug mode | `false` | ❌ |
| `LOG_LEVEL` | Logging level | `INFO` | ❌ |

### Example .env

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
BOT_USERNAME=my_awesome_bot
BOT_MODE=polling
ADMIN_USER_IDS=123456789,987654321
DATABASE_TYPE=auto
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

### Database Switching

The template supports both SQLite and PostgreSQL databases with easy switching via environment variables:

```env
# Auto-detect database type from URL (default)
DATABASE_TYPE=auto
DATABASE_URL=sqlite:///bot.db  # Uses SQLite

# Force SQLite (regardless of URL)
DATABASE_TYPE=sqlite
DATABASE_URL=postgresql://user:pass@localhost/db  # Still uses SQLite

# Force PostgreSQL (regardless of URL)
DATABASE_TYPE=postgresql
DATABASE_URL=simple.db  # Still uses PostgreSQL
```

#### PostgreSQL Setup

1. Install PostgreSQL dependencies:
```bash
uv add asyncpg
```

2. Configure PostgreSQL connection:
```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/database_name
```

3. The bot will automatically create tables and handle connections.

#### Database Examples

See the examples directory for practical usage:
- `examples/database_switching_demo.py` - Complete switching demonstration
- `examples/postgresql_example.py` - PostgreSQL-specific features

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

## 📊 Monitoring

### Health Check

When running in webhook mode, access:
- `GET /health` - Health check endpoint
- `GET /` - Basic info endpoint

### Logs

Logs are written to:
- Console (stdout)
- `bot.log` file

Log levels: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`

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