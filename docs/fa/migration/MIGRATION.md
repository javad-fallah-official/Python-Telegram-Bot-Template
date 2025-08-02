# 🔄 راهنمای مهاجرت

> **مهاجرت از نسخه‌های قدیمی aiogram و بروزرسانی ربات**

## 🎯 درباره مهاجرت

این راهنما شامل تمام مراحل مهاجرت از نسخه‌های قدیمی aiogram (1.x و 2.x) به نسخه 3.x و همچنین بروزرسانی ربات‌های موجود است.

## 📊 جدول مقایسه نسخه‌ها

| ویژگی | aiogram 1.x | aiogram 2.x | aiogram 3.x |
|--------|-------------|-------------|-------------|
| Python | 3.6+ | 3.7+ | 3.8+ |
| Async/Await | محدود | کامل | کامل |
| Type Hints | خیر | جزئی | کامل |
| Middleware | ساده | پیشرفته | بهبود یافته |
| Filters | محدود | پیشرفته | بهبود یافته |
| FSM | ساده | پیشرفته | بهبود یافته |
| Router | خیر | خیر | بله |

## 🚀 مهاجرت از aiogram 2.x به 3.x

### 1. تغییرات اصلی

#### Import ها
```python
# aiogram 2.x
from aiogram import Bot, Dispatcher, executor
from aiogram.types import Message
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# aiogram 3.x
from aiogram import Bot, Dispatcher, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
```

#### ایجاد Bot و Dispatcher
```python
# aiogram 2.x
bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

# aiogram 3.x
bot = Bot(token=TOKEN)
dp = Dispatcher()
```

#### Handler Registration
```python
# aiogram 2.x
@dp.message_handler(commands=['start'])
async def start_handler(message: Message):
    await message.reply("سلام!")

@dp.message_handler(content_types=['photo'])
async def photo_handler(message: Message):
    await message.reply("تصویر دریافت شد!")

# aiogram 3.x
@dp.message(Command("start"))
async def start_handler(message: Message):
    await message.reply("سلام!")

@dp.message(F.photo)
async def photo_handler(message: Message):
    await message.reply("تصویر دریافت شد!")
```

### 2. تغییرات FSM

#### تعریف States
```python
# aiogram 2.x
from aiogram.dispatcher.filters.state import State, StatesGroup

class UserForm(StatesGroup):
    name = State()
    age = State()

# aiogram 3.x
from aiogram.fsm.state import State, StatesGroup

class UserForm(StatesGroup):
    name = State()
    age = State()
```

#### استفاده از FSM
```python
# aiogram 2.x
@dp.message_handler(state=UserForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await UserForm.age.set()
    await message.reply("سن خود را وارد کنید:")

# aiogram 3.x
@dp.message(UserForm.name)
async def process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await state.set_state(UserForm.age)
    await message.reply("سن خود را وارد کنید:")
```

### 3. تغییرات Filters

#### Custom Filters
```python
# aiogram 2.x
from aiogram.dispatcher.filters import BoundFilter

class IsAdminFilter(BoundFilter):
    key = 'is_admin'
    
    def __init__(self, is_admin):
        self.is_admin = is_admin
    
    async def check(self, message: Message):
        return message.from_user.id in ADMIN_IDS

dp.filters_factory.bind(IsAdminFilter)

# aiogram 3.x
from aiogram.filters import BaseFilter

class IsAdminFilter(BaseFilter):
    def __init__(self, admin_ids: list):
        self.admin_ids = admin_ids
    
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in self.admin_ids

# استفاده
@dp.message(Command("admin"), IsAdminFilter(ADMIN_IDS))
async def admin_handler(message: Message):
    await message.reply("پنل مدیریت")
```

### 4. تغییرات Middleware

#### ساختار Middleware
```python
# aiogram 2.x
from aiogram.dispatcher.middlewares import BaseMiddleware

class LoggingMiddleware(BaseMiddleware):
    async def on_process_message(self, message: Message, data: dict):
        print(f"پیام دریافت شد: {message.text}")

dp.middleware.setup(LoggingMiddleware())

# aiogram 3.x
from aiogram import BaseMiddleware
from typing import Callable, Dict, Any, Awaitable

class LoggingMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any]
    ) -> Any:
        print(f"پیام دریافت شد: {event.text}")
        return await handler(event, data)

dp.message.middleware(LoggingMiddleware())
```

### 5. تغییرات Executor

#### راه‌اندازی ربات
```python
# aiogram 2.x
from aiogram import executor

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

# aiogram 3.x
import asyncio

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
```

## 🔧 مراحل مهاجرت گام به گام

### مرحله 1: آماده‌سازی

#### 1. پشتیبان‌گیری
```bash
# ایجاد branch جدید
git checkout -b migration-to-aiogram3

# پشتیبان‌گیری فایل‌ها
cp -r . ../backup-before-migration/
```

#### 2. بررسی وابستگی‌ها
```bash
# بررسی نسخه فعلی
pip show aiogram

# لیست وابستگی‌ها
pip freeze > requirements-old.txt
```

### مرحله 2: بروزرسانی وابستگی‌ها

