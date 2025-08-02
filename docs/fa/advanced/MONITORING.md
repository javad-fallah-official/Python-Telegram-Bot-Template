# 📊 راهنمای مانیتورینگ و نظارت

> **مانیتورینگ کامل ربات تلگرام برای اطمینان از عملکرد بهینه**

## 🎯 درباره مانیتورینگ

این راهنما شامل تمام جنبه‌های مانیتورینگ ربات تلگرام از جمله logging، metrics، alerting، health checks و dashboard های real-time است.

## 📝 سیستم Logging

### 1. تنظیمات Logging پیشرفته

#### Structured Logging
```python
# monitoring/structured_logger.py
import logging
import json
import sys
from datetime import datetime
from typing import Dict, Any, Optional
import traceback
from pythonjsonlogger import jsonlogger

class StructuredLogger:
    """Logger ساختاریافته با قابلیت‌های پیشرفته"""
    
    def __init__(self, name: str, level: str = "INFO"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))
        
        # پاک کردن handler های قبلی
        self.logger.handlers.clear()
        
        # تنظیم formatter
        formatter = jsonlogger.JsonFormatter(
            fmt='%(asctime)s %(name)s %(levelname)s %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler('logs/bot.log', encoding='utf-8')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
        
        # Error file handler
        error_handler = logging.FileHandler('logs/errors.log', encoding='utf-8')
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        self.logger.addHandler(error_handler)
    
    def log_message_processing(self, user_id: int, message_type: str, 
                             processing_time: float, success: bool = True, 
                             error: Optional[str] = None):
        """Log پردازش پیام"""
        log_data = {
            'event': 'message_processing',
            'user_id': user_id,
            'message_type': message_type,
            'processing_time_ms': round(processing_time * 1000, 2),
            'success': success,
            'timestamp': datetime.now().isoformat()
        }
        
        if error:
            log_data['error'] = error
            self.logger.error("Message processing failed", extra=log_data)
        else:
            self.logger.info("Message processed successfully", extra=log_data)
    
    def log_user_activity(self, user_id: int, username: str, action: str, 
                         metadata: Optional[Dict] = None):
        """Log فعالیت کاربر"""
        log_data = {
            'event': 'user_activity',
            'user_id': user_id,
            'username': username,
            'action': action,
            'timestamp': datetime.now().isoformat()
        }
        
        if metadata:
            log_data['metadata'] = metadata
        
        self.logger.info("User activity", extra=log_data)
    
    def log_system_event(self, event_type: str, details: Dict[str, Any], 
                        level: str = "INFO"):
        """Log رویداد سیستم"""
        log_data = {
            'event': 'system_event',
            'event_type': event_type,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        
        log_level = getattr(logging, level.upper())
        self.logger.log(log_level, f"System event: {event_type}", extra=log_data)
    
    def log_performance_metrics(self, metrics: Dict[str, Any]):
        """Log metrics عملکرد"""
        log_data = {
            'event': 'performance_metrics',
            'metrics': metrics,
            'timestamp': datetime.now().isoformat()
        }
        
        self.logger.info("Performance metrics", extra=log_data)
    
    def log_exception(self, exception: Exception, context: Optional[Dict] = None):
        """Log exception با جزئیات کامل"""
        log_data = {
            'event': 'exception',
            'exception_type': type(exception).__name__,
            'exception_message': str(exception),
            'traceback': traceback.format_exc(),
            'timestamp': datetime.now().isoformat()
        }
        
        if context:
            log_data['context'] = context
        
        self.logger.error("Exception occurred", extra=log_data)

# Global logger instance
structured_logger = StructuredLogger("telegram_bot")
```

