# Infometrix Target Architecture (Two-API Design)

**Version:** 3.6.0  
**Status:** Target Architecture (Not Yet Implemented)  
**Last Updated:** 2025-12-19

---

## 🎯 Architecture Overview

Infometrix uses a **two-API architecture** with separate external-facing portals:

1. **Platform API** (internal) - Core platform + common business modules
2. **Enforcement API** (internal) - Sensitive enforcement/debt recovery domain
3. **External Portals** - Separate frontend applications (Client Portal, Debtor Portal)

---

## 🏗️ Service Architecture

### Internal APIs

| Service | Port | Purpose | Status |
|---------|------|---------|--------|
| `platform-api` | 8000 | Core platform + CRM + Helpdesk + Quoting | **Target** |
| `enforcement-api` | 8001 | EnforceSense module + enforcement workflows | **Target** |

### External Portals

| Portal | Port | Purpose | Status |
|--------|------|---------|--------|
| `admin-portal` | 3010 | Internal admin/staff UI | ✅ Current |
| `client-portal` | 3011 | External client-facing portal | **Target** |
| `debtor-portal` | 3012 | External debtor self-service (multilingual) | **Target** |

### Infrastructure

| Service | Port | Purpose |
|---------|------|---------|
| `postgres` | 5432 | Primary database |
| `redis` | 6379 | Caching & session store |
| `celery-worker` | - | Background tasks |
| `celery-beat` | - | Scheduled tasks |
| `minio` | 9002/9092 | Object storage |
| `mailhog` | 1026/3006 | Email testing |

---

## 📦 API Topology

### Platform API (Internal)

**Purpose:** Core platform + common business modules

**Includes:**
- Tenant management, users/roles/RBAC
- CRM core (Accounts/Contacts/Leads/Activities)
- Helpdesk module
- Quoting/Proposals module
- Shared files/documents, templates, notifications, audit logging

**Location:** `apps/platform-api/`

**Routes:**
- `/api/v1/auth/*` - Authentication
- `/api/v1/tenants/*` - Tenant management
- `/api/v1/users/*` - User management
- `/api/v1/customers/*` - Customer management
- `/api/v1/quotes/*` - Quote management
- `/api/v1/helpdesk/*` - Helpdesk module
- `/api/v1/documents/*` - Document management

### Enforcement API (Internal)

**Purpose:** Sensitive enforcement/debt recovery domain

**Includes:**
- EnforceSense module backend (cases, debtor relations, payments, visits, compliance)
- Enforcement-specific audit, workflows, evidence, notices
- Sensitive debtor data processing
- Enforcement-specific permissions

**Location:** `apps/enforcement-api/`

**Routes:**
- `/api/v1/enforcesense/*` - EnforceSense module
- `/api/v1/portal/sessions/*` - Debtor portal session management
- `/api/v1/portal/cases/*` - Debtor portal case access

**Security:** Isolated from Platform API at service boundary (separate server, separate deployment)

---

## 🌐 External Portals

### Admin Portal (Internal)

**Purpose:** Internal admin/staff UI shell

**Location:** `apps/admin-portal/`

**Access:** Internal staff only (JWT auth)

**Features:**
- Module switcher at top of left nav
- Context menu based on active module
- Tenant management
- User management
- System configuration

### Client Portal (External)

**Purpose:** External client-facing portal

**Location:** `apps/client-portal/`

**Access:** Client authentication (separate from staff)

**APIs:**
- Primarily Platform API
- May call Enforcement API for enforcement-specific client views

**Security:** Separate route namespaces, strict auth policies, no internal/admin endpoints

### Debtor Portal (External, Multilingual)

**Purpose:** Debtor self-service portal

**Location:** `apps/debtor-portal/`

**Access:** Token-based secure links / one-time codes / magic links

**APIs:**
- Primarily Enforcement API
- Separate auth model (not staff JWT)

**Features:**
- **Multilingual support** (mandatory)
  - i18n framework with translation files (en, ro, cs, etc.)
  - Auto-detect from browser
  - Manual language override
  - All user-facing strings translated
  - Locale-aware API templates

**Routes:**
- `/login` - Magic link / code entry
- `/case/:caseId` - Case view (read-only)
- `/payment/:caseId` - Payment interface

---

## 🔐 Security & Multitenancy

### Tenant Isolation

- Every request is tenant-scoped
- `tenantId` enforced on every DB query
- RBAC enforced server-side on every endpoint
- Feature flags enforced server-side (not only UI)

### Authentication Models

**Internal Staff:**
- JWT tokens with tenant context
- Standard RBAC permissions

**Debtor Portal:**
- Token-based secure links
- One-time codes / magic links
- Strict expiry + rate limiting
- Separate audience/claims (not staff JWT)

