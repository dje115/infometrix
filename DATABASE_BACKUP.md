# 💾 Database Backup & Restore Guide

Complete guide for backing up and restoring the Infometrix database.

---

## ⚠️ IMPORTANT

- **Database Name:** `ccs_quote_tool` (kept for compatibility)
- **Always backup before major changes**
- **Backups are stored in `backups/` directory**
- **Repository is private** - safe to commit backups

---

## 🔄 Quick Backup

### Automated Backup Script

```powershell
# Run backup script (creates timestamped backup)
.\scripts\backup_database.ps1

# Backup will be saved to: backups/database_backup_YYYYMMDD_HHMMSS.sql
```

### Manual Backup

```powershell
# Create backups directory
New-Item -ItemType Directory -Force -Path .\backups

# Create SQL backup
docker exec infometrix-postgres pg_dump -U postgres ccs_quote_tool > backups\database_backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Create compressed dump backup (recommended)
docker exec infometrix-postgres pg_dump -U postgres -F c -f /tmp/backup.dump ccs_quote_tool
docker cp infometrix-postgres:/tmp/backup.dump backups\database_backup_$(Get-Date -Format "yyyyMMdd_HHmmss").dump
```

---

## 📥 Restore from Backup

### Restore SQL Backup

```powershell
# Restore from SQL file
Get-Content backups\database_backup_YYYYMMDD_HHMMSS.sql | docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool

# Or using psql directly
docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool < backups\database_backup_YYYYMMDD_HHMMSS.sql
```

### Restore Dump Backup

```powershell
# Copy dump file to container
docker cp backups\database_backup_YYYYMMDD_HHMMSS.dump infometrix-postgres:/tmp/restore.dump

# Restore from dump
docker exec infometrix-postgres pg_restore -U postgres -d ccs_quote_tool -c /tmp/restore.dump

# Clean up
docker exec infometrix-postgres rm /tmp/restore.dump
```

### Restore to New Database

```powershell
# Create new database
docker exec -i infometrix-postgres psql -U postgres -c "CREATE DATABASE ccs_quote_tool_new;"

# Restore to new database
Get-Content backups\database_backup_YYYYMMDD_HHMMSS.sql | docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool_new
```

---

## 🔄 Backup Strategies

### Daily Automated Backup

Create a scheduled task (Windows Task Scheduler) or cron job:

```powershell
# PowerShell script for Task Scheduler
# File: scripts\scheduled_backup.ps1

$backupDir = ".\backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = "$backupDir\database_backup_$timestamp.sql"

New-Item -ItemType Directory -Force -Path $backupDir | Out-Null
docker exec infometrix-postgres pg_dump -U postgres ccs_quote_tool > $backupFile

# Keep only last 7 days of backups
Get-ChildItem $backupDir -Filter "database_backup_*.sql" | 
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-7) } | 
    Remove-Item
```

### Before Major Changes

Always backup before:
- Running migrations
- Updating schema
- Bulk data changes
- Testing destructive operations

```powershell
# Quick pre-change backup
docker exec infometrix-postgres pg_dump -U postgres ccs_quote_tool > backups\pre_change_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

---

## 📊 Backup File Formats

### SQL Format (`.sql`)

**Pros:**
- Human-readable
- Easy to inspect
- Can edit if needed

**Cons:**
- Larger file size
- Slower restore

**Use when:**
- Need to inspect/edit data
- Small databases
- One-time backups

### Custom Dump Format (`.dump`)

**Pros:**
- Compressed (smaller)
- Faster restore
- Can restore specific tables

**Cons:**
- Binary format (not readable)
- Requires pg_restore

**Use when:**
- Regular backups
- Large databases
- Production backups

---

## 🔍 Verify Backup

### Check Backup File

```powershell
# Check SQL backup size
Get-Item backups\database_backup_*.sql | Select-Object Name, Length, LastWriteTime

