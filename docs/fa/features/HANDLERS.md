# 🎛️ راهنمای هندلرها

> **مدیریت دستورات و پیام‌های ربات تلگرام**

## 🎯 درباره هندلرها

هندلرها قلب ربات تلگرام هستند. آن‌ها مسئول پردازش پیام‌ها، دستورات، callback query ها و سایر رویدادهای تلگرام هستند.

## 🏗️ ساختار هندلرها

### ساختار فایل‌ها
```
bot/handlers/
├── __init__.py          # ثبت همه هندلرها
├── commands/            # هندلرهای دستورات
│   ├── __init__.py
│   ├── start.py        # دستور /start
│   ├── help.py         # دستور /help
│   └── admin.py        # دستورات مدیریتی
├── messages/           # هندلرهای پیام
│   ├── __init__.py
│   ├── text.py         # پیام‌های متنی
│   ├── photo.py        # تصاویر
│   └── document.py     # فایل‌ها
├── callbacks/          # هندلرهای callback
│   ├── __init__.py
│   └── inline.py       # دکمه‌های inline
└── errors/             # مدیریت خطاها
    ├── __init__.py
    └── handlers.py     # هندلر خطاها
```

## 🚀 ساخت هندلر جدید

### 1. هندلر دستور ساده
```python
# bot/handlers/commands/weather.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

router = Router()

@router.message(Command("weather"))
async def weather_command(message: Message):
    """هندلر دستور /weather"""
    await message.answer(
        "🌤️ آب و هوای امروز:\n"
        "دمای هوا: 25°C\n"
        "وضعیت: آفتابی"
    )
```

### 2. هندلر با پارامتر
```python
# bot/handlers/commands/user.py
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command, CommandObject

router = Router()

@router.message(Command("user"))
async def user_command(message: Message, command: CommandObject):
    """هندلر دستور /user با پارامتر"""
    if command.args:
        username = command.args
        await message.answer(f"👤 اطلاعات کاربر: @{username}")
    else:
        await message.answer("❌ لطفاً نام کاربری را وارد کنید\nمثال: /user username")
```

### 3. هندلر پیام متنی
```python
# bot/handlers/messages/echo.py
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text)
async def echo_handler(message: Message):
    """هندلر echo برای پیام‌های متنی"""
    user_text = message.text
    await message.answer(f"📝 شما گفتید: {user_text}")
```

### 4. هندلر callback query
```python
# bot/handlers/callbacks/menu.py
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

router = Router()

@router.callback_query(F.data == "main_menu")
async def main_menu_callback(callback: CallbackQuery):
    """هندلر منوی اصلی"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="⚙️ تنظیمات", callback_data="settings")],
        [InlineKeyboardButton(text="📊 آمار", callback_data="stats")],
        [InlineKeyboardButton(text="❓ راهنما", callback_data="help")]
    ])
    
    await callback.message.edit_text(
        "🏠 منوی اصلی\nیکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=keyboard
    )
    await callback.answer()
```

## 🔧 فیلترهای پیشرفته

### 1. فیلتر کاربران مدیر
```python
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from core.config import Config

router = Router()

@router.message(Command("admin"))
async def admin_command(message: Message):
    """دستور مخصوص مدیران"""
    config = Config()
    admin_ids = config.get_admin_user_ids()
    
    if message.from_user.id not in admin_ids:
        await message.answer("❌ شما مجوز استفاده از این دستور را ندارید")
        return
    
    await message.answer("👑 پنل مدیریت\nشما مدیر ربات هستید")
```

### 2. فیلتر نوع فایل
```python
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.photo)
async def photo_handler(message: Message):
    """هندلر تصاویر"""
    await message.answer("📸 تصویر دریافت شد!")

@router.message(F.document)
async def document_handler(message: Message):
    """هندلر فایل‌ها"""
    file_name = message.document.file_name
    await message.answer(f"📄 فایل دریافت شد: {file_name}")

@router.message(F.voice)
async def voice_handler(message: Message):
    """هندلر پیام‌های صوتی"""
    await message.answer("🎤 پیام صوتی دریافت شد!")
```

### 3. فیلتر متن خاص
```python
from aiogram import Router, F
from aiogram.types import Message

router = Router()

@router.message(F.text.contains("سلام"))
async def greeting_handler(message: Message):
    """هندلر پیام‌های حاوی سلام"""
    await message.answer("👋 سلام! خوش آمدید")

@router.message(F.text.regexp(r"\d+"))
async def number_handler(message: Message):
    """هندلر پیام‌های حاوی عدد"""
    await message.answer("🔢 عدد شناسایی شد!")
```

## 🎨 کیبوردها و دکمه‌ها

