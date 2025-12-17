# Infometrix Migration Deliverables

## Summary

This document lists all files changed, commands to run, verification steps, and remaining TODOs for the Infometrix platform migration.

---

## Files Changed

### Migration Documentation
- ✅ `MIGRATION_PLAN.md` - Complete migration plan with numbered steps
- ✅ `GITHUB_MIGRATION_COMMANDS.md` - Exact commands for GitHub migration
- ✅ `DELIVERABLES.md` - This file

### Backend Module System
- ✅ `backend/app/modules/__init__.py` - Module package init
- ✅ `backend/app/modules/base.py` - Base module interface
- ✅ `backend/app/modules/registry.py` - Module registry system
- ✅ `backend/app/core/feature_flags.py` - Feature flag service
- ✅ `backend/app/modules/helpdesk/__init__.py` - Helpdesk module init
- ✅ `backend/app/modules/helpdesk/module.py` - Helpdesk module implementation
- ✅ `backend/app/modules/enforcesense/__init__.py` - EnforceSense module init
- ✅ `backend/app/modules/enforcesense/module.py` - EnforceSense module placeholder
- ✅ `backend/app/models/tenant.py` - Added `feature_flags` column
- ✅ `backend/migrations/add_feature_flags.sql` - Database migration for feature flags

### Frontend Module System
- ✅ `frontend/src/types/modules.ts` - Module navigation types and core groups

### EnforceSense Integration
- ✅ `modules/enforcesense/README.md` - Integration documentation

### Rebranding (Pending)
- ⏳ `README.md` - Update to Infometrix branding
- ⏳ `frontend/package.json` - Update name/description
- ⏳ `admin-portal/package.json` - Update name/description
- ⏳ `docker-compose.yml` - Update service names
- ⏳ `docker-compose.prod.yml` - Update service names
- ⏳ `docker-compose.dev.yml` - Update service names
- ⏳ `env.example` - Update comments/defaults
- ⏳ `frontend/src/components/Layout.tsx` - Update app title and navigation

---

## Commands to Run

### 1. Database Migration

```powershell
# Apply feature flags migration
cd backend
Get-Content "migrations/add_feature_flags.sql" | docker-compose exec -T postgres psql -U postgres -d ccs_quote_tool

# Or if running locally:
psql -U postgres -d ccs_quote_tool -f migrations/add_feature_flags.sql
```

### 2. Backend Lint/Test

```powershell
# Navigate to backend
cd backend

# Run tests (if available)
python -m pytest tests/ -v

# Run linter (if configured)
python -m pylint app/modules/ app/core/feature_flags.py

# Type checking (if using mypy)
mypy app/modules/ app/core/feature_flags.py
```

### 3. Frontend Lint/Build

```powershell
# Navigate to frontend
cd frontend

# Install dependencies (if needed)
npm install

# Run linter
npm run lint

# Run type check
npm run type-check

# Build for production
npm run build
```

### 4. Admin Portal Lint/Build

```powershell
# Navigate to admin portal
cd admin-portal

# Install dependencies (if needed)
npm install

# Run linter
npm run lint

# Build for production
npm run build
```

### 5. Docker Build & Test

```powershell
# Test development build
docker-compose up -d --build
docker-compose logs -f

# Test production build
docker-compose -f docker-compose.prod.yml up -d --build
docker-compose -f docker-compose.prod.yml logs -f

# Stop when done
docker-compose down
# or
docker-compose -f docker-compose.prod.yml down
```

### 6. GitHub Migration

See `GITHUB_MIGRATION_COMMANDS.md` for detailed steps.

**Quick Summary:**
```powershell
# Step 1: Add remote to existing repo
cd "C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2"
git remote add infometrix https://github.com/dje115/infometrix.git
git push infometrix --all
git push infometrix --tags

# Step 2: Clone locally
cd "C:\Users\david\Documents"
git clone https://github.com/dje115/infometrix.git Infometrix
cd Infometrix

# Step 3: Verify
git remote -v
```

### 7. EnforceSense Submodule

```powershell
cd "C:\Users\david\Documents\Infometrix"
git submodule add https://github.com/dje115/enforcesense.git modules/enforcesense
git submodule update --init --recursive
```

---

## Verification Checklist

### Pre-Migration
- [ ] Existing app runs successfully
- [ ] All tests pass
- [ ] Database backup created (recommended)

### Post-Migration (GitHub)
- [ ] New repository created at https://github.com/dje115/infometrix
- [ ] All branches pushed
- [ ] All tags pushed
- [ ] Local clone works
- [ ] Commit history preserved (if using mirror push)

### Post-Migration (Code)
- [ ] Database migration applied successfully
- [ ] Backend starts without errors
- [ ] Frontend builds without errors
- [ ] Admin portal builds without errors
- [ ] Docker containers start successfully

### Module System
- [ ] Module registry loads without errors
- [ ] Helpdesk module registers successfully
- [ ] EnforceSense module registers successfully
- [ ] Feature flags service works
- [ ] Feature flags can be set/get per tenant

