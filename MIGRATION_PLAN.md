# Infometrix Platform Migration Plan

## Overview
This document outlines the step-by-step migration plan from CCS Quote Tool v2 to Infometrix platform, preserving history and setting up modular architecture.

---

## Phase 1: Repository Migration & Setup

### Step 1.1: Create New GitHub Repository
**Goal:** Create new `infometrix` repository (not a rename)

**Actions:**
1. Go to https://github.com/new
2. Repository name: `infometrix` (or `infometrix-platform` if preferred)
3. Description: "Infometrix - Multi-tenant CRM platform with modular architecture"
4. Visibility: Private (or Public as needed)
5. **DO NOT** initialize with README, .gitignore, or license (we'll migrate existing)

**Recommended Name:** `infometrix` (simpler, cleaner)

---

### Step 1.2: Migrate Code with History Preservation
**Goal:** Preserve full git history from ccs-quote-tool-v2

**Option A: Mirror Push (Recommended)**
```powershell
# Navigate to existing repo
cd "C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2"

# Add new remote (replace YOUR_USERNAME with dje115)
git remote add infometrix https://github.com/dje115/infometrix.git

# Push all branches and tags
git push infometrix --all
git push infometrix --tags

# Verify
git remote -v
```

**Option B: Fresh Start (If history preservation fails)**
```powershell
# Create new repo folder
cd "C:\Users\david\Documents"
mkdir Infometrix
cd Infometrix

# Initialize git
git init
git remote add origin https://github.com/dje115/infometrix.git

# Copy files (excluding .git)
# Then commit
git add .
git commit -m "Initial commit: Migrate from CCS Quote Tool v2 to Infometrix"

# Push
git push -u origin main
```

**Recommendation:** Use Option A (mirror push) to preserve history.

---

### Step 1.3: Local Clone & Relocate
**Goal:** Get working copy in `C:\Users\david\Documents\Infometrix`

**Commands:**
```powershell
# If using Option A (mirror push):
cd "C:\Users\david\Documents"
git clone https://github.com/dje115/infometrix.git Infometrix
cd Infometrix

# If using Option B (fresh start):
# Already in Infometrix folder from Step 1.2
```

---

### Step 1.4: Update Remotes
**Goal:** Ensure local points to new Infometrix repo

**Commands:**
```powershell
cd "C:\Users\david\Documents\Infometrix"

# Verify current remotes
git remote -v

# If old remote exists, remove it
git remote remove origin  # if needed

# Add/update to new repo
git remote add origin https://github.com/dje115/infometrix.git

# Verify
git remote -v
# Should show:
# origin  https://github.com/dje115/infometrix.git (fetch)
# origin  https://github.com/dje115/infometrix.git (push)

# Test connection
git fetch origin
```

---

## Phase 2: Rebranding (Incremental, Safe)

### Step 2.1: Search & Replace Branding Strings
**Goal:** Update all CCS references to Infometrix (minimal, safe changes)

**Files to Update:**
- `README.md` - Title, descriptions
- `frontend/package.json` - name, description
- `admin-portal/package.json` - name, description
- `docker-compose.yml` - service names, container names
- `docker-compose.prod.yml` - service names, container names
- `docker-compose.dev.yml` - service names, container names
- `env.example` - comments, default values
- `frontend/src/components/Layout.tsx` - App title
- Any CI/CD files (`.github/workflows/*`)

**Search Patterns:**
- `ccs-quote-tool-v2` → `infometrix`
- `CCS Quote Tool` → `Infometrix`
- `ccs-quote-tool` → `infometrix`
- `ccs_quote_tool` → `infometrix` (database name - keep for compatibility)
- `ccs.com` → `infometrix.com` (or keep as-is for now)

**Commit Strategy:**
```powershell
# Commit after each major file group
git add README.md frontend/package.json admin-portal/package.json
git commit -m "rebrand: Update package names and README to Infometrix"

git add docker-compose*.yml
git commit -m "rebrand: Update Docker service names to Infometrix"

git add frontend/src/components/Layout.tsx
git commit -m "rebrand: Update app title to Infometrix"
```

**⚠️ Important:** Do NOT rename database tables/columns yet. Keep `ccs_quote_tool` database name for compatibility.

---

## Phase 3: Module Scaffolding

### Step 3.1: Create Module Registry System
**Goal:** Build foundation for modular architecture

**Structure:**
```
backend/
  app/
    modules/
      __init__.py
      registry.py          # Module registry
      base.py              # Base module class
      helpdesk/
        __init__.py
        routes.py          # Module routes
        permissions.py     # Module permissions
      enforcesense/
        __init__.py
        README.md          # Integration docs
      quoting/
        __init__.py
        routes.py
      sales/
        __init__.py
        routes.py
```

**Files to Create:**
1. `backend/app/modules/registry.py` - Central registry
2. `backend/app/modules/base.py` - Base module interface
3. `backend/app/core/feature_flags.py` - Feature flag system
4. `backend/app/core/module_permissions.py` - Module permission checks

---

### Step 3.2: Feature Flags System
**Goal:** Tenant-level feature flags for modules

**Database Migration:**
```sql
-- Add feature_flags JSON column to tenants table
ALTER TABLE tenants ADD COLUMN IF NOT EXISTS feature_flags JSONB DEFAULT '{}'::jsonb;

-- Example flags:
-- {
--   "helpdesk_enabled": true,
--   "enforcesense_enabled": false,
--   "quoting_enabled": true
-- }
```

**Implementation:**
- `backend/app/core/feature_flags.py` - Feature flag service
- Check flags in middleware/dependencies
- Expose via API for frontend

---

### Step 3.3: Module Permissions System
**Goal:** RBAC per module

**Structure:**
```python
# Permissions format: module:action
# Examples:
# - helpdesk:view_tickets
# - helpdesk:create_ticket
# - helpdesk:admin
# - enforcesense:view_cases
# - quoting:create_quote
```

**Integration:**
- Extend existing `backend/app/core/permissions.py`
- Add module-aware permission checks
- Update user roles to include module permissions

---

## Phase 4: Left Navigation by Modules

### Step 4.1: Define Module Groups
**Goal:** Organize navigation by module boundaries

**Module Groups:**
1. **Sales / CRM** (Core)
   - Dashboard
   - Customers
   - Leads
   - Opportunities
   - Campaigns

2. **Helpdesk**
   - Helpdesk (Tickets)
   - Helpdesk Performance
   - NPA Dashboard
   - Knowledge Base
   - Ticket Templates
   - Ticket Macros

3. **Quoting & Proposals**
   - Quotes
   - Contracts
   - Contract Templates

4. **EnforceSense** (Placeholder)
   - EnforceSense Dashboard (placeholder)
   - Cases (placeholder)
   - Reports (placeholder)

5. **Settings**
   - Settings
   - Users
   - Compliance
   - AI Prompts

---

### Step 4.2: Update Frontend Navigation
**Goal:** Group navigation items by modules

**File:** `frontend/src/components/Layout.tsx`

**Changes:**
- Convert flat `menuItems` array to grouped structure
- Add module metadata (group, feature flag, permissions)
- Render grouped navigation with collapsible sections
- Filter by feature flags and permissions

**Structure:**
```typescript
interface MenuGroup {
  id: string;
  label: string;
  featureFlag?: string;
  items: MenuItem[];
}

interface MenuItem {
  text: string;
  icon: ReactNode;
  path: string;
  permission?: string;
  adminOnly?: boolean;
}
```

---

## Phase 5: EnforceSense Integration Scaffolding

### Step 5.1: Choose Integration Method
**Goal:** Decide how EnforceSense integrates

**Option A: Git Submodule (Recommended)**
**Pros:**
- Independent versioning
- Clear separation
- Easy updates

**Cons:**
- Requires submodule commands
- Slightly more complex workflow

**Commands:**
```powershell
cd "C:\Users\david\Documents\Infometrix"
git submodule add https://github.com/dje115/enforcesense.git modules/enforcesense

# Initialize submodules (for other developers)
git submodule update --init --recursive
```

**Option B: Git Subtree**
**Pros:**
- Simpler workflow (no submodule commands)
- Code appears directly in repo

**Cons:**
- Less clear separation
- Harder to update independently

**Commands:**
```powershell
cd "C:\Users\david\Documents\Infometrix"
git subtree add --prefix=modules/enforcesense https://github.com/dje115/enforcesense.git main --squash
```

**Option C: Vendor Copy**
**Pros:**
- Simplest
- No git complexity

**Cons:**
- No automatic updates
- Manual sync required

**Recommendation:** **Option A (Git Submodule)** for Windows + Cursor workflow
- Cursor handles submodules well
- Clear separation of concerns
- Independent versioning

---

### Step 5.2: Create Integration Structure
**Goal:** Scaffold EnforceSense module integration

**Structure:**
```
modules/
  enforcesense/
    README.md              # Integration guide
    routes.py              # Route mounting
    auth_bridge.py         # Auth integration
    db_bridge.py           # Database boundary
```

**Files to Create:**
1. `modules/enforcesense/README.md` - Integration documentation
2. `backend/app/modules/enforcesense/routes.py` - Route mounting
3. `backend/app/modules/enforcesense/__init__.py` - Module initialization

---

## Phase 6: Helpdesk Module Isolation (Milestone 1)

### Step 6.1: Identify Helpdesk Components
**Goal:** Find all helpdesk-related code

**Backend:**
- `backend/app/models/helpdesk.py` - Models
- `backend/app/api/v1/endpoints/helpdesk.py` - API endpoints
- `backend/app/api/v1/endpoints/sla.py` - SLA endpoints
- `backend/app/services/helpdesk*.py` - Services
- `backend/app/tasks/*ticket*.py` - Celery tasks

**Frontend:**
- `frontend/src/pages/Helpdesk.tsx`
- `frontend/src/pages/TicketDetail.tsx`
- `frontend/src/pages/HelpdeskPerformance.tsx`
- `frontend/src/pages/TicketTemplates.tsx`
- `frontend/src/pages/TicketMacros.tsx`
- `frontend/src/pages/KnowledgeBase.tsx`
- `frontend/src/pages/SLAManagement.tsx`
- `frontend/src/pages/SLADashboard.tsx`
- `frontend/src/pages/SLAReportBuilder.tsx`
- `frontend/src/components/Ticket*.tsx` - All ticket components
- `frontend/src/components/NPADashboard.tsx`

**Routes:**
- `/helpdesk`
- `/helpdesk/performance`
- `/helpdesk/npa-dashboard`
- `/helpdesk/knowledge-base`
- `/helpdesk/templates`
- `/helpdesk/macros`
- `/sla/*` (SLA routes)

---

### Step 6.2: Move Helpdesk Code to Module
**Goal:** Organize helpdesk under `modules/helpdesk/`

**Backend Structure:**
```
backend/app/modules/helpdesk/
  __init__.py
  models.py              # Move from app/models/helpdesk.py
  routes.py              # Move from app/api/v1/endpoints/helpdesk.py
  sla_routes.py          # Move from app/api/v1/endpoints/sla.py
  services/
    __init__.py
    ticket_service.py
    sla_service.py
  tasks/
    __init__.py
    ticket_tasks.py
    sla_tasks.py
  permissions.py         # Module permissions
```

**Frontend Structure:**
```
frontend/src/modules/
  helpdesk/
    pages/
      Helpdesk.tsx
      TicketDetail.tsx
      HelpdeskPerformance.tsx
      TicketTemplates.tsx
      TicketMacros.tsx
      KnowledgeBase.tsx
      SLAManagement.tsx
      SLADashboard.tsx
      SLAReportBuilder.tsx
    components/
      TicketComposer.tsx
      TicketDetailDialog.tsx
      TicketBulkActions.tsx
      TicketChatbot.tsx
      TicketKBAnswer.tsx
      TicketLinkDialog.tsx
      TicketMacroMenu.tsx
      TicketMergeDialog.tsx
      TicketNPA.tsx
      TicketTemplateSelector.tsx
      TimeTrackingDialog.tsx
      NPADashboard.tsx
      CustomerSLAWidget.tsx
      CustomerSLAHistory.tsx
    routes.tsx            # Module routes
```

---

### Step 6.3: Add Feature Flag
**Goal:** Control helpdesk visibility per tenant

**Implementation:**
1. Add `HELPDESK_ENABLED` feature flag check
2. Update module registry to include helpdesk
3. Add permission checks: `helpdesk:view`, `helpdesk:create`, `helpdesk:admin`
4. Update navigation to respect feature flag
5. Update routes to check feature flag

---

### Step 6.4: Update Routes & Imports
**Goal:** Keep routing working after move

**Changes:**
- Update `backend/app/api/v1/api.py` to mount helpdesk routes conditionally
- Update `frontend/src/App.tsx` to import from module paths
- Update all import statements
- Test all routes work

---

## Phase 7: Verification & Testing

### Step 7.1: Build & Lint
**Commands:**
```powershell
# Backend
cd backend
python -m pytest tests/  # If tests exist
python -m pylint app/    # If linter configured

# Frontend
cd frontend
npm run lint
npm run type-check
npm run build

# Admin Portal
cd admin-portal
npm run lint
npm run build
```

---

### Step 7.2: Docker Test
```powershell
# Test development build
docker-compose up -d --build
docker-compose logs -f

# Test production build
docker-compose -f docker-compose.prod.yml up -d --build
```

---

### Step 7.3: Verification Checklist
**Navigation:**
- [ ] Left nav shows grouped modules
- [ ] Helpdesk group appears/disappears based on feature flag
- [ ] All routes accessible
- [ ] Permissions work correctly

**Helpdesk Module:**
- [ ] Helpdesk page loads
- [ ] Ticket creation works
- [ ] Ticket detail page works
- [ ] SLA features work
- [ ] All helpdesk routes accessible

**Branding:**
- [ ] App title shows "Infometrix"
- [ ] No "CCS" references in UI (except database names)
- [ ] Package names updated

**Database:**
- [ ] Existing data accessible
- [ ] No schema changes (compatibility maintained)

---

## Phase 8: Deliverables

### Files Changed
**Rebranding:**
- `README.md`
- `frontend/package.json`
- `admin-portal/package.json`
- `docker-compose.yml`
- `docker-compose.prod.yml`
- `docker-compose.dev.yml`
- `env.example`
- `frontend/src/components/Layout.tsx`

**Module System:**
- `backend/app/modules/` (new directory)
- `backend/app/core/feature_flags.py` (new)
- `backend/app/core/module_permissions.py` (new)
- `backend/migrations/add_feature_flags.sql` (new)

**Navigation:**
- `frontend/src/components/Layout.tsx` (updated)

**Helpdesk Module:**
- `backend/app/modules/helpdesk/` (new, moved from existing)
- `frontend/src/modules/helpdesk/` (new, moved from existing)

**EnforceSense:**
- `modules/enforcesense/` (submodule)
- `backend/app/modules/enforcesense/` (scaffolding)

---

### Commands Summary

**Git Migration:**
```powershell
# Step 1: Add remote
cd "C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2"
git remote add infometrix https://github.com/dje115/infometrix.git
git push infometrix --all
git push infometrix --tags

# Step 2: Clone locally
cd "C:\Users\david\Documents"
git clone https://github.com/dje115/infometrix.git Infometrix
cd Infometrix
git remote -v  # Verify
```

**EnforceSense Submodule:**
```powershell
cd "C:\Users\david\Documents\Infometrix"
git submodule add https://github.com/dje115/enforcesense.git modules/enforcesense
```

**Build & Test:**
```powershell
# Lint
cd frontend && npm run lint
cd admin-portal && npm run lint

# Build
cd frontend && npm run build
cd admin-portal && npm run build

# Docker
docker-compose up -d --build
```

---

### TODO: Manual Items

**Database Schema:**
- [ ] Keep `ccs_quote_tool` database name (compatibility)
- [ ] Keep table names unchanged (compatibility)
- [ ] Add `feature_flags` JSONB column to `tenants` table
- [ ] Consider migration script for existing tenants

**Environment Variables:**
- [ ] Update `.env` files with new service names
- [ ] Update Docker environment variables
- [ ] Update CI/CD configs if present

**Documentation:**
- [ ] Update all markdown docs with new branding
- [ ] Update API documentation
- [ ] Create module development guide

**EnforceSense Integration:**
- [ ] Complete EnforceSense route mounting
- [ ] Implement auth bridge
- [ ] Define database boundaries
- [ ] Test integration

---

## Safety Notes

1. **Incremental Commits:** Commit after each logical step
2. **Test After Each Phase:** Ensure app runs after each major change
3. **Database Compatibility:** Keep existing schema names for now
4. **Feature Flags:** Use flags to disable modules during migration
5. **Rollback Plan:** Keep old repo as backup until migration verified

---

## Next Steps After Migration

1. Complete EnforceSense integration
2. Migrate other modules (Quoting, Sales) to module structure
3. Consider database schema migration (rename tables if needed)
4. Add module marketplace concept
5. Enhance feature flag system with UI

---

**Status:** Ready for execution
**Last Updated:** 2025-01-XX

