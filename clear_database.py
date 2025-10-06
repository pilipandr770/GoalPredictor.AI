"""
Очистка БД и загрузка свежих исторических данных
"""
from extensions import db
from app import create_app
from models import Team, Match, Prediction

app = create_app()

with app.app_context():
    print("🗑️  Очистка базы данных...")
    
    # Удалить все прогнозы
    pred_count = Prediction.query.delete()
    print(f"   ✅ Удалено прогнозов: {pred_count}")
    
    # Удалить все матчи
    match_count = Match.query.delete()
    print(f"   ✅ Удалено матчей: {match_count}")
    
    # Удалить все команды
    team_count = Team.query.delete()
    print(f"   ✅ Удалено команд: {team_count}")
    
    db.session.commit()
    
    print("\n✅ База данных очищена!")
    print("   Теперь запустите: py load_real_historical_data.py")
