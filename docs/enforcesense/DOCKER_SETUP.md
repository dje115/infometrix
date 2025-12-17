# Docker Setup Guide

This document describes the Docker configuration for EnforceSense's multi-API architecture.

## Architecture Overview

EnforceSense uses a multi-API architecture with separate containers for each API surface:

- **api-platform**: Platform/tenant management API (port 6310)
- **api-admin**: Admin API for tenant operations (port 6311)
- **api-client**: Client portal API (port 4312)
- **api-debtor**: Debtor self-service API (port 4313)
- **api-agent**: Agent/mobile API (port 4314)

## Port Mappings

### Infrastructure Services

| Service | Host Port | Container Port |
|---------|-----------|----------------|
| Postgres | 6543 | 5432 |
| Redis | 6380 | 6379 |
| MinIO API | 49000 | 9000 |
| MinIO Console | 49001 | 9001 |
| MailHog SMTP | 41025 | 1025 |
| MailHog UI | 48025 | 8025 |

### API Services

| API Service | Host Port | Container Port |
|-------------|-----------|----------------|
| api-platform | 4310 | 3000 |
| api-admin | 4311 | 3000 |
| api-client | 4312 | 3000 |
| api-debtor | 4313 | 3000 |
| api-agent | 4314 | 3000 |

### Frontend Services

| Frontend | Host Port | Container Port |
|----------|-----------|----------------|
| web-platform | 4300 | 4173 |
| web-admin | 4301 | 4173 |
| web-client | 4302 | 4173 |
| web-debtor | 4303 | 4173 |

## Environment Variables

### Required Environment Variables

Create a `.env` file in the root directory with the following variables:

```bash
# Node Environment
NODE_ENV=development
PORT=3000

# Database Configuration
# For Docker containers (from within Docker network):
DATABASE_URL=postgresql://enforcesense:enforcesense_password@postgres:5432/enforcesense_db?schema=public

# For host machine access:
# DATABASE_URL=postgresql://enforcesense:enforcesense_password@localhost:4543/enforcesense_db?schema=public

# PostgreSQL Individual Settings (optional if DATABASE_URL is set)
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=enforcesense
POSTGRES_PASSWORD=enforcesense_password
POSTGRES_DB=enforcesense_db

# JWT Configuration
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=24h
JWT_REFRESH_SECRET=your-super-secret-refresh-key-change-this-in-production
JWT_REFRESH_EXPIRES_IN=7d

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO Configuration
MINIO_ENDPOINT=http://minio:9000
MINIO_ACCESS_KEY=enforcesense
MINIO_SECRET_KEY=enforcesense_minio_password
MINIO_BUCKET=enforcesense
MINIO_USE_SSL=false

# Encryption Key (REQUIRED)
# Generate with: openssl rand -base64 32
ENCRYPTION_KEY=your-encryption-key-change-this-in-production
```

## Frontend API Configuration

Each frontend app is configured to connect to its corresponding API:

- **web-platform** → `http://api-platform:3000` (VITE_API_BASE_URL)
- **web-admin** → `http://api-admin:3000` (VITE_API_BASE_URL)
- **web-client** → `http://api-client:3000` (VITE_API_BASE_URL)
- **web-debtor** → `http://api-debtor:3000` (VITE_API_BASE_URL)

These are set as environment variables in `docker-compose.yml` and are available at build time for Vite.

## Docker Compose Commands

**Important**: All commands use the project name `enforcesense` to ensure containers are properly grouped.

### Start all services

```bash
docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d
```

Or use the npm script:
```bash
pnpm docker:up
```

### Stop all services

```bash
docker-compose -f infra/docker/docker-compose.yml -p enforcesense down
```

Or use the npm script:
```bash
pnpm docker:down
```

### View logs

```bash
# All services
docker-compose -f infra/docker/docker-compose.yml -p enforcesense logs -f

# Specific service
docker-compose -f infra/docker/docker-compose.yml -p enforcesense logs -f api-admin
```

Or use the npm script:
```bash
pnpm docker:logs
```

### Rebuild services

```bash
# Rebuild all services
docker-compose -f infra/docker/docker-compose.yml -p enforcesense build

# Rebuild specific service
docker-compose -f infra/docker/docker-compose.yml -p enforcesense build api-admin

# Rebuild without cache (for clean builds)
docker-compose -f infra/docker/docker-compose.yml -p enforcesense build --no-cache api-admin
```

### Check service status

```bash
# List all EnforceSense containers
docker ps --filter "name=enforcesense" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
```

## Dockerfile Structure

Each API app has its own Dockerfile located at:
- `apps/api-platform/Dockerfile`
- `apps/api-admin/Dockerfile`
- `apps/api-client/Dockerfile`
- `apps/api-debtor/Dockerfile`
- `apps/api-agent/Dockerfile`

Each frontend app also has its own Dockerfile:
- `apps/web-platform/Dockerfile`
- `apps/web-admin/Dockerfile`
- `apps/web-client/Dockerfile`
- `apps/web-debtor/Dockerfile`

All Dockerfiles follow a multi-stage build pattern:
1. **Builder stage**: 
   - Installs dependencies using pnpm workspace filters
   - Builds the application using `nest build`
   - Output is in `dist/apps/{api-name}/src/main.js`
2. **Runner stage**: 
   - Copies workspace files (package.json, pnpm-lock.yaml, pnpm-workspace.yaml)
   - Copies packages and built dist files
   - Installs production dependencies using `pnpm install --prod --frozen-lockfile --filter "{api-name}..."`
   - This ensures pnpm symlinks are properly created for module resolution
   - Sets NODE_PATH=/app/node_modules for proper module resolution

## Notes

- All services run on the `enforcesense-net` bridge network
- Database and Redis volumes persist data between container restarts
- MinIO data is stored in a named volume
- Project name is set to `enforcesense` in docker-compose.yml (replaces deprecated `version` field)
- All API containers use Node.js 22-alpine (latest LTS)
- Production dependencies are installed in the runner stage to ensure proper pnpm workspace symlink resolution

## Troubleshooting

### API containers restarting

If API containers are restarting, check the logs:
```bash
docker logs enforcesense-api-platform --tail 50
```

Common issues:
- **Module not found**: Ensure production dependencies are installed in runner stage
- **Port conflicts**: Check if ports 4310-4314 are already in use
- **Database connection**: Verify PostgreSQL is running and accessible

### Rebuilding after dependency changes

After updating `package.json` files:
1. Update `pnpm-lock.yaml`: `pnpm install`
2. Rebuild containers: `docker-compose -f infra/docker/docker-compose.yml -p enforcesense build --no-cache`
3. Restart services: `docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d`

