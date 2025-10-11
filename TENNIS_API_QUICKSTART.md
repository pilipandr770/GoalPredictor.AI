# 🎾 Підключення реального Tennis API

## Швидкий старт (5 хвилин)

### 1️⃣ Отримайте безкоштовний API ключ

Перейдіть на: **https://rapidapi.com/jjrm365-kIFr3Nx_odV/api/tennis-api-atp-wta-itf**

- Натисніть **"Subscribe to Test"**
- Виберіть план **"BASIC"** (безкоштовно, 100 запитів/місяць)
- Скопіюйте ваш **X-RapidAPI-Key**

### 2️⃣ Додайте ключ у .env

Відкрийте файл `.env` і знайдіть рядок:

```properties
# RAPIDAPI_TENNIS_KEY=your-rapidapi-tennis-key-here
```

Розкоментуйте і вставте ваш ключ:

```properties
RAPIDAPI_TENNIS_KEY=abc123def456ghi789jkl012mno345pqr678stu901vwx234
```

### 3️⃣ Перезапустіть додаток

```bash
# Зупиніть сервер (Ctrl+C)
python app.py
```

### 4️⃣ Перевірте результат

- Відкрийте: **http://localhost:5000/tennis**
- Синє повідомлення "Demo-Modus aktiv" **зникне**
- Ви побачите **реальні ATP/WTA матчі**

---

## ✅ Що отримаєте

- 🎾 Реальне розклад матчів ATP, WTA, ITF
- 📊 Точні дані про рейтинги гравців
- 🏆 Інформація про турніри
- 📈 Більш точні ML-прогнози

---

## 📖 Детальна інструкція

Повний гайд: **[TENNIS_API_SETUP.md](TENNIS_API_SETUP.md)**

---

## 💡 Залишилися питання?

- Email: tennisapi@matchstat.com
- RapidAPI Support: https://rapidapi.com/dashboard
