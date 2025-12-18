# Infometrix Platform Migration Notes

**Created:** 2025-12-17  
**Branch:** `infometrix-platform-migration`  
**Purpose:** Document current state before migrating to two-API architecture

## Current Architecture

### Services and Ports

- **Backend (Platform API)**: Port 8000
  - FastAPI application
  - Location: `backend/`
  - Main entry: `backend/main.py`
  
- **Frontend (Main UI)**: Port 3000
  - React application with TypeScript
  - Location: `frontend/`
  - Vite dev server
  
- **Admin Portal**: Port 3010
  - Vue.js application
  - Location: `admin-portal/`
  - Internal admin interface

- **PostgreSQL Database**: Port 5432
  - Database name: `ccs_quote_tool` (kept for compatibility)
  - User: `postgres`
  - Password: `postgres_password_2025`

- **Redis**: Port 6379
  - Cache and session store

- **MailHog**: Ports 1026 (SMTP), 3006 (Web UI)
  - Email testing in development

- **MinIO**: Ports 9002 (API), 9092 (Console)
  - Object storage

## Current Run Commands

### Start All Services
```bash
docker-compose up -d
```

### Start with Logs
```bash
docker-compose up
```

### Stop All Services
```bash
docker-compose down
```

### Restart Specific Service
```bash
docker-compose restart <service-name>
```

### View Logs
```bash
docker-compose logs -f <service-name>
```

## Environment Variables

Key environment variables (see `env.example` for full list):

- `ENVIRONMENT=development`
- `DEBUG=true`
- `SECRET_KEY` (required)
- `DATABASE_URL=postgresql://postgres:postgres_password_2025@postgres:5432/ccs_quote_tool`
- `REDIS_URL=redis://redis:6379/0`
- `DEFAULT_TENANT=infometrix`
- `SUPER_ADMIN_EMAIL=admin@infometrix.com`
- `SUPER_ADMIN_PASSWORD` (required)

## Current Module System

### Modules Implemented

1. **CRM Module** (always enabled)
   - Location: `frontend/src/modules/crm/`
   - Backend: Core CRM endpoints in `backend/app/api/v1/endpoints/`
   - Routes: Dashboard, Customers, Leads, Opportunities, Campaigns, Planning

2. **Helpdesk Module** (feature flag: `HELPDESK_ENABLED`)
   - Location: `frontend/src/modules/helpdesk/`
   - Backend: `backend/app/modules/helpdesk/`
   - Routes: Helpdesk, Tickets, SLA Management, Knowledge Base

3. **Settings Module** (always enabled)
   - Location: `frontend/src/modules/settings/`
   - Routes: Settings, Users, Compliance, AI Prompts, Suppliers

4. **EnforceSense Module** (skeleton, feature flag: `ENFORCESENSE_ENABLED`)
   - Frontend: `frontend/src/modules/enforcesense/` (placeholder pages)
   - Backend: `backend/app/modules/enforcesense/` (skeleton)

### Module Registry

- Frontend: `frontend/src/modules/registry.ts`
- Backend: `backend/app/modules/registry.py`
- Module API: `backend/app/api/v1/endpoints/modules.py`

## Current Database Schema

- Database: PostgreSQL 16
- Name: `ccs_quote_tool` (legacy name, kept for compatibility)
- Migrations: `backend/migrations/`
- Models: `backend/app/models/`

## Known Issues/Limitations

1. **Single API Architecture**: Currently all modules in one FastAPI backend
2. **No External Portals**: No separate client or debtor portals yet
3. **No Multilingual Support**: Frontend is English-only
4. **Module System**: Partially implemented - Helpdesk refactored, EnforceSense is skeleton
5. **Database Name**: Still uses `ccs_quote_tool` for backward compatibility

## Migration Goals

1. Split into Platform API (port 8000) and Enforcement API (port 8001)
2. Create Debtor Portal (port 3002) with multilingual support
3. Create shared packages for common code
4. Maintain backward compatibility during migration
5. Keep app runnable after each commit

## Verification Checklist

Before starting migration, verify:

- [x] Backend starts on port 8000
- [x] Frontend accessible on port 3000
- [x] Admin portal accessible on port 3010
- [x] Module switcher works
- [x] Helpdesk module accessible
- [x] All services start successfully
- [x] Database connection works
- [x] Redis connection works

## Migration Status

✅ **COMPLETE** - All 8 commits completed successfully!

See `MIGRATION_COMPLETE.md` for full summary.

### Completed Commits:
- ✅ Commit 0: Baseline (this document)
- ✅ Commit 1: Module Registry + Module Switcher UI
- ✅ Commit 2: Tenant Module Enablement + Server-Side Enforcement
- ✅ Commit 3: Helpdesk Module Boundary
- ✅ Commit 4: Create Enforcement API Skeleton
- ✅ Commit 5: EnforceSense Module "Bones" in Enforcement API
- ✅ Commit 6: Debtor Portal Skeleton + Multilingual (i18n) Wiring
- ✅ Commit 7: Debtor Auth Flow + Enforcement API Integration

