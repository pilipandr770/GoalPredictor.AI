# 🎾 Tennis Integration Plan

## 📊 Датасети (FREE)

### 1. **Jeff Sackmann Tennis Datasets** ⭐ РЕКОМЕНДУЮ
**GitHub:** https://github.com/JeffSackmann/tennis_atp (ATP - чоловіки)
**GitHub:** https://github.com/JeffSackmann/tennis_wta (WTA - жінки)

**Що є:**
- ✅ Всі ATP матчі з 1968 року (CSV формат)
- ✅ Всі WTA матчі з 1920 року
- ✅ Дані по турнірах: Grand Slams, Masters 1000, ATP 500/250
- ✅ Рейтинги гравців (щотижневі)
- ✅ H2H статистика
- ✅ Статистика матчів (аси, подвійні помилки, winners тощо)

**Файли:**
```
atp_matches_2020.csv
atp_matches_2021.csv
atp_matches_2022.csv
atp_matches_2023.csv
atp_matches_2024.csv
atp_rankings_current.csv
atp_players.csv
```

**Колонки (приклад):**
```csv
tourney_id,tourney_name,surface,draw_size,tourney_level,tourney_date,
match_num,winner_id,winner_name,winner_rank,loser_id,loser_name,loser_rank,
score,w_ace,w_df,w_svpt,w_1stIn,w_1stWon,w_2ndWon,w_SvGms,w_bpSaved,w_bpFaced,
l_ace,l_df,l_svpt,l_1stIn,l_1stWon,l_2ndWon,l_SvGms,l_bpSaved,l_bpFaced
```

**Переваги:**
- Безкоштовно, відкритий доступ
- Оновлюється регулярно
- Високої якості, перевірені дані
- Містить все що потрібно для ML

---

### 2. **Tennis-Data.co.uk** (альтернатива)
**URL:** http://www.tennis-data.co.uk/

**Що є:**
- Історичні матчі з коефіцієнтами букмекерів
- ATP, WTA, Challengers
- Excel/CSV формат

**Мінуси:**
- Менш детальна статистика
- Містить коефіцієнти (треба видаляти для ML)

---

## 🌐 API для розкладу матчів

### 1. **API-TENNIS (RapidAPI)** ⭐ БЕЗКОШТОВНИЙ ТАРИФ
**URL:** https://rapidapi.com/api-sports/api/api-tennis

**Free Plan:**
- ✅ 100 requests/день (достатньо для щоденного оновлення)
- ✅ Поточні матчі, розклад
- ✅ Live scores
- ✅ Статистика гравців
- ✅ H2H

**Endpoints:**
```
GET /fixtures         # Розклад матчів
GET /fixtures/live    # Live матчі
GET /players          # Інфо про гравця
GET /h2h              # Head-to-head
GET /rankings         # Рейтинги ATP/WTA
```

**Приклад запиту:**
```python
import requests

url = "https://api-tennis.p.rapidapi.com/fixtures"
headers = {
    "X-RapidAPI-Key": "YOUR_KEY",
    "X-RapidAPI-Host": "api-tennis.p.rapidapi.com"
}
params = {"date": "2025-10-11"}
response = requests.get(url, headers=headers, params=params)
```

---

### 2. **The Odds API** (якщо маєш ключ)
**URL:** https://the-odds-api.com/

**Free Plan:**
- ✅ 500 requests/місяць
- ✅ Розклад матчів
- ✅ Live odds (можна ігнорувати)

**Переваги:**
- Той самий API що ми могли б використати для футболу
- Мультиспорт

---

### 3. **SofaScore Web Scraping** (без API)
**URL:** https://www.sofascore.com/tennis

**Підхід:**
- Парсинг через requests + BeautifulSoup
- Не потребує API ключа
- Ризик: можуть заблокувати IP

**Мінуси:**
- Не рекомендую для продакшну
- Проти TOS

---

### 4. **Tennis Abstract API** (неофіційний)
**URL:** http://www.tennisabstract.com/

**Що є:**
- Прогнози на матчі
- Рейтинги Elo
- Статистика

**Мінуси:**
- Немає офіційного API
- Потрібен scraping

---

## ⚡ Рекомендована архітектура

### Phase 1: Мінімальна реалізація (1-2 дні)

