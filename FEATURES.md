# ✅ GoalPredictor.AI - Повний функціонал

## 🏆 Основні функції

### ⚽ Футбол
- ✅ ML-прогнози на матчі (Over/Under 2.5, Home/Away Win)
- ✅ Інтеграція з Football-Data.org API (10 req/min безкоштовно)
- ✅ Розклад матчів на 7 днів вперед
- ✅ Історичні дані та статистика команд
- ✅ Калібровані ймовірності (Platt scaling)
- ✅ Автоматичне оновлення результатів

### 🎾 Теніс (НОВИНКА!)
- ✅ ML-прогнози на ATP/WTA матчі (ROC-AUC 0.705)
- ✅ 25 features: рейтинги, форма, H2H, статистика на покритті
- ✅ Demo-режим (5 тестових матчів)
- ✅ Інтеграція з MatchStat Tennis API (100 req/month безкоштовно)
- ✅ Фільтри по покриттю, турніру, датах
- ✅ Німецька локалізація інтерфейсу

---

## 🎨 Інтерфейс

- ✅ Responsive дизайн (Bootstrap 5)
- ✅ Темна/світла тема
- ✅ Німецька локалізація
- ✅ Інтерактивні модальні вікна з прогнозами
- ✅ Візуалізація факторів прогнозу

---

## 🔐 Система користувачів

- ✅ Реєстрація/авторизація
- ✅ Premium підписка (Stripe інтеграція)
- ✅ Адмін-панель
- ✅ Історія прогнозів користувача

---

## 🤖 Machine Learning

### Футбол:
- **Over/Under 2.5**: ROC-AUC 0.522 (baseline)
- **Away Win**: ROC-AUC 0.685
- Часовий спліт (80/20)
- Калібрація ймовірностей

### Теніс:
- **Player Win**: ROC-AUC 0.705
- 25 features (rank, form, H2H, surface stats)
- RandomForest + CalibratedClassifierCV
- Fallback prediction (на основі рейтингу)

---

## 📊 API Endpoints

### Football
- `GET /api/matches/today` - матчі на сьогодні
- `GET /api/matches/upcoming` - майбутні матчі
- `GET /api/predictions/upcoming` - прогнози

### Tennis
- `GET /api/tennis/matches?days=7` - матчі на N днів
- `GET /api/tennis/predictions/<match_id>` - прогноз на матч
- `GET /api/tennis/health` - health check

---

## 🗄️ База даних

### Models:
- **User** - користувачі
- **Team** - футбольні команди
- **Match** - футбольні матчі
- **Prediction** - футбольні прогнози
- **TennisPlayer** - тенісисти
- **TennisMatch** - тенісні матчі
- **TennisPrediction** - тенісні прогнози
- **Subscription** - підписки
- **UserPrediction** - історія прогнозів користувачів

### Сумісність:
- ✅ SQLite (локальна розробка)
- ✅ PostgreSQL (production на Render)
- ✅ Динамічне визначення schema

---

## 🔄 Background Jobs

### Scheduler (APScheduler):
- ⏰ 06:00 - Оновлення результатів матчів
- ⏰ 07:00 - Оновлення розкладу матчів
- ⏰ 08:00 - Генерація нових прогнозів
- ⏰ 02:00 - Оновлення статистики команд

---

## 🌐 Деплой

### Local Development:
```bash
# SQLite база даних
DATABASE_URL=sqlite:///goalpredictor.db
python app.py
```

### Production (Render.com):
```bash
# PostgreSQL база даних
DATABASE_URL=postgresql://user:pass@host/db
DATABASE_SCHEMA=goalpredictor
gunicorn app:app
```

---

## 📦 Залежності

### Python:
- Flask 3.0.0
- SQLAlchemy 2.0.23
- scikit-learn 1.5.2
- numpy 1.24.3
- pandas 2.1.4
- APScheduler 3.10.4

### Frontend:
- Bootstrap 5.3.0
- Font Awesome 6.4.0
- Vanilla JavaScript (ES6+)

---

## 🎯 Roadmap

### Phase 11 (Поточна):
- ✅ Теніс повністю інтегрований
- ✅ ML-модель працює
- ⏳ Real API ключ (опціонально)
- ⏳ Деплой на production

### Phase 12 (Наступна):
- ⏳ Баскетбол прогнози
- ⏳ Хокей прогнози
- ⏳ Мобільний додаток (React Native)

---

## 📄 Документація

- **[TENNIS_API_SETUP.md](TENNIS_API_SETUP.md)** - Повна інструкція по Tennis API
- **[TENNIS_API_QUICKSTART.md](TENNIS_API_QUICKSTART.md)** - Швидкий старт (5 хвилин)
- **[TENNIS_PROGRESS.md](TENNIS_PROGRESS.md)** - Історія розробки тенісу
- **[TENNIS_INTEGRATION_PLAN.md](TENNIS_INTEGRATION_PLAN.md)** - Технічний план

---

## 🤝 Contributing

Pull requests are welcome! For major changes, please open an issue first.

---

## 📧 Contact

- GitHub: [@pilipandr770](https://github.com/pilipandr770)
- Email: support@goalpredictor.ai

---

## 📝 License

MIT License - see [LICENSE](LICENSE) file for details
