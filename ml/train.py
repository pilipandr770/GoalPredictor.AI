"""
Обучение ML-модели на исторических данных
"""
import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Добавить корневую директорию в путь
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.model import GoalPredictorModel
from services.football_api import FootballAPIService


def load_kaggle_dataset(filepath):
    """
    Загрузить и обработать датасет с Kaggle
    
    Ожидаемые колонки:
    - Date, HomeTeam, AwayTeam, FTHG, FTAG, League
    """
    print(f"📁 Загружаю датасет: {filepath}")
    
    df = pd.read_csv(filepath)
    
    # Конвертировать дату
    df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
    
    # Вычислить общее количество голов
    if 'FTHG' in df.columns and 'FTAG' in df.columns:
        df['TotalGoals'] = df['FTHG'] + df['FTAG']
        df['Over2_5'] = (df['TotalGoals'] > 2.5).astype(int)
        df['BTTS'] = ((df['FTHG'] > 0) & (df['FTAG'] > 0)).astype(int)
    
    print(f"✅ Загружено {len(df)} матчей")
    print(f"   Период: {df['Date'].min()} - {df['Date'].max()}")
    print(f"   Over 2.5: {df['Over2_5'].mean():.1%}")
    
    return df


def calculate_team_statistics(df, team_name, is_home=None, last_n_matches=10):
    """
    Рассчитать статистику команды на основе последних матчей
    
    Args:
        df: DataFrame с матчами
        team_name: Название команды
        is_home: True для домашних, False для выездных, None для всех
        last_n_matches: Количество последних матчей для анализа
    """
    # Фильтр матчей команды
    if is_home is True:
        team_matches = df[df['HomeTeam'] == team_name].copy()
        goals_scored_col = 'FTHG'
        goals_conceded_col = 'FTAG'
    elif is_home is False:
        team_matches = df[df['AwayTeam'] == team_name].copy()
        goals_scored_col = 'FTAG'
        goals_conceded_col = 'FTHG'
    else:
        home_matches = df[df['HomeTeam'] == team_name].copy()
        away_matches = df[df['AwayTeam'] == team_name].copy()
        
        home_matches['GoalsScored'] = home_matches['FTHG']
        home_matches['GoalsConceded'] = home_matches['FTAG']
        away_matches['GoalsScored'] = away_matches['FTAG']
        away_matches['GoalsConceded'] = away_matches['FTHG']
        
        team_matches = pd.concat([home_matches, away_matches])
        goals_scored_col = 'GoalsScored'
        goals_conceded_col = 'GoalsConceded'
    
    # Сортировка по дате
    team_matches = team_matches.sort_values('Date', ascending=False)
    
    # Взять последние N матчей
    recent_matches = team_matches.head(last_n_matches)
    
    if len(recent_matches) == 0:
        return None
    
    # Расчет статистики
    stats = {
        'total_matches': len(recent_matches),
        'avg_goals_scored': recent_matches[goals_scored_col].mean(),
        'avg_goals_conceded': recent_matches[goals_conceded_col].mean(),
        'total_goals_avg': recent_matches['TotalGoals'].mean(),
        'over_2_5_percentage': recent_matches['Over2_5'].mean(),
        'btts_percentage': recent_matches['BTTS'].mean(),
    }
    
    # Форма команды (последние 5 матчей)
    last_5 = recent_matches.head(5)
    form = []
    
    for _, match in last_5.iterrows():
        if is_home is True:
            if match['FTHG'] > match['FTAG']:
                form.append('W')
            elif match['FTHG'] < match['FTAG']:
                form.append('L')
            else:
                form.append('D')
        elif is_home is False:
            if match['FTAG'] > match['FTHG']:
                form.append('W')
            elif match['FTAG'] < match['FTHG']:
                form.append('L')
            else:
                form.append('D')
        else:
            # Общая форма
            if 'GoalsScored' in match:
                if match['GoalsScored'] > match['GoalsConceded']:
                    form.append('W')
                elif match['GoalsScored'] < match['GoalsConceded']:
                    form.append('L')
                else:
                    form.append('D')
    
    stats['last_5_form'] = ''.join(form)
    stats['wins'] = form.count('W')
    stats['draws'] = form.count('D')
    stats['losses'] = form.count('L')
    
    # Чистые счета
    clean_sheets = (recent_matches[goals_conceded_col] == 0).sum()
    stats['clean_sheets_percentage'] = clean_sheets / len(recent_matches)
    
    return stats


