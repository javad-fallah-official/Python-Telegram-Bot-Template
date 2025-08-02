# ⚡ راهنمای بهینه‌سازی عملکرد

> **بهینه‌سازی کامل ربات تلگرام برای عملکرد بالا و مقیاس‌پذیری**

## 🎯 درباره بهینه‌سازی

این راهنما شامل تمام تکنیک‌های بهینه‌سازی عملکرد ربات تلگرام از جمله بهینه‌سازی کد، پایگاه داده، حافظه، شبکه و مقیاس‌پذیری است.

## 📊 اندازه‌گیری عملکرد

### 1. Profiling و Benchmarking

#### CPU Profiling
```python
# tools/profiler.py
import cProfile
import pstats
import io
from functools import wraps
import time
import asyncio

def profile_function(func):
    """Decorator برای profiling توابع"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        
        result = func(*args, **kwargs)
        
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        
        print(f"Profile for {func.__name__}:")
        print(s.getvalue())
        
        return result
    return wrapper

def profile_async_function(func):
    """Decorator برای profiling توابع async"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        pr = cProfile.Profile()
        pr.enable()
        
        result = await func(*args, **kwargs)
        
        pr.disable()
        s = io.StringIO()
        ps = pstats.Stats(pr, stream=s).sort_stats('cumulative')
        ps.print_stats()
        
        print(f"Async Profile for {func.__name__}:")
        print(s.getvalue())
        
        return result
    return wrapper

# استفاده
@profile_async_function
async def process_message(message):
    # پردازش پیام
    await asyncio.sleep(0.1)
    return "processed"
```

#### Memory Profiling
```python
# tools/memory_profiler.py
import tracemalloc
import psutil
import os
from functools import wraps

class MemoryProfiler:
    """کلاس profiling حافظه"""
    
    def __init__(self):
        self.snapshots = []
    
    def start_tracing(self):
        """شروع ردیابی حافظه"""
        tracemalloc.start()
    
    def take_snapshot(self, name: str):
        """گرفتن snapshot از حافظه"""
        snapshot = tracemalloc.take_snapshot()
        self.snapshots.append((name, snapshot))
    
    def compare_snapshots(self, name1: str, name2: str):
        """مقایسه دو snapshot"""
        snap1 = next((s for n, s in self.snapshots if n == name1), None)
        snap2 = next((s for n, s in self.snapshots if n == name2), None)
        
        if snap1 and snap2:
            top_stats = snap2.compare_to(snap1, 'lineno')
            
            print(f"مقایسه حافظه: {name1} -> {name2}")
            for stat in top_stats[:10]:
                print(stat)
    
    def get_current_memory_usage(self):
        """دریافت مصرف فعلی حافظه"""
        process = psutil.Process(os.getpid())
        memory_info = process.memory_info()
        
        return {
            'rss': memory_info.rss / 1024 / 1024,  # MB
            'vms': memory_info.vms / 1024 / 1024,  # MB
            'percent': process.memory_percent()
        }

def memory_usage(func):
    """Decorator برای اندازه‌گیری مصرف حافظه"""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        profiler = MemoryProfiler()
        
        # حافظه قبل از اجرا
        before = profiler.get_current_memory_usage()
        
        result = await func(*args, **kwargs)
        
        # حافظه بعد از اجرا
        after = profiler.get_current_memory_usage()
        
        print(f"Memory usage for {func.__name__}:")
        print(f"  Before: {before['rss']:.2f} MB")
        print(f"  After: {after['rss']:.2f} MB")
        print(f"  Diff: {after['rss'] - before['rss']:.2f} MB")
        
        return result
    return wrapper
```

#### Performance Monitoring
```python
# monitoring/performance.py
import time
import asyncio
from collections import defaultdict, deque
from datetime import datetime, timedelta
import statistics

class PerformanceMonitor:
    """مانیتور عملکرد"""
    
    def __init__(self, window_size: int = 1000):
        self.window_size = window_size
        self.metrics = defaultdict(lambda: deque(maxlen=window_size))
        self.counters = defaultdict(int)
    
    def record_timing(self, operation: str, duration: float):
        """ثبت زمان عملیات"""
        self.metrics[f"{operation}_timing"].append(duration)
    
    def increment_counter(self, counter: str):
        """افزایش شمارنده"""
        self.counters[counter] += 1
    
    def get_stats(self, operation: str) -> dict:
        """دریافت آمار عملیات"""
        timings = list(self.metrics[f"{operation}_timing"])
        
        if not timings:
            return {}
        
        return {
            'count': len(timings),
            'avg': statistics.mean(timings),
            'median': statistics.median(timings),
            'min': min(timings),
            'max': max(timings),
            'p95': statistics.quantiles(timings, n=20)[18] if len(timings) > 20 else max(timings),
            'p99': statistics.quantiles(timings, n=100)[98] if len(timings) > 100 else max(timings)
        }
    
    def get_throughput(self, counter: str, window_minutes: int = 5) -> float:
        """محاسبه throughput"""
        # این یک پیاده‌سازی ساده است
        # در عمل باید از time-based windows استفاده کرد
        return self.counters[counter] / window_minutes

# Global monitor instance
perf_monitor = PerformanceMonitor()

def monitor_performance(operation: str):
    """Decorator برای مانیتورینگ عملکرد"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            
            try:
                result = await func(*args, **kwargs)
                perf_monitor.increment_counter(f"{operation}_success")
                return result
            except Exception as e:
                perf_monitor.increment_counter(f"{operation}_error")
                raise
            finally:
                duration = time.time() - start_time
                perf_monitor.record_timing(operation, duration)
        
        return wrapper
    return decorator
```

