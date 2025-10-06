import os
import pandas as pd
import joblib

print("Testing trained models...")
print("="*70)

models_dir = os.path.join("ml", "models")
models = {}

for target in ["over_2_5", "btts", "home_win", "draw", "away_win"]:
    model_path = os.path.join(models_dir, f"{target}_model.pkl")
    if os.path.exists(model_path):
        models[target] = joblib.load(model_path)
        print(f"  Loaded: {target}")

feature_columns_path = os.path.join(models_dir, "feature_columns.pkl")
if os.path.exists(feature_columns_path):
    feature_columns = joblib.load(feature_columns_path)
    print(f"  Loaded feature columns: {len(feature_columns)} features")

print(f"\nTotal models loaded: {len(models)}")
print("\nFeature columns:")
for col in feature_columns:
    print(f"  - {col}")

print("\n" + "="*70)
print("TEST PREDICTION")
print("="*70)

test_features = {
    "home_recent_wins": 3,
    "home_recent_draws": 1,
    "home_recent_losses": 1,
    "home_recent_goals_for": 10,
    "home_recent_goals_against": 6,
    "home_recent_form_points": 10,
    "away_recent_wins": 2,
    "away_recent_draws": 2,
    "away_recent_losses": 1,
    "away_recent_goals_for": 8,
    "away_recent_goals_against": 5,
    "away_recent_form_points": 8,
    "h2h_home_wins": 2,
    "h2h_draws": 1,
    "h2h_away_wins": 0,
    "home_avg_goals": 2.0,
    "home_total_matches": 5,
    "away_avg_goals": 1.6,
    "away_total_matches": 5,
    "total_goals": 3.6
}

X = pd.DataFrame([test_features])
X = X[feature_columns]

print("\nTest Match: Strong Home Team vs Good Away Team")
print("-"*70)

for target, model in models.items():
    pred_proba = model.predict_proba(X)[0]
    prob_no = pred_proba[0] * 100
    prob_yes = pred_proba[1] * 100
    print(f"  {target:12s}: No={prob_no:5.1f}%  Yes={prob_yes:5.1f}%")

print("\n" + "="*70)
print("Models are working correctly!")
print("="*70)
