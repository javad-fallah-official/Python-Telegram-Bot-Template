# 🚀 راهنمای استقرار

> **استقرار ربات تلگرام در محیط‌های مختلف production**

## 🎯 درباره استقرار

این راهنما شامل تمام روش‌های استقرار ربات تلگرام در محیط‌های مختلف از جمله VPS، Docker، Cloud Services و CDN است.

## 🏗️ آماده‌سازی برای استقرار

### 1. بررسی پیش‌نیازها

#### چک‌لیست آماده‌سازی
```bash
# بررسی تست‌ها
pytest tests/ -v

# بررسی کیفیت کد
flake8 .
black --check .

# بررسی امنیت
bandit -r .

# بررسی وابستگی‌ها
pip-audit

# بررسی تنظیمات
python -c "from core.config import Config; Config().validate()"
```

#### فایل‌های ضروری
```
project/
├── requirements.txt        # وابستگی‌های Python
├── Dockerfile             # تنظیمات Docker
├── docker-compose.yml     # ترکیب سرویس‌ها
├── .env.example          # نمونه متغیرهای محیطی
├── nginx.conf            # تنظیمات Nginx
├── systemd/              # سرویس systemd
│   └── bot.service
└── scripts/              # اسکریپت‌های استقرار
    ├── deploy.sh
    ├── backup.sh
    └── health_check.sh
```

### 2. تنظیمات امنیتی

#### متغیرهای محیطی
```bash
# .env.production
BOT_TOKEN=your_production_token
DATABASE_URL=postgresql://user:pass@localhost/botdb
SECRET_KEY=your_secret_key_here
DEBUG=False
LOG_LEVEL=INFO

# تنظیمات Webhook
WEBHOOK_URL=https://yourdomain.com/webhook
WEBHOOK_SECRET=your_webhook_secret

# تنظیمات امنیتی
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
CORS_ORIGINS=https://yourdomain.com

# تنظیمات پایگاه داده
DB_POOL_SIZE=20
DB_MAX_OVERFLOW=30
DB_POOL_TIMEOUT=30
```

#### فایل secrets
```bash
# secrets/bot_token
your_production_bot_token

# secrets/db_password
your_database_password

# secrets/webhook_secret
your_webhook_secret_key
```

## 🐳 استقرار با Docker

### 1. Dockerfile

#### Dockerfile اصلی
```dockerfile
# Dockerfile
FROM python:3.11-slim

# تنظیم متغیرهای محیطی
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# نصب وابستگی‌های سیستم
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ایجاد کاربر غیر root
RUN useradd --create-home --shell /bin/bash app

# تنظیم دایرکتوری کار
WORKDIR /app

# کپی فایل‌های requirements
COPY requirements.txt .

# نصب وابستگی‌های Python
RUN pip install --no-cache-dir -r requirements.txt

# کپی کد برنامه
COPY . .

# تغییر مالکیت فایل‌ها
RUN chown -R app:app /app

# تغییر به کاربر app
USER app

# تنظیم health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/health_check.py || exit 1

# اجرای برنامه
CMD ["python", "main.py"]
```

#### Multi-stage Dockerfile
```dockerfile
# Dockerfile.multi-stage
# مرحله ساخت
FROM python:3.11-slim as builder

WORKDIR /app

# نصب وابستگی‌های ساخت
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# نصب وابستگی‌ها
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# مرحله اجرا
FROM python:3.11-slim

# کپی وابستگی‌ها از مرحله ساخت
COPY --from=builder /root/.local /root/.local

# تنظیم PATH
ENV PATH=/root/.local/bin:$PATH

# نصب وابستگی‌های runtime
RUN apt-get update && apt-get install -y \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# ایجاد کاربر
RUN useradd --create-home --shell /bin/bash app

WORKDIR /app

# کپی کد
COPY . .
RUN chown -R app:app /app

USER app

HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python scripts/health_check.py || exit 1

CMD ["python", "main.py"]
```

