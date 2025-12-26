# PowerShell Deployment Verification Script
# This script verifies that all performance fixes are properly applied

Write-Host "🔍 Verifying Deployment..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "📡 Checking Docker..." -ForegroundColor Yellow
try {
    $null = docker ps 2>&1
    Write-Host "✅ Docker is running" -ForegroundColor Green
} catch {
    Write-Host "❌ Docker is not running" -ForegroundColor Red
    exit 1
}
Write-Host ""

# Check if containers are running
Write-Host "📦 Checking containers..." -ForegroundColor Yellow
$backendRunning = docker ps --format '{{.Names}}' | Select-String "infometrix-backend"
$postgresRunning = docker ps --format '{{.Names}}' | Select-String "infometrix-postgres"

if ($backendRunning) {
    Write-Host "✅ Backend container is running" -ForegroundColor Green
} else {
    Write-Host "❌ Backend container is not running" -ForegroundColor Red
}

if ($postgresRunning) {
    Write-Host "✅ PostgreSQL container is running" -ForegroundColor Green
} else {
    Write-Host "❌ PostgreSQL container is not running" -ForegroundColor Red
}
Write-Host ""

# Check if migrations were applied
if ($postgresRunning) {
    Write-Host "🔍 Checking database indexes..." -ForegroundColor Yellow
    
    # Check for foreign key indexes
    $fkIndexes = docker exec infometrix-postgres psql -U postgres -d ccs_quote_tool -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%' AND (indexname LIKE '%_contact_id%' OR indexname LIKE '%_created_by%' OR indexname LIKE '%_supplier_id%' OR indexname LIKE '%_parent_quote_id%' OR indexname LIKE '%_template_id%');" 2>&1 | ForEach-Object { $_.Trim() }
    
    if ([int]$fkIndexes -ge 5) {
        Write-Host "✅ Foreign key indexes found: $fkIndexes" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Found $fkIndexes foreign key indexes (expected at least 5)" -ForegroundColor Yellow
    }
    
    # Check for composite indexes
    $compositeIndexes = docker exec infometrix-postgres psql -U postgres -d ccs_quote_tool -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND indexname LIKE 'idx_%' AND (indexname LIKE '%_tenant_%' OR indexname LIKE '%_customer_%' OR indexname LIKE '%_status%');" 2>&1 | ForEach-Object { $_.Trim() }
    
    if ([int]$compositeIndexes -ge 5) {
        Write-Host "✅ Composite indexes found: $compositeIndexes" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Found $compositeIndexes composite indexes (expected at least 5)" -ForegroundColor Yellow
    }
    
    # Check for EnforceSense indexes
    $enforcesenseIndexes = docker exec infometrix-postgres psql -U postgres -d ccs_quote_tool -t -c "SELECT COUNT(*) FROM pg_indexes WHERE schemaname = 'public' AND (indexname LIKE '%debtor%' OR indexname LIKE '%enforcement%' OR indexname LIKE '%case%' OR indexname LIKE '%ledger%');" 2>&1 | ForEach-Object { $_.Trim() }
    
    if ([int]$enforcesenseIndexes -ge 5) {
        Write-Host "✅ EnforceSense indexes found: $enforcesenseIndexes" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Found $enforcesenseIndexes EnforceSense indexes (expected at least 5)" -ForegroundColor Yellow
    }
    
    Write-Host ""
}

# Check backend logs for migration messages
if ($backendRunning) {
    Write-Host "📋 Checking backend logs for migration messages..." -ForegroundColor Yellow
    $migrationLogs = docker logs infometrix-backend 2>&1 | Select-String -Pattern "migration|index" | Select-Object -Last 5
    
    if ($migrationLogs) {
        Write-Host "✅ Migration logs found:" -ForegroundColor Green
        $migrationLogs | ForEach-Object { Write-Host "   $_" }
    } else {
        Write-Host "⚠️  No migration logs found (this is OK if migrations already applied)" -ForegroundColor Yellow
    }
    Write-Host ""
}

# Check if backend is responding
if ($backendRunning) {
    Write-Host "🌐 Checking backend health..." -ForegroundColor Yellow
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -Method Get -TimeoutSec 5 -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "✅ Backend is responding" -ForegroundColor Green
        } else {
            Write-Host "❌ Backend returned status code: $($response.StatusCode)" -ForegroundColor Red
        }
    } catch {
        Write-Host "❌ Backend is not responding" -ForegroundColor Red
    }
    Write-Host ""
}

# Summary
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "📊 Verification Summary" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

if ($backendRunning -and $postgresRunning) {
    Write-Host "✅ Core services are running" -ForegroundColor Green
} else {
    Write-Host "❌ Some services are not running" -ForegroundColor Red
}

Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Yellow
Write-Host "1. Test the application in browser"
Write-Host "2. Navigate to Customers, Opportunities, Leads pages"
Write-Host "3. Verify no timeout errors occur"
Write-Host "4. Test error handling (disconnect network temporarily)"
Write-Host "5. Verify retry buttons work"
Write-Host ""

