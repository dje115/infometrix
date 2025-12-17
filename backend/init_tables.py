#!/usr/bin/env python3
"""
Initialize database tables
Creates all tables using SQLAlchemy Base.metadata.create_all
"""

import sys
from pathlib import Path

# Add the app directory to the Python path
sys.path.append(str(Path(__file__).parent))

from app.core.database import engine, Base
from app.models import *  # Import all models to register them with Base

def init_tables():
    """Create all database tables"""
    print("🗄️  Creating database tables...")
    
    try:
        # Create all tables (ignore errors about existing objects)
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ Database tables created successfully!")
        return True
    except Exception as e:
        # Check if error is about existing objects (which is fine)
        error_str = str(e).lower()
        if "already exists" in error_str or "duplicate" in error_str:
            print(f"⚠️  Some objects already exist (this is normal): {e}")
            print("✅ Database tables verified/created!")
            return True
        else:
            print(f"❌ Error creating tables: {e}")
            return False

if __name__ == "__main__":
    success = init_tables()
    sys.exit(0 if success else 1)

