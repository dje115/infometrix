# Rebranding Guide: CCS Quote Tool v2 → Infometrix

This guide provides step-by-step instructions for rebranding the codebase from CCS to Infometrix.

## ⚠️ Important Notes

- **Database names:** Keep `ccs_quote_tool` database name for compatibility
- **Table names:** Keep all table names unchanged
- **Incremental commits:** Commit after each file group
- **Test after changes:** Ensure app runs after each major change

---

## Files to Update

### 1. README.md

**Search for:**
- `CCS Quote Tool v2`
- `CCS Quote Tool`
- `ccs-quote-tool-v2`
- `CCS Technology Ltd`
- `admin@ccs.com`
- `ccs.com`

**Replace with:**
- `Infometrix`
- `Infometrix Platform`
- `infometrix`
- `Infometrix Ltd` (or your company name)
- `admin@infometrix.com` (or keep as-is)
- `infometrix.com` (or keep as-is)

**Example:**
```markdown
# Before:
# CCS Quote Tool v2 - World-Class AI-Powered CRM & Quoting System

# After:
# Infometrix - World-Class AI-Powered CRM & Quoting Platform
```

---

### 2. Package.json Files

#### frontend/package.json

```json
{
  "name": "infometrix-frontend",
  "description": "Infometrix - Modern CRM & Quoting Platform Frontend",
  ...
}
```

#### admin-portal/package.json

```json
{
  "name": "infometrix-admin-portal",
  "description": "Infometrix - Tenant Admin Portal",
  ...
}
```

---

### 3. Docker Compose Files

#### docker-compose.yml

**Search for:**
- `ccs-postgres` → `infometrix-postgres`
- `ccs-redis` → `infometrix-redis`
- `ccs-backend` → `infometrix-backend`
- `ccs-frontend` → `infometrix-frontend`
- `ccs-admin-portal` → `infometrix-admin-portal`
- `ccs-celery-worker` → `infometrix-celery-worker`
- `ccs-celery-beat` → `infometrix-celery-beat`
- `ccs-mailhog` → `infometrix-mailhog`
- `ccs-minio` → `infometrix-minio`
- `ccs-network` → `infometrix-network`
- `ccs_quote_tool` → Keep as-is (database name)
- `ccs-quote-tool` → `infometrix` (bucket name)

**Note:** Keep database name `ccs_quote_tool` for compatibility.

---

### 4. Frontend Layout

#### frontend/src/components/Layout.tsx

**Line 160:**
```typescript
// Before:
<Typography variant="h6" noWrap component="div">
  CCS Quote Tool
</Typography>

// After:
<Typography variant="h6" noWrap component="div">
  Infometrix
</Typography>
```

**Line 220:**
```typescript
// Before:
{menuItems.find(item => item.path === location.pathname)?.text || 'CCS Quote Tool'}

// After:
{menuItems.find(item => item.path === location.pathname)?.text || 'Infometrix'}
```

---

### 5. Environment Files

#### env.example

**Search for:**
- `CCS Quote Tool` → `Infometrix`
- `ccs.com` → `infometrix.com` (or keep as-is)
- `admin@ccs.com` → `admin@infometrix.com` (or keep as-is)

**Example:**
```env
# Before:
SMTP_FROM_NAME=CCS Quote Tool
SMTP_FROM_EMAIL=noreply@ccs.com

# After:
SMTP_FROM_NAME=Infometrix
SMTP_FROM_EMAIL=noreply@infometrix.com
```

---

### 6. Backend Configuration

#### backend/app/core/config.py (if exists)

**Search for:**
- `CCS Quote Tool` → `Infometrix`
- `ccs.com` → `infometrix.com`

---

### 7. CI/CD Files

#### .github/workflows/*.yml (if exists)

**Search for:**
- `ccs-quote-tool-v2` → `infometrix`
- `CCS Quote Tool` → `Infometrix`

---

## Rebranding Script (PowerShell)

**⚠️ Use with caution - review changes before committing**

