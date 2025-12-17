# 🤖 AI Agent Handover Document - Infometrix Platform

**Last Updated:** 2025-12-17  
**Platform Version:** 3.0.6  
**Status:** Active Development - Module System Migration

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

---

## 📁 **Project Structure**

```
Infometrix/
├── backend/              # FastAPI Python backend
│   ├── app/
│   │   ├── modules/     # Module system (NEW)
│   │   │   ├── helpdesk/
│   │   │   ├── enforcesense/
│   │   │   ├── base.py
│   │   │   └── registry.py
│   │   ├── api/v1/      # API endpoints
│   │   ├── models/      # SQLAlchemy models
│   │   └── core/        # Core services (feature flags, etc.)
│   └── migrations/     # Database migrations
│
├── frontend/            # React frontend (CRM interface)
├── admin-portal/        # Vue.js admin interface
├── docs/                # Documentation (THIS FOLDER)
│   ├── specs/          # Specifications
│   ├── ccs-archive/    # Legacy CCS documentation
│   └── enforcesense/   # EnforceSense documentation
│
└── docker-compose.yml   # Development environment
```

---

## 🔄 **Current Migration Status**

### ✅ **Completed:**
- Repository rebranded from `ccs-quote-tool-v2` to `infometrix`
- Module system scaffolding created
- Feature flags system implemented
- Database migration for `feature_flags` column
- Docker containers rebranded
- Package.json files updated
- **Database initialized with system tenant and default tenant**
- **34 AI prompts seeded across all categories**
- **All services running (Frontend, Admin, Backend, Celery, MailHog, MinIO)**
- **Shared folder data migrated from CCS**

### 🚧 **In Progress:**
- Frontend navigation grouped by modules
- Helpdesk module migration
- Module registry integration

### 📋 **Pending:**
- EnforceSense module integration (separate repo)
- Complete frontend navigation restructure
- Module permission system refinement

---

## 🗂️ **Key Documentation Locations**

### **This Workspace (Infometrix):**
- **`README.md`** - Main project README
- **`docs/AGENT_HANDOVER.md`** - This document
- **`AGENT_START.md`** - Quick start for new agents
- **`MIGRATION_PLAN.md`** - Detailed migration plan
- **`docs/specs/`** - Technical specifications

### **Legacy CCS Project:**
- **Location:** `C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2\`
- **Key Docs:**
  - `README.md` - Original project documentation
  - `DEVELOPMENT_PLAN.md` - 6-month strategic plan
  - `MASTER_SPECIFICATION.md` - Complete feature spec
  - `HANDOVER_DOCUMENT.md` - Previous handover
  - See `docs/ccs-archive/` for copied specs

### **EnforceSense Project:**
- **Location:** `C:\Users\david\Documents\EnforceSense\`
- **Key Docs:**
  - `README.md` - EnforceSense overview
  - `docs/AGENTS_START_HERE.md` - Agent guide
  - `docs/CORE_DOMAIN_MODEL.md` - Domain model
  - `docs/UK_DEBT_ENFORCEMENT_END_TO_END.md` - Business process
  - See `docs/enforcesense/` for copied specs

---

## 🏗️ **Module System Architecture**

### **Module Structure:**
```python
# backend/app/modules/base.py
class BaseModule:
    name: str
    description: str
    icon: str
    category: str  # "Sales/CRM", "Helpdesk", "Quoting & Proposals", etc.
    route_prefix: str
    permissions: List[str]
    
    def register_routes(self, router)
    def get_navigation_items(self) -> List[Dict]
