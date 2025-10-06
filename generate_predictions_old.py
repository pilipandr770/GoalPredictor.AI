"""
Скрипт для генерации прогнозов на загруженные матчи
"""
from extensions import db
from app import create_app
from models import Match, Prediction
from ml.predict import PredictionService
from datetime import datetime

app = create_app()
prediction_service = PredictionService()

with app.app_context():
    print("=" * 60)
    print("ГЕНЕРАЦИЯ ПРОГНОЗОВ")
    print("=" * 60)
    
    # Получить все матчи без прогнозов
    matches_without_predictions = Match.query.filter(
        ~Match.predictions.any()
    ).limit(10).all()  # Ограничим первыми 10 для теста
    
    if not matches_without_predictions:
        print("\n⚠️ Все матчи уже имеют прогнозы или нет матчей в базе!")
    else:
        print(f"\n🔮 Создание прогнозов для {len(matches_without_predictions)} матчей...")
        
        generated = 0
        errors = 0
        
        for match in matches_without_predictions:
            try:
                home = match.home_team.name if match.home_team else "?"
                away = match.away_team.name if match.away_team else "?"
                
                print(f"\n   Матч: {home} vs {away}")
                
                # Подготовить данные для прогноза
                match_data = {
                    'home_team_id': match.home_team_id,
                    'away_team_id': match.away_team_id,
                    'home_team_name': home,
                    'away_team_name': away,
                    'league': match.league,
                    'date': match.match_date
                }
                
                # Создать прогноз
                prediction_data = prediction_service.predict_match(
                    match_data,
                    include_explanation=False  # Без AI объяснений для скорости
                )
                
                # Сохранить в БД
                prediction = Prediction(
                    match_id=match.id,
                    probability=prediction_data.get('probability', 50.0),
                    confidence=prediction_data.get('confidence', 50.0),
                    explanation=prediction_data.get('explanation'),
                    factors=str(prediction_data.get('features', {})),
                    model_version=prediction_data.get('model_version', 'unknown')
                )
                
                db.session.add(prediction)
                db.session.commit()
                
                print(f"   ✅ Прогноз: {prediction.probability}% (уверенность: {prediction.confidence}%)")
                generated += 1
                
            except Exception as e:
                print(f"   ❌ Ошибка: {str(e)}")
                errors += 1
                db.session.rollback()
        
        print(f"\n{'=' * 60}")
        print(f"✅ Прогнозов создано: {generated}")
        if errors > 0:
            print(f"❌ Ошибок: {errors}")
        print(f"{'=' * 60}")
