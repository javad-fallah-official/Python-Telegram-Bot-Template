# 🏗️ ساختار کامل پروژه

> **راهنمای جامع ساختار پروژه قالب ربات تلگرام پایتون**

## 📋 فهرست مطالب

- [🎯 نمای کلی](#-نمای-کلی)
- [📁 ساختار کد](#-ساختار-کد)
- [📚 ساختار مستندات](#-ساختار-مستندات)
- [🔧 فایل‌های پیکربندی](#-فایل‌های-پیکربندی)
- [🧪 ساختار تست‌ها](#-ساختار-تست‌ها)
- [📝 مثال‌ها](#-مثال‌ها)
- [🛠️ ابزارها و اسکریپت‌ها](#️-ابزارها-و-اسکریپت‌ها)

## 🎯 نمای کلی

این پروژه با ساختار مدولار و منظم طراحی شده که امکان توسعه، نگهداری و تست آسان را فراهم می‌کند.

```
Python-Telegram-Bot-Template/
├── 📁 bot/                    # هسته ربات و هندلرها
├── 📁 core/                   # اجزای اصلی سیستم
├── 📁 services/               # سرویس‌های ربات
├── 📁 utils/                  # ابزارهای کمکی
├── 📁 tests/                  # تست‌های پروژه
├── 📁 examples/               # مثال‌های کاربردی
├── 📁 docs/                   # مستندات
├── 📁 scripts/                # اسکریپت‌های کمکی
├── 📄 main.py                 # نقطه ورود اصلی
└── 📄 pyproject.toml          # تنظیمات پروژه
```

## 📁 ساختار کد

### 🤖 پوشه `bot/` - هسته ربات

```
bot/
├── __init__.py              # ماژول اصلی ربات
├── factory.py               # کارخانه ساخت ربات (BotFactory)
└── handlers/                # هندلرهای ربات
    ├── __init__.py          # ماژول هندلرها
    ├── commands.py          # هندلرهای دستورات (/start, /help, ...)
    ├── messages.py          # هندلرهای پیام‌های متنی
    ├── errors.py            # هندلر خطاها
    └── registry.py          # ثبت‌کننده هندلرها
```

**توضیحات:**
- `factory.py`: الگوی Factory برای ساخت و پیکربندی ربات
- `handlers/commands.py`: دستورات اصلی ربات مانند `/start`, `/help`
- `handlers/messages.py`: پردازش پیام‌های متنی، عکس، فایل
- `handlers/errors.py`: مدیریت خطاها و استثناها
- `handlers/registry.py`: ثبت خودکار تمام هندلرها

### ⚙️ پوشه `core/` - اجزای اصلی

```
core/
├── __init__.py              # ماژول اصلی core
├── config.py                # مدیریت تنظیمات (Config class)
├── database.py              # لایه انتزاعی پایگاه داده
├── db_factory.py            # کارخانه ساخت پایگاه داده
├── postgres.py              # پیاده‌سازی PostgreSQL
├── logger.py                # سیستم لاگ‌گیری
├── middleware.py            # میدل‌ویرهای ربات
└── runner.py                # اجراکننده ربات (BotRunner)
```

**توضیحات:**
- `config.py`: مدیریت متغیرهای محیطی و تنظیمات
- `database.py`: کلاس پایه برای عملیات پایگاه داده
- `db_factory.py`: انتخاب خودکار نوع پایگاه داده
- `postgres.py`: پیاده‌سازی اختصاصی PostgreSQL
- `logger.py`: تنظیمات لاگ‌گیری با فرمت‌های مختلف
- `middleware.py`: میدل‌ویرهای احراز هویت و لاگ‌گیری
- `runner.py`: مدیریت چرخه حیات ربات

### 🔧 پوشه `services/` - سرویس‌ها

```
services/
├── __init__.py              # ماژول سرویس‌ها
├── base.py                  # کلاس پایه سرویس‌ها
├── polling.py               # سرویس Polling
└── webhook.py               # سرویس Webhook
```

**توضیحات:**
- `base.py`: کلاس پایه برای تمام سرویس‌ها
- `polling.py`: اجرای ربات در حالت Polling
- `webhook.py`: اجرای ربات در حالت Webhook

### 🛠️ پوشه `utils/` - ابزارهای کمکی

```
utils/
├── __init__.py              # ماژول ابزارها
├── cache.py                 # سیستم کش
├── files.py                 # عملیات فایل
├── formatters.py            # فرمت‌کننده‌های متن
├── keyboards.py             # کیبوردهای شخصی‌سازی شده
├── logging_utils.py         # ابزارهای لاگ‌گیری
├── text.py                  # پردازش متن
└── validators.py            # اعتبارسنجی داده‌ها
```

**توضیحات:**
- `cache.py`: کش حافظه و Redis
- `files.py`: آپلود، دانلود و پردازش فایل‌ها
- `formatters.py`: فرمت‌بندی پیام‌ها و داده‌ها
- `keyboards.py`: کیبوردهای Reply و Inline
- `logging_utils.py`: ابزارهای کمکی لاگ‌گیری
- `text.py`: پردازش و تحلیل متن
- `validators.py`: اعتبارسنجی ورودی‌ها

## 📚 ساختار مستندات

### 🌐 مستندات انگلیسی `docs/`

```
docs/
├── README.md                # راهنمای اصلی مستندات
├── DOCUMENTATION_REFACTOR_SUMMARY.md  # خلاصه بازسازی مستندات
├── POSTGRESQL.md            # راهنمای PostgreSQL
├── setup/                   # راه‌اندازی
│   ├── INSTALLATION.md      # راهنمای نصب
│   └── CONFIGURATION.md     # راهنمای تنظیمات
├── features/                # ویژگی‌ها
│   ├── DATABASE.md          # راهنمای پایگاه داده
│   └── HANDLERS.md          # راهنمای هندلرها
├── migration/               # مهاجرت
│   ├── AIOGRAM_MIGRATION.md # مهاجرت aiogram
│   ├── DATABASE_MIGRATION.md# مهاجرت پایگاه داده
│   └── TEST_MIGRATION.md    # مهاجرت تست‌ها
├── development/             # توسعه
│   ├── TESTING.md          # راهنمای تست‌نویسی
│   └── CONTRIBUTING.md     # راهنمای مشارکت
├── advanced/                # موضوعات پیشرفته
│   └── POSTGRESQL.md        # PostgreSQL پیشرفته
└── api/                     # مرجع API
    ├── HANDLERS.md         # API هندلرها
    ├── DATABASE.md         # API پایگاه داده
    ├── UTILITIES.md        # API ابزارها
    └── MIDDLEWARE.md       # API میدل‌ویر
```

### 🇮🇷 مستندات فارسی `docs/fa/`

```
docs/fa/
├── README.md                # راهنمای اصلی فارسی
├── PROJECT_STRUCTURE.md     # این سند - ساختار پروژه
├── setup/                   # راه‌اندازی
│   ├── INSTALLATION.md      # راهنمای نصب
│   └── CONFIGURATION.md     # راهنمای تنظیمات
├── features/                # ویژگی‌ها
│   ├── DATABASE.md          # راهنمای پایگاه داده
│   └── HANDLERS.md          # راهنمای هندلرها
├── migration/               # مهاجرت
│   └── MIGRATION.md         # راهنمای مهاجرت
├── development/             # توسعه
│   └── TESTING.md          # راهنمای تست‌نویسی
├── advanced/                # موضوعات پیشرفته
│   ├── DEPLOYMENT.md        # راهنمای استقرار
│   ├── OPTIMIZATION.md      # راهنمای بهینه‌سازی
│   └── MONITORING.md        # راهنمای نظارت
└── api/                     # مرجع API (در حال توسعه)
    ├── HANDLERS.md         # API هندلرها
    ├── DATABASE.md         # API پایگاه داده
    ├── UTILITIES.md        # API ابزارها
    └── MIDDLEWARE.md       # API میدل‌ویر
```

## 🔧 فایل‌های پیکربندی

### 📄 فایل‌های اصلی

```
├── .env.example             # نمونه متغیرهای محیطی
├── .gitignore              # فایل‌های نادیده گرفته شده Git
├── .python-version         # نسخه Python مورد استفاده
├── pyproject.toml          # تنظیمات پروژه و وابستگی‌ها
├── uv.lock                 # قفل وابستگی‌ها (uv)
├── conftest.py             # تنظیمات pytest
├── main.py                 # نقطه ورود اصلی
├── run_tests.py            # اجراکننده تست‌ها
├── README.md               # راهنمای اصلی پروژه
├── QUICKSTART.md           # راهنمای شروع سریع
└── AIOGRAM_VERIFICATION_SUMMARY.md  # خلاصه تأیید aiogram
```

### ⚙️ توضیح فایل‌های پیکربندی

| فایل | هدف | محتوا |
|------|------|-------|
| `.env.example` | نمونه تنظیمات | متغیرهای محیطی مورد نیاز |
| `pyproject.toml` | تنظیمات پروژه | وابستگی‌ها، ابزارها، متادیتا |
| `conftest.py` | تنظیمات تست | Fixtures و تنظیمات pytest |
| `main.py` | نقطه ورود | اجرای اصلی ربات |
| `run_tests.py` | اجرای تست | اسکریپت اجرای تست‌ها |

## 🧪 ساختار تست‌ها

```
tests/
├── README.md                # راهنمای تست‌ها
├── __init__.py              # ماژول تست‌ها
├── conftest.py              # تنظیمات مشترک تست‌ها
├── utils.py                 # ابزارهای کمکی تست
├── test_bot.py              # تست‌های ربات اصلی
├── test_core.py             # تست‌های اجزای core
├── test_integration.py      # تست‌های یکپارچگی
├── test_postgres.py         # تست‌های PostgreSQL
├── test_services.py         # تست‌های سرویس‌ها
├── test_setup.py            # تست‌های راه‌اندازی
└── test_utils.py            # تست‌های ابزارها
```

### 🎯 انواع تست‌ها

| نوع تست | فایل | توضیح |
|---------|------|-------|
| **Unit Tests** | `test_*.py` | تست اجزای مجزا |
| **Integration Tests** | `test_integration.py` | تست تعامل اجزا |
| **Database Tests** | `test_postgres.py` | تست عملیات پایگاه داده |
| **Service Tests** | `test_services.py` | تست سرویس‌ها |
| **Setup Tests** | `test_setup.py` | تست راه‌اندازی |

## 📝 مثال‌ها

```
examples/
├── example_bot.py           # مثال ربات کامل
├── database_switching_demo.py  # نمایش تغییر پایگاه داده
├── logging_demo.py          # نمایش سیستم لاگ‌گیری
├── logging_toggle_demo.py   # تغییر سطح لاگ
└── postgresql_example.py    # مثال PostgreSQL
```

### 📋 توضیح مثال‌ها

| مثال | هدف | کاربرد |
|------|------|--------|
| `example_bot.py` | ربات کامل | نمایش تمام ویژگی‌ها |
| `database_switching_demo.py` | تغییر دیتابیس | نحوه تغییر نوع پایگاه داده |
| `logging_demo.py` | لاگ‌گیری | نمایش سیستم لاگ |
| `logging_toggle_demo.py` | کنترل لاگ | تغییر سطح لاگ در زمان اجرا |
| `postgresql_example.py` | PostgreSQL | استفاده از PostgreSQL |

## 🛠️ ابزارها و اسکریپت‌ها

```
scripts/
└── analyze_logs.py          # تحلیل فایل‌های لاگ
```

### 🔧 ابزارهای کمکی

| اسکریپت | هدف | استفاده |
|---------|------|---------|
| `analyze_logs.py` | تحلیل لاگ‌ها | بررسی و تحلیل فایل‌های لاگ |
| `run_tests.py` | اجرای تست | اجرای خودکار تست‌ها |

## 🎯 نکات مهم ساختار

### ✅ مزایای این ساختار

1. **مدولار بودن**: هر بخش مسئولیت مشخصی دارد
2. **قابلیت توسعه**: آسان برای اضافه کردن ویژگی‌های جدید
3. **تست‌پذیری**: ساختار مناسب برای تست‌نویسی
4. **نگهداری آسان**: کد منظم و قابل فهم
5. **مستندسازی کامل**: مستندات جامع به دو زبان

### 🔄 الگوهای طراحی استفاده شده

1. **Factory Pattern**: در `BotFactory` و `DatabaseFactory`
2. **Strategy Pattern**: در انتخاب نوع پایگاه داده
3. **Observer Pattern**: در سیستم لاگ‌گیری
4. **Singleton Pattern**: در مدیریت تنظیمات
5. **Dependency Injection**: در تزریق وابستگی‌ها

### 📊 آمار پروژه

| بخش | تعداد فایل | خطوط کد (تقریبی) |
|-----|-----------|------------------|
| **Core** | 7 | 1,500+ |
| **Bot** | 5 | 800+ |
| **Utils** | 7 | 600+ |
| **Services** | 3 | 300+ |
| **Tests** | 8 | 1,200+ |
| **Examples** | 5 | 400+ |
| **Docs** | 20+ | 5,000+ |
| **جمع کل** | 55+ | 9,800+ |

## 🚀 نحوه استفاده از ساختار

### 1️⃣ اضافه کردن هندلر جدید
```python
# در bot/handlers/commands.py
@router.message(Command("new_command"))
async def new_command_handler(message: Message):
    await message.answer("پاسخ دستور جدید")
```

### 2️⃣ اضافه کردن ابزار جدید
```python
# در utils/new_utility.py
def new_utility_function():
    """ابزار جدید"""
    pass
```

### 3️⃣ اضافه کردن تست جدید
```python
# در tests/test_new_feature.py
def test_new_feature():
    """تست ویژگی جدید"""
    assert True
```

### 4️⃣ اضافه کردن مستند جدید
```markdown
<!-- در docs/fa/new_guide.md -->
# راهنمای جدید
محتوای راهنما...
```

## 🔍 جستجو در ساختار

برای پیدا کردن فایل یا کد مورد نظر:

1. **هندلرها**: `bot/handlers/`
2. **تنظیمات**: `core/config.py`
3. **پایگاه داده**: `core/database.py`, `core/postgres.py`
4. **ابزارها**: `utils/`
5. **تست‌ها**: `tests/`
6. **مثال‌ها**: `examples/`
7. **مستندات**: `docs/` یا `docs/fa/`

---

**نکته**: این ساختار به‌طور مداوم بهبود می‌یابد. برای آخرین تغییرات، مخزن پروژه را بررسی کنید.