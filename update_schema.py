"""
Скрипт для обновления схемы базы данных PostgreSQL
Добавляет недостающие колонки в таблицу users
"""
import os
import sys
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Добавить корневую директорию в путь
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
from extensions import db

def update_database_schema():
    """Обновить схему базы данных"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("🔧 Обновление схемы базы данных GoalPredictor.AI")
        print("=" * 60)
        print()
        
        try:
            # Проверяем, есть ли колонка is_premium
            result = db.session.execute(db.text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = 'goalpredictor' 
                AND table_name = 'users' 
                AND column_name = 'is_premium'
            """))
            
            if result.fetchone() is None:
                print("📝 Добавляем колонку is_premium...")
                db.session.execute(db.text("""
                    ALTER TABLE goalpredictor.users 
                    ADD COLUMN is_premium BOOLEAN DEFAULT FALSE
                """))
                db.session.commit()
                print("✅ Колонка is_premium добавлена")
            else:
                print("✓ Колонка is_premium уже существует")
            
            print()
            print("=" * 60)
            print("✅ Схема базы данных успешно обновлена!")
            print("=" * 60)
            
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при обновлении схемы: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    update_database_schema()