#### Log Rotation و Management
```python
# monitoring/log_manager.py
import logging
from logging.handlers import RotatingFileHandler, TimedRotatingFileHandler
import os
import gzip
import shutil
from datetime import datetime, timedelta
import asyncio
from typing import List
import glob

class LogManager:
    """مدیریت log ها و rotation"""
    
    def __init__(self, log_dir: str = "logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)
    
    def setup_rotating_logger(self, name: str, filename: str, 
                            max_bytes: int = 10*1024*1024,  # 10MB
                            backup_count: int = 5) -> logging.Logger:
        """تنظیم logger با rotation بر اساس اندازه"""
        logger = logging.getLogger(name)
        
        handler = RotatingFileHandler(
            filename=os.path.join(self.log_dir, filename),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        return logger
    
    def setup_timed_logger(self, name: str, filename: str,
                          when: str = 'midnight',
                          interval: int = 1,
                          backup_count: int = 30) -> logging.Logger:
        """تنظیم logger با rotation بر اساس زمان"""
        logger = logging.getLogger(name)
        
        handler = TimedRotatingFileHandler(
            filename=os.path.join(self.log_dir, filename),
            when=when,
            interval=interval,
            backupCount=backup_count,
            encoding='utf-8'
        )
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        
        return logger
    
    async def compress_old_logs(self, days_old: int = 7):
        """فشرده‌سازی log های قدیمی"""
        cutoff_date = datetime.now() - timedelta(days=days_old)
        
        log_files = glob.glob(os.path.join(self.log_dir, "*.log.*"))
        
        for log_file in log_files:
            file_stat = os.stat(log_file)
            file_date = datetime.fromtimestamp(file_stat.st_mtime)
            
            if file_date < cutoff_date and not log_file.endswith('.gz'):
                # فشرده‌سازی فایل
                with open(log_file, 'rb') as f_in:
                    with gzip.open(f"{log_file}.gz", 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                
                # حذف فایل اصلی
                os.remove(log_file)
                
                structured_logger.log_system_event(
                    'log_compressed',
                    {'file': log_file, 'compressed_to': f"{log_file}.gz"}
                )
    
    async def cleanup_old_logs(self, days_to_keep: int = 30):
        """پاکسازی log های خیلی قدیمی"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        log_files = glob.glob(os.path.join(self.log_dir, "*.log.*"))
        log_files.extend(glob.glob(os.path.join(self.log_dir, "*.gz")))
        
        deleted_files = []
        for log_file in log_files:
            file_stat = os.stat(log_file)
            file_date = datetime.fromtimestamp(file_stat.st_mtime)
            
            if file_date < cutoff_date:
                os.remove(log_file)
                deleted_files.append(log_file)
        
        if deleted_files:
            structured_logger.log_system_event(
                'logs_cleaned',
                {'deleted_files': deleted_files, 'count': len(deleted_files)}
            )
    
    async def get_log_statistics(self) -> Dict[str, Any]:
        """آمار log ها"""
        log_files = glob.glob(os.path.join(self.log_dir, "*"))
        
        total_size = 0
        file_count = 0
        compressed_count = 0
        
        for log_file in log_files:
            if os.path.isfile(log_file):
                total_size += os.path.getsize(log_file)
                file_count += 1
                
                if log_file.endswith('.gz'):
                    compressed_count += 1
        
        return {
            'total_files': file_count,
            'compressed_files': compressed_count,
            'total_size_mb': round(total_size / 1024 / 1024, 2),
            'log_directory': self.log_dir
        }

# Global log manager
log_manager = LogManager()
```

### 2. Application Logging