# Check if backup contains data
Select-String -Path backups\database_backup_*.sql -Pattern "CREATE TABLE" | Measure-Object
```

### Test Restore

```powershell
# Create test database
docker exec -i infometrix-postgres psql -U postgres -c "CREATE DATABASE test_restore;"

# Restore to test database
Get-Content backups\database_backup_YYYYMMDD_HHMMSS.sql | docker exec -i infometrix-postgres psql -U postgres -d test_restore

# Verify tables exist
docker exec -i infometrix-postgres psql -U postgres -d test_restore -c "\dt"

# Drop test database
docker exec -i infometrix-postgres psql -U postgres -c "DROP DATABASE test_restore;"
```

---

## 📦 Backup to GitHub

Since the repository is private, backups can be committed:

```powershell
# 1. Create backup
.\scripts\backup_database.ps1

# 2. Add backup to git
git add backups/database_backup_*.sql

# 3. Commit
git commit -m "chore: Add database backup"

# 4. Push
git push origin main
```

### Backup Retention

Keep backups in `backups/` directory:
- **Daily backups:** Keep last 7 days
- **Weekly backups:** Keep last 4 weeks
- **Monthly backups:** Keep last 3 months

---

## 🗄️ Database Schema Backup

### Backup Schema Only (No Data)

```powershell
# Schema only backup
docker exec infometrix-postgres pg_dump -U postgres -s ccs_quote_tool > backups\schema_backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

### Backup Data Only (No Schema)

```powershell
# Data only backup
docker exec infometrix-postgres pg_dump -U postgres -a ccs_quote_tool > backups\data_backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql
```

---

## 🔐 Backup Security

### Encrypted Backups

```powershell
# Create encrypted backup (requires GPG)
docker exec infometrix-postgres pg_dump -U postgres ccs_quote_tool | gpg -c > backups\database_backup_$(Get-Date -Format "yyyyMMdd_HHMMSS").sql.gpg

# Restore encrypted backup
gpg -d backups\database_backup_YYYYMMDD_HHMMSS.sql.gpg | docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool
```

### Backup Permissions

```powershell
# Set backup directory permissions (Linux/Mac)
chmod 700 backups/

# Windows: Use file system permissions
```

---

## 📋 Backup Checklist

Before committing to GitHub:

- [ ] Backup created successfully
- [ ] Backup file size is reasonable (> 0 bytes)
- [ ] Backup contains expected tables
- [ ] Backup tested (restore to test database)
- [ ] Backup file named with timestamp
- [ ] Old backups cleaned up (if needed)

---

## 🚨 Emergency Restore

### Complete Database Loss

```powershell
# 1. Stop services
docker-compose stop

# 2. Remove database volume (if needed)
docker-compose down -v postgres

# 3. Start PostgreSQL
docker-compose up -d postgres

# 4. Wait for PostgreSQL to be ready
docker-compose logs -f postgres

# 5. Restore from backup
Get-Content backups\database_backup_LATEST.sql | docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool

# 6. Start all services
docker-compose up -d
```

---

## 📝 Backup Script

Create `scripts/backup_database.ps1`:

```powershell
# Database Backup Script
$backupDir = Join-Path $PSScriptRoot "..\backups"
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$backupFile = Join-Path $backupDir "database_backup_$timestamp.sql"

# Create backup directory
New-Item -ItemType Directory -Force -Path $backupDir | Out-Null

Write-Host "Creating database backup..." -ForegroundColor Green
docker exec infometrix-postgres pg_dump -U postgres ccs_quote_tool > $backupFile

if (Test-Path $backupFile) {
    $fileSize = (Get-Item $backupFile).Length / 1MB
    Write-Host "Backup created: $backupFile ($([math]::Round($fileSize, 2)) MB)" -ForegroundColor Green
} else {
    Write-Host "Backup failed!" -ForegroundColor Red
    exit 1
}
```

---

**Last Updated:** 2025-12-19  
**Backup Location:** `backups/` directory  
**Repository:** Private - safe to commit backups

