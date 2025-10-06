"""
Сервис прогнозирования с использованием ансамбля моделей ML
Интегрирует расширенные признаки и множественные модели
"""
import os
import sys
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

# Добавить путь к ML модулю
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ml.train_ensemble import EnsembleGoalPredictor
from ml.advanced_features import AdvancedFeatureEngineering
from services.football_api import FootballAPIService


class EnhancedPredictionService:
    """Сервис прогнозирования с ансамблем моделей"""
    
    def __init__(self):
        self.ensemble = EnsembleGoalPredictor()
        self.feature_engine = AdvancedFeatureEngineering()
        self.football_api = FootballAPIService()
        self.model_loaded = False
        
        # Загрузить последнюю модель ансамбля
        self._load_latest_ensemble()
    
    def _load_latest_ensemble(self):
        """Загрузить последнюю обученную модель ансамбля"""
        try:
            model_dir = 'ml/models'
            ensemble_files = [f for f in os.listdir(model_dir) if f.startswith('ensemble_')]
            
            if ensemble_files:
                latest_model = sorted(ensemble_files)[-1]
                model_path = os.path.join(model_dir, latest_model)
                self.ensemble.load_ensemble(model_path)
                self.model_loaded = True
                print(f"✅ Ансамбль загружен: {latest_model}")
            else:
                print("⚠️  Ансамбль не найден. Используйте train_ensemble.py")
        except Exception as e:
            print(f"❌ Ошибка загрузки ансамбля: {e}")
    
    def get_upcoming_matches(self, days_ahead=7, leagues=None):
        """
        Получить расписание предстоящих матчей
        
        Args:
            days_ahead: Количество дней вперед
            leagues: Список кодов лиг (PL, PD, BL1, SA, FL1)
        
        Returns:
            list: Список матчей с информацией
        """
        if leagues is None:
            leagues = ['PL', 'PD', 'BL1', 'SA', 'FL1']  # Топ-5 лиг
        
        all_matches = []
        
        for league_code in leagues:
            try:
                matches = self.football_api.get_matches(competition=league_code)
                
                # Фильтр только будущих матчей
                today = datetime.now()
                future_date = today + timedelta(days=days_ahead)
                
                for match in matches:
                    match_date = datetime.fromisoformat(match['utcDate'].replace('Z', '+00:00'))
                    
                    if today <= match_date <= future_date:
                        all_matches.append({
                            'id': match['id'],
                            'date': match_date.strftime('%Y-%m-%d %H:%M'),
                            'competition': match['competition']['name'],
                            'home_team': match['homeTeam']['name'],
                            'away_team': match['awayTeam']['name'],
                            'home_team_id': match['homeTeam']['id'],
                            'away_team_id': match['awayTeam']['id'],
                            'status': match['status']
                        })
            except Exception as e:
                print(f"Ошибка получения матчей для {league_code}: {e}")
        
        # Сортировка по дате
        all_matches.sort(key=lambda x: x['date'])
        
        return all_matches
    
    def get_team_recent_matches(self, team_id, limit=10):
        """Получить последние матчи команды"""
        try:
            matches = self.football_api.get_team_matches(team_id)
            
            # Фильтр только завершенных матчей
            finished_matches = [m for m in matches if m['status'] == 'FINISHED']
            
            # Сортировка по дате (новые первые)
            finished_matches.sort(
                key=lambda x: datetime.fromisoformat(x['utcDate'].replace('Z', '+00:00')),
                reverse=True
            )
            
            return finished_matches[:limit]
        except Exception as e:
            print(f"Ошибка получения матчей команды {team_id}: {e}")
            return []
    
    def calculate_team_stats(self, team_id, is_home=True):
        """
        Рассчитать статистику команды для прогноза
        
        Args:
            team_id: ID команды
            is_home: Домашние или выездные матчи
        
        Returns:
            dict: Статистика команды
        """
        recent_matches = self.get_team_recent_matches(team_id)
        
        if not recent_matches:
            return self._get_default_stats()
        
        stats = {
            'goals_scored_last_3': 0,
            'goals_scored_last_5': 0,
            'goals_scored_last_10': 0,
            'goals_conceded_last_3': 0,
            'goals_conceded_last_5': 0,
            'goals_conceded_last_10': 0,
            'shots_last_5': 0,
            'shots_on_target_last_5': 0,
            'corners_last_5': 0,
            'fouls_last_5': 0,
            'yellow_cards_last_5': 0,
        }
        
        # Рассчитать статистику по окнам
        for i, match in enumerate(recent_matches[:10]):
            score = match.get('score', {}).get('fullTime', {})
            home_goals = score.get('home', 0) or 0
            away_goals = score.get('away', 0) or 0
            
            # Определить голы для/против
            if match['homeTeam']['id'] == team_id:
                goals_for = home_goals
                goals_against = away_goals
            else:
                goals_for = away_goals
                goals_against = home_goals
            
            # Добавить в окна
            if i < 3:
                stats['goals_scored_last_3'] += goals_for
                stats['goals_conceded_last_3'] += goals_against
            if i < 5:
                stats['goals_scored_last_5'] += goals_for
                stats['goals_conceded_last_5'] += goals_against
            if i < 10:
                stats['goals_scored_last_10'] += goals_for
                stats['goals_conceded_last_10'] += goals_against
        
        # Средние значения
        for key in ['goals_scored_last_3', 'goals_conceded_last_3']:
            stats[key] = stats[key] / min(3, len(recent_matches))
        
        for key in ['goals_scored_last_5', 'goals_conceded_last_5', 
                    'shots_last_5', 'shots_on_target_last_5', 'corners_last_5',
                    'fouls_last_5', 'yellow_cards_last_5']:
            stats[key] = stats[key] / min(5, len(recent_matches))
        
        for key in ['goals_scored_last_10', 'goals_conceded_last_10']:
            stats[key] = stats[key] / min(10, len(recent_matches))
        
        return stats
    
    def _get_default_stats(self):
        """Статистика по умолчанию если нет данных"""
        return {
            'goals_scored_last_3': 1.0,
            'goals_scored_last_5': 1.0,
            'goals_scored_last_10': 1.0,
            'goals_conceded_last_3': 1.0,
            'goals_conceded_last_5': 1.0,
            'goals_conceded_last_10': 1.0,
            'shots_last_5': 10.0,
            'shots_on_target_last_5': 4.0,
            'corners_last_5': 5.0,
            'fouls_last_5': 12.0,
            'yellow_cards_last_5': 2.0,
        }
    
    def create_features_for_match(self, home_team_id, away_team_id, match_date=None):
        """
        Создать признаки для прогноза матча
        
        Args:
            home_team_id: ID домашней команды
            away_team_id: ID выездной команды
            match_date: Дата матча (для временных признаков)
        
        Returns:
            dict: 58 признаков для модели
        """
        # Получить статистику команд
        home_stats = self.calculate_team_stats(home_team_id, is_home=True)
        away_stats = self.calculate_team_stats(away_team_id, is_home=False)
        
        # Объединить признаки с префиксами
        features = {}
        for key, value in home_stats.items():
            features[f'home_{key}'] = value
        for key, value in away_stats.items():
            features[f'away_{key}'] = value
        
        # Временные признаки
        if match_date:
            try:
                if isinstance(match_date, str):
                    # Попробовать разные форматы даты
                    for fmt in ['%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d %H:%M', '%Y-%m-%d']:
                        try:
                            match_date = datetime.strptime(match_date, fmt)
                            break
                        except:
                            continue
                
                if hasattr(match_date, 'weekday'):
                    features['day_of_week'] = match_date.weekday()
                    features['is_weekend'] = 1 if match_date.weekday() >= 5 else 0
                    features['month'] = match_date.month
                    features['is_holiday_season'] = 1 if match_date.month in [12, 1] else 0
                else:
                    # Если не удалось распарсить, используем значения по умолчанию
                    features['day_of_week'] = 0
                    features['is_weekend'] = 0
                    features['month'] = 1
                    features['is_holiday_season'] = 0
            except Exception as e:
                print(f"⚠️ Ошибка парсинга даты '{match_date}': {e}")
                features['day_of_week'] = 0
                features['is_weekend'] = 0
                features['month'] = 1
                features['is_holiday_season'] = 0
        else:
            features['day_of_week'] = 0
            features['is_weekend'] = 0
            features['month'] = 1
            features['is_holiday_season'] = 0
        
        # Head-to-head (упрощенная версия, в реальности нужна история)
        features['h2h_matches'] = 5
        features['h2h_avg_goals'] = 2.5
        features['h2h_over_2_5_pct'] = 0.6
        
        # Расчетные признаки
        features['expected_home_goals'] = (
            features['home_goals_scored_last_5'] + features['away_goals_conceded_last_5']
        ) / 2
        
        features['expected_away_goals'] = (
            features['away_goals_scored_last_5'] + features['home_goals_conceded_last_5']
        ) / 2
        
        features['expected_total_goals'] = (
            features['expected_home_goals'] + features['expected_away_goals']
        )
        
        features['attacking_strength'] = (
            features.get('home_shots_on_target_last_5', 4) + 
            features.get('away_shots_on_target_last_5', 4)
        )
        
        features['total_aggression'] = (
            features.get('home_fouls_last_5', 12) + 
            features.get('away_fouls_last_5', 12)
        )
        
        # Форма команд (если есть в данных)
        features['home_form_points'] = 0
        features['away_form_points'] = 0
        features['home_win_streak_3'] = 0
        features['away_win_streak_3'] = 0
        
        return features
    
    def predict_match(self, match_info):
        """
        Сделать прогноз для матча с объяснениями
        
        Args:
            match_info: Информация о матче
        
        Returns:
            dict: Прогноз с объяснениями
        """
        if not self.model_loaded:
            return {
                'error': 'Модель не загружена',
                'ensemble_proba': 0.5,
                'prediction': 'Unknown',
                'confidence': 'Low'
            }
        
        try:
            # Создать признаки
            features = self.create_features_for_match(
                match_info['home_team_id'],
                match_info['away_team_id'],
                match_info.get('date')
            )
            
            # Получить прогноз от ансамбля
            prediction = self.ensemble.predict(features)
            
            # Добавить объяснения
            prediction['match_info'] = match_info
            prediction['key_factors'] = self._extract_key_factors(features)
            prediction['explanation'] = self._generate_explanation(features, prediction)
            
            return prediction
            
        except Exception as e:
            print(f"Ошибка прогноза: {e}")
            return {
                'error': str(e),
                'ensemble_proba': 0.5,
                'prediction': 'Error',
                'confidence': 'Low'
            }
    
    def _extract_key_factors(self, features):
        """Извлечь ключевые факторы для объяснения"""
        key_factors = []
        
        # Ожидаемые голы
        if 'expected_total_goals' in features:
            key_factors.append({
                'name': 'Ожидаемые голы',
                'value': f"{features['expected_total_goals']:.2f}",
                'impact': 'high' if features['expected_total_goals'] > 2.5 else 'low'
            })
        
        # Форма хозяев
        if 'home_goals_scored_last_5' in features:
            home_form = features['home_goals_scored_last_5']
            key_factors.append({
                'name': 'Форма хозяев (голы)',
                'value': f"{home_form:.2f} за 5 матчей",
                'impact': 'high' if home_form > 1.5 else 'medium'
            })
        
        # Форма гостей
        if 'away_goals_scored_last_5' in features:
            away_form = features['away_goals_scored_last_5']
            key_factors.append({
                'name': 'Форма гостей (голы)',
                'value': f"{away_form:.2f} за 5 матчей",
                'impact': 'high' if away_form > 1.5 else 'medium'
            })
        
        # Атакующая сила
        if 'attacking_strength' in features:
            key_factors.append({
                'name': 'Атакующая сила',
                'value': f"{features['attacking_strength']:.1f} ударов в створ",
                'impact': 'high' if features['attacking_strength'] > 8 else 'medium'
            })
        
        # Head-to-head
        if 'h2h_over_2_5_pct' in features:
            key_factors.append({
                'name': 'История встреч',
                'value': f"{features['h2h_over_2_5_pct']:.0%} Over 2.5",
                'impact': 'medium'
            })
        
        return key_factors[:5]  # Топ-5 факторов
    
    def _generate_explanation(self, features, prediction):
        """Сгенерировать текстовое объяснение"""
        proba = prediction['ensemble_proba']
        
        if proba > 0.75:
            confidence_text = "Высокая уверенность"
        elif proba > 0.60:
            confidence_text = "Средняя уверенность"
        elif proba > 0.50:
            confidence_text = "Низкая уверенность"
        else:
            confidence_text = "Прогноз против Over 2.5"
        
        expected_goals = features.get('expected_total_goals', 2.0)
        
        explanation = f"{confidence_text} в прогнозе Over 2.5 голов ({proba:.1%}). "
        explanation += f"Ожидаемое количество голов: {expected_goals:.2f}. "
        
        # Добавить причины
        if proba > 0.6:
            reasons = []
            if features.get('home_goals_scored_last_5', 0) > 1.5:
                reasons.append("сильная атака хозяев")
            if features.get('away_goals_scored_last_5', 0) > 1.5:
                reasons.append("результативные гости")
            if features.get('attacking_strength', 0) > 8:
                reasons.append("высокая атакующая активность обеих команд")
            
            if reasons:
                explanation += "Основные факторы: " + ", ".join(reasons) + "."
        
        return explanation


# Глобальный экземпляр сервиса
_prediction_service = None

def get_prediction_service():
    """Получить singleton экземпляр сервиса"""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = EnhancedPredictionService()
    return _prediction_service
