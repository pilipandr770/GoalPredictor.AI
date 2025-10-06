"""
Скрипт для загрузки исторических данных о матчах за 2020-2025 годы
Использует Football-Data.org API для получения завершенных матчей
"""
import time
from datetime import datetime, timedelta
from extensions import db
from app import create_app
from models import Team, Match
from services.football_api import FootballAPIService
from sqlalchemy.exc import IntegrityError

app = create_app()
football_api = FootballAPIService()

# Топ-5 европейских лиг
LEAGUES = {
    'PL': 'Premier League',
    'PD': 'La Liga',
    'BL1': 'Bundesliga',
    'SA': 'Serie A',
    'FL1': 'Ligue 1'
}

# Сезоны для загрузки (2020-2025)
SEASONS = [2020, 2021, 2022, 2023, 2024, 2025]


def load_season_matches(league_code, season_year):
    """
    Загрузить все завершенные матчи из сезона
    """
    print(f"   📥 Сезон {season_year}/{season_year+1}...")
    
    try:
        # Диапазон дат для сезона (август-май)
        date_from = f"{season_year}-08-01"
        date_to = f"{season_year + 1}-05-31"
        
        # Получить завершенные матчи
        endpoint = f'competitions/{league_code}/matches'
        params = {
            'dateFrom': date_from,
            'dateTo': date_to,
            'status': 'FINISHED'
        }
        
        # Прямой запрос к API
        response = football_api.api._make_request(endpoint, params)
        
        if not response or 'matches' not in response:
            print(f"      ⚠️ Нет данных")
            return 0
        
        matches = response['matches']
        matches_added = 0
        
        for match_data in matches:
            try:
                # Пропустить матчи без результата
                if match_data['score']['fullTime']['home'] is None:
                    continue
                
                # Создать/обновить команды
                home_team = Team.query.filter_by(
                    api_id=match_data['homeTeam']['id']
                ).first()
                
                if not home_team:
                    home_team = Team(
                        api_id=match_data['homeTeam']['id'],
                        name=match_data['homeTeam']['name'],
                        league=league_code,
                        country='Unknown'
                    )
                    db.session.add(home_team)
                
                away_team = Team.query.filter_by(
                    api_id=match_data['awayTeam']['id']
                ).first()
                
                if not away_team:
                    away_team = Team(
                        api_id=match_data['awayTeam']['id'],
                        name=match_data['awayTeam']['name'],
                        league=league_code,
                        country='Unknown'
                    )
                    db.session.add(away_team)
                
                db.session.flush()  # Получить ID команд
                
                # Создать матч если его еще нет
                existing_match = Match.query.filter_by(
                    api_id=match_data['id']
                ).first()
                
                if not existing_match:
                    home_goals = match_data['score']['fullTime']['home']
                    away_goals = match_data['score']['fullTime']['away']
                    total_goals = home_goals + away_goals
                    
                    new_match = Match(
                        api_id=match_data['id'],
                        home_team_id=home_team.id,
                        away_team_id=away_team.id,
                        match_date=datetime.fromisoformat(
                            match_data['utcDate'].replace('Z', '+00:00')
                        ),
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
                print(f"      ⚠️ Ошибка обработки матча: {str(e)}")
                continue
        
        db.session.commit()
        return matches_added
    
    except Exception as e:
        print(f"      ❌ Ошибка: {str(e)}")
        db.session.rollback()
        return 0


def calculate_team_statistics():
    """
    Рассчитать статистику для всех команд на основе загруженных матчей
    """
    print("\n📊 Расчет статистики команд...")
    
    teams = Team.query.all()
    
    for team in teams:
        # Получить все завершенные матчи команды
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
        
        # Подсчет статистики
        goals_scored = 0
        goals_conceded = 0
        over_2_5_count = 0
        
        for match in home_matches:
            goals_scored += match.home_goals
            goals_conceded += match.away_goals
            if match.over_2_5:
                over_2_5_count += 1
        
        for match in away_matches:
            goals_scored += match.away_goals
            goals_conceded += match.home_goals
            if match.over_2_5:
                over_2_5_count += 1
        
        # Обновить команду
        team.total_matches = total_matches
        team.goals_scored = goals_scored
        team.goals_conceded = goals_conceded
        team.avg_goals_per_match = goals_scored / total_matches if total_matches > 0 else 0
        team.over_2_5_percentage = (over_2_5_count / total_matches * 100) if total_matches > 0 else 0
        
        # Форма последних 5 матчей
        recent_matches = (home_matches + away_matches)[-5:]
        form = ''
        for match in recent_matches:
            if match.home_team_id == team.id:
                if match.home_goals > match.away_goals:
                    form += 'W'
                elif match.home_goals == match.away_goals:
                    form += 'D'
                else:
                    form += 'L'
            else:
                if match.away_goals > match.home_goals:
                    form += 'W'
                elif match.away_goals == match.home_goals:
                    form += 'D'
                else:
                    form += 'L'
        
        team.last_5_form = form[-5:]  # Последние 5
        team.last_update = datetime.utcnow()
    
    db.session.commit()
    print(f"   ✅ Статистика обновлена для {len(teams)} команд")


def main():
    """
    Основная функция
    """
    with app.app_context():
        print("=" * 70)
        print("📚 ЗАГРУЗКА ИСТОРИЧЕСКИХ ДАННЫХ (2020-2025)")
        print("=" * 70)
        print(f"\n⏰ Начало: {datetime.now().strftime('%H:%M:%S')}")
        print("\n⚠️ ВАЖНО: Бесплатный API ограничен 10 запросами/минуту")
        print("   Загрузка займет ~15-20 минут (с паузами)\n")
        
        total_matches_loaded = 0
        
        for league_code, league_name in LEAGUES.items():
            print(f"\n🏆 {league_name} ({league_code})")
            print("-" * 70)
            
            for season_year in SEASONS:
                matches_count = load_season_matches(league_code, season_year)
                total_matches_loaded += matches_count
                
                if matches_count > 0:
                    print(f"      ✅ Загружено: {matches_count} матчей")
                
                # Пауза между запросами (API лимит: 10/мин)
                time.sleep(7)  # 7 секунд между запросами
        
        print("\n" + "=" * 70)
        print(f"✅ ЗАГРУЗКА ЗАВЕРШЕНА")
        print(f"   Всего матчей загружено: {total_matches_loaded}")
        print(f"   Команд в базе: {Team.query.count()}")
        print(f"   Матчей в базе: {Match.query.count()}")
        print("=" * 70)
        
        # Рассчитать статистику
        calculate_team_statistics()
        
        print(f"\n⏰ Окончание: {datetime.now().strftime('%H:%M:%S')}")
        print("\n🎯 Данные готовы для обучения модели!")


if __name__ == '__main__':
    main()
