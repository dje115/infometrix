# Migration Notes - Two-API Architecture

**Created:** 2025-12-19  
**Branch:** `infometrix-platform-migration`  
**Plan File:** `C:\Users\david\.cursor\plans\two-api_architecture_migration_3ccc8ea3.plan.md`

---

## 📋 Current State (Baseline)

### Run Commands

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Rebuild after changes
docker-compose up --build -d
```

### Environment Variables

**Required:**
- `DATABASE_URL` - PostgreSQL connection (default: `postgresql://postgres:postgres_password_2025@postgres:5432/ccs_quote_tool`)
- `REDIS_URL` - Redis connection (default: `redis://redis:6379/0`)
- `SECRET_KEY` - Application secret key

**Optional (for AI features):**
- `OPENAI_API_KEY` - OpenAI API key
- `COMPANIES_HOUSE_API_KEY` - Companies House API key
- `GOOGLE_MAPS_API_KEY` - Google Maps API key

### Port Mappings

| Service | Host Port | Container Port | URL |
|---------|-----------|----------------|-----|
| Backend | 8000 | 8000 | http://localhost:8000 |
| Frontend | 3000 | 3000 | http://localhost:3000 |
| Admin Portal | 3010 | 3010 | http://localhost:3010 |
| PostgreSQL | 5432 | 5432 | localhost:5432 |
| Redis | 6379 | 6379 | localhost:6379 |
| MinIO API | 9002 | 9000 | http://localhost:9002 |
| MinIO Console | 9092 | 9001 | http://localhost:9092 |
| MailHog SMTP | 1026 | 1025 | localhost:1026 |
| MailHog UI | 3006 | 8025 | http://localhost:3006 |

### Target Ports (After Migration)

| Service | Host Port | Container Port | URL |
|---------|-----------|----------------|-----|
| Platform API | 8000 | 8000 | http://localhost:8000 |
| Enforcement API | 8001 | 8001 | http://localhost:8001 |
| Admin Portal | 3010 | 3010 | http://localhost:3010 |
| Client Portal | 3001 | 3000 | http://localhost:3001 |
| Debtor Portal | 3002 | 3000 | http://localhost:3002 |

---

## 🏗️ Current Architecture

### Directory Structure

```
infometrix/
├── backend/                    # Single FastAPI app
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── enforcesense.py
│   │   │   └── debtor_portal.py
│   │   ├── modules/
│   │   │   └── enforcesense/
│   │   └── models/
│   │       └── enforcesense.py
│   └── migrations/
├── frontend/                   # Single React app
│   └── src/
│       ├── modules/
│       │   ├── helpdesk/
│       │   └── enforcesense/
│       └── pages/
│           └── DebtorPortal*.tsx
├── admin-portal/               # Vue.js admin portal
└── docker-compose.yml
```

### Current Modules

1. **CRM Module** - Core customer relationship management
2. **Helpdesk Module** - Ticket management (`frontend/src/modules/helpdesk/`)
3. **EnforceSense Module** - Debt enforcement (integrated in main backend/frontend)
4. **Quoting Module** - Quote generation

### Database

- **Name:** `ccs_quote_tool` (kept for compatibility)
- **Type:** PostgreSQL 16
- **Connection:** `postgresql://postgres:postgres_password_2025@postgres:5432/ccs_quote_tool`

---

## ⚠️ Known Issues / Limitations

1. **Monolithic Architecture:** All modules in single backend/frontend
2. **No Separate Enforcement API:** EnforceSense is a module, not a service
3. **No Multilingual Support:** Debtor portal not multilingual yet
4. **No Separate Portals:** Client and Debtor portals are routes, not separate apps
5. **Shared Database:** All services use same database (will remain during migration)

---

## 🎯 Migration Goals

1. Split into Platform API + Enforcement API
2. Create separate external portals (Client, Debtor)
3. Implement multilingual support in Debtor Portal
4. Maintain backward compatibility during migration
5. Keep app runnable after each commit

