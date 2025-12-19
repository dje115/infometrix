# Migration Plan: Monolithic to Two-API Architecture

**Version:** 3.6.0  
**Last Updated:** 2025-12-19

---

## 📊 Current State vs Target State

### Current (Monolithic Modular)

```
infometrix/
├── backend/                    # Single FastAPI app
│   ├── app/
│   │   ├── api/v1/endpoints/
│   │   │   ├── enforcesense.py  # EnforceSense endpoints
│   │   │   └── debtor_portal.py # Debtor portal endpoints
│   │   └── modules/
│   │       └── enforcesense/    # EnforceSense module
│   └── migrations/
├── frontend/                    # Single React app
│   └── src/
│       ├── modules/enforcesense/
│       └── pages/DebtorPortal*.tsx
└── admin-portal/                # Vue.js admin portal
```

**Ports:**
- Backend: 8000
- Frontend: 3000
- Admin Portal: 3010

### Target (Two-API Architecture)

```
infometrix/
├── apps/
│   ├── platform-api/           # Platform API (port 8000)
│   ├── enforcement-api/         # Enforcement API (port 8001)
│   ├── admin-portal/            # Admin portal (port 3010)
│   ├── client-portal/           # Client portal (port 3011)
│   └── debtor-portal/           # Debtor portal (port 3012, multilingual)
├── packages/
│   ├── shared/                  # Shared types, auth, tenancy
│   └── ui/                      # Shared UI components
└── docker-compose.yml
```

---

## 🎯 Migration Commit Plan

### Commit 0 — Baseline Safety Net

**Goal:** Freeze a "known good" starting point

**Actions:**
- Create branch: `infometrix-platform-migration`
- Document current run steps
- Document env vars and ports
- Create `MIGRATION_NOTES.md` with current state

**Verification:**
- ✅ App still runs
- ✅ All tests pass

---

### Commit 1 — Add Module Registry + Module Switcher UI

**Goal:** Put the "module tab" concept in place without breaking anything

**Actions:**
- Add `src/platform/modules/registry.ts`:
  - `crm` module defined and enabled by default
  - `helpdesk` module defined (initially points to existing routes)
- Implement UI:
  - Module switcher at top of left nav
  - Context menu below, driven by registry
  - Everything still maps to existing pages
- Add tenant module config stub:
  - `tenant.enabledModules` default to `["crm","helpdesk"]`

**Files Changed:**
- `frontend/src/platform/modules/registry.ts` (new)
- `frontend/src/components/Layout.tsx` (module switcher UI)
- `backend/app/models/tenant.py` (add `enabledModules` field)

**Verification:**
- ✅ App still runs
- ✅ Nav shows module switcher (even if both map to same routes)

---

### Commit 2 — Tenant Module Enablement + Server-Side Enforcement

**Goal:** Make "enabled modules" real (even if seeded)

**Actions:**
- Add `enabledModules` to tenant model (DB migration)
- Add middleware guard:
  - For each route, check `moduleKey` is enabled for tenant
- Add simple permissions guard placeholders

**Files Changed:**
- `backend/app/models/tenant.py` (add `enabledModules`)
- `backend/migrations/add_enabled_modules.sql` (new)
- `backend/app/core/middleware.py` (module guard)

**Verification:**
- ✅ App still runs
- ✅ Nothing changes for existing tenant (default includes CRM/helpdesk)

---

### Commit 3 — Helpdesk Module Boundary (Move UI Only)

**Goal:** First real module split, without changing behavior

**Actions:**
- Create `src/modules/helpdesk/`:
  - `pages/`
  - `routes.ts`
  - `nav.ts`
- Move existing helpdesk UI components/pages into that folder
- Keep imports working via minimal path fixes
- Register helpdesk routes through registry
- Add feature flag key: `HELPDESK_ENABLED`

**Files Changed:**
- `frontend/src/modules/helpdesk/` (new structure)
- `frontend/src/App.tsx` (update imports)
- `frontend/src/platform/modules/registry.ts` (register helpdesk)

**Verification:**
- ✅ App still runs
- ✅ Helpdesk tab switches to its own menu and screens

---

### Commit 4 — Create Enforcement API Skeleton

**Goal:** Add a second API service but don't route production traffic to it yet

**Actions:**
- Create `apps/enforcement-api/`:
  - Bare server with `/health` endpoint
  - Shared auth/tenant middleware placeholders
  - Config loader + env template
- Create `packages/shared/`:
  - `TenantContext` type
  - Auth claims types
  - Common validation helpers

**Files Changed:**
- `apps/enforcement-api/` (new)
- `packages/shared/` (new)
- `docker-compose.yml` (add enforcement-api service, port 8001)

