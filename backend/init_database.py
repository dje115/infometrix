#!/usr/bin/env python3
"""
Database initialization script
Creates all tables and seeds initial data
"""
import sys
from sqlalchemy import text, inspect
from app.core.database import engine, Base, SessionLocal
from app.core.config import settings

def init_database():
    """Initialize database with all tables"""
    print("🗄️ Initializing database...")
    
    # Create all tables, ignoring errors about existing objects
    try:
        # Get all table names
        inspector = inspect(engine)
        existing_tables = set(inspector.get_table_names())
        
        # Create tables one by one to avoid transaction rollback issues
        created_count = 0
        skipped_count = 0
        
        for table_name, table in Base.metadata.tables.items():
            if table_name in existing_tables:
                skipped_count += 1
                continue
                
            try:
                table.create(bind=engine, checkfirst=True)
                created_count += 1
                print(f"  ✅ Created table: {table_name}")
            except Exception as e:
                if "already exists" in str(e).lower() or "duplicate" in str(e).lower():
                    skipped_count += 1
                else:
                    print(f"  ⚠️  Error creating {table_name}: {str(e)[:100]}")
        
        print(f"✅ Database initialization complete: {created_count} created, {skipped_count} already existed")
        
        # Verify tenants table exists
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1 FROM tenants LIMIT 1"))
            result.fetchone()
            print("✅ Verified: tenants table exists")
            return True
            
    except Exception as e:
        if "does not exist" in str(e).lower():
            print(f"❌ Tables not created: {e}")
            return False
        else:
            print(f"⚠️  Warning: {str(e)[:200]}")
            # Try to verify anyway
            try:
                with engine.connect() as conn:
                    result = conn.execute(text("SELECT 1 FROM tenants LIMIT 1"))
                    result.fetchone()
                    print("✅ Tables exist despite warning")
                    return True
            except:
                return False

if __name__ == "__main__":
    success = init_database()
    sys.exit(0 if success else 1)


