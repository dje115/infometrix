# Docker Build Instructions - Infometrix Platform

**Version:** 3.6.0  
**Last Updated:** 2025-12-19

---

## 🎯 Overview

This guide provides complete instructions for building and running the Infometrix platform using Docker Compose.

---

## 📋 Prerequisites

### Required Software
- **Docker Desktop** (Windows) or **Docker Engine** (Linux/Mac)
- **Docker Compose** (v2.0+)
- **Git** (for cloning repository)

### System Requirements
- **RAM:** Minimum 8GB (16GB recommended)
- **Disk Space:** Minimum 10GB free
- **CPU:** 2+ cores recommended

### Verify Installation

```powershell
# Check Docker version
docker --version

# Check Docker Compose version
docker-compose --version

# Verify Docker is running
docker ps
```

---

## 🚀 Quick Start

### 1. Clone Repository

```powershell
git clone https://github.com/dje115/infometrix.git
cd infometrix
```

### 2. Environment Setup

Create `.env` file in project root (optional - defaults work for development):

```env
# Database
POSTGRES_DB=ccs_quote_tool
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres_password_2025

# API Keys (optional for development)
OPENAI_API_KEY=your_key_here
COMPANIES_HOUSE_API_KEY=your_key_here
GOOGLE_MAPS_API_KEY=your_key_here

# Application Version
APP_VERSION=3.6.0
```

### 3. Build and Start Services

```powershell
# Build all images and start containers
docker-compose up --build -d

# View logs (all services)
docker-compose logs -f

# View logs for specific service
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f admin-portal
```

### 4. Verify Services

```powershell
# Check container status
docker-compose ps

# Test backend health
curl http://localhost:8000/health

# Test frontend
curl http://localhost:3000

# Test admin portal
curl http://localhost:3010
```

---

## 🏗️ Service Details

### Core Services

| Service | Container Name | Port | Purpose |
|---------|---------------|------|---------|
| Backend | `infometrix-backend` | 8000 | FastAPI backend API |
| Frontend | `infometrix-frontend` | 3000 | React frontend |
| Admin Portal | `infometrix-admin-portal` | 3010 | Vue.js admin portal |
| PostgreSQL | `infometrix-postgres` | 5432 | Database |
| Redis | `infometrix-redis` | 6379 | Cache & sessions |

### Background Services

| Service | Container Name | Purpose |
|---------|---------------|---------|
| Celery Worker | `infometrix-celery-worker` | Background tasks |
| Celery Beat | `infometrix-celery-beat` | Scheduled tasks |

### Infrastructure Services

| Service | Container Name | Ports | Purpose |
|---------|---------------|-------|---------|
| MinIO | `infometrix-minio` | 9002/9092 | Object storage |
| MailHog | `infometrix-mailhog` | 1026/3006 | Email testing |

### Target Services (Migration)

| Service | Container Name | Port | Status |
|---------|---------------|------|--------|
| Enforcement API | `infometrix-enforcement-api` | 8001 | ⏳ In Progress |
| Debtor Portal | `infometrix-debtor-portal` | 3012 | ⏳ In Progress |

---

## 🔧 Build Commands

### Full Rebuild

```powershell
# Stop and remove all containers
docker-compose down

# Remove volumes (WARNING: deletes data)
docker-compose down -v

# Rebuild all images from scratch
docker-compose build --no-cache

# Start services
docker-compose up -d
```

### Rebuild Specific Service

```powershell
# Rebuild backend only
docker-compose build --no-cache backend
docker-compose up -d backend

# Rebuild frontend only
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Development Mode (Hot Reload)

```powershell
# Start with volume mounts for hot reload
docker-compose up -d

# View logs in real-time
docker-compose logs -f backend frontend
```

**Note:** Development mode uses volume mounts (`./backend:/app`, `./frontend:/app`) for hot reload.

---

## 🗄️ Database Management

### Access Database

```powershell
# Connect to PostgreSQL
docker-compose exec postgres psql -U postgres -d ccs_quote_tool

# Or use external tool
# Host: localhost
# Port: 5432
# Database: ccs_quote_tool
# User: postgres
# Password: postgres_password_2025
```

### Run Migrations

```powershell
# Run migrations (if using Alembic)
docker-compose exec backend alembic upgrade head

# Or run SQL migrations manually
docker-compose exec postgres psql -U postgres -d ccs_quote_tool -f /path/to/migration.sql
```

### Backup Database

```powershell
# Create backup
docker-compose exec postgres pg_dump -U postgres ccs_quote_tool > backup.sql

# Restore backup
docker-compose exec -T postgres psql -U postgres ccs_quote_tool < backup.sql
```

---

## 🔍 Troubleshooting

### Services Won't Start

```powershell
# Check logs for errors
docker-compose logs backend
docker-compose logs frontend

