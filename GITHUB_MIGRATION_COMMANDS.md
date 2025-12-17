# GitHub Migration Commands

## Step-by-Step Commands for Migrating to Infometrix Repository

### Prerequisites
- Git installed
- GitHub account (dje115)
- Access to both repositories

---

## Step 1: Create New GitHub Repository

**Manual Step (via GitHub Web UI):**
1. Go to: https://github.com/new
2. Repository name: `infometrix`
3. Description: "Infometrix - Multi-tenant CRM platform with modular architecture"
4. Visibility: Private (or Public as needed)
5. **DO NOT** initialize with README, .gitignore, or license
6. Click "Create repository"

**Note:** After creation, GitHub will show setup instructions. **Ignore them** - we'll use the commands below.

---

## Step 2: Migrate Code with History (Recommended)

### Option A: Mirror Push (Preserves Full History)

```powershell
# Navigate to existing CCS Quote Tool v2 repository
cd "C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2"

# Verify current remotes
git remote -v

# Add new Infometrix remote (replace YOUR_USERNAME if different)
git remote add infometrix https://github.com/dje115/infometrix.git

# Push all branches
git push infometrix --all

# Push all tags
git push infometrix --tags

# Verify
git remote -v
# Should show both old and new remotes
```

**If you want to remove the old remote after verification:**
```powershell
# Only do this AFTER verifying everything works
git remote remove origin  # or whatever the old remote was named
```

---

### Option B: Fresh Start (If History Preservation Fails)

**⚠️ Only use if Option A fails**

```powershell
# Create new directory
cd "C:\Users\david\Documents"
mkdir Infometrix
cd Infometrix

# Initialize git
git init
git remote add origin https://github.com/dje115/infometrix.git

# Copy all files from old repo (excluding .git folder)
# Use PowerShell to copy:
Copy-Item -Path "..\CCS quote tool\CCS Quote Tool v2\*" -Destination "." -Recurse -Exclude ".git"

# Add and commit
git add .
git commit -m "Initial commit: Migrate from CCS Quote Tool v2 to Infometrix"

# Push to new repo
git branch -M main
git push -u origin main
```

---

## Step 3: Local Clone & Setup

### If Using Option A (Mirror Push):

```powershell
# Navigate to Documents
cd "C:\Users\david\Documents"

# Clone the new repository
git clone https://github.com/dje115/infometrix.git Infometrix

# Navigate into it
cd Infometrix

# Verify remotes
git remote -v
# Should show:
# origin  https://github.com/dje115/infometrix.git (fetch)
# origin  https://github.com/dje115/infometrix.git (push)
```

### If Using Option B (Fresh Start):

```powershell
# You're already in the Infometrix folder from Step 2
# Just verify:
git remote -v
```

---

## Step 4: Update Remotes (If Needed)

```powershell
cd "C:\Users\david\Documents\Infometrix"

# Check current remotes
git remote -v

# If you need to update origin:
git remote set-url origin https://github.com/dje115/infometrix.git

# Or if origin doesn't exist:
git remote add origin https://github.com/dje115/infometrix.git

# Verify
git remote -v

# Test connection
git fetch origin
git branch -a  # Should show remote branches
```

---

## Step 5: Verify Migration

```powershell
# Check commit history (if using Option A)
git log --oneline -10

# Check branches
git branch -a

# Check tags
git tag

# Verify files
ls  # Should see all project files
```

---

## Step 6: Add EnforceSense Submodule (After Migration)

```powershell
cd "C:\Users\david\Documents\Infometrix"

# Add EnforceSense as submodule
git submodule add https://github.com/dje115/enforcesense.git modules/enforcesense

# Initialize submodules (if needed)
git submodule update --init --recursive

# Commit submodule addition
git add .gitmodules modules/enforcesense
git commit -m "feat: Add EnforceSense as git submodule"
git push origin main
```

---

## Troubleshooting

### Issue: "remote origin already exists"
```powershell
# Remove old remote first
git remote remove origin
# Then add new one
git remote add origin https://github.com/dje115/infometrix.git
```

### Issue: "Authentication failed"
```powershell
# Use GitHub Personal Access Token instead of password
# Or configure SSH:
git remote set-url origin git@github.com:dje115/infometrix.git
```

### Issue: "Large file push fails"
```powershell
# Check for large files
git ls-files | ForEach-Object { Get-Item $_ } | Where-Object { $_.Length -gt 100MB }

# If needed, use Git LFS for large files
git lfs install
git lfs track "*.largefile"
```

### Issue: "Submodule not found"
```powershell
# Initialize submodules
git submodule update --init --recursive

# Or clone with submodules
git clone --recursive https://github.com/dje115/infometrix.git
```

---

## Verification Checklist

After migration, verify:

- [ ] Repository exists at https://github.com/dje115/infometrix
- [ ] All branches pushed (check GitHub UI)
- [ ] All tags pushed (check GitHub UI)
- [ ] Local clone works: `git clone https://github.com/dje115/infometrix.git`
- [ ] Commit history preserved (if using Option A)
- [ ] All files present in new repo
- [ ] Remote configured correctly: `git remote -v`

---

## Next Steps

After successful migration:

1. Update local working directory to use new repo
2. Run rebranding scripts (see MIGRATION_PLAN.md)
3. Set up module scaffolding
4. Test build and deployment

---

**Last Updated:** 2025-01-XX

