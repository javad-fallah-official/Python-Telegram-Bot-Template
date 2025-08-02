# 📦 راهنمای نصب

> **راه‌اندازی کامل قالب ربات تلگرام پایتون**

## 🎯 پیش‌نیازها

### سیستم‌عامل
- **Windows**: Windows 10/11
- **macOS**: macOS 10.15+
- **Linux**: Ubuntu 20.04+, Debian 10+, CentOS 8+

### نرم‌افزارهای مورد نیاز
- **Python**: 3.13+ (توصیه شده: 3.13.1)
- **Git**: برای کلون کردن پروژه
- **uv**: مدیر بسته‌های سریع (اختیاری ولی توصیه شده)

## 🚀 نصب سریع

### گام 1: دریافت کد منبع
```bash
# کلون کردن مخزن
git clone https://github.com/your-username/Python-Telegram-Bot-Template.git
cd Python-Telegram-Bot-Template
```

### گام 2: نصب وابستگی‌ها

#### روش 1: با uv (توصیه شده)
```bash
# نصب uv (اگر نصب نیست)
pip install uv

# ایجاد محیط مجازی و نصب وابستگی‌ها
uv sync
```

#### روش 2: با pip
```bash
# ایجاد محیط مجازی
python -m venv venv

# فعال‌سازی محیط مجازی
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# نصب وابستگی‌ها
pip install -r requirements.txt
```

### گام 3: تنظیم متغیرهای محیطی
```bash
# کپی کردن فایل نمونه
cp .env.example .env

# ویرایش فایل .env
# Windows:
notepad .env
# macOS/Linux:
nano .env
```

### گام 4: دریافت توکن ربات
1. به [@BotFather](https://t.me/BotFather) در تلگرام پیام دهید
2. دستور `/newbot` را ارسال کنید
3. نام و نام کاربری ربات را انتخاب کنید
4. توکن دریافتی را در فایل `.env` قرار دهید

### گام 5: اجرای ربات
```bash
# اجرای ربات
python main.py
```

## 🔧 نصب تفصیلی

### نصب Python

#### Windows
1. از [python.org](https://python.org) آخرین نسخه Python را دانلود کنید
2. حین نصب، گزینه "Add Python to PATH" را فعال کنید
3. نصب را تکمیل کنید

#### macOS
```bash
# با Homebrew
brew install python@3.13

# یا دانلود از python.org
```

#### Linux (Ubuntu/Debian)
```bash
# بروزرسانی فهرست بسته‌ها
sudo apt update

# نصب Python
sudo apt install python3.13 python3.13-venv python3.13-pip

# ایجاد لینک symbolic
sudo ln -sf /usr/bin/python3.13 /usr/bin/python3
```

### نصب uv (توصیه شده)

#### همه سیستم‌عامل‌ها
```bash
# نصب با pip
pip install uv

# یا نصب مستقیم (Unix)
curl -LsSf https://astral.sh/uv/install.sh | sh

# یا نصب مستقیم (Windows)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

## 🗄️ تنظیم پایگاه داده

### SQLite (پیش‌فرض)
```env
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///bot.db
```

### PostgreSQL
```bash
# نصب PostgreSQL
# Ubuntu/Debian:
sudo apt install postgresql postgresql-contrib

# macOS:
brew install postgresql

# Windows: دانلود از postgresql.org
```

```env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/botdb
```

## 🧪 تست نصب

### تست سریع
```bash
# تست import کردن ماژول‌ها
python -c "import aiogram; print('aiogram:', aiogram.__version__)"
python -c "from core.config import Config; print('Config loaded successfully')"
```

### اجرای تست‌ها
```bash
# اجرای همه تست‌ها
pytest

# اجرای تست‌های خاص
pytest tests/test_bot.py -v

# تست با پوشش کد
pytest --cov=. --cov-report=html
```

## 🔍 عیب‌یابی نصب

### مشکلات رایج

#### خطای "Python not found"
```bash
# بررسی نصب Python
python --version
python3 --version

# اضافه کردن Python به PATH (Windows)
# کنترل پنل > سیستم > تنظیمات پیشرفته > متغیرهای محیطی
```

#### خطای "Permission denied"
```bash
# Linux/macOS: استفاده از sudo
sudo pip install -r requirements.txt

# یا استفاده از --user
pip install --user -r requirements.txt
```

#### خطای "Module not found"
```bash
# بررسی فعال بودن محیط مجازی
which python
which pip

# فعال‌سازی مجدد محیط مجازی
source venv/bin/activate  # Linux/macOS
venv\Scripts\activate     # Windows
```

#### خطای "SSL Certificate"
```bash
# بروزرسانی certificates
pip install --upgrade certifi

# یا غیرفعال کردن SSL (غیرامن)
pip install --trusted-host pypi.org --trusted-host pypi.python.org -r requirements.txt
```

### بررسی وابستگی‌ها
```bash
# نمایش وابستگی‌های نصب شده
pip list

# بررسی وابستگی‌های مورد نیاز
pip check

# نمایش اطلاعات بسته
pip show aiogram
```

## 🔄 بروزرسانی

### بروزرسانی وابستگی‌ها
```bash
# با uv
uv sync --upgrade

# با pip
pip install --upgrade -r requirements.txt
```

### بروزرسانی کد منبع
```bash
# دریافت آخرین تغییرات
git pull origin main

# نصب وابستگی‌های جدید
uv sync  # یا pip install -r requirements.txt
```

## 🐳 نصب با Docker

### Dockerfile
```dockerfile
FROM python:3.13-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["python", "main.py"]
```

### docker-compose.yml
```yaml
version: '3.8'
services:
  bot:
    build: .
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_TYPE=postgresql
      - DATABASE_URL=postgresql://postgres:password@db:5432/botdb
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=botdb
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

### اجرا با Docker
```bash
# ساخت و اجرا
docker-compose up --build

# اجرا در پس‌زمینه
docker-compose up -d
```

## 📋 چک‌لیست نصب

- [ ] Python 3.13+ نصب شده
- [ ] Git نصب شده
- [ ] کد منبع کلون شده
- [ ] محیط مجازی ایجاد شده
- [ ] وابستگی‌ها نصب شده
- [ ] فایل `.env` تنظیم شده
- [ ] توکن ربات دریافت شده
- [ ] پایگاه داده تنظیم شده
- [ ] تست‌ها با موفقیت اجرا شده
- [ ] ربات با موفقیت اجرا شده

## 🆘 دریافت کمک

اگر در هنگام نصب با مشکل مواجه شدید:

1. **مستندات**: [تنظیمات](CONFIGURATION.md)
2. **Issues**: [گزارش مشکل](https://github.com/your-repo/issues)
3. **Discussions**: [پرسش و پاسخ](https://github.com/your-repo/discussions)

## 🔗 مراحل بعدی

پس از نصب موفق:
1. [تنظیمات پیشرفته](CONFIGURATION.md)
2. [ساخت هندلرهای جدید](../features/HANDLERS.md)
3. [تنظیم پایگاه داده](../features/DATABASE.md)
4. [نوشتن تست‌ها](../development/TESTING.md)