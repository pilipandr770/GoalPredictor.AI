# GoalPredictor.AI - Руководство по развертыванию

## 🚀 Развертывание в продакшен

### 1. Подготовка сервера

Рекомендуемая конфигурация:
- **OS:** Ubuntu 22.04 LTS
- **RAM:** 2GB минимум, 4GB рекомендуется
- **CPU:** 2 ядра
- **Диск:** 20GB SSD

### 2. Установка зависимостей

```bash
# Обновить систему
sudo apt update && sudo apt upgrade -y

# Установить Python и зависимости
sudo apt install python3.10 python3.10-venv python3-pip nginx postgresql redis-server -y

# Установить supervisor для управления процессами
sudo apt install supervisor -y
```

### 3. Настройка PostgreSQL

```bash
# Войти в PostgreSQL
sudo -u postgres psql

# Создать базу данных и пользователя
CREATE DATABASE goalpredictor;
CREATE USER goalpredictor_user WITH PASSWORD 'your_strong_password';
GRANT ALL PRIVILEGES ON DATABASE goalpredictor TO goalpredictor_user;
\q
```

### 4. Клонирование и настройка проекта

```bash
# Создать директорию для приложения
sudo mkdir -p /var/www/goalpredictor
sudo chown $USER:$USER /var/www/goalpredictor

# Клонировать репозиторий
cd /var/www/goalpredictor
git clone https://github.com/your-repo/goalpredictor.git .

# Создать виртуальное окружение
python3 -m venv venv
source venv/bin/activate

# Установить зависимости
pip install -r requirements.txt
pip install gunicorn
```

### 5. Настройка переменных окружения

```bash
# Создать .env файл
nano .env
```

Заполните продакшен переменные:

```env
FLASK_ENV=production
DEBUG=False
SECRET_KEY=your-super-secret-production-key-here

# PostgreSQL
DATABASE_URL=postgresql://goalpredictor_user:your_strong_password@localhost/goalpredictor

# API Keys
FOOTBALL_API_KEY=your-api-key
OPENAI_API_KEY=your-api-key
STRIPE_SECRET_KEY=your-stripe-key
STRIPE_WEBHOOK_SECRET=your-webhook-secret

# Redis
REDIS_URL=redis://localhost:6379/0

# Application
APP_URL=https://goalpredictor.ai
```

### 6. Инициализация базы данных

```bash
# Активировать venv
source venv/bin/activate

# Создать таблицы
python -c "from app import create_app, db; app = create_app('production'); app.app_context().push(); db.create_all()"
```

### 7. Настройка Gunicorn

Создать файл `gunicorn_config.py`:

```python
import multiprocessing

bind = "127.0.0.1:8000"
workers = multiprocessing.cpu_count() * 2 + 1
worker_class = "sync"
timeout = 120
keepalive = 5
errorlog = "/var/www/goalpredictor/logs/gunicorn_error.log"
accesslog = "/var/www/goalpredictor/logs/gunicorn_access.log"
```

### 8. Настройка Supervisor

Создать файл `/etc/supervisor/conf.d/goalpredictor.conf`:

```ini
[program:goalpredictor]
directory=/var/www/goalpredictor
command=/var/www/goalpredictor/venv/bin/gunicorn -c gunicorn_config.py app:app
user=www-data
autostart=true
autorestart=true
stopasgroup=true
killasgroup=true
stderr_logfile=/var/log/goalpredictor/gunicorn.err.log
stdout_logfile=/var/log/goalpredictor/gunicorn.out.log
```

Запустить:

```bash
sudo mkdir -p /var/log/goalpredictor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start goalpredictor
```

### 9. Настройка Nginx

Создать файл `/etc/nginx/sites-available/goalpredictor`:

```nginx
server {
    listen 80;
    server_name goalpredictor.ai www.goalpredictor.ai;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/goalpredictor/static;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
}
```

Активировать:

