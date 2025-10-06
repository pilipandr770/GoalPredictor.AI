"""
Загрузка РЕАЛЬНЫХ исторических данных из football-data.co.uk (2020-2025)
Этот источник содержит актуальные завершенные матчи с полной статистикой
"""
import requests
import pandas as pd
import io
from datetime import datetime
from extensions import db
from app import create_app
from models import Team, Match
from sqlalchemy.exc import IntegrityError

app = create_app()

# Датасеты по сезонам (2020-2025)
DATASETS = {
    'Premier League (E0)': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/E0.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/E0.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/E0.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/E0.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/E0.csv',
    },
    'La Liga (SP1)': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/SP1.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/SP1.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/SP1.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/SP1.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/SP1.csv',
    },
    'Bundesliga (D1)': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/D1.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/D1.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/D1.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/D1.csv',
    },
    'Serie A (I1)': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/I1.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/I1.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/I1.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/I1.csv',
    },
    'Ligue 1 (F1)': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/F1.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/F1.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/F1.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/F1.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/F1.csv',
    }
}

LEAGUE_MAPPING = {
    'E0': 'PL',   # Premier League
    'SP1': 'PD',  # La Liga
    'D1': 'BL1',  # Bundesliga
    'I1': 'SA',   # Serie A
    'F1': 'FL1'   # Ligue 1
}


