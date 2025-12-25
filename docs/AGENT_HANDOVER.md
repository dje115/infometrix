# 🤖 AI Agent Handover Document - Infometrix Platform

**Last Updated:** 2025-12-25  
**Platform Version:** 3.7.0  
**Status:** Active Development - Multi-Tenant Authentication & EnforceSense Module

---

## 🎯 **What Is Infometrix?**

Infometrix is a **multi-tenant SaaS CRM and Quoting Platform** that has been rebranded from "CCS Quote Tool v2". It's a comprehensive business management platform with:

- **CRM Core** (Sales/CRM module)
- **Helpdesk Module** (Ticketing & Support)
- **Quoting & Proposals Module**
- **EnforceSense Module** (Debt enforcement - separate repository)
- **Settings & Administration**

### **Key Architecture Points:**

1. **Multi-Tenant SaaS:** Each tenant has isolated data, users, and configuration
2. **Modular Architecture:** Features are organized into modules with feature flags
3. **Feature Flags:** Tenant-level control over module visibility
4. **RBAC:** Role-based access control for users
5. **AI-Powered:** GPT-5 integration for lead analysis, company intelligence
6. **Explicit Tenant Identification:** No default tenant fallback - all environments require explicit tenant identifier

---

## 📁 **Project Structure**

```
Infometrix/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── modules/     # Module system
│   │   │   ├── helpdesk/
│   │   │   ├── enforcesense/
│   │   │   ├── base.py
│   │   │   └── registry.py
│   │   ├── api/v1/      # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   └── core/        # Core services (feature flags, middleware, etc.)
│   └── migrations/     # Database migrations
│
├── frontend/            # React frontend (CRM interface)
├── admin-portal/        # Vue.js admin interface
├── apps/
│   └── enforcement-api/ # EnforceSense API (separate service)
├── docs/                # Documentation (THIS FOLDER)
│   ├── specs/          # Specifications
│   ├── ccs-archive/    # Legacy CCS documentation
│   └── enforcesense/   # EnforceSense documentation
│
└── docker-compose.yml   # Development environment
```

---

## 🔄 **Current Status (2025-12-25)**

### ✅ **Recently Completed:**
- **Multi-Tenant Login Enhancement:** Added tenant slug field to login page
- **Tenant Middleware Update:** Removed default tenant fallback - now requires explicit tenant identifier in all environments (dev and production)
- **Version Management:** Fixed version endpoint to correctly read from VERSION file (3.7.0)
- **EnforceSense Module:** Bulk operations, case status history, debtor address management, vulnerability indicators
- **TypeScript Errors:** All resolved - no linter errors in frontend

### 🚧 **Current Issues:**
- **Docker Desktop:** Not currently running (needs to be started)
- **Backend Status:** Unknown (requires Docker to check)
- **Login Flow:** Now requires tenant slug - users must provide tenant identifier on login

### 📋 **Pending:**
- Verify backend starts correctly after tenant middleware changes
- Test login flow with tenant slug
- Verify all services are running correctly
- Complete EnforceSense module integration testing

---

## 🔑 **Key Changes in v3.7.0**

### **1. Multi-Tenant Authentication Changes**

**CRITICAL:** The platform now **requires explicit tenant identification** in all environments. There is **no default tenant fallback**.

#### **Login Page Changes:**
- Added "Tenant Slug" input field (required)
- Users must provide: **Username, Tenant Slug, and Password**
- Tenant slug is sent as `X-Tenant-ID` header in login requests
- Location: `frontend/src/pages/Login.tsx`

#### **Backend Middleware Changes:**
- Removed default "ccs" tenant fallback in development
- All routes (except `/api/v1/version`, `/health`, `/`) now require tenant identifier
- Tenant can be provided via:
  - `X-Tenant-ID` header (preferred for API calls)
  - Subdomain (e.g., `ccs.localhost:3000`)
- Location: `backend/app/core/middleware.py`

#### **Why This Change?**
- User requirement: "i dont want it defaulting to anything as i will setup multi tenants in dev as in production"
- Ensures dev environment matches production behavior
- Prevents accidental cross-tenant data access
- Forces explicit tenant setup

### **2. Version Management**

- Version is now correctly read from `VERSION` file in project root
- Fallback chain: `APP_VERSION` env var → `VERSION` file → `settings.VERSION` → `"3.7.0"`
- Location: `backend/app/api/v1/endpoints/version.py`

### **3. EnforceSense Module Enhancements**

- Bulk operations for cases (status update, assignment)
- Case status history tracking
- Debtor address management (CRUD)
- Debtor vulnerability indicators
- Enhanced dashboard with charts
- See EnforceSense TODO list for complete details

---

## 🚀 **Development Workflow**

### **Starting the Platform:**
```powershell
cd "C:\devfolder\Infometrix"
# Start Docker Desktop first!
docker-compose up -d
```

