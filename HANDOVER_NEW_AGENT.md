# 🚀 HANDOVER DOCUMENT - READ THIS FIRST

**Date:** 2025-12-19  
**Status:** EnforceSense Module - Core Development Complete  
**Next Agent:** Start here for full context

---

## ⚠️ CRITICAL: READ THIS FIRST

This document is the **primary handover document** for new agents/developers. Read this **BEFORE** starting any work.

---

## 📋 Quick Status Summary

### ✅ COMPLETED (Ready for Use)

**EnforceSense Module - 100% Core Complete:**
- ✅ Backend Services (Case Transactions, Payment Processing, Arrangements)
- ✅ All API Endpoints (20+ endpoints)
- ✅ Frontend Pages (Cases, Debtors, Clients, Payments, Arrangements)
- ✅ Financial Ledger System (immutable, single source of truth)
- ✅ Two-API Architecture Migration (Platform API + Enforcement API)
- ✅ Debtor Portal (multilingual, i18n ready)

**Infometrix Platform:**
- ✅ Multi-tenant SaaS architecture
- ✅ CRM Module (fully functional)
- ✅ Helpdesk Module (fully functional)
- ✅ Module system with feature flags
- ✅ Authentication & authorization
- ✅ Database migrations system

### 🚧 NOT BEING WORKED ON (Do NOT Start These)

**These are explicitly NOT in scope for current development:**

1. **AI Features for EnforceSense** - Note normalization, risk sanitization, summaries
   - Status: Backend service exists, but not actively being developed
   - Do NOT start unless explicitly requested

2. **Reporting System** - Case reports, payment reports, analytics
   - Status: Not started
   - Do NOT start unless explicitly requested

3. **Fee Schedules & Fee Rules** - Advanced fee calculation system
   - Status: Models exist, but not fully implemented
   - Do NOT start unless explicitly requested

4. **Fee Challenge Workflow** - UK legal requirement for fee challenges
   - Status: Models exist, but workflow not implemented
   - Do NOT start unless explicitly requested

5. **Other Platform Modules:**
   - Quoting Module enhancements
   - Lead Generation enhancements
   - Document Generation
   - Microsoft Copilot integration
   - All other pending TODOs in the main TODO list

**IMPORTANT:** Focus ONLY on what the user explicitly requests. Do NOT assume these need to be done.

---

## 🏗️ Architecture Overview

### Two-API Architecture (MIGRATION COMPLETE)

```
Infometrix/
├── apps/
│   ├── platform-api/          # Core platform + CRM + Helpdesk (port 8000)
│   ├── enforcement-api/        # EnforceSense module (port 8001) ⭐ NEW
│   ├── admin-portal/           # Vue.js admin portal (port 3010)
│   └── debtor-portal/          # Multilingual debtor portal (port 3002) ⭐ NEW
├── frontend/                    # React main frontend (port 3000)
├── backend/                     # Legacy (being migrated to platform-api)
└── packages/
    └── shared/                  # Shared types, validation, auth
```

### Services Running

| Service | Port | URL | Status |
|---------|------|-----|--------|
| Platform API | 8000 | http://localhost:8000 | ✅ Running |
| Enforcement API | 8001 | http://localhost:8001 | ✅ Running |
| Frontend | 3000 | http://localhost:3000 | ✅ Running |
| Admin Portal | 3010 | http://localhost:3010 | ✅ Running |
| Debtor Portal | 3002 | http://localhost:3002 | ✅ Running |
| PostgreSQL | 5432 | localhost:5432 | ✅ Running |
| Redis | 6379 | localhost:6379 | ✅ Running |

---

## 🐳 Docker Build Instructions

### Prerequisites

1. **Docker Desktop** installed and running
2. **Git** installed
3. **PowerShell** (Windows) or **Bash** (Linux/Mac)

### Quick Start (Development)

```powershell
# 1. Clone repository (if new workspace)
git clone <repository-url>
cd Infometrix

# 2. Copy environment file
Copy-Item .env.example .env
# Edit .env with your API keys if needed

# 3. Start all services
docker-compose up -d

# 4. Wait for services to be healthy (check logs)
docker-compose logs -f

# 5. Access services
# Frontend: http://localhost:3000
# Platform API: http://localhost:8000/docs
# Enforcement API: http://localhost:8001/docs
# Admin Portal: http://localhost:3010
# Debtor Portal: http://localhost:3002
```

### Building from Scratch

```powershell
# 1. Stop any running containers
docker-compose down

# 2. Remove volumes (WARNING: This deletes data)
docker-compose down -v

# 3. Build all images
docker-compose build --no-cache

# 4. Start services
docker-compose up -d

# 5. Check service health
docker-compose ps
docker-compose logs backend
docker-compose logs enforcement-api
docker-compose logs frontend
```

### Rebuilding Specific Service

```powershell
# Rebuild and restart a specific service
docker-compose up -d --build enforcement-api
docker-compose up -d --build frontend
docker-compose up -d --build backend
```

