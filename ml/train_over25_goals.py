"""
Тренування моделі для прогнозу Over/Under 2.5 голів
Акцент на ІСТОРІЮ ГОЛІВ як найважливішу фічу
"""
import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix, roc_auc_score
from sklearn.preprocessing import StandardScaler
import joblib
import warnings
warnings.filterwarnings("ignore")


def load_data():
    """Завантажити підготовлені дані"""
    print("="*70)
    print("🎯 ТРЕНУВАННЯ МОДЕЛІ: Over/Under 2.5 голів")
    print("="*70)
    
    # Шукаємо файл з даними
    data_paths = [
        'ml/data/training_data_enhanced.csv',
        'ml/data/training_data.csv',
        'ml/data/prepared_data.csv',
        'ml/data/enhanced_data.csv',
        'data/prepared_matches.csv'
    ]
    
    df = None
    for path in data_paths:
        if os.path.exists(path):
            print(f"\n📂 Завантаження даних: {path}")
            df = pd.read_csv(path)
            print(f"✅ Завантажено {len(df)} матчів")
            break
    
    if df is None:
        raise FileNotFoundError("❌ Файл з даними не знайдено! Запустіть ml/download_data.py")
    
    return df


def create_goal_focused_features(df):
    """
    Створити фічі з акцентом на ГОЛИ
    Найважливіші фічі - історія забитих голів
    """
    print("\n🔧 Створення фічів з акцентом на голи...")
    
    feature_columns = []
    
    # ============================================
    # 🎯 НАЙВАЖЛИВІШІ ФІЧІ: Історія голів
    # ============================================
    
    # Голи господарів (найважливіші!)
    goal_features_home = [
        'home_recent_goals_for',      # Забиті голи
        'home_recent_goals_against',  # Пропущені голи
        'home_avg_goals',              # Середні голи за сезон
        'home_scoring_trend'           # Тренд забивання голів
    ]
    
    # Голи гостей (найважливіші!)
    goal_features_away = [
        'away_recent_goals_for',      # Забиті голи
        'away_recent_goals_against',  # Пропущені голи
        'away_avg_goals',              # Середні голи за сезон
        'away_scoring_trend'           # Тренд забивання голів
    ]
    
    # Загальні показники голів
    goal_features_general = [
        # НЕ використовуємо 'total_goals' - це DATA LEAKAGE!
        'expected_total_goals'         # Очікувані голи
    ]
    
    # Об'єднати всі фічі голів
    all_goal_features = goal_features_home + goal_features_away + goal_features_general
    
    # Перевірити які фічі є в даних
    available_features = []
    for feat in all_goal_features:
        if feat in df.columns:
            available_features.append(feat)
    
    print(f"   ✅ Знайдено {len(available_features)} фічів голів:")
    for feat in available_features:
        print(f"      • {feat}")
    
    feature_columns.extend(available_features)
    
    # ============================================
    # 📊 ДОДАТКОВІ ФІЧІ (менший вес)
    # ============================================
    
    # Форма команд (допоміжні фічі)
    form_features = [
        'home_recent_form_points',
        'away_recent_form_points',
        'home_recent_wins',
        'away_recent_wins',
        'home_total_matches',
        'away_total_matches'
    ]
    
    # Head-to-head статистика
    h2h_features = [
        'h2h_home_wins',
        'h2h_draws',
        'h2h_away_wins'
    ]
    
    # Додати якщо є
    for feat in form_features + h2h_features:
        if feat in df.columns and feat not in feature_columns:
            feature_columns.append(feat)
    
    print(f"\n📋 Всього фічів: {len(feature_columns)}")
    
    return feature_columns


def prepare_data(df):
    """Підготувати дані для тренування"""
    print("\n📊 Підготовка даних...")
    
    # Створити цільову змінну: Over 2.5 голів
    if 'over_2_5' not in df.columns:
        if 'total_goals' in df.columns:
            df['over_2_5'] = (df['total_goals'] > 2.5).astype(int)
        elif 'home_score' in df.columns and 'away_score' in df.columns:
            df['over_2_5'] = ((df['home_score'] + df['away_score']) > 2.5).astype(int)
        else:
            raise ValueError("❌ Неможливо створити цільову змінну over_2_5")
    
    # Статистика цільової змінної
    over_25_rate = df['over_2_5'].mean()
    print(f"\n🎯 Статистика Over 2.5:")
    print(f"   Over 2.5: {df['over_2_5'].sum()} матчів ({over_25_rate:.1%})")
    print(f"   Under 2.5: {(1-df['over_2_5']).sum()} матчів ({1-over_25_rate:.1%})")
    
    # Вибрати фічі з акцентом на голи
    feature_columns = create_goal_focused_features(df)
    
    # Видалити рядки з пропущеними значеннями
    df_clean = df[feature_columns + ['over_2_5']].dropna()
    print(f"\n✅ Після очищення: {len(df_clean)} матчів")
    
    X = df_clean[feature_columns]
    y = df_clean['over_2_5']
    
    return X, y, feature_columns