#### Bot Event Logging
```python
# monitoring/bot_logger.py
import asyncio
from typing import Dict, Any, Optional
from aiogram import types
import time

class BotEventLogger:
    """Logger رویدادهای ربات"""
    
    def __init__(self, logger: StructuredLogger):
        self.logger = logger
        self.session_start_time = time.time()
        self.message_count = 0
        self.error_count = 0
        self.user_sessions: Dict[int, float] = {}
    
    async def log_bot_startup(self, bot_info: Dict[str, Any]):
        """Log راه‌اندازی ربات"""
        self.logger.log_system_event(
            'bot_startup',
            {
                'bot_username': bot_info.get('username'),
                'bot_id': bot_info.get('id'),
                'startup_time': time.time()
            }
        )
    
    async def log_bot_shutdown(self):
        """Log خاموش شدن ربات"""
        uptime = time.time() - self.session_start_time
        
        self.logger.log_system_event(
            'bot_shutdown',
            {
                'uptime_seconds': round(uptime, 2),
                'total_messages': self.message_count,
                'total_errors': self.error_count,
                'shutdown_time': time.time()
            }
        )
    
    async def log_message_received(self, message: types.Message, 
                                 processing_start: float):
        """Log دریافت پیام"""
        self.message_count += 1
        
        # ثبت session کاربر
        user_id = message.from_user.id
        if user_id not in self.user_sessions:
            self.user_sessions[user_id] = time.time()
        
        self.logger.log_message_processing(
            user_id=user_id,
            message_type=message.content_type,
            processing_time=time.time() - processing_start,
            success=True
        )
        
        # Log جزئیات پیام
        self.logger.log_user_activity(
            user_id=user_id,
            username=message.from_user.username or "unknown",
            action="message_sent",
            metadata={
                'message_type': message.content_type,
                'chat_type': message.chat.type,
                'message_length': len(message.text or ""),
                'has_entities': bool(message.entities)
            }
        )
    
    async def log_command_executed(self, message: types.Message, 
                                 command: str, success: bool = True,
                                 error: Optional[str] = None):
        """Log اجرای دستور"""
        self.logger.log_user_activity(
            user_id=message.from_user.id,
            username=message.from_user.username or "unknown",
            action="command_executed",
            metadata={
                'command': command,
                'success': success,
                'error': error,
                'chat_type': message.chat.type
            }
        )
    
    async def log_callback_query(self, callback_query: types.CallbackQuery,
                               success: bool = True,
                               error: Optional[str] = None):
        """Log callback query"""
        self.logger.log_user_activity(
            user_id=callback_query.from_user.id,
            username=callback_query.from_user.username or "unknown",
            action="callback_query",
            metadata={
                'callback_data': callback_query.data,
                'success': success,
                'error': error
            }
        )
    
    async def log_error(self, error: Exception, context: Dict[str, Any]):
        """Log خطا"""
        self.error_count += 1
        self.logger.log_exception(error, context)
    
    async def log_user_statistics(self):
        """Log آمار کاربران"""
        active_sessions = len(self.user_sessions)
        
        self.logger.log_performance_metrics({
            'active_user_sessions': active_sessions,
            'total_messages_processed': self.message_count,
            'total_errors': self.error_count,
            'uptime_seconds': time.time() - self.session_start_time
        })

# Global bot event logger
bot_event_logger = BotEventLogger(structured_logger)
```

## 📈 سیستم Metrics

### 1. Custom Metrics

