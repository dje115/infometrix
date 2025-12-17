# EnforceSense Setup Guide

This guide provides step-by-step instructions to set up and run the EnforceSense platform from scratch.

## Prerequisites

- **Node.js**: >= 20.0.0 (LTS recommended: 22.x)
- **pnpm**: >= 8.0.0
- **Docker**: Latest version with Docker Compose support
- **Git**: For cloning the repository

## Initial Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd EnforceSense
```

### 2. Install Dependencies

```bash
# Install pnpm if not already installed
npm install -g pnpm

# Install all workspace dependencies
pnpm install
```

### 3. Environment Configuration

Create a `.env` file in the root directory. See [ENV_EXAMPLE_CONTENT.md](ENV_EXAMPLE_CONTENT.md) for complete environment variable documentation.

**Minimum required variables:**

```bash
# Database (for Docker containers)
DATABASE_URL=postgresql://enforcesense:enforcesense_password@postgres:5432/enforcesense_db?schema=public

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# JWT
JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
JWT_EXPIRES_IN=24h
JWT_REFRESH_SECRET=your-super-secret-refresh-key-change-this-in-production
JWT_REFRESH_EXPIRES_IN=7d

# Encryption
ENCRYPTION_KEY=your-encryption-key-change-this-in-production
```

**Generate encryption key:**
```bash
openssl rand -base64 32
```

### 4. Database Setup

The database will be automatically created when you start the Docker containers. To run migrations manually:

```bash
# From the root directory
cd apps/api
pnpm prisma:generate
pnpm prisma:migrate
```

## Starting the Platform

### Using Docker Compose (Recommended)

```bash
# Start all services
pnpm docker:up

# Or manually:
docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d
```

This will start:
- **Infrastructure**: PostgreSQL, Redis, MinIO, MailHog
- **API Services**: api-platform, api-admin, api-client, api-debtor, api-agent
- **Frontend Apps**: web-admin, web-client, web-debtor

### Verify Services are Running

```bash
# Check all containers
docker ps --filter "name=enforcesense" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Check specific API logs
docker logs enforcesense-api-platform --tail 20
```

Expected output should show all containers with status "Up" and APIs showing "Nest application successfully started".

## Accessing the Platform

Once all services are running, access the applications at:

- **Admin Portal**: http://localhost:4301
- **Client Portal**: http://localhost:4302
- **Debtor Portal**: http://localhost:4303
- **API Platform**: http://localhost:4310
- **API Admin**: http://localhost:4311
- **API Client**: http://localhost:4312
- **API Debtor**: http://localhost:4313
- **API Agent**: http://localhost:4314
- **MailHog UI**: http://localhost:48025
- **MinIO Console**: http://localhost:49001
  - Username: `enforcesense`
  - Password: `enforcesense_minio_password`

## Development Workflow

### Rebuilding After Changes

```bash
# Rebuild specific service
docker-compose -f infra/docker/docker-compose.yml -p enforcesense build api-admin

# Rebuild all services
docker-compose -f infra/docker/docker-compose.yml -p enforcesense build

# Rebuild without cache (clean build)
docker-compose -f infra/docker/docker-compose.yml -p enforcesense build --no-cache
```

### Viewing Logs

```bash
# All services
pnpm docker:logs

# Specific service
docker logs enforcesense-api-admin -f
docker logs enforcesense-web-admin -f
```

### Stopping Services

```bash
# Stop all services
pnpm docker:down

# Stop specific service
docker-compose -f infra/docker/docker-compose.yml -p enforcesense stop api-admin
```

## Local Development (Without Docker)

If you prefer to run services locally:

1. **Start Infrastructure Services** (PostgreSQL, Redis, MinIO, MailHog):
   ```bash
   docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d postgres redis minio mailhog
   ```

2. **Update .env** for local access:
   ```bash
   DATABASE_URL=postgresql://enforcesense:enforcesense_password@localhost:4543/enforcesense_db?schema=public
   REDIS_HOST=localhost
   REDIS_PORT=46379
   ```

3. **Run API Services**:
   ```bash
   cd apps/api-platform && pnpm start:dev
   cd apps/api-admin && pnpm start:dev
   # ... etc
   ```

4. **Run Frontend Apps**:
   ```bash
   cd apps/web-admin && pnpm dev
   cd apps/web-client && pnpm dev
   # ... etc
   ```

## Troubleshooting

### API Containers Keep Restarting

1. Check logs:
   ```bash
   docker logs enforcesense-api-platform --tail 50
   ```

2. Common issues:
   - **Module not found**: Rebuild containers with `--no-cache`
   - **Database connection**: Ensure PostgreSQL is running
   - **Port conflicts**: Check if ports 4310-4314 are in use

### Database Connection Issues

1. Verify PostgreSQL is running:
   ```bash
   docker ps | grep postgres
   ```

2. Test connection:
   ```bash
   psql -h localhost -p 4543 -U enforcesense -d enforcesense_db
   ```

3. Check environment variables in `.env` file

### Frontend Can't Connect to API

1. Verify API containers are running
2. Check `VITE_API_BASE_URL` environment variable in docker-compose.yml
3. Check browser console for CORS errors
4. Verify network connectivity: `docker network inspect enforcesense_enforcesense-net`

## Production Deployment

For production deployment, see [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for:
- Cloud deployment strategies
- Security hardening
- Scaling considerations
- Network topology

## Additional Resources

- [Implementation Plan](IMPLEMENTATION_PLAN.md) - Architecture and development guidelines
- [Development Services & Ports](DEV_SERVICES.md) - Complete service documentation
- [Docker Setup Guide](DOCKER_SETUP.md) - Detailed Docker configuration
- [Environment Variables](ENV_EXAMPLE_CONTENT.md) - Environment variable reference

## Support

For issues or questions:
1. Check the logs: `docker logs <container-name>`
2. Review the documentation in `/docs`
3. Verify all prerequisites are met
4. Ensure environment variables are correctly set