### Viewing Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f enforcement-api
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
```

### Stopping Services

```powershell
# Stop all services (keeps data)
docker-compose stop

# Stop and remove containers (keeps data)
docker-compose down

# Stop and remove everything including volumes (DELETES DATA)
docker-compose down -v
```

### Database Access

```powershell
# Connect to PostgreSQL
docker exec -it infometrix-postgres psql -U postgres -d ccs_quote_tool

# Or use connection string:
# postgresql://postgres:postgres_password_2025@localhost:5432/ccs_quote_tool
```

---

## 📦 Database Backup & Restore

### Creating Backup

```powershell
# Create backup directory
New-Item -ItemType Directory -Force -Path .\backups

# Backup database
docker exec infometrix-postgres pg_dump -U postgres ccs_quote_tool > backups\database_backup_$(Get-Date -Format "yyyyMMdd_HHmmss").sql

# Or using pg_dump format
docker exec infometrix-postgres pg_dump -U postgres -F c ccs_quote_tool > backups\database_backup_$(Get-Date -Format "yyyyMMdd_HHmmss").dump
```

### Restoring Backup

```powershell
# Restore from SQL file
Get-Content backups\database_backup_YYYYMMDD_HHMMSS.sql | docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool

# Restore from dump file
docker exec -i infometrix-postgres pg_restore -U postgres -d ccs_quote_tool < backups\database_backup_YYYYMMDD_HHMMSS.dump
```

### Automated Backup Script

See `scripts/backup_database.ps1` for automated backup script.

---

## 📚 Essential Documentation

### **MUST READ (In Order)**

1. **This Document** (`HANDOVER_NEW_AGENT.md`) ⭐ **YOU ARE HERE**
   - Current status, what's done, what's NOT being done

2. **Docker Build Guide** (`DOCKER_BUILD.md`)
   - Complete Docker setup instructions
   - Troubleshooting guide

3. **EnforceSense Documentation** (`docs/enforcesense/`)
   - `CORE_DOMAIN_MODEL.md` - **CRITICAL** - Core domain rules
   - `FINANCIAL_MODEL.md` - **CRITICAL** - Financial ledger system
   - `FEE_TRANSPARENCY.md` - UK legal requirements
   - `IMPLEMENTATION_PLAN.md` - Architecture and design decisions
   - `DEVELOPMENT_TODO.md` - Current TODO list

4. **Migration Notes** (`MIGRATION_NOTES.md`)
   - Two-API architecture migration status
   - What was migrated and how

### **Reference Documentation**

- `README.md` - Project overview
- `docs/enforcesense/README_ENFORCESENSE.md` - EnforceSense overview
- `docs/enforcesense/DEVELOPMENT_RULES.md` - Development rules
- `docs/ARCHITECTURE_TARGET.md` - Target architecture
- `COMPREHENSIVE_TODO_LIST.md` - Full TODO list (many items NOT in scope)

---

## 🔑 Key Technical Decisions

### 1. Financial Model (CRITICAL - DO NOT CHANGE)

- **Ledger is single source of truth** - All balances derived from ledger entries
- **Never store balances directly** - Always calculate from ledger
- **Immutable ledger entries** - Reversals create new entries, never modify originals
- **Case-level financial data** - All financial activity belongs to Case, NOT Debtor

See: `docs/enforcesense/FINANCIAL_MODEL.md`

### 2. Core Domain Model (CRITICAL - DO NOT CHANGE)

- **Debtor** - Real-world person OR legal entity (shared across cases)
- **Client** - Creditor/instructing organisation
- **Case** - Single enforcement instruction (ONE Debtor + ONE Client)
- **Financial data at Case level** - NOT at Debtor level

See: `docs/enforcesense/CORE_DOMAIN_MODEL.md`

### 3. Two-API Architecture

- **Platform API** (port 8000) - Core platform, CRM, Helpdesk
- **Enforcement API** (port 8001) - EnforceSense module only
- **Shared database** - Both APIs use same PostgreSQL instance
- **Separate authentication** - Enforcement API has its own auth middleware

### 4. Module System

- Modules registered in `backend/app/modules/registry.py`
- Feature flags control module visibility
- Tenant-level module enablement
- Server-side enforcement of module access

---

## 🛠️ Development Workflow

### Making Changes

1. **Backend Changes:**
   - Platform API: `backend/app/` or `apps/platform-api/app/`
   - Enforcement API: `apps/enforcement-api/app/`
   - Changes auto-reload in development mode

2. **Frontend Changes:**
   - Main frontend: `frontend/src/`
   - Changes auto-reload (hot-reload enabled)

3. **Database Changes:**
   - Create migration in `backend/migrations/` or `apps/enforcement-api/migrations/`
   - Run migrations manually or on startup

### Testing Changes

```powershell
# Check if services are running
docker-compose ps

# View logs for errors
docker-compose logs -f enforcement-api

