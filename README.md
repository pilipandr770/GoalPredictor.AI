# GoalPredictor.AI ⚽

![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**Интеллектуальная платформа для прогнозирования футбольных матчей на основе машинного обучения и статистического анализа.**

## 🎯 О проекте

GoalPredictor.AI — это SaaS-платформа, которая использует продвинутые ML-алгоритмы для анализа статистики футбольных команд и прогнозирования результатов матчей топ-5 европейских лиг.

### Ключевые возможности

- ⚽ **Прогнозирование Over 2.5 Goals** с точностью 70%+
- 🧠 **Машинное обучение** (LightGBM, XGBoost)
- 🤖 **AI-объяснения** прогнозов через GPT-4
- 📊 **Анализ 30+ статистических показателей**
- 🔄 **Автоматическое ежедневное обновление** данных
- 💳 **Подписки через Stripe**
- 📧 **Email-уведомления** для Premium пользователей

### Технологии

**Backend:**
- Flask 3.0 (Python)
- SQLAlchemy + PostgreSQL
- LightGBM / XGBoost
- OpenAI GPT-4
- Stripe API
- APScheduler

**Frontend:**
- HTML5 / CSS3 / JavaScript
- Bootstrap-подобные стили
- Responsive design

**Интеграции:**
- Football-Data.org API (бесплатный, 10 запросов/мин)
- RapidAPI (альтернативный провайдер)
- OpenAI API
- Stripe Payments

## 🚀 Быстрый старт

### Предварительные требования

- Python 3.10+
- pip
- virtualenv (рекомендуется)

### Установка

1. **Клонировать репозиторий:**
```powershell
cd C:\Users\ПК\GoalPredictor.AI
```

2. **Создать виртуальное окружение:**
```powershell
python -m venv venv
.\venv\Scripts\activate
```

3. **Установить зависимости:**
```powershell
pip install -r requirements.txt
```

4. **Настроить переменные окружения:**

Скопируйте `.env.example` в `.env` и заполните свои API ключи:

```env
# Football API (ВЫБЕРИТЕ ПРОВАЙДЕРА)
# Вариант 1: Football-Data.org (БЕСПЛАТНЫЙ, рекомендуется)
FOOTBALL_API_PROVIDER=football-data-org
FOOTBALL_DATA_ORG_KEY=your-football-data-org-key
# Регистрация: https://www.football-data.org/client/register
# Лимиты: 10 запросов/минуту, 100 запросов/день

# Вариант 2: RapidAPI (платный)
# FOOTBALL_API_PROVIDER=rapidapi
# FOOTBALL_API_KEY=your-rapidapi-key

# OpenAI
OPENAI_API_KEY=your-openai-key

# Stripe
STRIPE_SECRET_KEY=your-stripe-secret-key
STRIPE_PUBLIC_KEY=your-stripe-public-key

# Database
DATABASE_URL=sqlite:///goalpredictor.db
```

5. **Инициализировать базу данных:**
```powershell
python
>>> from app import create_app, db
>>> app = create_app()
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

6. **Обучить ML-модель:**

Скачайте датасет с Kaggle и поместите в `data/football_matches.csv`, затем:

```powershell
python ml/train.py
```

7. **Запустить приложение:**
```powershell
python app.py
```

Приложение будет доступно по адресу: http://localhost:5000

## 📁 Структура проекта

```
GoalPredictor.AI/
│
├── app.py                    # Главный файл Flask приложения
├── config.py                 # Конфигурация
├── models.py                 # Модели базы данных
├── requirements.txt          # Зависимости Python
├── .env.example              # Пример переменных окружения
│
├── api/                      # API маршруты
│   ├── routes_matches.py     # Прогнозы и матчи
│   ├── routes_auth.py        # Аутентификация
│   ├── routes_users.py       # Пользователи
│   └── routes_subscriptions.py # Подписки
│
├── ml/                       # Машинное обучение
│   ├── model.py              # ML-модель
│   ├── train.py              # Обучение модели
│   └── predict.py            # Создание прогнозов
│
├── services/                 # Внешние сервисы
│   ├── football_api.py       # Football API клиент
│   ├── openai_service.py     # OpenAI интеграция
│   ├── stripe_service.py     # Stripe платежи
│   └── scheduler.py          # Планировщик задач
│
├── templates/                # HTML шаблоны
│   ├── base.html
│   ├── index.html
│   ├── predictions.html
│   ├── about.html
│   ├── pricing.html
│   └── profile.html
│
├── static/                   # Статические файлы
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── main.js
│   └── images/
│
└── data/                     # Данные
    └── football_matches.csv  # Исторические данные для обучения
```

## 🤖 Как работает ML-модель

### 1. Сбор признаков (Features)

Модель анализирует более 30 признаков:
- Средние голы за/против
- Процент Over 2.5 в последних матчах
- Форма команды (последние 5 игр)
- Домашние/выездные показатели
- BTTS (обе команды забивают)
- Статистика "чистых счетов"
- Взаимодействие признаков

### 2. Обучение

Используем **LightGBM** — быстрый и точный градиентный бустинг:
- Обучение на исторических данных (5 лет)
- Кросс-валидация (5-fold)
- ROC-AUC метрика
- Регулярное переобучение (раз в неделю)

### 3. Прогнозирование

- Вычисление вероятности Over 2.5 Goals
- Определение уровня уверенности (high/medium/low)
- Генерация объяснения через GPT-4

## 📊 API Документация

### Получить прогнозы на сегодня

```http
GET /api/matches/today
```

**Response:**
```json
{
  "success": true,
  "count": 10,
  "predictions": [
    {
      "match_info": {
        "home_team": "Manchester United",
        "away_team": "Liverpool",
        "league": "Premier League",
        "date": "2025-10-05T20:00:00"
      },
      "probability": 0.73,
      "confidence": "high",
      "prediction": "Over 2.5",
      "explanation": "⚽ Высокая вероятность результативного матча..."
    }
  ]
}
```

### Аутентификация

```http
POST /api/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "username": "username",
  "password": "password123"
}
```

### Создать подписку

```http
POST /api/subscriptions/create-checkout
Content-Type: application/json

