# 🎯 Bot Handlers Guide

This guide covers how to create, register, and manage bot handlers for commands, messages, and other Telegram events using the aiogram framework.

## Overview

### Handler Types
- **Command Handlers** - Handle `/command` messages
- **Message Handlers** - Handle text messages and media
- **Callback Query Handlers** - Handle inline keyboard callbacks
- **Error Handlers** - Handle exceptions and errors

### Handler Architecture
- **Modular Design** - Handlers organized in separate modules
- **Automatic Registration** - Centralized handler registration
- **Middleware Support** - Rate limiting, admin controls, logging
- **Type Safety** - Full type hints and validation

## Command Handlers

### Basic Command Handler

```python
from aiogram.types import Message
from aiogram.filters import Command

async def start_command(message: Message) -> None:
    """Handle /start command."""
    user = message.from_user
    await message.answer(f"Hello {user.first_name}! Welcome to the bot.")

async def help_command(message: Message) -> None:
    """Handle /help command."""
    help_text = """
🤖 **Bot Commands:**

/start - Start the bot
/help - Show this help message
/info - Get your user information
/settings - Bot settings
    """
    await message.answer(help_text, parse_mode="Markdown")
```

### Command with Arguments

```python
async def echo_command(message: Message) -> None:
    """Handle /echo command with arguments."""
    # Get command arguments
    args = message.text.split()[1:] if message.text else []
    
    if not args:
        await message.answer("Usage: /echo <text to echo>")
        return
    
    echo_text = " ".join(args)
    await message.answer(f"Echo: {echo_text}")

async def user_command(message: Message) -> None:
    """Handle /user command with user ID argument."""
    args = message.text.split()[1:] if message.text else []
    
    if not args:
        await message.answer("Usage: /user <user_id>")
        return
    
    try:
        user_id = int(args[0])
        # Get user from database
        from core.db_factory import DatabaseFactory
        db = DatabaseFactory.create_database()
        user = await db.get_user(user_id)
        
        if user:
            await message.answer(f"User: {user['username']} ({user['first_name']})")
        else:
            await message.answer("User not found.")
    except ValueError:
        await message.answer("Invalid user ID. Please provide a number.")
```

### Admin-Only Commands

```python
from core.middleware import admin_required

@admin_required
async def admin_stats_command(message: Message) -> None:
    """Handle /stats command (admin only)."""
    from core.db_factory import DatabaseFactory
    db = DatabaseFactory.create_database()
    
    stats = await db.get_database_stats()
    stats_text = f"""
📊 **Bot Statistics:**

👥 Total Users: {stats['user_count']}
📈 Active Users (7d): {stats['active_users_7d']}
💾 Database Size: {stats['size_mb']} MB
    """
    await message.answer(stats_text, parse_mode="Markdown")

@admin_required
async def broadcast_command(message: Message) -> None:
    """Handle /broadcast command (admin only)."""
    args = message.text.split()[1:] if message.text else []
    
    if not args:
        await message.answer("Usage: /broadcast <message>")
        return
    
    broadcast_text = " ".join(args)
    
    # Get all users and send message
    from core.db_factory import DatabaseFactory
    db = DatabaseFactory.create_database()
    users = await db.get_all_users()
    
    sent_count = 0
    for user in users:
        try:
            await message.bot.send_message(user['id'], broadcast_text)
            sent_count += 1
        except Exception:
            # User blocked bot or other error
            continue
    
    await message.answer(f"Broadcast sent to {sent_count} users.")
```

## Message Handlers

### Text Message Handler

```python
from aiogram.types import Message
from aiogram.filters import Text

async def handle_text_message(message: Message) -> None:
    """Handle regular text messages."""
    user = message.from_user
    text = message.text
    
    # Log user activity
    from core.db_factory import DatabaseFactory
    db = DatabaseFactory.create_database()
    await db.log_activity(user.id, 'message_sent', text[:100])
    
    # Simple echo response
    await message.answer(f"You said: {text}")

async def handle_greeting(message: Message) -> None:
    """Handle greeting messages."""
    greetings = ["hello", "hi", "hey", "good morning", "good evening"]
    
    if any(greeting in message.text.lower() for greeting in greetings):
        await message.answer("Hello! How can I help you today?")
```

### Media Message Handlers

```python
from aiogram.types import Message
from aiogram.enums import ContentType

async def handle_photo(message: Message) -> None:
    """Handle photo messages."""
    photo = message.photo[-1]  # Get highest resolution
    file_info = await message.bot.get_file(photo.file_id)
    
    await message.answer(
        f"Nice photo! File size: {file_info.file_size} bytes"
    )

async def handle_document(message: Message) -> None:
    """Handle document messages."""
    document = message.document
    
    # Check file size limit (20MB)
    if document.file_size > 20 * 1024 * 1024:
        await message.answer("File too large. Maximum size is 20MB.")
        return
    
    await message.answer(
        f"Document received: {document.file_name}\n"
        f"Size: {document.file_size} bytes\n"
        f"Type: {document.mime_type}"
    )

async def handle_voice(message: Message) -> None:
    """Handle voice messages."""
    voice = message.voice
    duration = voice.duration
    
    await message.answer(
        f"Voice message received! Duration: {duration} seconds"
    )
```

