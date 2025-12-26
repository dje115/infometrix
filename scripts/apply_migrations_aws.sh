#!/bin/bash
# AWS Production Migration Script
# This script applies migrations to AWS RDS PostgreSQL

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}AWS Production Migration Script${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""

# Configuration from environment variables or AWS Secrets Manager
DB_USER="${AWS_DB_USER:-${DB_USER}}"
DB_NAME="${AWS_DB_NAME:-${DB_NAME:-ccs_quote_tool}}"
DB_HOST="${AWS_DB_HOST:-${DB_HOST}}"
DB_PORT="${AWS_DB_PORT:-5432}"
DB_PASSWORD="${AWS_DB_PASSWORD:-${DB_PASSWORD}}"

# AWS RDS endpoint format: your-db.xxxxx.us-east-1.rds.amazonaws.com
# If using AWS Secrets Manager, you can retrieve secrets:
# DB_PASSWORD=$(aws secretsmanager get-secret-value --secret-id your-secret-name --query SecretString --output text | jq -r .password)

# Validate required variables
if [ -z "$DB_HOST" ]; then
    echo -e "${RED}Error: DB_HOST or AWS_DB_HOST must be set${NC}"
    echo "  Example: your-db.xxxxx.us-east-1.rds.amazonaws.com"
    exit 1
fi

if [ -z "$DB_USER" ]; then
    echo -e "${RED}Error: DB_USER or AWS_DB_USER must be set${NC}"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}Error: DB_PASSWORD or AWS_DB_PASSWORD must be set${NC}"
    echo "  Consider using AWS Secrets Manager for secure password retrieval"
    exit 1
fi

echo -e "${YELLOW}Configuration:${NC}"
echo "  Host: $DB_HOST"
echo "  Port: $DB_PORT"
echo "  Database: $DB_NAME"
echo "  User: $DB_USER"
echo ""

# Check if psql is available
if ! command -v psql &> /dev/null; then
    echo -e "${RED}Error: psql command not found. Please install PostgreSQL client tools.${NC}"
    echo "  AWS: Use EC2 instance, AWS Cloud9, or install PostgreSQL client"
    exit 1
fi

# Test database connection
echo -e "${YELLOW}Testing database connection...${NC}"
if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -c '\q' 2>/dev/null; then
    echo -e "${GREEN}✅ Database connection successful${NC}"
else
    echo -e "${RED}❌ Database connection failed${NC}"
    echo "  Check your RDS endpoint, security groups, and VPC configuration"
    exit 1
fi
echo ""

# Function to apply migration
apply_migration() {
    local migration_file=$1
    local description=$2
    
    if [ ! -f "$migration_file" ]; then
        echo -e "${YELLOW}⚠️  Migration file not found: $migration_file (skipping)${NC}"
        return 0
    fi
    
    echo -e "${YELLOW}📝 Applying: $description${NC}"
    echo "   File: $migration_file"
    
    if PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file" > /dev/null 2>&1; then
        echo -e "${GREEN}   ✅ Success${NC}"
        return 0
    else
        # Check if error is because index already exists (safe to ignore)
        ERROR_OUTPUT=$(PGPASSWORD="$DB_PASSWORD" psql -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER" -d "$DB_NAME" -f "$migration_file" 2>&1)
        if echo "$ERROR_OUTPUT" | grep -q "already exists"; then
            echo -e "${YELLOW}   ⚠️  Already applied (skipping)${NC}"
            return 0
        else
            echo -e "${YELLOW}   ⚠️  Failed or already applied (continuing)${NC}"
            return 0
        fi
    fi
}

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

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All migrations completed!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Restart your application service (ECS, EC2, Lambda, etc.)"
echo "2. Test the application - timeouts should be resolved"
echo "3. Monitor query performance in CloudWatch"
echo ""

