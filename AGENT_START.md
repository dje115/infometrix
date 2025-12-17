# Infometrix Platform - Agent Start Guide

## 🎯 Project Overview

**Infometrix** is a multi-tenant CRM platform with modular architecture. It has been migrated from CCS Quote Tool v2 and rebranded.

## 📁 Project Structure

```
Infometrix/
├── backend/              # FastAPI backend
│   ├── app/
│   │   ├── modules/      # Module system (Helpdesk, EnforceSense, etc.)
│   │   ├── api/v1/      # API endpoints
│   │   ├── core/        # Core services (feature flags, permissions)
│   │   └── models/      # Database models
│   └── migrations/      # Database migrations
├── frontend/             # React frontend
├── admin-portal/         # Vue.js admin portal
├── modules/              # External modules (EnforceSense submodule)
└── docker-compose.yml    # Docker configuration
```

## 🚀 Quick Start

### Development Mode

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

**Access:**
- Frontend: http://localhost:3000
- Admin Portal: http://localhost:3010
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

**Default Login:**
- Email: `admin@ccs.com`
- Password: `admin123`

## 🏗️ Architecture

### Module System

Modules are feature-flagged and can be enabled/disabled per tenant:

- **Helpdesk** (`HELPDESK_ENABLED`) - Ticket management, SLA tracking
- **EnforceSense** (`ENFORCESENSE_ENABLED`) - Debt recovery module
- **Quoting** (`QUOTING_ENABLED`) - Quotes and proposals
- **Sales** (`SALES_ENABLED`) - Sales CRM features

### Key Components

1. **Module Registry** (`backend/app/modules/registry.py`)
   - Central registry for all modules
   - Feature flag checking
   - Permission management

2. **Feature Flags** (`backend/app/core/feature_flags.py`)
   - Tenant-level feature flags
   - Stored in `tenants.feature_flags` JSONB column

3. **Navigation Groups**
   - Sales / CRM (core)
   - Helpdesk (feature-flagged)
   - Quoting & Proposals (feature-flagged)
   - EnforceSense (feature-flagged)
   - Settings

## 📝 Important Notes

### Database
- **Database name:** `ccs_quote_tool` (kept for compatibility)
- **Table names:** Unchanged (compatibility maintained)
- **Migrations:** Located in `backend/migrations/`

### Git Repository
- **Remote:** https://github.com/dje115/infometrix
- **Local:** `C:\Users\david\Documents\Infometrix`

### Module Development
- Modules extend `BaseModule` class
- Register in `backend/app/modules/__init__.py`
- Routes mounted at `/api/v1/modules/{module_id}/`
- Permissions: `{module_id}:{action}`

## 🔧 Common Tasks

### Apply Database Migration

```powershell
Get-Content "backend/migrations/add_feature_flags.sql" | docker-compose exec -T postgres psql -U postgres -d ccs_quote_tool
```

### Build Frontend

```powershell
cd frontend
npm install
npm run build
```

### Run Tests

```powershell
# Backend
cd backend
python -m pytest tests/

# Frontend
cd frontend
npm run lint
npm run type-check
```

## 📚 Documentation

- **MIGRATION_PLAN.md** - Complete migration plan
- **QUICK_START_MIGRATION.md** - Quick reference
- **DELIVERABLES.md** - Full checklist
- **README.md** - Main documentation

## 🎯 Current Status

✅ **Completed:**
- Code rebranded to Infometrix
- Module system created
- Feature flags implemented
- Helpdesk module registered
- EnforceSense module scaffolded
- Database migration applied
- **Database initialized with system tenant and 34 AI prompts**
- **All services running (Frontend, Admin, Backend, Celery, MailHog, MinIO)**

🔄 **In Progress:**
- Frontend navigation grouping (pending)
- Helpdesk module isolation (Milestone 1)

## 🚨 Important Reminders

1. **Database compatibility:** Keep `ccs_quote_tool` name
2. **Incremental changes:** Test after each modification
3. **Feature flags:** Use for module enable/disable
4. **Permissions:** Follow `{module}:{action}` format

---

**Last Updated:** 2025-12-17  
**Platform Version:** 3.0.6  
**Status:** ✅ Ready for Development - All services running, database seeded

