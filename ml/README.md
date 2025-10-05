# 🤖 ML Модуль GoalPredictor.AI

Модуль машинного обучения для прогнозирования футбольных матчей с фокусом на **Over 2.5 голов**.

## 📊 Результаты моделей

### Эволюция точности:

| Версия | Алгоритм | Данные | Признаки | Accuracy | AUC | Улучшение |
|--------|----------|--------|----------|----------|-----|-----------|
| v1.0 | LightGBM | 975 | 29 | 52.31% | 52.56% | - |
| **v2.0** | **Ансамбль (4 модели)** | **2140** | **58** | **68.69%** | **81.14%** | **+31.3%** 🚀 |

### 🏆 Лучшие модели в ансамбле v2.0:

1. **Random Forest: 71.50%** (AUC 80.30%)
2. **CatBoost: 70.09%** (AUC 81.47%)
3. **XGBoost: 69.63%** (AUC 80.60%)
4. **LightGBM: 69.39%** (AUC 80.06%)

## 📁 Структура модуля

```
ml/
├── model.py                    # Базовая модель LightGBM (v1.0)
├── train.py                    # Обучение базовой модели
├── download_data.py            # Загрузка датасета с Kaggle (2024-2025)
├── download_enhanced_data.py   # Загрузка расширенных датасетов
├── advanced_features.py        # Генерация 58 продвинутых признаков
├── train_ensemble.py           # Обучение ансамбля из 4 моделей
├── compare_models.py           # Сравнение всех моделей
├── test_predictions.py         # Тестирование прогнозов
└── models/                     # Сохраненные модели
    ├── goal_predictor_model_*.pkl      # Базовая модель v1.0
    └── ensemble_model_*.pkl            # Ансамбль v2.0
```

## 🚀 Быстрый старт

### 1. Загрузка данных

```bash
# Базовый датасет (Kaggle 2024-2025, топ-5 лиг)
python ml/download_data.py

# Расширенный датасет (Premier League 2002-2022, детальная статистика)
python ml/download_enhanced_data.py
```

### 2. Обучение моделей

```bash
# Базовая модель v1.0 (LightGBM)
python ml/train.py

# Генерация продвинутых признаков
python ml/advanced_features.py

# Обучение ансамбля v2.0 (4 модели)
python ml/train_ensemble.py
```

### 3. Сравнение и тестирование

```bash
# Сравнить все модели
python ml/compare_models.py

# Протестировать прогнозы
python ml/test_predictions.py
```

## 🎯 Признаки моделей

### Базовая модель v1.0 (29 признаков):

- Средние голы (забитые/пропущенные)
- Процент Over 2.5 и BTTS
- Форма команд (последние 5 матчей)
- Домашние/выездные показатели
- Защита (clean sheets)
- Лига и день недели

### Ансамбль v2.0 (58 признаков):

**Rolling averages (окна: 3, 5, 10 матчей):**
- Голы забитые/пропущенные
- Удары и удары в створ
- Корнеры
- Фолы
- Желтые карточки

**Head-to-head:**
- Количество встреч
- Средние голы в личных встречах
- Процент Over 2.5 в личных встречах

**Временные признаки:**
- День недели
- Месяц
- Выходной/будний день
- Праздничный сезон

**Форма команды (из датасета):**
- Form Points (очки за последние матчи)
- Win/Loss Streaks (серии побед/поражений)
- Goal Difference (разница забитых/пропущенных)

**Расчетные признаки:**
- Ожидаемое количество голов
- Атакующая сила
- Агрессивность (фолы + карточки)

## 📈 Датасеты

### 1. Базовый (Kaggle 2024-2025)

- **Источник:** `tarekmasryo/football-matches-20242025-top-5-leagues`
- **Матчи:** 1941
- **Лиги:** Premier League, La Liga, Bundesliga, Serie A, Ligue 1
- **Период:** 2024-2025 сезон
- **Колонки:** 23

### 2. Расширенный (Premier League)

- **Источник:** `saife245/english-premier-league`
- **Матчи:** 22,883
- **Период:** 2000-2022
- **Колонки:** 196 (детальная статистика)
- **Дополнительно:** Удары, корнеры, карточки, фолы, коэффициенты букмекеров

### 3. European Football Database

- **Источник:** `hugomathien/soccer`
- **Формат:** SQLite (32.7 MB)
- **Содержит:** Детальную статистику европейских лиг

## 🎲 Использование моделей

### Базовая модель v1.0

