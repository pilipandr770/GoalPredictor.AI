"""
Покращення фіч для ML моделей

НОВІ ФІЧІ:
1. days_rest_home - дні відпочинку домашньої команди
2. days_rest_away - дні відпочинку виїзної команди
3. rest_advantage - різниця у відпочинку (може впливати на втому)
4. is_back_to_back_home - чи грає домашня команда два дні поспіль
5. is_back_to_back_away - чи грає виїзна команда два дні поспіль
6. home_scoring_trend - тренд голів за останні 5 ігор (зростає/падає)
7. away_scoring_trend - тренд голів за останні 5 ігор

МАЙБУТНІ ФІЧІ (потребують API):
- travel_distance - відстань між містами команд
- weather_temp - температура на момент матчу
- weather_rain - дощ (так/ні)
- motivation_index - турнірна мотивація (топ-4, вильот, середина)
"""
import pandas as pd
import numpy as np
from pathlib import Path


def add_rest_days_features(df):
    """
    Додати фічі про дні відпочинку між матчами
    
    ВАЖЛИВО: Сортувати по команді та даті!
    """
    print("🔧 Додавання фіч про відпочинок...")
    
    # Копія для роботи
    df = df.copy()
    df['date'] = pd.to_datetime(df['date'])
    
    # Потрібні колонки з оригінальних даних
    if 'home_team_id' not in df.columns or 'away_team_id' not in df.columns:
        print("⚠️  Пропуск: немає home_team_id/away_team_id")
        return df
    
    # Для кожної команди - знайти попередній матч
    # TODO: Реалізувати після додавання team_id в training_data.csv
    
    # Поки що заглушка
    df['days_rest_home'] = 3.0  # Середнє значення
    df['days_rest_away'] = 3.0
    df['rest_advantage'] = 0.0
    df['is_back_to_back_home'] = 0
    df['is_back_to_back_away'] = 0
    
    print(f"  ✓ Додано 5 фіч про відпочинок")
    return df


def add_scoring_trends(df):
    """
    Додати тренди голів (зростання/падіння форми)
    """
    print("🔧 Додавання трендів голів...")
    
    df = df.copy()
    
    # Якщо є історія голів за останні матчі
    if 'home_recent_goals_for' in df.columns:
        # Простий тренд: порівняти перші 2 та останні 3 гри з 5
        # Позитивне значення = форма покращується
        # TODO: Реалізувати ковзаюче вікно для точного тренду
        
        df['home_scoring_trend'] = 0.0  # Заглушка
        df['away_scoring_trend'] = 0.0
        
        print(f"  ✓ Додано 2 фічі трендів")
    else:
        print("  ⚠️  Пропуск: немає recent_goals")
    
    return df


def add_momentum_features(df):
    """
    Додати фічі про імпульс/моментум команди
    """
    print("🔧 Додавання фіч імпульсу...")
    
    df = df.copy()
    
    if 'home_recent_form_points' in df.columns and 'away_recent_form_points' in df.columns:
        # Різниця у формі
        df['form_difference'] = df['home_recent_form_points'] - df['away_recent_form_points']
        
        # Нормалізована форма (0-1)
        df['home_form_normalized'] = df['home_recent_form_points'] / 15.0  # max 5 wins = 15 points
        df['away_form_normalized'] = df['away_recent_form_points'] / 15.0
        
        print(f"  ✓ Додано 3 фічі імпульсу")
    else:
        print("  ⚠️  Пропуск: немає form_points")
    
    return df


def add_h2h_dominance(df):
    """
    Додати фічі про домінування в H2H
    """
    print("🔧 Додавання H2H домінування...")
    
    df = df.copy()
    
    if all(col in df.columns for col in ['h2h_home_wins', 'h2h_draws', 'h2h_away_wins']):
        # Відсоток перемог домашніх у H2H
        h2h_total = df['h2h_home_wins'] + df['h2h_draws'] + df['h2h_away_wins']
        h2h_total = h2h_total.replace(0, 1)  # Уникнути ділення на 0
        
        df['h2h_home_dominance'] = df['h2h_home_wins'] / h2h_total
        df['h2h_away_dominance'] = df['h2h_away_wins'] / h2h_total
        df['h2h_balance'] = df['h2h_home_dominance'] - df['h2h_away_dominance']
        
        print(f"  ✓ Додано 3 фічі H2H")
    else:
        print("  ⚠️  Пропуск: немає h2h даних")
    
    return df


def add_defensive_features(df):
    """
    Додати фічі про захист
    """
    print("🔧 Додавання фіч захисту...")
    
    df = df.copy()
    
    if all(col in df.columns for col in ['home_recent_goals_against', 'away_recent_goals_against']):
        # Голів пропущено в середньому за гру
        home_matches = df['home_total_matches'].replace(0, 1)
        away_matches = df['away_total_matches'].replace(0, 1)
        
        df['home_defensive_rating'] = df['home_recent_goals_against'] / 5.0  # 5 останніх ігор
        df['away_defensive_rating'] = df['away_recent_goals_against'] / 5.0
        
        # Комбінована очікувана кількість голів
        df['expected_goals_combined'] = (
            df['home_avg_goals'] + df['away_defensive_rating'] +
            df['away_avg_goals'] + df['home_defensive_rating']
        ) / 2.0
        
        print(f"  ✓ Додано 3 фічі захисту")
    else:
        print("  ⚠️  Пропуск: немає defensive даних")
    
    return df


def enhance_training_data(input_path='ml/data/training_data.csv', 
                          output_path='ml/data/training_data_enhanced.csv'):
    """
    Головна функція: додати всі нові фічі
    """
    print()
    print("=" * 70)
    print("🚀 ПОКРАЩЕННЯ ТРЕНУВАЛЬНИХ ДАНИХ")
    print("=" * 70)
    print()
    
    # Завантажити
    print(f"📂 Завантаження: {input_path}")
    df = pd.read_csv(input_path)
    print(f"  ✓ Завантажено: {len(df)} записів, {len(df.columns)} колонок")
    print()
    
    # Додати фічі
    original_cols = len(df.columns)
    
    df = add_rest_days_features(df)
    df = add_scoring_trends(df)
    df = add_momentum_features(df)
    df = add_h2h_dominance(df)
    df = add_defensive_features(df)
    
    new_cols = len(df.columns) - original_cols
    
    print()
    print(f"✅ Додано {new_cols} нових фіч!")
    print(f"   Було: {original_cols} → Стало: {len(df.columns)}")
    print()
    
    # Зберегти
    print(f"💾 Збереження: {output_path}")
    df.to_csv(output_path, index=False)
    print(f"  ✓ Збережено")
    print()
    
    # Показати нові колонки
    new_features = [col for col in df.columns if col not in pd.read_csv(input_path).columns]
    print("📋 Нові фічі:")
    for feat in new_features:
        print(f"  • {feat}")
    print()
    
    print("=" * 70)
    print("✅ ГОТОВО")
    print("=" * 70)
    print()
    print("НАСТУПНИЙ КРОК:")
    print("  python ml/train_temporal_split.py")
    print("  (змінити data_path на training_data_enhanced.csv)")
    print()


if __name__ == '__main__':
    enhance_training_data()
