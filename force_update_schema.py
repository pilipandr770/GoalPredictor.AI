"""
Принудительное добавление колонки is_premium в таблицу users
Запускается после migrate_to_postgres.py
"""
import os
import sys
import psycopg2

def force_add_is_premium():
    """Принудительно добавить колонку is_premium"""
    print("\n" + "=" * 60)
    print("🔧 FORCE: Добавление is_premium в таблицу users")
    print("=" * 60 + "\n")
    
    database_url = os.getenv('DATABASE_URL')
    schema = os.getenv('DATABASE_SCHEMA', 'goalpredictor')
    
    if not database_url:
        print("❌ ERROR: DATABASE_URL environment variable not found!")
        print("\n📋 Available environment variables:")
        for key in sorted(os.environ.keys()):
            print(f"   {key}")
        sys.exit(1)
    
    print(f"✓ DATABASE_URL found")
    print(f"✓ Using schema: {schema}\n")
    
    try:
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()
        
        # Set search path
        cursor.execute(f"SET search_path TO {schema}")
        
        # Try to add column with IF NOT EXISTS logic in PL/pgSQL
        cursor.execute(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 
                    FROM information_schema.columns 
                    WHERE table_schema = '{schema}'
                    AND table_name = 'users'
                    AND column_name = 'is_premium'
                ) THEN
                    ALTER TABLE {schema}.users 
                    ADD COLUMN is_premium BOOLEAN DEFAULT FALSE;
                    RAISE NOTICE 'Column is_premium added successfully';
                ELSE
                    RAISE NOTICE 'Column is_premium already exists';
                END IF;
            END $$;
        """)
        
        # Verify the column exists
        cursor.execute(f"""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_schema = '{schema}'
            AND table_name = 'users'
            AND column_name = 'is_premium'
        """)
        
        if cursor.fetchone():
            print("✅ SUCCESS: Column is_premium is present in users table")
        else:
            print("❌ ERROR: Column is_premium not found after ALTER TABLE!")
            sys.exit(1)
        
        cursor.close()
        conn.close()
        
        print("\n" + "=" * 60)
        print("✅ Schema update completed successfully")
        print("=" * 60 + "\n")
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    force_add_is_premium()
