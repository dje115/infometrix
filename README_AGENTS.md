# 🤖 Quick Start for AI Agents

**Welcome to Infometrix!** This is the main workspace you should use.

---

## ✅ **Current Status (2025-12-17)**

- ✅ **All services running** (Frontend, Admin, Backend, Celery, MailHog, MinIO)
- ✅ **Database initialized** with 2 tenants and 34 AI prompts
- ✅ **Ready for development**

---

## 📍 **Workspace Location**

**USE THIS WORKSPACE:**
```
C:\Users\david\Documents\Infometrix\
```

**OLD WORKSPACE (Reference Only):**
```
C:\Users\david\Documents\CCS quote tool\CCS Quote Tool v2\
```

---

## 🚀 **Quick Start**

### **1. Open Workspace:**
```
File → Open Workspace → C:\Users\david\Documents\Infometrix\Infometrix.code-workspace
```

### **2. Services Are Already Running:**
- Frontend: http://localhost:3000
- Admin: http://localhost:3010
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs

### **3. Default Login:**
- Email: `admin@ccs.com`
- Password: `admin123`

---

## 📚 **Documentation (Read in Order)**

1. **START HERE:** [`docs/AGENT_HANDOVER.md`](docs/AGENT_HANDOVER.md) - Complete context
2. **Quick Reference:** [`AGENT_START.md`](AGENT_START.md) - Quick commands
3. **Current Status:** [`CURRENT_STATUS.md`](CURRENT_STATUS.md) - Latest status
4. **Workspace Guide:** [`WORKSPACE_HANDOVER.md`](WORKSPACE_HANDOVER.md) - Workspace details

---

## 🎯 **Key Facts**

- **Database:** `ccs_quote_tool` (name kept for compatibility)
- **Tenants:** 2 (System + Default CCS)
- **AI Prompts:** 34 system prompts seeded
- **GitHub:** https://github.com/dje115/infometrix
- **Architecture:** Monolithic modular (all modules in main backend/frontend)
- **EnforceSense:** Module within main backend/frontend (NOT separate container)
- **Debtor Portal:** Routes within main frontend (NOT separate container)

---

## 📦 **Module Locations**

### EnforceSense Module
- **Backend API:** `/api/v1/modules/enforcesense/*` (port 8000)
- **Frontend Routes:** `/enforcesense/*` (port 3000)
- **Models:** `backend/app/models/enforcesense.py`
- **Endpoints:** `backend/app/api/v1/endpoints/enforcesense.py`
- **Frontend Pages:** `frontend/src/modules/enforcesense/pages/`

### Debtor Portal
- **Backend API:** `/api/v1/debtor-portal/*` (port 8000)
- **Frontend Routes:** `/debtor-portal/*` (port 3000)
- **Endpoints:** `backend/app/api/v1/endpoints/debtor_portal.py`
- **Frontend Pages:** `frontend/src/pages/DebtorPortal*.tsx`

### ⚠️ Legacy Container
- `infometrix-enforcement-api` (port 8001) - **OLD/LEGACY** - Not part of current architecture

**See:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) for complete architecture details.

---

**Last Updated:** 2025-12-19  
**Status:** ✅ Ready  
**Version:** 3.6.0


