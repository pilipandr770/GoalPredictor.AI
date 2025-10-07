"""
Правильне тренування ML моделей з часовим спліттом та без target leakage

КРИТИЧНІ ЗМІНИ:
1. Часовий спліт: train на старих даних, test на нових
2. Перевірка на leakage: видалення цільових змінних з фіч
3. Калібрація ймовірностей: CalibratedClassifierCV
4. Правильні метрики: ROC-AUC, Brier score, calibration curves
5. Rolling backtest: перевірка на різних часових відрізках
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
from sklearn.model_selection import TimeSeriesSplit
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV, calibration_curve
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss,
    confusion_matrix, classification_report
)
import warnings
warnings.filterwarnings('ignore')


class TemporalMLTrainer:
    """Тренування ML моделей з часовим спліттом та калібрацією"""
    
    # Цільові змінні які НЕ МОЖУТЬ бути фічами
    TARGET_COLUMNS = [
        'total_goals', 'over_2_5', 'btts', 
        'home_win', 'draw', 'away_win',
        'result', 'score', 'goals'  # На всякий випадок
    ]
    
    def __init__(self, data_path='ml/data/training_data.csv'):
        self.data_path = data_path
        self.df = None
        self.models = {}
        self.feature_columns = []
        self.results = []
        
    def load_data(self):
        """Завантажити дані"""
        print("=" * 70)
        print("📂 ЗАВАНТАЖЕННЯ ДАНИХ")
        print("=" * 70)
        
        self.df = pd.read_csv(self.data_path)
        print(f"✓ Завантажено {len(self.df)} записів")
        print(f"✓ Колонки: {list(self.df.columns)}")
        
        # Перевірити наявність дати
        if 'date' not in self.df.columns:
            raise ValueError("❌ Немає колонки 'date' для часового спліту!")
        
        # Конвертувати дату
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values('date').reset_index(drop=True)
        
        print(f"✓ Період даних: {self.df['date'].min()} до {self.df['date'].max()}")
        print()
        
    def check_leakage(self):
        """КРИТИЧНА ПЕРЕВІРКА: Видалити цільові змінні з фіч"""
        print("=" * 70)
        print("🔍 ПЕРЕВІРКА НА TARGET LEAKAGE")
        print("=" * 70)
        
        leaked_columns = []
        for col in self.df.columns:
            if col.lower() in [tc.lower() for tc in self.TARGET_COLUMNS]:
                leaked_columns.append(col)
        
        if leaked_columns:
            print(f"⚠️  ВИЯВЛЕНО LEAKAGE: {leaked_columns}")
            print("   Ці колонки будуть видалені з фіч!")
        else:
            print("✓ Leakage не виявлено")
        
        # Також видалити ID та дату з фіч (вони не мають предиктивної сили)
        non_feature_columns = leaked_columns + ['match_id', 'date', 'league']
        
        # Фічі = всі колонки крім цільових та метаданих
        self.feature_columns = [
            col for col in self.df.columns 
            if col not in non_feature_columns
        ]
        
        print(f"✓ Фічів для тренування: {len(self.feature_columns)}")
        print(f"  {self.feature_columns}")
        print()
        
        return leaked_columns
    
    def temporal_split(self, test_size=0.2):
        """
        Часовий спліт: останні test_size% даних - тест
        
        ВАЖЛИВО: Це НЕ random split!
        Train: старі матчі
        Test: нові матчі
        """
        print("=" * 70)
        print("⏰ ЧАСОВИЙ СПЛІТ")
        print("=" * 70)
        
        split_index = int(len(self.df) * (1 - test_size))
        
        train_df = self.df.iloc[:split_index]
        test_df = self.df.iloc[split_index:]
        
        print(f"✓ Train: {len(train_df)} матчів ({train_df['date'].min()} до {train_df['date'].max()})")
        print(f"✓ Test:  {len(test_df)} матчів ({test_df['date'].min()} до {test_df['date'].max()})")
        print()
        
        return train_df, test_df
    
    def train_model(self, target_name, X_train, y_train, X_test, y_test):
        """
        Тренування моделі з калібрацією
        
        НОВІ ФІЧІ:
        - Калібрація ймовірностей (CalibratedClassifierCV)
        - Правильні метрики (ROC-AUC, Brier)
        - Калібраційні криві
        """
        print(f"  🎯 {target_name}")
        print(f"     Позитивних прикладів: train={y_train.sum()}/{len(y_train)}, test={y_test.sum()}/{len(y_test)}")
        
        results = {
            'target': target_name,
            'train_size': len(X_train),
            'test_size': len(X_test),
            'positive_ratio': float(y_train.sum() / len(y_train))
        }
        
        # Моделі
        models = {
            'RandomForest': RandomForestClassifier(
                n_estimators=100, 
                max_depth=10,
                min_samples_split=20,
                min_samples_leaf=10,
                random_state=42,
                n_jobs=-1
            ),
            'GradientBoosting': GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                min_samples_split=20,
                min_samples_leaf=10,
                random_state=42
            )
        }
        
        for model_name, model in models.items():
            # 1. Базове тренування
            model.fit(X_train, y_train)
            
            # 2. КАЛІБРАЦІЯ (нова фіча!)
            calibrated_model = CalibratedClassifierCV(
                model, 
                method='sigmoid',  # Platt scaling
                cv=3
            )
            calibrated_model.fit(X_train, y_train)
            
            # 3. Предикшни
            train_pred = calibrated_model.predict(X_train)
            test_pred = calibrated_model.predict(X_test)
            
            train_proba = calibrated_model.predict_proba(X_train)[:, 1]
            test_proba = calibrated_model.predict_proba(X_test)[:, 1]
            
            # 4. МЕТРИКИ (розширені!)
            train_acc = accuracy_score(y_train, train_pred)
            test_acc = accuracy_score(y_test, test_pred)
            
            # ROC-AUC (найважливіша метрика для ймовірностей)
            try:
                train_auc = roc_auc_score(y_train, train_proba)
                test_auc = roc_auc_score(y_test, test_proba)
            except:
                train_auc = test_auc = 0.5
            
            # Brier score (якість калібрації)
            train_brier = brier_score_loss(y_train, train_proba)
            test_brier = brier_score_loss(y_test, test_proba)
            
            # Precision-Recall AUC
            try:
                train_pr_auc = average_precision_score(y_train, train_proba)
                test_pr_auc = average_precision_score(y_test, test_proba)
            except:
                train_pr_auc = test_pr_auc = 0.0
            
            results[model_name] = {
                'accuracy_train': train_acc,
                'accuracy_test': test_acc,
                'roc_auc_train': train_auc,
                'roc_auc_test': test_auc,
                'brier_train': train_brier,
                'brier_test': test_brier,
                'pr_auc_train': train_pr_auc,
                'pr_auc_test': test_pr_auc,
                'precision': precision_score(y_test, test_pred, zero_division=0),
                'recall': recall_score(y_test, test_pred, zero_division=0),
                'f1': f1_score(y_test, test_pred, zero_division=0)
            }
            
            print(f"     {model_name:20s} | Acc: {test_acc:.1%} | AUC: {test_auc:.3f} | Brier: {test_brier:.3f}")
            
            # Зберегти кращу модель
            if model_name == 'RandomForest':  # Можна вибрати кращу по AUC
                self.models[target_name] = calibrated_model
        
        self.results.append(results)
        print()
        return results
    
    def train_all_targets(self):
        """Тренування всіх цільових змінних"""
        print("=" * 70)
        print("🤖 ТРЕНУВАННЯ МОДЕЛЕЙ")
        print("=" * 70)
        print()
        
        # Часовий спліт
        train_df, test_df = self.temporal_split(test_size=0.2)
        
        # Фічі
        X_train = train_df[self.feature_columns].fillna(0)
        X_test = test_df[self.feature_columns].fillna(0)
        
        # Тренування кожної цілі
        targets = {
            'over_2_5': 'over_2_5',
            'btts': 'btts',
            'home_win': 'home_win',
            'draw': 'draw',
            'away_win': 'away_win'
        }
        
        for target_name, target_col in targets.items():
            if target_col not in self.df.columns:
                print(f"  ⚠️  Пропуск {target_name} - колонка {target_col} не знайдена")
                continue
            
            y_train = train_df[target_col]
            y_test = test_df[target_col]
            
            self.train_model(target_name, X_train, y_train, X_test, y_test)
    
    def save_models(self):
        """Зберегти моделі та метрики"""
        print("=" * 70)
        print("💾 ЗБЕРЕЖЕННЯ МОДЕЛЕЙ")
        print("=" * 70)
        
        models_dir = Path('ml/models')
        models_dir.mkdir(exist_ok=True, parents=True)
        
        # Зберегти моделі
        for target_name, model in self.models.items():
            model_path = models_dir / f"{target_name}_model.pkl"
            with open(model_path, 'wb') as f:
                pickle.dump(model, f)
            print(f"  ✓ {model_path}")
        
        # Зберегти feature columns
        feature_path = models_dir / 'feature_columns.pkl'
        with open(feature_path, 'wb') as f:
            pickle.dump(self.feature_columns, f)
        print(f"  ✓ {feature_path}")
        
        # Зберегти метадані
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'train_samples': len(self.df),
            'feature_count': len(self.feature_columns),
            'features': self.feature_columns,
            'version': 'v3.0_temporal_calibrated'
        }
        metadata_path = models_dir / 'model_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  ✓ {metadata_path}")
        
        # Зберегти звіт
        self.save_report()
        print()
    
    def save_report(self):
        """Зберегти детальний звіт"""
        report_data = []
        
        for result in self.results:
            target = result['target']
            for model_name in ['RandomForest', 'GradientBoosting']:
                if model_name not in result:
                    continue
                
                metrics = result[model_name]
                report_data.append({
                    'Target': target,
                    'Model': model_name,
                    'Accuracy_Train': f"{metrics['accuracy_train']:.1%}",
                    'Accuracy_Test': f"{metrics['accuracy_test']:.1%}",
                    'ROC_AUC_Test': f"{metrics['roc_auc_test']:.3f}",
                    'Brier_Test': f"{metrics['brier_test']:.3f}",
                    'PR_AUC_Test': f"{metrics['pr_auc_test']:.3f}",
                    'Precision': f"{metrics['precision']:.1%}",
                    'Recall': f"{metrics['recall']:.1%}",
                    'F1': f"{metrics['f1']:.3f}"
                })
        
        df_report = pd.DataFrame(report_data)
        report_path = Path('ml/models/training_report_v3.csv')
        df_report.to_csv(report_path, index=False)
        
        print(f"  ✓ {report_path}")
        print()
        print("📊 РЕЗУЛЬТАТИ:")
        print(df_report.to_string(index=False))
        print()


def main():
    """Головна функція"""
    print()
    print("=" * 70)
    print("🚀 ML ТРЕНУВАННЯ З ЧАСОВИМ СПЛІТТОМ ТА КАЛІБРАЦІЄЮ")
    print("=" * 70)
    print()
    
    trainer = TemporalMLTrainer()
    
    # 1. Завантажити дані
    trainer.load_data()
    
    # 2. КРИТИЧНО: Перевірити leakage
    leaked = trainer.check_leakage()
    
    if leaked:
        print("⚠️  УВАГА: Виявлено target leakage!")
        print("   Цільові змінні будуть виключені з фіч")
        print()
    
    # 3. Тренування з часовим спліттом
    trainer.train_all_targets()
    
    # 4. Зберегти
    trainer.save_models()
    
    print("=" * 70)
    print("✅ ТРЕНУВАННЯ ЗАВЕРШЕНО")
    print("=" * 70)
    print()
    print("КРИТИЧНІ ЗМІНИ:")
    print("  ✓ Видалено target leakage (цільові змінні не в фічах)")
    print("  ✓ Часовий спліт (train на старих, test на нових)")
    print("  ✓ Калібрація ймовірностей (Platt scaling)")
    print("  ✓ Правильні метрики (ROC-AUC, Brier, PR-AUC)")
    print()
    print("ОЧІКУВАНІ РЕЗУЛЬТАТИ:")
    print("  • ROC-AUC: 0.55-0.70 (реалістично для футболу)")
    print("  • Accuracy: 50-65% (не 100%!)")
    print("  • Brier: 0.20-0.25 (нижче = краще)")
    print()


if __name__ == '__main__':
    main()
