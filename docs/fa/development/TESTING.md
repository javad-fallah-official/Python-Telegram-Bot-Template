# 🧪 راهنمای تست‌نویسی

> **تست کامل ربات تلگرام با pytest و aiogram**

## 🎯 درباره تست‌ها

تست‌نویسی بخش حیاتی توسعه ربات است که اطمینان از عملکرد صحیح کد را فراهم می‌کند. این راهنما شامل تمام جنبه‌های تست‌نویسی برای ربات تلگرام است.

## 🏗️ ساختار تست‌ها

### ساختار فایل‌ها
```
tests/
├── __init__.py
├── conftest.py              # تنظیمات pytest
├── utils.py                 # ابزارهای کمکی تست
├── test_bot.py             # تست‌های اصلی ربات
├── test_handlers.py        # تست هندلرها
├── test_database.py        # تست پایگاه داده
├── test_config.py          # تست تنظیمات
├── integration/            # تست‌های یکپارچگی
│   ├── __init__.py
│   ├── test_bot_flow.py    # تست جریان کامل
│   └── test_webhook.py     # تست webhook
└── fixtures/               # داده‌های تست
    ├── users.json
    ├── messages.json
    └── responses.json
```

## ⚙️ تنظیمات pytest

### فایل conftest.py
```python
# tests/conftest.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from aiogram import Bot, Dispatcher
from aiogram.types import User, Chat, Message
from core.config import Config
from core.database import Database

@pytest.fixture(scope="session")
def event_loop():
    """ایجاد event loop برای تست‌های async"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def config():
    """تنظیمات تست"""
    return Config(
        BOT_TOKEN="123456:TEST_TOKEN",
        DATABASE_TYPE="sqlite",
        DATABASE_URL="sqlite:///:memory:",
        DEBUG=True
    )

@pytest.fixture
def test_db():
    """پایگاه داده تست"""
    db = Database(database_url="sqlite:///:memory:")
    db.create_tables()
    yield db
    db.close()

@pytest.fixture
def mock_bot():
    """Mock bot برای تست"""
    bot = AsyncMock(spec=Bot)
    bot.id = 123456789
    bot.username = "test_bot"
    bot.first_name = "Test Bot"
    return bot

@pytest.fixture
def mock_dispatcher():
    """Mock dispatcher برای تست"""
    return MagicMock(spec=Dispatcher)

@pytest.fixture
def test_user():
    """کاربر تست"""
    return User(
        id=123456789,
        is_bot=False,
        first_name="احمد",
        last_name="محمدی",
        username="ahmad_test",
        language_code="fa"
    )

@pytest.fixture
def test_chat():
    """چت تست"""
    return Chat(
        id=123456789,
        type="private",
        first_name="احمد",
        last_name="محمدی",
        username="ahmad_test"
    )

@pytest.fixture
def test_message(test_user, test_chat):
    """پیام تست"""
    message = AsyncMock(spec=Message)
    message.message_id = 1
    message.from_user = test_user
    message.chat = test_chat
    message.text = "سلام"
    message.date = pytest.approx(1234567890)
    return message
```

### فایل pytest.ini
```ini
# pytest.ini
[tool:pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = 
    -v
    --tb=short
    --strict-markers
    --disable-warnings
    --cov=.
    --cov-report=html
    --cov-report=term-missing
markers =
    slow: marks tests as slow
    integration: marks tests as integration tests
    unit: marks tests as unit tests
    asyncio: marks tests as async
```

## 🤖 تست BotFactory

### تست ایجاد ربات
```python
# tests/test_bot.py
import pytest
from bot.factory import BotFactory
from core.config import Config

class TestBotFactory:
    """تست‌های BotFactory"""
    
    def test_create_bot(self, config):
        """تست ایجاد ربات"""
        bot = BotFactory.create_bot(config)
        
        assert bot is not None
        assert hasattr(bot, 'token')
        assert bot.token == config.BOT_TOKEN
    
    def test_create_dispatcher(self):
        """تست ایجاد dispatcher"""
        dp = BotFactory.create_dispatcher()
        
        assert dp is not None
        assert hasattr(dp, 'include_router')
    
    @pytest.mark.asyncio
    async def test_initialize_bot(self, mock_bot, config):
        """تست مقداردهی اولیه ربات"""
        await BotFactory.initialize_bot(mock_bot, config)
        
        # بررسی فراخوانی متدهای مقداردهی
        mock_bot.set_my_commands.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_shutdown_bot(self, mock_bot):
        """تست خاموش کردن ربات"""
        await BotFactory.shutdown_bot(mock_bot)
        
        # بررسی فراخوانی close
        mock_bot.session.close.assert_called_once()
```