#### Metrics Collector
```python
# monitoring/metrics_collector.py
import time
import asyncio
from typing import Dict, List, Any, Optional
from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import datetime, timedelta
import statistics

@dataclass
class MetricPoint:
    """نقطه metric"""
    timestamp: float
    value: float
    tags: Dict[str, str]

class MetricsCollector:
    """جمع‌آوری و ذخیره metrics"""
    
    def __init__(self, retention_hours: int = 24):
        self.retention_hours = retention_hours
        self.metrics: Dict[str, deque] = defaultdict(lambda: deque())
        self.counters: Dict[str, int] = defaultdict(int)
        self.gauges: Dict[str, float] = defaultdict(float)
        self.histograms: Dict[str, List[float]] = defaultdict(list)
        self._lock = asyncio.Lock()
    
    async def record_counter(self, name: str, value: int = 1, 
                           tags: Optional[Dict[str, str]] = None):
        """ثبت counter metric"""
        async with self._lock:
            key = self._make_key(name, tags)
            self.counters[key] += value
            
            # ثبت در time series
            point = MetricPoint(
                timestamp=time.time(),
                value=self.counters[key],
                tags=tags or {}
            )
            self.metrics[name].append(point)
    
    async def record_gauge(self, name: str, value: float,
                         tags: Optional[Dict[str, str]] = None):
        """ثبت gauge metric"""
        async with self._lock:
            key = self._make_key(name, tags)
            self.gauges[key] = value
            
            # ثبت در time series
            point = MetricPoint(
                timestamp=time.time(),
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(point)
    
    async def record_histogram(self, name: str, value: float,
                             tags: Optional[Dict[str, str]] = None):
        """ثبت histogram metric"""
        async with self._lock:
            key = self._make_key(name, tags)
            self.histograms[key].append(value)
            
            # محدود کردن اندازه histogram
            if len(self.histograms[key]) > 1000:
                self.histograms[key] = self.histograms[key][-1000:]
            
            # ثبت در time series
            point = MetricPoint(
                timestamp=time.time(),
                value=value,
                tags=tags or {}
            )
            self.metrics[name].append(point)
    
    async def get_counter_value(self, name: str, 
                              tags: Optional[Dict[str, str]] = None) -> int:
        """دریافت مقدار counter"""
        key = self._make_key(name, tags)
        return self.counters.get(key, 0)
    
    async def get_gauge_value(self, name: str,
                            tags: Optional[Dict[str, str]] = None) -> float:
        """دریافت مقدار gauge"""
        key = self._make_key(name, tags)
        return self.gauges.get(key, 0.0)
    
    async def get_histogram_stats(self, name: str,
                                tags: Optional[Dict[str, str]] = None) -> Dict[str, float]:
        """آمار histogram"""
        key = self._make_key(name, tags)
        values = self.histograms.get(key, [])
        
        if not values:
            return {}
        
        return {
            'count': len(values),
            'min': min(values),
            'max': max(values),
            'mean': statistics.mean(values),
            'median': statistics.median(values),
            'p95': statistics.quantiles(values, n=20)[18] if len(values) >= 20 else max(values),
            'p99': statistics.quantiles(values, n=100)[98] if len(values) >= 100 else max(values)
        }
    
    async def get_time_series(self, name: str, 
                            hours: int = 1) -> List[MetricPoint]:
        """دریافت time series"""
        cutoff_time = time.time() - (hours * 3600)
        
        points = [
            point for point in self.metrics.get(name, [])
            if point.timestamp >= cutoff_time
        ]
        
        return sorted(points, key=lambda p: p.timestamp)
    
    async def cleanup_old_metrics(self):
        """پاکسازی metrics قدیمی"""
        cutoff_time = time.time() - (self.retention_hours * 3600)
        
        async with self._lock:
            for name, points in self.metrics.items():
                # حذف نقاط قدیمی
                while points and points[0].timestamp < cutoff_time:
                    points.popleft()
    
    def _make_key(self, name: str, tags: Optional[Dict[str, str]]) -> str:
        """ایجاد کلید برای metric"""
        if not tags:
            return name
        
        tag_str = ",".join(f"{k}={v}" for k, v in sorted(tags.items()))
        return f"{name}[{tag_str}]"
    
    async def export_prometheus_format(self) -> str:
        """Export در فرمت Prometheus"""
        lines = []
        
        # Counters
        for key, value in self.counters.items():
            lines.append(f"# TYPE {key} counter")
            lines.append(f"{key} {value}")
        
        # Gauges
        for key, value in self.gauges.items():
            lines.append(f"# TYPE {key} gauge")
            lines.append(f"{key} {value}")
        
        # Histograms
        for key, values in self.histograms.items():
            if values:
                stats = await self.get_histogram_stats(key.split('[')[0])
                lines.append(f"# TYPE {key} histogram")
                lines.append(f"{key}_count {stats.get('count', 0)}")
                lines.append(f"{key}_sum {sum(values)}")
                lines.append(f"{key}_avg {stats.get('mean', 0)}")
        
        return "\n".join(lines)

# Global metrics collector
metrics_collector = MetricsCollector()
```

