# Version Update to 3.7.0 - December 2024

## Summary
Updated application version from 3.6.0 to 3.7.0 to reflect all dependency updates and improvements.

## Version Updates Applied

### Frontend
- **package.json**: `3.6.0` → `3.7.0`

### Backend
- **Dockerfile**: `APP_VERSION=3.6.0` → `APP_VERSION=3.7.0`
- **config.py**: Already set to `3.7.0`
- **version.py**: Fallback updated to `3.7.0`

### Docker Compose
- **docker-compose.yml**: `APP_VERSION:-3.6.0` → `APP_VERSION:-3.7.0`

### Version File
- **VERSION**: Updated to `3.7.0` (single source of truth)

## What's New in 3.7.0

### Dependency Updates
- ✅ ESLint 8.x → 9.18.0 (migrated to flat config)
- ✅ React 19.2.0 → 19.2.3
- ✅ All npm packages updated to latest stable versions
- ✅ Material-UI 7.3.4 → 7.3.6
- ✅ Axios 1.7.7 → 1.13.2
- ✅ Chart.js 4.4.0 → 4.5.1
- ✅ All Python packages verified/updated to latest stable

### Docker Improvements
- ✅ Added pip timeout/retry configuration (300s timeout, 5 retries)
- ✅ Improved build reliability

### Performance Fixes
- ✅ Database query optimizations (N+1 fixes)
- ✅ Parallel query execution
- ✅ Database indexes added (32+ indexes)
- ✅ Dashboard performance improvements

## Build Instructions

```bash
# Rebuild all containers with latest code
docker-compose build --no-cache --pull backend enforcement-api frontend

# Start the stack
docker-compose up -d

# Verify version
curl http://localhost:8000/api/v1/version
```

## Version Priority (Backend)

The backend version is determined in this order:
1. `APP_VERSION` environment variable (set in Docker)
2. `VERSION` file in project root
3. `settings.VERSION` from config.py (fallback)

All are now set to `3.7.0`.


