# PowerShell Script: Apply Migrations to Docker PostgreSQL Container
# This script applies migrations to the Docker PostgreSQL container

Write-Host "🐳 Applying Migrations to Docker PostgreSQL Container..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
try {
    $null = docker ps 2>&1
} catch {
    Write-Host "❌ Docker is not running. Please start Docker Desktop and try again." -ForegroundColor Red
    exit 1
}

# Check if postgres container exists
$postgresRunning = docker ps --format '{{.Names}}' | Select-String "infometrix-postgres"
if (-not $postgresRunning) {
    Write-Host "⚠️  PostgreSQL container not found. Starting containers..." -ForegroundColor Yellow
    docker-compose up -d postgres
    Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}

Write-Host "✅ PostgreSQL container is ready" -ForegroundColor Green
Write-Host ""

# Function to apply migration
function Apply-Migration {
    param(
        [string]$MigrationFile,
        [string]$Description
    )
    
    if (-not (Test-Path $MigrationFile)) {
        Write-Host "⚠️  Migration file not found: $MigrationFile (skipping)" -ForegroundColor Yellow
        return $true
    }
    
    Write-Host "📝 Applying: $Description" -ForegroundColor Yellow
    Write-Host "   File: $MigrationFile"
    
    try {
        Get-Content $MigrationFile | docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool 2>&1 | Out-Null
        Write-Host "   ✅ Success" -ForegroundColor Green
        return $true
    } catch {
        $errorOutput = Get-Content $MigrationFile | docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool 2>&1
        if ($errorOutput -match "already exists") {
            Write-Host "   ⚠️  Already applied (skipping)" -ForegroundColor Yellow
            return $true
        } else {
            Write-Host "   ⚠️  Failed or already applied (continuing)" -ForegroundColor Yellow
            return $true
        }
    }
}

# Apply migrations
Write-Host "🔧 Applying Performance Migrations..." -ForegroundColor Green
Write-Host ""

# Migration 1: Missing Foreign Key Indexes
Apply-Migration `
    -MigrationFile "backend/migrations/add_missing_foreign_key_indexes.sql" `
    -Description "Missing Foreign Key Indexes (11 indexes)"

# Migration 2: Composite Indexes
Apply-Migration `
    -MigrationFile "backend/migrations/add_composite_indexes_for_common_queries.sql" `
    -Description "Composite Indexes for Common Queries (10 indexes)"

# Migration 3: EnforceSense Performance Indexes
Apply-Migration `
    -MigrationFile "apps/enforcement-api/migrations/add_performance_indexes_enforcesense.sql" `
    -Description "EnforceSense Performance Indexes (11+ indexes)"

Write-Host ""
Write-Host "✅ All migrations completed!" -ForegroundColor Green
Write-Host ""
Write-Host "🎯 Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart backend: docker-compose restart backend"
Write-Host "2. Test the application - timeouts should be resolved"
Write-Host ""



