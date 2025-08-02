# 🎯 Handlers API Reference

This document provides a comprehensive API reference for the bot's handler system, including commands, messages, callbacks, and error handlers.

## Table of Contents

- [Handler Architecture](#handler-architecture)
- [Command Handlers](#command-handlers)
- [Message Handlers](#message-handlers)
- [Callback Query Handlers](#callback-query-handlers)
- [Error Handlers](#error-handlers)
- [Handler Registration](#handler-registration)
- [Middleware Integration](#middleware-integration)
- [Custom Handlers](#custom-handlers)

## Handler Architecture

### Base Handler Structure

All handlers in the bot follow the aiogram v3.x pattern:

```python
from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, Text

# Create router for organizing handlers
router = Router()

@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    """Handle /start command."""
    await message.answer("Hello!")
```

### Handler Types

| Type | Description | Use Case |
|------|-------------|----------|
| **Command** | `/command` patterns | Bot commands |
| **Message** | Text/media messages | Content processing |
| **Callback** | Inline button clicks | Interactive responses |
| **Error** | Exception handling | Error management |

## Command Handlers

### Basic Commands

#### `/start` Command
```python
@router.message(Command("start"))
async def start_command(message: Message) -> None:
    """
    Handle the /start command.
    
    Sends welcome message and registers user if new.
    
    Args:
        message: The incoming message object
    """
    user = message.from_user
    
    # Register user in database
    await database.save_user({
        'id': user.id,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name
    })
    
    # Send welcome message
    welcome_text = f"Hello {user.first_name}! 👋\n\nWelcome to the bot!"
    await message.answer(welcome_text)
```

#### `/help` Command
```python
@router.message(Command("help"))
async def help_command(message: Message) -> None:
    """
    Display available commands and usage information.
    
    Args:
        message: The incoming message object
    """
    help_text = """
🤖 **Available Commands:**

/start - Start the bot
/help - Show this help message
/profile - View your profile
/settings - Bot settings
/stats - Usage statistics

Need more help? Contact support!
    """
    await message.answer(help_text, parse_mode="Markdown")
```

### Commands with Arguments

#### `/profile` Command
```python
@router.message(Command("profile"))
async def profile_command(message: Message) -> None:
    """
    Display user profile information.
    
    Args:
        message: The incoming message object
    """
    user_id = message.from_user.id
    
    # Get user data from database
    user_data = await database.get_user(user_id)
    if not user_data:
        await message.answer("❌ User not found. Please use /start first.")
        return
    
    # Format profile information
    profile_text = f"""
👤 **Your Profile**

**Name:** {user_data.get('first_name', 'N/A')}
**Username:** @{user_data.get('username', 'N/A')}
**User ID:** `{user_data['id']}`
**Joined:** {user_data.get('created_at', 'Unknown')}
**Commands Used:** {user_data.get('command_count', 0)}
    """
    
    await message.answer(profile_text, parse_mode="Markdown")
```

#### `/search` Command with Arguments
```python
@router.message(Command("search"))
async def search_command(message: Message, command: CommandObject) -> None:
    """
    Search for content with given query.
    
    Usage: /search <query>
    
    Args:
        message: The incoming message object
        command: Command object containing arguments
    """
    # Extract search query
    query = command.args
    if not query:
        await message.answer("❌ Please provide a search query.\n\nUsage: `/search <query>`")
        return
    
    # Perform search (example implementation)
    try:
        results = await search_service.search(query)
        
        if not results:
            await message.answer(f"🔍 No results found for: `{query}`")
            return
        
        # Format results
        response = f"🔍 **Search Results for:** `{query}`\n\n"
        for i, result in enumerate(results[:5], 1):
            response += f"{i}. {result['title']}\n"
        
        await message.answer(response, parse_mode="Markdown")
        
    except Exception as e:
        logger.error(f"Search error: {e}")
        await message.answer("❌ Search failed. Please try again later.")
```

### Admin Commands

#### Admin-Only Decorator
```python
from functools import wraps
from core.config import Config

def admin_required(func):
    """Decorator to restrict commands to admin users."""
    @wraps(func)
    async def wrapper(message: Message, *args, **kwargs):
        user_id = message.from_user.id
        if user_id not in Config.ADMIN_IDS:
            await message.answer("❌ This command is only available to administrators.")
            return
        return await func(message, *args, **kwargs)
    return wrapper

@router.message(Command("stats"))
@admin_required
async def admin_stats_command(message: Message) -> None:
    """
    Display bot statistics (admin only).
    
    Args:
        message: The incoming message object
    """
    stats = await database.get_bot_statistics()
    
    stats_text = f"""
📊 **Bot Statistics**

**Total Users:** {stats['total_users']}
**Active Users (24h):** {stats['active_users_24h']}
**Commands Today:** {stats['commands_today']}
**Database Size:** {stats['db_size']}
**Uptime:** {stats['uptime']}
    """
    
    await message.answer(stats_text, parse_mode="Markdown")
```

## Message Handlers

### Text Message Handlers

#### Echo Handler
```python
@router.message(F.text)
async def echo_handler(message: Message) -> None:
    """
    Echo back user messages (fallback handler).
    
    Args:
        message: The incoming message object
    """
    # Log user activity
    await database.log_activity(
        user_id=message.from_user.id,
        activity_type="message_sent",
        details={"text_length": len(message.text)}
    )
    
    # Echo the message
    await message.answer(f"You said: {message.text}")
```

#### Keyword Response Handler
```python
@router.message(F.text.contains("hello"))
async def hello_response(message: Message) -> None:
    """
    Respond to messages containing 'hello'.
    
    Args:
        message: The incoming message object
    """
    responses = [
        "Hello there! 👋",
        "Hi! How can I help you?",
        "Hey! Nice to see you!",
        "Hello! What's up?"
    ]
    
    response = random.choice(responses)
    await message.answer(response)
```

### Media Message Handlers

#### Photo Handler
```python
@router.message(F.photo)
async def photo_handler(message: Message) -> None:
    """
    Handle photo messages.
    
    Args:
        message: The incoming message object
    """
    # Get the largest photo size
    photo = message.photo[-1]
    
    # Log photo received
    await database.log_activity(
        user_id=message.from_user.id,
        activity_type="photo_sent",
        details={
            "file_id": photo.file_id,
            "file_size": photo.file_size
        }
    )
    
    await message.answer(
        f"📸 Nice photo! File size: {photo.file_size} bytes"
    )
```

#### Document Handler
```python
@router.message(F.document)
async def document_handler(message: Message) -> None:
    """
    Handle document messages.
    
    Args:
        message: The incoming message object
    """
    document = message.document
    
    # Check file size limit (10MB)
    if document.file_size > 10 * 1024 * 1024:
        await message.answer("❌ File too large. Maximum size is 10MB.")
        return
    
    # Process document
    await message.answer(
        f"📄 Document received: `{document.file_name}`\n"
        f"Size: {document.file_size} bytes\n"
        f"Type: {document.mime_type}"
    )
```

## Callback Query Handlers

### Basic Callback Handlers

#### Simple Callback
```python
@router.callback_query(F.data == "button_clicked")
async def button_callback(callback: CallbackQuery) -> None:
    """
    Handle button click callback.
    
    Args:
        callback: The callback query object
    """
    await callback.answer("Button clicked!")
    await callback.message.edit_text("✅ Button was clicked!")
```

#### Parameterized Callbacks
```python
@router.callback_query(F.data.startswith("user_"))
async def user_action_callback(callback: CallbackQuery) -> None:
    """
    Handle user action callbacks.
    
    Callback data format: user_{action}_{user_id}
    
    Args:
        callback: The callback query object
    """
    # Parse callback data
    parts = callback.data.split("_")
    if len(parts) != 3:
        await callback.answer("❌ Invalid callback data")
        return
    
    action = parts[1]
    user_id = int(parts[2])
    
    if action == "ban":
        # Ban user logic
        await ban_user(user_id)
        await callback.answer(f"User {user_id} banned")
        
    elif action == "unban":
        # Unban user logic
        await unban_user(user_id)
        await callback.answer(f"User {user_id} unbanned")
        
    else:
        await callback.answer("❌ Unknown action")
```

### Inline Keyboard Handlers

#### Settings Menu
```python
@router.callback_query(F.data == "settings")
async def settings_callback(callback: CallbackQuery) -> None:
    """
    Display settings menu.
    
    Args:
        callback: The callback query object
    """
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔔 Notifications", callback_data="setting_notifications"),
            InlineKeyboardButton(text="🌐 Language", callback_data="setting_language")
        ],
        [
            InlineKeyboardButton(text="🎨 Theme", callback_data="setting_theme"),
            InlineKeyboardButton(text="🔒 Privacy", callback_data="setting_privacy")
        ],
        [
            InlineKeyboardButton(text="⬅️ Back", callback_data="main_menu")
        ]
    ])
    
    await callback.message.edit_text(
        "⚙️ **Settings**\n\nChoose a setting to configure:",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
```

#### Pagination Handler
```python
@router.callback_query(F.data.startswith("page_"))
async def pagination_callback(callback: CallbackQuery) -> None:
    """
    Handle pagination callbacks.
    
    Args:
        callback: The callback query object
    """
    page = int(callback.data.split("_")[1])
    
    # Get data for the page
    items = await get_paginated_data(page)
    
    # Create pagination keyboard
    keyboard = create_pagination_keyboard(page, total_pages=10)
    
    # Update message
    text = f"📄 **Page {page}**\n\n"
    for item in items:
        text += f"• {item}\n"
    
    await callback.message.edit_text(
        text,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    
    await callback.answer()
```

## Error Handlers

### Global Error Handler

```python
@router.error()
async def error_handler(event: ErrorEvent) -> None:
    """
    Global error handler for all unhandled exceptions.
    
    Args:
        event: The error event object
    """
    exception = event.exception
    update = event.update
    
    # Log the error
    logger.error(
        f"Error in update {update.update_id}: {exception}",
        exc_info=True
    )
    
    # Try to send error message to user
    try:
        if update.message:
            await update.message.answer(
                "❌ An error occurred while processing your request. "
                "Please try again later."
            )
        elif update.callback_query:
            await update.callback_query.answer(
                "❌ An error occurred. Please try again.",
                show_alert=True
            )
    except Exception as e:
        logger.error(f"Failed to send error message: {e}")
    
    # Report critical errors to admin
    if isinstance(exception, CriticalError):
        await notify_admin_of_error(exception, update)
```

### Specific Error Handlers

```python
@router.error(ExceptionTypeFilter(TelegramBadRequest))
async def telegram_error_handler(event: ErrorEvent) -> None:
    """
    Handle Telegram API errors.
    
    Args:
        event: The error event object
    """
    exception = event.exception
    
    if "message is not modified" in str(exception):
        # Ignore message not modified errors
        return
    
    if "chat not found" in str(exception):
        # Handle chat not found
        logger.warning(f"Chat not found: {exception}")
        return
    
    # Log other Telegram errors
    logger.error(f"Telegram API error: {exception}")
```

## Handler Registration

### Automatic Registration

```python
# bot/handlers/registry.py
from aiogram import Dispatcher
from . import commands, messages, callbacks, errors

def register_handlers(dp: Dispatcher) -> None:
    """
    Register all handlers with the dispatcher.
    
    Args:
        dp: The dispatcher instance
    """
    # Register routers in order of priority
    dp.include_router(errors.router)      # Error handlers first
    dp.include_router(commands.router)    # Commands
    dp.include_router(callbacks.router)   # Callbacks
    dp.include_router(messages.router)    # Messages last (fallback)
```

### Manual Registration

```python
# Alternative manual registration
def register_handlers_manual(dp: Dispatcher) -> None:
    """
    Manually register specific handlers.
    
    Args:
        dp: The dispatcher instance
    """
    # Register specific handlers
    dp.message.register(start_command, Command("start"))
    dp.message.register(help_command, Command("help"))
    dp.callback_query.register(button_callback, F.data == "button")
    dp.error.register(error_handler)
```

## Middleware Integration

### Handler Middleware

```python
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject

class LoggingMiddleware(BaseMiddleware):
    """Middleware to log all handler calls."""
    
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Process handler call with logging.
        
        Args:
            handler: The handler function
            event: The Telegram event
            data: Handler data
            
        Returns:
            Handler result
        """
        start_time = time.time()
        
        try:
            result = await handler(event, data)
            duration = time.time() - start_time
            
            logger.info(
                f"Handler {handler.__name__} completed in {duration:.3f}s"
            )
            
            return result
            
        except Exception as e:
            duration = time.time() - start_time
            
            logger.error(
                f"Handler {handler.__name__} failed after {duration:.3f}s: {e}"
            )
            
            raise

# Register middleware
dp.message.middleware(LoggingMiddleware())
dp.callback_query.middleware(LoggingMiddleware())
```

### Authentication Middleware

```python
class AuthMiddleware(BaseMiddleware):
    """Middleware to handle user authentication."""
    
    async def __call__(
        self,
        handler: Callable,
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        """
        Check user authentication before handler execution.
        
        Args:
            handler: The handler function
            event: The Telegram event
            data: Handler data
            
        Returns:
            Handler result or None if unauthorized
        """
        # Get user from event
        user = None
        if hasattr(event, 'from_user'):
            user = event.from_user
        
        if not user:
            return await handler(event, data)
        
        # Check if user is banned
        if await database.is_user_banned(user.id):
            if hasattr(event, 'answer'):
                await event.answer("❌ You are banned from using this bot.")
            return
        
        # Update user activity
        await database.update_user_activity(user.id)
        
        # Add user to handler data
        data['user'] = user
        
        return await handler(event, data)
```

## Custom Handlers

### State Machine Handler

```python
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

class RegistrationStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_email = State()

@router.message(Command("register"))
async def start_registration(message: Message, state: FSMContext) -> None:
    """
    Start user registration process.
    
    Args:
        message: The incoming message
        state: FSM context
    """
    await state.set_state(RegistrationStates.waiting_for_name)
    await message.answer("👤 Please enter your full name:")

@router.message(RegistrationStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext) -> None:
    """
    Process user name input.
    
    Args:
        message: The incoming message
        state: FSM context
    """
    await state.update_data(name=message.text)
    await state.set_state(RegistrationStates.waiting_for_age)
    await message.answer("🎂 Please enter your age:")

@router.message(RegistrationStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext) -> None:
    """
    Process user age input.
    
    Args:
        message: The incoming message
        state: FSM context
    """
    try:
        age = int(message.text)
        if age < 13 or age > 120:
            await message.answer("❌ Please enter a valid age (13-120):")
            return
        
        await state.update_data(age=age)
        await state.set_state(RegistrationStates.waiting_for_email)
        await message.answer("📧 Please enter your email address:")
        
    except ValueError:
        await message.answer("❌ Please enter a valid number:")
```

### Dynamic Handler Registration

```python
class DynamicHandlerManager:
    """Manager for dynamic handler registration."""
    
    def __init__(self, dp: Dispatcher):
        self.dp = dp
        self.registered_handlers = {}
    
    async def register_command_handler(
        self, 
        command: str, 
        handler_func: Callable,
        description: str = ""
    ) -> None:
        """
        Dynamically register a command handler.
        
        Args:
            command: Command name (without /)
            handler_func: Handler function
            description: Command description
        """
        # Create router for the handler
        router = Router()
        router.message.register(handler_func, Command(command))
        
        # Include router in dispatcher
        self.dp.include_router(router)
        
        # Store handler info
        self.registered_handlers[command] = {
            'handler': handler_func,
            'description': description,
            'router': router
        }
    
    async def unregister_command_handler(self, command: str) -> bool:
        """
        Unregister a command handler.
        
        Args:
            command: Command name to unregister
            
        Returns:
            True if handler was unregistered, False if not found
        """
        if command not in self.registered_handlers:
            return False
        
        # Remove router (Note: aiogram doesn't support router removal)
        # This is a limitation of the current aiogram version
        del self.registered_handlers[command]
        return True
    
    def get_registered_commands(self) -> Dict[str, Dict]:
        """
        Get all registered commands.
        
        Returns:
            Dictionary of registered commands and their info
        """
        return self.registered_handlers.copy()
```

## Best Practices

### 1. Handler Organization
- Group related handlers in separate modules
- Use routers to organize handlers logically
- Keep handlers focused on single responsibilities

### 2. Error Handling
- Always handle exceptions in handlers
- Provide meaningful error messages to users
- Log errors for debugging

### 3. Performance
- Use async/await properly
- Avoid blocking operations in handlers
- Implement rate limiting for resource-intensive operations

### 4. Security
- Validate all user inputs
- Implement proper authentication
- Use admin-only decorators for sensitive commands

### 5. Testing
- Write unit tests for all handlers
- Mock external dependencies
- Test error conditions

---

*For more examples and advanced patterns, see the [handlers directory](../../bot/handlers/) in the source code.*