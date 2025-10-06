"""
Скрипт для проверки текущего состояния прогнозов
"""
from extensions import db
from app import create_app
from models import Match, Prediction, Team
from datetime import datetime, timedelta

app = create_app()

with app.app_context():
    print("=" * 60)
    print("ПРОВЕРКА СОСТОЯНИЯ БАЗЫ ДАННЫХ")
    print("=" * 60)
    
    # Статистика по таблицам
    total_teams = Team.query.count()
    total_matches = Match.query.count()
    total_predictions = Prediction.query.count()
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"   Команды: {total_teams}")
    print(f"   Матчи: {total_matches}")
    print(f"   Прогнозы: {total_predictions}")
    
    # Последние матчи
    print(f"\n⚽ ПОСЛЕДНИЕ 5 МАТЧЕЙ:")
    recent_matches = Match.query.order_by(Match.match_date.desc()).limit(5).all()
    for m in recent_matches:
        home = m.home_team.name if m.home_team else "?"
        away = m.away_team.name if m.away_team else "?"
        date = m.match_date.strftime("%Y-%m-%d %H:%M") if m.match_date else "?"
        print(f"   {m.id}: {home} vs {away} - {date}")
    
    # Прогнозы
    print(f"\n🔮 ПОСЛЕДНИЕ 5 ПРОГНОЗОВ:")
    recent_predictions = Prediction.query.order_by(Prediction.created_at.desc()).limit(5).all()
    if recent_predictions:
        for p in recent_predictions:
            match = Match.query.get(p.match_id)
            if match:
                home = match.home_team.name if match.home_team else "?"
                away = match.away_team.name if match.away_team else "?"
                print(f"   {p.id}: {home} vs {away}")
                print(f"      Вероятность: {p.probability}%, Уверенность: {p.confidence}%")
                print(f"      Версия модели: {p.model_version}")
    else:
        print("   ❌ Прогнозы отсутствуют!")
    
    # Будущие матчи (на следующие 7 дней)
    today = datetime.now()
    week_later = today + timedelta(days=7)
    upcoming_matches = Match.query.filter(
        Match.match_date >= today,
        Match.match_date <= week_later
    ).order_by(Match.match_date).limit(10).all()
    
    print(f"\n📅 ПРЕДСТОЯЩИЕ МАТЧИ (следующие 7 дней):")
    if upcoming_matches:
        for m in upcoming_matches:
            home = m.home_team.name if m.home_team else "?"
            away = m.away_team.name if m.away_team else "?"
            date = m.match_date.strftime("%Y-%m-%d %H:%M") if m.match_date else "?"
            has_prediction = Prediction.query.filter_by(match_id=m.id).first() is not None
            status = "✅" if has_prediction else "❌"
            print(f"   {status} {m.id}: {home} vs {away} - {date}")
    else:
        print("   ❌ Нет предстоящих матчей в базе!")
    
    print("\n" + "=" * 60)
