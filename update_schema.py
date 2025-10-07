"""
Скрипт для обновления схемы базы данных PostgreSQL
Добавляет недостающие колонки в таблицу users
Использует прямое подключение к PostgreSQL без Flask
"""
import os
import sys
import psycopg2

# Загружаем dotenv только если запускается локально
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # На Render dotenv может не быть установлен до requirements.txt


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
        print("📋 Доступные переменные окружения:")
        for key in os.environ.keys():
            if 'DATA' in key or 'SCHEMA' in key:
                print(f"   {key} = {os.environ[key][:50]}...")
        return
    
    print(f"📊 Схема: {schema}")
    print(f"🔗 Подключение к базе данных...")
    print(f"📍 URL: {database_url[:50]}...")
    
    try:
        # Подключение к PostgreSQL
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        print("✅ Подключение установлено")
        
        # Устанавливаем search_path
        cursor.execute(f"SET search_path TO {schema}")
        print(f"✅ Установлен search_path: {schema}")
        
        # Проверяем текущие колонки в таблице users
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = %s
            AND table_name = 'users'
            ORDER BY ordinal_position
        """, (schema,))
        
        existing_columns = [row[0] for row in cursor.fetchall()]
        print(f"📋 Существующие колонки в users: {', '.join(existing_columns)}")
        
        # Проверяем, есть ли колонка is_premium
        if 'is_premium' in existing_columns:
            print("✓ Колонка is_premium уже существует")
        else:
            print("📝 Добавляем колонку is_premium...")
            cursor.execute(f"""
                ALTER TABLE {schema}.users 
                ADD COLUMN is_premium BOOLEAN DEFAULT FALSE
            """)
            print("✅ Колонка is_premium добавлена")
            
            # Проверяем результат
            cursor.execute("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_schema = %s
                AND table_name = 'users' 
                AND column_name = 'is_premium'
            """, (schema,))
            
            if cursor.fetchone():
                print("✅ Проверка: колонка is_premium успешно создана")
            else:
                print("⚠️  Предупреждение: колонка не найдена после создания!")
        
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
