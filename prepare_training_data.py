"""
Подготовка данных для обучения ML модели
Извлекает признаки из загруженных матчей и создает training dataset
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from extensions import db
from app import create_app
from models import Team, Match
from sqlalchemy import and_

app = create_app()


def calculate_recent_form(team_id, before_date, num_matches=5):
    """
    Рассчитать форму команды за последние N матчей
    """
    # Получить последние матчи до указанной даты
    matches = Match.query.filter(
        and_(
            Match.status == 'FINISHED',
            Match.match_date < before_date,
            (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
        )
    ).order_by(Match.match_date.desc()).limit(num_matches).all()
    
    if not matches:
        return 0, 0, 0, 0, 0  # Нет данных
    
    wins = 0
    draws = 0
    losses = 0
    goals_scored = 0
    goals_conceded = 0
    
    for match in matches:
        is_home = match.home_team_id == team_id
        
        if is_home:
            goals_scored += match.home_goals
            goals_conceded += match.away_goals
            
            if match.home_goals > match.away_goals:
                wins += 1
            elif match.home_goals == match.away_goals:
                draws += 1
            else:
                losses += 1
        else:
            goals_scored += match.away_goals
            goals_conceded += match.home_goals
            
            if match.away_goals > match.home_goals:
                wins += 1
            elif match.away_goals == match.home_goals:
                draws += 1
            else:
                losses += 1
    
    return wins, draws, losses, goals_scored, goals_conceded


def calculate_head_to_head(home_team_id, away_team_id, before_date, num_matches=5):
    """
    Статистика личных встреч
    """
    h2h_matches = Match.query.filter(
        and_(
            Match.status == 'FINISHED',
            Match.match_date < before_date,
            ((Match.home_team_id == home_team_id) & (Match.away_team_id == away_team_id)) |
            ((Match.home_team_id == away_team_id) & (Match.away_team_id == home_team_id))
        )
    ).order_by(Match.match_date.desc()).limit(num_matches).all()
    
    if not h2h_matches:
        return 0, 0, 0
    
    home_wins = 0
    draws = 0
    away_wins = 0
    
    for match in h2h_matches:
        if match.home_team_id == home_team_id:
            if match.home_goals > match.away_goals:
                home_wins += 1
            elif match.home_goals == match.away_goals:
                draws += 1
            else:
                away_wins += 1
        else:
            if match.away_goals > match.home_goals:
                home_wins += 1
            elif match.away_goals == match.home_goals:
                draws += 1
            else:
                away_wins += 1
    
    return home_wins, draws, away_wins


def extract_features_for_match(match):
    """
    Извлечь признаки для одного матча
    """
    features = {}
    
    # Базовая информация
    features['match_id'] = match.id
    features['date'] = match.match_date
    features['league'] = match.league
    
    # Форма домашней команды (последние 5 матчей)
    home_wins, home_draws, home_losses, home_gf, home_ga = calculate_recent_form(
        match.home_team_id, match.match_date, 5
    )
    
    features['home_recent_wins'] = home_wins
    features['home_recent_draws'] = home_draws
    features['home_recent_losses'] = home_losses
    features['home_recent_goals_for'] = home_gf
    features['home_recent_goals_against'] = home_ga
    features['home_recent_form_points'] = home_wins * 3 + home_draws
    
    # Форма гостевой команды
    away_wins, away_draws, away_losses, away_gf, away_ga = calculate_recent_form(
        match.away_team_id, match.match_date, 5
    )
    
    features['away_recent_wins'] = away_wins
    features['away_recent_draws'] = away_draws
    features['away_recent_losses'] = away_losses
    features['away_recent_goals_for'] = away_gf
    features['away_recent_goals_against'] = away_ga
    features['away_recent_form_points'] = away_wins * 3 + away_draws
    
    # Личные встречи
    h2h_home_wins, h2h_draws, h2h_away_wins = calculate_head_to_head(
        match.home_team_id, match.away_team_id, match.match_date, 5
    )
    
    features['h2h_home_wins'] = h2h_home_wins
    features['h2h_draws'] = h2h_draws
    features['h2h_away_wins'] = h2h_away_wins
    
    # Статистика команд из БД
    home_team = Team.query.get(match.home_team_id)
    away_team = Team.query.get(match.away_team_id)
    
    if home_team:
        features['home_avg_goals'] = home_team.avg_goals_per_match
        features['home_total_matches'] = home_team.total_matches
    else:
        features['home_avg_goals'] = 0
        features['home_total_matches'] = 0
    
    if away_team:
        features['away_avg_goals'] = away_team.avg_goals_per_match
        features['away_total_matches'] = away_team.total_matches
    else:
        features['away_avg_goals'] = 0
        features['away_total_matches'] = 0
    
    # Целевые переменные
    features['total_goals'] = match.total_goals
    features['over_2_5'] = 1 if match.over_2_5 else 0
    features['btts'] = 1 if match.btts else 0
    features['home_win'] = 1 if match.result == '1' else 0
    features['draw'] = 1 if match.result == 'X' else 0
    features['away_win'] = 1 if match.result == '2' else 0
    
    return features


def prepare_training_dataset():
    """
    Подготовить датасет для обучения
    """
    with app.app_context():
        print("=" * 70)
        print("📊 ПОДГОТОВКА ДАННЫХ ДЛЯ ОБУЧЕНИЯ")
        print("=" * 70)
        
        # Получить все завершенные матчи
        matches = Match.query.filter_by(status='FINISHED').order_by(Match.match_date).all()
        
        print(f"\n📈 Всего завершенных матчей: {len(matches)}")
        
        if len(matches) < 100:
            print("\n⚠️ ПРЕДУПРЕЖДЕНИЕ: Мало данных для обучения!")
            print("   Рекомендуется минимум 500 матчей")
            print("   Запустите: py collect_historical_data.py\n")
            return
        
        print("\n🔄 Извлечение признаков...")
        
        dataset = []
        processed = 0
        skipped = 0
        
        for i, match in enumerate(matches):
            if (i + 1) % 100 == 0:
                print(f"   Обработано: {i + 1}/{len(matches)}")
            
            try:
                # Пропустить матчи без достаточной истории (первые 10 матчей сезона)
                if i < 10:
                    skipped += 1
                    continue
                
                features = extract_features_for_match(match)
                dataset.append(features)
                processed += 1
            
            except Exception as e:
                skipped += 1
                continue
        
        print(f"\n✅ Признаки извлечены:")
        print(f"   Обработано: {processed}")
        print(f"   Пропущено: {skipped}")
        
        # Создать DataFrame
        df = pd.DataFrame(dataset)
        
        # Удалить строки с NaN
        df = df.dropna()
        
        print(f"\n📊 Итоговый датасет:")
        print(f"   Строк: {len(df)}")
        print(f"   Признаков: {len(df.columns)}")
        
        # Сохранить в CSV
        output_file = 'ml/data/training_data.csv'
        df.to_csv(output_file, index=False)
        
        print(f"\n💾 Данные сохранены: {output_file}")
        
        # Статистика по целевым переменным
        print(f"\n📈 Распределение целевых переменных:")
        print(f"   Over 2.5: {df['over_2_5'].sum()} ({df['over_2_5'].mean()*100:.1f}%)")
        print(f"   BTTS: {df['btts'].sum()} ({df['btts'].mean()*100:.1f}%)")
        print(f"   Home Win: {df['home_win'].sum()} ({df['home_win'].mean()*100:.1f}%)")
        print(f"   Draw: {df['draw'].sum()} ({df['draw'].mean()*100:.1f}%)")
        print(f"   Away Win: {df['away_win'].sum()} ({df['away_win'].mean()*100:.1f}%)")
        
        print("\n" + "=" * 70)
        print("✅ ПОДГОТОВКА ЗАВЕРШЕНА")
        print("=" * 70)
        print("\n💡 Теперь можно запустить обучение:")
        print("   py ml/train.py")


if __name__ == '__main__':
    prepare_training_dataset()
