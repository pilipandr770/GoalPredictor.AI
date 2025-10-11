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
                print("🔧 Creating missing tables manually...")
                
                # Создаём таблицы без ForeignKey вручную
                conn.execute(text(f"""
                    -- Users table
                    CREATE TABLE IF NOT EXISTS {schema}.users (
                        id SERIAL PRIMARY KEY,
                        email VARCHAR(120) UNIQUE NOT NULL,
                        username VARCHAR(80) UNIQUE NOT NULL,
                        password_hash VARCHAR(255) NOT NULL,
                        is_admin BOOLEAN DEFAULT FALSE,
                        is_premium BOOLEAN DEFAULT FALSE,
                        subscription_id VARCHAR(255),
                        subscription_end TIMESTAMP,
                        daily_predictions_count INTEGER DEFAULT 0,
                        last_prediction_date DATE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        last_login TIMESTAMP,
                        is_active BOOLEAN DEFAULT TRUE
                    );
                    CREATE INDEX IF NOT EXISTS idx_users_email ON {schema}.users(email);
                    
                    -- Teams table
                    CREATE TABLE IF NOT EXISTS {schema}.teams (
                        id SERIAL PRIMARY KEY,
                        api_id INTEGER UNIQUE NOT NULL,
                        name VARCHAR(100) NOT NULL,
                        league VARCHAR(50) NOT NULL,
                        country VARCHAR(50) NOT NULL,
                        logo_url VARCHAR(255),
                        total_matches INTEGER DEFAULT 0,
                        goals_scored INTEGER DEFAULT 0,
                        goals_conceded INTEGER DEFAULT 0,
                        avg_goals_per_match FLOAT DEFAULT 0.0,
                        over_2_5_percentage FLOAT DEFAULT 0.0,
                        last_5_form VARCHAR(5),
                        last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_teams_api_id ON {schema}.teams(api_id);
                    
                    -- Matches table
                    CREATE TABLE IF NOT EXISTS {schema}.matches (
                        id SERIAL PRIMARY KEY,
                        api_id INTEGER UNIQUE NOT NULL,
                        home_team_id INTEGER NOT NULL,
                        away_team_id INTEGER NOT NULL,
                        league VARCHAR(50) NOT NULL,
                        match_date TIMESTAMP NOT NULL,
                        status VARCHAR(20) DEFAULT 'scheduled',
                        home_score INTEGER,
                        away_score INTEGER,
                        home_goals INTEGER,
                        away_goals INTEGER,
                        total_goals INTEGER,
                        result VARCHAR(1),
                        over_2_5 BOOLEAN,
                        btts BOOLEAN,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_matches_api_id ON {schema}.matches(api_id);
                    CREATE INDEX IF NOT EXISTS idx_matches_date ON {schema}.matches(match_date);
                    
                    -- Predictions table
                    CREATE TABLE IF NOT EXISTS {schema}.predictions (
                        id SERIAL PRIMARY KEY,
                        match_id INTEGER NOT NULL,
                        prediction_type VARCHAR(50) DEFAULT 'over_2.5',
                        probability FLOAT NOT NULL,
                        confidence VARCHAR(20) NOT NULL,
                        explanation TEXT,
                        factors JSON,
                        is_correct BOOLEAN,
                        actual_result VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        model_version VARCHAR(50)
                    );
                    
                    -- User predictions table
                    CREATE TABLE IF NOT EXISTS {schema}.user_predictions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        prediction_id INTEGER NOT NULL,
                        viewed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    
                    -- Tennis players table
                    CREATE TABLE IF NOT EXISTS {schema}.tennis_players (
                        id SERIAL PRIMARY KEY,
                        atp_id INTEGER UNIQUE,
                        name VARCHAR(100) NOT NULL,
                        country VARCHAR(3),
                        current_rank INTEGER,
                        current_points INTEGER,
                        career_wins INTEGER DEFAULT 0,
                        career_losses INTEGER DEFAULT 0,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_tennis_players_atp_id ON {schema}.tennis_players(atp_id);
                    
                    -- Tennis matches table
                    CREATE TABLE IF NOT EXISTS {schema}.tennis_matches (
                        id SERIAL PRIMARY KEY,
                        api_id VARCHAR(100) UNIQUE,
                        tournament_name VARCHAR(150) NOT NULL,
                        tournament_level VARCHAR(20),
                        surface VARCHAR(20),
                        round VARCHAR(20),
                        player1_id INTEGER NOT NULL,
                        player2_id INTEGER NOT NULL,
                        match_date TIMESTAMP NOT NULL,
                        completed BOOLEAN DEFAULT FALSE,
                        winner_id INTEGER,
                        score VARCHAR(50),
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                    CREATE INDEX IF NOT EXISTS idx_tennis_matches_api_id ON {schema}.tennis_matches(api_id);
                    CREATE INDEX IF NOT EXISTS idx_tennis_matches_date ON {schema}.tennis_matches(match_date);
                    
                    -- Tennis predictions table
                    CREATE TABLE IF NOT EXISTS {schema}.tennis_predictions (
                        id SERIAL PRIMARY KEY,
                        match_id INTEGER NOT NULL,
                        player1_win_probability FLOAT NOT NULL,
                        player2_win_probability FLOAT NOT NULL,
                        confidence VARCHAR(20) NOT NULL,
                        explanation TEXT,
                        factors JSON,
                        is_correct BOOLEAN,
                        actual_winner_id INTEGER,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        model_version VARCHAR(50)
                    );
                    
                    -- Subscriptions table
                    CREATE TABLE IF NOT EXISTS {schema}.subscriptions (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER NOT NULL,
                        stripe_subscription_id VARCHAR(255) UNIQUE NOT NULL,
                        stripe_customer_id VARCHAR(255) NOT NULL,
                        stripe_price_id VARCHAR(255) NOT NULL,
                        status VARCHAR(50) NOT NULL,
                        plan_type VARCHAR(20) NOT NULL,
                        current_period_start TIMESTAMP NOT NULL,
                        current_period_end TIMESTAMP NOT NULL,
                        cancel_at_period_end BOOLEAN DEFAULT FALSE,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );
                """))
                conn.commit()
                
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
