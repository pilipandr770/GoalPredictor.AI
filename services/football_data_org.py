"""
Адаптер для Football-Data.org API
Бесплатный API с ограничениями: 10 запросов/минуту, 100 в день для free tier
"""
import requests
from datetime import datetime, timedelta
from config import Config


class FootballDataOrgAPI:
    """
    Клиент для Football-Data.org API
    """
    
    def __init__(self):
        self.api_key = Config.FOOTBALL_DATA_ORG_KEY
        self.base_url = 'https://api.football-data.org/v4'
        
        self.headers = {
            'X-Auth-Token': self.api_key
        }
        
        self.leagues = Config.LEAGUES
        
        # Маппинг кодов лиг
        self.league_codes = {
            'Premier League': 'PL',
            'La Liga': 'PD',
            'Bundesliga': 'BL1',
            'Serie A': 'SA',
            'Ligue 1': 'FL1'
        }
    
    def _make_request(self, endpoint, params=None):
        """
        Базовый метод для выполнения запросов к API
        """
        url = f"{self.base_url}/{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()
            
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"❌ Ошибка запроса к Football-Data.org API: {e}")
            return None
    
    def get_todays_fixtures(self, league=None, date=None):
        """
        Получить расписание матчей на сегодня (или указанную дату)
        """
        if date is None:
            date = datetime.now().strftime('%Y-%m-%d')
        
        all_fixtures = []
        
        if league:
            # Конкретная лига
            league_code = self.league_codes.get(league, league)
            fixtures = self._make_request(f'competitions/{league_code}/matches', {
                'dateFrom': date,
                'dateTo': date
            })
            
            if fixtures and 'matches' in fixtures:
                all_fixtures = fixtures['matches']
        else:
            # Все топ-5 лиги
            for league_name, league_code in self.league_codes.items():
                fixtures = self._make_request(f'competitions/{league_code}/matches', {
                    'dateFrom': date,
                    'dateTo': date
                })
                
                if fixtures and 'matches' in fixtures:
                    for match in fixtures['matches']:
                        match['league_name'] = league_name
                    all_fixtures.extend(fixtures['matches'])
        
        return self._format_fixtures(all_fixtures)
    
    def get_upcoming_fixtures(self, league_code, days=7):
        """
        Получить предстоящие матчи на N дней вперед
        """
        date_from = datetime.now().strftime('%Y-%m-%d')
        date_to = (datetime.now() + timedelta(days=days)).strftime('%Y-%m-%d')
        
        fixtures = self._make_request(f'competitions/{league_code}/matches', {
            'dateFrom': date_from,
            'dateTo': date_to
        })
        
        if fixtures and 'matches' in fixtures:
            return self._format_fixtures(fixtures['matches'])
        
        return []
    
    def _format_fixtures(self, fixtures):
        """
        Форматировать данные о матчах в единый формат
        """
        formatted = []
        
        for fixture in fixtures:
            formatted.append({
                'id': fixture['id'],
                'date': fixture['utcDate'],
                'status': self._map_status(fixture['status']),
                'league': fixture.get('league_name', fixture['competition']['name']),
                'league_id': fixture['competition']['code'],
                'home_team_id': fixture['homeTeam']['id'],
                'home_team_name': fixture['homeTeam']['name'],
                'home_team_logo': fixture['homeTeam'].get('crest', ''),
                'away_team_id': fixture['awayTeam']['id'],
                'away_team_name': fixture['awayTeam']['name'],
                'away_team_logo': fixture['awayTeam'].get('crest', ''),
                'venue': fixture.get('venue', 'Unknown'),
                'goals': {
                    'home': fixture['score']['fullTime']['home'],
                    'away': fixture['score']['fullTime']['away']
                },
                'teams': {
                    'home': {
                        'id': fixture['homeTeam']['id'],
                        'name': fixture['homeTeam']['name']
                    },
                    'away': {
                        'id': fixture['awayTeam']['id'],
                        'name': fixture['awayTeam']['name']
                    }
                }
            })
        
        return formatted
    
    def _map_status(self, status):
        """
        Маппинг статусов из football-data.org в наш формат
        """
        status_map = {
            'SCHEDULED': 'scheduled',
            'TIMED': 'scheduled',
            'IN_PLAY': 'live',
            'PAUSED': 'live',
            'FINISHED': 'finished',
            'SUSPENDED': 'suspended',
            'POSTPONED': 'postponed',
            'CANCELLED': 'cancelled'
        }
        return status_map.get(status, 'scheduled')
    
    def get_team_last_matches(self, team_id, limit=10):
        """
        Получить последние матчи команды
        """
        fixtures = self._make_request(f'teams/{team_id}/matches', {
            'status': 'FINISHED',
            'limit': limit
        })
        
        if fixtures and 'matches' in fixtures:
            return self._format_fixtures(fixtures['matches'][:limit])
        
        return []
    
    def get_team_statistics(self, team_id, league_code, season=None):
        """
        Получить статистику команды за сезон
        """
        if season is None:
            season = datetime.now().year
        
        # Football-data.org не предоставляет детальную статистику напрямую
        # Получаем матчи команды и вычисляем статистику
        fixtures = self._make_request(f'teams/{team_id}/matches', {
            'competitions': league_code,
            'season': season,
            'status': 'FINISHED'
        })
        
        if not fixtures or 'matches' not in fixtures:
            return None
        
        return self._calculate_team_stats(fixtures['matches'], team_id)
    
    def _calculate_team_stats(self, matches, team_id):
        """
        Рассчитать статистику из матчей
        """
        total_matches = len(matches)
        wins = 0
        draws = 0
        losses = 0
        goals_scored = 0
        goals_conceded = 0
        home_wins = 0
        home_goals = 0
        away_wins = 0
        away_goals = 0
        
        for match in matches:
            is_home = match['homeTeam']['id'] == team_id
            
            if is_home:
                home_score = match['score']['fullTime']['home']
                away_score = match['score']['fullTime']['away']
                goals_scored += home_score or 0
                goals_conceded += away_score or 0
                home_goals += home_score or 0
                
                if home_score > away_score:
                    wins += 1
                    home_wins += 1
                elif home_score < away_score:
                    losses += 1
                else:
                    draws += 1
            else:
                home_score = match['score']['fullTime']['home']
                away_score = match['score']['fullTime']['away']
                goals_scored += away_score or 0
                goals_conceded += home_score or 0
                away_goals += away_score or 0
                
                if away_score > home_score:
                    wins += 1
                    away_wins += 1
                elif away_score < home_score:
                    losses += 1
                else:
                    draws += 1
        
        return {
            'team_id': team_id,
            'team_name': matches[0]['homeTeam']['name'] if matches[0]['homeTeam']['id'] == team_id else matches[0]['awayTeam']['name'],
            'total_matches': total_matches,
            'wins': wins,
            'draws': draws,
            'losses': losses,
            'goals_scored': goals_scored,
            'goals_conceded': goals_conceded,
            'avg_goals_scored': goals_scored / total_matches if total_matches > 0 else 0,
            'avg_goals_conceded': goals_conceded / total_matches if total_matches > 0 else 0,
            'home_wins': home_wins,
            'home_goals': home_goals,
            'home_avg_goals': home_goals / (total_matches / 2) if total_matches > 0 else 0,
            'away_wins': away_wins,
            'away_goals': away_goals,
            'away_avg_goals': away_goals / (total_matches / 2) if total_matches > 0 else 0
        }
    
    def get_league_standings(self, league_code, season=None):
        """
        Получить турнирную таблицу лиги
        """
        standings = self._make_request(f'competitions/{league_code}/standings')
        
        if standings and 'standings' in standings:
            return standings['standings'][0]['table']
        
        return []
    
    def get_match_details(self, fixture_id):
        """
        Получить детальную информацию о матче
        """
        match = self._make_request(f'matches/{fixture_id}')
        
        if match:
            formatted = self._format_fixtures([match])
            return formatted[0] if formatted else None
        
        return None
    
    def update_match_results(self, fixture_id):
        """
        Обновить результаты завершенного матча
        """
        match = self.get_match_details(fixture_id)
        
        if not match or match['status'] != 'finished':
            return None
        
        home_score = match['goals']['home']
        away_score = match['goals']['away']
        
        if home_score is None or away_score is None:
            return None
        
        total_goals = home_score + away_score
        
        return {
            'fixture_id': fixture_id,
            'home_score': home_score,
            'away_score': away_score,
            'total_goals': total_goals,
            'over_2_5': total_goals > 2.5,
            'btts': home_score > 0 and away_score > 0,
            'status': match['status']
        }


# Пример использования
if __name__ == '__main__':
    api = FootballDataOrgAPI()
    
    print("⚽ Тестирование Football-Data.org API\n")
    
    # Получить матчи на сегодня
    print("📅 Матчи на сегодня:")
    todays_matches = api.get_todays_fixtures()
    
    if todays_matches:
        for match in todays_matches[:5]:
            print(f"   {match['home_team_name']} vs {match['away_team_name']}")
            print(f"   Лига: {match['league']}, Время: {match['date']}\n")
    else:
        print("   Нет матчей или ошибка API\n")
