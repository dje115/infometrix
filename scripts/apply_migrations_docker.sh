#!/bin/bash
# Apply Migrations in Docker Environment
# This script applies migrations to the Docker PostgreSQL container

set -e

echo "🐳 Applying Migrations to Docker PostgreSQL Container..."
echo ""

# Check if Docker is running
if ! docker ps > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker and try again."
    exit 1
fi

# Check if postgres container exists
if ! docker ps --format '{{.Names}}' | grep -q "infometrix-postgres"; then
    echo "⚠️  PostgreSQL container not found. Starting containers..."
    docker-compose up -d postgres
    echo "⏳ Waiting for PostgreSQL to be ready..."
    sleep 10
fi

echo "✅ PostgreSQL container is ready"
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
    
    if docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool < "$migration_file" > /dev/null 2>&1; then
        echo "   ✅ Success"
        return 0
    else
        # Check if error is because index already exists
        if docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool < "$migration_file" 2>&1 | grep -q "already exists"; then
            echo "   ⚠️  Already applied (skipping)"
            return 0
        else
            echo "   ⚠️  Failed or already applied (continuing)"
            return 0
        fi
    fi
}

# Apply migrations
echo "🔧 Applying Performance Migrations..."
echo ""

# Migration 1: Missing Foreign Key Indexes
apply_migration \
    "backend/migrations/add_missing_foreign_key_indexes.sql" \
    "Missing Foreign Key Indexes (11 indexes)"

# Migration 2: Composite Indexes
apply_migration \
    "backend/migrations/add_composite_indexes_for_common_queries.sql" \
    "Composite Indexes for Common Queries (10 indexes)"

# Migration 3: EnforceSense Performance Indexes
apply_migration \
    "apps/enforcement-api/migrations/add_performance_indexes_enforcesense.sql" \
    "EnforceSense Performance Indexes (11+ indexes)"

echo ""
echo "✅ All migrations completed!"
echo ""
echo "🎯 Next steps:"
echo "1. Restart backend: docker-compose restart backend"
echo "2. Test the application - timeouts should be resolved"
echo ""

