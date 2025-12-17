# 📚 CCS Quote Tool v2 - Reference Guide

**Purpose:** This document helps you find information in the old CCS project when working on Infometrix.

**⚠️ IMPORTANT:** The CCS folder is for **reference only**. Do not modify it. All active development is in Infometrix.

---

## 📁 **Location**

**Old CCS Project:** `C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2\`  
**New Infometrix Project:** `C:\Users\david\Documents\Infometrix\`

---

## 🔍 **Finding Information**

### **If You Need to Understand a Feature:**

1. **Check Infometrix First:**
   - `docs/AGENT_HANDOVER.md` - Current status
   - `docs/ccs-archive/MASTER_SPECIFICATION.md` - Feature specs
   - `README.md` - Project overview

2. **Then Check CCS (Reference Only):**
   - `C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2\MASTER_SPECIFICATION.md`
   - `C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2\README.md`
   - `C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2\DEVELOPMENT_PLAN.md`

### **If You Need to Copy Code:**

1. **Find the file in CCS:**
   - Use file search or browse the folder structure

2. **Copy to Infometrix:**
   ```powershell
   Copy-Item "C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2\<path>" -Destination "C:\Users\david\Documents\Infometrix\<path>"
   ```

3. **Update References:**
   - Change "CCS" to "Infometrix"
   - Update imports/paths if needed
   - Test thoroughly

---

## 📋 **Key Files in CCS (Reference)**

### **Documentation:**
- `MASTER_SPECIFICATION.md` - Complete feature specification
- `DEVELOPMENT_PLAN.md` - 6-month strategic plan
- `HANDOVER_DOCUMENT.md` - Previous handover
- `README.md` - Project overview

### **Configuration:**
- `env.example` - Environment variables (already copied)
- `docker-compose.yml` - Docker config (already copied and updated)
- `api-keys.env` - API keys template (already copied)

### **Code (Reference Only):**
- `backend/` - Backend code (reference implementation)
- `frontend/` - Frontend code (reference implementation)
- `admin-portal/` - Admin portal code (reference implementation)

---

## ⚠️ **Rules for Using CCS Reference**

### **✅ DO:**
- Read and understand code from CCS
- Copy patterns and implementations
- Reference documentation
- Learn from architecture decisions

### **❌ DON'T:**
- Modify files in CCS folder
- Commit changes to CCS
- Import code directly from CCS
- Use CCS as active workspace

---

## 🔄 **Migration Status**

### **Already Migrated:**
- ✅ All code files
- ✅ Configuration files
- ✅ Documentation (in `docs/ccs-archive/`)
- ✅ Docker setup
- ✅ Database migrations

### **May Need Reference:**
- 🔍 Specific feature implementations
- 🔍 Business logic patterns
- 🔍 API endpoint examples
- 🔍 Frontend component patterns

---

## 📖 **Quick Reference Table**

| What You Need | Where in CCS | Where in Infometrix |
|--------------|--------------|---------------------|
| Feature Spec | `MASTER_SPECIFICATION.md` | `docs/ccs-archive/MASTER_SPECIFICATION.md` |
| Development Plan | `DEVELOPMENT_PLAN.md` | `docs/ccs-archive/DEVELOPMENT_PLAN.md` |
| Backend Code | `backend/app/` | `backend/app/` (updated) |
| Frontend Code | `frontend/src/` | `frontend/src/` (updated) |
| Admin Code | `admin-portal/src/` | `admin-portal/src/` (updated) |
| Docker Config | `docker-compose.yml` | `docker-compose.yml` (rebranded) |
| Environment | `env.example` | `env.example` (updated) |

---

## 🆘 **If You Can't Find Something**

1. **Search in Infometrix first:**
   - Use codebase search
   - Check `docs/` folder
   - Check module system

2. **Then search in CCS:**
   - Browse `C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2\`
   - Use file search
   - Check documentation files

3. **Document what you found:**
   - Update `docs/MIGRATION_CHECKLIST.md` if you copy something
   - Note where it came from
   - Update references

---

**Last Updated:** 2025-12-17  
**Purpose:** Reference guide for accessing old CCS project


