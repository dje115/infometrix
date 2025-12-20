# 🐳 Docker Build & Deployment Guide

Complete guide for building and running Infometrix in Docker.

---

## 📋 Prerequisites

### Required Software

1. **Docker Desktop**
   - Windows: Download from https://www.docker.com/products/docker-desktop
   - Mac: Download from https://www.docker.com/products/docker-desktop
   - Linux: Install Docker Engine and Docker Compose

2. **Git**
   - Download from https://git-scm.com/downloads

3. **PowerShell** (Windows) or **Bash** (Linux/Mac)

### System Requirements

- **RAM:** Minimum 8GB (16GB recommended)
- **Disk Space:** Minimum 20GB free
- **CPU:** 2+ cores recommended

---

## 🚀 Quick Start

### First Time Setup

```powershell
# 1. Clone repository
git clone <repository-url>
cd Infometrix

# 2. Copy environment file
Copy-Item .env.example .env

# 3. Edit .env file (add API keys if needed)
# Notepad .env

# 4. Start all services
docker-compose up -d

# 5. Wait for services to start (30-60 seconds)
# Check logs:
docker-compose logs -f

# 6. Access services:
# Frontend: http://localhost:3000
# Platform API Docs: http://localhost:8000/docs
# Enforcement API Docs: http://localhost:8001/docs
# Admin Portal: http://localhost:3010
# Debtor Portal: http://localhost:3002
```

### Default Credentials

- **Email:** `admin@infometrix.com` (or `admin@ccs.com`)
- **Password:** `admin123`

---

## 🏗️ Building Services

### Build All Services

```powershell
# Build all images (first time or after changes)
docker-compose build

# Build without cache (clean build)
docker-compose build --no-cache

# Build specific service
docker-compose build enforcement-api
docker-compose build frontend
docker-compose build backend
```

### Build Targets

Each service has multiple build targets:

**Backend:**
- `development` - Hot-reload enabled, debug mode
- `production` - Optimized build, no debug

**Frontend:**
- Development mode with hot-reload
- Production build (optimized)

**Enforcement API:**
- Development mode with hot-reload

---

## 🔄 Starting & Stopping Services

### Start Services

```powershell
# Start all services in background
docker-compose up -d

# Start specific service
docker-compose up -d enforcement-api

# Start and view logs
docker-compose up
```

### Stop Services

```powershell
# Stop all services (keeps containers and data)
docker-compose stop

# Stop and remove containers (keeps volumes/data)
docker-compose down

# Stop and remove everything including volumes (DELETES DATA)
docker-compose down -v
```

### Restart Services

```powershell
# Restart all services
docker-compose restart

# Restart specific service
docker-compose restart enforcement-api
```

---

## 📊 Service Status & Health

### Check Service Status

```powershell
# List all services and their status
docker-compose ps

# Check if specific service is running
docker-compose ps enforcement-api
```

### Health Checks

All services have health checks configured:

```powershell
# Check health of all services
docker-compose ps

# Services should show "healthy" status
```

### Service Logs

```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f enforcement-api
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres
docker-compose logs -f redis

# Last 100 lines
docker-compose logs --tail=100 enforcement-api

# Follow logs from specific time
docker-compose logs --since 10m enforcement-api
```

---

## 🗄️ Database Management

### Database Connection

```powershell
# Connect to PostgreSQL
docker exec -it infometrix-postgres psql -U postgres -d ccs_quote_tool

# Connection string:
# postgresql://postgres:postgres_password_2025@localhost:5432/ccs_quote_tool
```

### Database Migrations

Migrations are in:
- `backend/migrations/` - Platform API migrations
- `apps/enforcement-api/migrations/` - Enforcement API migrations

```powershell
# Run migrations manually (if needed)
docker exec infometrix-postgres psql -U postgres -d ccs_quote_tool -f /path/to/migration.sql

# Or connect and run:
docker exec -it infometrix-postgres psql -U postgres -d ccs_quote_tool
# Then: \i /path/to/migration.sql
```

### Database Backup

See `DATABASE_BACKUP.md` for detailed backup instructions.

```powershell
# Quick backup
docker exec infometrix-postgres pg_dump -U postgres ccs_quote_tool > backup.sql
```

### Database Restore

```powershell
# Restore from backup
Get-Content backup.sql | docker exec -i infometrix-postgres psql -U postgres -d ccs_quote_tool
```

---

## 🔧 Development Mode

### Hot Reload

All services support hot-reload in development mode:

- **Backend:** Changes in `backend/` auto-reload
- **Enforcement API:** Changes in `apps/enforcement-api/` auto-reload
- **Frontend:** Changes in `frontend/src/` auto-reload (Vite HMR)
- **Admin Portal:** Changes in `admin-portal/` auto-reload
- **Debtor Portal:** Changes in `apps/debtor-portal/` auto-reload

### Making Changes

1. **Edit code** in your IDE
2. **Save file**
3. **Service auto-reloads** (check logs to confirm)
4. **Refresh browser** (for frontend changes)

### Debugging

```powershell
# View real-time logs
docker-compose logs -f enforcement-api

# Check for errors
docker-compose logs enforcement-api | Select-String "ERROR"

# Check service health
docker-compose ps
```

---

## 🐛 Troubleshooting

### Port Already in Use