```powershell
# Navigate to project root
cd "C:\Users\david\Documents\Infometrix"

# Backup first (recommended)
git add .
git commit -m "chore: Backup before rebranding"

# Replace in README.md
(Get-Content README.md) -replace 'CCS Quote Tool v2', 'Infometrix' | Set-Content README.md
(Get-Content README.md) -replace 'CCS Quote Tool', 'Infometrix' | Set-Content README.md
(Get-Content README.md) -replace 'ccs-quote-tool-v2', 'infometrix' | Set-Content README.md

# Replace in package.json files
(Get-Content frontend/package.json) -replace 'ccs-quote-tool-v2-frontend', 'infometrix-frontend' | Set-Content frontend/package.json
(Get-Content frontend/package.json) -replace 'CCS Quote Tool v2', 'Infometrix' | Set-Content frontend/package.json

(Get-Content admin-portal/package.json) -replace 'ccs-admin-portal', 'infometrix-admin-portal' | Set-Content admin-portal/package.json
(Get-Content admin-portal/package.json) -replace 'CCS Quote Tool v2', 'Infometrix' | Set-Content admin-portal/package.json

# Replace in docker-compose files (be careful with database name)
(Get-Content docker-compose.yml) -replace 'ccs-postgres', 'infometrix-postgres' | Set-Content docker-compose.yml
(Get-Content docker-compose.yml) -replace 'ccs-redis', 'infometrix-redis' | Set-Content docker-compose.yml
(Get-Content docker-compose.yml) -replace 'ccs-backend', 'infometrix-backend' | Set-Content docker-compose.yml
(Get-Content docker-compose.yml) -replace 'ccs-frontend', 'infometrix-frontend' | Set-Content docker-compose.yml
(Get-Content docker-compose.yml) -replace 'ccs-admin-portal', 'infometrix-admin-portal' | Set-Content docker-compose.yml
(Get-Content docker-compose.yml) -replace 'ccs-celery-worker', 'infometrix-celery-worker' | Set-Content docker-compose.yml
(Get-Content docker-compose.yml) -replace 'ccs-celery-beat', 'infometrix-celery-beat' | Set-Content docker-compose.yml
(Get-Content docker-compose.yml) -replace 'ccs-mailhog', 'infometrix-mailhog' | Set-Content docker-compose.yml
(Get-Content docker-compose.yml) -replace 'ccs-minio', 'infometrix-minio' | Set-Content docker-compose.yml
(Get-Content docker-compose.yml) -replace 'ccs-network', 'infometrix-network' | Set-Content docker-compose.yml
# Note: Keep ccs_quote_tool database name

# Review changes
git diff

# Commit
git add .
git commit -m "rebrand: Update branding from CCS to Infometrix"
```

---

## Manual Updates Required

### Frontend Layout Component

**File:** `frontend/src/components/Layout.tsx`

**Manual edits needed:**
1. Line 160: Change "CCS Quote Tool" to "Infometrix"
2. Line 220: Change fallback text to "Infometrix"

### Environment Variables

**Files:** `.env`, `.env.local`, production configs

**Manual updates:**
- Update `SMTP_FROM_NAME`
- Update `SMTP_FROM_EMAIL` (if changed)
- Update any hardcoded URLs

### Documentation Files

**Files:** All `.md` files in root and `docs/`

**Manual review needed:**
- Update company references
- Update email addresses
- Update URLs
- Update copyright notices

---

## Verification After Rebranding

1. **Build Test:**
   ```powershell
   cd frontend
   npm run build
   cd ../admin-portal
   npm run build
   ```

2. **Docker Test:**
   ```powershell
   docker-compose up -d --build
   docker-compose logs -f
   ```

3. **UI Check:**
   - Open http://localhost:3000
   - Verify app title shows "Infometrix"
   - Check browser tab title
   - Verify no "CCS" references in UI

4. **Search for Remaining References:**
   ```powershell
   # Search for remaining CCS references (excluding database names)
   Select-String -Path "*.md","*.json","*.tsx","*.ts","*.py" -Pattern "CCS|ccs-quote" -Exclude "ccs_quote_tool"
   ```

---

## Commit Strategy

**Recommended incremental commits:**

```powershell
# Commit 1: Documentation
git add README.md *.md
git commit -m "rebrand: Update documentation to Infometrix"

# Commit 2: Package files
git add frontend/package.json admin-portal/package.json
git commit -m "rebrand: Update package names to Infometrix"

# Commit 3: Docker configs
git add docker-compose*.yml
git commit -m "rebrand: Update Docker service names to Infometrix"

# Commit 4: Frontend UI
git add frontend/src/components/Layout.tsx
git commit -m "rebrand: Update app title to Infometrix"

# Commit 5: Environment files
git add env.example
git commit -m "rebrand: Update environment file defaults"
```

---

## Rollback

If rebranding causes issues:

```powershell
# Revert last commit
git reset --hard HEAD~1

# Or revert specific file
git checkout HEAD -- README.md
```

---

**Last Updated:** 2025-01-XX