**1. Завантажити датасет Jeff Sackmann**
```bash
git clone https://github.com/JeffSackmann/tennis_atp
```

**2. Підготувати training data**
- Матчі за 2020-2024 (останні 5 років)
- Фічі: рейтинг гравців, форма, H2H, покриття корту
- Target: winner (0/1)

**3. Натренувати модель**
- Binary classification (player1_win vs player2_win)
- Подібно до home_win/away_win у футболі

**4. API Integration**
- Зареєструватись на RapidAPI (API-TENNIS)
- Створити `services/tennis_api.py`
- Endpoint: `/api/tennis/matches`

**5. UI**
- Додати вкладку "Tennis" 🎾
- Компонент `TennisPredictions.vue` (якщо Vue) або template

---

### Phase 2: Повна реалізація (3-5 днів)

**Моделі (models.py):**
```python
class TennisPlayer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    atp_id = db.Column(db.Integer, unique=True)
    current_rank = db.Column(db.Integer)
    points = db.Column(db.Integer)
    country = db.Column(db.String(3))

class TennisMatch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    api_id = db.Column(db.Integer, unique=True)
    tournament = db.Column(db.String(100))
    surface = db.Column(db.String(20))  # Hard, Clay, Grass
    round = db.Column(db.String(20))    # R32, R16, QF, SF, F
    
    player1_id = db.Column(db.Integer, db.ForeignKey('tennis_players.id'))
    player2_id = db.Column(db.Integer, db.ForeignKey('tennis_players.id'))
    
    match_date = db.Column(db.DateTime)
    completed = db.Column(db.Boolean, default=False)
    winner_id = db.Column(db.Integer)

class TennisPrediction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('tennis_matches.id'))
    
    player1_win_probability = db.Column(db.Float)
    player2_win_probability = db.Column(db.Float)
    
    confidence = db.Column(db.String(20))
    explanation = db.Column(db.Text)
    factors = db.Column(db.JSON)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
```

**ML Features (30+ features):**
```python
TENNIS_FEATURES = [
    # Рейтинги
    'player1_rank', 'player2_rank', 'rank_difference',
    'player1_points', 'player2_points',
    
    # Форма (останні 10 матчів)
    'player1_recent_wins', 'player1_recent_losses',
    'player2_recent_wins', 'player2_recent_losses',
    'player1_form_points', 'player2_form_points',
    
    # H2H
    'h2h_player1_wins', 'h2h_player2_wins', 'h2h_total',
    'h2h_on_surface',  # на цьому покритті
    
    # Покриття корту
    'is_hard', 'is_clay', 'is_grass',
    'player1_hard_winrate', 'player2_hard_winrate',
    'player1_clay_winrate', 'player2_clay_winrate',
    'player1_grass_winrate', 'player2_grass_winrate',
    
    # Турнір
    'is_grand_slam', 'is_masters', 'tournament_importance',
    
    # Усталість
    'player1_days_since_last_match',
    'player2_days_since_last_match',
    'player1_matches_last_7days',
    'player2_matches_last_7days',
    
    # Статистика подачі (якщо є)
    'player1_ace_rate', 'player2_ace_rate',
    'player1_first_serve_won', 'player2_first_serve_won'
]
```

---

## 📋 TODO List для реалізації

### Step 1: Датасет (30 хв)
```bash
# Завантажити Jeff Sackmann ATP дані
git clone https://github.com/JeffSackmann/tennis_atp data/tennis_atp

# Або через Python
import pandas as pd
url = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv"
df = pd.read_csv(url)
```

### Step 2: Підготовка даних (2-3 год)
```python
# tennis/prepare_data.py
- Завантажити матчі 2020-2024
- Об'єднати з рейтингами
- Створити фічі (форма, H2H, покриття)
- Зберегти tennis_training_data.csv
```

### Step 3: Тренування моделі (1 год)
```python
# tennis/train_model.py
- Binary classification (player1 wins = 1, player2 wins = 0)
- RandomForest + Calibration
- Temporal split (як у футболі)
- ROC-AUC метрики
```

### Step 4: API Service (2-3 год)
```python
# services/tennis_api.py
- Інтеграція API-TENNIS (RapidAPI)
- Методи: get_fixtures(), get_player_stats(), get_h2h()
- Кешування (TTL 1 день)
```