## 🚀 بهینه‌سازی کد

### 1. Async/Await Optimization

#### بهینه‌سازی Concurrent Operations
```python
# optimizations/async_utils.py
import asyncio
from typing import List, Callable, Any
import aiohttp
from functools import wraps

class AsyncBatch:
    """پردازش batch async"""
    
    def __init__(self, batch_size: int = 10, delay: float = 0.1):
        self.batch_size = batch_size
        self.delay = delay
    
    async def process_batch(self, items: List[Any], processor: Callable):
        """پردازش batch از آیتم‌ها"""
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            
            # پردازش موازی batch
            batch_tasks = [processor(item) for item in batch]
            batch_results = await asyncio.gather(*batch_tasks, return_exceptions=True)
            
            results.extend(batch_results)
            
            # تاخیر بین batch ها
            if i + self.batch_size < len(items):
                await asyncio.sleep(self.delay)
        
        return results

async def send_messages_optimized(bot, chat_ids: List[int], text: str):
    """ارسال بهینه پیام به چندین کاربر"""
    
    async def send_single_message(chat_id: int):
        try:
            return await bot.send_message(chat_id, text)
        except Exception as e:
            return f"Error for {chat_id}: {e}"
    
    # استفاده از batch processing
    batch_processor = AsyncBatch(batch_size=20, delay=0.05)
    results = await batch_processor.process_batch(chat_ids, send_single_message)
    
    return results

# Connection pooling برای HTTP requests
class OptimizedHTTPClient:
    """HTTP client بهینه شده"""
    
    def __init__(self):
        self.connector = aiohttp.TCPConnector(
            limit=100,  # حداکثر connection
            limit_per_host=30,  # حداکثر connection per host
            ttl_dns_cache=300,  # DNS cache TTL
            use_dns_cache=True,
            keepalive_timeout=30,
            enable_cleanup_closed=True
        )
        
        self.timeout = aiohttp.ClientTimeout(
            total=30,
            connect=10,
            sock_read=10
        )
        
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=self.timeout
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get(self, url: str, **kwargs):
        """GET request بهینه"""
        async with self.session.get(url, **kwargs) as response:
            return await response.json()
    
    async def post(self, url: str, **kwargs):
        """POST request بهینه"""
        async with self.session.post(url, **kwargs) as response:
            return await response.json()
```

#### Task Management
```python
# optimizations/task_manager.py
import asyncio
import weakref
from typing import Set, Optional
import logging

class TaskManager:
    """مدیریت task های async"""
    
    def __init__(self):
        self._tasks: Set[asyncio.Task] = set()
        self._background_tasks: Set[asyncio.Task] = set()
    
    def create_task(self, coro, *, name: Optional[str] = None, background: bool = False) -> asyncio.Task:
        """ایجاد task با مدیریت خودکار"""
        task = asyncio.create_task(coro, name=name)
        
        if background:
            self._background_tasks.add(task)
            task.add_done_callback(self._background_tasks.discard)
        else:
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
        
        # Log کردن exception ها
        task.add_done_callback(self._log_task_exception)
        
        return task
    
    def _log_task_exception(self, task: asyncio.Task):
        """Log کردن exception های task"""
        if task.done() and not task.cancelled():
            exception = task.exception()
            if exception:
                logging.error(f"Task {task.get_name()} failed: {exception}")
    
    async def shutdown(self, timeout: float = 10.0):
        """خاموش کردن تمام task ها"""
        # لغو task های معمولی
        for task in self._tasks:
            task.cancel()
        
        # انتظار برای تکمیل
        if self._tasks:
            await asyncio.wait(self._tasks, timeout=timeout)
        
        # لغو task های background
        for task in self._background_tasks:
            task.cancel()
        
        if self._background_tasks:
            await asyncio.wait(self._background_tasks, timeout=timeout)
    
    def get_running_tasks_count(self) -> dict:
        """دریافت تعداد task های در حال اجرا"""
        return {
            'normal_tasks': len(self._tasks),
            'background_tasks': len(self._background_tasks),
            'total': len(self._tasks) + len(self._background_tasks)
        }

# Global task manager
task_manager = TaskManager()
```

### 2. Caching Strategies