## 🎛️ تست هندلرها

### تست دستورات
```python
# tests/test_handlers.py
import pytest
from unittest.mock import AsyncMock
from bot.handlers.commands.start import start_command
from bot.handlers.commands.help import help_command

class TestCommandHandlers:
    """تست هندلرهای دستورات"""
    
    @pytest.mark.asyncio
    async def test_start_command(self, test_message):
        """تست دستور /start"""
        await start_command(test_message)
        
        # بررسی فراخوانی answer
        test_message.answer.assert_called_once()
        
        # بررسی محتوای پاسخ
        args = test_message.answer.call_args[0]
        assert "خوش آمدید" in args[0]
        assert "شروع" in args[0]
    
    @pytest.mark.asyncio
    async def test_help_command(self, test_message):
        """تست دستور /help"""
        await help_command(test_message)
        
        test_message.answer.assert_called_once()
        args = test_message.answer.call_args[0]
        assert "راهنما" in args[0]
        assert "دستورات" in args[0]
    
    @pytest.mark.asyncio
    async def test_admin_command_unauthorized(self, test_message):
        """تست دستور مدیریتی بدون مجوز"""
        from bot.handlers.commands.admin import admin_command
        
        await admin_command(test_message)
        
        test_message.answer.assert_called_once()
        args = test_message.answer.call_args[0]
        assert "مجوز" in args[0] or "دسترسی" in args[0]
    
    @pytest.mark.asyncio
    async def test_admin_command_authorized(self, test_message, config):
        """تست دستور مدیریتی با مجوز"""
        from bot.handlers.commands.admin import admin_command
        
        # اضافه کردن کاربر به لیست مدیران
        config.ADMIN_USER_IDS = [test_message.from_user.id]
        
        await admin_command(test_message)
        
        test_message.answer.assert_called_once()
        args = test_message.answer.call_args[0]
        assert "مدیریت" in args[0] or "پنل" in args[0]
```

### تست پیام‌ها
```python
class TestMessageHandlers:
    """تست هندلرهای پیام"""
    
    @pytest.mark.asyncio
    async def test_text_handler(self, test_message):
        """تست هندلر پیام متنی"""
        from bot.handlers.messages.text import text_handler
        
        test_message.text = "سلام دنیا"
        await text_handler(test_message)
        
        test_message.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_photo_handler(self, test_message):
        """تست هندلر تصویر"""
        from bot.handlers.messages.photo import photo_handler
        
        # Mock کردن photo
        test_message.photo = [AsyncMock()]
        test_message.photo[0].file_id = "test_photo_id"
        
        await photo_handler(test_message)
        
        test_message.answer.assert_called_once()
        args = test_message.answer.call_args[0]
        assert "تصویر" in args[0]
    
    @pytest.mark.asyncio
    async def test_document_handler(self, test_message):
        """تست هندلر فایل"""
        from bot.handlers.messages.document import document_handler
        
        # Mock کردن document
        test_message.document = AsyncMock()
        test_message.document.file_name = "test.pdf"
        test_message.document.file_size = 1024
        
        await document_handler(test_message)
        
        test_message.answer.assert_called_once()
```

### تست callback query ها
```python
class TestCallbackHandlers:
    """تست هندلرهای callback"""
    
    @pytest.fixture
    def test_callback(self, test_user, test_message):
        """callback query تست"""
        callback = AsyncMock()
        callback.id = "test_callback_id"
        callback.from_user = test_user
        callback.message = test_message
        callback.data = "test_data"
        return callback
    
    @pytest.mark.asyncio
    async def test_menu_callback(self, test_callback):
        """تست callback منو"""
        from bot.handlers.callbacks.menu import menu_callback
        
        test_callback.data = "main_menu"
        await menu_callback(test_callback)
        
        # بررسی ویرایش پیام
        test_callback.message.edit_text.assert_called_once()
        
        # بررسی پاسخ callback
        test_callback.answer.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_settings_callback(self, test_callback):
        """تست callback تنظیمات"""
        from bot.handlers.callbacks.settings import settings_callback
        
        test_callback.data = "settings"
        await settings_callback(test_callback)
        
        test_callback.message.edit_text.assert_called_once()
        test_callback.answer.assert_called_once()
```