### 1. کیبورد Reply
```python
from aiogram import Router
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton
from aiogram.filters import Command

router = Router()

@router.message(Command("menu"))
async def menu_command(message: Message):
    """نمایش منوی اصلی"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📊 آمار"), KeyboardButton(text="⚙️ تنظیمات")],
            [KeyboardButton(text="📞 تماس"), KeyboardButton(text="📍 موقعیت")],
            [KeyboardButton(text="❌ بستن منو")]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    
    await message.answer(
        "🏠 منوی اصلی\nیکی از گزینه‌ها را انتخاب کنید:",
        reply_markup=keyboard
    )
```

### 2. کیبورد Inline
```python
from aiogram import Router
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

router = Router()

@router.message(Command("settings"))
async def settings_command(message: Message):
    """نمایش تنظیمات"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔔 اعلان‌ها", callback_data="toggle_notifications"),
            InlineKeyboardButton(text="🌙 حالت شب", callback_data="toggle_dark_mode")
        ],
        [
            InlineKeyboardButton(text="🌍 زبان", callback_data="change_language"),
            InlineKeyboardButton(text="🔒 حریم خصوصی", callback_data="privacy_settings")
        ],
        [InlineKeyboardButton(text="🔙 بازگشت", callback_data="main_menu")]
    ])
    
    await message.answer(
        "⚙️ تنظیمات\nگزینه مورد نظر را انتخاب کنید:",
        reply_markup=keyboard
    )
```

## 🗄️ کار با پایگاه داده

### 1. ذخیره اطلاعات کاربر
```python
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from core.database import Database

router = Router()

@router.message(Command("register"))
async def register_command(message: Message):
    """ثبت‌نام کاربر"""
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    db = Database()
    
    # بررسی وجود کاربر
    if db.user_exists(user_id):
        await message.answer("✅ شما قبلاً ثبت‌نام کرده‌اید")
        return
    
    # ثبت کاربر جدید
    db.create_user(
        user_id=user_id,
        username=username,
        first_name=first_name
    )
    
    await message.answer(
        f"🎉 ثبت‌نام موفق!\n"
        f"👤 نام: {first_name}\n"
        f"🆔 شناسه: {user_id}"
    )
```

### 2. دریافت آمار
```python
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from core.database import Database

router = Router()

@router.message(Command("stats"))
async def stats_command(message: Message):
    """نمایش آمار"""
    db = Database()
    
    total_users = db.get_user_count()
    active_users = db.get_active_user_count()
    
    await message.answer(
        f"📊 آمار ربات:\n\n"
        f"👥 کل کاربران: {total_users}\n"
        f"🟢 کاربران فعال: {active_users}\n"
        f"📈 نرخ فعالیت: {(active_users/total_users*100):.1f}%"
    )
```

## 🔄 State Management

### 1. تعریف State ها
```python
# bot/states/user_states.py
from aiogram.fsm.state import State, StatesGroup

class UserRegistration(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_city = State()
    confirmation = State()
```

### 2. استفاده از State ها
```python
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from bot.states.user_states import UserRegistration

router = Router()

@router.message(Command("profile"))
async def start_registration(message: Message, state: FSMContext):
    """شروع فرآیند ثبت پروفایل"""
    await state.set_state(UserRegistration.waiting_for_name)
    await message.answer("👤 لطفاً نام خود را وارد کنید:")

@router.message(UserRegistration.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """پردازش نام"""
    await state.update_data(name=message.text)
    await state.set_state(UserRegistration.waiting_for_age)
    await message.answer("🎂 لطفاً سن خود را وارد کنید:")

@router.message(UserRegistration.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """پردازش سن"""
    if not message.text.isdigit():
        await message.answer("❌ لطفاً عدد معتبر وارد کنید:")
        return
    
    await state.update_data(age=int(message.text))
    await state.set_state(UserRegistration.waiting_for_city)
    await message.answer("🏙️ لطفاً شهر خود را وارد کنید:")

@router.message(UserRegistration.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    """پردازش شهر"""
    await state.update_data(city=message.text)
    
    # دریافت تمام داده‌ها
    data = await state.get_data()
    
    await message.answer(
        f"✅ پروفایل شما:\n\n"
        f"👤 نام: {data['name']}\n"
        f"🎂 سن: {data['age']}\n"
        f"🏙️ شهر: {data['city']}\n\n"
        f"آیا اطلاعات صحیح است؟ (بله/خیر)"
    )
    
    await state.set_state(UserRegistration.confirmation)

@router.message(UserRegistration.confirmation)
async def confirm_registration(message: Message, state: FSMContext):
    """تأیید ثبت‌نام"""
    if message.text.lower() in ['بله', 'yes', 'آره']:
        data = await state.get_data()
        
        # ذخیره در پایگاه داده
        db = Database()
        db.save_user_profile(
            user_id=message.from_user.id,
            name=data['name'],
            age=data['age'],
            city=data['city']
        )
        
        await message.answer("🎉 پروفایل شما با موفقیت ذخیره شد!")
    else:
        await message.answer("❌ ثبت‌نام لغو شد. برای شروع مجدد /profile را ارسال کنید.")
    
    await state.clear()
```

