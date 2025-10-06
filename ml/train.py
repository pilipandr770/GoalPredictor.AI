import os
import sys
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib
import warnings
warnings.filterwarnings("ignore")

def load_prepared_data(data_path):
    print(f"Loading data: {data_path}")
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"File not found: {data_path}")
    df = pd.read_csv(data_path)
    print(f"Loaded {len(df)} samples with {len(df.columns)} features")
    print("\nTarget statistics:")
    if "over_2_5" in df.columns:
        print(f"  Over 2.5: {df['over_2_5'].mean():.1%}")
    if "btts" in df.columns:
        print(f"  BTTS: {df['btts'].mean():.1%}")
    return df

def prepare_features_and_targets(df):
    print("\nPreparing features and targets...")
    target_columns = ["over_2_5", "btts", "home_win", "draw", "away_win"]
    feature_columns = [col for col in df.columns if col not in target_columns + ["match_id", "date", "league"]]
    X = df[feature_columns]
    y = {}
    for target in target_columns:
        if target in df.columns:
            y[target] = df[target].astype(int)
    print(f"Features: {len(feature_columns)} columns")
    print(f"Targets: {list(y.keys())}")
    return X, y, feature_columns

def train_ensemble_models(X_train, X_test, y_train, y_test, target_name):
    print(f"\nTraining models for: {target_name}")
    print(f"  Train: {len(X_train)}, Test: {len(X_test)}")
    models = {
        "RandomForest": RandomForestClassifier(n_estimators=200, max_depth=15, min_samples_split=10, min_samples_leaf=5, random_state=42, n_jobs=-1),
        "GradientBoosting": GradientBoostingClassifier(n_estimators=150, max_depth=7, learning_rate=0.1, random_state=42)
    }
    results = {}
    best_model = None
    best_score = 0
    for model_name, model in models.items():
        print(f"  Training {model_name}...")
        model.fit(X_train, y_train)
        y_pred_train = model.predict(X_train)
        y_pred_test = model.predict(X_test)
        train_acc = accuracy_score(y_train, y_pred_train)
        test_acc = accuracy_score(y_test, y_pred_test)
        cv_scores = cross_val_score(model, X_train, y_train, cv=5, scoring="accuracy")
        cv_mean = cv_scores.mean()
        cv_std = cv_scores.std()
        results[model_name] = {"model": model, "train_acc": train_acc, "test_acc": test_acc, "cv_mean": cv_mean, "cv_std": cv_std, "y_pred_test": y_pred_test}
        print(f"    Train: {train_acc:.1%}, Test: {test_acc:.1%}, CV: {cv_mean:.1%} +/- {cv_std:.1%}")
        if cv_mean > best_score:
            best_score = cv_mean
            best_model = model_name
    print(f"  Best model: {best_model} (CV: {best_score:.1%})")
    best_result = results[best_model]
    print(f"\nClassification report ({best_model}):")
    print(classification_report(y_test, best_result["y_pred_test"], target_names=["No", "Yes"], zero_division=0))
    print("\nConfusion matrix:")
    print(confusion_matrix(y_test, best_result["y_pred_test"]))
    return best_result["model"], results

def train_all_models(data_path):
    print("="*70)
    print("TRAINING MODELS - GoalPredictor.AI")
    print("="*70)
    df = load_prepared_data(data_path)
    X, y_dict, feature_columns = prepare_features_and_targets(df)
    print("\nSplitting data (80/20)...")
    X_train, X_test = train_test_split(X, test_size=0.2, random_state=42)
    trained_models = {}
    all_results = {}
    for target_name, y in y_dict.items():
        print("\n" + "="*70)
        y_train, y_test = train_test_split(y, test_size=0.2, random_state=42)
        best_model, results = train_ensemble_models(X_train, X_test, y_train, y_test, target_name)
        trained_models[target_name] = best_model
        all_results[target_name] = results
    print("\n" + "="*70)
    print("Saving models...")
    models_dir = os.path.join(os.path.dirname(__file__), "models")
    os.makedirs(models_dir, exist_ok=True)
    for target_name, model in trained_models.items():
        model_path = os.path.join(models_dir, f"{target_name}_model.pkl")
        joblib.dump(model, model_path)
        print(f"  Saved: {target_name}")
    features_path = os.path.join(models_dir, "feature_columns.pkl")
    joblib.dump(feature_columns, features_path)
    print(f"  Saved features list")
    print("\n" + "="*70)
    print("SUMMARY REPORT")
    print("="*70)
    summary_data = []
    for target_name, results in all_results.items():
        for model_name, result in results.items():
            summary_data.append({"Target": target_name, "Model": model_name, "Train": f"{result['train_acc']:.1%}", "Test": f"{result['test_acc']:.1%}", "CV": f"{result['cv_mean']:.1%}", "Std": f"{result['cv_std']:.1%}"})
    summary_df = pd.DataFrame(summary_data)
    print(summary_df.to_string(index=False))
    report_path = os.path.join(models_dir, "training_report.csv")
    summary_df.to_csv(report_path, index=False)
    print(f"\nReport saved: {report_path}")
    print("\n" + "="*70)
    print("TRAINING COMPLETED!")
    print("="*70)
    return trained_models, all_results

if __name__ == "__main__":
    data_path = os.path.join("ml", "data", "training_data.csv")
    if not os.path.exists(data_path):
        print(f"Data file not found: {data_path}")
        print("\nRun prepare_training_data.py first!")
        sys.exit(1)
    train_all_models(data_path)
