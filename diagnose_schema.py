"""
Диагностика: В какой схеме находятся таблицы?
"""
import os
import psycopg2

database_url = os.getenv('DATABASE_URL')
schema = os.getenv('DATABASE_SCHEMA', 'goalpredictor')

print("=" * 60)
print("🔍 Диагностика схемы базы данных")
print("=" * 60)
print(f"\nЦелевая схема: {schema}")
print("\n📋 Поиск таблицы 'users' во всех схемах:\n")

try:
    conn = psycopg2.connect(database_url)
    cursor = conn.cursor()
    
    # Найти таблицу users во всех схемах
    cursor.execute("""
        SELECT table_schema, table_name
        FROM information_schema.tables
        WHERE table_name = 'users'
        ORDER BY table_schema;
    """)
    
    users_tables = cursor.fetchall()
    
    if users_tables:
        for schema_name, table_name in users_tables:
            print(f"✓ Найдена: {schema_name}.{table_name}")
            
            # Показать колонки
            cursor.execute("""
                SELECT column_name
                FROM information_schema.columns
                WHERE table_schema = %s
                AND table_name = 'users'
                ORDER BY ordinal_position;
            """, (schema_name,))
            
            columns = [row[0] for row in cursor.fetchall()]
            print(f"  Колонки: {', '.join(columns)}")
            print()
    else:
        print("❌ Таблица 'users' не найдена ни в одной схеме!")
    
    # Показать все таблицы в целевой схеме
    print(f"\n📊 Все таблицы в схеме '{schema}':\n")
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s
        ORDER BY table_name;
    """, (schema,))
    
    tables = cursor.fetchall()
    if tables:
        for (table_name,) in tables:
            print(f"  - {table_name}")
    else:
        print(f"  (схема '{schema}' пуста)")
    
    # Показать все таблицы в public
    print(f"\n📊 Все таблицы в схеме 'public':\n")
    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    public_tables = cursor.fetchall()
    if public_tables:
        for (table_name,) in public_tables:
            print(f"  - {table_name}")
    else:
        print("  (схема 'public' пуста)")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"\n❌ Ошибка: {e}\n")
    import traceback
    traceback.print_exc()