## 🛡️ مدیریت خطاها

### 1. هندلر خطاهای عمومی
```python
# bot/handlers/errors/handlers.py
from aiogram import Router
from aiogram.types import ErrorEvent
import logging

router = Router()

@router.error()
async def error_handler(event: ErrorEvent):
    """مدیریت خطاهای عمومی"""
    logging.error(f"خطا در هندلر: {event.exception}")
    
    if event.update.message:
        await event.update.message.answer(
            "❌ خطایی رخ داده است. لطفاً دوباره تلاش کنید."
        )
    elif event.update.callback_query:
        await event.update.callback_query.answer(
            "❌ خطایی رخ داده است",
            show_alert=True
        )
```

### 2. هندلر خطاهای خاص
```python
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.exceptions import TelegramBadRequest

router = Router()

@router.message(Command("delete"))
async def delete_message(message: Message):
    """حذف پیام"""
    try:
        await message.delete()
        await message.answer("✅ پیام حذف شد")
    except TelegramBadRequest as e:
        if "message to delete not found" in str(e):
            await message.answer("❌ پیام برای حذف یافت نشد")
        else:
            await message.answer("❌ خطا در حذف پیام")
```

## 📝 ثبت هندلرها

### 1. ثبت در فایل __init__.py
```python
# bot/handlers/__init__.py
from aiogram import Dispatcher

from .commands import start, help, admin, weather
from .messages import text, photo, document
from .callbacks import inline, menu
from .errors import handlers as error_handlers

def register_handlers(dp: Dispatcher):
    """ثبت همه هندلرها"""
    
    # ثبت هندلرهای دستورات
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(admin.router)
    dp.include_router(weather.router)
    
    # ثبت هندلرهای پیام
    dp.include_router(photo.router)
    dp.include_router(document.router)
    dp.include_router(text.router)  # آخرین هندلر متنی
    
    # ثبت هندلرهای callback
    dp.include_router(inline.router)
    dp.include_router(menu.router)
    
    # ثبت هندلر خطاها
    dp.include_router(error_handlers.router)
```

### 2. استفاده در BotFactory
```python
# bot/factory.py
from bot.handlers import register_handlers

class BotFactory:
    @staticmethod
    def create_dispatcher() -> Dispatcher:
        """ایجاد dispatcher با هندلرها"""
        dp = Dispatcher()
        
        # ثبت همه هندلرها
        register_handlers(dp)
        
        return dp
```

## 🧪 تست هندلرها

### 1. تست واحد هندلر
```python
# tests/test_handlers.py
import pytest
from unittest.mock import AsyncMock
from aiogram.types import Message, User, Chat
from bot.handlers.commands.start import start_command

@pytest.mark.asyncio
async def test_start_command():
    """تست دستور /start"""
    # ایجاد mock message
    message = AsyncMock(spec=Message)
    message.from_user = User(id=123, is_bot=False, first_name="Test")
    message.chat = Chat(id=123, type="private")
    
    # اجرای هندلر
    await start_command(message)
    
    # بررسی فراخوانی answer
    message.answer.assert_called_once()
    args = message.answer.call_args[0]
    assert "خوش آمدید" in args[0]
```

### 2. تست یکپارچگی
```python
# tests/test_integration.py
import pytest
from aiogram.methods import SendMessage
from tests.utils import MockBot

@pytest.mark.asyncio
async def test_weather_command_integration():
    """تست یکپارچگی دستور آب و هوا"""
    bot = MockBot()
    
    # شبیه‌سازی دستور
    result = await bot.send_command("/weather", user_id=123)
    
    # بررسی پاسخ
    assert isinstance(result, SendMessage)
    assert "آب و هوا" in result.text
```

## 📋 بهترین شیوه‌ها

### 1. ساختار کد
- هر هندلر در فایل جداگانه
- استفاده از Router برای گروه‌بندی
- نام‌گذاری واضح و توصیفی

### 2. مدیریت خطا
- همیشه try-catch استفاده کنید
- پیام‌های خطای کاربرپسند
- لاگ‌گیری مناسب

### 3. عملکرد
- استفاده از async/await
- اجتناب از عملیات طولانی در هندلرها
- استفاده از middleware برای کارهای مشترک

### 4. امنیت
- اعتبارسنجی ورودی‌ها
- محدودیت دسترسی
- محافظت از اطلاعات حساس

## 🔗 مراحل بعدی

- [تنظیم پایگاه داده](DATABASE.md)
- [نوشتن تست‌ها](../development/TESTING.md)
- [استقرار ربات](../advanced/DEPLOYMENT.md)