#### Memory Caching
```python
# optimizations/cache.py
import asyncio
import time
from typing import Any, Optional, Callable, Dict
from functools import wraps
import weakref
import pickle
import hashlib

class MemoryCache:
    """Cache حافظه با TTL"""
    
    def __init__(self, default_ttl: int = 300, max_size: int = 1000):
        self.default_ttl = default_ttl
        self.max_size = max_size
        self._cache: Dict[str, tuple] = {}  # key: (value, expire_time)
        self._access_times: Dict[str, float] = {}
    
    def _is_expired(self, key: str) -> bool:
        """بررسی انقضای کلید"""
        if key not in self._cache:
            return True
        
        _, expire_time = self._cache[key]
        return time.time() > expire_time
    
    def _evict_expired(self):
        """حذف آیتم‌های منقضی شده"""
        current_time = time.time()
        expired_keys = [
            key for key, (_, expire_time) in self._cache.items()
            if current_time > expire_time
        ]
        
        for key in expired_keys:
            self._cache.pop(key, None)
            self._access_times.pop(key, None)
    
    def _evict_lru(self):
        """حذف آیتم‌های کمتر استفاده شده (LRU)"""
        if len(self._cache) <= self.max_size:
            return
        
        # مرتب‌سازی بر اساس زمان دسترسی
        sorted_keys = sorted(
            self._access_times.items(),
            key=lambda x: x[1]
        )
        
        # حذف قدیمی‌ترین آیتم‌ها
        keys_to_remove = sorted_keys[:len(self._cache) - self.max_size]
        for key, _ in keys_to_remove:
            self._cache.pop(key, None)
            self._access_times.pop(key, None)
    
    def get(self, key: str) -> Optional[Any]:
        """دریافت از cache"""
        if self._is_expired(key):
            self._cache.pop(key, None)
            self._access_times.pop(key, None)
            return None
        
        self._access_times[key] = time.time()
        value, _ = self._cache[key]
        return value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None):
        """تنظیم در cache"""
        if ttl is None:
            ttl = self.default_ttl
        
        expire_time = time.time() + ttl
        self._cache[key] = (value, expire_time)
        self._access_times[key] = time.time()
        
        # پاکسازی
        self._evict_expired()
        self._evict_lru()
    
    def delete(self, key: str):
        """حذف از cache"""
        self._cache.pop(key, None)
        self._access_times.pop(key, None)
    
    def clear(self):
        """پاک کردن کامل cache"""
        self._cache.clear()
        self._access_times.clear()
    
    def stats(self) -> dict:
        """آمار cache"""
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hit_ratio': getattr(self, '_hits', 0) / max(getattr(self, '_requests', 1), 1)
        }

# Global cache instance
memory_cache = MemoryCache()

def cached(ttl: int = 300, key_func: Optional[Callable] = None):
    """Decorator برای caching"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # تولید کلید cache
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # استفاده از hash args و kwargs
                key_data = pickle.dumps((args, sorted(kwargs.items())))
                cache_key = f"{func.__name__}:{hashlib.md5(key_data).hexdigest()}"
            
            # بررسی cache
            cached_result = memory_cache.get(cache_key)
            if cached_result is not None:
                return cached_result
            
            # اجرای تابع و ذخیره در cache
            result = await func(*args, **kwargs)
            memory_cache.set(cache_key, result, ttl)
            
            return result
        return wrapper
    return decorator
```

#### Redis Caching
```python
# optimizations/redis_cache.py
import redis.asyncio as redis
import json
import pickle
from typing import Any, Optional, Union
import logging

class RedisCache:
    """Redis cache با قابلیت‌های پیشرفته"""
    
    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        self.redis_url = redis_url
        self.redis_client = None
    
    async def connect(self):
        """اتصال به Redis"""
        self.redis_client = redis.from_url(
            self.redis_url,
            encoding="utf-8",
            decode_responses=False,  # برای pickle
            max_connections=20,
            retry_on_timeout=True
        )
    
    async def disconnect(self):
        """قطع اتصال"""
        if self.redis_client:
            await self.redis_client.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """دریافت از Redis"""
        try:
            data = await self.redis_client.get(key)
            if data:
                return pickle.loads(data)
            return None
        except Exception as e:
            logging.error(f"Redis get error: {e}")
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 300):
        """تنظیم در Redis"""
        try:
            data = pickle.dumps(value)
            await self.redis_client.setex(key, ttl, data)
        except Exception as e:
            logging.error(f"Redis set error: {e}")
    
    async def delete(self, key: str):
        """حذف از Redis"""
        try:
            await self.redis_client.delete(key)
        except Exception as e:
            logging.error(f"Redis delete error: {e}")
    
    async def exists(self, key: str) -> bool:
        """بررسی وجود کلید"""
        try:
            return await self.redis_client.exists(key) > 0
        except Exception as e:
            logging.error(f"Redis exists error: {e}")
            return False
    
    async def increment(self, key: str, amount: int = 1) -> int:
        """افزایش مقدار"""
        try:
            return await self.redis_client.incrby(key, amount)
        except Exception as e:
            logging.error(f"Redis increment error: {e}")
            return 0
    
    async def get_many(self, keys: list) -> dict:
        """دریافت چندین کلید"""
        try:
            values = await self.redis_client.mget(keys)
            result = {}
            for key, value in zip(keys, values):
                if value:
                    result[key] = pickle.loads(value)
            return result
        except Exception as e:
            logging.error(f"Redis get_many error: {e}")
            return {}
    
    async def set_many(self, mapping: dict, ttl: int = 300):
        """تنظیم چندین کلید"""
        try:
            pipe = self.redis_client.pipeline()
            for key, value in mapping.items():
                data = pickle.dumps(value)
                pipe.setex(key, ttl, data)
            await pipe.execute()
        except Exception as e:
            logging.error(f"Redis set_many error: {e}")

# Global Redis cache
redis_cache = RedisCache()
```