def download_csv(url):
    """Загрузить CSV файл"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        df = pd.read_csv(io.StringIO(response.text))
        return df
    except Exception as e:
        print(f"      ❌ Ошибка: {str(e)}")
        return None


def parse_date(date_str):
    """Парсить дату из CSV"""
    formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']
    
    for fmt in formats:
        try:
            return datetime.strptime(str(date_str), fmt)
        except:
            continue
    return None


def import_csv_data(df, league_code, season_name):
    """
    Импортировать данные из CSV в БД
    """
    if df is None or df.empty:
        return 0
    
    matches_added = 0
    teams_cache = {}  # Кэш команд для ускорения
    skipped = 0
    errors = 0
    
    for idx, row in df.iterrows():
        try:
            # Пропустить строки без результата
            if pd.isna(row.get('FTHG')) or pd.isna(row.get('FTAG')):
                continue
            
            home_team_name = str(row['HomeTeam']).strip()
            away_team_name = str(row['AwayTeam']).strip()
            
            # Получить или создать домашнюю команду
            if home_team_name not in teams_cache:
                home_team = Team.query.filter_by(
                    name=home_team_name,
                    league=league_code
                ).first()
                
                if not home_team:
                    # Создать уникальный api_id на основе имени
                    api_id = abs(hash(home_team_name + league_code)) % 1000000
                    home_team = Team(
                        api_id=api_id,
                        name=home_team_name,
                        league=league_code,
                        country='Europe'
                    )
                    db.session.add(home_team)
                    db.session.flush()
                
                teams_cache[home_team_name] = home_team
            else:
                home_team = teams_cache[home_team_name]
            
            # Получить или создать гостевую команду
            if away_team_name not in teams_cache:
                away_team = Team.query.filter_by(
                    name=away_team_name,
                    league=league_code
                ).first()
                
                if not away_team:
                    api_id = abs(hash(away_team_name + league_code)) % 1000000
                    away_team = Team(
                        api_id=api_id,
                        name=away_team_name,
                        league=league_code,
                        country='Europe'
                    )
                    db.session.add(away_team)
                    db.session.flush()
                
                teams_cache[away_team_name] = away_team
            else:
                away_team = teams_cache[away_team_name]
            
            # Парсить дату
            match_date = parse_date(row['Date'])
            if not match_date:
                continue
            
            # Результаты
            home_goals = int(row['FTHG'])
            away_goals = int(row['FTAG'])
            total_goals = home_goals + away_goals
            result = row['FTR']  # H, A, D
            
            # Проверить существование матча (по дате и командам)
            existing = Match.query.filter_by(
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                match_date=match_date
            ).first()
            
            if not existing:
                # Создать уникальный api_id для матча
                match_id = abs(hash(f"{home_team_name}{away_team_name}{match_date.isoformat()}")) % 10000000
                
                new_match = Match(
                    api_id=match_id,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=match_date,
                    league=league_code,
                    status='FINISHED',
                    home_goals=home_goals,
                    away_goals=away_goals,
                    total_goals=total_goals,
                    result='1' if result == 'H' else ('X' if result == 'D' else '2'),
                    over_2_5=(total_goals > 2.5),
                    btts=(home_goals > 0 and away_goals > 0)
                )
                db.session.add(new_match)
                matches_added += 1
            else:
                skipped += 1
        
        except Exception as e:
            errors += 1
            if errors <= 3:  # Показать первые 3 ошибки
                print(f"\n      ⚠️ Ошибка в строке {idx}: {str(e)}")
            continue
    
    try:
        db.session.commit()
        print(f" (добавлено: {matches_added}, пропущено: {skipped}, ошибок: {errors})")
    except IntegrityError as e:
        db.session.rollback()
        print(f" ❌ Ошибка commit: {str(e)}")
    
    return matches_added


def calculate_team_stats():
    """Обновить статистику всех команд"""
    print("\n📊 Обновление статистики команд...")
    
    teams = Team.query.all()
    updated = 0
    
    for team in teams:
        # Все завершенные матчи команды
        home_matches = Match.query.filter_by(
            home_team_id=team.id,
            status='FINISHED'
        ).all()
        
        away_matches = Match.query.filter_by(
            away_team_id=team.id,
            status='FINISHED'
        ).all()
        
        total_matches = len(home_matches) + len(away_matches)
        
        if total_matches == 0:
            continue
        
        goals_scored = sum(m.home_goals for m in home_matches) + sum(m.away_goals for m in away_matches)
        goals_conceded = sum(m.away_goals for m in home_matches) + sum(m.home_goals for m in away_matches)
        over_count = sum(1 for m in home_matches + away_matches if m.over_2_5)
        
        team.total_matches = total_matches
        team.goals_scored = goals_scored
        team.goals_conceded = goals_conceded
        team.avg_goals_per_match = goals_scored / total_matches
        team.over_2_5_percentage = (over_count / total_matches * 100)
        team.last_update = datetime.utcnow()
        
        updated += 1
    
    db.session.commit()
    print(f"   ✅ Обновлено команд: {updated}")


def main():
    with app.app_context():
        print("=" * 80)
        print("⚽ ЗАГРУЗКА РЕАЛЬНЫХ ИСТОРИЧЕСКИХ ДАННЫХ (2020-2025)")
        print("=" * 80)
        print("\n📝 Источник: https://www.football-data.co.uk/")
        print("   Эти данные используются букмекерами и аналитиками")
        print("   Содержат полную историю матчей с результатами\n")
        
        total_matches = 0
        
        for league_name, seasons in DATASETS.items():
            league_code_short = league_name.split('(')[1].rstrip(')')
            league_code = LEAGUE_MAPPING.get(league_code_short, league_code_short)
            
            print(f"\n🏆 {league_name}")
            print("-" * 80)
            
            for season, url in seasons.items():
                print(f"   📥 {season}...", end=' ', flush=True)
                
                df = download_csv(url)
                if df is not None:
                    count = import_csv_data(df, league_code, season)
                    total_matches += count
                    print(f"✅ {count} матчей")
                else:
                    print("❌")
        
        print("\n" + "=" * 80)
        print(f"✅ ЗАГРУЗКА ЗАВЕРШЕНА!")
        print(f"   Новых матчей загружено: {total_matches}")
        print(f"   Всего завершенных матчей: {Match.query.filter_by(status='FINISHED').count()}")
        print(f"   Команд в базе: {Team.query.count()}")
        print("=" * 80)
        
        # Обновить статистику
        calculate_team_stats()
        
        print("\n🎯 Данные готовы для обучения!")
        print("   Запустите: py prepare_training_data.py")


if __name__ == '__main__':
    main()
