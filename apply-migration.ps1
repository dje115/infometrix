# Apply Feature Flags Migration Script
# This script applies the feature_flags migration to the database

Write-Host "🔧 Applying Feature Flags Migration..." -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Host "📡 Checking Docker..." -ForegroundColor Yellow
$dockerRunning = docker ps 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not running or not accessible!" -ForegroundColor Red
    Write-Host "Please start Docker Desktop and try again." -ForegroundColor Yellow
    exit 1
}
Write-Host "✓ Docker is running" -ForegroundColor Green
Write-Host ""

# Check if postgres container exists
Write-Host "📦 Checking PostgreSQL container..." -ForegroundColor Yellow
$postgresRunning = docker-compose ps postgres 2>&1 | Select-String "Up"
if (-not $postgresRunning) {
    Write-Host "⚠️  PostgreSQL container not running. Starting it..." -ForegroundColor Yellow
    docker-compose up -d postgres
    Write-Host "⏳ Waiting for PostgreSQL to be ready..." -ForegroundColor Yellow
    Start-Sleep -Seconds 10
}
Write-Host "✓ PostgreSQL container is ready" -ForegroundColor Green
Write-Host ""

# Apply migration
Write-Host "📝 Applying migration: add_feature_flags.sql" -ForegroundColor Yellow
Get-Content "backend/migrations/add_feature_flags.sql" | docker-compose exec -T postgres psql -U postgres -d ccs_quote_tool

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "✅ Migration applied successfully!" -ForegroundColor Green
    Write-Host ""
    
    # Verify migration
    Write-Host "🔍 Verifying migration..." -ForegroundColor Yellow
    docker-compose exec -T postgres psql -U postgres -d ccs_quote_tool -c "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tenants' AND column_name = 'feature_flags';"
    
    Write-Host ""
    Write-Host "✅ Feature flags column added to tenants table!" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "❌ Migration failed!" -ForegroundColor Red
    Write-Host "Please check the error messages above." -ForegroundColor Yellow
    exit 1
}