## 🗄️ بهینه‌سازی پایگاه داده

### 1. Query Optimization

#### Connection Pooling
```python
# optimizations/db_pool.py
import asyncpg
import asyncio
from typing import Optional, Any, List, Dict
import logging
from contextlib import asynccontextmanager

class DatabasePool:
    """Pool اتصال پایگاه داده بهینه"""
    
    def __init__(self, database_url: str, min_size: int = 10, max_size: int = 20):
        self.database_url = database_url
        self.min_size = min_size
        self.max_size = max_size
        self.pool: Optional[asyncpg.Pool] = None
    
    async def create_pool(self):
        """ایجاد pool اتصال"""
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=self.min_size,
            max_size=self.max_size,
            command_timeout=60,
            server_settings={
                'jit': 'off',  # بهینه‌سازی برای query های کوتاه
                'application_name': 'telegram_bot'
            }
        )
    
    async def close_pool(self):
        """بستن pool"""
        if self.pool:
            await self.pool.close()
    
    @asynccontextmanager
    async def acquire_connection(self):
        """دریافت اتصال از pool"""
        async with self.pool.acquire() as connection:
            yield connection
    
    async def execute_query(self, query: str, *args) -> List[Dict]:
        """اجرای query با connection pooling"""
        async with self.acquire_connection() as conn:
            rows = await conn.fetch(query, *args)
            return [dict(row) for row in rows]
    
    async def execute_many(self, query: str, args_list: List[tuple]):
        """اجرای batch query"""
        async with self.acquire_connection() as conn:
            await conn.executemany(query, args_list)
    
    async def execute_transaction(self, queries: List[tuple]):
        """اجرای transaction"""
        async with self.acquire_connection() as conn:
            async with conn.transaction():
                for query, args in queries:
                    await conn.execute(query, *args)

# Global database pool
db_pool = DatabasePool("postgresql://user:pass@localhost/db")
```

#### Query Caching
```python
# optimizations/query_cache.py
from functools import wraps
import hashlib
import json

class QueryCache:
    """Cache برای query های پایگاه داده"""
    
    def __init__(self, cache_backend=None):
        self.cache_backend = cache_backend or memory_cache
    
    def _generate_cache_key(self, query: str, args: tuple) -> str:
        """تولید کلید cache برای query"""
        key_data = json.dumps({
            'query': query,
            'args': args
        }, sort_keys=True)
        return f"query:{hashlib.md5(key_data.encode()).hexdigest()}"
    
    def cached_query(self, ttl: int = 300):
        """Decorator برای cache کردن query ها"""
        def decorator(func):
            @wraps(func)
            async def wrapper(*args, **kwargs):
                # استخراج query و args
                if 'query' in kwargs:
                    query = kwargs['query']
                    query_args = kwargs.get('args', ())
                else:
                    query = args[0] if args else ""
                    query_args = args[1:] if len(args) > 1 else ()
                
                # تولید کلید cache
                cache_key = self._generate_cache_key(query, query_args)
                
                # بررسی cache
                cached_result = await self.cache_backend.get(cache_key)
                if cached_result is not None:
                    return cached_result
                
                # اجرای query
                result = await func(*args, **kwargs)
                
                # ذخیره در cache
                await self.cache_backend.set(cache_key, result, ttl)
                
                return result
            return wrapper
        return decorator

query_cache = QueryCache()
```

#### Optimized Database Operations
```python
# optimizations/db_operations.py
from typing import List, Dict, Any, Optional
import asyncio

class OptimizedDatabase:
    """عملیات بهینه پایگاه داده"""
    
    def __init__(self, pool: DatabasePool):
        self.pool = pool
    
    @query_cache.cached_query(ttl=600)
    async def get_user_stats(self, user_id: int) -> Dict[str, Any]:
        """دریافت آمار کاربر با cache"""
        query = """
        SELECT 
            u.user_id,
            u.first_name,
            u.last_name,
            u.username,
            COUNT(m.id) as message_count,
            MAX(m.created_at) as last_message_at
        FROM users u
        LEFT JOIN messages m ON u.user_id = m.user_id
        WHERE u.user_id = $1
        GROUP BY u.user_id, u.first_name, u.last_name, u.username
        """
        
        result = await self.pool.execute_query(query, user_id)
        return result[0] if result else {}
    
    async def bulk_insert_messages(self, messages: List[Dict[str, Any]]):
        """درج bulk پیام‌ها"""
        if not messages:
            return
        
        query = """
        INSERT INTO messages (user_id, message_id, text, message_type, created_at)
        VALUES ($1, $2, $3, $4, $5)
        ON CONFLICT (user_id, message_id) DO NOTHING
        """
        
        args_list = [
            (
                msg['user_id'],
                msg['message_id'],
                msg['text'],
                msg['message_type'],
                msg['created_at']
            )
            for msg in messages
        ]
        
        await self.pool.execute_many(query, args_list)
    
    async def get_active_users_batch(self, limit: int = 1000, offset: int = 0) -> List[Dict]:
        """دریافت کاربران فعال به صورت batch"""
        query = """
        SELECT user_id, first_name, last_name, username
        FROM users
        WHERE is_active = true
        ORDER BY last_activity_at DESC
        LIMIT $1 OFFSET $2
        """
        
        return await self.pool.execute_query(query, limit, offset)
    
    async def update_user_activity_batch(self, user_activities: List[tuple]):
        """بروزرسانی batch فعالیت کاربران"""
        query = """
        UPDATE users 
        SET last_activity_at = $2, message_count = message_count + 1
        WHERE user_id = $1
        """
        
        await self.pool.execute_many(query, user_activities)
    
    async def cleanup_old_data(self, days: int = 30):
        """پاکسازی داده‌های قدیمی"""
        queries = [
            (
                "DELETE FROM messages WHERE created_at < NOW() - INTERVAL '%s days'",
                (days,)
            ),
            (
                "DELETE FROM user_sessions WHERE created_at < NOW() - INTERVAL '%s days'",
                (days,)
            )
        ]
        
        await self.pool.execute_transaction(queries)
```

