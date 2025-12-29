#!/usr/bin/env python3
"""
Docker Entrypoint Script for Backend
This script runs database migrations before starting the application
"""

import os
import sys
import subprocess
import time
import psycopg2
from psycopg2 import OperationalError

def wait_for_postgres(max_retries=30, retry_interval=1):
    """Wait for PostgreSQL to be ready"""
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'postgres'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres_password_2025'),
        'database': os.getenv('POSTGRES_DB', 'ccs_quote_tool')
    }
    
    print("⏳ Waiting for PostgreSQL to be ready...")
    for i in range(max_retries):
        try:
            conn = psycopg2.connect(**db_config)
            conn.close()
            print("✅ PostgreSQL is ready!")
            return True
        except OperationalError:
            if i < max_retries - 1:
                time.sleep(retry_interval)
            else:
                print("❌ PostgreSQL is not available after waiting")
                return False
    return False

def apply_migration(migration_file, description):
    """Apply a migration file"""
    if not os.path.exists(migration_file):
        print(f"⚠️  Migration file not found: {migration_file} (skipping)")
        return True
    
    print(f"📝 Applying: {description}")
    print(f"   File: {migration_file}")
    
    db_config = {
        'host': os.getenv('POSTGRES_HOST', 'postgres'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'user': os.getenv('POSTGRES_USER', 'postgres'),
        'password': os.getenv('POSTGRES_PASSWORD', 'postgres_password_2025'),
        'database': os.getenv('POSTGRES_DB', 'ccs_quote_tool')
    }
    
    try:
        conn = psycopg2.connect(**db_config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        with open(migration_file, 'r') as f:
            sql = f.read()
            cursor.execute(sql)
        
        cursor.close()
        conn.close()
        print("   ✅ Success")
        return True
    except Exception as e:
        # Check if error is because index already exists (safe to ignore)
        error_msg = str(e).lower()
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            print("   ⚠️  Already applied (skipping)")
            return True
        else:
            print(f"   ⚠️  Failed: {e} (continuing)")
            return True  # Continue even if migration fails

def main():
    """Main entrypoint"""
    print("🚀 Starting Infometrix Backend...")
    print("")
    
    # Wait for PostgreSQL
    if not wait_for_postgres():
        print("❌ Failed to connect to PostgreSQL")
        sys.exit(1)
    
    print("")
    print("🔧 Applying Performance Migrations...")
    print("")
    
    # Get base paths
    app_dir = os.getenv('APP_DIR', '/app')
    migrations_dir = os.path.join(app_dir, 'migrations')
    enforcement_migrations_dir = os.path.join(app_dir, '..', 'apps', 'enforcement-api', 'migrations')
    
    # Migration 1: Missing Foreign Key Indexes
    migration1 = os.path.join(migrations_dir, 'add_missing_foreign_key_indexes.sql')
    apply_migration(migration1, "Missing Foreign Key Indexes")
    
    # Migration 2: Composite Indexes
    migration2 = os.path.join(migrations_dir, 'add_composite_indexes_for_common_queries.sql')
    apply_migration(migration2, "Composite Indexes for Common Queries")
    
    # Migration 3: EnforceSense Performance Indexes
    migration3 = os.path.join(enforcement_migrations_dir, 'add_performance_indexes_enforcesense.sql')
    if os.path.exists(migration3):
        apply_migration(migration3, "EnforceSense Performance Indexes")
    
    print("")
    print("✅ Migrations completed!")
    print("")
    
    # Execute the main command
    print("🎯 Starting application...")
    if len(sys.argv) > 1:
        os.execvp(sys.argv[1], sys.argv[1:])
    else:
        # Default command
        os.execvp('uvicorn', ['uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'])

if __name__ == '__main__':
    main()



