# Infometrix Platform Architecture

**Version:** 3.6.0  
**Last Updated:** 2025-12-19

---

## 🏗️ Service Architecture

### Docker Containers

The Infometrix platform runs as a **monolithic modular architecture** where all modules are integrated into the main services:

| Container | Service | Port | Purpose |
|-----------|---------|------|---------|
| `infometrix-backend` | FastAPI Backend | 8000 | Main API server (includes all modules) |
| `infometrix-frontend` | React Frontend | 3000 | Main CRM frontend (includes all modules) |
| `infometrix-admin-portal` | Vue.js Admin Portal | 3010 | System administration portal |
| `infometrix-postgres` | PostgreSQL 16 | 5432 | Primary database |
| `infometrix-redis` | Redis 7 | 6379 | Caching & session store |
| `infometrix-celery-worker` | Celery Worker | - | Background task processing |
| `infometrix-celery-beat` | Celery Beat | - | Scheduled tasks |
| `infometrix-minio` | MinIO | 9002/9092 | Object storage (S3-compatible) |
| `infometrix-mailhog` | MailHog | 1026/3006 | SMTP testing & email viewer |

### ⚠️ Legacy Container (Not Part of Current Setup)

| Container | Status | Notes |
|-----------|--------|-------|
| `infometrix-enforcement-api` | **Legacy/Orphan** | Old separate API container. Not used in current architecture. Can be removed. |

---

## 📦 Module Architecture

### EnforceSense Module

**Location:** Integrated into main backend and frontend (NOT a separate container)

**Backend:**
- **Routes:** `/api/v1/modules/enforcesense/*`
- **Module File:** `backend/app/modules/enforcesense/module.py`
- **Endpoints:** `backend/app/api/v1/endpoints/enforcesense.py`
- **Models:** `backend/app/models/enforcesense.py`
- **AI Service:** `backend/app/services/enforcesense_ai_service.py`

**Frontend:**
- **Routes:** `/enforcesense`, `/enforcesense/cases`, `/enforcesense/cases/:id`
- **Pages:** `frontend/src/modules/enforcesense/pages/`
- **API Client:** `frontend/src/services/enforcesenseAPI.ts`

**Database:**
- **Tables:** `debtors`, `enforcement_clients`, `enforcement_cases`, `case_transactions`, `case_notes`
- **Migration:** `backend/migrations/add_enforcesense_tables.sql`

**Feature Flag:** `ENFORCESENSE_ENABLED` (controlled per tenant in admin portal)

### Debtor Portal

**Location:** Integrated into main backend and frontend (NOT a separate container)

**Backend:**
- **Routes:** `/api/v1/debtor-portal/*`
- **Endpoints:** `backend/app/api/v1/endpoints/debtor_portal.py`
- **Authentication:** Token-based (X-Debtor-Token header)

**Frontend:**
- **Routes:** `/debtor-portal/login`, `/debtor-portal/cases`
- **Pages:** `frontend/src/pages/DebtorPortalLogin.tsx`, `frontend/src/pages/DebtorPortalCases.tsx`

**Access:** Token-based authentication (separate from main CRM login)

---

## 🔌 API Endpoints

### Main Backend API (`http://localhost:8000`)

**Core Endpoints:**
- `/api/v1/auth/*` - Authentication
- `/api/v1/customers/*` - Customer management
- `/api/v1/quotes/*` - Quote management
- `/api/v1/helpdesk/*` - Helpdesk module
- `/api/v1/modules/enforcesense/*` - **EnforceSense module**
- `/api/v1/debtor-portal/*` - **Debtor portal API**
- `/api/v1/admin/*` - Admin operations
- `/api/v1/dashboard/*` - Dashboard data

**API Documentation:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🌐 Frontend Routes

### Main Frontend (`http://localhost:3000`)

**Core Routes:**
- `/` - Dashboard
- `/customers` - Customer management
- `/quotes` - Quote management
- `/helpdesk/*` - Helpdesk module
- `/enforcesense` - **EnforceSense dashboard**
- `/enforcesense/cases` - **EnforceSense cases list**
- `/enforcesense/cases/:id` - **EnforceSense case detail**
- `/debtor-portal/login` - **Debtor portal login**
- `/debtor-portal/cases` - **Debtor portal cases**

### Admin Portal (`http://localhost:3010`)

**Routes:**
- `/dashboard` - Admin dashboard
- `/tenants` - Tenant management (module access control)
- `/users` - User management
- `/api-keys` - Global API keys
- `/settings` - System settings
- `/ai-prompts` - AI prompt management

---

## 🗄️ Database

**Database Name:** `ccs_quote_tool` (kept for compatibility)

**Connection:**
- Host: `localhost:5432` (from host) or `postgres:5432` (from containers)
- User: `postgres`
- Password: `postgres_password_2025`

**Key Tables:**
- `tenants` - Multi-tenant isolation
- `users` - User accounts
- `customers`, `leads`, `quotes` - Core CRM
- `tickets`, `sla_policies` - Helpdesk module
- `debtors`, `enforcement_cases`, `case_notes` - **EnforceSense module**

---

## 🔐 Module Access Control

Modules are controlled per tenant via feature flags in the admin portal:

1. Navigate to **Admin Portal** → **Tenants**
2. Click **Edit** on a tenant
3. Scroll to **Module Access Control** section
4. Enable/disable modules:
   - `HELPDESK_ENABLED` - Helpdesk module
   - `ENFORCESENSE_ENABLED` - **EnforceSense module**
   - `QUOTING_ENABLED` - Quoting module
   - `SALES_ENABLED` - Sales/CRM module

---

## 🚀 Development Workflow

### Starting Services

```powershell
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Rebuild after code changes
docker-compose up --build -d
```

### Access URLs

- **Frontend (CRM):** http://localhost:3000
- **Admin Portal:** http://localhost:3010
- **Backend API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **MailHog UI:** http://localhost:3006
- **MinIO Console:** http://localhost:9092

### Default Login

- **Email:** `admin@ccs.com`
- **Password:** `admin123`

---

## 📝 Key Points for AI Agents

1. **EnforceSense is NOT a separate container** - it's a module within the main backend/frontend
2. **Debtor Portal is NOT a separate container** - it's part of the main frontend with separate routes
3. **All modules share the same database** - tenant isolation via `tenant_id`
4. **Module access is controlled via feature flags** - set in admin portal
5. **The `infometrix-enforcement-api` container is legacy** - can be removed

---

## 🔄 Migration Notes

The current architecture uses a **monolithic modular approach** where:
- All modules are integrated into the main backend API
- All frontends are integrated into the main React app
- Modules are enabled/disabled per tenant via feature flags

This is different from a **microservices architecture** where each module would be a separate service.

---

**Last Updated:** 2025-12-19  
**Version:** 3.6.0

