"""
Сервіс для прогнозу Over/Under 2.5 голів
Використовує натреновану модель з акцентом на історію голів
"""
import os
import joblib
import pandas as pd
import numpy as np


class Over25GoalsPredictionService:
    """Сервіс прогнозу Over 2.5 голів"""
    
    def __init__(self):
        self.model = None
        self.scaler = None
        self.features = None
        self.metadata = None
        self.loaded = False
        
        self._load_model()
    
    def _load_model(self):
        """Завантажити модель і допоміжні файли"""
        try:
            models_dir = 'ml/models'
            
            # Завантажити модель
            model_path = os.path.join(models_dir, 'over_2_5_goals_model.pkl')
            self.model = joblib.load(model_path)
            
            # Завантажити scaler
            scaler_path = os.path.join(models_dir, 'over_2_5_scaler.pkl')
            self.scaler = joblib.load(scaler_path)
            
            # Завантажити список фічів
            features_path = os.path.join(models_dir, 'over_2_5_features.pkl')
            self.features = joblib.load(features_path)
            
            # Завантажити metadata
            metadata_path = os.path.join(models_dir, 'over_2_5_metadata.pkl')
            self.metadata = joblib.load(metadata_path)
            
            self.loaded = True
            print(f"✅ Over 2.5 модель завантажено ({self.metadata.get('model_type', 'Unknown')})")
            print(f"   Фічів: {len(self.features)}")
            
        except Exception as e:
            print(f"⚠️  Помилка завантаження Over 2.5 моделі: {e}")
            self.loaded = False
    
    def predict(self, match_data):
        """
        Прогноз Over/Under 2.5 голів
        
        Args:
            match_data: dict з даними матчу
            Потрібні ключі:
                - home_recent_goals_for
                - home_recent_goals_against
                - home_avg_goals
                - away_recent_goals_for
                - away_recent_goals_against
                - away_avg_goals
                + інші фічі якщо є
        
        Returns:
            dict: {
                'over_2_5_probability': float (0-1),
                'prediction': 'Over 2.5' | 'Under 2.5',
                'confidence': 'High' | 'Medium' | 'Low',
                'confidence_percentage': float (0-100)
            }
        """
        if not self.loaded:
            return {
                'error': 'Модель не завантажена',
                'over_2_5_probability': 0.5,
                'prediction': 'Unknown',
                'confidence': 'None',
                'confidence_percentage': 0
            }
        
        try:
            # Створити DataFrame з одним рядком
            features_df = pd.DataFrame([match_data])
            
            # Додати відсутні фічі (заповнити 0)
            for feature in self.features:
                if feature not in features_df.columns:
                    features_df[feature] = 0
            
            # Вибрати тільки потрібні фічі в правильному порядку
            features_df = features_df[self.features]
            
            # Стандартизувати
            features_scaled = self.scaler.transform(features_df)
            
            # Прогноз
            probability = self.model.predict_proba(features_scaled)[0][1]  # Ймовірність Over 2.5
            
            # Визначити prediction
            prediction_text = 'Over 2.5' if probability >= 0.5 else 'Under 2.5'
            
            # Розрахувати confidence
            confidence_score = abs(probability - 0.5) * 2  # 0-1 scale
            if confidence_score >= 0.6:
                confidence_text = 'High'
            elif confidence_score >= 0.3:
                confidence_text = 'Medium'
            else:
                confidence_text = 'Low'
            
            return {
                'over_2_5_probability': float(probability),
                'under_2_5_probability': float(1 - probability),
                'prediction': prediction_text,
                'confidence': confidence_text,
                'confidence_percentage': float(max(probability, 1-probability) * 100),
                'key_factors': self._explain_prediction(match_data)
            }
            
        except Exception as e:
            print(f"Помилка прогнозу Over 2.5: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'over_2_5_probability': 0.5,
                'prediction': 'Error',
                'confidence': 'None',
                'confidence_percentage': 0
            }
    
    def _explain_prediction(self, match_data):
        """Пояснити чому модель зробила такий прогноз"""
        factors = []
        
        # Перевірити голи господарів
        home_goals = match_data.get('home_recent_goals_for', 0)
        if home_goals > 8:  # Багато голів за останні матчі
            factors.append({
                'factor': 'Home Team Scoring',
                'value': f'{home_goals} goals in recent matches',
                'impact': 'positive'
            })
        elif home_goals < 3:
            factors.append({
                'factor': 'Home Team Scoring',
                'value': f'Only {home_goals} goals in recent matches',
                'impact': 'negative'
            })
        
        # Перевірити голи гостей
        away_goals = match_data.get('away_recent_goals_for', 0)
        if away_goals > 8:
            factors.append({
                'factor': 'Away Team Scoring',
                'value': f'{away_goals} goals in recent matches',
                'impact': 'positive'
            })
        elif away_goals < 3:
            factors.append({
                'factor': 'Away Team Scoring',
                'value': f'Only {away_goals} goals in recent matches',
                'impact': 'negative'
            })
        
        # Перевірити захист
        home_conceded = match_data.get('home_recent_goals_against', 0)
        away_conceded = match_data.get('away_recent_goals_against', 0)
        
        if home_conceded + away_conceded > 15:
            factors.append({
                'factor': 'Weak Defenses',
                'value': 'Both teams concede many goals',
                'impact': 'positive'
            })
        
        return factors


# Singleton instance
_service_instance = None

def get_over25_prediction_service():
    """Отримати singleton instance сервісу"""
    global _service_instance
    if _service_instance is None:
        _service_instance = Over25GoalsPredictionService()
    return _service_instance


# Тестування
if __name__ == '__main__':
    print("🧪 Тестування Over 2.5 Goals Prediction Service\n")
    
    service = get_over25_prediction_service()
    
    if service.loaded:
        # Тестовий матч з багатьма голами
        test_match_high_scoring = {
            'home_recent_goals_for': 12,
            'home_recent_goals_against': 8,
            'home_avg_goals': 2.1,
            'home_scoring_trend': 0.2,
            'away_recent_goals_for': 10,
            'away_recent_goals_against': 9,
            'away_avg_goals': 1.9,
            'away_scoring_trend': 0.1,
            'home_recent_form_points': 10,
            'away_recent_form_points': 9
        }
        
        result = service.predict(test_match_high_scoring)
        print("📊 Тест 1: Матч з багатьма голами")
        print(f"   Prediction: {result['prediction']}")
        print(f"   Probability: {result['over_2_5_probability']:.1%}")
        print(f"   Confidence: {result['confidence']} ({result['confidence_percentage']:.1f}%)")
        
        # Тестовий матч з малою кількістю голів
        test_match_low_scoring = {
            'home_recent_goals_for': 3,
            'home_recent_goals_against': 2,
            'home_avg_goals': 0.9,
            'home_scoring_trend': -0.1,
            'away_recent_goals_for': 2,
            'away_recent_goals_against': 1,
            'away_avg_goals': 0.7,
            'away_scoring_trend': -0.2,
            'home_recent_form_points': 5,
            'away_recent_form_points': 4
        }
        
        result = service.predict(test_match_low_scoring)
        print("\n📊 Тест 2: Матч з малою кількістю голів")
        print(f"   Prediction: {result['prediction']}")
        print(f"   Probability: {result['over_2_5_probability']:.1%}")
        print(f"   Confidence: {result['confidence']} ({result['confidence_percentage']:.1f}%)")