## 🗄️ تست پایگاه داده

### تست مدل‌ها
```python
# tests/test_database.py
import pytest
from datetime import datetime
from core.database import Database

class TestDatabase:
    """تست‌های پایگاه داده"""
    
    def test_connection(self, test_db):
        """تست اتصال به پایگاه داده"""
        assert test_db.test_connection() == True
    
    def test_create_tables(self, test_db):
        """تست ایجاد جداول"""
        test_db.create_tables()
        
        # بررسی وجود جداول
        tables = test_db.get_table_names()
        assert 'users' in tables
        assert 'messages' in tables
        assert 'user_settings' in tables

class TestUserModel:
    """تست مدل کاربر"""
    
    def test_create_user(self, test_db):
        """تست ایجاد کاربر"""
        user = test_db.create_user(
            user_id=123456789,
            username="test_user",
            first_name="احمد",
            last_name="محمدی"
        )
        
        assert user.user_id == 123456789
        assert user.username == "test_user"
        assert user.first_name == "احمد"
        assert user.last_name == "محمدی"
        assert user.is_active == True
        assert isinstance(user.created_at, datetime)
    
    def test_get_user(self, test_db):
        """تست دریافت کاربر"""
        # ایجاد کاربر
        created_user = test_db.create_user(
            user_id=123456789,
            first_name="احمد"
        )
        
        # دریافت کاربر
        retrieved_user = test_db.get_user(user_id=123456789)
        
        assert retrieved_user is not None
        assert retrieved_user.user_id == created_user.user_id
        assert retrieved_user.first_name == created_user.first_name
    
    def test_user_exists(self, test_db):
        """تست بررسی وجود کاربر"""
        # کاربر موجود نیست
        assert test_db.user_exists(999999999) == False
        
        # ایجاد کاربر
        test_db.create_user(user_id=123456789, first_name="احمد")
        
        # کاربر موجود است
        assert test_db.user_exists(123456789) == True
    
    def test_update_user(self, test_db):
        """تست بروزرسانی کاربر"""
        # ایجاد کاربر
        user = test_db.create_user(
            user_id=123456789,
            first_name="احمد"
        )
        
        # بروزرسانی
        updated_user = test_db.update_user(
            user_id=123456789,
            first_name="علی",
            last_name="رضایی"
        )
        
        assert updated_user.first_name == "علی"
        assert updated_user.last_name == "رضایی"
    
    def test_deactivate_user(self, test_db):
        """تست غیرفعال کردن کاربر"""
        # ایجاد کاربر
        test_db.create_user(user_id=123456789, first_name="احمد")
        
        # غیرفعال کردن
        test_db.deactivate_user(user_id=123456789)
        
        # بررسی وضعیت
        user = test_db.get_user(user_id=123456789)
        assert user.is_active == False

class TestMessageModel:
    """تست مدل پیام"""
    
    def test_save_message(self, test_db):
        """تست ذخیره پیام"""
        # ایجاد کاربر
        test_db.create_user(user_id=123456789, first_name="احمد")
        
        # ذخیره پیام
        message = test_db.save_message(
            user_id=123456789,
            message_id=12345,
            text="سلام دنیا",
            message_type="text"
        )
        
        assert message.user_id == 123456789
        assert message.message_id == 12345
        assert message.text == "سلام دنیا"
        assert message.message_type == "text"
    
    def test_get_user_messages(self, test_db):
        """تست دریافت پیام‌های کاربر"""
        # ایجاد کاربر
        test_db.create_user(user_id=123456789, first_name="احمد")
        
        # ذخیره چند پیام
        test_db.save_message(123456789, 1, "پیام اول", "text")
        test_db.save_message(123456789, 2, "پیام دوم", "text")
        test_db.save_message(123456789, 3, "پیام سوم", "text")
        
        # دریافت پیام‌ها
        messages = test_db.get_user_messages(user_id=123456789, limit=2)
        
        assert len(messages) == 2
        assert messages[0].text == "پیام سوم"  # آخرین پیام
        assert messages[1].text == "پیام دوم"
    
    def test_get_message_count(self, test_db):
        """تست شمارش پیام‌ها"""
        # ایجاد کاربر
        test_db.create_user(user_id=123456789, first_name="احمد")
        
        # ذخیره پیام‌ها
        test_db.save_message(123456789, 1, "پیام 1", "text")
        test_db.save_message(123456789, 2, "پیام 2", "text")
        test_db.save_message(123456789, 3, "پیام 3", "photo")
        
        # شمارش کل
        total_count = test_db.get_user_message_count(user_id=123456789)
        assert total_count == 3
        
        # شمارش بر اساس نوع
        text_count = test_db.get_user_message_count(
            user_id=123456789,
            message_type="text"
        )
        assert text_count == 2
```