**Verification:**
- ✅ App still runs
- ✅ Enforcement API can start independently (`docker-compose up enforcement-api`)

---

### Commit 5 — EnforceSense Module "Bones" in Enforcement API

**Goal:** Create minimum endpoints/entities to prove the boundary

**Actions:**
- In `apps/enforcement-api/src/modules/enforcesense/`:
  - Minimal data model:
    - `Case` (id, tenantId, clientAccountId, debtorPartyId, status, createdAt)
    - `DebtorParty` (person/company, name, addressRef, preferredLanguage)
  - Endpoints:
    - `GET /enforcesense/cases` (tenant scoped)
    - `POST /enforcesense/cases`
    - `GET /enforcesense/debtors/:id`
  - Permissions stubs: `ENFORCE_READ`, `ENFORCE_WRITE`

**Files Changed:**
- `apps/enforcement-api/src/modules/enforcesense/` (new)
- `apps/enforcement-api/src/models/` (new)

**Verification:**
- ✅ Enforcement API runs
- ✅ No UI depends on it yet

---

### Commit 6 — Add Debtor Portal Skeleton + Multilingual (i18n) Wiring

**Goal:** Multilingual from day 1, even if only 2 pages

**Actions:**
- Create `apps/debtor-portal/`:
  - Routes:
    - `/login` (magic link / code entry placeholder)
    - `/case/:caseId` (read-only skeleton)
  - i18n:
    - Translation files: `en.json`, `ro.json` (at minimum)
    - Language detection + manual language switch
    - No hardcoded user-facing strings

**Files Changed:**
- `apps/debtor-portal/` (new)
- `apps/debtor-portal/locales/en.json` (new)
- `apps/debtor-portal/locales/ro.json` (new)
- `docker-compose.yml` (add debtor-portal service, port 3012)

**Verification:**
- ✅ Debtor portal runs standalone
- ✅ Language switching works

---

### Commit 7 — Debtor Auth Flow + Enforcement API Integration

**Goal:** Working end-to-end path into a case view

**Actions:**
- Enforcement API:
  - Create "debtor portal session" endpoints:
    - `POST /portal/sessions` (create session for case/debtor, returns short-lived token)
    - `GET /portal/cases/:caseId` (requires portal token, tenant-scoped)
  - Add strict expiry + rate limiting placeholders
- Debtor portal:
  - Consume portal endpoint
  - Display case basics (localized labels via i18n)
  - Store locale per session and pass to API

**Files Changed:**
- `apps/enforcement-api/src/api/v1/endpoints/portal.py` (new)
- `apps/debtor-portal/src/services/api.ts` (new)
- `apps/debtor-portal/src/pages/CaseDetail.tsx` (update)

**Verification:**
- ✅ Debtor portal can load case data from Enforcement API
- ✅ Localized labels work

---

## 🔄 Data Migration Strategy

### Step 1: Move EnforceSense Data

1. Create new tables in same database (for now)
2. Migrate data from `backend/app/models/enforcesense.py` to `apps/enforcement-api/src/models/`
3. Update foreign key references to use Platform API IDs

### Step 2: Split Services

1. Move EnforceSense endpoints from `backend/app/api/v1/endpoints/enforcesense.py` to `apps/enforcement-api/`
2. Update frontend to call Enforcement API (port 8001) instead of Platform API
3. Update debtor portal to call Enforcement API

### Step 3: Separate Deployments

1. Update `docker-compose.yml` to run both APIs
2. Update environment variables
3. Test inter-service communication

---

## 📋 Verification Checklist

After each commit:

- [ ] App still runs
- [ ] All existing tests pass
- [ ] No breaking changes to existing functionality
- [ ] New features work as expected
- [ ] Documentation updated

---

## 🚨 Breaking Changes to Avoid

1. **Don't move Platform API endpoints yet** - Keep existing routes working
2. **Don't change database schema abruptly** - Use migrations
3. **Don't break existing frontend routes** - Keep backward compatibility
4. **Don't remove old code until new code is proven** - Use feature flags

---

## 📝 TODOs for Later Hardening

1. **Inter-Service Communication:**
   - Add caching layer for cross-API calls
   - Implement retry logic
   - Add circuit breakers

2. **Security:**
   - Implement strict rate limiting on debtor portal
   - Add IP allowlisting for internal APIs
   - Implement API key rotation

3. **Performance:**
   - Add Redis caching for cross-API lookups
   - Implement connection pooling
   - Add monitoring/observability

4. **Events (Phase 2):**
   - Implement event/outbox pattern
   - Add event handlers for Account updated, Address changed, etc.
   - Add event replay capability

---

**Last Updated:** 2025-12-19  
**Version:** 3.6.0

