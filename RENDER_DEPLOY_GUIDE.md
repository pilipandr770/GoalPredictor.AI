# 🚀 Деплой GoalPredictor.AI на Render.com

## 📋 Подготовка к деплою

### 1. Предварительные требования

- ✅ Аккаунт на [Render.com](https://render.com)
- ✅ PostgreSQL база данных на Render (уже создана)
- ✅ Репозиторий на GitHub (pilipandr770/GoalPredictor.AI)
- ✅ API ключи (Football-Data.org, OpenAI)

### 2. Структура проекта

```
GoalPredictor.AI/
├── render.yaml              # Конфигурация Render
├── gunicorn_config.py       # Настройки Gunicorn
├── migrate_to_postgres.py   # Миграция на PostgreSQL
├── Procfile                 # Альтернативный запуск
├── runtime.txt              # Версия Python
├── requirements.txt         # Зависимости Python
├── .env.production         # Переменные окружения (не коммитить!)
└── app.py                  # Главный файл приложения
```

## 🗄️ База данных PostgreSQL

### Информация о базе данных:

```
URL: postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a/ittoken_db
Host: dpg-d0visga4d50c73ekmu4g-a
Database: ittoken_db
User: ittoken_db_user
Schema: goalpredictor (отдельная схема для этого проекта)
```

**⚠️ ВАЖНО:** Мы используем **отдельную схему** `goalpredictor` для изоляции данных от других проектов!

## 📦 Деплой через Render Dashboard

### Шаг 1: Создание Web Service

1. Зайдите в [Render Dashboard](https://dashboard.render.com)
2. Нажмите **"New +"** → **"Web Service"**
3. Подключите GitHub репозиторий `pilipandr770/GoalPredictor.AI`
4. Настройте следующие параметры:

#### Основные настройки:

| Параметр | Значение |
|----------|----------|
| **Name** | `goalpredictor-ai` |
| **Region** | `Frankfurt (EU Central)` |
| **Branch** | `master` |
| **Runtime** | `Python 3` |
| **Build Command** | `pip install -r requirements.txt && python migrate_to_postgres.py` |
| **Start Command** | `gunicorn --config gunicorn_config.py app:app` |
| **Plan** | `Free` (или `Starter`) |

### Шаг 2: Настройка переменных окружения

В разделе **Environment Variables** добавьте:

#### 🔐 Обязательные переменные:

```bash
# Database
DATABASE_URL=postgresql://ittoken_db_user:Xm98VVSZv7cMJkopkdWRkgvZzC7Aly42@dpg-d0visga4d50c73ekmu4g-a/ittoken_db
DATABASE_SCHEMA=goalpredictor

# Flask
FLASK_ENV=production
SECRET_KEY=[Сгенерируйте в Render - автоматически]
DEBUG=False

# APIs
FOOTBALL_DATA_API_KEY=ваш_ключ_football_data_org
OPENAI_API_KEY=ваш_ключ_openai

# Security
SESSION_COOKIE_SECURE=True
SESSION_COOKIE_HTTPONLY=True
```

#### 📝 Опциональные переменные:

```bash
# Stripe (для будущих платежей)
STRIPE_PUBLIC_KEY=pk_...
STRIPE_SECRET_KEY=sk_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (если настроите)
MAIL_USERNAME=your_email@gmail.com
MAIL_PASSWORD=your_app_password
```

### Шаг 3: Auto Deploy

✅ Включите **"Auto-Deploy"** - при каждом push в `master` будет автоматический деплой

## 🔄 Автоматический деплой через render.yaml

Вместо ручной настройки можно использовать `render.yaml`:

1. Зайдите в Render Dashboard
2. **"New +"** → **"Blueprint"**
3. Подключите репозиторий
4. Render автоматически прочитает `render.yaml` и создаст сервис

**⚠️ Не забудьте:** добавить API ключи вручную в Dashboard (они не хранятся в render.yaml)

## 🗃️ Миграция базы данных

### Автоматическая миграция

При деплое автоматически выполнится скрипт `migrate_to_postgres.py`, который:

1. ✅ Создаст схему `goalpredictor` в PostgreSQL
2. ✅ Создаст все таблицы в этой схеме
3. ✅ Настроит `search_path` для изоляции данных

### Ручная миграция (если нужно)

```bash
# В Render Shell или локально с подключением к Render DB
python migrate_to_postgres.py
```

### Проверка миграции

```bash
# Подключитесь к БД через Render Shell
psql $DATABASE_URL

# Проверьте схему
\dn

# Проверьте таблицы
\dt goalpredictor.*

# Смените схему по умолчанию
SET search_path TO goalpredictor, public;

# Проверьте данные
SELECT * FROM goalpredictor.users LIMIT 5;
```

## 🚦 Проверка деплоя

### 1. Health Check

После деплоя откройте:
```
https://goalpredictor-ai.onrender.com/
```

### 2. Проверка логов

В Render Dashboard → вкладка **"Logs"**:

```
✅ Ищите сообщения:
- "🚀 GoalPredictor.AI starting on Render.com..."
- "✅ Server is ready. Waiting for requests..."
- "📦 Creating schema: goalpredictor"
- "✅ All tables created successfully"
```

### 3. Проверка API endpoints

```bash
# Главная страница
curl https://goalpredictor-ai.onrender.com/

# API проверка
curl https://goalpredictor-ai.onrender.com/api/matches/today

# Прогнозы
curl https://goalpredictor-ai.onrender.com/predictions
```

## 🔧 Настройка после деплоя

### 1. Загрузка исторических данных

Выполните в Render Shell:

```bash
python load_real_historical_data.py
```

Это загрузит ~5000 матчей из CSV файлов (2020-2025).

### 2. Тренировка моделей

```bash
python ml/train.py
```

Обучит ML модели на исторических данных.

### 3. Создание админа

```bash
python create_admin.py
```

## 📊 Планировщик задач

### APScheduler на Render

Планировщик автоматически запустится с приложением и будет выполнять:

- **Каждый день в 07:00** - Обновление расписания матчей
- **Каждый день в 08:00** - Генерация прогнозов
- **Каждый день в 16:00** - Обновление результатов

### Background Worker (опционально)

Для более надежного выполнения фоновых задач создайте отдельный Worker:

1. **"New +"** → **"Background Worker"**
2. **Start Command:** `python -m celery -A app.celery worker --loglevel=info`

## ⚙️ Настройки производительности

### Gunicorn Workers

В `gunicorn_config.py` настроено:

```python
workers = WEB_CONCURRENCY * 2 + 1  # обычно 4-8 workers
timeout = 120  # 2 минуты на запрос
```

### Database Pool

В `config.py` настроено:

```python
pool_size = 5
max_overflow = 10
pool_recycle = 3600  # 1 час
```

## 🔒 Безопасность

### Обязательно настройте:

1. ✅ Сгенерируйте `SECRET_KEY` в Render (автоматически)
2. ✅ Установите `SESSION_COOKIE_SECURE=True`
3. ✅ Используйте HTTPS (автоматически на Render)
4. ✅ Не коммитьте `.env.production` в Git
5. ✅ Регулярно ротируйте API ключи

## 🐛 Troubleshooting

### Проблема: "Migration failed"

**Решение:**
```bash
# Проверьте подключение к БД
psql $DATABASE_URL

# Вручную создайте схему
CREATE SCHEMA IF NOT EXISTS goalpredictor;

# Запустите миграцию снова
python migrate_to_postgres.py
```

### Проблема: "Table already exists"

**Решение:** Это нормально если перезапускаете деплой. Проверьте что таблицы в правильной схеме:
```sql
\dt goalpredictor.*
```

### Проблема: "App crashed - Workers timeout"

**Решение:** Увеличьте timeout в `gunicorn_config.py`:
```python
timeout = 180  # 3 минуты
```

### Проблема: "Memory limit exceeded"

**Решение:** 
- Уменьшите количество workers
- Апгрейдите план на Render (Starter или выше)
- Оптимизируйте загрузку ML моделей

## 📈 Мониторинг

### Render Metrics

В Dashboard доступны метрики:
- CPU usage
- Memory usage
- Response time
- Error rate

### Логирование

Все логи доступны в реальном времени:
```
Dashboard → Your Service → Logs
```

## 🔄 Обновления

### Автоматические обновления

При push в `master` ветку:
1. Render автоматически запустит build
2. Выполнит миграции
3. Перезапустит сервис

### Ручное обновление

В Dashboard → **"Manual Deploy"** → **"Deploy latest commit"**

## 📝 Полезные команды

### Render Shell

```bash
# Открыть shell в контейнере
render shell

# Проверить версию Python
python --version

# Проверить установленные пакеты
pip list

# Проверить переменные окружения
env | grep DATABASE

# Запустить Python REPL
python
```

### PostgreSQL

```bash
# Подключиться к БД
psql $DATABASE_URL

# Список схем
\dn

# Список таблиц в схеме
\dt goalpredictor.*

# Выйти
\q
```

## 🎉 Готово!

После успешного деплоя ваше приложение будет доступно по адресу:

**https://goalpredictor-ai.onrender.com**

### Следующие шаги:

1. ✅ Протестируйте все страницы
2. ✅ Загрузите исторические данные
3. ✅ Обучите ML модели
4. ✅ Настройте домен (опционально)
5. ✅ Настройте мониторинг
6. ✅ Запустите продвижение! 🚀

---

## 🆘 Поддержка

Если возникли проблемы:

1. Проверьте логи в Render Dashboard
2. Проверьте подключение к PostgreSQL
3. Убедитесь что все переменные окружения установлены
4. Проверьте что схема `goalpredictor` создана

**Email:** andrii.it.info@gmail.com