## Callback Query Handlers

### Basic Callback Handler

```python
from aiogram.types import CallbackQuery
from aiogram.filters.callback_data import CallbackData

class MenuCallback(CallbackData, prefix="menu"):
    action: str
    item_id: int

async def handle_menu_callback(callback: CallbackQuery, callback_data: MenuCallback) -> None:
    """Handle menu callback queries."""
    action = callback_data.action
    item_id = callback_data.item_id
    
    if action == "select":
        await callback.message.edit_text(f"You selected item {item_id}")
    elif action == "delete":
        await callback.message.edit_text(f"Item {item_id} deleted")
    
    await callback.answer()  # Acknowledge the callback

async def handle_simple_callback(callback: CallbackQuery) -> None:
    """Handle simple callback queries."""
    data = callback.data
    
    if data == "button_1":
        await callback.message.edit_text("Button 1 pressed!")
    elif data == "button_2":
        await callback.message.edit_text("Button 2 pressed!")
    
    await callback.answer("Button pressed!")
```

### Inline Keyboard with Callbacks

```python
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

async def show_menu_command(message: Message) -> None:
    """Show interactive menu."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Option 1", 
                callback_data=MenuCallback(action="select", item_id=1).pack()
            ),
            InlineKeyboardButton(
                text="Option 2", 
                callback_data=MenuCallback(action="select", item_id=2).pack()
            )
        ],
        [
            InlineKeyboardButton(
                text="Delete Item", 
                callback_data=MenuCallback(action="delete", item_id=1).pack()
            )
        ]
    ])
    
    await message.answer("Choose an option:", reply_markup=keyboard)
```

## Error Handlers

### Global Error Handler

```python
from aiogram.types import ErrorEvent
import logging

logger = logging.getLogger(__name__)

async def error_handler(event: ErrorEvent) -> None:
    """Handle all bot errors."""
    exception = event.exception
    update = event.update
    
    # Log error details
    logger.error(
        f"Error occurred: {exception}\n"
        f"Update: {update}\n"
        f"User: {update.message.from_user.id if update.message else 'Unknown'}"
    )
    
    # Send error message to user
    if update.message:
        await update.message.answer(
            "Sorry, an error occurred. Please try again later."
        )
    
    # Notify admins about critical errors
    if isinstance(exception, CriticalError):
        await notify_admins(f"Critical error: {exception}")

async def timeout_handler(event: ErrorEvent) -> None:
    """Handle timeout errors."""
    if "timeout" in str(event.exception).lower():
        if event.update.message:
            await event.update.message.answer(
                "Request timed out. Please try again."
            )
```

### Specific Error Handlers

```python
from aiogram.exceptions import TelegramBadRequest, TelegramRetryAfter

async def handle_bad_request(event: ErrorEvent) -> None:
    """Handle bad request errors."""
    if isinstance(event.exception, TelegramBadRequest):
        logger.warning(f"Bad request: {event.exception}")
        
        if event.update.message:
            await event.update.message.answer(
                "Invalid request. Please check your input."
            )

async def handle_retry_after(event: ErrorEvent) -> None:
    """Handle rate limit errors."""
    if isinstance(event.exception, TelegramRetryAfter):
        retry_after = event.exception.retry_after
        logger.warning(f"Rate limited. Retry after {retry_after} seconds")
        
        if event.update.message:
            await event.update.message.answer(
                f"Too many requests. Please wait {retry_after} seconds."
            )
```

## Handler Registration

### Automatic Registration

```python
# bot/handlers/registry.py
from aiogram import Dispatcher
from aiogram.filters import Command, Text

from .commands import (
    start_command, help_command, echo_command,
    admin_stats_command, broadcast_command
)
from .messages import handle_text_message, handle_photo, handle_document
from .callbacks import handle_menu_callback, handle_simple_callback
from .errors import error_handler, timeout_handler

def register_handlers(dp: Dispatcher) -> None:
    """Register all handlers with the dispatcher."""
    
    # Command handlers
    dp.message.register(start_command, Command("start"))
    dp.message.register(help_command, Command("help"))
    dp.message.register(echo_command, Command("echo"))
    dp.message.register(admin_stats_command, Command("stats"))
    dp.message.register(broadcast_command, Command("broadcast"))
    
    # Message handlers
    dp.message.register(handle_photo, F.photo)
    dp.message.register(handle_document, F.document)
    dp.message.register(handle_text_message, Text())
    
    # Callback handlers
    dp.callback_query.register(handle_menu_callback, MenuCallback.filter())
    dp.callback_query.register(handle_simple_callback)
    
    # Error handlers
    dp.error.register(error_handler)
    dp.error.register(timeout_handler)
```

### Manual Registration

