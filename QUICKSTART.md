# 🚀 Быстрый старт GoalPredictor.AI

## Минимальная конфигурация для запуска

### 1. Установка (Первый раз)

```powershell
# Запустить скрипт настройки
.\setup.ps1
```

Этот скрипт:
- ✅ Создаст виртуальное окружение
- ✅ Установит все зависимости
- ✅ Создаст файл .env
- ✅ Инициализирует базу данных
- ✅ Создаст необходимые директории

### 2. Настройка API ключей

Откройте файл `.env` и заполните:

```env
# 🔑 ОБЯЗАТЕЛЬНЫЕ ключи для работы

# Football API - ВЫБЕРИТЕ ОДИН ИЗ ДВУХ ПРОВАЙДЕРОВ:

# Вариант 1 (РЕКОМЕНДУЕТСЯ): Football-Data.org - БЕСПЛАТНЫЙ
# Получите на https://www.football-data.org/client/register
FOOTBALL_API_PROVIDER=football-data-org
FOOTBALL_DATA_ORG_KEY=your-football-data-org-key
# Лимиты: 10 запросов/минуту, 100 запросов/день

# Вариант 2: RapidAPI (платный)
# FOOTBALL_API_PROVIDER=rapidapi
# FOOTBALL_API_KEY=your-rapidapi-key-here

# OpenAI API - Получите на https://platform.openai.com/api-keys
OPENAI_API_KEY=sk-your-openai-key-here

# Stripe - Получите на https://dashboard.stripe.com/test/apikeys
STRIPE_SECRET_KEY=sk_test_your-stripe-key
STRIPE_PUBLIC_KEY=pk_test_your-public-key

# Остальные можно оставить как есть для разработки
```

### 3. Подготовка данных для ML-модели

#### Вариант A: Использовать тестовые данные (быстро)

Создайте файл `data/football_matches.csv` с минимальными данными для теста:

```csv
Date,HomeTeam,AwayTeam,FTHG,FTAG,League
2024-01-01,Man United,Liverpool,2,3,Premier League
2024-01-02,Barcelona,Real Madrid,1,1,La Liga
2024-01-03,Bayern,Dortmund,4,2,Bundesliga
```

#### Вариант B: Скачать полный датасет (рекомендуется)

1. Перейдите на Kaggle: https://www.kaggle.com/datasets
2. Найдите "European Soccer Database" или похожий
3. Скачайте CSV файл с колонками: Date, HomeTeam, AwayTeam, FTHG, FTAG, League
4. Поместите в `data/football_matches.csv`

### 4. Обучение модели

```powershell
# Активировать окружение
.\venv\Scripts\activate

# Обучить модель (займет 2-5 минут)
python ml\train.py
```

### 5. Запуск приложения

```powershell
# Простой способ
.\run.ps1

# Или вручную
.\venv\Scripts\activate
python app.py
```

Приложение будет доступно: **http://localhost:5000**

---

## 🎯 Режимы работы

### Режим разработки (по умолчанию)

- База данных: SQLite (файл `goalpredictor.db`)
- Автоперезагрузка при изменениях
- Подробные логи ошибок
- Debug toolbar включен

### Режим продакшен

См. файл `DEPLOYMENT.md` для полной инструкции по развертыванию.

---

## 📖 Основные команды

### Работа с приложением

```powershell
# Запустить приложение
.\run.ps1

# Остановить: Ctrl+C

# Обновить модель
python ml\train.py

# Запустить планировщик задач
python services\scheduler.py
```

### Работа с базой данных

```powershell
# Создать таблицы заново
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.drop_all(); db.create_all()"

# Открыть Python shell с контекстом приложения
python
>>> from app import create_app, db
>>> from models import User, Match, Prediction
>>> app = create_app()
>>> app.app_context().push()
>>> # Теперь можно работать с моделями
```

### Тестирование API

```powershell
# Получить прогнозы на сегодня
curl http://localhost:5000/api/matches/today

# Регистрация пользователя
curl -X POST http://localhost:5000/api/auth/register -H "Content-Type: application/json" -d '{"email":"test@test.com","username":"test","password":"test123"}'

# Проверка здоровья приложения
curl http://localhost:5000/health
```

---

## 🐛 Решение проблем

### Ошибка: "No module named 'flask'"

```powershell
# Убедитесь что активировано виртуальное окружение
.\venv\Scripts\activate

# Переустановите зависимости
pip install -r requirements.txt
```

### Ошибка: "API Key not found"

Проверьте файл `.env` - все ключи должны быть заполнены.

### Ошибка: "Model not found"

```powershell
# Обучите модель
python ml\train.py
```

### Порт 5000 уже занят

Измените порт в `app.py`:

```python
app.run(host='0.0.0.0', port=5001)  # Используйте другой порт
```

---

## 📚 Дополнительная документация

- **README.md** - Полное описание проекта
- **DEPLOYMENT.md** - Развертывание в продакшен
- **API Documentation** - http://localhost:5000/api/docs (после запуска)

---

## 🎓 Демо-аккаунты

Для тестирования создайте аккаунт через веб-интерфейс или используйте:

```python
# Создать тестового пользователя
from app import create_app, db
from models import User

app = create_app()
with app.app_context():
    user = User(email='demo@goalpredictor.ai', username='demo')
    user.set_password('demo123')
    user.is_premium = True  # Для тестирования Premium функций
    db.session.add(user)
    db.session.commit()
```

---

## 💡 Советы

1. **Для разработки ML-модели**: Начните с небольшого датасета (100-200 матчей) для быстрого тестирования
2. **API лимиты**: Бесплатный план Football API - 100 запросов/день
3. **OpenAI**: Начните с модели `gpt-3.5-turbo` вместо `gpt-4` для экономии
4. **Stripe**: Используйте тестовый режим (ключи с `test`)

---

## 📞 Поддержка

Если возникли проблемы:

1. Проверьте логи: `logs/` директория
2. Изучите README.md
3. Проверьте Issues на GitHub
4. Напишите на: support@goalpredictor.ai

---

**Успешного запуска! ⚽🚀**