### Step 5: Prediction Service (2-3 год)
```python
# tennis/predict.py
- TennisPredictionService
- Завантажити модель
- Витягти фічі з API + історії
- Зробити прогноз
- Інтеграція OpenAI для пояснень
```

### Step 6: API Routes (1-2 год)
```python
# api/routes_tennis.py
@tennis_bp.route('/matches')
def get_tennis_matches():
    # Майбутні матчі
    
@tennis_bp.route('/predictions/<match_id>')
def get_tennis_prediction():
    # Прогноз на матч
```

### Step 7: UI (2-3 год)
```html
<!-- templates/tennis.html -->
- Табличка матчів
- Картки з прогнозами
- Фільтри (турнір, покриття)
```

### Step 8: Database Migration (30 хв)
```python
# migrations/
- Додати TennisPlayer, TennisMatch, TennisPrediction
- flask db migrate -m "Add tennis models"
- flask db upgrade
```

---

## 🎯 Очікувані метрики ML

**Easier than football!** 🎾 > ⚽

Причини:
1. **1 на 1** - простіша динаміка
2. **Рейтинги ATP/WTA** - дуже предиктивні
3. **Менше випадковості** - сильніший майже завжди виграє
4. **H2H важливий** - психологія, стиль гри

**Очікувані результати:**
- ROC-AUC: **0.70-0.80** (краще ніж футбол!)
- Accuracy: **65-75%** (топ-10 vs топ-50 = ~80%)
- Brier: **0.15-0.20**

**Найскладніші прогнози:**
- Топ-10 vs Топ-10 (близькі рейтинги)
- Qualifiers (невідомі гравці)
- Травми (не завжди в даних)

---

## 💰 Бізнес-модель

**Аргументи для користувачів:**
- 🎾 **Tennis** - менш випадковий ніж футбол
- 💎 **Premium-only** - теніс для преміум підписників
- 📊 **Вища точність** - легше прогнозувати
- 🌍 **Цілий рік** - турніри кожного тижня (не тільки сезон)

**Pricing:**
- **Free:** Football (3 прогнози/день)
- **Premium (€9.99/міс):** Football unlimited + Tennis unlimited
- **Pro (€19.99/міс):** Football + Tennis + Basketball + Live updates

---

## 🚀 Швидкий старт (MVP за 1 день)

### Скрипт для тесту:
```python
# test_tennis_prediction.py
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

# 1. Завантажити дані
url = "https://raw.githubusercontent.com/JeffSackmann/tennis_atp/master/atp_matches_2024.csv"
df = pd.read_csv(url)

# 2. Прості фічі
df['rank_diff'] = df['winner_rank'] - df['loser_rank']
df['target'] = 1  # winner = player1

# 3. Split
X = df[['winner_rank', 'loser_rank', 'rank_diff']].fillna(999)
y = df['target']
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

# 4. Train
model = RandomForestClassifier()
model.fit(X_train, y_train)

# 5. Evaluate
print(f"Accuracy: {model.score(X_test, y_test):.2%}")
# Очікується: 65-70% навіть з 3 фічами!
```

---

## ✅ Рекомендації

**Що використати:**
1. ✅ **Датасет:** Jeff Sackmann (GitHub) - безкоштовно, якісно
2. ✅ **API:** API-TENNIS (RapidAPI) - 100 req/день безкоштовно
3. ✅ **ML:** Binary classification (player1_win)
4. ✅ **UI:** Окрема вкладка Tennis 🎾

**Альтернатива БЕЗ API:**
- Завантажувати тільки historical data (Jeff Sackmann)
- Оновлювати датасет раз на тиждень вручну (git pull)
- Показувати прогнози на майбутні турніри
- Мінус: немає live розкладу

**Що НЕ робити:**
- ❌ Scraping SofaScore/Flashscore (проти TOS, нестабільно)
- ❌ Платні API (не потрібно на старті)
- ❌ Ускладнювати з live scores (зайве для MVP)

---

## 📞 Next Steps

1. Я створю структуру папок `tennis/`
2. Завантажу датасет Jeff Sackmann
3. Підготую training data з фічами
4. Натренуємо модель
5. Створимо API integration
6. Додамо UI

Почати зараз? 🚀
