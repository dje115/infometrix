# Next Steps - Development Roadmap

**Last Updated:** 2025-12-19  
**Current Status:** Migration foundation complete, ready for implementation

---

## 🎯 Current State

✅ **Completed:**
- All 7 migration commits executed
- Module registry and switcher UI working
- Admin portal module selection fixed
- Frontend module filtering working
- Enforcement API skeleton created (port 8001)
- Debtor Portal skeleton created (port 3002, multilingual)
- Shared packages structure created

⚠️ **Placeholders/Incomplete:**
- Enforcement API authentication (returns 501)
- Enforcement API database tables (not created)
- Debtor Portal token validation (in-memory only)
- EnforceSense logic still in Platform API

---

## 🚀 Immediate Next Steps (Priority Order)

### Phase 1: Enforcement API Foundation (HIGH PRIORITY)

#### 1.1 Create Shared Authentication Library
**Goal:** Centralize JWT validation and tenant resolution for both APIs

**Tasks:**
- [ ] Create `packages/shared/auth/jwt.py` with JWT validation functions
- [ ] Create `packages/shared/auth/tenant.py` with tenant resolution
- [ ] Port JWT logic from `backend/app/core/security.py`
- [ ] Port tenant logic from `backend/app/core/dependencies.py`
- [ ] Update both APIs to use shared library

**Files to Create:**
- `packages/shared/auth/__init__.py`
- `packages/shared/auth/jwt.py`
- `packages/shared/auth/tenant.py`

**Files to Update:**
- `apps/enforcement-api/app/core/dependencies.py`
- `backend/app/core/dependencies.py` (refactor to use shared)

**Estimated Time:** 2-3 hours

---

#### 1.2 Implement Enforcement API Authentication
**Goal:** Enable JWT authentication in Enforcement API

**Tasks:**
- [ ] Update `apps/enforcement-api/app/core/dependencies.py`
- [ ] Implement `get_current_user()` using shared auth library
- [ ] Implement `get_current_tenant()` using shared auth library
- [ ] Test authentication with Platform API tokens
- [ ] Add authentication to all Enforcement API endpoints

**Files to Update:**
- `apps/enforcement-api/app/core/dependencies.py`
- `apps/enforcement-api/app/modules/enforcesense/routes.py`
- `apps/enforcement-api/app/modules/enforcesense/portal_routes.py`

**Estimated Time:** 1-2 hours

---

#### 1.3 Create Database Tables for Enforcement API
**Goal:** Create EnforceSense tables in the shared database

**Tasks:**
- [ ] Review `backend/migrations/add_enforcesense_tables.sql`
- [ ] Create migration script for Enforcement API (or use existing)
- [ ] Ensure tables: `debtors`, `enforcement_cases`, `enforcement_clients`, `case_transactions`
- [ ] Run migration on database initialization
- [ ] Verify tables exist and are accessible

**Files to Create/Update:**
- `apps/enforcement-api/migrations/create_enforcesense_tables.sql` (or reuse existing)
- `apps/enforcement-api/app/core/database.py` (add migration runner)

**Files to Reference:**
- `backend/migrations/add_enforcesense_tables.sql` (existing migration)
- `apps/enforcement-api/app/modules/enforcesense/models.py` (SQLAlchemy models)

**Estimated Time:** 1-2 hours

---

#### 1.4 Implement Tenant Resolution in Enforcement API
**Goal:** Ensure all Enforcement API queries are tenant-scoped

**Tasks:**
- [ ] Add `current_tenant` dependency to all endpoints
- [ ] Filter all queries by `tenant_id`
- [ ] Add tenant validation in case creation
- [ ] Test tenant isolation (one tenant can't see another's data)

**Files to Update:**
- `apps/enforcement-api/app/modules/enforcesense/routes.py`
- `apps/enforcement-api/app/modules/enforcesense/portal_routes.py`

**Estimated Time:** 1 hour

---

### Phase 2: Move EnforceSense Logic (MEDIUM PRIORITY)

#### 2.1 Move EnforceSense Endpoints
**Goal:** Move EnforceSense endpoints from Platform API to Enforcement API

**Tasks:**
- [ ] Review `backend/app/api/v1/endpoints/enforcesense.py`
- [ ] Move endpoints to `apps/enforcement-api/app/modules/enforcesense/routes.py`
- [ ] Update frontend API calls to point to Enforcement API (port 8001)
- [ ] Remove EnforceSense endpoints from Platform API
- [ ] Update CORS settings if needed