```bash
sudo ln -s /etc/nginx/sites-available/goalpredictor /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### 10. Настройка SSL (Let's Encrypt)

```bash
# Установить certbot
sudo apt install certbot python3-certbot-nginx -y

# Получить сертификат
sudo certbot --nginx -d goalpredictor.ai -d www.goalpredictor.ai
```

### 11. Настройка планировщика (Cron)

```bash
# Редактировать crontab
crontab -e

# Добавить задачи
# Обновление данных каждое утро в 7:00
0 7 * * * /var/www/goalpredictor/venv/bin/python /var/www/goalpredictor/services/scheduler.py update_fixtures

# Генерация прогнозов в 8:00
0 8 * * * /var/www/goalpredictor/venv/bin/python /var/www/goalpredictor/services/scheduler.py generate_predictions

# Обновление результатов каждые 2 часа
0 */2 * * * /var/www/goalpredictor/venv/bin/python /var/www/goalpredictor/services/scheduler.py update_results
```

### 12. Настройка мониторинга

Установка и настройка мониторинга (опционально):

```bash
# Установить Prometheus и Grafana
sudo apt install prometheus grafana -y

# Настроить метрики Flask
pip install prometheus-flask-exporter
```

### 13. Резервное копирование

Настроить автоматическое резервное копирование базы данных:

```bash
# Создать скрипт backup.sh
#!/bin/bash
BACKUP_DIR="/var/backups/goalpredictor"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# Backup PostgreSQL
pg_dump -U goalpredictor_user goalpredictor > $BACKUP_DIR/db_$DATE.sql

# Удалить старые бэкапы (старше 7 дней)
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete

# Добавить в crontab (каждый день в 3:00)
# 0 3 * * * /var/www/goalpredictor/backup.sh
```

## 🔧 Обслуживание

### Просмотр логов

```bash
# Gunicorn logs
tail -f /var/log/goalpredictor/gunicorn.out.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Supervisor
sudo supervisorctl tail goalpredictor
```

### Перезапуск сервисов

```bash
# Перезапустить приложение
sudo supervisorctl restart goalpredictor

# Перезапустить Nginx
sudo systemctl restart nginx

# Перезапустить PostgreSQL
sudo systemctl restart postgresql
```

### Обновление приложения

```bash
cd /var/www/goalpredictor
git pull origin main
source venv/bin/activate
pip install -r requirements.txt --upgrade
sudo supervisorctl restart goalpredictor
```

## 🐳 Docker (альтернатива)

Создать `Dockerfile`:

```dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["gunicorn", "-c", "gunicorn_config.py", "app:app"]
```

Создать `docker-compose.yml`:

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://postgres:postgres@db:5432/goalpredictor
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  db:
    image: postgres:15
    environment:
      - POSTGRES_DB=goalpredictor
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
    depends_on:
      - web

volumes:
  postgres_data:
```

Запуск:

```bash
docker-compose up -d
```

## 📊 Мониторинг производительности

### Метрики для отслеживания

- Response time API endpoints
- Database query performance
- ML model prediction time
- Memory usage
- CPU usage
- Error rate
- Active users

### Алерты

Настроить уведомления для:
- Downtime (>1 минута)
- High error rate (>5%)
- Slow response time (>2 секунды)
- Database connection failures
- API rate limits exceeded

## 🔒 Безопасность

### Чеклист безопасности

- [ ] HTTPS enabled (SSL certificate)
- [ ] Firewall configured (UFW)
- [ ] SSH key-based authentication only
- [ ] Regular security updates
- [ ] Database backups
- [ ] Environment variables secured
- [ ] Rate limiting enabled
- [ ] CORS configured properly
- [ ] SQL injection protection
- [ ] XSS protection
- [ ] CSRF tokens
- [ ] Password hashing (bcrypt)
- [ ] Stripe webhook signature verification

## 📞 Поддержка

При возникновении проблем:
- Проверьте логи
- Убедитесь что все сервисы запущены
- Проверьте переменные окружения
- Свяжитесь с поддержкой: support@goalpredictor.ai