### **Services:**
- **Backend:** http://localhost:8000 (FastAPI) 
- **Frontend:** http://localhost:3000 (React CRM) 
- **Admin Portal:** http://localhost:3010 (Vue.js Admin) 
- **Enforcement API:** http://localhost:8001 (EnforceSense API)
- **PostgreSQL:** localhost:5432 
- **Redis:** localhost:6379 
- **MinIO:** http://localhost:9002 (API), http://localhost:9092 (Console) 
- **MailHog:** http://localhost:3006 (Email testing) 
- **Celery Worker:** Background tasks 
- **Celery Beat:** Scheduled tasks 

### **Login Credentials:**
- **Email:** `admin@ccs.com` (or your tenant admin email)
- **Password:** `admin123` (or your tenant admin password)
- **Tenant Slug:** `ccs` (or your tenant slug - **REQUIRED**)
- **Role:** Super Admin

**IMPORTANT:** You must now provide the tenant slug on the login page. There is no default.

---

## 🔑 **Key Concepts**

### **1. Multi-Tenancy:**
- Each tenant has isolated data
- Row-level security (RLS) in PostgreSQL
- Tenant context set via middleware or JWT token
- **NO DEFAULT TENANT** - explicit identification required

### **2. Tenant Identification:**
- **For Public Routes (Login):** Via `X-Tenant-ID` header or subdomain
- **For Authenticated Routes:** Via JWT token (tenant_id in token payload)
- **Middleware Validation:** Tenant must exist in database before access is granted

### **3. Module System:**
- Modules are self-contained features
- Registered via `ModuleRegistry`
- Visibility controlled by feature flags
- Navigation grouped by module category

### **4. Feature Flags:**
- Stored in `tenants.feature_flags` JSONB column
- Tenant-specific enable/disable
- Checked before module routes/UI are shown

### **5. RBAC:**
- User roles: SUPER_ADMIN, TENANT_ADMIN, MANAGER, SALES_REP, USER
- Permissions stored as JSON array per user
- Module-level permission checks

---

## 📚 **Important Files to Understand**

### **Backend:**
1. **`backend/app/core/middleware.py`** - Tenant middleware (requires explicit tenant)
2. **`backend/app/modules/registry.py`** - Module registration
3. **`backend/app/core/feature_flags.py`** - Feature flag service
4. **`backend/app/models/tenant.py`** - Tenant model (has feature_flags)
5. **`backend/app/api/v1/api.py`** - Main API router (registers modules)
6. **`backend/app/core/dependencies.py`** - Authentication dependencies (get_current_user, get_current_tenant)
7. **`backend/main.py`** - FastAPI app entry point

### **Frontend:**
1. **`frontend/src/pages/Login.tsx`** - Login page (now requires tenant slug)
2. **`frontend/src/components/Layout.tsx`** - Main layout (module navigation)
3. **`frontend/src/types/modules.ts`** - TypeScript module types
4. **`frontend/src/services/api.ts`** - API service (includes tenant slug in login)
5. **`frontend/src/App.tsx`** - Main app component

### **EnforceSense:**
1. **`apps/enforcement-api/app/modules/enforcesense/`** - EnforceSense module
2. **`apps/enforcement-api/app/modules/enforcesense/routes.py`** - API endpoints
3. **`apps/enforcement-api/app/modules/enforcesense/models.py`** - Database models
4. **`frontend/src/modules/enforcesense/`** - Frontend components

### **Database:**
1. **`backend/migrations/`** - Database migrations
2. **`backend/app/models/tenant.py`** - Tenant model schema

---

## 🎯 **Current Tasks & Priorities**

### **High Priority:**
1. ✅ Multi-tenant login with tenant slug (completed)
2. ✅ Remove default tenant fallback (completed)
3. ✅ Fix version endpoint (completed)
4. 🚧 Verify backend starts correctly
5. 🚧 Test login flow with tenant slug
6. 📋 Complete EnforceSense module testing

### **Medium Priority:**
1. Module permission system refinement
2. Frontend module visibility based on feature flags
3. Module-specific route protection
4. Performance optimizations

### **Low Priority:**
1. Module documentation
2. Module testing framework
3. Module marketplace concept

---

## 🔗 **Integration Points**

### **EnforceSense Integration:**
- **Location:** `apps/enforcement-api/` (separate service)
- **Status:** Active development
- **Port:** 8001
- **Frontend:** `frontend/src/modules/enforcesense/`
- **See:** EnforceSense TODO list for detailed status

### **Legacy CCS Features:**
- Most features already migrated
- Some documentation in `docs/ccs-archive/`
- Reference old workspace for historical context

---

## 🐛 **Known Issues & Gotchas**

1. **Docker Desktop:** Must be running before starting services
2. **Tenant Slug Required:** Login will fail without tenant slug - no default fallback
3. **Version Endpoint:** Now correctly reads from VERSION file (3.7.0)
4. **Module navigation:** Implemented in frontend
5. **EnforceSense:** Separate service on port 8001
6. **Database name:** Still `ccs_quote_tool` for compatibility (intentional)

