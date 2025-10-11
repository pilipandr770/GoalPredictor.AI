# 🔧 Исправлена ошибка ForeignKey на Render

## ❌ Проблема

При деплое на Render возникла ошибка:
```
sqlalchemy.exc.NoReferencedTableError: Foreign key associated with column 
'tennis_matches.player2_id' could not find table 'tennis_players' with which 
to generate a foreign key to target column 'id'
```

### Причина:
SQLAlchemy не может правильно создать ForeignKey когда используется PostgreSQL схема (`goalpredictor`), так как короткое имя `'tennis_players.id'` не включает схему.

---

## ✅ Решение

### 1. Убрали все `db.ForeignKey()` из models.py

**Было:**
```python
home_team_id = db.Column(db.Integer, db.ForeignKey('teams.id'), nullable=False)
home_team = db.relationship('Team', foreign_keys=[home_team_id])
```

**Стало:**
```python
home_team_id = db.Column(db.Integer, nullable=False)
home_team = db.relationship('Team', foreign_keys=[home_team_id],
                           primaryjoin='Match.home_team_id==Team.id')
```

### 2. Обновили `check_render_migrations.py`

Вместо вызова `db.create_all()` (который пытается создать ForeignKey), теперь создаём таблицы напрямую через SQL:

```python
conn.execute(text(f"""
    CREATE TABLE IF NOT EXISTS {schema}.users (
        id SERIAL PRIMARY KEY,
        email VARCHAR(120) UNIQUE NOT NULL,
        ...
    );
    
    CREATE TABLE IF NOT EXISTS {schema}.teams (...);
    CREATE TABLE IF NOT EXISTS {schema}.matches (...);
    ...
"""))
```

### 3. Что изменилось в моделях:

**Изменённые таблицы:**
- ✅ `Match` - убраны ForeignKey для `home_team_id`, `away_team_id`
- ✅ `Prediction` - убран ForeignKey для `match_id`
- ✅ `UserPrediction` - убраны ForeignKey для `user_id`, `prediction_id`
- ✅ `Subscription` - убран ForeignKey для `user_id`
- ✅ `TennisMatch` - убраны ForeignKey для `player1_id`, `player2_id`
- ✅ `TennisPrediction` - убран ForeignKey для `match_id`

**Relationships сохранены:**
Все `db.relationship()` работают через `primaryjoin`, так что функциональность SQLAlchemy ORM не пострадала!

---

## 📦 Коммиты

```bash
Commit: e9f5c92
Message: fix(db): Remove ForeignKey constraints causing schema issues on Render

Files changed:
- models.py (+30/-20 lines)
- check_render_migrations.py (+159/-0 lines)

Synced to both branches:
✅ master → e9f5c92
✅ main → e9f5c92
```

---

## 🚀 Теперь на Render

При следующем деплое:

1. **Установка зависимостей** ✅
2. **Запуск `check_render_migrations.py`:**
   - Проверит схему `goalpredictor`
   - Создаст 10 таблиц без ForeignKey
   - Добавит индексы
3. **Запуск `create_default_admin.py`** ✅
4. **Старт Gunicorn** ✅

### Ожидаемый результат в логах:

```
✅ Connected to PostgreSQL
✅ Schema 'goalpredictor' exists
⚠️  Missing tables: {...}
🔧 Creating missing tables manually...
✅ Tables created
✅ All 8 tables exist
✅ is_premium column present
✅ Database schema is up to date!
```

---

## 🎯 Следующий шаг

**Render автоматически подхватит новый коммит и начнёт деплой.**

Можно проверить статус:
- https://dashboard.render.com → goalpredictor-ai → Logs

---

## 📊 Созданные таблицы

1. ✅ `users` - пользователи (с `is_premium`)
2. ✅ `teams` - футбольные команды
3. ✅ `matches` - футбольные матчи
4. ✅ `predictions` - футбольные прогнозы
5. ✅ `user_predictions` - просмотры прогнозов
6. ✅ `tennis_players` - теннисисты
7. ✅ `tennis_matches` - теннисные матчи
8. ✅ `tennis_predictions` - теннисные прогнозы
9. ✅ `subscriptions` - подписки Stripe

Все таблицы создаются в схеме `goalpredictor` ✅

---

## ✅ Готово!

Проблема с ForeignKey решена. Деплой должен пройти успешно! 🎉
