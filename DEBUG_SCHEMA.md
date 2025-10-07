# Отладка проблемы с is_premium на Render

## Проблема
```
psycopg2.errors.UndefinedColumn: column users.is_premium does not exist
```

## Причина
Скрипт `update_schema.py` не выполнился успешно во время сборки, либо не смог подключиться к базе данных.

## Решения

### 1. Автоматическое решение (через force_update_schema.py)
Новый скрипт `force_update_schema.py` использует:
- Прямое подключение через psycopg2
- PL/pgSQL блок DO для идемпотентного добавления колонки
- Подробное логирование
- Выход с ошибкой если не удалось

### 2. Ручное решение (через Render Shell)
Если автоматический скрипт не сработал, подключись к Render Shell:

```bash
# В Render Dashboard -> Shell
python force_update_schema.py
```

### 3. Прямое SQL решение
Подключись к PostgreSQL напрямую:

```sql
-- Подключись к БД через Render Dashboard -> Database -> Connect
\c ittoken_db

-- Установи search_path
SET search_path TO goalpredictor;

-- Добавь колонку если не существует
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_schema = 'goalpredictor'
        AND table_name = 'users'
        AND column_name = 'is_premium'
    ) THEN
        ALTER TABLE goalpredictor.users 
        ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Проверь результат
SELECT column_name 
FROM information_schema.columns 
WHERE table_schema = 'goalpredictor' 
AND table_name = 'users';
```

### 4. Обновление существующих записей
После добавления колонки:

```sql
-- Установи search_path
SET search_path TO goalpredictor;

-- Обнови всех пользователей (установи is_premium = false по умолчанию)
UPDATE users SET is_premium = false WHERE is_premium IS NULL;

-- Сделай админа premium
UPDATE users SET is_premium = true WHERE email = 'admin@goalpredictor.ai';
```

## Проверка логов на Render

### Что искать в логах сборки:
```
🔧 FORCE: Добавление is_premium в таблицу users
✓ DATABASE_URL found
✓ Using schema: goalpredictor
✅ SUCCESS: Column is_premium is present in users table
✅ Schema update completed successfully
```

### Если видишь ошибку:
```
❌ ERROR: DATABASE_URL environment variable not found!
```
**Решение:** Проверь переменные окружения в Render Dashboard.

```
❌ ERROR: Column is_premium not found after ALTER TABLE!
```
**Решение:** Используй ручное SQL решение (способ #3).

## Проверка после деплоя

### 1. Проверь, что колонка создана
В Render Shell:
```bash
python -c "from app import create_app; from extensions import db; app = create_app(); app.app_context().push(); result = db.session.execute(db.text('SELECT column_name FROM information_schema.columns WHERE table_schema = \\'goalpredictor\\' AND table_name = \\'users\\' AND column_name = \\'is_premium\\'')); print('is_premium exists:', result.fetchone() is not None)"
```

### 2. Проверь, что админ создан
```bash
python -c "from app import create_app; from models import User; app = create_app(); app.app_context().push(); admin = User.query.filter_by(email='admin@goalpredictor.ai').first(); print('Admin exists:', admin is not None)"
```

## Профилактика на будущее

### Использовать Flask-Migrate (Alembic)
```bash
# Создать миграцию
flask db migrate -m "Add is_premium column"

# Применить миграцию
flask db upgrade
```

### Добавить в render.yaml:
```yaml
buildCommand: "pip install --upgrade pip && pip install -r requirements.txt && flask db upgrade && python create_default_admin.py"
```

## Контакты для отладки
- DATABASE_URL: `postgresql://ittoken_db_user:***@dpg-d0visga4d50c73ekmu4g-a/ittoken_db`
- DATABASE_SCHEMA: `goalpredictor`
- Admin Email: `admin@goalpredictor.ai`
- Admin Password: `Admin123!`