# Test API endpoints
# Platform API: http://localhost:8000/docs
# Enforcement API: http://localhost:8001/docs
```

### Code Structure

```
apps/enforcement-api/
├── app/
│   ├── core/              # Config, database, dependencies
│   ├── modules/
│   │   └── enforcesense/  # EnforceSense module
│   │       ├── models.py   # SQLAlchemy models
│   │       ├── routes.py   # API endpoints
│   │       └── portal_routes.py  # Debtor portal endpoints
│   └── services/          # Business logic services
│       ├── case_transaction_service.py
│       ├── payment_processing_service.py
│       └── arrangement_service.py
├── main.py               # FastAPI app entry point
└── requirements.txt

frontend/src/modules/enforcesense/
├── pages/                # React pages
│   ├── Cases.tsx
│   ├── CaseDetail.tsx
│   ├── Debtors.tsx
│   ├── DebtorDetail.tsx
│   ├── Clients.tsx
│   ├── ClientDetail.tsx
│   ├── RecordPayment.tsx
│   ├── PaymentAllocation.tsx
│   └── CreateArrangement.tsx
└── services/
    └── enforcesenseAPI.ts  # API client
```

---

## 🐛 Common Issues & Solutions

### Services Won't Start

```powershell
# Check if ports are in use
netstat -ano | findstr :8000
netstat -ano | findstr :8001
netstat -ano | findstr :3000

# Kill process using port (Windows)
# Find PID from netstat, then:
taskkill /PID <PID> /F

# Restart Docker Desktop
# Then: docker-compose up -d
```

### Database Connection Errors

```powershell
# Check if PostgreSQL is running
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Frontend Not Loading

```powershell
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose up -d --build frontend

# Clear browser cache
```

### API Errors

```powershell
# Check API logs
docker-compose logs enforcement-api
docker-compose logs backend

# Check if database migrations ran
docker exec infometrix-postgres psql -U postgres -d ccs_quote_tool -c "\dt"
```

---

## 📝 Git Workflow

### Before Starting Work

```powershell
# 1. Check current branch
git branch

# 2. Pull latest changes
git pull origin main

# 3. Create feature branch (if needed)
git checkout -b feature/your-feature-name
```

### Committing Changes

```powershell
# 1. Check what changed
git status
git diff

# 2. Stage changes
git add .

# 3. Commit with descriptive message
git commit -m "feat: Add feature description"

# 4. Push to remote
git push origin your-branch-name
```

### Commit Message Format

Use [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation changes
- `refactor:` - Code refactoring
- `test:` - Test changes
- `chore:` - Maintenance tasks

---

## 🎯 Current Development Focus

**EnforceSense Module** is the current focus. All core functionality is complete:

- ✅ Case management
- ✅ Debtor management
- ✅ Client management
- ✅ Payment processing
- ✅ Payment arrangements
- ✅ Transaction ledger
- ✅ Notes with AI improvement

**What to work on next:**
- Only what the user explicitly requests
- Bug fixes if reported
- Performance improvements if needed
- Do NOT start new features unless explicitly requested

---

## 🔐 Environment Variables

### Required

```env
DATABASE_URL=postgresql://postgres:postgres_password_2025@postgres:5432/ccs_quote_tool
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-secret-key-here
```

### Optional (for AI features)

```env
OPENAI_API_KEY=your-openai-key
COMPANIES_HOUSE_API_KEY=your-companies-house-key
GOOGLE_MAPS_API_KEY=your-google-maps-key
```

### Enforcement API Specific

```env
ENFORCEMENT_API_PORT=8001
VITE_ENFORCEMENT_API_URL=http://localhost:8001
```

---

## 📞 Getting Help

1. **Check Documentation First:**
   - This handover document
   - `docs/enforcesense/` directory
   - `DOCKER_BUILD.md`

2. **Check Logs:**
   - `docker-compose logs -f` for all services
   - Check specific service logs

3. **Check Code:**
   - Review existing implementations
   - Follow patterns already established

---

## ✅ Handover Checklist

Before starting work, ensure you have:

- [ ] Read this document completely
- [ ] Read `DOCKER_BUILD.md`
- [ ] Read `docs/enforcesense/CORE_DOMAIN_MODEL.md`
- [ ] Read `docs/enforcesense/FINANCIAL_MODEL.md`
- [ ] Docker Desktop installed and running
- [ ] Repository cloned
- [ ] `.env` file configured
- [ ] Services running (`docker-compose up -d`)
- [ ] Can access frontend at http://localhost:3000
- [ ] Can access API docs at http://localhost:8000/docs and http://localhost:8001/docs
- [ ] Database backup created (see `DATABASE_BACKUP.md`)

---

## 🚨 Important Reminders

1. **DO NOT** modify the financial model without reading `FINANCIAL_MODEL.md` first
2. **DO NOT** change core domain model without reading `CORE_DOMAIN_MODEL.md` first
3. **DO NOT** start features not explicitly requested
4. **DO** follow existing code patterns
5. **DO** test changes before committing
6. **DO** create database backups before major changes

---

**Last Updated:** 2025-12-19  
**Status:** Ready for Development  
**Next Steps:** Wait for explicit user instructions

