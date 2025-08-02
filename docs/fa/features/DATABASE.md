# 🗄️ راهنمای پایگاه داده

> **مدیریت داده‌ها در ربات تلگرام**

## 🎯 درباره پایگاه داده

این قالب از دو نوع پایگاه داده پشتیبانی می‌کند:
- **SQLite**: برای توسعه و پروژه‌های کوچک
- **PostgreSQL**: برای محیط تولید و پروژه‌های بزرگ

## 🏗️ ساختار پایگاه داده

### فایل‌های مرتبط
```
core/
├── database/
│   ├── __init__.py      # کلاس اصلی Database
│   ├── models.py        # مدل‌های جداول
│   ├── sqlite.py        # پیاده‌سازی SQLite
│   └── postgresql.py    # پیاده‌سازی PostgreSQL
└── config.py            # تنظیمات پایگاه داده
```

### مدل‌های جداول
```python
# core/database/models.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    """مدل کاربر"""
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    username = Column(String(255), nullable=True)
    first_name = Column(String(255), nullable=True)
    last_name = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class Message(Base):
    """مدل پیام"""
    __tablename__ = 'messages'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, nullable=False)
    message_id = Column(Integer, nullable=False)
    text = Column(Text, nullable=True)
    message_type = Column(String(50), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserSettings(Base):
    """مدل تنظیمات کاربر"""
    __tablename__ = 'user_settings'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, unique=True, nullable=False)
    language = Column(String(10), default='fa')
    notifications = Column(Boolean, default=True)
    dark_mode = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
```

## ⚙️ تنظیمات پایگاه داده

### SQLite (پیش‌فرض)
```env
# .env
DATABASE_TYPE=sqlite
DATABASE_URL=sqlite:///bot.db
```

### PostgreSQL
```env
# .env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://username:password@localhost:5432/botdb
```

### تنظیمات پیشرفته PostgreSQL
```env
# .env
DATABASE_TYPE=postgresql
DATABASE_URL=postgresql://user:pass@localhost:5432/botdb?sslmode=require
DATABASE_POOL_SIZE=20
DATABASE_MAX_OVERFLOW=30
DATABASE_POOL_TIMEOUT=30
```

## 🔧 کلاس Database

### استفاده اصلی
```python
from core.database import Database

# ایجاد نمونه
db = Database()

# تست اتصال
if db.test_connection():
    print("✅ اتصال به پایگاه داده موفق")
else:
    print("❌ خطا در اتصال به پایگاه داده")
```

### متدهای اصلی
```python
# ایجاد جداول
db.create_tables()

# حذف جداول
db.drop_tables()

# بازنشانی پایگاه داده
db.reset_database()

# بستن اتصال
db.close()
```

## 👥 مدیریت کاربران

### ایجاد کاربر جدید
```python
from core.database import Database

db = Database()

# ایجاد کاربر
user_data = {
    'user_id': 123456789,
    'username': 'john_doe',
    'first_name': 'John',
    'last_name': 'Doe'
}

user = db.create_user(**user_data)
print(f"کاربر ایجاد شد: {user.first_name}")
```

### دریافت اطلاعات کاربر
```python
# دریافت کاربر با ID
user = db.get_user(user_id=123456789)
if user:
    print(f"نام: {user.first_name}")
    print(f"نام کاربری: @{user.username}")
    print(f"تاریخ عضویت: {user.created_at}")

# بررسی وجود کاربر
if db.user_exists(user_id=123456789):
    print("کاربر موجود است")
```

### بروزرسانی کاربر
```python
# بروزرسانی اطلاعات
db.update_user(
    user_id=123456789,
    first_name="احمد",
    last_name="محمدی"
)

# غیرفعال کردن کاربر
db.deactivate_user(user_id=123456789)

# فعال کردن کاربر
db.activate_user(user_id=123456789)
```

### دریافت لیست کاربران
```python
# همه کاربران
all_users = db.get_all_users()

# کاربران فعال
active_users = db.get_active_users()

# کاربران با صفحه‌بندی
users_page = db.get_users_paginated(page=1, per_page=10)

print(f"تعداد کل کاربران: {len(all_users)}")
print(f"تعداد کاربران فعال: {len(active_users)}")
```

## 💬 مدیریت پیام‌ها

### ذخیره پیام
```python
# ذخیره پیام متنی
db.save_message(
    user_id=123456789,
    message_id=12345,
    text="سلام، چطوری؟",
    message_type="text"
)

# ذخیره پیام تصویری
db.save_message(
    user_id=123456789,
    message_id=12346,
    text=None,
    message_type="photo"
)
```