## ⚙️ تست تنظیمات

### تست کلاس Config
```python
# tests/test_config.py
import pytest
import os
from core.config import Config

class TestConfig:
    """تست‌های تنظیمات"""
    
    def test_config_loading(self):
        """تست بارگذاری تنظیمات"""
        config = Config(
            BOT_TOKEN="123456:TEST_TOKEN",
            DATABASE_TYPE="sqlite"
        )
        
        assert config.BOT_TOKEN == "123456:TEST_TOKEN"
        assert config.DATABASE_TYPE == "sqlite"
        assert config.BOT_MODE == "polling"  # مقدار پیش‌فرض
    
    def test_config_validation(self):
        """تست اعتبارسنجی تنظیمات"""
        # تنظیمات معتبر
        valid_config = Config(BOT_TOKEN="123456:TEST_TOKEN")
        valid_config.validate()  # نباید خطا دهد
        
        # تنظیمات نامعتبر
        invalid_config = Config(BOT_TOKEN="")
        with pytest.raises(ValueError):
            invalid_config.validate()
    
    def test_webhook_mode_detection(self):
        """تست تشخیص حالت webhook"""
        # حالت polling
        polling_config = Config(
            BOT_TOKEN="123456:TEST_TOKEN",
            BOT_MODE="polling"
        )
        assert polling_config.is_webhook_mode() == False
        
        # حالت webhook
        webhook_config = Config(
            BOT_TOKEN="123456:TEST_TOKEN",
            BOT_MODE="webhook"
        )
        assert webhook_config.is_webhook_mode() == True
    
    def test_admin_user_ids(self):
        """تست لیست مدیران"""
        config = Config(
            BOT_TOKEN="123456:TEST_TOKEN",
            ADMIN_USER_IDS="123,456,789"
        )
        
        admin_ids = config.get_admin_user_ids()
        assert admin_ids == [123, 456, 789]
    
    def test_database_url_generation(self):
        """تست تولید URL پایگاه داده"""
        # SQLite
        sqlite_config = Config(
            BOT_TOKEN="123456:TEST_TOKEN",
            DATABASE_TYPE="sqlite",
            DATABASE_URL="sqlite:///test.db"
        )
        assert sqlite_config.get_database_url() == "sqlite:///test.db"
        
        # PostgreSQL
        pg_config = Config(
            BOT_TOKEN="123456:TEST_TOKEN",
            DATABASE_TYPE="postgresql",
            DATABASE_URL="postgresql://user:pass@localhost/db"
        )
        assert "postgresql://" in pg_config.get_database_url()
```

## 🔄 تست‌های یکپارچگی

### تست جریان کامل
```python
# tests/integration/test_bot_flow.py
import pytest
from unittest.mock import AsyncMock
from bot.factory import BotFactory
from core.config import Config

class TestBotIntegration:
    """تست‌های یکپارچگی ربات"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_complete_bot_flow(self, config, test_db):
        """تست جریان کامل ربات"""
        # ایجاد ربات و dispatcher
        bot = BotFactory.create_bot(config)
        dp = BotFactory.create_dispatcher()
        
        # Mock کردن session
        bot.session = AsyncMock()
        
        # مقداردهی اولیه
        await BotFactory.initialize_bot(bot, config)
        
        # شبیه‌سازی پیام
        from aiogram.types import Update, Message, User, Chat
        
        user = User(id=123, is_bot=False, first_name="احمد")
        chat = Chat(id=123, type="private")
        message = Message(
            message_id=1,
            date=1234567890,
            chat=chat,
            from_user=user,
            text="/start"
        )
        update = Update(update_id=1, message=message)
        
        # پردازش update
        await dp.feed_update(bot, update)
        
        # بررسی ذخیره در پایگاه داده
        user_in_db = test_db.get_user(user_id=123)
        assert user_in_db is not None
        assert user_in_db.first_name == "احمد"
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_user_registration_flow(self, config, test_db):
        """تست جریان ثبت‌نام کاربر"""
        # شبیه‌سازی فرآیند ثبت‌نام کامل
        bot = BotFactory.create_bot(config)
        dp = BotFactory.create_dispatcher()
        
        # Mock session
        bot.session = AsyncMock()
        
        # شروع ثبت‌نام
        # ... کد شبیه‌سازی فرآیند کامل
        
        # بررسی نتیجه نهایی
        assert True  # جایگزین با بررسی واقعی
```

