"""
Скрипт для обновления схемы базы данных PostgreSQL
Добавляет недостающие колонки в таблицу users
Использует прямое подключение к PostgreSQL без Flask
"""
import os
import psycopg2
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()


def update_database_schema():
    """Обновить схему базы данных"""
    print("=" * 60)
    print("🔧 Обновление схемы базы данных GoalPredictor.AI")
    print("=" * 60)
    print()
    
    # Получить DATABASE_URL из переменных окружения
    database_url = os.getenv('DATABASE_URL')
    schema = os.getenv('DATABASE_SCHEMA', 'goalpredictor')
    
    if not database_url:
        print("❌ DATABASE_URL не найден в переменных окружения")
        return
    
    print(f"📊 Схема: {schema}")
    print(f"� Подключение к базе данных...")
    
    try:
        # Подключение к PostgreSQL
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Устанавливаем search_path
        cursor.execute(f"SET search_path TO {schema}")
        print(f"✅ Установлен search_path: {schema}")
        
        # Проверяем, есть ли колонка is_premium
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = %s
            AND table_name = 'users' 
            AND column_name = 'is_premium'
        """, (schema,))
        
        result = cursor.fetchone()
        
        if result is None:
            print("📝 Добавляем колонку is_premium...")
            cursor.execute(f"""
                ALTER TABLE {schema}.users 
                ADD COLUMN is_premium BOOLEAN DEFAULT FALSE
            """)
            print("✅ Колонка is_premium добавлена")
        else:
            print("✓ Колонка is_premium уже существует")
        
        cursor.close()
        conn.close()
        
        print()
        print("=" * 60)
        print("✅ Схема базы данных успешно обновлена!")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Ошибка при обновлении схемы: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    update_database_schema()