### دریافت پیام‌ها
```python
# آخرین پیام‌های کاربر
recent_messages = db.get_user_messages(
    user_id=123456789,
    limit=10
)

# پیام‌های یک روز گذشته
from datetime import datetime, timedelta
yesterday = datetime.now() - timedelta(days=1)

messages = db.get_messages_since(
    user_id=123456789,
    since=yesterday
)

# جستجو در پیام‌ها
search_results = db.search_messages(
    user_id=123456789,
    query="سلام"
)
```

### آمار پیام‌ها
```python
# تعداد پیام‌های کاربر
message_count = db.get_user_message_count(user_id=123456789)

# تعداد پیام‌های امروز
today_count = db.get_today_message_count(user_id=123456789)

# آمار انواع پیام
stats = db.get_message_type_stats(user_id=123456789)
print(f"پیام متنی: {stats.get('text', 0)}")
print(f"تصویر: {stats.get('photo', 0)}")
print(f"فایل: {stats.get('document', 0)}")
```

## ⚙️ تنظیمات کاربر

### ایجاد و بروزرسانی تنظیمات
```python
# ایجاد تنظیمات پیش‌فرض
db.create_user_settings(user_id=123456789)

# بروزرسانی زبان
db.update_user_setting(
    user_id=123456789,
    setting='language',
    value='en'
)

# تغییر وضعیت اعلان‌ها
db.toggle_notifications(user_id=123456789)

# تغییر حالت شب
db.toggle_dark_mode(user_id=123456789)
```

### دریافت تنظیمات
```python
# دریافت همه تنظیمات
settings = db.get_user_settings(user_id=123456789)
if settings:
    print(f"زبان: {settings.language}")
    print(f"اعلان‌ها: {'فعال' if settings.notifications else 'غیرفعال'}")
    print(f"حالت شب: {'فعال' if settings.dark_mode else 'غیرفعال'}")

# دریافت تنظیم خاص
language = db.get_user_setting(user_id=123456789, setting='language')
print(f"زبان کاربر: {language}")
```

## 📊 آمار و گزارش‌ها

### آمار کلی
```python
# آمار کاربران
user_stats = db.get_user_statistics()
print(f"کل کاربران: {user_stats['total']}")
print(f"کاربران فعال: {user_stats['active']}")
print(f"کاربران جدید امروز: {user_stats['new_today']}")

# آمار پیام‌ها
message_stats = db.get_message_statistics()
print(f"کل پیام‌ها: {message_stats['total']}")
print(f"پیام‌های امروز: {message_stats['today']}")
print(f"میانگین پیام روزانه: {message_stats['daily_average']}")
```

### گزارش‌های تفصیلی
```python
# فعال‌ترین کاربران
top_users = db.get_most_active_users(limit=10)
for user in top_users:
    print(f"{user.first_name}: {user.message_count} پیام")

# آمار روزانه
daily_stats = db.get_daily_statistics(days=7)
for day, stats in daily_stats.items():
    print(f"{day}: {stats['messages']} پیام، {stats['new_users']} کاربر جدید")
```

## 🔄 Migration و Schema

### ایجاد Migration
```python
# core/database/migrations.py
from sqlalchemy import text

class DatabaseMigration:
    def __init__(self, db):
        self.db = db
    
    def migrate_v1_to_v2(self):
        """مهاجرت از نسخه 1 به 2"""
        # اضافه کردن ستون جدید
        self.db.execute(text("""
            ALTER TABLE users 
            ADD COLUMN phone_number VARCHAR(20)
        """))
        
        # ایجاد جدول جدید
        self.db.execute(text("""
            CREATE TABLE user_preferences (
                id SERIAL PRIMARY KEY,
                user_id INTEGER NOT NULL,
                preference_key VARCHAR(100) NOT NULL,
                preference_value TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """))
    
    def rollback_v2_to_v1(self):
        """بازگشت از نسخه 2 به 1"""
        self.db.execute(text("DROP TABLE IF EXISTS user_preferences"))
        self.db.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS phone_number"))
```

### اجرای Migration
```python
from core.database import Database
from core.database.migrations import DatabaseMigration

db = Database()
migration = DatabaseMigration(db)

# اجرای migration
try:
    migration.migrate_v1_to_v2()
    print("✅ Migration موفق")
except Exception as e:
    print(f"❌ خطا در migration: {e}")
    migration.rollback_v2_to_v1()
```

## 🔒 امنیت پایگاه داده

