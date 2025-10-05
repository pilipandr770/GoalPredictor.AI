"""
Модуль для создания прогнозов на основе обученной модели
"""
import os
import sys
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.model import GoalPredictorModel
from services.football_api import FootballAPIService
from services.openai_service import OpenAIService


class PredictionService:
    """
    Сервис для создания прогнозов на матчи
    """
    
    def __init__(self):
        self.model = GoalPredictorModel()
        self.football_api = FootballAPIService()
        self.openai_service = OpenAIService()
        
        # Загрузить обученную модель
        try:
            self.model.load_model()
        except Exception as e:
            print(f"⚠️ Не удалось загрузить модель: {e}")
            print("   Модель нужно обучить! Запустите: python ml/train.py")
    
    def predict_match(self, match_data, include_explanation=True):
        """
        Создать прогноз для конкретного матча
        
        Args:
            match_data: Данные о матче (из API или БД)
            include_explanation: Генерировать ли текстовое объяснение
        
        Returns:
            dict: Полный прогноз с объяснением
        """
        # Получить статистику команд
        home_stats = self._get_team_stats(
            match_data['home_team_id'],
            is_home=True
        )
        
        away_stats = self._get_team_stats(
            match_data['away_team_id'],
            is_home=False
        )
        
        # Информация о матче
        match_info = {
            'date': match_data.get('date', datetime.now()),
            'league': match_data.get('league', 'Unknown')
        }
        
        # Получить прогноз от модели
        prediction = self.model.predict(home_stats, away_stats, match_info)
        
        # Добавить информацию о матче
        prediction['match_info'] = {
            'home_team': match_data['home_team_name'],
            'away_team': match_data['away_team_name'],
            'league': match_data.get('league', ''),
            'date': match_data.get('date', ''),
        }
        
        # Генерировать объяснение через OpenAI
        if include_explanation:
            explanation = self._generate_explanation(
                prediction,
                home_stats,
                away_stats,
                match_data
            )
            prediction['explanation'] = explanation
        
        return prediction
    
    def _get_team_stats(self, team_id, is_home=True):
        """
        Получить статистику команды из API или БД
        """
        try:
            # Получить последние матчи команды
            matches = self.football_api.get_team_last_matches(team_id, limit=10)
            
            # Рассчитать статистику
            stats = self._calculate_stats_from_matches(matches, team_id, is_home)
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Ошибка при получении статистики команды {team_id}: {e}")
            # Вернуть дефолтную статистику
            return self._get_default_stats()
    
    def _calculate_stats_from_matches(self, matches, team_id, is_home):
        """
        Рассчитать статистику на основе последних матчей
        """
        if not matches:
            return self._get_default_stats()
        
        total_goals_scored = 0
        total_goals_conceded = 0
        over_2_5_count = 0
        btts_count = 0
        clean_sheets = 0
        form = []
        wins = 0
        
        for match in matches:
            # Определить голы
            if match['teams']['home']['id'] == team_id:
                goals_scored = match['goals']['home']
                goals_conceded = match['goals']['away']
                is_team_home = True
            else:
                goals_scored = match['goals']['away']
                goals_conceded = match['goals']['home']
                is_team_home = False
            
            total_goals_scored += goals_scored
            total_goals_conceded += goals_conceded
            
            # Over 2.5
            total_goals = match['goals']['home'] + match['goals']['away']
            if total_goals > 2.5:
                over_2_5_count += 1
            
            # BTTS
            if match['goals']['home'] > 0 and match['goals']['away'] > 0:
                btts_count += 1
            
            # Clean sheet
            if goals_conceded == 0:
                clean_sheets += 1
            
            # Форма
            if goals_scored > goals_conceded:
                form.append('W')
                wins += 1
            elif goals_scored < goals_conceded:
                form.append('L')
            else:
                form.append('D')
        
        num_matches = len(matches)
        
        stats = {
            'total_matches': num_matches,
            'avg_goals_scored': total_goals_scored / num_matches,
            'avg_goals_conceded': total_goals_conceded / num_matches,
            'over_2_5_percentage': over_2_5_count / num_matches,
            'btts_percentage': btts_count / num_matches,
            'clean_sheets_percentage': clean_sheets / num_matches,
            'last_5_form': ''.join(form[:5]),
            'wins': wins,
        }
        
        # Домашние/выездные показатели
        if is_home:
            stats['home_avg_goals_scored'] = stats['avg_goals_scored']
        else:
            stats['away_avg_goals_scored'] = stats['avg_goals_scored']
        
        return stats
    
    def _get_default_stats(self):
        """Дефолтная статистика если данные недоступны"""
        return {
            'total_matches': 10,
            'avg_goals_scored': 1.5,
            'avg_goals_conceded': 1.2,
            'over_2_5_percentage': 0.5,
            'btts_percentage': 0.5,
            'clean_sheets_percentage': 0.3,
            'last_5_form': 'WDWLD',
            'wins': 2,
            'home_avg_goals_scored': 1.5,
            'away_avg_goals_scored': 1.3,
        }
    
    def _generate_explanation(self, prediction, home_stats, away_stats, match_data):
        """
        Генерировать текстовое объяснение прогноза через OpenAI
        """
        try:
            explanation = self.openai_service.generate_match_explanation(
                prediction,
                home_stats,
                away_stats,
                match_data
            )
            return explanation
        except Exception as e:
            print(f"⚠️ Ошибка генерации объяснения: {e}")
            # Вернуть базовое объяснение
            return self._generate_basic_explanation(prediction, home_stats, away_stats)
    
    def _generate_basic_explanation(self, prediction, home_stats, away_stats):
        """
        Базовое объяснение без OpenAI
        """
        prob = prediction['probability']
        
        explanation = f"Вероятность более 2.5 голов: {prob:.1%}\n\n"
        explanation += "Ключевые факторы:\n"
        explanation += f"• Домашняя команда забивает в среднем {home_stats['avg_goals_scored']:.1f} гола\n"
        explanation += f"• Гостевая команда забивает в среднем {away_stats['avg_goals_scored']:.1f} гола\n"
        explanation += f"• Over 2.5 в матчах хозяев: {home_stats['over_2_5_percentage']:.0%}\n"
        explanation += f"• Over 2.5 в матчах гостей: {away_stats['over_2_5_percentage']:.0%}\n"
        
        return explanation
    
    def predict_todays_matches(self, league=None):
        """
        Создать прогнозы на все матчи сегодня
        
        Args:
            league: Фильтр по лиге (опционально)
        
        Returns:
            list: Список прогнозов
        """
        # Получить расписание матчей на сегодня
        matches = self.football_api.get_todays_fixtures(league)
        
        predictions = []
        
        for match in matches:
            try:
                # Создать прогноз
                prediction = self.predict_match(match, include_explanation=True)
                predictions.append(prediction)
                
            except Exception as e:
                print(f"⚠️ Ошибка прогноза для матча {match.get('id')}: {e}")
                continue
        
        # Сортировать по вероятности (самые уверенные сначала)
        predictions.sort(key=lambda x: x['probability'], reverse=True)
        
        return predictions


if __name__ == '__main__':
    # Тестирование
    predictor = PredictionService()
    
    # Пример прогноза
    test_match = {
        'home_team_id': 33,  # Manchester United
        'away_team_id': 40,  # Liverpool
        'home_team_name': 'Manchester United',
        'away_team_name': 'Liverpool',
        'league': 'Premier League',
        'date': datetime.now()
    }
    
    prediction = predictor.predict_match(test_match)
    
    print("\n" + "="*60)
    print(f"🎯 Прогноз: {test_match['home_team_name']} vs {test_match['away_team_name']}")
    print("="*60)
    print(f"Вероятность Over 2.5: {prediction['probability']:.1%}")
    print(f"Уверенность: {prediction['confidence']}")
    print(f"Рекомендация: {prediction['recommendation']}")
    print(f"\n{prediction.get('explanation', 'Объяснение недоступно')}")
    print("="*60)
