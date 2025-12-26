#!/bin/bash
# Migration Application Script
# This script applies all performance-related database migrations

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DB_USER="${DB_USER:-postgres}"
DB_NAME="${DB_NAME:-ccs_quote_tool}"
DB_HOST="${DB_HOST:-localhost}"
DB_PORT="${DB_PORT:-5432}"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}Infometrix Database Migration Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: psql command not found. Please install PostgreSQL client tools.${NC}"
    exit 1
fi

# Function to apply migration
apply_migration() {
    local migration_file=$1
    local description=$2
    
    if [ ! -f "$migration_file" ]; then
        echo -e "${RED}Error: Migration file not found: $migration_file${NC}"
        return 1
    fi
    
    echo -e "${YELLOW}Applying: $description${NC}"
    echo -e "File: $migration_file"
    
    if PGPASSWORD="${DB_PASSWORD}" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file"; then
        echo -e "${GREEN}✓ Successfully applied: $description${NC}"
        echo ""
        return 0
    else
        echo -e "${RED}✗ Failed to apply: $description${NC}"
        echo ""
        return 1
    fi
}

# Get database password if not set
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${YELLOW}Database password not set in DB_PASSWORD environment variable.${NC}"
    echo -e "${YELLOW}You will be prompted for the password.${NC}"
    echo ""
fi

# Apply migrations in order
echo -e "${GREEN}Starting migration process...${NC}"
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

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All migrations completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Restart your backend server"
echo "2. Test the application - timeouts should be resolved"
echo "3. Monitor query performance"
echo ""