```python
from aiogram import Dispatcher
from aiogram.filters import Command

# Create dispatcher
dp = Dispatcher()

# Register individual handlers
dp.message.register(start_command, Command("start"))
dp.message.register(help_command, Command("help"))

# Register with filters
dp.message.register(
    admin_command, 
    Command("admin"),
    lambda message: message.from_user.id in ADMIN_IDS
)
```

## Middleware Integration

### Using Middleware Decorators

```python
from core.middleware import rate_limit, log_user_activity, admin_required

@rate_limit(max_calls=5, window=60)
@log_user_activity
async def limited_command(message: Message) -> None:
    """Command with rate limiting and activity logging."""
    await message.answer("This command is rate limited!")

@admin_required
@log_user_activity
async def admin_only_command(message: Message) -> None:
    """Admin-only command with logging."""
    await message.answer("Admin command executed!")
```

### Custom Middleware

```python
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class UserTrackingMiddleware(BaseMiddleware):
    """Track user interactions."""
    
    async def __call__(
        self,
        handler,
        event: TelegramObject,
        data: dict
    ) -> any:
        # Pre-processing
        if hasattr(event, 'from_user'):
            user = event.from_user
            # Save/update user in database
            from core.db_factory import DatabaseFactory
            db = DatabaseFactory.create_database()
            await db.save_user({
                'id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name
            })
        
        # Call handler
        result = await handler(event, data)
        
        # Post-processing
        # Log interaction, update statistics, etc.
        
        return result

# Register middleware
dp.message.middleware(UserTrackingMiddleware())
```

## Advanced Handler Patterns

### State Machine Handlers

```python
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class UserRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_email = State()

async def start_registration(message: Message, state: FSMContext) -> None:
    """Start user registration process."""
    await state.set_state(UserRegistration.waiting_for_name)
    await message.answer("Please enter your name:")

async def process_name(message: Message, state: FSMContext) -> None:
    """Process user name input."""
    await state.update_data(name=message.text)
    await state.set_state(UserRegistration.waiting_for_age)
    await message.answer("Please enter your age:")

async def process_age(message: Message, state: FSMContext) -> None:
    """Process user age input."""
    try:
        age = int(message.text)
        await state.update_data(age=age)
        await state.set_state(UserRegistration.waiting_for_email)
        await message.answer("Please enter your email:")
    except ValueError:
        await message.answer("Please enter a valid age (number):")
```

### Dynamic Handler Registration

```python
def create_dynamic_handler(command_name: str, response: str):
    """Create a dynamic command handler."""
    async def handler(message: Message) -> None:
        await message.answer(response)
    
    return handler

# Register dynamic handlers
dynamic_commands = {
    "ping": "Pong!",
    "version": "Bot v1.0.0",
    "status": "Bot is running!"
}

for cmd, response in dynamic_commands.items():
    handler = create_dynamic_handler(cmd, response)
    dp.message.register(handler, Command(cmd))
```

## Testing Handlers

### Unit Testing

```python
import pytest
from unittest.mock import AsyncMock
from aiogram.types import Message, User

@pytest.fixture
def mock_message():
    """Create mock message for testing."""
    message = AsyncMock(spec=Message)
    message.from_user = User(id=123, is_bot=False, first_name="Test")
    message.text = "/start"
    return message

async def test_start_command(mock_message):
    """Test start command handler."""
    await start_command(mock_message)
    
    mock_message.answer.assert_called_once()
    args = mock_message.answer.call_args[0]
    assert "Hello Test" in args[0]

async def test_echo_command(mock_message):
    """Test echo command with arguments."""
    mock_message.text = "/echo Hello World"
    
    await echo_command(mock_message)
    
    mock_message.answer.assert_called_once_with("Echo: Hello World")
```

### Integration Testing

```python
async def test_command_flow():
    """Test complete command flow."""
    from bot.factory import BotFactory
    
    bot = BotFactory.create_bot()
dp = BotFactory.create_dispatcher()
    
    # Register handlers
    from bot.handlers.registry import register_handlers
    register_handlers(dp)
    
    # Simulate message
    mock_update = create_mock_update("/start")
    await dp.feed_update(bot, mock_update)
    
    # Verify response
    # ... test assertions
```

## Best Practices

### 1. Handler Organization
- Group related handlers in modules
- Use descriptive function names
- Add comprehensive docstrings
- Implement proper error handling

### 2. Performance
- Use async/await properly
- Avoid blocking operations
- Implement rate limiting
- Cache frequently accessed data

### 3. Security
- Validate user input
- Implement admin checks
- Log security events
- Handle sensitive data properly

### 4. User Experience
- Provide clear error messages
- Use inline keyboards for interactions
- Implement progress indicators
- Handle edge cases gracefully

## Examples

See the [examples/](../../examples/) directory for:
- `example_bot.py` - Complete bot with various handlers
- `advanced_handlers.py` - Advanced handler patterns
- `state_machine_example.py` - State machine implementation

---

*Need help with handlers? Check the [aiogram documentation](https://docs.aiogram.dev/) or review our [examples](../../examples/).*