```powershell
# Check what's using the port (Windows)
netstat -ano | findstr :8000
netstat -ano | findstr :8001
netstat -ano | findstr :3000

# Find process ID (PID) from output
# Kill process:
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### Services Won't Start

```powershell
# 1. Check Docker Desktop is running
# 2. Check logs for errors
docker-compose logs

# 3. Try rebuilding
docker-compose build --no-cache
docker-compose up -d

# 4. Check disk space
docker system df

# 5. Clean up unused resources
docker system prune -a
```

### Database Connection Errors

```powershell
# 1. Check PostgreSQL is running
docker-compose ps postgres

# 2. Check PostgreSQL logs
docker-compose logs postgres

# 3. Restart PostgreSQL
docker-compose restart postgres

# 4. Check database exists
docker exec infometrix-postgres psql -U postgres -l
```

### Frontend Not Loading

```powershell
# 1. Check frontend logs
docker-compose logs frontend

# 2. Rebuild frontend
docker-compose up -d --build frontend

# 3. Clear browser cache
# 4. Check port 3000 is not in use
```

### API Errors

```powershell
# 1. Check API logs
docker-compose logs enforcement-api
docker-compose logs backend

# 2. Check API health endpoints
# http://localhost:8000/health
# http://localhost:8001/health

# 3. Check database migrations ran
docker exec infometrix-postgres psql -U postgres -d ccs_quote_tool -c "\dt"
```

### Out of Memory

```powershell
# Check Docker resource usage
docker stats

# Increase Docker Desktop memory:
# Docker Desktop > Settings > Resources > Memory
# Increase to 8GB+ if available

# Restart Docker Desktop
```

### Clean Slate (Nuclear Option)

```powershell
# WARNING: This deletes ALL data

# 1. Stop all services
docker-compose down -v

# 2. Remove all images
docker-compose down --rmi all

# 3. Clean Docker system
docker system prune -a --volumes

# 4. Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

---

## 📦 Production Build

### Building for Production

```powershell
# Use production docker-compose file
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

### Production Considerations

1. **Environment Variables:**
   - Set strong `SECRET_KEY`
   - Configure production database URL
   - Set production API keys

2. **Security:**
   - Use HTTPS in production
   - Configure CORS properly
   - Set up firewall rules
   - Use secrets management

3. **Performance:**
   - Enable Redis caching
   - Configure database connection pooling
   - Set up CDN for static assets

4. **Monitoring:**
   - Set up logging aggregation
   - Configure health checks
   - Set up alerts

---

## 🔍 Service Details

### Platform API (Backend)

- **Port:** 8000
- **Path:** `backend/` or `apps/platform-api/`
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL
- **Cache:** Redis

### Enforcement API

- **Port:** 8001
- **Path:** `apps/enforcement-api/`
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL (shared)
- **Cache:** Redis (shared)

### Frontend

- **Port:** 3000
- **Path:** `frontend/`
- **Framework:** React 18 + TypeScript
- **Build Tool:** Vite
- **UI Library:** Material-UI

### Admin Portal

- **Port:** 3010
- **Path:** `admin-portal/`
- **Framework:** Vue.js 3
- **UI Library:** Element Plus

### Debtor Portal

- **Port:** 3002
- **Path:** `apps/debtor-portal/`
- **Framework:** React 18 + TypeScript
- **i18n:** react-i18next (en/ro/cs)

### PostgreSQL

- **Port:** 5432
- **Database:** `ccs_quote_tool`
- **User:** `postgres`
- **Password:** `postgres_password_2025`
- **Volume:** `postgres_data`

### Redis

- **Port:** 6379
- **Volume:** `redis_data`

---

## 📝 Environment Variables

### Required Variables

```env
# Database
DATABASE_URL=postgresql://postgres:postgres_password_2025@postgres:5432/ccs_quote_tool

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256

# Tenant
DEFAULT_TENANT=ccs
SUPER_ADMIN_EMAIL=admin@ccs.com
SUPER_ADMIN_PASSWORD=admin123
```

### Optional Variables

```env
# AI Features
OPENAI_API_KEY=your-openai-key
COMPANIES_HOUSE_API_KEY=your-companies-house-key
GOOGLE_MAPS_API_KEY=your-google-maps-key

# MinIO (File Storage)
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
MINIO_BUCKET=ccs-quote-tool
MINIO_SECURE=false

# Enforcement API
ENFORCEMENT_API_PORT=8001
VITE_ENFORCEMENT_API_URL=http://localhost:8001
```

---

## 🔄 Updates & Maintenance

### Updating Code

```powershell
# 1. Pull latest changes
git pull origin main

# 2. Rebuild affected services
docker-compose build enforcement-api
docker-compose up -d enforcement-api
```

### Updating Dependencies

```powershell
# Backend dependencies
cd backend
pip install -r requirements.txt

# Enforcement API dependencies
cd apps/enforcement-api
pip install -r requirements.txt

# Frontend dependencies
cd frontend
npm install

# Rebuild services
docker-compose build
docker-compose up -d
```

---

## 📚 Additional Resources

- **Docker Documentation:** https://docs.docker.com/
- **Docker Compose Documentation:** https://docs.docker.com/compose/
- **FastAPI Documentation:** https://fastapi.tiangolo.com/
- **React Documentation:** https://react.dev/
- **Material-UI Documentation:** https://mui.com/

---

**Last Updated:** 2025-12-19  
**Maintained By:** Development Team

