# Database Backup Script for Infometrix
# Creates timestamped SQL backup of the database

$ErrorActionPreference = "Stop"

# Get script directory and project root
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
$backupDir = Join-Path $projectRoot "backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $backupDir "database_backup_$timestamp.sql"

# Create backup directory if it doesn't exist
Write-Host "Creating backup directory: $backupDir" -ForegroundColor Cyan
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

# Check if PostgreSQL container is running
Write-Host "Checking PostgreSQL container..." -ForegroundColor Cyan
$containerRunning = docker ps --filter "name=infometrix-postgres" --format "{{.Names}}"

if (-not $containerRunning) {
    Write-Host "ERROR: PostgreSQL container is not running!" -ForegroundColor Red
    Write-Host "Start services with: docker-compose up -d" -ForegroundColor Yellow
    exit 1
}

# Create backup
Write-Host "Creating database backup..." -ForegroundColor Green
Write-Host "Backup file: $backupFile" -ForegroundColor Cyan

try {
    docker exec infometrix-postgres pg_dump -U postgres ccs_quote_tool > $backupFile
    
    if (Test-Path $backupFile) {
        $fileSize = (Get-Item $backupFile).Length / 1MB
        Write-Host "`n✅ Backup created successfully!" -ForegroundColor Green
        Write-Host "   File: $backupFile" -ForegroundColor White
        Write-Host "   Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor White
        Write-Host "   Timestamp: $timestamp" -ForegroundColor White
        
        # List recent backups
        Write-Host "`nRecent backups:" -ForegroundColor Cyan
        Get-ChildItem $backupDir -Filter "database_backup_*.sql" | 
            Sort-Object LastWriteTime -Descending | 
            Select-Object -First 5 | 
            ForEach-Object {
                $size = $_.Length / 1MB
                Write-Host "   $($_.Name) - $([math]::Round($size, 2)) MB - $($_.LastWriteTime)" -ForegroundColor Gray
            }
    } else {
        Write-Host "`n❌ Backup file was not created!" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "`n❌ Backup failed: $_" -ForegroundColor Red
    exit 1
}

Write-Host "`n✅ Backup complete!" -ForegroundColor Green

