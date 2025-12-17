# EnforceSense Module Integration

This directory contains the EnforceSense module integrated into the Infometrix platform.

## Integration Method

**Git Submodule** - EnforceSense is maintained as a separate repository and integrated via git submodule.

## Repository

- **Source:** https://github.com/dje115/enforcesense
- **Local Path:** `modules/enforcesense/`

## Setup

### Initial Setup

```powershell
# Clone the Infometrix repository with submodules
git clone --recursive https://github.com/dje115/infometrix.git

# Or if already cloned, initialize submodules
git submodule update --init --recursive
```

### Updating EnforceSense

```powershell
# Navigate to submodule
cd modules/enforcesense

# Pull latest changes
git pull origin main

# Return to root
cd ../..

# Commit the submodule update
git add modules/enforcesense
git commit -m "chore: Update EnforceSense submodule"
```

## Integration Points

### Authentication

EnforceSense uses the Infometrix authentication system:
- JWT tokens from Infometrix login
- Tenant context from Infometrix session
- User permissions from Infometrix RBAC

### Database

EnforceSense maintains its own database schema but shares:
- Tenant isolation (via `tenant_id` foreign keys)
- User management (references Infometrix `users` table)

### Routes

EnforceSense routes are mounted at:
- `/api/v1/modules/enforcesense/*`

### Navigation

EnforceSense navigation items appear in the left navigation under the "EnforceSense" group when:
- Feature flag `ENFORCESENSE_ENABLED` is `true` for the tenant
- User has appropriate permissions

## Development

### Working with EnforceSense

1. Navigate to the submodule:
   ```powershell
   cd modules/enforcesense
   ```

2. Make changes in the submodule (it's a full git repo)

3. Commit changes in the submodule:
   ```powershell
   git add .
   git commit -m "feat: Add new feature"
   git push origin main
   ```

4. Return to Infometrix root and update submodule reference:
   ```powershell
   cd ../..
   git add modules/enforcesense
   git commit -m "chore: Update EnforceSense submodule"
   ```

### Testing Integration

1. Ensure EnforceSense is enabled for your tenant:
   ```sql
   UPDATE tenants 
   SET feature_flags = jsonb_set(
     feature_flags, 
     '{ENFORCESENSE_ENABLED}', 
     'true'::jsonb
   )
   WHERE id = 'your-tenant-id';
   ```

2. Start the Infometrix platform:
   ```powershell
   docker-compose up -d
   ```

3. Verify EnforceSense routes are accessible:
   - Check `/api/v1/modules/enforcesense/health` (if implemented)
   - Verify navigation shows EnforceSense group

## Module Structure

```
modules/enforcesense/
├── README.md              # This file
├── backend/              # EnforceSense backend (if separate)
├── frontend/             # EnforceSense frontend (if separate)
└── ...                   # Other EnforceSense files
```

## Feature Flags

EnforceSense is controlled by the `ENFORCESENSE_ENABLED` feature flag:
- Set to `true` to enable for a tenant
- Set to `false` to disable (default)

## Permissions

EnforceSense defines these permissions:
- `enforcesense:view` - View EnforceSense module
- `enforcesense:view_cases` - View cases
- `enforcesense:create_case` - Create new cases
- `enforcesense:update_case` - Update cases
- `enforcesense:admin` - Admin access

## Status

**Current Status:** Placeholder/Scaffolding

**Next Steps:**
1. Complete EnforceSense route mounting
2. Implement authentication bridge
3. Define database boundaries
4. Test full integration

---

**Last Updated:** 2025-01-XX

