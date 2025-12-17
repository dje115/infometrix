# EnforceSense – Dev Services & Ports

This document describes all development services, their port mappings, and how they communicate in the EnforceSense Docker Compose stack.

## Service Overview

| Service       | Container Name          | Purpose                          |
|---------------|-------------------------|----------------------------------|
| PostgreSQL    | `enforcesense-postgres` | Primary database                 |
| Redis         | `enforcesense-redis`    | Caching & job queue              |
| MinIO         | `enforcesense-minio`    | Object storage (S3-compatible)   |
| MailHog       | `enforcesense-mailhog`  | SMTP server & email viewer       |
| API Platform  | `enforcesense-api-platform` | Platform/tenant management API |
| API Admin     | `enforcesense-api-admin` | Admin API for tenant operations |
| API Client    | `enforcesense-api-client` | Client portal API |
| API Debtor    | `enforcesense-api-debtor` | Debtor self-service API |
| API Agent     | `enforcesense-api-agent` | Agent/mobile API |
| Web Platform  | `enforcesense-web-platform` | Platform portal (React + Vite) - Tenant management |
| Web Admin     | `enforcesense-web-admin`| Admin portal (React + Vite)      |
| Web Client    | `enforcesense-web-client`| Client portal (React + Vite)    |
| Web Debtor    | `enforcesense-web-debtor`| Debtor portal (React + Vite)   |

## Port Mappings

Host ports are allocated in the **6xxx range** and bound to **`127.0.0.2`** to avoid Windows/WSL loopback conflicts (e.g. `wslrelay.exe`) that can cause `ERR_CONNECTION_RESET` on `localhost`.

### Infrastructure Services

| Service       | Host Port → Container Port | Access URL                    |
|---------------|----------------------------|-------------------------------|
| PostgreSQL    | 6543 → 5432                | `127.0.0.2:6543`              |
| Redis         | 6380 → 6379               | `127.0.0.2:6380`              |
| MinIO API     | 6900 → 9000               | `http://127.0.0.2:6900`       |
| MinIO Console | 6901 → 9001               | `http://127.0.0.2:6901`       |
| MailHog SMTP  | 61025 → 1025              | `127.0.0.2:61025`             |
| MailHog UI    | 65025 → 8025              | `http://127.0.0.2:65025`      |

### API Services

| Service       | Host Port → Container Port | Access URL                    |
|---------------|----------------------------|-------------------------------|
| API Platform  | 6310 → 3000                | `http://127.0.0.2:6310`       |
| API Admin     | 6311 → 3000                | `http://127.0.0.2:6311`       |
| API Client    | 6312 → 3000                | `http://127.0.0.2:6312`       |
| API Debtor    | 6313 → 3000                | `http://127.0.0.2:6313`       |
| API Agent     | 6314 → 3000                | `http://127.0.0.2:6314`       |

### Frontend Services

| Service       | Host Port → Container Port | Access URL                    |
|---------------|----------------------------|-------------------------------|
| Platform UI   | 6300 → 4173                | `http://127.0.0.2:6300`       |
| Admin UI      | 6301 → 4173                | `http://127.0.0.2:6301`       |
| Client UI     | 6302 → 4173                | `http://127.0.0.2:6302`       |
| Debtor UI     | 6303 → 4173                | `http://127.0.0.2:6303`       |

## Container-to-Container Communication

Within the Docker network (`enforcesense-net`), services communicate using **container names** and **internal ports**:

- **APIs → PostgreSQL**: `postgres:5432`
- **APIs → Redis**: `redis:6379`
- **APIs → MinIO**: `minio:9000`
- **APIs → MailHog**: `mailhog:1025`
- **web-platform → API**: `api-platform:3000` (via `VITE_API_BASE_URL`)
- **web-admin → API**: `api-admin:3000` (via `VITE_API_BASE_URL`)
- **web-client → API**: `api-client:3000` (via `VITE_API_BASE_URL`)
- **web-debtor → API**: `api-debtor:3000` (via `VITE_API_BASE_URL`)

## Host-to-Service Access

From your **host machine** (outside Docker), use `127.0.0.2` with the **host port**:

- **PostgreSQL**: `127.0.0.2:6543`
- **Redis**: `127.0.0.2:6380`
- **MinIO Console**: `http://127.0.0.2:6901` (login: `enforcesense` / `enforcesense_minio_password`)
- **MailHog UI**: `http://127.0.0.2:65025`
- **API Platform**: `http://127.0.0.2:6310`
- **API Admin**: `http://127.0.0.2:6311`
- **API Client**: `http://127.0.0.2:6312`
- **API Debtor**: `http://127.0.0.2:6313`
- **API Agent**: `http://127.0.0.2:6314`
- **Platform Portal**: `http://127.0.0.2:6300`
- **Admin Portal**: `http://127.0.0.2:6301`
- **Client Portal**: `http://127.0.0.2:6302`
- **Debtor Portal**: `http://127.0.0.2:6303`

## Reserved Ports

The following ports are **reserved for future services** and should not be used:

- **4304–4309**: Reserved for additional web services or microservices
- **Note**: Port 4300 is now used by Platform Portal

## Environment Variables

### For Container Communication

Services inside Docker should use:
- `POSTGRES_HOST=postgres`
- `REDIS_HOST=redis`
- `MINIO_ENDPOINT=http://minio:9000`
- `MAIL_HOST=mailhog`

### For Host Access

Tools running on your host machine should use:
- `POSTGRES_HOST=127.0.0.2`
- `POSTGRES_PORT=6543`
- `REDIS_HOST=127.0.0.2`
- `REDIS_PORT=6380`

## Rules for AI Agents

When adding new services to `docker-compose.yml`:

1. **Port Range**: Use ports in the **4000–4999** or **49000+** range
2. **Container Names**: Use prefix `enforcesense-` (e.g., `enforcesense-new-service`)
3. **Network**: Always add services to `enforcesense-net`
4. **Documentation**: Update this file with new service details
5. **Reserved Ports**: Avoid ports **4304–4310** (reserved)
6. **Environment Variables**: Use container names for internal communication, `localhost` for host access

## Quick Reference

```bash
# Start all services (using project name)
docker-compose -f infra/docker/docker-compose.yml -p enforcesense up -d

# Or use npm script
pnpm docker:up

# View logs
docker-compose -f infra/docker/docker-compose.yml -p enforcesense logs -f

# Or use npm script
pnpm docker:logs

# Stop all services
docker-compose -f infra/docker/docker-compose.yml -p enforcesense down

# Or use npm script
pnpm docker:down

# Check service status
docker ps --filter "name=enforcesense" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

# Access PostgreSQL from host
psql -h localhost -p 4543 -U enforcesense -d enforcesense_db

# Access Redis from host
redis-cli -h localhost -p 46379

# View logs for specific API
docker logs enforcesense-api-platform --tail 50 -f
```

