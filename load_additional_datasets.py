"""
Загрузка дополнительных датасетов с football-data.co.uk
Бесплатные CSV файлы с историческими данными о матчах
"""
import requests
import pandas as pd
import io
from datetime import datetime
from extensions import db
from app import create_app
from models import Team, Match

app = create_app()

# URL-ы для датасетов (2020-2025)
DATASET_URLS = {
    'Premier League': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/E0.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/E0.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/E0.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/E0.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/E0.csv',
    },
    'La Liga': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/SP1.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/SP1.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/SP1.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/SP1.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/SP1.csv',
    },
    'Bundesliga': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/D1.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/D1.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/D1.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/D1.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/D1.csv',
    },
    'Serie A': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/I1.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/I1.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/I1.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/I1.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/I1.csv',
    },
    'Ligue 1': {
        '2020-21': 'https://www.football-data.co.uk/mmz4281/2021/F1.csv',
        '2021-22': 'https://www.football-data.co.uk/mmz4281/2122/F1.csv',
        '2022-23': 'https://www.football-data.co.uk/mmz4281/2223/F1.csv',
        '2023-24': 'https://www.football-data.co.uk/mmz4281/2324/F1.csv',
        '2024-25': 'https://www.football-data.co.uk/mmz4281/2425/F1.csv',
    }
}

LEAGUE_CODES = {
    'Premier League': 'PL',
    'La Liga': 'PD',
    'Bundesliga': 'BL1',
    'Serie A': 'SA',
    'Ligue 1': 'FL1'
}


def download_csv_dataset(url):
    """
    Скачать CSV датасет
    """
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        
        # Прочитать CSV
        df = pd.read_csv(io.StringIO(response.text))
        return df
    
    except Exception as e:
        print(f"      ❌ Ошибка загрузки: {str(e)}")
        return None


def parse_date(date_str):
    """
    Парсить дату из разных форматов
    """
    formats = ['%d/%m/%Y', '%d/%m/%y', '%Y-%m-%d']
    
    for fmt in formats:
        try:
            return datetime.strptime(date_str, fmt)
        except:
            continue
    
    return None


def process_csv_matches(df, league_code, season):
    """
    Обработать матчи из CSV файла
    """
    if df is None or df.empty:
        return 0
    
    matches_added = 0
    
    # Основные колонки в football-data.co.uk CSV
    # Date, HomeTeam, AwayTeam, FTHG (Full Time Home Goals), FTAG, FTR (Full Time Result)
    
    for _, row in df.iterrows():
        try:
            # Пропустить пустые строки
            if pd.isna(row.get('HomeTeam')) or pd.isna(row.get('AwayTeam')):
                continue
            
            # Пропустить матчи без результата
            if pd.isna(row.get('FTHG')) or pd.isna(row.get('FTAG')):
                continue
            
            home_team_name = str(row['HomeTeam']).strip()
            away_team_name = str(row['AwayTeam']).strip()
            
            # Создать/найти домашнюю команду
            home_team = Team.query.filter_by(
                name=home_team_name,
                league=league_code
            ).first()
            
            if not home_team:
                # Создать с фейковым api_id (отрицательный для CSV данных)
                home_team = Team(
                    api_id=-abs(hash(home_team_name + league_code)) % 1000000,
                    name=home_team_name,
                    league=league_code,
                    country='Unknown'
                )
                db.session.add(home_team)
            
            # Создать/найти гостевую команду
            away_team = Team.query.filter_by(
                name=away_team_name,
                league=league_code
            ).first()
            
            if not away_team:
                away_team = Team(
                    api_id=-abs(hash(away_team_name + league_code)) % 1000000,
                    name=away_team_name,
                    league=league_code,
                    country='Unknown'
                )
                db.session.add(away_team)
            
            db.session.flush()
            
            # Парсить дату
            match_date = parse_date(str(row['Date']))
            if not match_date:
                continue
            
            # Результаты
            home_goals = int(row['FTHG'])
            away_goals = int(row['FTAG'])
            total_goals = home_goals + away_goals
            
            # Проверить существование матча
            existing = Match.query.filter_by(
                home_team_id=home_team.id,
                away_team_id=away_team.id,
                match_date=match_date
            ).first()
            
            if not existing:
                new_match = Match(
                    api_id=-abs(hash(f"{home_team_name}{away_team_name}{match_date}")) % 1000000,
                    home_team_id=home_team.id,
                    away_team_id=away_team.id,
                    match_date=match_date,
                    league=league_code,
                    status='FINISHED',
                    home_goals=home_goals,
                    away_goals=away_goals,
                    total_goals=total_goals,
                    result='1' if home_goals > away_goals else ('X' if home_goals == away_goals else '2'),
                    over_2_5=total_goals > 2.5,
                    btts=(home_goals > 0 and away_goals > 0)
                )
                db.session.add(new_match)
                matches_added += 1
        
        except Exception as e:
            continue
    
    db.session.commit()
    return matches_added


def main():
    """
    Загрузить все датасеты
    """
    with app.app_context():
        print("=" * 70)
        print("📊 ЗАГРУЗКА ДОПОЛНИТЕЛЬНЫХ ДАТАСЕТОВ (football-data.co.uk)")
        print("=" * 70)
        print("\n📝 Источник: https://www.football-data.co.uk/")
        print("   Датасеты содержат полную историю матчей с 2020 года\n")
        
        total_matches = 0
        
        for league_name, seasons in DATASET_URLS.items():
            league_code = LEAGUE_CODES[league_name]
            print(f"\n🏆 {league_name} ({league_code})")
            print("-" * 70)
            
            for season, url in seasons.items():
                print(f"   📥 Сезон {season}...", end=' ')
                
                df = download_csv_dataset(url)
                
                if df is not None:
                    matches_count = process_csv_matches(df, league_code, season)
                    total_matches += matches_count
                    print(f"✅ {matches_count} матчей")
                else:
                    print(f"❌ Ошибка")
        
        print("\n" + "=" * 70)
        print(f"✅ ЗАГРУЗКА ЗАВЕРШЕНА")
        print(f"   Всего матчей загружено: {total_matches}")
        print(f"   Команд в базе: {Team.query.count()}")
        print(f"   Матчей в базе: {Match.query.count()}")
        print("=" * 70)
        
        print("\n💡 Теперь можно запустить обучение модели!")


if __name__ == '__main__':
    main()