```python
from ml.model import GoalPredictorModel

model = GoalPredictorModel()
model.load_model()  # Загрузить последнюю модель

# Статистика команд
home_stats = {
    'avg_goals_scored': 1.8,
    'avg_goals_conceded': 1.2,
    'over_2_5_percentage': 0.6,
    'btts_percentage': 0.55,
    'last_5_form': 'WWLDW',
    # ... другие признаки
}

away_stats = {
    # ... аналогично
}

match_info = {
    'date': datetime.now(),
    'league': 'Premier League'
}

# Прогноз
prediction = model.predict(home_stats, away_stats, match_info)
print(f"Over 2.5: {prediction['probability']:.1%}")
print(f"Рекомендация: {prediction['recommendation']}")
```

### Ансамбль v2.0

```python
from ml.train_ensemble import EnsembleGoalPredictor

ensemble = EnsembleGoalPredictor()
ensemble.load_ensemble('ml/models/ensemble_model_20251005_223748.pkl')

# Признаки (58 параметров)
features = {
    'home_goals_scored_last_3': 1.67,
    'home_goals_conceded_last_3': 1.0,
    'away_goals_scored_last_5': 1.4,
    # ... все 58 признаков
}

# Прогноз
prediction = ensemble.predict(features)
print(f"Ансамбль: {prediction['ensemble_proba']:.1%}")
print(f"Прогноз: {prediction['prediction']}")
print(f"Уверенность: {prediction['confidence']}")

# Прогнозы отдельных моделей
for model_name, proba in prediction['individual_predictions'].items():
    print(f"  {model_name}: {proba:.1%}")
```

## 💡 Рекомендации по использованию

### Уровни уверенности:

- **> 75%:** Высокая уверенность (strong bet) 🔥
- **60-75%:** Средняя уверенность (moderate bet) ✅
- **50-60%:** Низкая уверенность (risky bet) ⚠️
- **< 50%:** Ставка против Over 2.5 ❌

### Стратегия ставок:

1. **Консервативная:** Только прогнозы > 75% (высокий ROI)
2. **Умеренная:** Прогнозы > 65% (баланс риска)
3. **Агрессивная:** Прогнозы > 55% (больше ставок)

## 🔬 Техническиеdetали

### Алгоритмы ансамбля:

1. **LightGBM:**
   - n_estimators=300, learning_rate=0.05
   - max_depth=8, num_leaves=31
   - Вес в ансамбле: 24.83%

2. **XGBoost:**
   - n_estimators=300, learning_rate=0.05
   - max_depth=7, subsample=0.8
   - Вес в ансамбле: 25.00%

3. **CatBoost:**
   - iterations=300, learning_rate=0.05
   - depth=7, l2_leaf_reg=3
   - Вес в ансамбле: 25.27%

4. **Random Forest:**
   - n_estimators=200, max_depth=15
   - min_samples_split=10
   - Вес в ансамбле: 24.91%

### Weighted Voting:

Финальный прогноз = Σ (proba_i × weight_i)

Веса рассчитываются на основе AUC каждой модели:
```
weight_i = AUC_i / Σ(AUC_all)
```

## 📊 Метрики производительности

### Тестовая выборка (428 матчей):

```
              precision    recall  f1-score   support

   Under 2.5       0.69      0.67      0.68       212
    Over 2.5       0.68      0.71      0.70       216

    accuracy                           0.69       428
   macro avg       0.69      0.69      0.69       428
weighted avg       0.69      0.69      0.69       428
```

### Cross-validation (5-fold):

- Средняя точность: 68.5% (±2.1%)
- ROC-AUC: 81.1% (±1.8%)

## 🚧 Будущие улучшения

- [ ] Добавить данные о травмах игроков
- [ ] Интегрировать погодные условия
- [ ] Добавить мотивационный фактор (турнирная таблица)
- [ ] Стэкинг моделей (meta-learning)
- [ ] Real-time обновление статистики
- [ ] A/B тестирование стратегий ставок

## 📝 Логи обучения

Все результаты обучения сохраняются в:
- `ml/models/` - сохраненные модели
- Консольный вывод с метриками
- Classification reports

## 🤝 Вклад

При добавлении новых признаков или моделей:
1. Обновите `advanced_features.py`
2. Добавьте модель в `train_ensemble.py`
3. Обновите этот README
4. Запустите `compare_models.py`

## 📄 Лицензия

MIT License - GoalPredictor.AI