### 2. Docker Compose

#### docker-compose.yml
```yaml
# docker-compose.yml
version: '3.8'

services:
  bot:
    build: .
    container_name: telegram_bot
    restart: unless-stopped
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/botdb
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis
    volumes:
      - ./logs:/app/logs
      - ./data:/app/data
    networks:
      - bot_network
    healthcheck:
      test: ["CMD", "python", "scripts/health_check.py"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15
    container_name: bot_postgres
    restart: unless-stopped
    environment:
      - POSTGRES_DB=botdb
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./backups:/backups
    networks:
      - bot_network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  redis:
    image: redis:7-alpine
    container_name: bot_redis
    restart: unless-stopped
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    networks:
      - bot_network
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: bot_nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
      - ./logs/nginx:/var/log/nginx
    depends_on:
      - bot
    networks:
      - bot_network

volumes:
  postgres_data:
  redis_data:

networks:
  bot_network:
    driver: bridge
```

#### docker-compose.production.yml
```yaml
# docker-compose.production.yml
version: '3.8'

services:
  bot:
    image: your-registry/telegram-bot:latest
    container_name: telegram_bot_prod
    restart: unless-stopped
    environment:
      - BOT_TOKEN_FILE=/run/secrets/bot_token
      - DATABASE_URL=postgresql://postgres:${DB_PASSWORD}@db:5432/botdb
    secrets:
      - bot_token
      - db_password
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

secrets:
  bot_token:
    file: ./secrets/bot_token
  db_password:
    file: ./secrets/db_password
```

### 3. اسکریپت‌های Docker

#### اسکریپت ساخت
```bash
#!/bin/bash
# scripts/docker_build.sh

set -e

echo "🏗️ ساخت Docker image..."

# تنظیم متغیرها
IMAGE_NAME="telegram-bot"
TAG=${1:-latest}
REGISTRY=${REGISTRY:-"your-registry.com"}

# ساخت image
docker build -t ${IMAGE_NAME}:${TAG} .

# تگ کردن برای registry
docker tag ${IMAGE_NAME}:${TAG} ${REGISTRY}/${IMAGE_NAME}:${TAG}

echo "✅ Image ساخته شد: ${REGISTRY}/${IMAGE_NAME}:${TAG}"

# اختیاری: push به registry
if [ "$2" = "push" ]; then
    echo "📤 Push به registry..."
    docker push ${REGISTRY}/${IMAGE_NAME}:${TAG}
    echo "✅ Image push شد"
fi
```

#### اسکریپت استقرار
```bash
#!/bin/bash
# scripts/docker_deploy.sh

set -e

echo "🚀 شروع استقرار..."

# بررسی فایل‌های ضروری
if [ ! -f ".env" ]; then
    echo "❌ فایل .env یافت نشد"
    exit 1
fi

# بررسی Docker و Docker Compose
command -v docker >/dev/null 2>&1 || { echo "❌ Docker نصب نیست"; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose نصب نیست"; exit 1; }

# توقف سرویس‌های قدیمی
echo "⏹️ توقف سرویس‌های قدیمی..."
docker-compose down

# دریافت آخرین image
echo "📥 دریافت آخرین image..."
docker-compose pull

# راه‌اندازی سرویس‌ها
echo "▶️ راه‌اندازی سرویس‌ها..."
docker-compose up -d

# بررسی وضعیت
echo "🔍 بررسی وضعیت سرویس‌ها..."
sleep 10
docker-compose ps

# تست health check
echo "🏥 تست health check..."
for i in {1..30}; do
    if docker-compose exec -T bot python scripts/health_check.py; then
        echo "✅ ربات با موفقیت راه‌اندازی شد"
        break
    fi
    echo "⏳ انتظار برای آماده شدن ربات... ($i/30)"
    sleep 10
done

echo "🎉 استقرار کامل شد!"
```

## 🖥️ استقرار روی VPS

### 1. تنظیم سرور

