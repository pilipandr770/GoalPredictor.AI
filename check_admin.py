"""
Проверка администратора в базе данных
"""
import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from models import User

app = create_app()

with app.app_context():
    print("=" * 60)
    print("🔍 Проверка администратора")
    print("=" * 60)
    print()
    
    # Найти админа
    admin = User.query.filter_by(email='admin@goalpredictor.ai').first()
    
    if not admin:
        print("❌ Администратор не найден!")
        print()
        sys.exit(1)
    
    print("✅ Администратор найден!")
    print()
    print(f"ID: {admin.id}")
    print(f"Email: {admin.email}")
    print(f"Username: {admin.username}")
    print(f"is_admin: {admin.is_admin}")
    print(f"is_premium: {admin.is_premium}")
    print(f"is_active: {admin.is_active}")
    print(f"password_hash: {admin.password_hash[:50]}...")
    print()
    
    # Проверить пароль
    test_password = 'Admin123!'
    password_valid = admin.check_password(test_password)
    
    print(f"🔐 Проверка пароля '{test_password}': {'✅ OK' if password_valid else '❌ FAILED'}")
    print()
    
    if not password_valid:
        print("⚠️  Пароль не совпадает! Сбрасываем пароль...")
        admin.set_password(test_password)
        from extensions import db
        db.session.commit()
        print("✅ Пароль сброшен на: Admin123!")
        print()
    
    print("=" * 60)
