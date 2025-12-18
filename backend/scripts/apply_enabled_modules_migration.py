#!/usr/bin/env python3
"""
Apply enabled_modules migration to existing tenants
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from app.core.config import settings

def apply_migration():
    """Apply enabled_modules migration"""
    print("Applying enabled_modules migration...")
    
    try:
        engine = create_engine(settings.DATABASE_URL)
        with engine.connect() as conn:
            # Add column if not exists
            conn.execute(text("""
                ALTER TABLE tenants 
                ADD COLUMN IF NOT EXISTS enabled_modules JSONB DEFAULT '[]'::jsonb;
            """))
            
            # Update existing tenants
            conn.execute(text("""
                UPDATE tenants 
                SET enabled_modules = '["crm", "helpdesk"]'::jsonb
                WHERE enabled_modules IS NULL OR enabled_modules = '[]'::jsonb;
            """))
            
            conn.commit()
        
        print("✅ Migration applied successfully!")
        
        # Verify
        with engine.connect() as conn:
            result = conn.execute(text("SELECT id, name, enabled_modules FROM tenants;"))
            rows = result.fetchall()
            print("\nTenants after migration:")
            for row in rows:
                print(f"  {row[1]}: {row[2]}")
        
        engine.dispose()
        return True
    except Exception as e:
        print(f"❌ Error applying migration: {e}")
        return False

if __name__ == "__main__":
    success = apply_migration()
    sys.exit(0 if success else 1)

