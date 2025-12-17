# 🐳 Infometrix Services Status

**Last Updated:** 2025-12-17

---

## ✅ **All Services Running**

### **Core Services:**
- ✅ **PostgreSQL** - Database (port 5432)
- ✅ **Redis** - Cache & Session Store (port 6379)
- ✅ **Backend API** - FastAPI backend (port 8000)
- ✅ **Frontend** - React CRM interface (port 3000)
- ✅ **Admin Portal** - Vue.js admin interface (port 3010)

### **Background Services:**
- ✅ **Celery Worker** - Background task processing
- ✅ **Celery Beat** - Scheduled tasks
- ✅ **MailHog** - Email testing (SMTP: 1026, Web UI: 3006)
- ✅ **MinIO** - Object storage (API: 9002, Console: 9092)

---

## 🌐 **Access Points**

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend (CRM) | http://localhost:3000 | Main CRM interface |
| Admin Portal | http://localhost:3010 | Tenant administration |
| Backend API | http://localhost:8000 | REST API |
| API Docs | http://localhost:8000/docs | Swagger documentation |
| MailHog UI | http://localhost:3006 | Email testing interface |
| MinIO Console | http://localhost:9092 | Object storage management |

---

## 🔑 **Default Credentials**

- **Email:** `admin@ccs.com`
- **Password:** `admin123`

---

## 📊 **Service Details**

### **Backend API (FastAPI)**
- **Port:** 8000
- **Framework:** FastAPI
- **Features:** REST API, WebSocket support, Multi-tenant
- **Docs:** http://localhost:8000/docs

### **Frontend (React)**
- **Port:** 3000
- **Framework:** React + Vite
- **Features:** Hot-reload, Material-UI, Module-based navigation
- **Status:** ✅ Running

### **Admin Portal (Vue.js)**
- **Port:** 3010
- **Framework:** Vue 3 + Vite
- **Features:** Tenant management, User administration
- **Status:** ✅ Running

### **Celery Worker**
- **Purpose:** Background task processing
- **Tasks:** AI analysis, Lead generation, Email sending
- **Status:** ✅ Running

### **Celery Beat**
- **Purpose:** Scheduled tasks
- **Tasks:** SLA compliance reports, Scheduled campaigns
- **Status:** ✅ Running

### **MailHog**
- **SMTP Port:** 1026
- **Web UI Port:** 3006
- **Purpose:** Email testing (captures all emails)
- **Status:** ✅ Running

### **MinIO**
- **API Port:** 9002
- **Console Port:** 9092
- **Purpose:** Object storage (S3-compatible)
- **Credentials:** minioadmin / minioadmin123
- **Status:** ✅ Running

---

## 🚀 **Starting All Services**

```powershell
cd "C:\Users\david\Documents\Infometrix"
docker-compose up -d
```

This starts:
- PostgreSQL
- Redis
- Backend API
- Frontend
- Admin Portal
- Celery Worker
- Celery Beat
- MailHog
- MinIO

---

## 📋 **Service Comparison: CCS vs Infometrix**

| Service | CCS | Infometrix | Status |
|---------|-----|------------|--------|
| PostgreSQL | ✅ | ✅ | ✅ Migrated |
| Redis | ✅ | ✅ | ✅ Migrated |
| Backend API | ✅ | ✅ | ✅ Migrated |
| Frontend | ✅ | ✅ | ✅ Migrated |
| Admin Portal | ✅ | ✅ | ✅ Migrated |
| Celery Worker | ✅ | ✅ | ✅ Migrated |
| Celery Beat | ✅ | ✅ | ✅ Migrated |
| MailHog | ✅ | ✅ | ✅ Migrated |
| MinIO | ✅ | ✅ | ✅ Migrated |

**All services from CCS have been migrated to Infometrix!**

---

## 🔍 **Checking Service Status**

```powershell
# Check all services
docker-compose ps

# Check specific service logs
docker-compose logs frontend
docker-compose logs backend
docker-compose logs celery-worker

# Check service health
docker-compose ps | Select-String "healthy|Up"
```

---

## ⚠️ **Troubleshooting**

### **If a service won't start:**
1. Check logs: `docker-compose logs <service-name>`
2. Rebuild: `docker-compose build <service-name>`
3. Restart: `docker-compose restart <service-name>`

### **If frontend/admin won't build:**
- Check `package.json` dependencies
- Verify `Dockerfile.dev` uses `--legacy-peer-deps`
- Check for missing files

### **If backend won't start:**
- Verify database is running
- Check environment variables
- Review backend logs

---

**Last Updated:** 2025-12-17  
**All Services:** ✅ Running


