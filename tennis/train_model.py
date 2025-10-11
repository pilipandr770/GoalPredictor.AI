"""
Tennis ML Model Training
Binary classification: player1 win prediction
"""
import pandas as pd
import numpy as np
import pickle
import json
from pathlib import Path
from datetime import datetime
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, average_precision_score, brier_score_loss
)
import warnings
warnings.filterwarnings('ignore')


class TennisModelTrainer:
    """Train tennis prediction models"""
    
    # Non-feature columns
    NON_FEATURES = [
        'match_id', 'date', 'surface', 'tourney_name', 'tourney_level',
        'player1_win'  # TARGET
    ]
    
    def __init__(self, data_path='tennis/data/tennis_training_data.csv'):
        self.data_path = data_path
        self.df = None
        self.model = None
        self.feature_columns = []
        self.results = {}
        
    def load_data(self):
        """Load training data"""
        print("=" * 70)
        print("📂 ЗАВАНТАЖЕННЯ ДАНИХ")
        print("=" * 70)
        print()
        
        self.df = pd.read_csv(self.data_path)
        print(f"✓ Завантажено: {len(self.df)} записів")
        
        # Конвертувати дату
        self.df['date'] = pd.to_datetime(self.df['date'])
        self.df = self.df.sort_values('date').reset_index(drop=True)
        
        print(f"✓ Період: {self.df['date'].min()} до {self.df['date'].max()}")
        print()
        
    def prepare_features(self):
        """Prepare feature columns"""
        print("=" * 70)
        print("🔧 ПІДГОТОВКА ФІЧ")
        print("=" * 70)
        print()
        
        # Feature columns = все крім NON_FEATURES
        self.feature_columns = [
            col for col in self.df.columns 
            if col not in self.NON_FEATURES
        ]
        
        print(f"✓ Фічів: {len(self.feature_columns)}")
        print(f"  {self.feature_columns}")
        print()
        
    def temporal_split(self, test_size=0.2):
        """
        Temporal split: train on old matches, test on new
        """
        print("=" * 70)
        print("⏰ ЧАСОВИЙ СПЛІТ")
        print("=" * 70)
        print()
        
        split_index = int(len(self.df) * (1 - test_size))
        
        train_df = self.df.iloc[:split_index]
        test_df = self.df.iloc[split_index:]
        
        print(f"✓ Train: {len(train_df)} матчів ({train_df['date'].min().date()} до {train_df['date'].max().date()})")
        print(f"✓ Test:  {len(test_df)} матчів ({test_df['date'].min().date()} до {test_df['date'].max().date()})")
        print()
        
        return train_df, test_df
    
    def train_model(self):
        """Train calibrated model"""
        print("=" * 70)
        print("🤖 ТРЕНУВАННЯ МОДЕЛІ")
        print("=" * 70)
        print()
        
        # Split
        train_df, test_df = self.temporal_split(test_size=0.2)
        
        # Features
        X_train = train_df[self.feature_columns].fillna(0)
        y_train = train_df['player1_win']
        
        X_test = test_df[self.feature_columns].fillna(0)
        y_test = test_df['player1_win']
        
        print(f"  Target distribution:")
        print(f"    Train: {y_train.mean():.1%} player1 wins")
        print(f"    Test:  {y_test.mean():.1%} player1 wins")
        print()
        
        # Base model
        print("  🔧 Тренування RandomForest...")
        base_model = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=20,
            min_samples_leaf=10,
            random_state=42,
            n_jobs=-1
        )
        base_model.fit(X_train, y_train)
        
        # Calibration
        print("  🔧 Калібрація (Platt scaling)...")
        self.model = CalibratedClassifierCV(
            base_model,
            method='sigmoid',
            cv=3
        )
        self.model.fit(X_train, y_train)
        
        # Predictions
        train_pred = self.model.predict(X_train)
        test_pred = self.model.predict(X_test)
        
        train_proba = self.model.predict_proba(X_train)[:, 1]
        test_proba = self.model.predict_proba(X_test)[:, 1]
        
        # Metrics
        results = {
            'accuracy_train': accuracy_score(y_train, train_pred),
            'accuracy_test': accuracy_score(y_test, test_pred),
            'roc_auc_train': roc_auc_score(y_train, train_proba),
            'roc_auc_test': roc_auc_score(y_test, test_proba),
            'brier_train': brier_score_loss(y_train, train_proba),
            'brier_test': brier_score_loss(y_test, test_proba),
            'pr_auc_train': average_precision_score(y_train, train_proba),
            'pr_auc_test': average_precision_score(y_test, test_proba),
            'precision': precision_score(y_test, test_pred),
            'recall': recall_score(y_test, test_pred),
            'f1': f1_score(y_test, test_pred)
        }
        
        self.results = results
        
        print()
        print("  📊 РЕЗУЛЬТАТИ:")
        print(f"    Accuracy:  Train {results['accuracy_train']:.1%}, Test {results['accuracy_test']:.1%}")
        print(f"    ROC-AUC:   Train {results['roc_auc_train']:.3f}, Test {results['roc_auc_test']:.3f}")
        print(f"    Brier:     Train {results['brier_train']:.3f}, Test {results['brier_test']:.3f}")
        print(f"    Precision: {results['precision']:.1%}")
        print(f"    Recall:    {results['recall']:.1%}")
        print(f"    F1:        {results['f1']:.3f}")
        print()
        
        # Feature importance
        if hasattr(base_model, 'feature_importances_'):
            importances = base_model.feature_importances_
            feature_importance = sorted(
                zip(self.feature_columns, importances),
                key=lambda x: x[1],
                reverse=True
            )
            
            print("  🎯 TOP-10 ВАЖЛИВИХ ФІЧ:")
            for feat, imp in feature_importance[:10]:
                print(f"    • {feat:30s}: {imp:.4f}")
            print()
        
        return results
    
    def save_model(self):
        """Save model and metadata"""
        print("=" * 70)
        print("💾 ЗБЕРЕЖЕННЯ МОДЕЛІ")
        print("=" * 70)
        print()
        
        models_dir = Path('tennis/models')
        models_dir.mkdir(exist_ok=True, parents=True)
        
        # Save model (protocol=4 for compatibility with older sklearn)
        model_path = models_dir / 'tennis_player1_win_model.pkl'
        with open(model_path, 'wb') as f:
            pickle.dump(self.model, f, protocol=4)
        print(f"  ✓ {model_path}")
        
        # Save feature columns
        feature_path = models_dir / 'tennis_feature_columns.pkl'
        with open(feature_path, 'wb') as f:
            pickle.dump(self.feature_columns, f, protocol=4)
        print(f"  ✓ {feature_path}")
        
        # Save metadata
        metadata = {
            'trained_at': datetime.now().isoformat(),
            'train_samples': len(self.df),
            'feature_count': len(self.feature_columns),
            'features': self.feature_columns,
            'metrics': {k: float(v) for k, v in self.results.items()},
            'version': 'v1.0_temporal_calibrated'
        }
        metadata_path = models_dir / 'tennis_model_metadata.json'
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
        print(f"  ✓ {metadata_path}")
        
        # Save report
        report_path = models_dir / 'tennis_training_report.csv'
        df_report = pd.DataFrame([{
            'Model': 'RandomForest_Calibrated',
            'Accuracy_Train': f"{self.results['accuracy_train']:.1%}",
            'Accuracy_Test': f"{self.results['accuracy_test']:.1%}",
            'ROC_AUC_Test': f"{self.results['roc_auc_test']:.3f}",
            'Brier_Test': f"{self.results['brier_test']:.3f}",
            'Precision': f"{self.results['precision']:.1%}",
            'Recall': f"{self.results['recall']:.1%}",
            'F1': f"{self.results['f1']:.3f}"
        }])
        df_report.to_csv(report_path, index=False)
        print(f"  ✓ {report_path}")
        print()
        
    def run(self):
        """Full training pipeline"""
        print()
        print("=" * 70)
        print("🎾 ТРЕНУВАННЯ TENNIS ML МОДЕЛІ")
        print("=" * 70)
        print()
        
        # 1. Load
        self.load_data()
        
        # 2. Prepare features
        self.prepare_features()
        
        # 3. Train
        self.train_model()
        
        # 4. Save
        self.save_model()
        
        print("=" * 70)
        print("✅ ТРЕНУВАННЯ ЗАВЕРШЕНО")
        print("=" * 70)
        print()
        print("ІНТЕРПРЕТАЦІЯ:")
        auc = self.results['roc_auc_test']
        if auc >= 0.75:
            quality = "🏆 ВІДМІННА"
        elif auc >= 0.70:
            quality = "✅ ХОРОША"
        elif auc >= 0.65:
            quality = "👍 ЗАДОВІЛЬНА"
        else:
            quality = "⚠️  СЛАБКА"
        
        print(f"  Якість моделі: {quality}")
        print(f"  ROC-AUC: {auc:.3f}")
        print()
        print("ПОРІВНЯННЯ З ФУТБОЛОМ:")
        print("  Football over_2.5: AUC 0.522 (слабка)")
        print("  Football away_win:  AUC 0.685 (хороша)")
        print(f"  Tennis player_win:  AUC {auc:.3f}")
        print()
        
        if auc > 0.68:
            print("  ✅ Теніс ЛЕГШЕ прогнозувати ніж футбол!")
        print()


def main():
    trainer = TennisModelTrainer()
    trainer.run()


if __name__ == '__main__':
    main()
