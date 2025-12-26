#!/bin/bash
# Docker Entrypoint Script for Backend
# This script runs database migrations before starting the application

set -e

echo "🚀 Starting Infometrix Backend..."
echo ""

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
until PGPASSWORD="${POSTGRES_PASSWORD:-postgres_password_2025}" psql -h "${POSTGRES_HOST:-postgres}" -U "${POSTGRES_USER:-postgres}" -d "${POSTGRES_DB:-ccs_quote_tool}" -c '\q' 2>/dev/null; do
  echo "   PostgreSQL is unavailable - sleeping"
  sleep 1
done
echo "✅ PostgreSQL is ready!"
echo ""

# Function to apply migration
apply_migration() {
    local migration_file=$1
    local description=$2
    
    if [ ! -f "$migration_file" ]; then
        echo "⚠️  Migration file not found: $migration_file (skipping)"
        return 0
    fi
    
    echo "📝 Applying: $description"
    echo "   File: $migration_file"
    
    if PGPASSWORD="${POSTGRES_PASSWORD:-postgres_password_2025}" psql \
        -h "${POSTGRES_HOST:-postgres}" \
        -U "${POSTGRES_USER:-postgres}" \
        -d "${POSTGRES_DB:-ccs_quote_tool}" \
        -f "$migration_file" \
        > /dev/null 2>&1; then
        echo "   ✅ Success"
        return 0
    else
        # Check if error is because index already exists (safe to ignore)
        if PGPASSWORD="${POSTGRES_PASSWORD:-postgres_password_2025}" psql \
            -h "${POSTGRES_HOST:-postgres}" \
            -U "${POSTGRES_USER:-postgres}" \
            -d "${POSTGRES_DB:-ccs_quote_tool}" \
            -f "$migration_file" 2>&1 | grep -q "already exists"; then
            echo "   ⚠️  Already applied (skipping)"
            return 0
        else
            echo "   ⚠️  Failed or already applied (continuing)"
            return 0
        fi
    fi
}

# Apply performance migrations
echo "🔧 Applying Performance Migrations..."
echo ""

# Migration 1: Missing Foreign Key Indexes
# Check if we're in backend or enforcement-api context
if [ -f "/app/migrations/add_missing_foreign_key_indexes.sql" ]; then
    apply_migration \
        "/app/migrations/add_missing_foreign_key_indexes.sql" \
        "Missing Foreign Key Indexes"
elif [ -f "/app/../backend/migrations/add_missing_foreign_key_indexes.sql" ]; then
    apply_migration \
        "/app/../backend/migrations/add_missing_foreign_key_indexes.sql" \
        "Missing Foreign Key Indexes"
fi

# Migration 2: Composite Indexes
if [ -f "/app/migrations/add_composite_indexes_for_common_queries.sql" ]; then
    apply_migration \
        "/app/migrations/add_composite_indexes_for_common_queries.sql" \
        "Composite Indexes for Common Queries"
elif [ -f "/app/../backend/migrations/add_composite_indexes_for_common_queries.sql" ]; then
    apply_migration \
        "/app/../backend/migrations/add_composite_indexes_for_common_queries.sql" \
        "Composite Indexes for Common Queries"
fi

# Migration 3: EnforceSense Performance Indexes (if exists)
if [ -f "/app/../apps/enforcement-api/migrations/add_performance_indexes_enforcesense.sql" ]; then
    apply_migration \
        "/app/../apps/enforcement-api/migrations/add_performance_indexes_enforcesense.sql" \
        "EnforceSense Performance Indexes"
fi

echo ""
echo "✅ Migrations completed!"
echo ""

# Execute the main command
echo "🎯 Starting application..."
exec "$@"