### 2. Database Indexing

#### Index Management
```sql
-- optimizations/indexes.sql

-- Index برای جستجوی کاربران
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_active 
ON users (is_active, last_activity_at DESC) 
WHERE is_active = true;

-- Index برای پیام‌های کاربر
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_user_created 
ON messages (user_id, created_at DESC);

-- Index برای جستجوی متنی
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_text_search 
ON messages USING gin(to_tsvector('english', text));

-- Index برای آمار
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_type_created 
ON messages (message_type, created_at);

-- Partial index برای پیام‌های اخیر
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_recent 
ON messages (created_at DESC) 
WHERE created_at > NOW() - INTERVAL '7 days';

-- Index برای user settings
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_user_settings_lookup 
ON user_settings (user_id, setting_key);

-- Composite index برای query های پیچیده
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_stats 
ON users (is_active, created_at, last_activity_at) 
WHERE is_active = true;
```

#### Index Monitoring
```python
# optimizations/index_monitor.py
import asyncio
from typing import List, Dict

class IndexMonitor:
    """مانیتورینگ index های پایگاه داده"""
    
    def __init__(self, db_pool: DatabasePool):
        self.db_pool = db_pool
    
    async def get_index_usage_stats(self) -> List[Dict]:
        """آمار استفاده از index ها"""
        query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            idx_tup_read,
            idx_tup_fetch,
            idx_scan,
            idx_tup_read::float / NULLIF(idx_scan, 0) as avg_tuples_per_scan
        FROM pg_stat_user_indexes
        ORDER BY idx_scan DESC;
        """
        
        return await self.db_pool.execute_query(query)
    
    async def get_unused_indexes(self) -> List[Dict]:
        """پیدا کردن index های استفاده نشده"""
        query = """
        SELECT 
            schemaname,
            tablename,
            indexname,
            pg_size_pretty(pg_relation_size(indexrelid)) as size
        FROM pg_stat_user_indexes
        WHERE idx_scan = 0
        AND schemaname = 'public';
        """
        
        return await self.db_pool.execute_query(query)
    
    async def get_table_sizes(self) -> List[Dict]:
        """اندازه جداول"""
        query = """
        SELECT 
            tablename,
            pg_size_pretty(pg_total_relation_size(tablename::regclass)) as total_size,
            pg_size_pretty(pg_relation_size(tablename::regclass)) as table_size,
            pg_size_pretty(pg_total_relation_size(tablename::regclass) - pg_relation_size(tablename::regclass)) as index_size
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(tablename::regclass) DESC;
        """
        
        return await self.db_pool.execute_query(query)
```

## 🧠 بهینه‌سازی حافظه

### 1. Memory Management

#### Object Pooling
```python
# optimizations/object_pool.py
import asyncio
from typing import TypeVar, Generic, Callable, Optional, Set
from collections import deque
import weakref

T = TypeVar('T')

class ObjectPool(Generic[T]):
    """Pool اشیاء برای کاهش memory allocation"""
    
    def __init__(self, factory: Callable[[], T], max_size: int = 100):
        self.factory = factory
        self.max_size = max_size
        self._pool: deque = deque()
        self._in_use: Set[T] = set()
        self._lock = asyncio.Lock()
    
    async def acquire(self) -> T:
        """دریافت شیء از pool"""
        async with self._lock:
            if self._pool:
                obj = self._pool.popleft()
            else:
                obj = self.factory()
            
            self._in_use.add(obj)
            return obj
    
    async def release(self, obj: T):
        """بازگرداندن شیء به pool"""
        async with self._lock:
            if obj in self._in_use:
                self._in_use.remove(obj)
                
                if len(self._pool) < self.max_size:
                    # Reset object state if needed
                    if hasattr(obj, 'reset'):
                        obj.reset()
                    self._pool.append(obj)
    
    def stats(self) -> dict:
        """آمار pool"""
        return {
            'pool_size': len(self._pool),
            'in_use': len(self._in_use),
            'max_size': self.max_size
        }

# مثال استفاده
class MessageProcessor:
    """پردازشگر پیام قابل استفاده مجدد"""
    
    def __init__(self):
        self.reset()
    
    def reset(self):
        """ریست کردن وضعیت"""
        self.processed_count = 0
        self.errors = []
    
    async def process(self, message):
        """پردازش پیام"""
        self.processed_count += 1
        # پردازش پیام
        return f"Processed: {message}"

# ایجاد pool
message_processor_pool = ObjectPool(MessageProcessor, max_size=50)
```