#### Bot-specific Metrics
```python
# monitoring/bot_metrics.py
import asyncio
import time
from typing import Dict, Any
from functools import wraps

class BotMetrics:
    """Metrics مخصوص ربات"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
        self.start_time = time.time()
    
    async def record_message_processed(self, message_type: str, 
                                     processing_time: float,
                                     success: bool = True):
        """ثبت پردازش پیام"""
        # Counter پیام‌های پردازش شده
        await self.collector.record_counter(
            'messages_processed_total',
            tags={'type': message_type, 'status': 'success' if success else 'error'}
        )
        
        # Histogram زمان پردازش
        await self.collector.record_histogram(
            'message_processing_duration_seconds',
            processing_time,
            tags={'type': message_type}
        )
    
    async def record_command_executed(self, command: str, success: bool = True):
        """ثبت اجرای دستور"""
        await self.collector.record_counter(
            'commands_executed_total',
            tags={'command': command, 'status': 'success' if success else 'error'}
        )
    
    async def record_user_activity(self, user_id: int, action: str):
        """ثبت فعالیت کاربر"""
        await self.collector.record_counter(
            'user_activities_total',
            tags={'action': action}
        )
        
        # Gauge کاربران فعال
        await self.collector.record_gauge(
            'active_users',
            len(set([user_id]))  # در عمل باید از cache استفاده کرد
        )
    
    async def record_error(self, error_type: str, component: str):
        """ثبت خطا"""
        await self.collector.record_counter(
            'errors_total',
            tags={'type': error_type, 'component': component}
        )
    
    async def record_database_operation(self, operation: str, 
                                      duration: float, success: bool = True):
        """ثبت عملیات پایگاه داده"""
        await self.collector.record_counter(
            'database_operations_total',
            tags={'operation': operation, 'status': 'success' if success else 'error'}
        )
        
        await self.collector.record_histogram(
            'database_operation_duration_seconds',
            duration,
            tags={'operation': operation}
        )
    
    async def record_api_call(self, endpoint: str, status_code: int, 
                            duration: float):
        """ثبت فراخوانی API"""
        await self.collector.record_counter(
            'api_calls_total',
            tags={'endpoint': endpoint, 'status_code': str(status_code)}
        )
        
        await self.collector.record_histogram(
            'api_call_duration_seconds',
            duration,
            tags={'endpoint': endpoint}
        )
    
    async def update_system_metrics(self):
        """بروزرسانی metrics سیستم"""
        # Uptime
        uptime = time.time() - self.start_time
        await self.collector.record_gauge('bot_uptime_seconds', uptime)
        
        # Memory usage
        memory_info = memory_monitor.get_memory_info()
        await self.collector.record_gauge(
            'memory_usage_bytes',
            memory_info['rss_mb'] * 1024 * 1024
        )
        
        # Database connections
        if hasattr(db_pool, 'pool') and db_pool.pool:
            await self.collector.record_gauge(
                'database_connections_active',
                len(db_pool.pool._holders)
            )

# Global bot metrics
bot_metrics = BotMetrics(metrics_collector)

def track_execution_time(metric_name: str, tags: Dict[str, str] = None):
    """Decorator برای ردیابی زمان اجرا"""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            start_time = time.time()
            success = True
            
            try:
                result = await func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                duration = time.time() - start_time
                await metrics_collector.record_histogram(
                    metric_name,
                    duration,
                    tags=tags
                )
                
                await metrics_collector.record_counter(
                    f"{metric_name}_total",
                    tags={**(tags or {}), 'status': 'success' if success else 'error'}
                )
        
        return wrapper
    return decorator
```

## 🚨 سیستم Alerting

### 1. Alert Manager