### **Recent Fixes:**
- ✅ TypeScript errors resolved
- ✅ Version endpoint fixed
- ✅ Tenant middleware updated
- ✅ Login page updated with tenant slug field

---

## 📖 **Reading Order for New Agents**

1. **Start Here:** `AGENT_START.md` (quick overview)
2. **This Document:** `docs/AGENT_HANDOVER.md` (comprehensive context)
3. **Migration Plan:** `MIGRATION_PLAN.md` (what we're doing)
4. **Module System:** `backend/app/modules/base.py` (how modules work)
5. **Feature Flags:** `backend/app/core/feature_flags.py` (how flags work)
6. **Tenant Middleware:** `backend/app/core/middleware.py` (tenant identification)
7. **EnforceSense:** `TODO.md` (EnforceSense TODO list)
8. **Legacy Docs:** `docs/ccs-archive/` (historical context)

---

## 🆘 **Getting Help**

### **If You're Stuck:**
1. Check `AGENT_START.md` for quick answers
2. Review `MIGRATION_PLAN.md` for context
3. Check `docs/ccs-archive/` for legacy documentation
4. Review module code in `backend/app/modules/`
5. Check EnforceSense TODO list for module-specific tasks

### **Common Questions:**
- **"Where is X feature?"** → Check `docs/ccs-archive/` or old workspace
- **"How do modules work?"** → See `backend/app/modules/base.py`
- **"What's the migration status?"** → See `MIGRATION_PLAN.md`
- **"How do I add a module?"** → See module examples in `backend/app/modules/`
- **"Why is login failing?"** → Check that tenant slug is provided (no default)
- **"How do I test multi-tenant?"** → Create multiple tenants and test with different slugs

---

## 📝 **Notes for AI Agents**

### **When Working on This Project:**
1. **Always check feature flags** before showing module UI
2. **Respect tenant isolation** - never cross tenant boundaries
3. **Use module registry** for navigation, not hardcoded routes
4. **Check permissions** before allowing module access
5. **Require tenant slug** - never assume default tenant
6. **Reference legacy docs** when migrating features

### **Code Style:**
- Backend: Python (FastAPI, SQLAlchemy, async/await)
- Frontend: React (TypeScript, Material-UI)
- Admin: Vue.js (TypeScript, Element Plus)
- Database: PostgreSQL with JSONB for flexible data

### **Testing:**
- Backend: pytest (when tests exist)
- Frontend: Manual testing (test framework TBD)
- Database: Migrations tested manually
- **Multi-tenant:** Test with multiple tenants to verify isolation

---

## ✅ **Verification Checklist**

Before considering work complete:
- [ ] Feature flags checked for module visibility
- [ ] Tenant isolation verified (test with multiple tenants)
- [ ] Module registered in registry
- [ ] Navigation updated (if UI change)
- [ ] Permissions checked
- [ ] Tenant slug required (no default fallback)
- [ ] Documentation updated
- [ ] Legacy docs referenced if needed

---

## 🔍 **Troubleshooting**

### **Login Issues:**
- **Error: "Tenant identifier required"**
  - Solution: Provide tenant slug in login form
  - Check that tenant exists in database
  - Verify `X-Tenant-ID` header is being sent

- **Error: "Invalid tenant"**
  - Solution: Verify tenant slug matches database
  - Check tenant is not soft-deleted
  - Verify tenant has active status

### **Backend Not Starting:**
- Check Docker Desktop is running
- Check logs: `docker-compose logs backend`
- Verify environment variables are set
- Check database connection

### **Version Display Issues:**
- Check `VERSION` file exists in project root
- Verify `backend/app/core/config.py` has correct version
- Check version endpoint: `GET /api/v1/version`

---

**Last Updated:** 2025-12-25  
**Maintained By:** Development Team  
**Questions?** Check `AGENT_START.md` or `MIGRATION_PLAN.md`

---

## ✅ **Current System Status (2025-12-25)**

### **Version:**
- **Platform Version:** 3.7.0
- **VERSION File:** `3.7.0`
- **Config Version:** `3.7.0`

### **Authentication:**
- ✅ Tenant slug field added to login page
- ✅ Default tenant fallback removed
- ✅ Middleware requires explicit tenant identifier
- ✅ Login API updated to accept tenant slug

### **TypeScript:**
- ✅ No linter errors in frontend
- ✅ All type errors resolved

### **Docker:**
- ⚠️ Docker Desktop not currently running
- ⚠️ Services status unknown (requires Docker to check)

### **EnforceSense:**
- ✅ Bulk operations implemented
- ✅ Case status history tracking
- ✅ Debtor address management
- ✅ Vulnerability indicators
- ✅ Enhanced dashboard with charts

---

**Next Steps:**
1. Start Docker Desktop
2. Verify all services start correctly
3. Test login flow with tenant slug
4. Verify multi-tenant isolation
5. Continue EnforceSense module development