#### Memory Monitoring
```python
# optimizations/memory_monitor.py
import psutil
import gc
import sys
from typing import Dict, List
import tracemalloc
import logging

class MemoryMonitor:
    """مانیتورینگ مصرف حافظه"""
    
    def __init__(self):
        self.process = psutil.Process()
        self.baseline_memory = None
    
    def get_memory_info(self) -> Dict[str, float]:
        """اطلاعات حافظه"""
        memory_info = self.process.memory_info()
        
        return {
            'rss_mb': memory_info.rss / 1024 / 1024,
            'vms_mb': memory_info.vms / 1024 / 1024,
            'percent': self.process.memory_percent(),
            'available_mb': psutil.virtual_memory().available / 1024 / 1024
        }
    
    def set_baseline(self):
        """تنظیم baseline حافظه"""
        self.baseline_memory = self.get_memory_info()
    
    def get_memory_diff(self) -> Dict[str, float]:
        """تفاوت با baseline"""
        if not self.baseline_memory:
            return {}
        
        current = self.get_memory_info()
        return {
            key: current[key] - self.baseline_memory[key]
            for key in current.keys()
        }
    
    def force_garbage_collection(self) -> Dict[str, int]:
        """اجبار garbage collection"""
        before_objects = len(gc.get_objects())
        
        # اجرای garbage collection
        collected = gc.collect()
        
        after_objects = len(gc.get_objects())
        
        return {
            'collected': collected,
            'objects_before': before_objects,
            'objects_after': after_objects,
            'objects_freed': before_objects - after_objects
        }
    
    def get_top_memory_objects(self, limit: int = 10) -> List[Dict]:
        """اشیاء پرمصرف حافظه"""
        if not tracemalloc.is_tracing():
            tracemalloc.start()
        
        snapshot = tracemalloc.take_snapshot()
        top_stats = snapshot.statistics('lineno')
        
        result = []
        for stat in top_stats[:limit]:
            result.append({
                'filename': stat.traceback.format()[-1],
                'size_mb': stat.size / 1024 / 1024,
                'count': stat.count
            })
        
        return result
    
    async def monitor_continuously(self, interval: int = 60):
        """مانیتورینگ مداوم"""
        while True:
            memory_info = self.get_memory_info()
            
            # هشدار در صورت مصرف بالای حافظه
            if memory_info['percent'] > 80:
                logging.warning(f"High memory usage: {memory_info['percent']:.1f}%")
                
                # اجرای garbage collection
                gc_stats = self.force_garbage_collection()
                logging.info(f"Garbage collection: {gc_stats}")
            
            await asyncio.sleep(interval)

# Global memory monitor
memory_monitor = MemoryMonitor()
```

### 2. Data Structure Optimization

#### Efficient Data Structures
```python
# optimizations/data_structures.py
import array
from collections import defaultdict, deque
from typing import Any, Dict, List, Optional
import bisect

class CircularBuffer:
    """Buffer دایره‌ای برای ذخیره محدود داده"""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.buffer = deque(maxlen=max_size)
    
    def append(self, item: Any):
        """اضافه کردن آیتم"""
        self.buffer.append(item)
    
    def get_all(self) -> List[Any]:
        """دریافت تمام آیتم‌ها"""
        return list(self.buffer)
    
    def get_recent(self, count: int) -> List[Any]:
        """دریافت آیتم‌های اخیر"""
        return list(self.buffer)[-count:]
    
    def clear(self):
        """پاک کردن buffer"""
        self.buffer.clear()

class LRUCache:
    """LRU Cache بهینه"""
    
    def __init__(self, max_size: int):
        self.max_size = max_size
        self.cache: Dict[Any, Any] = {}
        self.access_order = deque()
    
    def get(self, key: Any) -> Optional[Any]:
        """دریافت از cache"""
        if key in self.cache:
            # بروزرسانی ترتیب دسترسی
            self.access_order.remove(key)
            self.access_order.append(key)
            return self.cache[key]
        return None
    
    def put(self, key: Any, value: Any):
        """قرار دادن در cache"""
        if key in self.cache:
            # بروزرسانی مقدار موجود
            self.cache[key] = value
            self.access_order.remove(key)
            self.access_order.append(key)
        else:
            # اضافه کردن مقدار جدید
            if len(self.cache) >= self.max_size:
                # حذف قدیمی‌ترین آیتم
                oldest_key = self.access_order.popleft()
                del self.cache[oldest_key]
            
            self.cache[key] = value
            self.access_order.append(key)

class CompactUserData:
    """ساختار فشرده برای داده‌های کاربر"""
    
    def __init__(self):
        # استفاده از array برای اعداد
        self.user_ids = array.array('q')  # long long
        self.message_counts = array.array('i')  # int
        
        # استفاده از dict برای string ها
        self.usernames: Dict[int, str] = {}
        self.first_names: Dict[int, str] = {}
    
    def add_user(self, user_id: int, username: str, first_name: str, message_count: int):
        """اضافه کردن کاربر"""
        index = len(self.user_ids)
        
        self.user_ids.append(user_id)
        self.message_counts.append(message_count)
        
        if username:
            self.usernames[index] = username
        if first_name:
            self.first_names[index] = first_name
    
    def get_user(self, index: int) -> Dict[str, Any]:
        """دریافت کاربر"""
        if index >= len(self.user_ids):
            return {}
        
        return {
            'user_id': self.user_ids[index],
            'message_count': self.message_counts[index],
            'username': self.usernames.get(index, ''),
            'first_name': self.first_names.get(index, '')
        }
    
    def memory_usage(self) -> Dict[str, int]:
        """محاسبه مصرف حافظه"""
        return {
            'user_ids_bytes': self.user_ids.buffer_info()[1] * self.user_ids.itemsize,
            'message_counts_bytes': self.message_counts.buffer_info()[1] * self.message_counts.itemsize,
            'usernames_estimate': sum(len(s.encode('utf-8')) for s in self.usernames.values()),
            'first_names_estimate': sum(len(s.encode('utf-8')) for s in self.first_names.values())
        }
```

