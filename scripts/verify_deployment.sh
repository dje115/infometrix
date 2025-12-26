#!/bin/bash
# Deployment Verification Script
# This script verifies that all performance fixes are properly applied

set -e

echo "🔍 Verifying Deployment..."
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is running
echo "📡 Checking Docker..."
if ! docker ps > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker is not running${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Check if containers are running
echo "📦 Checking containers..."
BACKEND_RUNNING=$(docker ps --format '{{.Names}}' | grep -q "infometrix-backend" && echo "yes" || echo "no")
POSTGRES_RUNNING=$(docker ps --format '{{.Names}}' | grep -q "infometrix-postgres" && echo "yes" || echo "no")

if [ "$BACKEND_RUNNING" = "yes" ]; then
    echo -e "${GREEN}✅ Backend container is running${NC}"
else
    echo -e "${RED}❌ Backend container is not running${NC}"
fi

if [ "$POSTGRES_RUNNING" = "yes" ]; then
    echo -e "${GREEN}✅ PostgreSQL container is running${NC}"
else
    echo -e "${RED}❌ PostgreSQL container is not running${NC}"
fi
echo ""

# Check if migrations were applied
if [ "$POSTGRES_RUNNING" = "yes" ]; then
    echo "🔍 Checking database indexes..."
    
    # Check for foreign key indexes
    FK_INDEXES=$(docker exec infometrix-postgres psql -U postgres -d ccs_quote_tool -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%' AND (indexname LIKE '%_contact_id%' OR indexname LIKE '%_created_by%' OR indexname LIKE '%_supplier_id%' OR indexname LIKE '%_parent_quote_id%' OR indexname LIKE '%_template_id%');" 2>/dev/null | tr -d ' ')
    
    if [ "$FK_INDEXES" -ge "5" ]; then
        echo -e "${GREEN}✅ Foreign key indexes found: $FK_INDEXES${NC}"
    else
        echo -e "${YELLOW}⚠️  Found $FK_INDEXES foreign key indexes (expected at least 5)${NC}"
    fi
    
    # Check for composite indexes
    COMPOSITE_INDEXES=$(docker exec infometrix-postgres psql -U postgres -d ccs_quote_tool -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%' AND (indexname LIKE '%_tenant_%' OR indexname LIKE '%_customer_%' OR indexname LIKE '%_status%');" 2>/dev/null | tr -d ' ')
    
    if [ "$COMPOSITE_INDEXES" -ge "5" ]; then
        echo -e "${GREEN}✅ Composite indexes found: $COMPOSITE_INDEXES${NC}"
    else
        echo -e "${YELLOW}⚠️  Found $COMPOSITE_INDEXES composite indexes (expected at least 5)${NC}"
    fi
    
    # Check for EnforceSense indexes
    ENFORCESENSE_INDEXES=$(docker exec infometrix-postgres psql -U postgres -d ccs_quote_tool -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND (indexname LIKE '%debtor%' OR indexname LIKE '%enforcement%' OR indexname LIKE '%case%' OR indexname LIKE '%ledger%');" 2>/dev/null | tr -d ' ')
    
    if [ "$ENFORCESENSE_INDEXES" -ge "5" ]; then
        echo -e "${GREEN}✅ EnforceSense indexes found: $ENFORCESENSE_INDEXES${NC}"
    else
        echo -e "${YELLOW}⚠️  Found $ENFORCESENSE_INDEXES EnforceSense indexes (expected at least 5)${NC}"
    fi
    
    echo ""
fi

# Check backend logs for migration messages
if [ "$BACKEND_RUNNING" = "yes" ]; then
    echo "📋 Checking backend logs for migration messages..."
    MIGRATION_LOGS=$(docker logs infometrix-backend 2>&1 | grep -i "migration\|index" | tail -5)
    
    if [ -n "$MIGRATION_LOGS" ]; then
        echo -e "${GREEN}✅ Migration logs found:${NC}"
        echo "$MIGRATION_LOGS" | sed 's/^/   /'
    else
        echo -e "${YELLOW}⚠️  No migration logs found (this is OK if migrations already applied)${NC}"
    fi
    echo ""
fi

# Check if backend is responding
if [ "$BACKEND_RUNNING" = "yes" ]; then
    echo "🌐 Checking backend health..."
    if curl -f http://localhost:8000/health > /dev/null 2>&1; then
        echo -e "${GREEN}✅ Backend is responding${NC}"
    else
        echo -e "${RED}❌ Backend is not responding${NC}"
    fi
    echo ""
fi

# Summary
echo "=========================================="
echo "📊 Verification Summary"
echo "=========================================="
echo ""

if [ "$BACKEND_RUNNING" = "yes" ] && [ "$POSTGRES_RUNNING" = "yes" ]; then
    echo -e "${GREEN}✅ Core services are running${NC}"
else
    echo -e "${RED}❌ Some services are not running${NC}"
fi

echo ""
echo "🎯 Next steps:"
echo "1. Test the application in browser"
echo "2. Navigate to Customers, Opportunities, Leads pages"
echo "3. Verify no timeout errors occur"
echo "4. Test error handling (disconnect network temporarily)"
echo "5. Verify retry buttons work"
echo ""