### Navigation
- [ ] Left navigation shows grouped structure
- [ ] Helpdesk group appears when `HELPDESK_ENABLED=true`
- [ ] Helpdesk group hidden when `HELPDESK_ENABLED=false`
- [ ] EnforceSense group appears when `ENFORCESENSE_ENABLED=true`
- [ ] Permissions filter navigation items correctly

### Helpdesk Module
- [ ] Helpdesk page loads: `/helpdesk`
- [ ] Ticket creation works
- [ ] Ticket detail page works: `/helpdesk/tickets/:id`
- [ ] SLA features accessible: `/sla`, `/sla/dashboard`
- [ ] Knowledge base accessible: `/helpdesk/knowledge-base`
- [ ] All helpdesk routes work

### Branding
- [ ] App title shows "Infometrix" (after rebranding)
- [ ] No "CCS Quote Tool" in UI (after rebranding)
- [ ] Package names updated (after rebranding)
- [ ] Docker service names updated (after rebranding)

### Database
- [ ] Existing data accessible
- [ ] Feature flags column exists in `tenants` table
- [ ] Default feature flags set for existing tenants
- [ ] No schema breaking changes

---

## Remaining TODOs

### High Priority
1. **Rebrand Key Files**
   - [ ] Update `README.md` with Infometrix branding
   - [ ] Update `frontend/package.json` name/description
   - [ ] Update `admin-portal/package.json` name/description
   - [ ] Update `docker-compose*.yml` service names
   - [ ] Update `frontend/src/components/Layout.tsx` app title
   - [ ] Update `env.example` comments

2. **Frontend Navigation Update**
   - [ ] Update `Layout.tsx` to use grouped navigation
   - [ ] Add feature flag checking in frontend
   - [ ] Add permission checking in frontend
   - [ ] Test navigation filtering

3. **Backend Module Registration**
   - [ ] Register modules in `backend/app/api/v1/api.py`
   - [ ] Mount module routes conditionally
   - [ ] Add feature flag middleware
   - [ ] Test module route mounting

### Medium Priority
4. **Helpdesk Module Isolation**
   - [ ] Move helpdesk models to `modules/helpdesk/`
   - [ ] Move helpdesk services to `modules/helpdesk/`
   - [ ] Move helpdesk tasks to `modules/helpdesk/`
   - [ ] Move frontend helpdesk pages to `modules/helpdesk/`
   - [ ] Update all imports
   - [ ] Test all helpdesk functionality

5. **EnforceSense Integration**
   - [ ] Add EnforceSense as git submodule
   - [ ] Create route mounting in EnforceSense module
   - [ ] Implement authentication bridge
   - [ ] Define database boundaries
   - [ ] Test integration

### Low Priority
6. **Documentation**
   - [ ] Update all markdown docs with new branding
   - [ ] Create module development guide
   - [ ] Update API documentation
   - [ ] Create feature flag management guide

7. **Database Schema (Future)**
   - [ ] Consider renaming `ccs_quote_tool` database (compatibility layer first)
   - [ ] Consider renaming tables (compatibility layer first)
   - [ ] Create migration scripts for schema changes

---

## Manual Items That Cannot Be Auto-Renamed

### Database Schema Names
**⚠️ Keep these unchanged for compatibility:**
- Database name: `ccs_quote_tool` (keep as-is)
- Table names: All existing table names (keep as-is)
- Column names: All existing column names (keep as-is)

**Reason:** Breaking changes would require data migration. Add compatibility mapping layer instead.

### Environment Variables
**Update manually in:**
- `.env` files (local development)
- Production environment configuration
- CI/CD pipeline configuration
- Docker environment files

### Configuration Files
**Update manually:**
- Any hardcoded references in config files
- API endpoint URLs in external services
- Webhook configurations
- Third-party integrations

---

## Testing Strategy

### Unit Tests
- Test module registry
- Test feature flag service
- Test module registration
- Test permission checking

### Integration Tests
- Test module route mounting
- Test feature flag filtering
- Test navigation generation
- Test helpdesk module isolation

### E2E Tests
- Test full navigation flow
- Test feature flag enable/disable
- Test permission-based access
- Test helpdesk functionality

---

## Rollback Plan

If migration fails:

1. **Git Rollback:**
   ```powershell
   # Revert to previous commit
   git reset --hard HEAD~1
   
   # Or revert specific commits
   git revert <commit-hash>
   ```

2. **Database Rollback:**
   ```sql
   -- Remove feature_flags column (if migration applied)
   ALTER TABLE tenants DROP COLUMN IF EXISTS feature_flags;
   ```

3. **Code Rollback:**
   - Remove module system files
   - Revert Layout.tsx changes
   - Revert package.json changes

4. **Docker Rollback:**
   ```powershell
   # Use previous docker-compose config
   docker-compose down
   # Restore old config files
   ```

---

## Success Criteria

Migration is successful when:

✅ All verification checklist items pass  
✅ App runs in development mode  
✅ App runs in production mode (Docker)  
✅ All existing features work  
✅ Module system functional  
✅ Feature flags work  
✅ Navigation grouped correctly  
✅ Helpdesk module isolated  
✅ EnforceSense scaffolding in place  
✅ No breaking changes to database  
✅ All tests pass  

---

**Last Updated:** 2025-01-XX  
**Status:** In Progress - Module scaffolding complete, rebranding pending

