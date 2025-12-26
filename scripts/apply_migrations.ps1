# PowerShell Migration Application Script
# This script applies all performance-related database migrations

param(
    [string]$DbUser = "postgres",
    [string]$DbName = "ccs_quote_tool",
    [string]$DbHost = "localhost",
    [string]$DbPort = "5432",
    [string]$DbPassword = ""
)

Write-Host "========================================" -ForegroundColor Green
Write-Host "Infometrix Database Migration Script" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""

# Check if psql is available
try {
    $null = Get-Command psql -ErrorAction Stop
} catch {
    Write-Host "Error: psql command not found. Please install PostgreSQL client tools." -ForegroundColor Red
    exit 1
}

# Function to apply migration
function Apply-Migration {
    param(
        [string]$MigrationFile,
        [string]$Description
    )
    
    if (-not (Test-Path $MigrationFile)) {
        Write-Host "Error: Migration file not found: $MigrationFile" -ForegroundColor Red
        return $false
    }
    
    Write-Host "Applying: $Description" -ForegroundColor Yellow
    Write-Host "File: $MigrationFile"
    
    $env:PGPASSWORD = $DbPassword
    $psqlArgs = @(
        "-h", $DbHost,
        "-p", $DbPort,
        "-U", $DbUser,
        "-d", $DbName,
        "-f", $MigrationFile
    )
    
    try {
        & psql $psqlArgs
        if ($LASTEXITCODE -eq 0) {
            Write-Host "✓ Successfully applied: $Description" -ForegroundColor Green
            Write-Host ""
            return $true
        } else {
            Write-Host "✗ Failed to apply: $Description" -ForegroundColor Red
            Write-Host ""
            return $false
        }
    } catch {
        Write-Host "✗ Failed to apply: $Description" -ForegroundColor Red
        Write-Host "Error: $_" -ForegroundColor Red
        Write-Host ""
        return $false
    } finally {
        Remove-Item Env:\PGPASSWORD -ErrorAction SilentlyContinue
    }
}

# Get database password if not provided
if ([string]::IsNullOrEmpty($DbPassword)) {
    Write-Host "Database password not provided. You will be prompted for the password." -ForegroundColor Yellow
    Write-Host ""
}

# Apply migrations in order
Write-Host "Starting migration process..." -ForegroundColor Green
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

Write-Host "========================================" -ForegroundColor Green
Write-Host "All migrations completed!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "1. Restart your backend server"
Write-Host "2. Test the application - timeouts should be resolved"
Write-Host "3. Monitor query performance"
Write-Host ""