## 🌐 بهینه‌سازی شبکه

### 1. HTTP Optimization

#### Request Batching
```python
# optimizations/http_batch.py
import asyncio
import aiohttp
from typing import List, Dict, Any, Optional
import time

class HTTPBatcher:
    """Batch کردن درخواست‌های HTTP"""
    
    def __init__(self, batch_size: int = 10, flush_interval: float = 1.0):
        self.batch_size = batch_size
        self.flush_interval = flush_interval
        self.pending_requests: List[Dict] = []
        self.last_flush = time.time()
        self._lock = asyncio.Lock()
        self._session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        connector = aiohttp.TCPConnector(
            limit=100,
            limit_per_host=30,
            ttl_dns_cache=300,
            use_dns_cache=True
        )
        
        self._session = aiohttp.ClientSession(
            connector=connector,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.flush()
        if self._session:
            await self._session.close()
    
    async def add_request(self, method: str, url: str, **kwargs) -> asyncio.Future:
        """اضافه کردن درخواست به batch"""
        future = asyncio.Future()
        
        async with self._lock:
            self.pending_requests.append({
                'method': method,
                'url': url,
                'kwargs': kwargs,
                'future': future
            })
            
            # بررسی نیاز به flush
            should_flush = (
                len(self.pending_requests) >= self.batch_size or
                time.time() - self.last_flush >= self.flush_interval
            )
            
            if should_flush:
                await self._flush_batch()
        
        return future
    
    async def _flush_batch(self):
        """اجرای batch درخواست‌ها"""
        if not self.pending_requests:
            return
        
        batch = self.pending_requests.copy()
        self.pending_requests.clear()
        self.last_flush = time.time()
        
        # اجرای موازی درخواست‌ها
        tasks = []
        for request in batch:
            task = asyncio.create_task(
                self._execute_request(request)
            )
            tasks.append(task)
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _execute_request(self, request: Dict):
        """اجرای یک درخواست"""
        try:
            async with self._session.request(
                request['method'],
                request['url'],
                **request['kwargs']
            ) as response:
                result = await response.json()
                request['future'].set_result(result)
        except Exception as e:
            request['future'].set_exception(e)
    
    async def flush(self):
        """اجبار flush کردن batch"""
        async with self._lock:
            await self._flush_batch()
```

### 2. Connection Optimization

#### Connection Pooling
```python
# optimizations/connection_pool.py
import asyncio
import aiohttp
from typing import Optional, Dict, Any
import ssl
import certifi

class OptimizedHTTPClient:
    """HTTP client بهینه شده"""
    
    def __init__(self, 
                 max_connections: int = 100,
                 max_connections_per_host: int = 30,
                 keepalive_timeout: int = 30,
                 timeout: int = 30):
        
        # تنظیمات SSL
        ssl_context = ssl.create_default_context(cafile=certifi.where())
        ssl_context.check_hostname = False
        ssl_context.verify_mode = ssl.CERT_REQUIRED
        
        # تنظیمات connector
        self.connector = aiohttp.TCPConnector(
            limit=max_connections,
            limit_per_host=max_connections_per_host,
            ttl_dns_cache=300,
            use_dns_cache=True,
            keepalive_timeout=keepalive_timeout,
            enable_cleanup_closed=True,
            ssl=ssl_context
        )
        
        # تنظیمات timeout
        self.timeout = aiohttp.ClientTimeout(
            total=timeout,
            connect=10,
            sock_read=timeout
        )
        
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=self.timeout,
            headers={
                'User-Agent': 'TelegramBot/1.0',
                'Accept': 'application/json',
                'Accept-Encoding': 'gzip, deflate'
            }
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def get(self, url: str, **kwargs) -> Dict[str, Any]:
        """GET request بهینه"""
        async with self.session.get(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    async def post(self, url: str, **kwargs) -> Dict[str, Any]:
        """POST request بهینه"""
        async with self.session.post(url, **kwargs) as response:
            response.raise_for_status()
            return await response.json()
    
    def get_connection_stats(self) -> Dict[str, Any]:
        """آمار اتصالات"""
        if self.connector:
            return {
                'total_connections': len(self.connector._conns),
                'available_connections': len(self.connector._available_connections),
                'acquired_connections': len(self.connector._acquired),
                'closed_connections': len(self.connector._closed)
            }
        return {}
```

