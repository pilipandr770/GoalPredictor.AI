"""
Модуль машинного обучения для прогнозирования футбольных матчей
Основан на анализе статистики команд и расчете вероятности >2.5 голов
"""
import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score
import lightgbm as lgb
import joblib


class GoalPredictorModel:
    """
    ML-модель для прогнозирования результатов футбольных матчей
    """
    
    def __init__(self, model_path='ml/models'):
        self.model_path = model_path
        self.model = None
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_version = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Создать папку для моделей если не существует
        os.makedirs(model_path, exist_ok=True)
    
    def create_features(self, home_stats, away_stats, match_info=None):
        """
        Создание признаков для модели на основе статистики команд
        
        Args:
            home_stats: Статистика домашней команды
            away_stats: Статистика выездной команды
            match_info: Дополнительная информация о матче
        
        Returns:
            dict: Словарь с признаками
        """
        features = {}
        
        # === Базовые статистики ===
        # Средние голы за матч
        features['home_avg_goals_scored'] = home_stats.get('avg_goals_scored', 0)
        features['home_avg_goals_conceded'] = home_stats.get('avg_goals_conceded', 0)
        features['away_avg_goals_scored'] = away_stats.get('avg_goals_scored', 0)
        features['away_avg_goals_conceded'] = away_stats.get('avg_goals_conceded', 0)
        
        # Общее количество ожидаемых голов
        features['expected_home_goals'] = (
            home_stats.get('avg_goals_scored', 0) + 
            away_stats.get('avg_goals_conceded', 0)
        ) / 2
        
        features['expected_away_goals'] = (
            away_stats.get('avg_goals_scored', 0) + 
            home_stats.get('avg_goals_conceded', 0)
        ) / 2
        
        features['total_expected_goals'] = features['expected_home_goals'] + features['expected_away_goals']
        
        # === Статистика Over 2.5 ===
        features['home_over_2_5_percentage'] = home_stats.get('over_2_5_percentage', 0)
        features['away_over_2_5_percentage'] = away_stats.get('over_2_5_percentage', 0)
        features['combined_over_2_5'] = (
            features['home_over_2_5_percentage'] + 
            features['away_over_2_5_percentage']
        ) / 2
        
        # === Форма команд (последние 5 матчей) ===
        features['home_recent_form_score'] = self._calculate_form_score(
            home_stats.get('last_5_form', '')
        )
        features['away_recent_form_score'] = self._calculate_form_score(
            away_stats.get('last_5_form', '')
        )
        
        # === Домашние/Выездные показатели ===
        features['home_home_avg_goals'] = home_stats.get('home_avg_goals_scored', 0)
        features['away_away_avg_goals'] = away_stats.get('away_avg_goals_scored', 0)
        
        # === BTTS (Both Teams To Score) ===
        features['home_btts_percentage'] = home_stats.get('btts_percentage', 0)
        features['away_btts_percentage'] = away_stats.get('btts_percentage', 0)
        
        # === Защита ===
        features['home_clean_sheets_percentage'] = home_stats.get('clean_sheets_percentage', 0)
        features['away_clean_sheets_percentage'] = away_stats.get('clean_sheets_percentage', 0)
        
        # === Силовые показатели ===
        features['home_total_matches'] = home_stats.get('total_matches', 0)
        features['away_total_matches'] = away_stats.get('total_matches', 0)
        features['home_wins'] = home_stats.get('wins', 0)
        features['away_wins'] = away_stats.get('wins', 0)
        
        # Процент побед
        if features['home_total_matches'] > 0:
            features['home_win_percentage'] = features['home_wins'] / features['home_total_matches']
        else:
            features['home_win_percentage'] = 0
        
        if features['away_total_matches'] > 0:
            features['away_win_percentage'] = features['away_wins'] / features['away_total_matches']
        else:
            features['away_win_percentage'] = 0
        
        # === Информация о матче ===
        if match_info:
            # День недели (выходные обычно более результативные)
            if 'date' in match_info:
                match_date = match_info['date']
                features['is_weekend'] = 1 if match_date.weekday() >= 5 else 0
            
            # Важность лиги (топ-лиги более результативные)
            league_weights = {
                'Premier League': 1.0,
                'La Liga': 0.95,
                'Bundesliga': 1.1,  # Бундеслига известна результативностью
                'Serie A': 0.85,     # Серия А более оборонительная
                'Ligue 1': 0.9
            }
            features['league_weight'] = league_weights.get(match_info.get('league', ''), 0.9)
        else:
            features['is_weekend'] = 0
            features['league_weight'] = 0.9
        
        # === Взаимодействие признаков ===
        features['goals_momentum'] = (
            features['home_avg_goals_scored'] * features['away_avg_goals_conceded'] +
            features['away_avg_goals_scored'] * features['home_avg_goals_conceded']
        )
        
        features['attacking_strength_diff'] = abs(
            features['home_avg_goals_scored'] - features['away_avg_goals_scored']
        )
        
        features['defensive_weakness'] = (
            features['home_avg_goals_conceded'] + features['away_avg_goals_conceded']
        )
        
        self.feature_names = list(features.keys())
        return features
    
    def _calculate_form_score(self, form_string):
        """
        Рассчитать числовой показатель формы на основе результатов
        W (win) = 3, D (draw) = 1, L (loss) = 0
        """
        if not form_string:
            return 0
        
        score_map = {'W': 3, 'D': 1, 'L': 0}
        scores = [score_map.get(char, 0) for char in form_string]
        
        # Взвешенная сумма (последние матчи важнее)
        weights = [1.5, 1.3, 1.1, 1.0, 0.9][:len(scores)]
        weighted_score = sum(s * w for s, w in zip(scores, weights))
        
        max_score = sum([3 * w for w in weights])
        return weighted_score / max_score if max_score > 0 else 0
    
    def train(self, training_data, target_column='over_2_5'):
        """
        Обучение модели на исторических данных
        
        Args:
            training_data: DataFrame с историческими данными
            target_column: Название целевой колонки
        """
        print("🎯 Начинаю обучение модели...")
        
        # Определить названия признаков (все колонки кроме целевых)
        exclude_cols = ['over_2_5', 'btts', 'date', 'league']
        self.feature_names = [col for col in training_data.columns if col not in exclude_cols]
        
        print(f"   Количество признаков: {len(self.feature_names)}")
        
        # Подготовка данных
        X = training_data[self.feature_names]
        y = training_data[target_column]
        
        # Нормализация признаков
        X_scaled = self.scaler.fit_transform(X)
        
        # Разделение на обучающую и тестовую выборки
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Обучение LightGBM (быстрый и точный)
        self.model = lgb.LGBMClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=7,
            num_leaves=31,
            random_state=42,
            verbose=-1
        )
        
        self.model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            eval_metric='auc'
        )
        
        # Оценка модели
        train_score = self.model.score(X_train, y_train)
        test_score = self.model.score(X_test, y_test)
        
        # Кросс-валидация
        cv_scores = cross_val_score(
            self.model, X_scaled, y, cv=5, scoring='roc_auc'
        )
        
        print(f"✅ Обучение завершено!")
        print(f"   Train Accuracy: {train_score:.2%}")
        print(f"   Test Accuracy: {test_score:.2%}")
        print(f"   CV ROC-AUC: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")
        
        # Важность признаков
        feature_importance = pd.DataFrame({
            'feature': self.feature_names,
            'importance': self.model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        print("\n📊 Топ-10 важных признаков:")
        print(feature_importance.head(10))
        
        return {
            'train_score': train_score,
            'test_score': test_score,
            'cv_score': cv_scores.mean(),
            'feature_importance': feature_importance
        }
    
    def predict(self, home_stats, away_stats, match_info=None):
        """
        Сделать прогноз для конкретного матча
        
        Returns:
            dict: Прогноз с вероятностью и уровнем уверенности
        """
        if self.model is None:
            raise ValueError("Модель не обучена! Сначала вызовите train() или load_model()")
        
        # Создать признаки
        features = self.create_features(home_stats, away_stats, match_info)
        
        return self.predict_from_features(features)
    
    def predict_from_features(self, features):
        """
        Сделать прогноз на основе уже созданных признаков
        
        Args:
            features: dict с признаками матча
        
        Returns:
            dict: Прогноз с вероятностями
        """
        if self.model is None:
            raise ValueError("Модель не обучена! Сначала вызовите train() или load_model()")
        
        # Преобразовать в DataFrame
        X = pd.DataFrame([features])[self.feature_names]
        X_scaled = self.scaler.transform(X)
        
        # Получить вероятности для обоих классов
        probabilities = self.model.predict_proba(X_scaled)[0]
        over_2_5_prob = probabilities[1]  # Вероятность Over 2.5
        
        # Определить уровень уверенности
        if over_2_5_prob >= 0.75:
            confidence = 'high'
            recommendation = 'Сильная рекомендация'
        elif over_2_5_prob >= 0.65:
            confidence = 'medium'
            recommendation = 'Умеренная рекомендация'
        elif over_2_5_prob >= 0.55:
            confidence = 'low'
            recommendation = 'Слабая рекомендация'
        else:
            confidence = 'very_low'
            recommendation = 'Не рекомендуется'
        
        return {
            'over_2_5': over_2_5_prob,
            'under_2_5': probabilities[0],
            'confidence': confidence,
            'recommendation': recommendation,
            'prediction': 'Over 2.5' if over_2_5_prob >= 0.5 else 'Under 2.5',
            'model_version': self.model_version
        }
    
    def save_model(self, filename=None):
        """Сохранить модель на диск"""
        if filename is None:
            filename = f'goal_predictor_model_{self.model_version}.pkl'
        
        filepath = os.path.join(self.model_path, filename)
        
        model_data = {
            'model': self.model,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'model_version': self.model_version
        }
        
        joblib.dump(model_data, filepath)
        print(f"💾 Модель сохранена: {filepath}")
        
        return filepath
    
    def load_model(self, filename=None):
        """Загрузить модель с диска"""
        try:
            # Попробовать загрузить новую модель (v2.0)
            over_2_5_path = os.path.join(self.model_path, 'over_2_5_model.pkl')
            features_path = os.path.join(self.model_path, 'feature_columns.pkl')
            
            if os.path.exists(over_2_5_path) and os.path.exists(features_path):
                # Новая версия модели (из ml/train.py)
                self.model = joblib.load(over_2_5_path)
                self.feature_names = joblib.load(features_path)
                self.model_version = 'v2.0'
                
                print(f"📂 Модель загружена: {over_2_5_path}")
                print(f"   Версия: {self.model_version}")
                return True
                
        except Exception as e:
            print(f"   Попытка загрузить новую модель не удалась: {e}")
        
        # Попробовать старый формат
        try:
            if filename is None:
                # Загрузить последнюю модель
                model_files = [f for f in os.listdir(self.model_path) 
                              if f.endswith('.pkl') and 'goal_predictor' in f]
                if not model_files:
                    raise FileNotFoundError("Модели не найдены!")
                filename = sorted(model_files)[-1]
            
            # Если filename уже содержит полный путь, использовать его
            if os.path.dirname(filename):
                filepath = filename
            else:
                filepath = os.path.join(self.model_path, filename)
            
            model_data = joblib.load(filepath)
            
            # Проверить что это словарь со старым форматом
            if isinstance(model_data, dict):
                self.model = model_data['model']
                self.scaler = model_data['scaler']
                self.feature_names = model_data['feature_names']
                self.model_version = model_data['model_version']
            else:
                # Это просто модель
                self.model = model_data
            
            print(f"📂 Модель загружена: {filepath}")
            print(f"   Версия: {self.model_version}")
            
            return True
        except Exception as e:
            print(f"   Ошибка загрузки старой модели: {e}")
            raise
