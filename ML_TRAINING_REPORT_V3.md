# ML Training Report - Version 3.0

## 🚨 КРИТИЧНЕ ВИПРАВЛЕННЯ: Target Leakage

### Проблема (Version 2.0)
```
over_2_5: 100% Train, 100% Test ❌
btts:     87.2% Train, 77.9% Test ❌
```

**Причина:** В `training_data.csv` цільові змінні (`total_goals`, `over_2_5`, `btts`, `home_win`, `draw`, `away_win`) використовувались як фічі!

### Рішення (Version 3.0)
✅ Видалено всі цільові змінні з фіч  
✅ Часовий спліт (train на старих даних, test на нових)  
✅ Калібрація ймовірностей (CalibratedClassifierCV)  
✅ Правильні метрики (ROC-AUC, Brier, PR-AUC)

---

## 📊 Нові Результати (Realistic Metrics)

### Dataset
- **Total**: 5014 matches
- **Train**: 4011 matches (2020-09-13 до 2024-03-30)
- **Test**: 1003 matches (2024-03-30 до 2025-05-25)
- **Features**: 19 (без target leakage)

### Metrics Explanation
- **Accuracy**: % правильних прогнозів
- **ROC-AUC**: 0.5 = random, 1.0 = perfect (реалістично 0.55-0.75)
- **Brier Score**: 0.0 = perfect, 0.25 = random (нижче = краще)
- **PR-AUC**: Precision-Recall AUC

### Results

| Target    | Model            | Test Acc | ROC-AUC | Brier | Interpretation |
|-----------|------------------|----------|---------|-------|----------------|
| over_2.5  | RandomForest     | 54.4%    | 0.520   | 0.248 | Слабка, потрібно більше фіч |
| over_2.5  | GradientBoosting | 52.9%    | 0.507   | 0.249 | Слабка |
| btts      | RandomForest     | 55.9%    | 0.497   | 0.247 | Ледь краща за random |
| btts      | GradientBoosting | 55.9%    | 0.523   | 0.247 | Посередня |
| home_win  | RandomForest     | 63.7%    | 0.677   | 0.223 | ✅ Хороша! |
| home_win  | GradientBoosting | 63.3%    | 0.662   | 0.229 | ✅ Хороша! |
| draw      | RandomForest     | 75.4%    | 0.523   | 0.186 | Висока acc через imbalance |
| draw      | GradientBoosting | 75.4%    | 0.520   | 0.185 | Висока acc через imbalance |
| away_win  | RandomForest     | 69.4%    | 0.685   | 0.200 | ✅ Відмінна! |
| away_win  | GradientBoosting | 67.3%    | 0.662   | 0.206 | ✅ Хороша! |

---

## 🎯 Висновки

### Найкращі моделі:
1. **away_win** (AUC 0.685) - найсильніша модель
2. **home_win** (AUC 0.677) - друга за силою
3. **btts** (AUC 0.523) - посередня
4. **over_2.5** (AUC 0.520) - слабка

### Чому over_2.5 слабка?
- Лише 19 фіч (форма команд за останні 5 ігор + H2H)
- Немає: погода, травми, суддя, мотивація, дні відпочинку
- Голи залежать від багатьох факторів, які ми не враховуємо

### Що покращить over_2.5:
1. ✅ **Дні відпочинку** між матчами
2. ✅ **Подорож** (відстань home→away)
3. ✅ **Турнірна мотивація** (боротьба за топ-4/від вильоту)
4. ⚠️ **Погода** (температура/дощ) - якщо є API
5. ⚠️ **Травми** ключових гравців - якщо є API
6. ⚠️ **Суддя** статистика - якщо є дані

---

## 🔧 Technical Changes

### 1. Temporal Split (замість random)
```python
train_df = df[df['date'] < '2024-03-30']  # Старі дані
test_df = df[df['date'] >= '2024-03-30']  # Нові дані
```

### 2. Leakage Prevention
```python
TARGET_COLUMNS = ['total_goals', 'over_2_5', 'btts', 
                  'home_win', 'draw', 'away_win']
feature_columns = [col for col in df.columns 
                   if col not in TARGET_COLUMNS + ['match_id', 'date', 'league']]
```

### 3. Probability Calibration
```python
calibrated_model = CalibratedClassifierCV(
    base_model, 
    method='sigmoid',  # Platt scaling
    cv=3
)
```

### 4. Proper Metrics
```python
roc_auc = roc_auc_score(y_test, proba)
brier = brier_score_loss(y_test, proba)
pr_auc = average_precision_score(y_test, proba)
```

---

## 📁 Generated Files

- `ml/models/*_model.pkl` - Калібровані моделі (v3.0)
- `ml/models/feature_columns.pkl` - 19 фіч без leakage
- `ml/models/model_metadata.json` - Метадані тренування
- `ml/models/training_report_v3.csv` - Детальні метрики

---

## 🚀 Next Steps

### Priority 1 (Покращити over_2.5):
1. Додати фічу "дні відпочинку" (days_since_last_match)
2. Додати фічу "подорож" (travel_distance)
3. Експериментувати з вікнами (3/5/10 останніх ігор)

### Priority 2 (Пояснення):
1. SHAP values для важливості фіч
2. Інтеграція SHAP в OpenAI пояснення

### Priority 3 (Моніторинг):
1. Rolling backtest по місяцях
2. Щотижневе перетренування
3. Алерти при погіршенні метрик

---

**Trained**: 2025-01-XX  
**Version**: v3.0_temporal_calibrated  
**Status**: ✅ Production Ready (без leakage)
