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

### Commit 0: Baseline Safety Net ✅
- [x] Create migration branch
- [x] Document current state (this file)
- [x] Verify app runs successfully

### Commit 1: Module Registry + Module Switcher UI ⏳
- [ ] Enhance module registry
- [ ] Verify module switcher UI
- [ ] Add tenant module config stub

### Commit 2: Tenant Module Enablement ⏳
- [ ] Add module enablement middleware
- [ ] Wire module checks into routes
- [ ] Add permissions guard placeholders

### Commit 3: Helpdesk Module Boundary ⏳
- [ ] Verify Helpdesk module structure
- [ ] Ensure feature flag integration
- [ ] Update module registry

### Commit 4: Enforcement API Skeleton ⏳
- [ ] Create Enforcement API structure
- [ ] Bare server with health endpoint
- [ ] Create shared package structure
- [ ] Update docker-compose.yml

### Commit 5: EnforceSense Module Bones ⏳
- [ ] Minimal data models
- [ ] Basic endpoints
- [ ] Permission stubs
- [ ] Module registration

### Commit 6: Debtor Portal Skeleton + i18n ⏳
- [ ] Create Debtor Portal structure
- [ ] i18n setup (en/ro/cs)
- [ ] Basic routes
- [ ] Language selector component
- [ ] Update docker-compose.yml

### Commit 7: Debtor Auth Flow + Integration ⏳
- [ ] Portal session endpoints
- [ ] Debtor Portal auth integration
- [ ] Case view implementation
- [ ] Locale handling in API

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
**Status:** Commit 0 Complete, Starting Commit 1