### محافظت از SQL Injection
```python
# ❌ اشتباه - آسیب‌پذیر
def get_user_unsafe(username):
    query = f"SELECT * FROM users WHERE username = '{username}'"
    return db.execute(query)

# ✅ درست - امن
def get_user_safe(username):
    query = text("SELECT * FROM users WHERE username = :username")
    return db.execute(query, {'username': username})
```

### رمزگذاری داده‌های حساس
```python
import hashlib
import secrets

def hash_sensitive_data(data):
    """رمزگذاری داده‌های حساس"""
    salt = secrets.token_hex(16)
    hashed = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
    return f"{salt}:{hashed.hex()}"

def verify_sensitive_data(data, hashed_data):
    """تأیید داده‌های رمزگذاری شده"""
    salt, hash_value = hashed_data.split(':')
    new_hash = hashlib.pbkdf2_hmac('sha256', data.encode(), salt.encode(), 100000)
    return new_hash.hex() == hash_value
```

## 🧪 تست پایگاه داده

### تست واحد
```python
# tests/test_database.py
import pytest
from core.database import Database

@pytest.fixture
def test_db():
    """ایجاد پایگاه داده تست"""
    db = Database(database_url="sqlite:///:memory:")
    db.create_tables()
    yield db
    db.close()

def test_create_user(test_db):
    """تست ایجاد کاربر"""
    user = test_db.create_user(
        user_id=123,
        username="test_user",
        first_name="Test"
    )
    
    assert user.user_id == 123
    assert user.username == "test_user"
    assert user.first_name == "Test"

def test_user_exists(test_db):
    """تست بررسی وجود کاربر"""
    test_db.create_user(user_id=123, first_name="Test")
    
    assert test_db.user_exists(123) == True
    assert test_db.user_exists(456) == False
```

### تست یکپارچگی
```python
def test_user_message_flow(test_db):
    """تست جریان کامل کاربر و پیام"""
    # ایجاد کاربر
    user = test_db.create_user(user_id=123, first_name="Test")
    
    # ذخیره پیام
    test_db.save_message(
        user_id=123,
        message_id=1,
        text="سلام",
        message_type="text"
    )
    
    # بررسی آمار
    count = test_db.get_user_message_count(123)
    assert count == 1
    
    # دریافت پیام‌ها
    messages = test_db.get_user_messages(123)
    assert len(messages) == 1
    assert messages[0].text == "سلام"
```

## 🔧 بهینه‌سازی عملکرد

### ایندکس‌گذاری
```sql
-- ایندکس‌های مهم
CREATE INDEX idx_users_user_id ON users(user_id);
CREATE INDEX idx_messages_user_id ON messages(user_id);
CREATE INDEX idx_messages_created_at ON messages(created_at);
CREATE INDEX idx_user_settings_user_id ON user_settings(user_id);
```

### Connection Pooling
```python
# core/database/postgresql.py
from sqlalchemy import create_engine
from sqlalchemy.pool import QueuePool

class PostgreSQLDatabase:
    def __init__(self, database_url):
        self.engine = create_engine(
            database_url,
            poolclass=QueuePool,
            pool_size=20,
            max_overflow=30,
            pool_timeout=30,
            pool_recycle=3600
        )
```

### کش کردن
```python
from functools import lru_cache
from datetime import datetime, timedelta

class Database:
    @lru_cache(maxsize=1000)
    def get_user_cached(self, user_id):
        """دریافت کاربر با کش"""
        return self._get_user_from_db(user_id)
    
    def clear_user_cache(self, user_id):
        """پاک کردن کش کاربر"""
        self.get_user_cached.cache_clear()
```

## 📋 بهترین شیوه‌ها

### 1. طراحی Schema
- استفاده از کلیدهای خارجی
- نرمال‌سازی مناسب
- انتخاب نوع داده مناسب

### 2. مدیریت اتصال
- استفاده از Connection Pool
- بستن اتصالات غیرضروری
- مدیریت timeout ها

### 3. امنیت
- اعتبارسنجی ورودی‌ها
- استفاده از Prepared Statements
- رمزگذاری داده‌های حساس

### 4. عملکرد
- ایندکس‌گذاری مناسب
- محدود کردن نتایج
- استفاده از کش

## 🔗 مراحل بعدی

- [تنظیم PostgreSQL پیشرفته](../advanced/POSTGRESQL.md)
- [مهاجرت پایگاه داده](../migration/DATABASE_MIGRATION.md)
- [نوشتن تست‌ها](../development/TESTING.md)