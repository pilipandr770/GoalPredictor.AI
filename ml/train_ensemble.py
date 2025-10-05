"""
Обучение ансамбля из нескольких моделей для улучшения точности прогнозов
Использует LightGBM, XGBoost, CatBoost, Random Forest
"""
import pandas as pd
import numpy as np
import os
from datetime import datetime
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, roc_auc_score, classification_report
import lightgbm as lgb
import xgboost as xgb
import joblib

# Попробовать импортировать CatBoost
try:
    from catboost import CatBoostClassifier
    CATBOOST_AVAILABLE = True
except ImportError:
    CATBOOST_AVAILABLE = False
    print("⚠️  CatBoost не установлен. Установите: pip install catboost")


class EnsembleGoalPredictor:
    """Ансамбль из нескольких моделей для прогнозирования Over 2.5"""
    
    def __init__(self, model_path='ml/models'):
        self.model_path = model_path
        self.models = {}
        self.scaler = StandardScaler()
        self.feature_names = []
        self.model_weights = {}
        
        os.makedirs(model_path, exist_ok=True)
    
    def train_lightgbm(self, X_train, y_train, X_test, y_test):
        """Обучить LightGBM модель"""
        print("\n🎯 Обучение LightGBM...")
        
        model = lgb.LGBMClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=8,
            num_leaves=31,
            min_child_samples=20,
            subsample=0.8,
            colsample_bytree=0.8,
            random_state=42,
            verbose=-1
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            eval_metric='auc'
        )
        
        # Оценка
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        train_proba = model.predict_proba(X_train)[:, 1]
        test_proba = model.predict_proba(X_test)[:, 1]
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        train_auc = roc_auc_score(y_train, train_proba)
        test_auc = roc_auc_score(y_test, test_proba)
        
        print(f"   Train Accuracy: {train_acc:.2%}")
        print(f"   Test Accuracy: {test_acc:.2%}")
        print(f"   Train AUC: {train_auc:.2%}")
        print(f"   Test AUC: {test_auc:.2%}")
        
        return model, test_acc, test_auc
    
    def train_xgboost(self, X_train, y_train, X_test, y_test):
        """Обучить XGBoost модель"""
        print("\n🎯 Обучение XGBoost...")
        
        model = xgb.XGBClassifier(
            n_estimators=300,
            learning_rate=0.05,
            max_depth=7,
            min_child_weight=1,
            subsample=0.8,
            colsample_bytree=0.8,
            gamma=0.1,
            random_state=42,
            eval_metric='logloss',
            use_label_encoder=False
        )
        
        model.fit(
            X_train, y_train,
            eval_set=[(X_test, y_test)],
            verbose=False
        )
        
        # Оценка
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        train_proba = model.predict_proba(X_train)[:, 1]
        test_proba = model.predict_proba(X_test)[:, 1]
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        train_auc = roc_auc_score(y_train, train_proba)
        test_auc = roc_auc_score(y_test, test_proba)
        
        print(f"   Train Accuracy: {train_acc:.2%}")
        print(f"   Test Accuracy: {test_acc:.2%}")
        print(f"   Train AUC: {train_auc:.2%}")
        print(f"   Test AUC: {test_auc:.2%}")
        
        return model, test_acc, test_auc
    
    def train_catboost(self, X_train, y_train, X_test, y_test):
        """Обучить CatBoost модель"""
        if not CATBOOST_AVAILABLE:
            print("\n⚠️  CatBoost пропущен (не установлен)")
            return None, 0, 0
        
        print("\n🎯 Обучение CatBoost...")
        
        model = CatBoostClassifier(
            iterations=300,
            learning_rate=0.05,
            depth=7,
            l2_leaf_reg=3,
            random_seed=42,
            verbose=False
        )
        
        model.fit(
            X_train, y_train,
            eval_set=(X_test, y_test),
            verbose=False
        )
        
        # Оценка
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        train_proba = model.predict_proba(X_train)[:, 1]
        test_proba = model.predict_proba(X_test)[:, 1]
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        train_auc = roc_auc_score(y_train, train_proba)
        test_auc = roc_auc_score(y_test, test_proba)
        
        print(f"   Train Accuracy: {train_acc:.2%}")
        print(f"   Test Accuracy: {test_acc:.2%}")
        print(f"   Train AUC: {train_auc:.2%}")
        print(f"   Test AUC: {test_auc:.2%}")
        
        return model, test_acc, test_auc
    
    def train_random_forest(self, X_train, y_train, X_test, y_test):
        """Обучить Random Forest модель"""
        print("\n🎯 Обучение Random Forest...")
        
        model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=5,
            max_features='sqrt',
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Оценка
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        train_proba = model.predict_proba(X_train)[:, 1]
        test_proba = model.predict_proba(X_test)[:, 1]
        
        train_acc = accuracy_score(y_train, train_pred)
        test_acc = accuracy_score(y_test, test_pred)
        train_auc = roc_auc_score(y_train, train_proba)
        test_auc = roc_auc_score(y_test, test_proba)
        
        print(f"   Train Accuracy: {train_acc:.2%}")
        print(f"   Test Accuracy: {test_acc:.2%}")
        print(f"   Train AUC: {train_auc:.2%}")
        print(f"   Test AUC: {test_auc:.2%}")
        
        return model, test_acc, test_auc
    
    def train_ensemble(self, training_data, target_column='over_2_5'):
        """
        Обучить ансамбль из всех моделей
        
        Args:
            training_data: DataFrame с признаками и целевой переменной
            target_column: Название целевой колонки
        """
        print("="*70)
        print("🚀 ОБУЧЕНИЕ АНСАМБЛЯ МОДЕЛЕЙ")
        print("="*70)
        
        # Подготовка данных
        self.feature_names = [col for col in training_data.columns 
                             if col not in ['over_2_5', 'btts']]
        
        print(f"\n📊 Данные для обучения:")
        print(f"   Образцов: {len(training_data)}")
        print(f"   Признаков: {len(self.feature_names)}")
        print(f"   Over 2.5: {training_data[target_column].mean():.1%}")
        
        X = training_data[self.feature_names]
        y = training_data[target_column]
        
        # Нормализация
        X_scaled = self.scaler.fit_transform(X)
        
        # Разделение на обучающую и тестовую выборки
        X_train, X_test, y_train, y_test = train_test_split(
            X_scaled, y, test_size=0.2, random_state=42, stratify=y
        )
        
        print(f"\n📈 Размеры выборок:")
        print(f"   Train: {len(X_train)} образцов")
        print(f"   Test: {len(X_test)} образцов")
        
        # Обучить все модели
        results = {}
        
        # 1. LightGBM
        lgb_model, lgb_acc, lgb_auc = self.train_lightgbm(X_train, y_train, X_test, y_test)
        if lgb_model:
            self.models['lightgbm'] = lgb_model
            results['lightgbm'] = {'accuracy': lgb_acc, 'auc': lgb_auc}
        
        # 2. XGBoost
        xgb_model, xgb_acc, xgb_auc = self.train_xgboost(X_train, y_train, X_test, y_test)
        if xgb_model:
            self.models['xgboost'] = xgb_model
            results['xgboost'] = {'accuracy': xgb_acc, 'auc': xgb_auc}
        
        # 3. CatBoost
        cat_model, cat_acc, cat_auc = self.train_catboost(X_train, y_train, X_test, y_test)
        if cat_model:
            self.models['catboost'] = cat_model
            results['catboost'] = {'accuracy': cat_acc, 'auc': cat_auc}
        
        # 4. Random Forest
        rf_model, rf_acc, rf_auc = self.train_random_forest(X_train, y_train, X_test, y_test)
        if rf_model:
            self.models['random_forest'] = rf_model
            results['random_forest'] = {'accuracy': rf_acc, 'auc': rf_auc}
        
        # Вычислить веса для ансамбля (на основе AUC)
        total_auc = sum(r['auc'] for r in results.values())
        for model_name, metrics in results.items():
            self.model_weights[model_name] = metrics['auc'] / total_auc
        
        # Тест ансамбля
        print("\n" + "="*70)
        print("🎯 ТЕСТИРОВАНИЕ АНСАМБЛЯ")
        print("="*70)
        
        ensemble_proba = self._ensemble_predict_proba(X_test)
        ensemble_pred = (ensemble_proba >= 0.5).astype(int)
        
        ensemble_acc = accuracy_score(y_test, ensemble_pred)
        ensemble_auc = roc_auc_score(y_test, ensemble_proba)
        
        print(f"\n📊 Результаты:")
        print(f"\n{'Модель':<20} {'Accuracy':>12} {'AUC':>12} {'Вес':>12}")
        print("-" * 60)
        for model_name, metrics in results.items():
            weight = self.model_weights.get(model_name, 0)
            print(f"{model_name:<20} {metrics['accuracy']:>11.2%} {metrics['auc']:>11.2%} {weight:>11.2%}")
        
        print("-" * 60)
        print(f"{'АНСАМБЛЬ':<20} {ensemble_acc:>11.2%} {ensemble_auc:>11.2%}")
        print("=" * 60)
        
        # Classification Report
        print(f"\n📋 Детальный отчет ансамбля:")
        print(classification_report(y_test, ensemble_pred, target_names=['Under 2.5', 'Over 2.5']))
        
        return {
            'models': results,
            'ensemble': {'accuracy': ensemble_acc, 'auc': ensemble_auc},
            'weights': self.model_weights
        }
    
    def _ensemble_predict_proba(self, X):
        """Получить вероятность от ансамбля"""
        predictions = []
        weights = []
        
        for model_name, model in self.models.items():
            proba = model.predict_proba(X)[:, 1]
            weight = self.model_weights[model_name]
            predictions.append(proba * weight)
            weights.append(weight)
        
        # Взвешенное среднее
        ensemble_proba = np.sum(predictions, axis=0)
        return ensemble_proba
    
    def predict(self, features):
        """
        Сделать прогноз ансамблем
        
        Args:
            features: dict или DataFrame с признаками
        """
        if isinstance(features, dict):
            X = pd.DataFrame([features])[self.feature_names]
        else:
            X = features[self.feature_names]
        
        X_scaled = self.scaler.transform(X)
        
        # Получить прогнозы от каждой модели
        predictions = {}
        for model_name, model in self.models.items():
            proba = model.predict_proba(X_scaled)[0][1]
            predictions[model_name] = proba
        
        # Финальный прогноз ансамбля
        ensemble_proba = self._ensemble_predict_proba(X_scaled)[0]
        
        return {
            'ensemble_proba': ensemble_proba,
            'individual_predictions': predictions,
            'prediction': 'Over 2.5' if ensemble_proba >= 0.5 else 'Under 2.5',
            'confidence': 'High' if abs(ensemble_proba - 0.5) > 0.25 else 'Medium' if abs(ensemble_proba - 0.5) > 0.15 else 'Low'
        }
    
    def save_ensemble(self):
        """Сохранить все модели ансамбля"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        ensemble_data = {
            'models': self.models,
            'scaler': self.scaler,
            'feature_names': self.feature_names,
            'weights': self.model_weights,
            'timestamp': timestamp
        }
        
        filepath = os.path.join(self.model_path, f'ensemble_model_{timestamp}.pkl')
        joblib.dump(ensemble_data, filepath)
        
        print(f"\n💾 Ансамбль сохранен: {filepath}")
        return filepath
    
    def load_ensemble(self, filepath):
        """Загрузить ансамбль с диска"""
        ensemble_data = joblib.load(filepath)
        
        self.models = ensemble_data['models']
        self.scaler = ensemble_data['scaler']
        self.feature_names = ensemble_data['feature_names']
        self.model_weights = ensemble_data['weights']
        
        print(f"✅ Ансамбль загружен: {filepath}")
        print(f"   Моделей: {len(self.models)}")
        print(f"   Признаков: {len(self.feature_names)}")


def main():
    """Главная функция для обучения"""
    print("="*70)
    print("🎯 ОБУЧЕНИЕ АНСАМБЛЯ МОДЕЛЕЙ GOALPREDICTOR.AI")
    print("="*70)
    
    # Загрузить данные
    print("\n📁 Загрузка данных...")
    df = pd.read_csv('data/processed/enhanced_features.csv')
    print(f"✅ Загружено {len(df)} образцов с {len(df.columns)} признаками")
    
    # Создать и обучить ансамбль
    ensemble = EnsembleGoalPredictor()
    results = ensemble.train_ensemble(df, target_column='over_2_5')
    
    # Сохранить
    ensemble.save_ensemble()
    
    print("\n✅ Обучение завершено успешно!")


if __name__ == '__main__':
    main()