#### Alert Rules
```python
# monitoring/alert_manager.py
import asyncio
import time
from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
from enum import Enum
import aiohttp

class AlertSeverity(Enum):
    """سطح شدت هشدار"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class AlertRule:
    """قانون هشدار"""
    name: str
    condition: Callable[[Dict[str, Any]], bool]
    severity: AlertSeverity
    message: str
    cooldown_seconds: int = 300  # 5 دقیقه
    enabled: bool = True

@dataclass
class Alert:
    """هشدار"""
    rule_name: str
    severity: AlertSeverity
    message: str
    timestamp: float
    resolved: bool = False
    resolved_at: Optional[float] = None

class AlertManager:
    """مدیریت هشدارها"""
    
    def __init__(self):
        self.rules: List[AlertRule] = []
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []
        self.last_check_time: Dict[str, float] = {}
        self.notification_handlers: List[Callable] = []
    
    def add_rule(self, rule: AlertRule):
        """اضافه کردن قانون هشدار"""
        self.rules.append(rule)
    
    def add_notification_handler(self, handler: Callable[[Alert], None]):
        """اضافه کردن handler اطلاع‌رسانی"""
        self.notification_handlers.append(handler)
    
    async def check_alerts(self, metrics: Dict[str, Any]):
        """بررسی قوانین هشدار"""
        current_time = time.time()
        
        for rule in self.rules:
            if not rule.enabled:
                continue
            
            # بررسی cooldown
            last_check = self.last_check_time.get(rule.name, 0)
            if current_time - last_check < rule.cooldown_seconds:
                continue
            
            # بررسی شرط
            try:
                if rule.condition(metrics):
                    await self._trigger_alert(rule, current_time)
                else:
                    await self._resolve_alert(rule.name, current_time)
            except Exception as e:
                structured_logger.log_exception(
                    e, 
                    {'context': 'alert_check', 'rule': rule.name}
                )
            
            self.last_check_time[rule.name] = current_time
    
    async def _trigger_alert(self, rule: AlertRule, timestamp: float):
        """فعال کردن هشدار"""
        if rule.name in self.active_alerts:
            return  # هشدار قبلاً فعال است
        
        alert = Alert(
            rule_name=rule.name,
            severity=rule.severity,
            message=rule.message,
            timestamp=timestamp
        )
        
        self.active_alerts[rule.name] = alert
        self.alert_history.append(alert)
        
        # ارسال اطلاع‌رسانی
        for handler in self.notification_handlers:
            try:
                await handler(alert)
            except Exception as e:
                structured_logger.log_exception(
                    e,
                    {'context': 'alert_notification', 'rule': rule.name}
                )
        
        structured_logger.log_system_event(
            'alert_triggered',
            {
                'rule': rule.name,
                'severity': rule.severity.value,
                'message': rule.message
            },
            level="ERROR" if rule.severity in [AlertSeverity.ERROR, AlertSeverity.CRITICAL] else "WARNING"
        )
    
    async def _resolve_alert(self, rule_name: str, timestamp: float):
        """حل کردن هشدار"""
        if rule_name not in self.active_alerts:
            return
        
        alert = self.active_alerts[rule_name]
        alert.resolved = True
        alert.resolved_at = timestamp
        
        del self.active_alerts[rule_name]
        
        structured_logger.log_system_event(
            'alert_resolved',
            {
                'rule': rule_name,
                'duration_seconds': timestamp - alert.timestamp
            }
        )
    
    def get_active_alerts(self) -> List[Alert]:
        """دریافت هشدارهای فعال"""
        return list(self.active_alerts.values())
    
    def get_alert_history(self, hours: int = 24) -> List[Alert]:
        """دریافت تاریخچه هشدارها"""
        cutoff_time = time.time() - (hours * 3600)
        return [
            alert for alert in self.alert_history
            if alert.timestamp >= cutoff_time
        ]

# Global alert manager
alert_manager = AlertManager()

# تعریف قوانین هشدار پیش‌فرض
def setup_default_alert_rules():
    """تنظیم قوانین هشدار پیش‌فرض"""
    
    # هشدار مصرف بالای حافظه
    alert_manager.add_rule(AlertRule(
        name="high_memory_usage",
        condition=lambda m: m.get('memory_usage_mb', 0) > 500,
        severity=AlertSeverity.WARNING,
        message="مصرف حافظه بالا: {memory_usage_mb} MB",
        cooldown_seconds=300
    ))
    
    # هشدار خطاهای زیاد
    alert_manager.add_rule(AlertRule(
        name="high_error_rate",
        condition=lambda m: m.get('error_rate_per_minute', 0) > 10,
        severity=AlertSeverity.ERROR,
        message="نرخ خطای بالا: {error_rate_per_minute} خطا در دقیقه",
        cooldown_seconds=180
    ))
    
    # هشدار قطع اتصال پایگاه داده
    alert_manager.add_rule(AlertRule(
        name="database_connection_failed",
        condition=lambda m: m.get('database_connected', True) == False,
        severity=AlertSeverity.CRITICAL,
        message="اتصال به پایگاه داده قطع شده است",
        cooldown_seconds=60
    ))
    
    # هشدار زمان پاسخ بالا
    alert_manager.add_rule(AlertRule(
        name="high_response_time",
        condition=lambda m: m.get('avg_response_time_ms', 0) > 5000,
        severity=AlertSeverity.WARNING,
        message="زمان پاسخ بالا: {avg_response_time_ms} میلی‌ثانیه",
        cooldown_seconds=300
    ))
```

### 2. Notification Handlers

