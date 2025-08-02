# ⚙️ راهنمای تنظیمات

> **پیکربندی کامل ربات تلگرام**

## 🎯 درباره تنظیمات

این راهنما شامل تمام تنظیمات قابل انجام برای ربات تلگرام است. تنظیمات از طریق متغیرهای محیطی (Environment Variables) و فایل `.env` انجام می‌شود.

## 📁 فایل .env

### ایجاد فایل تنظیمات
```bash
# کپی کردن فایل نمونه
cp .env.example .env

# ویرایش فایل
nano .env  # Linux/macOS
notepad .env  # Windows
```

### ساختار فایل .env
```env
# === تنظیمات اصلی ربات ===
BOT_TOKEN=your_bot_token_here
BOT_USERNAME=your_bot_username
BOT_MODE=polling

# === تنظیمات Webhook ===
WEBHOOK_URL=https://yourdomain.com/webhook
WEBHOOK_PATH=/webhook
WEBHOOK_SECRET_TOKEN=your_secret_token
WEBHOOK_HOST=0.0.0.0
WEBHOOK_PORT=8080

# === تنظیمات پایگاه داده ===
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///bot.db

# === تنظیمات لاگ و دیباگ ===
DEBUG=false
LOG_LEVEL=INFO

# === تنظیمات مدیریت ===
ADMIN_USER_IDS=123456789,987654321
```

## 🤖 تنظیمات ربات

