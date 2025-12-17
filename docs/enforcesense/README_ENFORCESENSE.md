# EnforceSense

EnforceSense is a comprehensive debt enforcement management platform built as a monorepo with multiple applications and shared packages.

> 🤖 **For AI Agents**: **[START HERE →](docs/AGENTS_START_HERE.md)** - Read this first before working on the project!

## Architecture

EnforceSense uses a **multi-API architecture** where each user-facing application has its own dedicated API service:

- **Platform Portal** → `api-platform` (port 4310) - Platform/tenant management
- **Admin Portal** → `api-admin` (port 4311) - Tenant internal operations
- **Client Portal** → `api-client` (port 4312) - Client-facing operations
- **Debtor Portal** → `api-debtor` (port 4313) - Debtor self-service
- **Agent/Mobile App** → `api-agent` (port 4314) - Field agent operations

This architecture provides:
- **Security isolation**: Different security policies per API
- **Independent scaling**: Scale each API based on demand
- **Cloud portability**: Deploy each API as separate services

For detailed architecture documentation, see [docs/IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md).

## Project Structure

```
/enforcesense
  /apps
    /api              # Legacy NestJS backend API (being migrated to api-* apps)
    /api-platform     # Platform/tenant management API
    /api-admin        # Admin API for tenant operations
    /api-client       # Client portal API
    /api-debtor       # Debtor self-service API
    /api-agent        # Agent/mobile API
    /web-platform     # Platform portal (React + Vite) - Tenant management
    /web-admin        # Admin portal (React + Vite)
    /web-client       # Client portal (React + Vite)
    /web-debtor       # Debtor portal (React + Vite)
    /mobile-agent     # Mobile agent app (placeholder)
  /packages
    /ui              # Shared UI components
    /types           # Shared TypeScript types
    /config          # Shared configuration
    /eslint-config   # Shared ESLint configuration
  /infra
    /docker          # Docker Compose configuration
    /db              # Database migrations and scripts
    /scripts         # Utility scripts
  /docs              # Documentation
```

## Prerequisites

- **Node.js**: >= 20.0.0
- **pnpm**: >= 8.0.0
- **Docker**: Latest version with Docker Compose support

## Quick Start

### 1. Clone and Install Dependencies

```bash
# Install pnpm if not already installed
npm install -g pnpm

# Install all dependencies
pnpm install
```

### 2. Set Up Environment Variables

```bash
# Create .env file in the root directory
# See docs/ENV_EXAMPLE_CONTENT.md for required environment variables

# Example .env file:
# DATABASE_URL=postgresql://enforcesense:enforcesense_password@postgres:5432/enforcesense_db?schema=public
# REDIS_HOST=redis
# REDIS_PORT=6379
# JWT_SECRET=your-super-secret-jwt-key-change-this-in-production
# ... (see docs/ENV_EXAMPLE_CONTENT.md for complete list)
```

For complete environment variable documentation, see [docs/ENV_EXAMPLE_CONTENT.md](docs/ENV_EXAMPLE_CONTENT.md).

### 3. Start All Services with Docker

```bash
# Start all services (PostgreSQL, Redis, MinIO, MailHog, API services, Web apps)
pnpm docker:up

# Or manually (using project name):
docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d
```

This will start:
- **Infrastructure**: PostgreSQL, Redis, MinIO, MailHog
- **API Services**: api-platform, api-admin, api-client, api-debtor, api-agent
- **Frontend Apps**: web-platform, web-admin, web-client, web-debtor

### 4. Access the Applications

Once all services are running, you can access:

- **Platform Portal**: http://127.0.0.2:6300
- **Admin Portal**: http://127.0.0.2:6301
- **Client Portal**: http://127.0.0.2:6302
- **Debtor Portal**: http://127.0.0.2:6303
- **API Platform**: http://127.0.0.2:6310
- **API Admin**: http://127.0.0.2:6311
- **API Client**: http://127.0.0.2:6312
- **API Debtor**: http://127.0.0.2:6313
- **API Agent**: http://127.0.0.2:6314
- **API Documentation (Swagger UI)**:
  - [Platform API Docs](http://127.0.0.2:6310/docs)
  - [Admin API Docs](http://127.0.0.2:6311/docs)
  - [Client API Docs](http://127.0.0.2:6312/docs)
  - [Debtor API Docs](http://127.0.0.2:6313/docs)
  - [Agent API Docs](http://127.0.0.2:6314/docs)
- **MailHog UI** (Email Viewer): http://127.0.0.2:65025
- **MinIO Console**: http://127.0.0.2:6901
  - Username: `enforcesense`
  - Password: `enforcesense_minio_password`

## Development

### Running Services Locally (without Docker)

If you prefer to run services locally:

```bash
# Install dependencies
pnpm install

# Run individual API services
cd apps/api-platform && pnpm start:dev
cd apps/api-admin && pnpm start:dev
cd apps/api-client && pnpm start:dev
cd apps/api-debtor && pnpm start:dev
cd apps/api-agent && pnpm start:dev

# Run frontend apps
cd apps/web-admin && pnpm dev
cd apps/web-client && pnpm dev
cd apps/web-debtor && pnpm dev
```

**Note**: You'll need PostgreSQL, Redis, MinIO, and MailHog running separately when developing locally. See [docs/DEV_SERVICES.md](docs/DEV_SERVICES.md) for connection details.

### Database Access

- **Host**: `127.0.0.2`
- **Port**: `6543`
- **Database**: `enforcesense_db`
- **Username**: `enforcesense`
- **Password**: `enforcesense_password`

```bash
# Connect with psql
psql -h 127.0.0.2 -p 6543 -U enforcesense -d enforcesense_db
```

### Redis Access

- **Host**: `127.0.0.2`
- **Port**: `6380`

```bash
# Connect with redis-cli
redis-cli -h 127.0.0.2 -p 6380
```

## Docker Commands

```bash
# Start all services
pnpm docker:up

# Stop all services
pnpm docker:down

# View logs
pnpm docker:logs

# View logs for specific service
docker-compose -f infra/docker/docker-compose.yml -p enforcesense logs -f api-admin
docker-compose -f infra/docker/docker-compose.yml -p enforcesense logs -f web-admin

# Rebuild and restart all services
docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d --build

# Rebuild specific service
docker-compose -f infra/docker/docker-compose.yml -p enforcesense build api-admin
docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d api-admin
```

## Port Reference

| Service       | Port  | URL                              |
|---------------|-------|----------------------------------|
| API Platform  | 6310  | http://127.0.0.2:6310            |
| API Platform Docs | 6310  | http://127.0.0.2:6310/docs        |
| API Admin     | 6311  | http://127.0.0.2:6311            |
| API Admin Docs | 6311  | http://127.0.0.2:6311/docs        |
| API Client    | 6312  | http://127.0.0.2:6312            |
| API Client Docs | 6312  | http://127.0.0.2:6312/docs        |
| API Debtor    | 6313  | http://127.0.0.2:6313            |
| API Debtor Docs | 6313  | http://127.0.0.2:6313/docs        |
| API Agent     | 6314  | http://127.0.0.2:6314            |
| API Agent Docs | 6314  | http://127.0.0.2:6314/docs        |
| Platform UI   | 6300  | http://127.0.0.2:6300            |
| Admin UI      | 6301  | http://127.0.0.2:6301            |
| Client UI     | 6302  | http://127.0.0.2:6302            |
| Debtor UI     | 6303  | http://127.0.0.2:6303            |
| PostgreSQL    | 6543  | 127.0.0.2:6543                   |
| Redis         | 6380  | 127.0.0.2:6380                   |
| MailHog SMTP  | 61025 | 127.0.0.2:61025                  |
| MailHog UI    | 65025 | http://127.0.0.2:65025           |
| MinIO API     | 6900  | http://127.0.0.2:6900            |
| MinIO Console | 6901  | http://127.0.0.2:6901            |

For detailed port mappings and service communication, see [docs/DEV_SERVICES.md](docs/DEV_SERVICES.md).

## Technology Stack

- **Backend**: NestJS (Node.js)
- **Frontend**: React + Vite + TypeScript
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Object Storage**: MinIO (S3-compatible)
- **Email Testing**: MailHog
- **Package Manager**: pnpm
- **Monorepo**: pnpm workspaces

## Documentation

### 🤖 For AI Agents - READ FIRST

- **[AGENTS_START_HERE.md](docs/AGENTS_START_HERE.md)** - ⭐ **START HERE** - Essential reading for all AI agents
- [AI Agent Guidelines](docs/AGENT_GUIDELINES.md) - **REQUIRED** - Mandatory rules and workflows for agents
- [Development TODO List](docs/DEVELOPMENT_TODO.md) - **REQUIRED** - Current task list - Check before starting any work

**Reference-only repo (do not modify):** CCS Quote Tool v2 can be used as a read-only reference for AI company research/enrichment and note-improvement patterns. See the “Reference Repo: CCS Quote Tool v2” section in [docs/AGENTS_START_HERE.md](docs/AGENTS_START_HERE.md) for the local path, GitHub link, and clone instructions.

### 📚 For Developers

- [Setup Guide](docs/SETUP_GUIDE.md) - Complete step-by-step setup instructions
- [Version Management](docs/VERSION_MANAGEMENT.md) - **Version numbering system** - How to manage and verify versions across all services
- [Implementation Plan](docs/IMPLEMENTATION_PLAN.md) - Consolidated implementation plan covering architecture, security, deployment, and development guidelines
- [Development Services & Ports](docs/DEV_SERVICES.md) - Complete service documentation and port mappings
- [Docker Setup Guide](docs/DOCKER_SETUP.md) - Docker configuration for multi-API architecture
- [Environment Variables](docs/ENV_EXAMPLE_CONTENT.md) - Environment variable examples and configuration

### 📖 API Documentation

- [API Documentation Guidelines](docs/API_DOCUMENTATION.md) - **REQUIRED** - Swagger/OpenAPI documentation standards and decorator usage
- [Code Documentation Standards](docs/CODE_DOCUMENTATION.md) - **REQUIRED** - JSDoc and inline documentation standards

**Live API Documentation (Swagger UI):**
- [Platform API Docs](http://localhost:4310/docs) - Platform/tenant management API
- [Admin API Docs](http://localhost:4311/docs) - Tenant internal operations API
- [Client API Docs](http://localhost:4312/docs) - Client portal API
- [Debtor API Docs](http://localhost:4313/docs) - Debtor self-service API
- [Agent API Docs](http://localhost:4314/docs) - Field agent/mobile API

### Archived Plans

The following plans have been consolidated into [IMPLEMENTATION_PLAN.md](docs/IMPLEMENTATION_PLAN.md) and moved to [docs/archive/](docs/archive/):

- [Phase 1 MVP Implementation Plan](docs/archive/enforcesense_phase_1_mvp_implementation_251bdc89.plan.md) - Archived (consolidated)
- [Security and Performance Remediation Plan](docs/archive/security_and_performance_remediation_a40c9525.plan.md) - Archived (consolidated, adapted for NestJS)

## License

Private - All rights reserved