#### Telegram Notifications
```python
# monitoring/notifications.py
import asyncio
import aiohttp
from typing import List, Optional
import json

class TelegramNotifier:
    """ارسال اطلاع‌رسانی از طریق تلگرام"""
    
    def __init__(self, bot_token: str, admin_chat_ids: List[int]):
        self.bot_token = bot_token
        self.admin_chat_ids = admin_chat_ids
        self.base_url = f"https://api.telegram.org/bot{bot_token}"
    
    async def send_alert(self, alert: Alert):
        """ارسال هشدار"""
        # تعیین emoji بر اساس شدت
        emoji_map = {
            AlertSeverity.INFO: "ℹ️",
            AlertSeverity.WARNING: "⚠️",
            AlertSeverity.ERROR: "❌",
            AlertSeverity.CRITICAL: "🚨"
        }
        
        emoji = emoji_map.get(alert.severity, "📢")
        
        message = f"""
{emoji} **هشدار سیستم**

**نوع:** {alert.rule_name}
**شدت:** {alert.severity.value.upper()}
**پیام:** {alert.message}
**زمان:** {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}

#alert #{alert.severity.value}
        """.strip()
        
        for chat_id in self.admin_chat_ids:
            await self._send_message(chat_id, message)
    
    async def _send_message(self, chat_id: int, text: str):
        """ارسال پیام"""
        url = f"{self.base_url}/sendMessage"
        
        payload = {
            'chat_id': chat_id,
            'text': text,
            'parse_mode': 'Markdown'
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    if response.status != 200:
                        structured_logger.log_system_event(
                            'notification_failed',
                            {
                                'chat_id': chat_id,
                                'status_code': response.status,
                                'response': await response.text()
                            }
                        )
        except Exception as e:
            structured_logger.log_exception(
                e,
                {'context': 'telegram_notification', 'chat_id': chat_id}
            )

class EmailNotifier:
    """ارسال اطلاع‌رسانی از طریق ایمیل"""
    
    def __init__(self, smtp_server: str, smtp_port: int,
                 username: str, password: str, 
                 admin_emails: List[str]):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.admin_emails = admin_emails
    
    async def send_alert(self, alert: Alert):
        """ارسال هشدار ایمیل"""
        import smtplib
        from email.mime.text import MIMEText
        from email.mime.multipart import MIMEMultipart
        
        subject = f"[Bot Alert] {alert.severity.value.upper()}: {alert.rule_name}"
        
        body = f"""
        هشدار سیستم ربات تلگرام
        
        نوع هشدار: {alert.rule_name}
        شدت: {alert.severity.value.upper()}
        پیام: {alert.message}
        زمان: {datetime.fromtimestamp(alert.timestamp).strftime('%Y-%m-%d %H:%M:%S')}
        
        لطفاً بررسی کنید.
        """
        
        try:
            msg = MIMEMultipart()
            msg['From'] = self.username
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()
            server.login(self.username, self.password)
            
            for email in self.admin_emails:
                msg['To'] = email
                server.send_message(msg)
                del msg['To']
            
            server.quit()
            
        except Exception as e:
            structured_logger.log_exception(
                e,
                {'context': 'email_notification'}
            )

class WebhookNotifier:
    """ارسال اطلاع‌رسانی از طریق webhook"""
    
    def __init__(self, webhook_urls: List[str]):
        self.webhook_urls = webhook_urls
    
    async def send_alert(self, alert: Alert):
        """ارسال هشدار webhook"""
        payload = {
            'alert': {
                'rule_name': alert.rule_name,
                'severity': alert.severity.value,
                'message': alert.message,
                'timestamp': alert.timestamp,
                'resolved': alert.resolved
            }
        }
        
        for url in self.webhook_urls:
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.post(url, json=payload) as response:
                        if response.status not in [200, 201, 202]:
                            structured_logger.log_system_event(
                                'webhook_notification_failed',
                                {
                                    'url': url,
                                    'status_code': response.status
                                }
                            )
            except Exception as e:
                structured_logger.log_exception(
                    e,
                    {'context': 'webhook_notification', 'url': url}
                )
```

## 🏥 Health Checks

### 1. Health Check System