## 📊 تست پوشش کد

### تنظیم Coverage
```bash
# نصب coverage
pip install pytest-cov

# اجرای تست با coverage
pytest --cov=. --cov-report=html --cov-report=term-missing

# نمایش گزارش
open htmlcov/index.html
```

### فایل .coveragerc
```ini
# .coveragerc
[run]
source = .
omit = 
    tests/*
    venv/*
    .venv/*
    */migrations/*
    */venv/*
    setup.py

[report]
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:
```

## 🚀 اجرای تست‌ها

### دستورات اصلی
```bash
# اجرای همه تست‌ها
pytest

# اجرای تست‌های خاص
pytest tests/test_handlers.py

# اجرای تست با جزئیات
pytest -v

# اجرای تست‌های async
pytest -k "asyncio"

# اجرای تست‌های یکپارچگی
pytest -m integration

# اجرای تست‌های سریع
pytest -m "not slow"
```

### تست در محیط‌های مختلف
```bash
# تست در محیط توسعه
pytest --env=development

# تست در محیط تولید
pytest --env=production

# تست با پایگاه داده واقعی
pytest --use-real-db
```

## 🔧 ابزارهای کمکی تست

### Mock Helpers
```python
# tests/utils.py
from unittest.mock import AsyncMock, MagicMock
from aiogram.types import User, Chat, Message

class MockBot:
    """کلاس کمکی برای Mock کردن ربات"""
    
    def __init__(self):
        self.bot = AsyncMock()
        self.sent_messages = []
    
    async def send_message(self, chat_id, text, **kwargs):
        """شبیه‌سازی ارسال پیام"""
        message = {
            'chat_id': chat_id,
            'text': text,
            'kwargs': kwargs
        }
        self.sent_messages.append(message)
        return message
    
    def get_sent_messages(self):
        """دریافت پیام‌های ارسال شده"""
        return self.sent_messages
    
    def clear_sent_messages(self):
        """پاک کردن پیام‌های ارسال شده"""
        self.sent_messages.clear()

def create_test_message(text="test", user_id=123, chat_id=123):
    """ایجاد پیام تست"""
    user = User(id=user_id, is_bot=False, first_name="Test")
    chat = Chat(id=chat_id, type="private")
    
    message = AsyncMock(spec=Message)
    message.message_id = 1
    message.from_user = user
    message.chat = chat
    message.text = text
    message.date = 1234567890
    
    return message

def create_test_callback(data="test", user_id=123):
    """ایجاد callback تست"""
    callback = AsyncMock()
    callback.id = "test_callback"
    callback.from_user = User(id=user_id, is_bot=False, first_name="Test")
    callback.data = data
    callback.message = create_test_message()
    
    return callback
```

## 📋 بهترین شیوه‌های تست

### 1. ساختار تست
- یک تست برای هر عملکرد
- نام‌گذاری واضح و توصیفی
- استفاده از fixture ها

### 2. Mock کردن
- Mock کردن وابستگی‌های خارجی
- استفاده از AsyncMock برای توابع async
- بررسی فراخوانی متدها

### 3. داده‌های تست
- استفاده از fixture ها
- جداسازی داده‌های تست
- پاک کردن داده‌ها پس از تست

### 4. عملکرد
- تست‌های سریع و مستقل
- اجتناب از وابستگی‌های خارجی
- استفاده از پایگاه داده حافظه

## 🔗 مراحل بعدی

- [مشارکت در پروژه](CONTRIBUTING.md)
- [استقرار ربات](../advanced/DEPLOYMENT.md)
- [بهینه‌سازی عملکرد](../advanced/OPTIMIZATION.md)