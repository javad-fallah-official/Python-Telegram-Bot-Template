# 🤖 Async Telegram Bot Template - Quick Start Guide

## 🚀 Getting Started

### 1. Setup Environment
```bash
# Copy environment template
copy .env.example .env

# Edit .env and add your bot token
# BOT_TOKEN=your_bot_token_here
```

### 2. Install Dependencies
```bash
# All dependencies are already installed via uv
# To add new packages:
uv add package_name
```

### 3. Run the Bot
```bash
# Run with default mode (from .env)
uv run python main.py

# Run in specific mode
uv run python main.py --mode polling
uv run python main.py --mode webhook

# Alternative entry points
uv run python cli.py --mode polling
uv run python run.py

# Get help
uv run python main.py --help
```

## 📁 Project Structure

```
├── main.py              # Main entry point (uses CLI)
├── cli.py               # Command-line interface
├── run.py               # Simple run script
├── bot.py               # Alternative entry point
├── core/                # Core infrastructure
│   ├── config.py        # Configuration management
│   ├── runner.py        # Unified bot runner
│   ├── database.py      # Async SQLite operations
│   ├── logger.py        # Enhanced logging system
│   └── middleware.py    # Rate limiting, admin checks
├── bot/                 # Bot application layer
│   ├── factory.py       # Bot creation and lifecycle
│   └── handlers/        # Command and message handlers
│       ├── commands.py  # Bot commands (/start, /help, etc.)
│       ├── errors.py    # Error handling
│       └── messages.py  # Message processing
├── services/            # Service implementations
│   ├── base.py          # Abstract service interface
│   ├── polling.py       # Polling service
│   └── webhook.py       # Webhook service (FastAPI)
├── utils/               # Utility modules
│   ├── logging_utils.py # Logging utilities and decorators
│   ├── formatters.py    # Text formatting utilities
│   ├── keyboards.py     # Keyboard builders
│   └── validators.py    # Input validation
├── examples/            # Example scripts
│   ├── logging_demo.py  # Logging features demo
│   └── logging_toggle_demo.py # Logging toggle demo
├── scripts/             # Utility scripts
│   └── analyze_logs.py  # Log analysis tool
├── .env.example         # Environment variables template
├── .env                 # Your environment variables (create this)
├── pyproject.toml       # Project dependencies
└── README.md            # Full documentation
```

## 🔧 Configuration Options

### Bot Modes
- **Polling Mode** (default): `BOT_MODE=polling`
- **Webhook Mode**: `BOT_MODE=webhook`

### Environment Variables
```env
# Required
BOT_TOKEN=your_bot_token_here

# Optional
BOT_USERNAME=your_bot_username
BOT_MODE=polling
DEBUG=false
LOG_LEVEL=INFO
LOGGING_ENABLED=true
ADMIN_USER_IDS=123456789,987654321
DATABASE_URL=bot.db

# Webhook specific (only needed for webhook mode)
WEBHOOK_URL=https://yourdomain.com
WEBHOOK_SECRET_TOKEN=your_secret_token
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8000
```

## 🛠️ Adding Custom Features

### 1. Add New Commands
```python
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes
from middleware import rate_limit, log_user_activity

@rate_limit(max_calls=5, window=60)
@log_user_activity
async def my_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Hello from my custom command!")

# Add to your bot
application.add_handler(CommandHandler("mycommand", my_command))
```

### 2. Use Database
```python
from database import Database

db = Database()
await db.connect()

# Save user
await db.save_user({
    'id': user.id,
    'username': user.username,
    'first_name': user.first_name
})

# Get user
user_data = await db.get_user(user_id)
```

### 3. Use Utilities
```python
from utils import formatter, keyboard_builder, validator

# Format text
safe_text = formatter.escape_markdown("Text with *special* chars")

# Create keyboard
keyboard = keyboard_builder.create_menu([
    [("Button 1", "callback_1")],
    [("Button 2", "callback_2")]
])

# Validate data
is_valid = validator.is_valid_email("test@example.com")
```

## 🔒 Security Features

- ✅ Rate limiting for commands
- ✅ Admin-only commands
- ✅ Input validation and sanitization
- ✅ Secure webhook with secret token
- ✅ User activity logging
- ✅ Error handling and logging

## 📊 Monitoring

### Health Check (Webhook Mode)
```bash
curl http://localhost:8000/health
```

### Logs
- Console output with colored formatting
- File logging to `bot.log`
- Configurable log levels

## 🚀 Deployment

### Local Development with Webhook
```bash
# Install ngrok for local webhook testing
# Set WEBHOOK_URL=https://your-ngrok-url.ngrok.io
BOT_MODE=webhook uv run python main.py
```

### Production Deployment
1. Set up your server with Python 3.13+
2. Configure environment variables
3. Use a process manager (systemd, supervisor, etc.)
4. Set up reverse proxy (nginx) for webhook mode

## 🧪 Testing

```bash
# Run all tests
uv run python test_setup.py

# Test specific functionality
uv run python -c "from utils import validator; print(validator.is_valid_email('test@example.com'))"
```

## 📦 Package Management

```bash
# Add new dependencies
uv add requests
uv add --dev pytest

# Update dependencies
uv lock --upgrade

# Install from lock file
uv sync
```

## 🎯 Next Steps

1. **Customize handlers.py** - Add your bot's specific commands
2. **Extend database.py** - Add tables for your bot's data
3. **Configure middleware.py** - Adjust rate limits and security
4. **Update utils.py** - Add utility functions for your use case
5. **Set up monitoring** - Add health checks and metrics
6. **Deploy** - Choose your deployment strategy

## 🆘 Troubleshooting

### Common Issues

1. **Import errors**: Make sure to use `uv run python` to activate the virtual environment
2. **BOT_TOKEN errors**: Ensure your `.env` file has the correct token
3. **Webhook issues**: Check that your WEBHOOK_URL is accessible from the internet
4. **Database errors**: Ensure the database file is writable

### Getting Help

- Check the logs in `bot.log`
- Run `uv run python test_setup.py` to verify setup
- Review the example bot in `example_bot.py`
- Check the full documentation in `README.md`

---

**Happy Bot Building! 🤖✨**