"""
Проверка и подготовка миграций для Render
Автоматически обновляет схему БД при деплое
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect

def check_and_migrate():
    """Проверка схемы и автоматическая миграция"""
    print("\n🔧 Checking database schema...")
    
    database_url = os.getenv('DATABASE_URL')
    schema = os.getenv('DATABASE_SCHEMA', 'goalpredictor')
    
    if not database_url:
        print("⚠️  No DATABASE_URL found - assuming local development")
        return True
    
    # Fix postgres:// to postgresql://
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    
    try:
        engine = create_engine(database_url, connect_args={
            "options": f"-csearch_path={schema},public"
        })
        
        with engine.connect() as conn:
            conn.execute(text(f"SET search_path TO {schema}, public"))
            
            # Проверяем наличие всех необходимых таблиц
            inspector = inspect(engine)
            existing_tables = set(inspector.get_table_names(schema=schema))
            
            required_tables = {
                'users', 'teams', 'matches', 'predictions',
                'user_predictions', 'tennis_players', 
                'tennis_matches', 'tennis_predictions'
            }
            
            missing_tables = required_tables - existing_tables
            
            if missing_tables:
                print(f"⚠️  Missing tables: {missing_tables}")
                print("🔧 Creating missing tables...")
                
                from app import create_app
                from extensions import db
                
                app = create_app('production')
                with app.app_context():
                    db.create_all()
                
                print("✅ Tables created")
            else:
                print(f"✅ All {len(required_tables)} tables exist")
            
            # Проверяем колонку is_premium
            columns = [col['name'] for col in inspector.get_columns('users', schema=schema)]
            if 'is_premium' not in columns:
                print("🔧 Adding is_premium column...")
                conn.execute(text(f"""
                    ALTER TABLE {schema}.users 
                    ADD COLUMN is_premium BOOLEAN DEFAULT FALSE
                """))
                conn.commit()
                print("✅ is_premium column added")
            
            print("\n✅ Database schema is up to date!\n")
            return True
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()

if __name__ == '__main__':
    success = check_and_migrate()
    sys.exit(0 if success else 1)
