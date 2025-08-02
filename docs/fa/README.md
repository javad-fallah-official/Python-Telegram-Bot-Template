# 📚 مستندات قالب ربات تلگرام پایتون

> **نسخه فارسی مستندات**  
> [English Documentation](../README.md) | **فارسی**

## 🎯 درباره این پروژه

قالب جامع و آماده برای ساخت ربات‌های تلگرام با استفاده از Python و aiogram. این قالب شامل تمام ابزارها و ساختارهای لازم برای توسعه ربات‌های حرفه‌ای است.

## 🚀 شروع سریع

### پیش‌نیازها
- Python 3.13+
- حساب کاربری تلگرام
- توکن ربات از [@BotFather](https://t.me/BotFather)

### نصب سریع
```bash
# کلون کردن پروژه
git clone <repository-url>
cd Python-Telegram-Bot-Template

# نصب وابستگی‌ها با uv (توصیه شده)
uv sync

# یا با pip
pip install -r requirements.txt

# تنظیم متغیرهای محیطی
cp .env.example .env
# ویرایش فایل .env و اضافه کردن توکن ربات
```

## 📖 فهرست مطالب

### 🏗️ ساختار پروژه
- [📋 ساختار کامل پروژه](PROJECT_STRUCTURE.md) - راهنمای جامع ساختار کد و مستندات

### 🛠️ راه‌اندازی و تنظیمات
- [📦 راهنمای نصب](setup/INSTALLATION.md) - نصب کامل و پیکربندی
- [⚙️ تنظیمات](setup/CONFIGURATION.md) - متغیرهای محیطی و پیکربندی

### 🎨 ویژگی‌های اصلی
- [🗄️ پایگاه داده](features/DATABASE.md) - SQLite و PostgreSQL
- [🎛️ هندلرها](features/HANDLERS.md) - مدیریت دستورات و پیام‌ها

### 🔄 راهنماهای مهاجرت
- [🤖 مهاجرت aiogram](migration/AIOGRAM_MIGRATION.md) - ارتقا به aiogram 3.x
- [🗄️ مهاجرت پایگاه داده](migration/DATABASE_MIGRATION.md) - تغییر نوع پایگاه داده
- [🧪 مهاجرت تست‌ها](migration/TEST_MIGRATION.md) - بروزرسانی تست‌ها

### 🔧 موضوعات پیشرفته
- [🐘 PostgreSQL](advanced/POSTGRESQL.md) - تنظیمات پیشرفته PostgreSQL

### 👨‍💻 توسعه
- [🧪 تست‌ها](development/TESTING.md) - راهنمای تست‌نویسی
- [🤝 مشارکت](development/CONTRIBUTING.md) - راهنمای مشارکت در پروژه

### 📋 مرجع API
- [🎛️ هندلرها](api/HANDLERS.md) - API هندلرهای ربات
- [🗄️ پایگاه داده](api/DATABASE.md) - API لایه پایگاه داده
- [🛠️ ابزارها](api/UTILITIES.md) - ابزارهای کمکی
- [🔗 میدل‌ویر](api/MIDDLEWARE.md) - سیستم میدل‌ویر

## 🔍 جستجوی سریع

| موضوع | مستند | توضیح |
|-------|--------|-------|
| ساختار پروژه | [ساختار](PROJECT_STRUCTURE.md) | راهنمای کامل ساختار کد و مستندات |
| نصب اولیه | [نصب](setup/INSTALLATION.md) | راه‌اندازی محیط توسعه |
| تنظیم توکن | [تنظیمات](setup/CONFIGURATION.md) | پیکربندی ربات |
| ساخت دستور | [هندلرها](features/HANDLERS.md) | اضافه کردن دستورات جدید |
| پایگاه داده | [دیتابیس](features/DATABASE.md) | کار با SQLite/PostgreSQL |
| تست‌نویسی | [تست‌ها](development/TESTING.md) | نوشتن و اجرای تست‌ها |
| مشارکت | [مشارکت](development/CONTRIBUTING.md) | کمک به پروژه |

## 🏗️ ساختار مستندات

```
docs/fa/
├── README.md                 # این فایل
├── setup/                    # راه‌اندازی و نصب
│   ├── INSTALLATION.md       # راهنمای نصب
│   └── CONFIGURATION.md      # تنظیمات
├── features/                 # ویژگی‌های اصلی
│   ├── DATABASE.md          # پایگاه داده
│   └── HANDLERS.md          # هندلرها
├── migration/               # راهنماهای مهاجرت
│   ├── AIOGRAM_MIGRATION.md # مهاجرت aiogram
│   ├── DATABASE_MIGRATION.md# مهاجرت دیتابیس
│   └── TEST_MIGRATION.md    # مهاجرت تست‌ها
├── advanced/                # موضوعات پیشرفته
│   └── POSTGRESQL.md        # PostgreSQL پیشرفته
├── development/             # توسعه
│   ├── TESTING.md          # تست‌نویسی
│   └── CONTRIBUTING.md     # مشارکت
└── api/                     # مرجع API
    ├── HANDLERS.md         # API هندلرها
    ├── DATABASE.md         # API پایگاه داده
    ├── UTILITIES.md        # API ابزارها
    └── MIDDLEWARE.md       # API میدل‌ویر
```

## 🎯 ویژگی‌های کلیدی

### 🤖 aiogram 3.x
- پشتیبانی کامل از آخرین نسخه aiogram
- الگوهای مدرن async/await
- سیستم فیلتر پیشرفته

### 🗄️ پایگاه داده انعطاف‌پذیر
- پشتیبانی از SQLite و PostgreSQL
- تغییر آسان نوع پایگاه داده
- مدیریت خودکار اتصالات

### 🔧 ساختار مدولار
- جداسازی واضح مسئولیت‌ها
- الگوی Factory برای ساخت ربات
- سیستم میدل‌ویر قابل توسعه

### 🧪 تست جامع
- پوشش کامل تست‌ها
- Mock کردن اجزای aiogram
- تست‌های یکپارچگی

### 📝 لاگ‌گیری پیشرفته
- سطوح مختلف لاگ
- فرمت‌بندی زیبا
- ذخیره در فایل

## 🚦 حالت‌های اجرا

### 📡 Polling (پیش‌فرض)
```bash
# اجرا در حالت polling
python main.py
```

### 🌐 Webhook
```bash
# تنظیم متغیر محیطی
export BOT_MODE=webhook
export WEBHOOK_URL=https://yourdomain.com/webhook

# اجرا در حالت webhook
python main.py
```

## 🔧 تنظیمات سریع

### متغیرهای ضروری
```env
BOT_TOKEN=your_bot_token_here
BOT_MODE=polling
DATABASE_TYPE=sqlite
```

### متغیرهای اختیاری
```env
DEBUG=true
LOG_LEVEL=INFO
ADMIN_USER_IDS=123456789,987654321
```

## 🤝 مشارکت

ما از مشارکت شما استقبال می‌کنیم! لطفاً [راهنمای مشارکت](development/CONTRIBUTING.md) را مطالعه کنید.

## 📄 مجوز

این پروژه تحت مجوز MIT منتشر شده است.

## 🆘 دریافت کمک

- 📖 [مستندات کامل](README.md)
- 🐛 [گزارش باگ](https://github.com/your-repo/issues)
- 💡 [درخواست ویژگی](https://github.com/your-repo/issues)
- 💬 [بحث و گفتگو](https://github.com/your-repo/discussions)

---

**نکته**: این مستندات به‌طور مداوم بروزرسانی می‌شوند. برای آخرین تغییرات، [مخزن پروژه](https://github.com/your-repo) را بررسی کنید.