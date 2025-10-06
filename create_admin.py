"""
Скрипт для создания первого администратора
"""
import sys
import os

# Добавить корневую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db
from models import User
from getpass import getpass


def create_admin():
    """Создать администратора"""
    app = create_app()
    
    with app.app_context():
        print("=" * 50)
        print("🔐 Создание администратора GoalPredictor.AI")
        print("=" * 50)
        print()
        
        # Ввод данных
        username = input("Введите имя пользователя: ").strip()
        if not username:
            print("❌ Имя пользователя не может быть пустым")
            return
        
        email = input("Введите email: ").strip()
        if not email:
            print("❌ Email не может быть пустым")
            return
        
        # Проверить существующих пользователей
        if User.query.filter_by(email=email).first():
            print(f"❌ Пользователь с email {email} уже существует")
            return
        
        if User.query.filter_by(username=username).first():
            print(f"❌ Пользователь с именем {username} уже существует")
            return
        
        password = getpass("Введите пароль: ")
        if not password or len(password) < 6:
            print("❌ Пароль должен содержать минимум 6 символов")
            return
        
        password_confirm = getpass("Подтвердите пароль: ")
        if password != password_confirm:
            print("❌ Пароли не совпадают")
            return
        
        try:
            # Создать администратора
            admin = User(
                username=username,
                email=email,
                is_admin=True,
                is_premium=True,
                is_active=True
            )
            admin.set_password(password)
            
            db.session.add(admin)
            db.session.commit()
            
            print()
            print("=" * 50)
            print("✅ Администратор успешно создан!")
            print("=" * 50)
            print(f"👤 Имя: {username}")
            print(f"📧 Email: {email}")
            print(f"🔑 Роль: Администратор")
            print()
            print("Теперь вы можете войти в админ-панель:")
            print("http://localhost:5000/login")
            print()
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка создания администратора: {e}")


if __name__ == '__main__':
    create_admin()