def prepare_training_data(df, min_matches=5):
    """
    Подготовить данные для обучения модели
    """
    print("🔄 Подготовка данных для обучения...")
    
    model = GoalPredictorModel()
    training_samples = []
    
    # Сортировка по дате
    df = df.sort_values('Date').reset_index(drop=True)
    
    # Для каждого матча создать признаки на основе предыдущих матчей
    for idx in range(len(df)):
        match = df.iloc[idx]
        
        # Получить историю до этого матча
        history = df.iloc[:idx]
        
        if len(history) < min_matches * 2:
            continue
        
        # Статистика команд
        home_stats = calculate_team_statistics(history, match['HomeTeam'], is_home=True)
        away_stats = calculate_team_statistics(history, match['AwayTeam'], is_home=False)
        
        if home_stats is None or away_stats is None:
            continue
        
        if home_stats['total_matches'] < min_matches or away_stats['total_matches'] < min_matches:
            continue
        
        # Создать признаки
        match_info = {
            'date': match['Date'],
            'league': match.get('League', 'Unknown')
        }
        
        features = model.create_features(home_stats, away_stats, match_info)
        features['over_2_5'] = match['Over2_5']
        features['btts'] = match['BTTS']
        
        training_samples.append(features)
        
        if len(training_samples) % 500 == 0:
            print(f"   Обработано {len(training_samples)} матчей...")
    
    training_df = pd.DataFrame(training_samples)
    
    print(f"✅ Подготовлено {len(training_df)} образцов для обучения")
    print(f"   Over 2.5: {training_df['over_2_5'].mean():.1%}")
    print(f"   BTTS: {training_df['btts'].mean():.1%}")
    
    return training_df


def train_model_from_kaggle(dataset_path):
    """
    Главная функция для обучения модели на датасете Kaggle
    """
    print("="*50)
    print("🚀 Обучение модели GoalPredictor.AI")
    print("="*50)
    
    # Загрузить датасет
    df = load_kaggle_dataset(dataset_path)
    
    # Фильтр топ-5 лиг
    top_leagues = ['Premier League', 'La Liga', 'Bundesliga', 'Serie A', 'Ligue 1']
    if 'League' in df.columns:
        df = df[df['League'].isin(top_leagues)]
        print(f"\n📊 Фильтр топ-5 лиг: {len(df)} матчей")
    
    # Фильтр последних 5 лет
    cutoff_date = datetime.now() - timedelta(days=365*5)
    df = df[df['Date'] >= cutoff_date]
    print(f"📅 Последние 5 лет: {len(df)} матчей")
    
    # Подготовить данные
    training_data = prepare_training_data(df)
    
    # Обучить модель
    model = GoalPredictorModel()
    results = model.train(training_data, target_column='over_2_5')
    
    # Сохранить модель
    model.save_model()
    
    print("\n" + "="*50)
    print("✅ Обучение завершено успешно!")
    print("="*50)
    
    return model, results


if __name__ == '__main__':
    # Путь к датасету Kaggle
    dataset_path = os.path.join('data', 'football_matches.csv')
    
    if not os.path.exists(dataset_path):
        print(f"❌ Датасет не найден: {dataset_path}")
        print("\n📥 Скачайте датасет с Kaggle:")
        print("   https://www.kaggle.com/datasets/secareanualin/football-events")
        print("\n   Или используйте любой другой датасет с колонками:")
        print("   Date, HomeTeam, AwayTeam, FTHG, FTAG, League")
        sys.exit(1)
    
    train_model_from_kaggle(dataset_path)
