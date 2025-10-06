"""
Скрипт для инициализации базы данных
"""
from app import create_app
from extensions import db
from models import User, Subscription, Match

def init_database():
    """Инициализация базы данных"""
    app = create_app()
    
    with app.app_context():
        print("🔄 Создание таблиц базы данных...")
        
        # Создаем все таблицы
        db.create_all()
        
        print("✅ Таблицы созданы успешно!")
        
        # Проверяем, есть ли администратор
        admin = User.query.filter_by(email='admin@goalpredictor.ai').first()
        
        if not admin:
            print("\n👤 Создание администратора...")
            admin = User(
                username='admin',
                email='admin@goalpredictor.ai',
                is_admin=True,
                is_premium=True,
                is_active=True
            )
            admin.set_password('admin123')
            db.session.add(admin)
            db.session.commit()
            print("✅ Администратор создан!")
            print("   📧 Email: admin@goalpredictor.ai")
            print("   🔑 Пароль: admin123")
        else:
            print("\n✅ Администратор уже существует")
            print("   📧 Email:", admin.email)
        
        # Статистика базы данных
        print("\n📊 Статистика базы данных:")
        print(f"   👥 Пользователей: {User.query.count()}")
        print(f"   💳 Подписок: {Subscription.query.count()}")
        print(f"   ⚽ Матчей: {Match.query.count()}")
        
        print("\n🎉 База данных готова к использованию!")

if __name__ == '__main__':
    init_database()
