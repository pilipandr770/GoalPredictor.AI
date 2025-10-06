import os
import sys
import pandas as pd
import joblib
from extensions import db
from app import create_app
from models import Match, Prediction, Team
from datetime import datetime
from sqlalchemy import and_

app = create_app()

def load_models():
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
    else:
        feature_columns = None
    return models, feature_columns

def calculate_recent_stats(team_id, limit=5):
    finished_matches = Match.query.filter(
        and_(
            Match.home_goals.isnot(None),
            Match.away_goals.isnot(None)
        )
    ).filter(
        (Match.home_team_id == team_id) | (Match.away_team_id == team_id)
    ).order_by(Match.match_date.desc()).limit(limit).all()
    if not finished_matches:
        return 0, 0, 0, 0, 0, 0, 0.0, len(finished_matches), 0
    wins = draws = losses = 0
    goals_for = goals_against = 0
    for match in finished_matches:
        if match.home_team_id == team_id:
            gf = match.home_goals
            ga = match.away_goals
        else:
            gf = match.away_goals
            ga = match.home_goals
        goals_for += gf
        goals_against += ga
        if gf > ga:
            wins += 1
        elif gf == ga:
            draws += 1
        else:
            losses += 1
    form_points = wins * 3 + draws
    avg_goals = goals_for / len(finished_matches)
    total_goals = goals_for + goals_against
    return wins, draws, losses, goals_for, goals_against, form_points, avg_goals, len(finished_matches), total_goals

def calculate_h2h(home_id, away_id, limit=3):
    h2h_matches = Match.query.filter(
        and_(
            Match.home_goals.isnot(None),
            Match.away_goals.isnot(None),
            Match.home_team_id == home_id,
            Match.away_team_id == away_id
        )
    ).order_by(Match.match_date.desc()).limit(limit).all()
    if not h2h_matches:
        return 0, 0, 0
    hw = d = aw = 0
    for match in h2h_matches:
        if match.home_goals > match.away_goals:
            hw += 1
        elif match.home_goals == match.away_goals:
            d += 1
        else:
            aw += 1
    return hw, d, aw

def extract_features(match):
    hw, hd, hl, hgf, hga, hfp, hag, htm, htg = calculate_recent_stats(match.home_team_id)
    aw, ad, al, agf, aga, afp, aag, atm, atg = calculate_recent_stats(match.away_team_id)
    h2h_hw, h2h_d, h2h_aw = calculate_h2h(match.home_team_id, match.away_team_id)
    features = {
        "home_recent_wins": hw,
        "home_recent_draws": hd,
        "home_recent_losses": hl,
        "home_recent_goals_for": hgf,
        "home_recent_goals_against": hga,
        "home_recent_form_points": hfp,
        "away_recent_wins": aw,
        "away_recent_draws": ad,
        "away_recent_losses": al,
        "away_recent_goals_for": agf,
        "away_recent_goals_against": aga,
        "away_recent_form_points": afp,
        "h2h_home_wins": h2h_hw,
        "h2h_draws": h2h_d,
        "h2h_away_wins": h2h_aw,
        "home_avg_goals": hag,
        "home_total_matches": htm,
        "away_avg_goals": aag,
        "away_total_matches": atm,
        "total_goals": htg + atg
    }
    return features

def generate_predictions():
    print("="*70)
    print("GENERATING PREDICTIONS")
    print("="*70)
    print("\nLoading models...")
    models, feature_columns = load_models()
    if not models:
        print("ERROR: No models found!")
        return
    print(f"Loaded {len(models)} models")
    with app.app_context():
        future_matches = Match.query.filter(
            and_(
                Match.home_goals.is_(None),
                Match.away_goals.is_(None)
            )
        ).all()
        if not future_matches:
            print("\nNo future matches found!")
            print("All matches in database have scores.")
            return
        print(f"\nFound {len(future_matches)} future matches")
        print("\nGenerating predictions...")
        generated = 0
        errors = 0
        for match in future_matches:
            try:
                home_name = match.home_team.name if match.home_team else "Unknown"
                away_name = match.away_team.name if match.away_team else "Unknown"
                print(f"\n  {home_name} vs {away_name}")
                features = extract_features(match)
                X = pd.DataFrame([features])
                if feature_columns:
                    X = X[feature_columns]
                predictions = {}
                for target, model in models.items():
                    pred_proba = model.predict_proba(X)[0]
                    predictions[target] = pred_proba[1] * 100
                    print(f"    {target}: {pred_proba[1]*100:.1f}%")
                existing_pred = Prediction.query.filter_by(match_id=match.id).first()
                if existing_pred:
                    existing_pred.over_2_5 = predictions.get("over_2_5", 50.0)
                    existing_pred.btts = predictions.get("btts", 50.0)
                    existing_pred.home_win = predictions.get("home_win", 33.3)
                    existing_pred.draw = predictions.get("draw", 33.3)
                    existing_pred.away_win = predictions.get("away_win", 33.3)
                    existing_pred.confidence = max(predictions.values())
                    existing_pred.model_version = "v2.0"
                else:
                    new_pred = Prediction(
                        match_id=match.id,
                        over_2_5=predictions.get("over_2_5", 50.0),
                        btts=predictions.get("btts", 50.0),
                        home_win=predictions.get("home_win", 33.3),
                        draw=predictions.get("draw", 33.3),
                        away_win=predictions.get("away_win", 33.3),
                        confidence=max(predictions.values()),
                        model_version="v2.0"
                    )
                    db.session.add(new_pred)
                db.session.commit()
                generated += 1
            except Exception as e:
                print(f"    ERROR: {str(e)}")
                import traceback
                traceback.print_exc()
                errors += 1
                db.session.rollback()
        print("\n" + "="*70)
        print(f"Generated: {generated} predictions")
        if errors > 0:
            print(f"Errors: {errors}")
        print("="*70)

if __name__ == "__main__":
    generate_predictions()