#### 1. بروزرسانی aiogram
```bash
# حذف نسخه قدیمی
pip uninstall aiogram

# نصب نسخه جدید
pip install aiogram==3.15.0

# بروزرسانی requirements.txt
echo "aiogram==3.15.0" > requirements.txt
```

#### 2. بروزرسانی سایر پکیج‌ها
```bash
# بروزرسانی همه پکیج‌ها
pip install --upgrade -r requirements.txt
```

### مرحله 3: تغییر کد

#### 1. بروزرسانی Import ها
```python
# فایل: bot/factory.py
# قبل از مهاجرت
from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

# بعد از مهاجرت
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
```

#### 2. بروزرسانی Handler ها
```python
# فایل: bot/handlers/commands/start.py
# قبل از مهاجرت
from aiogram import types
from aiogram.dispatcher import FSMContext

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    await message.reply("خوش آمدید!")

# بعد از مهاجرت
from aiogram import types, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

@router.message(Command("start"))
async def start_command(message: types.Message):
    await message.reply("خوش آمدید!")
```

#### 3. بروزرسانی Router ها
```python
# فایل: bot/handlers/__init__.py
# قبل از مهاجرت
def register_handlers(dp: Dispatcher):
    # ثبت handler ها

# بعد از مهاجرت
from aiogram import Router

def setup_routers() -> Router:
    router = Router()
    
    # اضافه کردن sub-router ها
    router.include_router(commands_router)
    router.include_router(messages_router)
    
    return router
```

### مرحله 4: تست و اصلاح

#### 1. اجرای تست‌ها
```bash
# اجرای تست‌های واحد
python -m pytest tests/ -v

# تست اتصال ربات
python -c "from bot.factory import BotFactory; print('OK')"
```

#### 2. اصلاح خطاها
```python
# خطاهای رایج و راه حل

# خطا: AttributeError: 'Dispatcher' object has no attribute 'message_handler'
# راه حل: استفاده از Router

# خطا: ImportError: cannot import name 'executor'
# راه حل: استفاده از asyncio.run()

# خطا: TypeError: 'NoneType' object is not callable
# راه حل: بررسی handler registration
```

## 🔄 مهاجرت از aiogram 1.x

### تغییرات اصلی

#### 1. Async/Await
```python
# aiogram 1.x
def start_handler(message):
    bot.send_message(message.chat.id, "سلام!")

# aiogram 3.x
async def start_handler(message: Message):
    await message.reply("سلام!")
```

#### 2. Type Hints
```python
# aiogram 1.x
def echo_handler(message):
    return message.text

# aiogram 3.x
async def echo_handler(message: Message) -> None:
    await message.reply(message.text)
```

#### 3. Handler Registration
```python
# aiogram 1.x
@bot.message_handler(commands=['start'])
def start_handler(message):
    bot.reply_to(message, "سلام!")

# aiogram 3.x
@router.message(Command("start"))
async def start_handler(message: Message):
    await message.reply("سلام!")
```

## 🗄️ مهاجرت پایگاه داده

### 1. تغییرات Schema

#### SQLite Migration
```sql
-- migration_001.sql
-- اضافه کردن ستون‌های جدید
ALTER TABLE users ADD COLUMN language_code VARCHAR(10) DEFAULT 'fa';
ALTER TABLE users ADD COLUMN timezone VARCHAR(50) DEFAULT 'Asia/Tehran';

-- ایجاد جداول جدید
CREATE TABLE IF NOT EXISTS user_settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id BIGINT NOT NULL,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    UNIQUE(user_id, setting_key)
);

-- ایجاد index ها
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
```

#### PostgreSQL Migration
```sql
-- migration_001.sql
-- اضافه کردن ستون‌های جدید
ALTER TABLE users ADD COLUMN IF NOT EXISTS language_code VARCHAR(10) DEFAULT 'fa';
ALTER TABLE users ADD COLUMN IF NOT EXISTS timezone VARCHAR(50) DEFAULT 'Asia/Tehran';

-- ایجاد جداول جدید
CREATE TABLE IF NOT EXISTS user_settings (
    id SERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    setting_key VARCHAR(100) NOT NULL,
    setting_value TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users (user_id),
    UNIQUE(user_id, setting_key)
);

-- ایجاد index ها
CREATE INDEX IF NOT EXISTS idx_user_settings_user_id ON user_settings(user_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);
```