#### نصب وابستگی‌ها
```bash
#!/bin/bash
# scripts/setup_server.sh

set -e

echo "🔧 تنظیم سرور..."

# بروزرسانی سیستم
sudo apt update && sudo apt upgrade -y

# نصب Python و ابزارهای ضروری
sudo apt install -y \
    python3.11 \
    python3.11-venv \
    python3-pip \
    postgresql \
    postgresql-contrib \
    nginx \
    redis-server \
    git \
    curl \
    htop \
    ufw \
    fail2ban

# نصب Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# نصب Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# تنظیم فایروال
sudo ufw allow ssh
sudo ufw allow 80
sudo ufw allow 443
sudo ufw --force enable

echo "✅ سرور آماده شد"
```

#### ایجاد کاربر ربات
```bash
#!/bin/bash
# scripts/create_bot_user.sh

# ایجاد کاربر مخصوص ربات
sudo useradd -m -s /bin/bash botuser
sudo usermod -aG docker botuser

# ایجاد دایرکتوری‌های ضروری
sudo mkdir -p /opt/telegram-bot/{logs,data,backups}
sudo chown -R botuser:botuser /opt/telegram-bot

# تنظیم SSH key برای کاربر
sudo -u botuser mkdir -p /home/botuser/.ssh
sudo -u botuser chmod 700 /home/botuser/.ssh

echo "✅ کاربر botuser ایجاد شد"
```

### 2. تنظیم Systemd Service

#### فایل سرویس
```ini
# /etc/systemd/system/telegram-bot.service
[Unit]
Description=Telegram Bot Service
After=network.target postgresql.service redis.service
Wants=postgresql.service redis.service

[Service]
Type=simple
User=botuser
Group=botuser
WorkingDirectory=/opt/telegram-bot
Environment=PYTHONPATH=/opt/telegram-bot
EnvironmentFile=/opt/telegram-bot/.env
ExecStart=/opt/telegram-bot/venv/bin/python main.py
ExecReload=/bin/kill -HUP $MAINPID
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal
SyslogIdentifier=telegram-bot

# تنظیمات امنیتی
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/opt/telegram-bot/logs /opt/telegram-bot/data

[Install]
WantedBy=multi-user.target
```

#### مدیریت سرویس
```bash
# فعال‌سازی سرویس
sudo systemctl enable telegram-bot.service

# شروع سرویس
sudo systemctl start telegram-bot.service

# بررسی وضعیت
sudo systemctl status telegram-bot.service

# مشاهده لاگ‌ها
sudo journalctl -u telegram-bot.service -f

# ری‌استارت سرویس
sudo systemctl restart telegram-bot.service
```

### 3. تنظیم Nginx

#### فایل تنظیمات
```nginx
# /etc/nginx/sites-available/telegram-bot
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL Configuration
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # Security Headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # Webhook endpoint
    location /webhook {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Webhook specific settings
        proxy_read_timeout 30s;
        proxy_connect_timeout 10s;
        client_max_body_size 20M;
    }
    
    # Health check endpoint
    location /health {
        proxy_pass http://127.0.0.1:8000;
        access_log off;
    }
    
    # Static files (if any)
    location /static/ {
        alias /opt/telegram-bot/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
    
    # Logs
    access_log /var/log/nginx/telegram-bot.access.log;
    error_log /var/log/nginx/telegram-bot.error.log;
}
```

#### فعال‌سازی سایت
```bash
# فعال‌سازی سایت
sudo ln -s /etc/nginx/sites-available/telegram-bot /etc/nginx/sites-enabled/

# تست تنظیمات
sudo nginx -t

# ری‌استارت Nginx
sudo systemctl restart nginx

# نصب SSL با Let's Encrypt
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

## ☁️ استقرار در Cloud Services

### 1. AWS (Amazon Web Services)

#### EC2 Instance
```bash
#!/bin/bash
# scripts/aws_deploy.sh

# تنظیم AWS CLI
aws configure

