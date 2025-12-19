# 🚀 START HERE - Infometrix Platform

**For AI Agents, Developers, and Workspaces**

---

## 📋 Quick Navigation

### For AI Agents
1. **Read this file first** (you are here)
2. **Then read:** [`README_AGENTS.md`](README_AGENTS.md) - Quick start for AI agents
3. **Architecture:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - Current implementation
4. **Target:** [`docs/ARCHITECTURE_TARGET.md`](docs/ARCHITECTURE_TARGET.md) - Target two-API architecture
5. **Migration:** [`docs/MIGRATION_TO_TWO_API.md`](docs/MIGRATION_TO_TWO_API.md) - Migration plan

### For Developers
1. **Docker Setup:** [`docs/DOCKER_BUILD.md`](docs/DOCKER_BUILD.md) - Complete Docker build instructions
2. **Development:** [`DEVELOPMENT_ENVIRONMENT.md`](DEVELOPMENT_ENVIRONMENT.md) - Development workflow
3. **Architecture:** [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - System architecture

### For Migration Work
1. **Plan File:** `C:\Users\david\.cursor\plans\two-api_architecture_migration_3ccc8ea3.plan.md` - Source of truth
2. **Status:** [`docs/PLAN_FILE_STATUS.md`](docs/PLAN_FILE_STATUS.md) - Current migration status
3. **Migration Plan:** [`docs/MIGRATION_TO_TWO_API.md`](docs/MIGRATION_TO_TWO_API.md) - Detailed steps

---

## 🎯 Current Status

**Version:** 3.6.0  
**Architecture:** Monolithic Modular (migrating to Two-API)  
**Status:** ✅ Running, ⏳ Migration in progress

### What's Running
- ✅ Main Backend API (port 8000)
- ✅ Main Frontend (port 3000)
- ✅ Admin Portal (port 3010)
- ⏳ Enforcement API (port 8001) - **In Progress**
- ⏳ Debtor Portal (port 3012) - **In Progress**

---

## 🏗️ Architecture Overview

### Current (Monolithic Modular)
- Single backend API with modules
- Single frontend with module routes
- All modules integrated into main services

### Target (Two-API Architecture)
- **Platform API** (port 8000) - Core platform + CRM + Helpdesk + Quoting
- **Enforcement API** (port 8001) - EnforceSense module
- **External Portals:**
  - Client Portal (port 3011) - Optional
  - Debtor Portal (port 3012) - Multilingual, required

**See:** [`docs/ARCHITECTURE_TARGET.md`](docs/ARCHITECTURE_TARGET.md) for full details

---

## 🐳 Docker Quick Start

```powershell
# Build and start all services
docker-compose up --build -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

**Full instructions:** [`docs/DOCKER_BUILD.md`](docs/DOCKER_BUILD.md)

---

## 📚 Essential Documentation

### Architecture
- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) - Current implementation
- [`docs/ARCHITECTURE_TARGET.md`](docs/ARCHITECTURE_TARGET.md) - Target design
- [`docs/PLAN_FILE_STATUS.md`](docs/PLAN_FILE_STATUS.md) - Migration status

### Development
- [`docs/DOCKER_BUILD.md`](docs/DOCKER_BUILD.md) - Docker setup
- [`DEVELOPMENT_ENVIRONMENT.md`](DEVELOPMENT_ENVIRONMENT.md) - Dev workflow
- [`README_AGENTS.md`](README_AGENTS.md) - AI agent guide

### Migration
- [`docs/MIGRATION_TO_TWO_API.md`](docs/MIGRATION_TO_TWO_API.md) - Migration plan
- Plan file: `C:\Users\david\.cursor\plans\two-api_architecture_migration_3ccc8ea3.plan.md`

---

## 🔑 Key Facts

- **Database:** `ccs_quote_tool` (PostgreSQL)
- **Default Login:** `admin@ccs.com` / `admin123`
- **Ports:**
  - Backend: 8000
  - Frontend: 3000
  - Admin Portal: 3010
  - Enforcement API: 8001 (target)
  - Debtor Portal: 3012 (target)

---

## ⚠️ Important Notes

1. **Follow the plan file** for migration work: `C:\Users\david\.cursor\plans\two-api_architecture_migration_3ccc8ea3.plan.md`
2. **Keep app runnable** after each commit
3. **Update documentation** as you make changes
4. **Verify each step** before marking complete

---

**Last Updated:** 2025-12-19  
**Version:** 3.6.0

