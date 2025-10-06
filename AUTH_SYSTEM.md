# 🔐 Система аутентификации и админ-панель - GoalPredictor.AI

## ✅ Реализовано

### 1. **Система регистрации и входа**
- ✅ Красивые страницы `/login` и `/register` с градиентным дизайном
- ✅ Валидация паролей с индикатором силы пароля
- ✅ Автоматическое перенаправление после входа
- ✅ Flask-Login интеграция для управления сессиями

### 2. **Админ-панель**
- ✅ Полнофункциональная панель управления на `/admin`
- ✅ Статистика пользователей в реальном времени
- ✅ Управление пользователями (обновление до Premium, удаление)
- ✅ Просмотр подписок и платежей
- ✅ Поиск и фильтрация пользователей

### 3. **API эндпоинты**
- ✅ `POST /api/auth/register` - регистрация нового пользователя
- ✅ `POST /api/auth/login` - вход в систему
- ✅ `POST /api/auth/logout` - выход
- ✅ `GET /api/admin/stats` - статистика для админа
- ✅ `GET /api/admin/users` - список пользователей
- ✅ `POST /api/admin/users/<id>/upgrade` - обновление до Premium
- ✅ `DELETE /api/admin/users/<id>` - удаление пользователя

### 4. **Модель данных**
- ✅ Поле `is_admin` для определения администраторов
- ✅ Поле `is_premium` для Premium пользователей
- ✅ Счетчики использования прогнозов
- ✅ Временные метки (created_at, last_login)

### 5. **Архитектура**
- ✅ Исправлены циклические импорты (создан `extensions.py`)
- ✅ Правильная инициализация SQLAlchemy
- ✅ Безопасное хранение паролей (werkzeug hashing)
- ✅ Декоратор `@admin_required` для защиты эндпоинтов

---

## 🚀 Быстрый старт

### 1. Создание первого администратора

**Вариант A: Через Python команду (быстро)**
```powershell
py -c "from app import create_app; from extensions import db; from models import User; app = create_app(); app.app_context().push(); admin = User(username='admin', email='admin@goalpredictor.ai', is_admin=True, is_premium=True, is_active=True); admin.set_password('admin123'); db.session.add(admin); db.session.commit(); print('✅ Администратор создан')"
```

**Вариант B: Через скрипт**
```powershell
py create_admin.py
```

### 2. Запуск приложения
```powershell
py app.py
```

### 3. Вход в систему

**Администратор:**
- Email: `admin@goalpredictor.ai`
- Пароль: `admin123`
- URL: http://localhost:5000/login

После входа вы будете автоматически перенаправлены в админ-панель: http://localhost:5000/admin

---

## 📋 Основные маршруты

### Веб-страницы
| Маршрут | Описание | Требует авторизации |
|---------|----------|---------------------|
| `/` | Главная страница | Нет |
| `/login` | Страница входа | Нет |
| `/register` | Страница регистрации | Нет |
| `/predictions` | Прогнозы AI | Нет |
| `/admin` | Админ-панель | **Да (Admin)** |
| `/profile` | Профиль пользователя | Да |

### API эндпоинты

#### Аутентификация
```javascript
// Регистрация
POST /api/auth/register
{
  "username": "testuser",
  "email": "test@example.com",
  "password": "password123"
}

// Вход
POST /api/auth/login
{
  "email": "test@example.com",
  "password": "password123"
}

// Выход
POST /api/auth/logout
```

#### Администрирование (требуется is_admin=True)
```javascript
// Статистика
GET /api/admin/stats
Response: {
  "total_users": 10,
  "premium_users": 3,
  "total_predictions": 150,
  "estimated_revenue": 30
}

// Список пользователей
GET /api/admin/users?page=1&per_page=50

// Обновить до Premium
POST /api/admin/users/1/upgrade

// Удалить пользователя
DELETE /api/admin/users/1
```

---

## 🎨 Возможности админ-панели

### Статистические карточки
- 👥 **Всего пользователей** - общее количество зарегистрированных
- ⭐ **Premium подписчиков** - количество платных аккаунтов
- 💰 **Общий доход** - приблизительная оценка ($10/пользователь)
- 📊 **Всего прогнозов** - использование системы

### Управление пользователями
- **Поиск** по email или имени
- **Фильтрация**: все / Premium / Free / Админы
- **Действия**:
  - ⭐ Обновить до Premium (вручную)
  - 🗑️ Удалить пользователя
- **Информация**: ID, имя, email, статус, количество прогнозов, даты

### Подписки
- Список всех активных Premium подписок
- Тип подписки, даты начала и окончания
- Статус активности

---

## 🔒 Безопасность

