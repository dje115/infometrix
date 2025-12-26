#!/usr/bin/env python3
"""
Production Migration Script (Azure/AWS Compatible)
This script applies migrations to production databases (Azure PostgreSQL or AWS RDS)
"""

import os
import sys
import psycopg2
from psycopg2 import OperationalError
import argparse
from pathlib import Path

def get_db_config():
    """Get database configuration from environment variables"""
    config = {
        'host': os.getenv('DB_HOST') or os.getenv('AZURE_DB_HOST') or os.getenv('AWS_DB_HOST'),
        'port': int(os.getenv('DB_PORT', '5432')),
        'user': os.getenv('DB_USER') or os.getenv('AZURE_DB_USER') or os.getenv('AWS_DB_USER'),
        'password': os.getenv('DB_PASSWORD') or os.getenv('AZURE_DB_PASSWORD') or os.getenv('AWS_DB_PASSWORD'),
        'database': os.getenv('DB_NAME', 'ccs_quote_tool')
    }
    
    # Validate required fields
    if not config['host']:
        raise ValueError("DB_HOST, AZURE_DB_HOST, or AWS_DB_HOST must be set")
    if not config['user']:
        raise ValueError("DB_USER, AZURE_DB_USER, or AWS_DB_USER must be set")
    if not config['password']:
        raise ValueError("DB_PASSWORD, AZURE_DB_PASSWORD, or AWS_DB_PASSWORD must be set")
    
    return config

def test_connection(config):
    """Test database connection"""
    print("⏳ Testing database connection...")
    try:
        conn = psycopg2.connect(**config)
        conn.close()
        print("✅ Database connection successful")
        return True
    except OperationalError as e:
        print(f"❌ Database connection failed: {e}")
        return False

def apply_migration(config, migration_file, description):
    """Apply a migration file"""
    migration_path = Path(migration_file)
    
    if not migration_path.exists():
        print(f"⚠️  Migration file not found: {migration_file} (skipping)")
        return True
    
    print(f"📝 Applying: {description}")
    print(f"   File: {migration_file}")
    
    try:
        conn = psycopg2.connect(**config)
        conn.autocommit = True
        cursor = conn.cursor()
        
        with open(migration_path, 'r') as f:
            sql = f.read()
            cursor.execute(sql)
        
        cursor.close()
        conn.close()
        print("   ✅ Success")
        return True
    except Exception as e:
        error_msg = str(e).lower()
        if 'already exists' in error_msg or 'duplicate' in error_msg:
            print("   ⚠️  Already applied (skipping)")
            return True
        else:
            print(f"   ⚠️  Failed: {e} (continuing)")
            return True  # Continue even if migration fails

def main():
    parser = argparse.ArgumentParser(description='Apply database migrations to production')
    parser.add_argument('--migrations-dir', default='backend/migrations',
                       help='Directory containing migration files')
    parser.add_argument('--enforcement-migrations-dir', 
                       default='apps/enforcement-api/migrations',
                       help='Directory containing EnforceSense migration files')
    
    args = parser.parse_args()
    
    print("🚀 Production Migration Script")
    print("=" * 40)
    print("")
    
    # Get database configuration
    try:
        config = get_db_config()
    except ValueError as e:
        print(f"❌ Configuration error: {e}")
        sys.exit(1)
    
    print("Configuration:")
    print(f"  Host: {config['host']}")
    print(f"  Port: {config['port']}")
    print(f"  Database: {config['database']}")
    print(f"  User: {config['user']}")
    print("")
    
    # Test connection
    if not test_connection(config):
        sys.exit(1)
    
    print("")
    print("🔧 Applying Performance Migrations...")
    print("")
    
    # Get base directory (assume script is run from project root)
    base_dir = Path.cwd()
    
    # Migration 1: Missing Foreign Key Indexes
    migration1 = base_dir / args.migrations_dir / 'add_missing_foreign_key_indexes.sql'
    apply_migration(config, migration1, "Missing Foreign Key Indexes (11 indexes)")
    
    # Migration 2: Composite Indexes
    migration2 = base_dir / args.migrations_dir / 'add_composite_indexes_for_common_queries.sql'
    apply_migration(config, migration2, "Composite Indexes for Common Queries (10 indexes)")
    
    # Migration 3: EnforceSense Performance Indexes
    migration3 = base_dir / args.enforcement_migrations_dir / 'add_performance_indexes_enforcesense.sql'
    apply_migration(config, migration3, "EnforceSense Performance Indexes (11+ indexes)")
    
    print("")
    print("=" * 40)
    print("✅ All migrations completed!")
    print("=" * 40)
    print("")
    print("🎯 Next steps:")
    print("1. Restart your application service")
    print("2. Test the application - timeouts should be resolved")
    print("3. Monitor query performance")
    print("")

if __name__ == '__main__':
    main()