def train_model(X, y):
    """Натренувати модель з акцентом на точність"""
    print("\n🤖 Тренування моделі...")
    print("="*70)
    
    # Розділити дані
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    
    print(f"📊 Train: {len(X_train)}, Test: {len(X_test)}")
    print(f"   Train Over 2.5: {y_train.mean():.1%}")
    print(f"   Test Over 2.5: {y_test.mean():.1%}")
    
    # Стандартизація (допоможе з важливістю фічів)
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Тренувати кілька моделей
    models = {
        'RandomForest': RandomForestClassifier(
            n_estimators=300,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            class_weight='balanced',
            random_state=42,
            n_jobs=-1
        ),
        'GradientBoosting': GradientBoostingClassifier(
            n_estimators=200,
            max_depth=7,
            learning_rate=0.1,
            random_state=42
        )
    }
    
    best_model = None
    best_model_name = None
    best_score = 0
    
    print("\n🎯 Тренування моделей:")
    for name, model in models.items():
        print(f"\n   {name}:")
        
        # Тренування
        if name == 'RandomForest':
            model.fit(X_train_scaled, y_train)
        else:
            model.fit(X_train_scaled, y_train)
        
        # Оцінка
        y_pred_train = model.predict(X_train_scaled)
        y_pred_test = model.predict(X_test_scaled)
        y_proba_test = model.predict_proba(X_test_scaled)[:, 1]
        
        train_acc = accuracy_score(y_train, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)
        test_auc = roc_auc_score(y_test, y_proba_test)
        
        # Cross-validation
        cv_scores = cross_val_score(model, X_train_scaled, y_train, cv=5, scoring='accuracy')
        cv_mean = cv_scores.mean()
        
        print(f"      Train Accuracy: {train_acc:.2%}")
        print(f"      Test Accuracy:  {test_acc:.2%}")
        print(f"      Test AUC:       {test_auc:.3f}")
        print(f"      CV Mean:        {cv_mean:.2%} (+/- {cv_scores.std():.2%})")
        
        if cv_mean > best_score:
            best_score = cv_mean
            best_model = model
            best_model_name = name
    
    print(f"\n✅ Найкраща модель: {best_model_name} (CV: {best_score:.2%})")
    
    # Детальний звіт
    print("\n" + "="*70)
    print(f"📊 ДЕТАЛЬНИЙ ЗВІТ: {best_model_name}")
    print("="*70)
    
    y_pred_final = best_model.predict(X_test_scaled)
    y_proba_final = best_model.predict_proba(X_test_scaled)[:, 1]
    
    print("\n📈 Classification Report:")
    print(classification_report(y_test, y_pred_final, 
                                target_names=['Under 2.5', 'Over 2.5'],
                                zero_division=0))
    
    print("\n📊 Confusion Matrix:")
    cm = confusion_matrix(y_test, y_pred_final)
    print(cm)
    print(f"\n   True Negatives:  {cm[0,0]} (правильно Under 2.5)")
    print(f"   False Positives: {cm[0,1]} (помилково Over 2.5)")
    print(f"   False Negatives: {cm[1,0]} (помилково Under 2.5)")
    print(f"   True Positives:  {cm[1,1]} (правильно Over 2.5)")
    
    # Важливість фічів
    if hasattr(best_model, 'feature_importances_'):
        print("\n🎯 ТОП-10 найважливіших фічів:")
        importances = best_model.feature_importances_
        indices = np.argsort(importances)[::-1][:10]
        
        for i, idx in enumerate(indices, 1):
            print(f"   {i}. {X.columns[idx]}: {importances[idx]:.4f}")
    
    return best_model, scaler, best_model_name


def save_model(model, scaler, feature_columns, model_name):
    """Зберегти модель"""
    print("\n💾 Збереження моделі...")
    
    models_dir = 'ml/models'
    os.makedirs(models_dir, exist_ok=True)
    
    # Зберегти модель
    model_path = os.path.join(models_dir, 'over_2_5_goals_model.pkl')
    joblib.dump(model, model_path)
    print(f"   ✅ Модель: {model_path}")
    
    # Зберегти scaler
    scaler_path = os.path.join(models_dir, 'over_2_5_scaler.pkl')
    joblib.dump(scaler, scaler_path)
    print(f"   ✅ Scaler: {scaler_path}")
    
    # Зберегти список фічів
    features_path = os.path.join(models_dir, 'over_2_5_features.pkl')
    joblib.dump(feature_columns, features_path)
    print(f"   ✅ Features: {features_path}")
    
    # Створити метадані
    metadata = {
        'model_type': model_name,
        'num_features': len(feature_columns),
        'features': list(feature_columns),
        'target': 'over_2_5',
        'version': '1.0'
    }
    
    metadata_path = os.path.join(models_dir, 'over_2_5_metadata.pkl')
    joblib.dump(metadata, metadata_path)
    print(f"   ✅ Metadata: {metadata_path}")
    
    print("\n🎉 Модель успішно збережено!")


def main():
    """Головна функція"""
    try:
        # 1. Завантажити дані
        df = load_data()
        
        # 2. Підготувати дані
        X, y, feature_columns = prepare_data(df)
        
        # 3. Натренувати модель
        model, scaler, model_name = train_model(X, y)
        
        # 4. Зберегти модель
        save_model(model, scaler, feature_columns, model_name)
        
        print("\n" + "="*70)
        print("✅ ТРЕНУВАННЯ ЗАВЕРШЕНО!")
        print("="*70)
        print("\n📝 Використання:")
        print("   1. Модель прогнозує чи буде Over/Under 2.5 голів")
        print("   2. Основна фіча: історія голів команд")
        print("   3. Використовуй services/prediction_service.py для прогнозів")
        
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
