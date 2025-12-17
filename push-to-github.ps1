# Infometrix - Push to GitHub Script
# This script adds all files, commits, and pushes to the new GitHub repository

Write-Host "🚀 Pushing Infometrix to GitHub..." -ForegroundColor Cyan
Write-Host ""

# Check if we're in the right directory
if (-not (Test-Path "backend")) {
    Write-Host "❌ Error: Not in Infometrix project root!" -ForegroundColor Red
    exit 1
}

# Check git remote
Write-Host "📡 Checking git remote..." -ForegroundColor Yellow
$remote = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Git remote not configured!" -ForegroundColor Red
    Write-Host "Run: git remote add origin https://github.com/dje115/infometrix.git" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Remote: $remote" -ForegroundColor Green
Write-Host ""

# Add all files
Write-Host "📦 Adding files to git..." -ForegroundColor Yellow
git add .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to add files!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Files added" -ForegroundColor Green
Write-Host ""

# Commit
Write-Host "💾 Committing changes..." -ForegroundColor Yellow
$commitMessage = "Initial commit: Migrate from CCS Quote Tool v2 to Infometrix

- Rebranded to Infometrix platform
- Added module system with feature flags
- Registered Helpdesk and EnforceSense modules
- Updated all package names and Docker services
- Created module registry and base classes
- Added database migration for feature flags"

git commit -m $commitMessage
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Error: Failed to commit!" -ForegroundColor Red
    exit 1
}
Write-Host "✓ Changes committed" -ForegroundColor Green
Write-Host ""

# Push to GitHub
Write-Host "🚀 Pushing to GitHub..." -ForegroundColor Yellow
Write-Host "Repository: https://github.com/dje115/infometrix" -ForegroundColor Cyan
Write-Host ""

git push -u origin master
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "⚠️  Push failed. Trying 'main' branch instead..." -ForegroundColor Yellow
    git branch -M main
    git push -u origin main
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Error: Failed to push to GitHub!" -ForegroundColor Red
        Write-Host "Please check your GitHub authentication and try again." -ForegroundColor Yellow
        exit 1
    }
}

Write-Host ""
Write-Host "✅ Successfully pushed to GitHub!" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next steps:" -ForegroundColor Cyan
Write-Host "1. Verify at: https://github.com/dje115/infometrix" -ForegroundColor White
Write-Host "2. Apply database migration (see AGENT_START.md)" -ForegroundColor White
Write-Host "3. Test the application: docker-compose up -d --build" -ForegroundColor White
Write-Host ""