```

### **Module Registry:**
```python
# backend/app/modules/registry.py
ModuleRegistry.register_module(HelpdeskModule())
ModuleRegistry.register_module(EnforceSenseModule())
```

### **Feature Flags:**
```python
# backend/app/core/feature_flags.py
FeatureFlagsService.is_enabled(tenant_id, "HELPDESK_ENABLED")
```

### **Database:**
```sql
-- tenants table has feature_flags JSONB column
feature_flags = {
  "HELPDESK_ENABLED": true,
  "ENFORCESENSE_ENABLED": false,
  "QUOTING_ENABLED": true,
  "SALES_ENABLED": true
}
```

---

## 🚀 **Development Workflow**

### **Starting the Platform:**
```powershell
cd "C:\Users\david\Documents\Infometrix"
docker-compose up -d
```

### **Services:**
- **Backend:** http://localhost:8000 (FastAPI) ✅ Running
- **Frontend:** http://localhost:3000 (React CRM) ✅ Running
- **Admin Portal:** http://localhost:3010 (Vue.js Admin) ✅ Running
- **PostgreSQL:** localhost:5432 ✅ Running
- **Redis:** localhost:6379 ✅ Running
- **MinIO:** http://localhost:9002 (API), http://localhost:9092 (Console) ✅ Running
- **MailHog:** http://localhost:3006 (Email testing) ✅ Running
- **Celery Worker:** Background tasks ✅ Running
- **Celery Beat:** Scheduled tasks ✅ Running

### **Default Credentials:**
- Email: `admin@ccs.com`
- Password: `admin123`
- Role: Super Admin
- Tenant: CCS (default)

---

## 🔑 **Key Concepts**

### **1. Multi-Tenancy:**
- Each tenant has isolated data
- Row-level security (RLS) in PostgreSQL
- Tenant context set via middleware

### **2. Module System:**
- Modules are self-contained features
- Registered via `ModuleRegistry`
- Visibility controlled by feature flags
- Navigation grouped by module category

### **3. Feature Flags:**
- Stored in `tenants.feature_flags` JSONB column
- Tenant-specific enable/disable
- Checked before module routes/UI are shown

### **4. RBAC:**
- User roles: SUPER_ADMIN, TENANT_ADMIN, MANAGER, SALES_REP, USER
- Permissions stored as JSON array per user
- Module-level permission checks

---

## 📚 **Important Files to Understand**

### **Backend:**
1. **`backend/app/modules/registry.py`** - Module registration
2. **`backend/app/core/feature_flags.py`** - Feature flag service
3. **`backend/app/models/tenant.py`** - Tenant model (has feature_flags)
4. **`backend/app/api/v1/api.py`** - Main API router (registers modules)
5. **`backend/main.py`** - FastAPI app entry point

### **Frontend:**
1. **`frontend/src/components/Layout.tsx`** - Main layout (needs module navigation)
2. **`frontend/src/types/modules.ts`** - TypeScript module types
3. **`frontend/src/App.tsx`** - Main app component

### **Database:**
1. **`backend/migrations/add_feature_flags.sql`** - Feature flags migration
2. **`backend/app/models/tenant.py`** - Tenant model schema

---

## 🎯 **Current Tasks & Priorities**

### **High Priority:**
1. ✅ Database migration applied
2. 🚧 Frontend navigation grouped by modules
3. 🚧 Helpdesk module fully migrated
4. 📋 EnforceSense integration approach decided

### **Medium Priority:**
1. Module permission system refinement
2. Frontend module visibility based on feature flags
3. Module-specific route protection

### **Low Priority:**
1. Module documentation
2. Module testing framework
3. Module marketplace concept

---

## 🔗 **Integration Points**

### **EnforceSense Integration:**
- **Location:** `C:\Users\david\Documents\EnforceSense\`
- **Status:** Separate repository, will be integrated as module
- **Options:**
  1. Git submodule
  2. Git subtree
  3. Vendor copy
- **Target:** `modules/enforcesense/` or `backend/app/modules/enforcesense/`

### **Legacy CCS Features:**
- Most features already migrated
- Some documentation in `docs/ccs-archive/`
- Reference old workspace for historical context

---

## 🐛 **Known Issues & Gotchas**

1. ✅ **Frontend containers:** Fixed - using `--legacy-peer-deps` flag
2. ✅ **Database:** Fully initialized with 2 tenants and 34 AI prompts
3. **Module navigation:** Not yet implemented in frontend (pending)
4. **EnforceSense:** Not yet integrated, placeholder module exists
5. **Database name:** Still `ccs_quote_tool` for compatibility (intentional)

---

## 📖 **Reading Order for New Agents**

1. **Start Here:** `AGENT_START.md` (quick overview)
2. **This Document:** `docs/AGENT_HANDOVER.md` (comprehensive context)
3. **Migration Plan:** `MIGRATION_PLAN.md` (what we're doing)
4. **Module System:** `backend/app/modules/base.py` (how modules work)
5. **Feature Flags:** `backend/app/core/feature_flags.py` (how flags work)
6. **Legacy Docs:** `docs/ccs-archive/` (historical context)
7. **EnforceSense:** `docs/enforcesense/` (related project)

---

## 🆘 **Getting Help**

### **If You're Stuck:**
1. Check `AGENT_START.md` for quick answers
2. Review `MIGRATION_PLAN.md` for context
3. Check `docs/ccs-archive/` for legacy documentation
4. Review module code in `backend/app/modules/`

### **Common Questions:**
- **"Where is X feature?"** → Check `docs/ccs-archive/` or old workspace
- **"How do modules work?"** → See `backend/app/modules/base.py`
- **"What's the migration status?"** → See `MIGRATION_PLAN.md`
- **"How do I add a module?"** → See module examples in `backend/app/modules/`

---

## 📝 **Notes for AI Agents**

### **When Working on This Project:**
1. **Always check feature flags** before showing module UI
2. **Respect tenant isolation** - never cross tenant boundaries
3. **Use module registry** for navigation, not hardcoded routes
4. **Check permissions** before allowing module access
5. **Reference legacy docs** when migrating features

### **Code Style:**
- Backend: Python (FastAPI, SQLAlchemy, async/await)
- Frontend: React (TypeScript, Material-UI)
- Admin: Vue.js (TypeScript, Element Plus)
- Database: PostgreSQL with JSONB for flexible data

### **Testing:**
- Backend: pytest (when tests exist)
- Frontend: Manual testing (test framework TBD)
- Database: Migrations tested manually

---

## ✅ **Verification Checklist**

Before considering work complete:
- [ ] Feature flags checked for module visibility
- [ ] Tenant isolation verified
- [ ] Module registered in registry
- [ ] Navigation updated (if UI change)
- [ ] Permissions checked
- [ ] Documentation updated
- [ ] Legacy docs referenced if needed

---

**Last Updated:** 2025-12-17  
**Maintained By:** Development Team  
**Questions?** Check `AGENT_START.md` or `MIGRATION_PLAN.md`

---

## ✅ **Current System Status (2025-12-17)**

### **Database:**
- ✅ **2 Tenants:** System Tenant + Default CCS Tenant
- ✅ **34 AI Prompts:** All system prompts seeded
- ✅ **48 Tables:** All application tables created
- ✅ **Feature Flags:** Column added and populated

### **Services:**
- ✅ All 9 services running (Frontend, Admin, Backend, PostgreSQL, Redis, Celery Worker, Celery Beat, MailHog, MinIO)
- ✅ Frontend accessible at http://localhost:3000
- ✅ Admin Portal accessible at http://localhost:3010
- ✅ Backend API accessible at http://localhost:8000

### **Data Migration:**
- ✅ Shared folder copied from CCS
- ⚠️ Database data: Old CCS database volume was corrupted, started fresh
- ✅ System tenant and default tenant created automatically
- ✅ All AI prompts seeded successfully