### 2. اسکریپت مهاجرت
```python
# scripts/migrate_database.py
import sqlite3
import logging
from pathlib import Path

class DatabaseMigrator:
    """کلاس مهاجرت پایگاه داده"""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.migrations_dir = Path("migrations")
    
    def get_current_version(self) -> int:
        """دریافت نسخه فعلی پایگاه داده"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # ایجاد جدول migrations اگر وجود ندارد
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS migrations (
                    id INTEGER PRIMARY KEY,
                    version INTEGER UNIQUE,
                    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # دریافت آخرین نسخه
            cursor.execute("SELECT MAX(version) FROM migrations")
            result = cursor.fetchone()
            
            conn.close()
            return result[0] if result[0] else 0
            
        except Exception as e:
            logging.error(f"خطا در دریافت نسخه: {e}")
            return 0
    
    def apply_migration(self, version: int, sql_file: Path):
        """اعمال migration"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # خواندن فایل SQL
            with open(sql_file, 'r', encoding='utf-8') as f:
                sql_content = f.read()
            
            # اجرای SQL
            cursor.executescript(sql_content)
            
            # ثبت migration
            cursor.execute(
                "INSERT INTO migrations (version) VALUES (?)",
                (version,)
            )
            
            conn.commit()
            conn.close()
            
            logging.info(f"Migration {version} اعمال شد")
            
        except Exception as e:
            logging.error(f"خطا در اعمال migration {version}: {e}")
            raise
    
    def migrate(self):
        """اجرای تمام migration های جدید"""
        current_version = self.get_current_version()
        
        # پیدا کردن فایل‌های migration
        migration_files = sorted(
            self.migrations_dir.glob("*.sql"),
            key=lambda x: int(x.stem.split('_')[0])
        )
        
        for migration_file in migration_files:
            version = int(migration_file.stem.split('_')[0])
            
            if version > current_version:
                logging.info(f"اعمال migration {version}...")
                self.apply_migration(version, migration_file)
        
        logging.info("تمام migration ها اعمال شدند")

# استفاده
if __name__ == "__main__":
    migrator = DatabaseMigrator("data/bot.db")
    migrator.migrate()
```

## 📝 چک‌لیست مهاجرت

### ✅ قبل از مهاجرت
- [ ] پشتیبان‌گیری از کد و پایگاه داده
- [ ] مستندسازی تغییرات مورد نیاز
- [ ] آماده‌سازی محیط تست
- [ ] بررسی وابستگی‌های پروژه

### ✅ حین مهاجرت
- [ ] بروزرسانی aiogram به نسخه 3.x
- [ ] تغییر import ها
- [ ] بروزرسانی handler ها
- [ ] تغییر FSM implementation
- [ ] بروزرسانی middleware ها
- [ ] تغییر executor به asyncio

### ✅ بعد از مهاجرت
- [ ] اجرای تست‌های واحد
- [ ] تست عملکرد ربات
- [ ] بررسی log ها
- [ ] تست در محیط production
- [ ] بروزرسانی مستندات

## 🚨 مشکلات رایج و راه حل

### 1. خطای Import
```python
# مشکل
ImportError: cannot import name 'executor' from 'aiogram'

# راه حل
# حذف executor و استفاده از asyncio
import asyncio

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
```

### 2. خطای Handler Registration
```python
# مشکل
AttributeError: 'Dispatcher' object has no attribute 'message_handler'

# راه حل
# استفاده از Router
from aiogram import Router

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    pass
```

### 3. خطای FSM
```python
# مشکل
ImportError: cannot import name 'FSMContext' from 'aiogram.dispatcher'

# راه حل
# تغییر import
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
```

### 4. خطای Filter
```python
# مشکل
TypeError: 'str' object is not callable

# راه حل
# استفاده از Filter classes
from aiogram.filters import Command

@router.message(Command("start"))  # به جای commands=['start']
async def start_handler(message: Message):
    pass
```

## 📊 بررسی عملکرد بعد از مهاجرت

### 1. Benchmarking
```python
# scripts/benchmark.py
import time
import asyncio
from bot.factory import BotFactory

async def benchmark_bot():
    """تست عملکرد ربات"""
    config = Config()
    bot = BotFactory.create_bot(config)
    
    start_time = time.time()
    
    # تست ارسال پیام
    for i in range(100):
        # شبیه‌سازی پردازش پیام
        await asyncio.sleep(0.01)
    
    end_time = time.time()
    
    print(f"زمان پردازش 100 پیام: {end_time - start_time:.2f} ثانیه")

if __name__ == "__main__":
    asyncio.run(benchmark_bot())
```

### 2. Memory Usage
```python
# scripts/memory_test.py
import psutil
import os

def check_memory_usage():
    """بررسی مصرف حافظه"""
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    print(f"مصرف حافظه: {memory_info.rss / 1024 / 1024:.2f} MB")
    print(f"حافظه مجازی: {memory_info.vms / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    check_memory_usage()
```

## 🔗 منابع مفید

### مستندات رسمی
- [aiogram 3.x Documentation](https://docs.aiogram.dev/en/latest/)
- [Migration Guide](https://docs.aiogram.dev/en/latest/migration_2_to_3.html)

### ابزارهای کمکی
- [aiogram-migration-tool](https://github.com/aiogram/migration-tool)
- [Code Converter](https://github.com/aiogram/aiogram-converter)

### مثال‌های عملی
- [Example Bots](https://github.com/aiogram/aiogram/tree/dev-3.x/examples)
- [Community Examples](https://github.com/aiogram/awesome-aiogram)

## 🔗 مراحل بعدی

- [تست ربات](../development/TESTING.md)
- [استقرار ربات](../advanced/DEPLOYMENT.md)
- [بهینه‌سازی عملکرد](../advanced/OPTIMIZATION.md)