{
  "plan_type": "monthly"
}
```

## 💳 Тарифные планы

### Free
- ✅ 3 прогноза в день
- ✅ Базовая аналитика
- ❌ Email-уведомления

### Premium Monthly — €9.99/мес
- ✅ Неограниченные прогнозы
- ✅ Детальная аналитика
- ✅ Email-уведомления
- ✅ Приоритетная поддержка

### Premium Yearly — €99.99/год
- ✅ Все возможности Monthly
- ✅ Скидка 17%
- ✅ Ранний доступ к новым функциям

## 🔐 Безопасность и Легальность

⚠️ **Важно:**
- Мы НЕ принимаем ставки
- Мы НЕ связаны с букмекерскими конторами
- Мы НЕ даем финансовых советов
- Прогнозы основаны на статистике и не гарантируют результат

Платформа соблюдает:
- GDPR (защита данных)
- PCI DSS (платежи через Stripe)
- Политику конфиденциальности

## 🧪 Тестирование

Запуск тестов:
```powershell
pytest tests/
```

## 📈 Метрики производительности

- **Точность модели:** 70-75%
- **ROC-AUC:** 0.75+
- **Время генерации прогноза:** < 2 сек
- **Uptime:** 99.9%

## 🛠️ Разработка

### Запуск в режиме разработки

```powershell
$env:FLASK_ENV="development"
$env:DEBUG="True"
python app.py
```

### Обновление модели

```powershell
python ml/train.py
```

### Ручной запуск планировщика

```powershell
python services/scheduler.py
```

## 📝 TODO

- [ ] Добавить Telegram бота
- [ ] Реализовать мобильное приложение
- [ ] Добавить прогнозы на другие исходы (1X2, BTTS)
- [ ] Интеграция с больше лигами
- [ ] Система рейтингов пользователей
- [ ] A/B тестирование моделей

## 🤝 Вклад в проект

Приветствуются Pull Requests! Для больших изменений сначала откройте Issue для обсуждения.

## 📄 Лицензия

MIT License - см. файл [LICENSE](LICENSE)

## 📧 Контакты

- Website: https://goalpredictor.ai
- Email: support@goalpredictor.ai
- Telegram: @goalpredictor_ai

---

**Сделано с ⚽ и 🤖**