---

## 📝 Migration Progress

### Commit 0: Baseline Safety Net ✅ COMPLETE
- [x] Create migration branch (`infometrix-platform-migration`)
- [x] Document current state (this file)
- [x] Verify app runs successfully

### Commit 1: Module Registry + Module Switcher UI ✅ COMPLETE
- [x] Enhance module registry (`frontend/src/modules/registry.ts`)
- [x] Create ModuleSwitcher component
- [x] Add tenant module config stub (`enabled_modules` field)
- [x] Update Layout to include ModuleSwitcher
- [x] Add GET /settings/tenant endpoint

### Commit 2: Tenant Module Enablement ✅ COMPLETE
- [x] Add module enablement middleware (`backend/app/core/module_dependencies.py`)
- [x] Wire module checks into helpdesk routes
- [x] Add permissions guard placeholders
- [x] Add GET /api/v1/modules endpoint

### Commit 3: Helpdesk Module Boundary ✅ COMPLETE
- [x] Verify Helpdesk module structure (already exists)
- [x] Ensure feature flag integration (HELPDESK_ENABLED exists)
- [x] Add helpdesk module index.ts

### Commit 4: Enforcement API Skeleton ✅ COMPLETE
- [x] Create Enforcement API structure (`apps/enforcement-api/`)
- [x] Bare server with health endpoint (`/health`)
- [x] Create shared package structure (`packages/shared/`)
- [x] Update docker-compose.yml (port 8001)

### Commit 5: EnforceSense Module Bones ✅ COMPLETE
- [x] Minimal data models (Case, DebtorParty)
- [x] Basic endpoints (GET/POST /enforcesense/cases, GET /enforcesense/debtors/:id)
- [x] Permission stubs (ENFORCE_READ, ENFORCE_WRITE)
- [x] Module registration in main.py

### Commit 6: Debtor Portal Skeleton + i18n ✅ COMPLETE
- [x] Create Debtor Portal structure (`apps/debtor-portal/`)
- [x] i18n setup (en/ro/cs translations)
- [x] Basic routes (/login, /case/:caseId)
- [x] Language selector component
- [x] Update docker-compose.yml (port 3002)

### Commit 7: Debtor Auth Flow + Integration ✅ COMPLETE
- [x] Portal session endpoints (POST /portal/sessions, GET /portal/cases/:caseId)
- [x] Debtor Portal auth integration (Login page calls API)
- [x] Case view implementation (CaseView page calls API)
- [x] Locale handling in API (Accept-Language header)

---

## 🔄 Testing Strategy

After each commit:
1. Verify app runs without errors
2. Test existing functionality still works
3. Test new functionality (if applicable)
4. Check logs for errors
5. Update this document with progress

---

## 📚 Reference Documents

- **Plan File:** `C:\Users\david\.cursor\plans\two-api_architecture_migration_3ccc8ea3.plan.md`
- **Architecture Target:** [`docs/ARCHITECTURE_TARGET.md`](docs/ARCHITECTURE_TARGET.md)
- **Migration Plan:** [`docs/MIGRATION_TO_TWO_API.md`](docs/MIGRATION_TO_TWO_API.md)
- **Docker Build:** [`docs/DOCKER_BUILD.md`](docs/DOCKER_BUILD.md)

---

**Last Updated:** 2025-12-19  
**Status:** ✅ ALL COMMITS COMPLETE (0-7)

## 🎉 Migration Complete!

All 7 commits from the plan file have been successfully implemented:
- ✅ Module registry and switcher UI
- ✅ Server-side module enforcement
- ✅ Enforcement API skeleton
- ✅ EnforceSense module bones
- ✅ Multilingual Debtor Portal
- ✅ Debtor portal authentication

**Next Steps:**
- Implement proper JWT authentication in Enforcement API
- Create database tables for EnforceSense models
- Add rate limiting to portal endpoints
- Implement payment processing for debtor portal

