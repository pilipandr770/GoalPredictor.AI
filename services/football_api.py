"""
Универсальный сервис для работы с Football API
Поддерживает: Football-Data.org и RapidAPI
"""
from config import Config


class FootballAPIService:
    """
    Универсальный клиент для Football API
    Автоматически выбирает провайдера на основе конфигурации
    """
    
    def __init__(self):
        self.provider = Config.FOOTBALL_API_PROVIDER
        
        if self.provider == 'football-data-org':
            # Используем Football-Data.org (бесплатный)
            from services.football_data_org import FootballDataOrgAPI
            self.api = FootballDataOrgAPI()
            print("✅ Используется Football-Data.org API (бесплатный, 10 запросов/мин)")
        elif self.provider == 'rapidapi':
            # Используем RapidAPI
            from services.football_rapidapi import FootballRapidAPI
            self.api = FootballRapidAPI()
            print("✅ Используется RapidAPI Football API")
        else:
            raise ValueError(f"Неизвестный провайдер: {self.provider}. Используйте 'football-data-org' или 'rapidapi'")
    
    # Делегируем все методы к выбранному провайдеру
    
    def get_todays_fixtures(self, league=None, date=None):
        """Получить расписание матчей на сегодня"""
        return self.api.get_todays_fixtures(league, date)
    
    def get_upcoming_fixtures(self, league_id, days=7):
        """Получить предстоящие матчи на N дней вперед"""
        return self.api.get_upcoming_fixtures(league_id, days)
    
    def get_team_last_matches(self, team_id, limit=10):
        """Получить последние матчи команды"""
        return self.api.get_team_last_matches(team_id, limit)
    
    def get_team_statistics(self, team_id, league_id, season=None):
        """Получить статистику команды за сезон"""
        return self.api.get_team_statistics(team_id, league_id, season)
    
    def get_head_to_head(self, team1_id, team2_id, limit=10):
        """Получить историю личных встреч (если поддерживается)"""
        if hasattr(self.api, 'get_head_to_head'):
            return self.api.get_head_to_head(team1_id, team2_id, limit)
        return []
    
    def get_league_standings(self, league_id, season=None):
        """Получить турнирную таблицу лиги"""
        return self.api.get_league_standings(league_id, season)
    
    def get_match_details(self, fixture_id):
        """Получить детальную информацию о матче"""
        return self.api.get_match_details(fixture_id)
    
    def update_match_results(self, fixture_id):
        """Обновить результаты завершенного матча"""
        return self.api.update_match_results(fixture_id)


# Пример использования
if __name__ == '__main__':
    api = FootballAPIService()
    
    print("\n⚽ Тестирование Football API\n")
    
    # Получить матчи на сегодня
    print("📅 Матчи на сегодня:")
    todays_matches = api.get_todays_fixtures()
    
    if todays_matches:
        for match in todays_matches[:5]:
            print(f"   {match['home_team_name']} vs {match['away_team_name']}")
            print(f"   Лига: {match['league']}, Время: {match['date']}\n")
    else:
        print("   Нет матчей или ошибка API\n")
    
    print(f"\n✅ Провайдер: {api.provider}")