### Реализованные меры:
✅ **Хеширование паролей** - werkzeug.security (PBKDF2 + SHA256)
✅ **Flask-Login** - управление сессиями
✅ **Декораторы защиты** - `@login_required`, `@admin_required`
✅ **Валидация email** - проверка уникальности
✅ **CORS** - настроено через flask-cors
✅ **Secret Key** - для подписи сессий

### Рекомендации для продакшна:
⚠️ Установите сложный SECRET_KEY в `.env`
⚠️ Используйте HTTPS
⚠️ Настройте rate limiting (flask-limiter)
⚠️ Добавьте CSRF защиту
⚠️ Включите двухфакторную аутентификацию

---

## 🗄️ Структура базы данных

### Таблица `users`
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(120) UNIQUE NOT NULL,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    
    -- Роли
    is_admin BOOLEAN DEFAULT FALSE,
    is_premium BOOLEAN DEFAULT FALSE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- Подписка
    subscription_id VARCHAR(255),
    subscription_end DATETIME,
    
    -- Статистика
    daily_predictions_count INTEGER DEFAULT 0,
    last_prediction_date DATE,
    
    -- Метаданные
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_login DATETIME
);
```

---

## 📁 Структура файлов

```
GoalPredictor.AI/
├── app.py                      # Главный файл приложения
├── extensions.py               # Flask расширения (db, login_manager)
├── models.py                   # Модели базы данных
├── config.py                   # Конфигурация
├── init_db.py                  # Инициализация БД
├── create_admin.py             # Создание администратора
├── test_login.py               # Тест аутентификации
│
├── api/
│   ├── routes_auth.py         # API для регистрации/входа
│   ├── routes_admin.py        # API для админ-панели
│   ├── routes_users.py        # API пользователей
│   └── routes_matches.py      # API матчей
│
├── templates/
│   ├── base.html              # Базовый шаблон
│   ├── login.html             # Страница входа
│   ├── register.html          # Страница регистрации
│   ├── admin/
│   │   └── dashboard.html     # Админ-панель
│   └── predictions.html       # Прогнозы
│
└── instance/
    └── goalpredictor.db       # База данных SQLite
```

---

## 🧪 Тестирование

### Тест входа
```powershell
py test_login.py
```

**Ожидаемый результат:**
```json
{
  "success": true,
  "message": "Вход выполнен успешно",
  "user": {
    "id": 1,
    "username": "admin",
    "email": "admin@goalpredictor.ai",
    "is_premium": true,
    "is_admin": true
  }
}
```

### Ручное тестирование

1. **Регистрация нового пользователя:**
   - Откройте http://localhost:5000/register
   - Заполните форму
   - Проверьте индикатор силы пароля
   - Нажмите "Зарегистрироваться"

2. **Вход:**
   - Откройте http://localhost:5000/login
   - Введите email и пароль
   - Проверьте перенаправление

3. **Админ-панель:**
   - Войдите как администратор
   - Откройте http://localhost:5000/admin
   - Проверьте статистику
   - Попробуйте поиск пользователей
   - Протестируйте обновление до Premium

---

## 🐛 Решенные проблемы

### Проблема: Циклические импорты
**Ошибка:** `RuntimeError: The current Flask app is not registered with this 'SQLAlchemy' instance`

**Решение:** Создан файл `extensions.py`, все импорты `from app import db` заменены на `from extensions import db`

**Затронутые файлы:**
- models.py
- api/routes_auth.py
- api/routes_admin.py
- api/routes_users.py
- api/routes_matches.py
- api/routes_subscriptions.py
- services/stripe_service.py
- services/scheduler.py

### Проблема: База данных не инициализирована
**Решение:** Создан скрипт `init_db.py` для создания всех таблиц

### Проблема: Нет администратора
**Решение:** Быстрая команда через Python CLI для создания админа

---

## 📝 TODO (будущие улучшения)

- [ ] Email верификация при регистрации
- [ ] Восстановление пароля
- [ ] Двухфакторная аутентификация (2FA)
- [ ] OAuth (Google, GitHub)
- [ ] Rate limiting
- [ ] CSRF защита
- [ ] Логирование действий администратора
- [ ] Экспорт данных пользователей (CSV/JSON)
- [ ] Графики и аналитика в админ-панели
- [ ] Уведомления по email

---

## 🎉 Готово к использованию!

Система полностью функциональна и готова к тестированию. Все основные функции работают:
- ✅ Регистрация
- ✅ Вход/выход
- ✅ Админ-панель
- ✅ Управление пользователями
- ✅ API эндпоинты

**Приложение запущено на:** http://localhost:5000

**Администратор:**
- Email: `admin@goalpredictor.ai`
- Пароль: `admin123`

---

*Дата создания: 6 октября 2025*
*Версия: 1.0*
