"""
Скрипт для ручного обновления расписания матчей
"""
from extensions import db
from app import create_app
from services.football_api import FootballAPIService
from models import Team, Match
from datetime import datetime, timedelta

app = create_app()
football_api = FootballAPIService()

with app.app_context():
    print("=" * 60)
    print("ЗАГРУЗКА ДАННЫХ ИЗ FOOTBALL-DATA.ORG API")
    print("=" * 60)
    
    # Лиги для загрузки
    leagues = {
        'PL': 'Premier League',
        'PD': 'La Liga',
        'BL1': 'Bundesliga',
        'SA': 'Serie A',
        'FL1': 'Ligue 1'
    }
    
    total_matches = 0
    
    for league_code, league_name in leagues.items():
        print(f"\n📥 Загрузка: {league_name} ({league_code})...")
        
        try:
            # Получить матчи на ближайшие 14 дней
            matches_data = football_api.get_upcoming_fixtures(
                league_code,
                days=14
            )
            
            if not matches_data:
                print(f"   ⚠️ Нет данных для {league_name}")
                continue
            
            matches_added = 0
            
            for match in matches_data:
                # Создать/обновить домашнюю команду
                home_team = Team.query.filter_by(
                    api_id=match['home_team_id']
                ).first()
                
                if not home_team:
                    home_team = Team(
                        api_id=match['home_team_id'],
                        name=match['home_team_name'],
                        league=league_code,
                        country='Unknown',
                        logo_url=match.get('home_team_logo', '')
                    )
                    db.session.add(home_team)
                
                # Создать/обновить гостевую команду
                away_team = Team.query.filter_by(
                    api_id=match['away_team_id']
                ).first()
                
                if not away_team:
                    away_team = Team(
                        api_id=match['away_team_id'],
                        name=match['away_team_name'],
                        league=league_code,
                        country='Unknown',
                        logo_url=match.get('away_team_logo', '')
                    )
                    db.session.add(away_team)
                
                db.session.flush()  # Получить ID команд
                
                # Создать/обновить матч
                existing_match = Match.query.filter_by(
                    api_id=match['id']
                ).first()
                
                if not existing_match:
                    new_match = Match(
                        api_id=match['id'],
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        match_date=datetime.fromisoformat(match['date'].replace('Z', '+00:00')),
                        league=league_code,
                        status=match.get('status', 'SCHEDULED')
                    )
                    db.session.add(new_match)
                    matches_added += 1
            
            db.session.commit()
            print(f"   ✅ Добавлено матчей: {matches_added}")
            total_matches += matches_added
            
        except Exception as e:
            print(f"   ❌ Ошибка: {str(e)}")
            db.session.rollback()
    
    print(f"\n{'=' * 60}")
    print(f"✅ ИТОГО ЗАГРУЖЕНО МАТЧЕЙ: {total_matches}")
    print(f"📊 Команд в базе: {Team.query.count()}")
    print(f"📊 Матчей в базе: {Match.query.count()}")
    print(f"{'=' * 60}")