**Files to Move/Update:**
- `backend/app/api/v1/endpoints/enforcesense.py` → Move logic to Enforcement API
- `frontend/src/services/api.ts` → Update EnforceSense API base URL
- `apps/enforcement-api/main.py` → Ensure routes are registered

**Estimated Time:** 2-3 hours

---

#### 2.2 Move EnforceSense Services
**Goal:** Move business logic services to Enforcement API

**Tasks:**
- [ ] Identify EnforceSense services in Platform API
- [ ] Move services to `apps/enforcement-api/app/modules/enforcesense/services/`
- [ ] Update imports and dependencies
- [ ] Test service functionality

**Estimated Time:** 2-3 hours

---

### Phase 3: Complete Debtor Portal (MEDIUM PRIORITY)

#### 3.1 Implement Token Validation
**Goal:** Replace in-memory token storage with database/Redis

**Tasks:**
- [ ] Create `portal_sessions` table (token, case_id, debtor_id, tenant_id, expires_at)
- [ ] Update `POST /portal/sessions` to store in database
- [ ] Update `GET /portal/cases/:caseId` to validate token from database
- [ ] Add token expiry checking
- [ ] Add rate limiting (e.g., 5 attempts per hour per case)

**Files to Update:**
- `apps/enforcement-api/app/modules/enforcesense/portal_routes.py`
- Create migration: `apps/enforcement-api/migrations/add_portal_sessions_table.sql`

**Estimated Time:** 2-3 hours

---

#### 3.2 Complete Case Detail Views
**Goal:** Display full case information in Debtor Portal

**Tasks:**
- [ ] Update `CaseView.tsx` to display:
  - Case details (reference, status, amount, balance)
  - Payment history
  - Transaction details
  - Next actions/notices
- [ ] Add payment form (if payment processing ready)
- [ ] Ensure all labels are localized (i18n)
- [ ] Add loading states and error handling

**Files to Update:**
- `apps/debtor-portal/src/pages/CaseView.tsx`
- `apps/debtor-portal/src/i18n/locales/*.json` (add missing translations)

**Estimated Time:** 3-4 hours

---

### Phase 4: Testing & Integration (LOW PRIORITY)

#### 4.1 End-to-End Testing
**Goal:** Verify complete flow works

**Tasks:**
- [ ] Test module enablement in admin portal
- [ ] Test module appears in frontend navigation
- [ ] Test Enforcement API endpoints with authentication
- [ ] Test Debtor Portal login and case viewing
- [ ] Test tenant isolation (multiple tenants)
- [ ] Test multilingual support

**Estimated Time:** 2-3 hours

---

## 📋 Quick Reference

### Current Ports
- **Platform API:** `http://localhost:8000`
- **Enforcement API:** `http://localhost:8001`
- **Frontend:** `http://localhost:3000`
- **Debtor Portal:** `http://localhost:3002`
- **Admin Portal:** `http://localhost:3010`

### Key Files
- **Enforcement API Auth:** `apps/enforcement-api/app/core/dependencies.py`
- **Enforcement API Models:** `apps/enforcement-api/app/modules/enforcesense/models.py`
- **Enforcement API Routes:** `apps/enforcement-api/app/modules/enforcesense/routes.py`
- **Debtor Portal Auth:** `apps/enforcement-api/app/modules/enforcesense/portal_routes.py`
- **Platform API EnforceSense:** `backend/app/api/v1/endpoints/enforcesense.py`

### Database
- **Name:** `ccs_quote_tool`
- **Connection:** `postgresql://postgres:postgres_password_2025@postgres:5432/ccs_quote_tool`
- **Migrations:** `backend/migrations/` (shared database)

---

## 🎯 Recommended Starting Point

**Start with Phase 1.1: Create Shared Authentication Library**

This is the foundation for everything else. Once authentication is shared, both APIs can use the same JWT validation and tenant resolution logic.

**Command to start:**
```bash
# Create shared auth library structure
mkdir -p packages/shared/auth
touch packages/shared/auth/__init__.py
touch packages/shared/auth/jwt.py
touch packages/shared/auth/tenant.py
```

Then port the JWT logic from `backend/app/core/security.py` and tenant logic from `backend/app/core/dependencies.py`.

---

## 📝 Notes

- All services share the same database (`ccs_quote_tool`)
- Authentication tokens from Platform API should work with Enforcement API (same secret key)
- Frontend needs to be updated to call Enforcement API for EnforceSense endpoints
- Debtor Portal uses different auth (token-based) than staff portals (JWT)

---

**Next Action:** Start with Phase 1.1 - Create Shared Authentication Library



