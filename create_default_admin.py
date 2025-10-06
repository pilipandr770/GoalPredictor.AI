"""
Автоматическое создание администратора по умолчанию
Для использования на Render.com
"""
import sys
import os

# Добавить корневую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models import User


def create_default_admin():
    """Создать администратора по умолчанию"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔐 Создание администратора по умолчанию")
        print("=" * 60)
        print()
        
        # Данные администратора по умолчанию
        admin_email = 'admin@goalpredictor.ai'
        admin_username = 'admin'
        admin_password = 'Admin123!'  # ВАЖНО: Сменить после первого входа!
        
        try:
            # Проверить, существует ли уже админ
            existing_admin = User.query.filter_by(email=admin_email).first()
            
            if existing_admin:
                print("✓ Администратор уже существует")
                print(f"  Email: {existing_admin.email}")
                print(f"  Username: {existing_admin.username}")
                print()
                return
            
            # Создать нового администратора
            admin = User(
                username=admin_username,
                email=admin_email,
                is_admin=True,
                is_active=True
            )
            admin.set_password(admin_password)
            
            db.session.add(admin)
            db.session.commit()
            
            print("✅ Администратор успешно создан!")
            print()
            print("📋 Данные для входа:")
            print(f"   Email: {admin_email}")
            print(f"   Username: {admin_username}")
            print(f"   Password: {admin_password}")
            print()
            print("⚠️  ВАЖНО: Смените пароль после первого входа!")
            print()
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка создания администратора: {e}")
            import traceback
            traceback.print_exc()
        
        print("=" * 60)


if __name__ == '__main__':
    create_default_admin()