#### Health Checker
```python
# monitoring/health_checker.py
import asyncio
import time
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass
from enum import Enum

class HealthStatus(Enum):
    """وضعیت سلامت"""
    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"

@dataclass
class HealthCheck:
    """بررسی سلامت"""
    name: str
    check_function: Callable[[], bool]
    timeout_seconds: int = 10
    critical: bool = False
    enabled: bool = True

@dataclass
class HealthResult:
    """نتیجه بررسی سلامت"""
    name: str
    status: HealthStatus
    message: str
    duration_ms: float
    timestamp: float

class HealthChecker:
    """بررسی‌کننده سلامت سیستم"""
    
    def __init__(self):
        self.checks: List[HealthCheck] = []
        self.last_results: Dict[str, HealthResult] = {}
    
    def add_check(self, check: HealthCheck):
        """اضافه کردن بررسی سلامت"""
        self.checks.append(check)
    
    async def run_all_checks(self) -> Dict[str, HealthResult]:
        """اجرای تمام بررسی‌ها"""
        results = {}
        
        for check in self.checks:
            if not check.enabled:
                continue
            
            result = await self._run_single_check(check)
            results[check.name] = result
            self.last_results[check.name] = result
        
        return results
    
    async def _run_single_check(self, check: HealthCheck) -> HealthResult:
        """اجرای یک بررسی"""
        start_time = time.time()
        
        try:
            # اجرای بررسی با timeout
            is_healthy = await asyncio.wait_for(
                check.check_function(),
                timeout=check.timeout_seconds
            )
            
            duration_ms = (time.time() - start_time) * 1000
            
            if is_healthy:
                return HealthResult(
                    name=check.name,
                    status=HealthStatus.HEALTHY,
                    message="OK",
                    duration_ms=duration_ms,
                    timestamp=time.time()
                )
            else:
                return HealthResult(
                    name=check.name,
                    status=HealthStatus.UNHEALTHY,
                    message="Check failed",
                    duration_ms=duration_ms,
                    timestamp=time.time()
                )
        
        except asyncio.TimeoutError:
            duration_ms = (time.time() - start_time) * 1000
            return HealthResult(
                name=check.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Timeout after {check.timeout_seconds}s",
                duration_ms=duration_ms,
                timestamp=time.time()
            )
        
        except Exception as e:
            duration_ms = (time.time() - start_time) * 1000
            return HealthResult(
                name=check.name,
                status=HealthStatus.UNHEALTHY,
                message=f"Error: {str(e)}",
                duration_ms=duration_ms,
                timestamp=time.time()
            )
    
    async def get_overall_status(self) -> HealthStatus:
        """وضعیت کلی سیستم"""
        if not self.last_results:
            return HealthStatus.UNHEALTHY
        
        critical_unhealthy = any(
            result.status == HealthStatus.UNHEALTHY
            for check in self.checks
            for result in [self.last_results.get(check.name)]
            if result and check.critical
        )
        
        if critical_unhealthy:
            return HealthStatus.UNHEALTHY
        
        any_unhealthy = any(
            result.status == HealthStatus.UNHEALTHY
            for result in self.last_results.values()
        )
        
        if any_unhealthy:
            return HealthStatus.DEGRADED
        
        return HealthStatus.HEALTHY
    
    async def get_health_summary(self) -> Dict[str, Any]:
        """خلاصه وضعیت سلامت"""
        overall_status = await self.get_overall_status()
        
        return {
            'status': overall_status.value,
            'timestamp': time.time(),
            'checks': {
                name: {
                    'status': result.status.value,
                    'message': result.message,
                    'duration_ms': result.duration_ms,
                    'timestamp': result.timestamp
                }
                for name, result in self.last_results.items()
            }
        }

# Global health checker
health_checker = HealthChecker()

# تعریف بررسی‌های سلامت
async def check_database_connection() -> bool:
    """بررسی اتصال پایگاه داده"""
    try:
        if not db_pool.pool:
            return False
        
        async with db_pool.acquire_connection() as conn:
            await conn.fetchval("SELECT 1")
        return True
    except:
        return False

async def check_memory_usage() -> bool:
    """بررسی مصرف حافظه"""
    memory_info = memory_monitor.get_memory_info()
    return memory_info['percent'] < 90

async def check_telegram_api() -> bool:
    """بررسی دسترسی به API تلگرام"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.telegram.org/bot{bot_token}/getMe",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
    except:
        return False

def setup_health_checks():
    """تنظیم بررسی‌های سلامت"""
    health_checker.add_check(HealthCheck(
        name="database",
        check_function=check_database_connection,
        timeout_seconds=5,
        critical=True
    ))
    
    health_checker.add_check(HealthCheck(
        name="memory",
        check_function=check_memory_usage,
        timeout_seconds=2,
        critical=False
    ))
    
    health_checker.add_check(HealthCheck(
        name="telegram_api",
        check_function=check_telegram_api,
        timeout_seconds=10,
        critical=True
    ))
```

## 🔗 مراحل بعدی

- [امنیت پیشرفته](SECURITY.md)
- [مقیاس‌پذیری](SCALING.md)
- [بهینه‌سازی عملکرد](OPTIMIZATION.md)