# Check container status
docker-compose ps

# Restart specific service
docker-compose restart backend
```

### Port Conflicts

If ports are already in use:

```powershell
# Find process using port (Windows)
netstat -ano | findstr :8000

# Kill process (replace PID)
taskkill /PID <PID> /F

# Or change port in docker-compose.yml
```

### Database Connection Issues

```powershell
# Check PostgreSQL is healthy
docker-compose ps postgres

# Check PostgreSQL logs
docker-compose logs postgres

# Restart PostgreSQL
docker-compose restart postgres
```

### Clear Everything and Start Fresh

```powershell
# Stop all containers
docker-compose down

# Remove all containers, networks, volumes
docker-compose down -v

# Remove all images
docker-compose rm -f

# Rebuild from scratch
docker-compose build --no-cache
docker-compose up -d
```

### View Resource Usage

```powershell
# Container stats
docker stats

# Disk usage
docker system df

# Clean up unused resources
docker system prune -a
```

---

## 📦 Image Building

### Build Arguments

Images accept build arguments:

```yaml
build:
  args:
    APP_VERSION: ${APP_VERSION:-3.6.0}
    BUILD_DATE: ${BUILD_DATE:-}
    BUILD_HASH: ${BUILD_HASH:-}
```

### Custom Build

```powershell
# Build with custom version
docker-compose build --build-arg APP_VERSION=3.6.1 backend

# Build with build date
docker-compose build --build-arg BUILD_DATE=$(Get-Date -Format "yyyy-MM-dd") backend
```

---

## 🌐 Access URLs

After starting services:

| Service | URL | Notes |
|---------|-----|-------|
| Frontend | http://localhost:3000 | Main CRM interface |
| Admin Portal | http://localhost:3010 | System administration |
| Backend API | http://localhost:8000 | API server |
| API Docs | http://localhost:8000/docs | Swagger UI |
| ReDoc | http://localhost:8000/redoc | ReDoc documentation |
| MailHog UI | http://localhost:3006 | Email viewer |
| MinIO Console | http://localhost:9092 | Object storage UI |

**Default Login:**
- Email: `admin@ccs.com`
- Password: `admin123`

---

## 🔐 Security Notes

### Development Environment
- Default passwords are used (change in production)
- No SSL/TLS (use HTTPS in production)
- Debug mode enabled (disable in production)

### Production Deployment
- Use environment variables for secrets
- Enable SSL/TLS
- Use strong passwords
- Disable debug mode
- Configure firewall rules
- Use secrets management

---

## 📝 Environment Variables

### Backend Environment Variables

```env
DATABASE_URL=postgresql://postgres:postgres_password_2025@postgres:5432/ccs_quote_tool
REDIS_URL=redis://redis:6379/0
SECRET_KEY=ccs_super_secret_key_2025_change_in_production
DEFAULT_TENANT=ccs
SUPER_ADMIN_EMAIL=admin@ccs.com
SUPER_ADMIN_PASSWORD=admin123
OPENAI_API_KEY=
COMPANIES_HOUSE_API_KEY=
GOOGLE_MAPS_API_KEY=
MINIO_ENDPOINT=minio:9000
MINIO_ACCESS_KEY=minioadmin
MINIO_SECRET_KEY=minioadmin123
```

### Frontend Environment Variables

```env
REACT_APP_API_URL=http://localhost:8000
CHOKIDAR_USEPOLLING=true
WATCHPACK_POLLING=true
```

### Admin Portal Environment Variables

```env
VITE_API_URL=http://localhost:8000
```

---

## 🚀 Production Build

For production, use production compose file:

```powershell
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d
```

**Note:** Production build uses optimized images without development tools.

---

## 📚 Additional Resources

- **Development Guide:** [`DEVELOPMENT_ENVIRONMENT.md`](../DEVELOPMENT_ENVIRONMENT.md)
- **Architecture:** [`docs/ARCHITECTURE.md`](ARCHITECTURE.md)
- **Migration Plan:** [`docs/MIGRATION_TO_TWO_API.md`](MIGRATION_TO_TWO_API.md)

---

## ✅ Verification Checklist

After building, verify:

- [ ] All containers are running (`docker-compose ps`)
- [ ] Backend API responds (`curl http://localhost:8000/health`)
- [ ] Frontend loads (`http://localhost:3000`)
- [ ] Admin portal loads (`http://localhost:3010`)
- [ ] Database is accessible
- [ ] Can log in with default credentials
- [ ] No errors in logs (`docker-compose logs`)

---

**Last Updated:** 2025-12-19  
**Version:** 3.6.0