**Client Portal:**
- Separate client authentication
- No access to internal/admin endpoints

---

## 📁 Repository Structure (Monorepo)

```
infometrix/
├── apps/
│   ├── platform-api/          # Platform API service
│   ├── enforcement-api/        # Enforcement API service
│   ├── admin-portal/          # Internal admin UI
│   ├── client-portal/         # External client portal
│   └── debtor-portal/         # External debtor portal (multilingual)
├── packages/
│   ├── shared/                # Types, validation, auth helpers, tenancy
│   └── ui/                    # Optional shared UI components
└── docker-compose.yml
```

**Rule:** No "random imports" across apps. Shared code goes through `packages/*`.

---

## 🔄 Data Ownership & Boundaries

### Platform API Owns

- Accounts/Contacts/Addresses
- Tenants/Users/Roles
- Generic Documents/Templates
- Helpdesk tickets
- Quotes/proposals

### Enforcement API Owns

- Enforcement Cases
- Debtor-specific workflows, notices, evidence
- Enforcement payments
- Debtor portal sessions/tokens

### Cross-Service Referencing

- Enforcement API stores references to Platform entities by immutable IDs (e.g., `accountId`, `contactId`)
- Avoid duplicating full CRM records in Enforcement
- If needed, store snapshot + source ID

---

## 🔌 Inter-Service Communication

### Phase 1 (Initial)

- Synchronous lookups via API calls when necessary
- Cached where appropriate
- Small shared library for auth/tenant context + common types

### Phase 2 (Later, Optional)

- Event/outbox pattern for key changes:
  - Account updated
  - Address changed
  - Case status changed
  - Payment posted
- Do not over-engineer events on day 1

---

## 📦 Module System

### Platform API Modules

**Location:** `apps/platform-api/src/modules/<moduleKey>/`

**Modules:**
- `crm` - Core CRM functionality
- `helpdesk` - Helpdesk module
- `quoting` - Quoting/Proposals module

### Enforcement API Modules

**Location:** `apps/enforcement-api/src/modules/<moduleKey>/`

**Modules:**
- `enforcesense` - EnforceSense module

### Module Definition

Each module must define:
- Routes
- Permissions required
- Navigation contributions (for internal portals)
- Feature flag keys
- README with purpose + endpoints

---

## 🎨 Navigation UX (Internal Portals)

**Module Switcher:**
- At top of left nav
- Shows enabled modules for tenant
- User must have permissions

**Context Menu:**
- Below module switcher
- Based on active module
- Modules shown = enabled for tenant AND permitted for user

---

## 🌍 Multilingual Debtor Portal (Mandatory)

### Requirements

1. **i18n Framework:**
   - Translation files: `en.json`, `ro.json`, `cs.json`, etc. (extendable)
   - Language detection:
     - Session preferred language (if token includes it)
     - Debtor preferred language from API
     - Browser language
     - Fallback: `en`

2. **All User-Facing Strings:**
   - Must be in translation files
   - No hardcoded strings

3. **API Support:**
   - Enforcement API accepts `locale` parameter
   - Returns localized strings/templates where applicable
   - Store debtor preferred language

### Translation File Structure

```
apps/debtor-portal/
└── locales/
    ├── en.json
    ├── ro.json
    └── cs.json
```

**Example Keys:**
- `login.title`
- `login.enterCode`
- `case.title`
- `case.status`
- `common.loading`
- `common.error`

---

## 🚀 Implementation Milestones

1. ✅ Platform API + existing app running
2. ⏳ Split Helpdesk into its own module (internal UI tab + module routes)
3. ⏳ Create Enforcement API skeleton + EnforceSense module "bones"
4. ⏳ Create Debtor Portal skeleton with multilingual framework
5. ⏳ Connect Debtor Portal to Enforcement API with secure auth flow

---

## ⚠️ Current vs Target State

### Current Implementation (Monolithic Modular)

- ✅ Single backend API with modules
- ✅ Single frontend with module routes
- ✅ EnforceSense as module within main backend
- ✅ Debtor Portal as routes within main frontend
- ❌ No separate Enforcement API
- ❌ No multilingual support
- ❌ No separate external portals

### Target Implementation (Two-API Architecture)

- ⏳ Platform API (separate service)
- ⏳ Enforcement API (separate service)
- ⏳ Separate external portals (Client, Debtor)
- ⏳ Multilingual debtor portal
- ⏳ Monorepo structure with `apps/` and `packages/`

---

## 📝 Migration Path

See [`docs/MIGRATION_TO_TWO_API.md`](MIGRATION_TO_TWO_API.md) for detailed migration plan.

---

**Last Updated:** 2025-12-19  
**Version:** 3.6.0  
**Status:** Target Architecture (Not Yet Implemented)



