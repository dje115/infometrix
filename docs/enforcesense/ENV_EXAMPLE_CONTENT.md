# Environment Variable Examples

Since `.env.example` files are protected, this document contains the content that should be in those files.

## Root `.env.example`

Create or update `/.env.example` with the following content:

```bash
# Postgres (inside Docker)
POSTGRES_USER=enforcesense
POSTGRES_PASSWORD=enforcesense_password
POSTGRES_DB=enforcesense_db
POSTGRES_HOST=postgres
POSTGRES_PORT=5432

DATABASE_URL=postgresql://enforcesense:enforcesense_password@postgres:5432/enforcesense_db?schema=public

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# MinIO
MINIO_ENDPOINT=http://minio:9000
MINIO_ROOT_USER=enforcesense
MINIO_ROOT_PASSWORD=enforcesense_minio_password
MINIO_BUCKET=enforcesense-dev

# Mailhog
MAIL_HOST=mailhog
MAIL_PORT=1025
MAIL_FROM="EnforceSense Dev <no-reply@enforcesense.local>"

# API ports (inside containers)
API_PORT=3000

# Host-facing base URLs (for docs / tooling)
API_PLATFORM_URL=http://127.0.0.2:6310
API_ADMIN_URL=http://127.0.0.2:6311
API_CLIENT_URL=http://localhost:4312
API_DEBTOR_URL=http://localhost:4313
API_AGENT_URL=http://localhost:4314

WEB_PLATFORM_URL=http://127.0.0.2:6300
WEB_ADMIN_URL=http://127.0.0.2:6301
WEB_CLIENT_URL=http://localhost:4302
WEB_DEBTOR_URL=http://localhost:4303

NODE_ENV=development
```

## Database `.env.example`

Create or update `/infra/db/.env.example` with the following content:

```bash
# Prisma CLI (run from host) connects via:
DATABASE_URL="postgresql://enforcesense:enforcesense_password@127.0.0.2:6543/enforcesense_db?schema=public"
```

Note: This uses `127.0.0.2:6543` because Prisma CLI runs from the host machine, not inside Docker containers.