# ایجاد Security Group
aws ec2 create-security-group \
    --group-name telegram-bot-sg \
    --description "Security group for Telegram bot"

# اضافه کردن قوانین
aws ec2 authorize-security-group-ingress \
    --group-name telegram-bot-sg \
    --protocol tcp \
    --port 22 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name telegram-bot-sg \
    --protocol tcp \
    --port 80 \
    --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
    --group-name telegram-bot-sg \
    --protocol tcp \
    --port 443 \
    --cidr 0.0.0.0/0

# راه‌اندازی instance
aws ec2 run-instances \
    --image-id ami-0c02fb55956c7d316 \
    --count 1 \
    --instance-type t3.micro \
    --key-name your-key-pair \
    --security-groups telegram-bot-sg \
    --user-data file://scripts/user-data.sh
```

#### ECS (Elastic Container Service)
```json
{
  "family": "telegram-bot",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "executionRoleArn": "arn:aws:iam::account:role/ecsTaskExecutionRole",
  "containerDefinitions": [
    {
      "name": "telegram-bot",
      "image": "your-account.dkr.ecr.region.amazonaws.com/telegram-bot:latest",
      "essential": true,
      "environment": [
        {
          "name": "BOT_TOKEN",
          "value": "your-bot-token"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/telegram-bot",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      },
      "healthCheck": {
        "command": ["CMD-SHELL", "python scripts/health_check.py || exit 1"],
        "interval": 30,
        "timeout": 5,
        "retries": 3
      }
    }
  ]
}
```

### 2. Google Cloud Platform

#### Cloud Run
```yaml
# cloudrun.yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: telegram-bot
  annotations:
    run.googleapis.com/ingress: all
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      containerConcurrency: 1000
      timeoutSeconds: 300
      containers:
      - image: gcr.io/your-project/telegram-bot:latest
        ports:
        - containerPort: 8080
        env:
        - name: BOT_TOKEN
          valueFrom:
            secretKeyRef:
              name: bot-secrets
              key: token
        resources:
          limits:
            cpu: 1000m
            memory: 512Mi
          requests:
            cpu: 100m
            memory: 128Mi
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 30
```

#### Deployment Script
```bash
#!/bin/bash
# scripts/gcp_deploy.sh

# تنظیم پروژه
gcloud config set project your-project-id

# ساخت و push image
gcloud builds submit --tag gcr.io/your-project-id/telegram-bot

# استقرار در Cloud Run
gcloud run deploy telegram-bot \
    --image gcr.io/your-project-id/telegram-bot \
    --platform managed \
    --region us-central1 \
    --allow-unauthenticated \
    --memory 512Mi \
    --cpu 1 \
    --max-instances 10 \
    --set-env-vars BOT_MODE=webhook
```

### 3. DigitalOcean

#### App Platform
```yaml
# .do/app.yaml
name: telegram-bot
services:
- name: bot
  source_dir: /
  github:
    repo: your-username/telegram-bot
    branch: main
    deploy_on_push: true
  run_command: python main.py
  environment_slug: python
  instance_count: 1
  instance_size_slug: basic-xxs
  env:
  - key: BOT_TOKEN
    scope: RUN_TIME
    type: SECRET
    value: your-bot-token
  - key: DATABASE_URL
    scope: RUN_TIME
    type: SECRET
    value: ${db.DATABASE_URL}
  health_check:
    http_path: /health
databases:
- name: db
  engine: PG
  version: "13"
  size_slug: db-s-dev-database
```

## 📊 مانیتورینگ و لاگ‌گیری

### 1. تنظیم Logging

#### فایل تنظیمات لاگ
```python
# core/logging_config.py
import logging
import logging.handlers
from pathlib import Path

def setup_logging(log_level: str = "INFO", log_dir: str = "logs"):
    """تنظیم سیستم لاگ‌گیری"""
    
    # ایجاد دایرکتوری لاگ
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # تنظیم formatter
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level.upper()))
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler با rotation
    file_handler = logging.handlers.RotatingFileHandler(
        log_path / "bot.log",
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Error file handler
    error_handler = logging.handlers.RotatingFileHandler(
        log_path / "error.log",
        maxBytes=10*1024*1024,
        backupCount=5
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
    
    # JSON handler برای structured logging
    json_handler = logging.handlers.RotatingFileHandler(
        log_path / "bot.json",
        maxBytes=10*1024*1024,
        backupCount=5
    )
    json_formatter = JsonFormatter()
    json_handler.setFormatter(json_formatter)
    root_logger.addHandler(json_handler)

class JsonFormatter(logging.Formatter):
    """Formatter برای خروجی JSON"""
    
    def format(self, record):
        import json
        from datetime import datetime
        
        log_entry = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'message': record.getMessage(),
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno
        }
        
        if record.exc_info:
            log_entry['exception'] = self.formatException(record.exc_info)
        
        return json.dumps(log_entry, ensure_ascii=False)
```

### 2. Health Check

#### اسکریپت بررسی سلامت
```python
# scripts/health_check.py
import asyncio
import sys
import logging
from datetime import datetime, timedelta
from core.config import Config
from core.database import Database

async def check_bot_health():
    """بررسی سلامت ربات"""
    try:
        config = Config()
        
        # بررسی تنظیمات
        config.validate()
        
        # بررسی پایگاه داده
        db = Database(config.DATABASE_URL)
        if not db.test_connection():
            raise Exception("اتصال به پایگاه داده ناموفق")
        
        # بررسی آخرین فعالیت
        last_activity = db.get_last_activity()
        if last_activity:
            time_diff = datetime.now() - last_activity
            if time_diff > timedelta(minutes=30):
                logging.warning(f"آخرین فعالیت: {time_diff} پیش")
        
        # بررسی فضای دیسک
        import shutil
        disk_usage = shutil.disk_usage('.')
        free_space_gb = disk_usage.free / (1024**3)
        if free_space_gb < 1:  # کمتر از 1 گیگابایت
            raise Exception(f"فضای دیسک کم: {free_space_gb:.2f} GB")
        
        # بررسی مصرف حافظه
        import psutil
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            raise Exception(f"مصرف حافظه بالا: {memory.percent}%")
        
        print("✅ ربات سالم است")
        return True
        
    except Exception as e:
        print(f"❌ خطا در بررسی سلامت: {e}")
        logging.error(f"Health check failed: {e}")
        return False

if __name__ == "__main__":
    result = asyncio.run(check_bot_health())
    sys.exit(0 if result else 1)
```

### 3. Monitoring با Prometheus

#### Metrics Exporter
```python
# monitoring/metrics.py
from prometheus_client import Counter, Histogram, Gauge, start_http_server
import time

# تعریف metrics
message_counter = Counter('bot_messages_total', 'تعداد کل پیام‌ها', ['message_type'])
response_time = Histogram('bot_response_time_seconds', 'زمان پاسخ ربات')
active_users = Gauge('bot_active_users', 'تعداد کاربران فعال')
error_counter = Counter('bot_errors_total', 'تعداد خطاها', ['error_type'])

class MetricsCollector:
    """کلاس جمع‌آوری metrics"""
    
    def __init__(self):
        self.start_time = time.time()
    
    def record_message(self, message_type: str):
        """ثبت پیام دریافتی"""
        message_counter.labels(message_type=message_type).inc()
    
    def record_response_time(self, duration: float):
        """ثبت زمان پاسخ"""
        response_time.observe(duration)
    
    def update_active_users(self, count: int):
        """بروزرسانی تعداد کاربران فعال"""
        active_users.set(count)
    
    def record_error(self, error_type: str):
        """ثبت خطا"""
        error_counter.labels(error_type=error_type).inc()

# شروع HTTP server برای metrics
def start_metrics_server(port: int = 8000):
    """شروع سرور metrics"""
    start_http_server(port)
    print(f"📊 Metrics server started on port {port}")

# استفاده در middleware
class MetricsMiddleware:
    """Middleware برای جمع‌آوری metrics"""
    
    def __init__(self, collector: MetricsCollector):
        self.collector = collector
    
    async def __call__(self, handler, event, data):
        start_time = time.time()
        
        try:
            # ثبت نوع پیام
            if hasattr(event, 'text'):
                self.collector.record_message('text')
            elif hasattr(event, 'photo'):
                self.collector.record_message('photo')
            
            # اجرای handler
            result = await handler(event, data)
            
            # ثبت زمان پاسخ
            duration = time.time() - start_time
            self.collector.record_response_time(duration)
            
            return result
            
        except Exception as e:
            # ثبت خطا
            self.collector.record_error(type(e).__name__)
            raise
```

## 🔒 امنیت در Production

### 1. تنظیمات امنیتی

#### Firewall Rules
```bash
#!/bin/bash
# scripts/setup_firewall.sh

# تنظیم UFW
sudo ufw --force reset
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH (تغییر پورت پیش‌فرض)
sudo ufw allow 2222/tcp

# HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# فعال‌سازی
sudo ufw --force enable

# تنظیم fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

cat << EOF | sudo tee -a /etc/fail2ban/jail.local
[sshd]
enabled = true
port = 2222
filter = sshd
logpath = /var/log/auth.log
maxretry = 3
bantime = 3600

[nginx-http-auth]
enabled = true
filter = nginx-http-auth
logpath = /var/log/nginx/error.log
maxretry = 5
bantime = 600
EOF

sudo systemctl restart fail2ban
```

#### SSL/TLS Configuration
```bash
#!/bin/bash
# scripts/setup_ssl.sh

# نصب Certbot
sudo apt install certbot python3-certbot-nginx

# دریافت گواهی SSL
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# تنظیم تجدید خودکار
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

# تست تجدید
sudo certbot renew --dry-run
```

### 2. Secrets Management

#### استفاده از HashiCorp Vault
```python
# core/secrets.py
import hvac
import os

class SecretsManager:
    """مدیریت secrets با Vault"""
    
    def __init__(self):
        self.client = hvac.Client(
            url=os.getenv('VAULT_URL', 'http://localhost:8200'),
            token=os.getenv('VAULT_TOKEN')
        )
    
    def get_secret(self, path: str, key: str) -> str:
        """دریافت secret"""
        try:
            response = self.client.secrets.kv.v2.read_secret_version(path=path)
            return response['data']['data'][key]
        except Exception as e:
            raise Exception(f"خطا در دریافت secret: {e}")
    
    def set_secret(self, path: str, secrets: dict):
        """تنظیم secret"""
        try:
            self.client.secrets.kv.v2.create_or_update_secret(
                path=path,
                secret=secrets
            )
        except Exception as e:
            raise Exception(f"خطا در تنظیم secret: {e}")

# استفاده
secrets = SecretsManager()
bot_token = secrets.get_secret('telegram-bot', 'token')
```

## 📋 چک‌لیست استقرار

### ✅ قبل از استقرار
- [ ] تست کامل در محیط development
- [ ] بررسی امنیت کد
- [ ] آماده‌سازی فایل‌های تنظیمات
- [ ] تهیه backup از داده‌ها
- [ ] تنظیم monitoring و alerting

### ✅ حین استقرار
- [ ] استقرار در محیط staging
- [ ] تست عملکرد
- [ ] بررسی logs
- [ ] تست load balancing
- [ ] تست failover

### ✅ بعد از استقرار
- [ ] مانیتورینگ metrics
- [ ] بررسی performance
- [ ] تست backup و restore
- [ ] مستندسازی تغییرات
- [ ] آموزش تیم

## 🔗 مراحل بعدی

- [بهینه‌سازی عملکرد](OPTIMIZATION.md)
- [مانیتورینگ و نظارت](MONITORING.md)
- [پشتیبان‌گیری و بازیابی](BACKUP.md)