## 📊 مانیتورینگ عملکرد

### 1. Real-time Monitoring

#### Performance Dashboard
```python
# monitoring/dashboard.py
import asyncio
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import aiohttp
from aiohttp import web

class PerformanceDashboard:
    """داشبورد عملکرد real-time"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.app = web.Application()
        self.setup_routes()
        self.metrics_history: List[Dict] = []
    
    def setup_routes(self):
        """تنظیم route ها"""
        self.app.router.add_get('/', self.dashboard_handler)
        self.app.router.add_get('/api/metrics', self.metrics_handler)
        self.app.router.add_get('/api/health', self.health_handler)
        self.app.router.add_static('/static', 'static')
    
    async def dashboard_handler(self, request):
        """صفحه اصلی داشبورد"""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Bot Performance Dashboard</title>
            <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                .metric-card { 
                    border: 1px solid #ddd; 
                    padding: 15px; 
                    margin: 10px; 
                    border-radius: 5px; 
                    display: inline-block;
                    min-width: 200px;
                }
                .chart-container { width: 80%; margin: 20px auto; }
            </style>
        </head>
        <body>
            <h1>🤖 Bot Performance Dashboard</h1>
            
            <div id="metrics-cards"></div>
            
            <div class="chart-container">
                <canvas id="responseTimeChart"></canvas>
            </div>
            
            <div class="chart-container">
                <canvas id="memoryChart"></canvas>
            </div>
            
            <script>
                // بروزرسانی metrics هر 5 ثانیه
                setInterval(updateMetrics, 5000);
                updateMetrics();
                
                async function updateMetrics() {
                    try {
                        const response = await fetch('/api/metrics');
                        const data = await response.json();
                        updateMetricsCards(data);
                        updateCharts(data);
                    } catch (error) {
                        console.error('Error fetching metrics:', error);
                    }
                }
                
                function updateMetricsCards(data) {
                    const container = document.getElementById('metrics-cards');
                    container.innerHTML = `
                        <div class="metric-card">
                            <h3>پیام‌های پردازش شده</h3>
                            <p>${data.messages_processed || 0}</p>
                        </div>
                        <div class="metric-card">
                            <h3>زمان پاسخ میانگین</h3>
                            <p>${(data.avg_response_time || 0).toFixed(2)} ms</p>
                        </div>
                        <div class="metric-card">
                            <h3>مصرف حافظه</h3>
                            <p>${(data.memory_usage || 0).toFixed(1)} MB</p>
                        </div>
                        <div class="metric-card">
                            <h3>کاربران فعال</h3>
                            <p>${data.active_users || 0}</p>
                        </div>
                    `;
                }
                
                function updateCharts(data) {
                    // پیاده‌سازی نمودارها
                }
            </script>
        </body>
        </html>
        """
        return web.Response(text=html, content_type='text/html')
    
    async def metrics_handler(self, request):
        """API metrics"""
        # جمع‌آوری metrics از منابع مختلف
        metrics = {
            'timestamp': datetime.now().isoformat(),
            'messages_processed': perf_monitor.counters.get('message_success', 0),
            'avg_response_time': self._get_avg_response_time(),
            'memory_usage': memory_monitor.get_memory_info()['rss_mb'],
            'active_users': await self._get_active_users_count(),
            'cache_hit_ratio': memory_cache.stats()['hit_ratio'],
            'database_connections': db_pool.pool._holders.__len__() if db_pool.pool else 0
        }
        
        # ذخیره در تاریخچه
        self.metrics_history.append(metrics)
        
        # نگه داشتن فقط 100 رکورد اخیر
        if len(self.metrics_history) > 100:
            self.metrics_history = self.metrics_history[-100:]
        
        return web.json_response(metrics)
    
    async def health_handler(self, request):
        """Health check endpoint"""
        health_status = {
            'status': 'healthy',
            'timestamp': datetime.now().isoformat(),
            'uptime': time.time() - start_time,
            'version': '1.0.0'
        }
        
        return web.json_response(health_status)
    
    def _get_avg_response_time(self) -> float:
        """محاسبه میانگین زمان پاسخ"""
        stats = perf_monitor.get_stats('message_processing')
        return stats.get('avg', 0) * 1000  # تبدیل به میلی‌ثانیه
    
    async def _get_active_users_count(self) -> int:
        """تعداد کاربران فعال"""
        # پیاده‌سازی بر اساس منطق برنامه
        return 0
    
    async def start_server(self):
        """شروع سرور داشبورد"""
        runner = web.AppRunner(self.app)
        await runner.setup()
        
        site = web.TCPSite(runner, 'localhost', self.port)
        await site.start()
        
        print(f"📊 Performance dashboard started on http://localhost:{self.port}")

# Global dashboard instance
dashboard = PerformanceDashboard()
```

## 🔗 مراحل بعدی

- [مانیتورینگ و نظارت](MONITORING.md)
- [امنیت پیشرفته](SECURITY.md)
- [مقیاس‌پذیری](SCALING.md)