### BOT_TOKEN (ضروری)
```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
```
- **توضیح**: توکن ربات از [@BotFather](https://t.me/BotFather)
- **نوع**: رشته
- **مثال**: `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz`

### BOT_USERNAME (اختیاری)
```env
BOT_USERNAME=my_awesome_bot
```
- **توضیح**: نام کاربری ربات (بدون @)
- **نوع**: رشته
- **پیش‌فرض**: خودکار از API تلگرام

### BOT_MODE (اختیاری)
```env
BOT_MODE=polling  # یا webhook
```
- **توضیح**: حالت اجرای ربات
- **مقادیر مجاز**: `polling`, `webhook`
- **پیش‌فرض**: `polling`

## 🌐 تنظیمات Webhook

### WEBHOOK_URL (برای webhook)
```env
WEBHOOK_URL=https://yourdomain.com/webhook
```
- **توضیح**: آدرس عمومی webhook
- **نوع**: URL
- **الزامی**: فقط در حالت webhook

### WEBHOOK_PATH (اختیاری)
```env
WEBHOOK_PATH=/webhook
```
- **توضیح**: مسیر endpoint webhook
- **نوع**: رشته
- **پیش‌فرض**: `/webhook`

### WEBHOOK_SECRET_TOKEN (توصیه شده)
```env
WEBHOOK_SECRET_TOKEN=your_very_secure_secret_token
```
- **توضیح**: توکن امنیتی webhook
- **نوع**: رشته
- **توصیه**: استفاده از رشته تصادفی قوی

### WEBHOOK_HOST (اختیاری)
```env
WEBHOOK_HOST=0.0.0.0
```
- **توضیح**: آدرس IP برای bind کردن سرور
- **نوع**: IP Address
- **پیش‌فرض**: `0.0.0.0`

### WEBHOOK_PORT (اختیاری)
```env
WEBHOOK_PORT=8080
```
- **توضیح**: پورت سرور webhook
- **نوع**: عدد صحیح
- **پیش‌فرض**: `8080`

## 🗄️ تنظیمات پایگاه داده

### DATABASE_TYPE (اختیاری)
```env
DATABASE_TYPE=sqlite  # یا postgresql
```
- **توضیح**: نوع پایگاه داده
- **مقادیر مجاز**: `sqlite`, `postgresql`
- **پیش‌فرض**: `sqlite`

### DATABASE_URL (اختیاری)
```env
# SQLite
DATABASE_URL=sqlite:///bot.db

# PostgreSQL
DATABASE_URL=postgresql://user:password@localhost:5432/dbname
```
- **توضیح**: رشته اتصال به پایگاه داده
- **نوع**: Database URL
- **پیش‌فرض**: `sqlite:///bot.db`

## 🔍 تنظیمات لاگ و دیباگ

### DEBUG (اختیاری)
```env
DEBUG=true  # یا false
```
- **توضیح**: فعال‌سازی حالت دیباگ
- **نوع**: Boolean
- **پیش‌فرض**: `false`

### LOG_LEVEL (اختیاری)
```env
LOG_LEVEL=INFO
```
- **توضیح**: سطح لاگ‌گیری
- **مقادیر مجاز**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`
- **پیش‌فرض**: `INFO`

## 👥 تنظیمات مدیریت

### ADMIN_USER_IDS (اختیاری)
```env
ADMIN_USER_IDS=123456789,987654321,555666777
```
- **توضیح**: لیست ID کاربران مدیر
- **نوع**: لیست اعداد جدا شده با کاما
- **مثال**: `123456789,987654321`

## 🔧 تنظیمات پیشرفته

### تنظیم متغیرهای محیطی در سیستم

#### Windows
```cmd
# PowerShell
$env:BOT_TOKEN="your_token_here"

# Command Prompt
set BOT_TOKEN=your_token_here
```

#### Linux/macOS
```bash
# موقت (برای جلسه فعلی)
export BOT_TOKEN="your_token_here"

# دائمی (در ~/.bashrc یا ~/.zshrc)
echo 'export BOT_TOKEN="your_token_here"' >> ~/.bashrc
source ~/.bashrc
```

### تنظیمات Docker
```yaml
# docker-compose.yml
version: '3.8'
services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - BOT_MODE=webhook
      - WEBHOOK_URL=https://yourdomain.com/webhook
      - DATABASE_TYPE=postgresql
      - DATABASE_URL=postgresql://postgres:password@db:5432/botdb
```

## 🏗️ کلاس Config

### استفاده در کد
```python
from core.config import Config

# بارگذاری تنظیمات
config = Config()

# دسترسی به تنظیمات
print(f"Bot Token: {config.BOT_TOKEN}")
print(f"Database Type: {config.DATABASE_TYPE}")
print(f"Debug Mode: {config.DEBUG}")

# اعتبارسنجی تنظیمات
config.validate()
```

### متدهای کلاس Config
```python
# بررسی حالت webhook
if config.is_webhook_mode():
    print("Running in webhook mode")

# بررسی حالت دیباگ
if config.is_debug():
    print("Debug mode is enabled")

# دریافت URL پایگاه داده
db_url = config.get_database_url()

# دریافت لیست مدیران
admin_ids = config.get_admin_user_ids()
```

## 🔒 امنیت تنظیمات

### بهترین شیوه‌ها

#### 1. محافظت از توکن‌ها
```bash
# هرگز توکن‌ها را در کد commit نکنید
echo ".env" >> .gitignore
echo "*.env" >> .gitignore
```

#### 2. استفاده از توکن‌های قوی
```python
import secrets

# تولید توکن امنیتی
secret_token = secrets.token_urlsafe(32)
print(f"WEBHOOK_SECRET_TOKEN={secret_token}")
```

#### 3. محدود کردن دسترسی فایل
```bash
# تنظیم مجوزهای فایل .env
chmod 600 .env
```

### متغیرهای حساس
این متغیرها را هرگز در کد یا مخزن عمومی قرار ندهید:
- `BOT_TOKEN`
- `WEBHOOK_SECRET_TOKEN`
- `DATABASE_URL` (اگر شامل رمز عبور باشد)

## 🧪 تست تنظیمات

### اسکریپت تست
```python
#!/usr/bin/env python3
"""تست تنظیمات ربات"""

from core.config import Config

def test_config():
    """تست بارگذاری و اعتبارسنجی تنظیمات"""
    try:
        config = Config()
        config.validate()
        print("✅ تنظیمات معتبر است")
        
        print(f"🤖 Bot Mode: {config.BOT_MODE}")
        print(f"🗄️ Database: {config.DATABASE_TYPE}")
        print(f"🔍 Debug: {config.DEBUG}")
        print(f"📊 Log Level: {config.LOG_LEVEL}")
        
    except Exception as e:
        print(f"❌ خطا در تنظیمات: {e}")
        return False
    
    return True

if __name__ == "__main__":
    test_config()
```

### اجرای تست
```bash
python test_config.py
```

## 🔄 تنظیمات محیط‌های مختلف

### محیط توسعه (Development)
```env
# .env.development
DEBUG=true
LOG_LEVEL=DEBUG
BOT_MODE=polling
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///dev_bot.db
```

### محیط تولید (Production)
```env
# .env.production
DEBUG=false
LOG_LEVEL=INFO
BOT_MODE=webhook
WEBHOOK_URL=https://yourdomain.com/webhook
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@localhost:5432/prod_db
```

### محیط تست (Testing)
```env
# .env.testing
DEBUG=true
LOG_LEVEL=DEBUG
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///:memory:
```

## 📋 چک‌لیست تنظیمات

### تنظیمات ضروری
- [ ] `BOT_TOKEN` تنظیم شده
- [ ] فایل `.env` ایجاد شده
- [ ] تنظیمات اعتبارسنجی شده

### تنظیمات Webhook (در صورت نیاز)
- [ ] `WEBHOOK_URL` تنظیم شده
- [ ] `WEBHOOK_SECRET_TOKEN` تنظیم شده
- [ ] SSL certificate معتبر
- [ ] دامنه قابل دسترس

### تنظیمات پایگاه داده
- [ ] `DATABASE_TYPE` انتخاب شده
- [ ] `DATABASE_URL` تنظیم شده
- [ ] اتصال به پایگاه داده تست شده

### تنظیمات امنیتی
- [ ] فایل `.env` در `.gitignore` قرار دارد
- [ ] توکن‌ها امن هستند
- [ ] مجوزهای فایل تنظیم شده

## 🆘 عیب‌یابی تنظیمات

### خطاهای رایج

#### "BOT_TOKEN not found"
```bash
# بررسی وجود فایل .env
ls -la .env

# بررسی محتوای فایل
cat .env | grep BOT_TOKEN
```

#### "Invalid database URL"
```python
# تست اتصال پایگاه داده
from core.database import Database

db = Database()
db.test_connection()
```

#### "Webhook SSL Error"
```bash
# بررسی SSL certificate
curl -I https://yourdomain.com/webhook
```

## 🔗 مراحل بعدی

پس از تنظیم موفق:
1. [ساخت هندلرهای جدید](../features/HANDLERS.md)
2. [تنظیم پایگاه داده](../features/DATABASE.md)
3. [راه‌اندازی تست‌ها](../development/TESTING.md)
4. [استقرار در production](../advanced/DEPLOYMENT.md)