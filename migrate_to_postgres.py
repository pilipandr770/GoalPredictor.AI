"""
Migration script for PostgreSQL with custom schema support
Prepares database for GoalPredictor.AI on Render.com
"""
import os
import sys
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker
from urllib.parse import urlparse

def get_database_url():
    """Get database URL from environment"""
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        print("❌ DATABASE_URL not found in environment variables")
        sys.exit(1)
    
    # Render sometimes uses 'postgres://' but SQLAlchemy needs 'postgresql://'
    if db_url.startswith('postgres://'):
        db_url = db_url.replace('postgres://', 'postgresql://', 1)
    
    return db_url

def get_schema_name():
    """Get schema name from environment or use default"""
    return os.getenv('DATABASE_SCHEMA', 'goalpredictor')

def create_schema_if_not_exists(engine, schema_name):
    """Create database schema if it doesn't exist"""
    with engine.connect() as conn:
        # Check if schema exists
        result = conn.execute(text(
            "SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"
        ), {"schema": schema_name})
        
        if result.fetchone() is None:
            print(f"📦 Creating schema: {schema_name}")
            conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_name}"'))
            conn.commit()
            print(f"✅ Schema '{schema_name}' created")
        else:
            print(f"✅ Schema '{schema_name}' already exists")

def setup_database():
    """Setup PostgreSQL database with custom schema"""
    print("🔧 Starting database setup for Render.com...")
    
    # Get configuration
    db_url = get_database_url()
    schema_name = get_schema_name()
    
    print(f"📊 Database: {urlparse(db_url).netloc}")
    print(f"📦 Schema: {schema_name}")
    
    # Create engine
    engine = create_engine(
        db_url,
        connect_args={
            "options": f"-csearch_path={schema_name},public"
        },
        pool_pre_ping=True,
        pool_size=5,
        max_overflow=10
    )
    
    try:
        # Test connection
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()"))
            version = result.fetchone()[0]
            print(f"✅ Connected to PostgreSQL")
            print(f"   Version: {version.split(',')[0]}")
        
        # Create schema
        create_schema_if_not_exists(engine, schema_name)
        
        # Create tables in the schema
        print("\n📋 Creating tables in schema...")
        from app import create_app
        from extensions import db
        
        app = create_app('production')
        with app.app_context():
            # Set schema for this session
            with db.engine.connect() as conn:
                conn.execute(text(f'SET search_path TO "{schema_name}", public'))
                conn.commit()
            
            # Create all tables
            db.create_all()
            print("✅ All tables created successfully")
            
            # Verify tables
            inspector = inspect(db.engine)
            tables = inspector.get_table_names(schema=schema_name)
            print(f"\n📊 Tables in schema '{schema_name}':")
            for table in tables:
                print(f"   - {table}")
        
        print("\n✅ Database setup complete!")
        return True
        
    except Exception as e:
        print(f"\n❌ Error setting up database: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        engine.dispose()

def verify_database():
    """Verify database configuration"""
    print("\n🔍 Verifying database setup...")
    
    db_url = get_database_url()
    schema_name = get_schema_name()
    
    engine = create_engine(db_url, pool_pre_ping=True)
    
    try:
        with engine.connect() as conn:
            # Check schema exists
            result = conn.execute(text(
                "SELECT schema_name FROM information_schema.schemata WHERE schema_name = :schema"
            ), {"schema": schema_name})
            
            if result.fetchone():
                print(f"✅ Schema '{schema_name}' verified")
            else:
                print(f"❌ Schema '{schema_name}' not found")
                return False
            
            # Count tables in schema
            result = conn.execute(text("""
                SELECT COUNT(*) 
                FROM information_schema.tables 
                WHERE table_schema = :schema
            """), {"schema": schema_name})
            
            table_count = result.fetchone()[0]
            print(f"✅ Found {table_count} tables in schema")
            
            return True
            
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        return False
    finally:
        engine.dispose()

if __name__ == '__main__':
    print("=" * 60)
    print("🚀 GoalPredictor.AI - PostgreSQL Migration")
    print("=" * 60)
    print()
    
    # Setup database
    if setup_database():
        # Verify setup
        if verify_database():
            print("\n" + "=" * 60)
            print("✅ Migration completed successfully!")
            print("=" * 60)
            sys.exit(0)
        else:
            print("\n❌ Verification failed")
            sys.exit(1)
    else:
        print("\n❌ Migration failed")
        sys.exit(1)
