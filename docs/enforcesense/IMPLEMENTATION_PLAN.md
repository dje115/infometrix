---
name: EnforceSense Implementation Plan
overview: Comprehensive implementation plan for EnforceSense Phase 1 MVP including architecture, security, deployment, and development guidelines
version: 2.0
last_updated: 2024
---

# EnforceSense Implementation Plan

This document consolidates the architecture, security, deployment strategy, and development guidelines for EnforceSense Phase 1 MVP.

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [API Segmentation & Deployment Topology](#api-segmentation--deployment-topology)
3. [Platform Control Plane vs Tenant Data Plane](#platform-control-plane-vs-tenant-data-plane)
4. [Security Requirements](#security-requirements)
5. [Performance Optimization](#performance-optimization)
6. [Development Environment](#development-environment)
7. [Deployment Strategy](#deployment-strategy)
8. [AI Development Agent Guidelines](#ai-development-agent-guidelines)
9. [Roadmap to Microservices](#roadmap-to-microservices)
10. [AI Integration Specification](#ai-integration-specification)

**Related Documents:**
- [AI Integration Specification](./AI_INTEGRATION_SPEC.md) - Comprehensive AI capabilities, architecture, and implementation guide

---

## Architecture Overview

EnforceSense is a comprehensive debt enforcement management platform built as a monorepo with:

- **Backend**: NestJS (Node.js/TypeScript)
- **Frontend**: React + Vite + TypeScript
- **Database**: PostgreSQL 16
- **Cache/Queue**: Redis 7
- **Object Storage**: MinIO (S3-compatible)
- **Package Manager**: pnpm workspaces

### Core Design Principles

- **Shared Core Domain Layer**: Business logic lives in shared packages (e.g., `/packages/backend-core`)
- **Multiple Edge API Apps**: Separate NestJS applications for different audiences
- **Independent Deployment**: Each API can be deployed and scaled independently
- **Security Isolation**: Different security policies per API surface
- **Cloud Portability**: Designed for AWS/GCP/Azure deployment

---

## API Segmentation & Deployment Topology

### Core vs Edge Design

- **Shared Core**: Domain logic in `/packages/backend-core` (to be created)
- **Edge APIs**: Separate NestJS applications for different audiences
- **Edge apps import from core**, applying different:
  - Authentication/Authorization (RBAC)
  - Rate limiting
  - CORS policies
  - Security headers

### API Surfaces (By Audience)

| API Service | Purpose | Trust Level | Port (Dev) |
|-------------|---------|-------------|------------|
| **api-platform** | Platform/tenant management, control plane | Highest (VPN/IP-allowlist) | 6310 |
| **api-admin** | Tenant internal operations, cases, imports, SAR, finance, AI prompts | High (internal tenant staff) | 6311 |
| **api-client** | Client portal backend | Medium (authenticated clients) | 4312 |
| **api-debtor** | Debtor self-service backend | Lowest (public-facing, minimal operations) | 4313 |
| **api-agent** | Field agent/mobile backend | Medium (authenticated agents) | 4314 |

### Frontend ↔ API Pairing

Each frontend application MUST speak ONLY to its corresponding API service:

- **Platform Portal** → `api-platform` (port 6310)
- **Admin Portal** (`web-admin`) → `api-admin` (port 6311)
- **Client Portal** (`web-client`) → `api-client` (port 4312)
- **Debtor Portal** (`web-debtor`) → `api-debtor` (port 4313)
- **Agent/Mobile App** (`mobile-agent`) → `api-agent` (port 4314)

**Rules:**
- No frontend may call another API surface
- Frontends use `VITE_API_BASE_URL` environment variable
- Strict CORS policies per API surface
- No cross-API communication from frontends

### Required API Apps Structure

Each API app MUST exist under `/apps` with:

```
/apps/api-platform/
/apps/api-admin/
/apps/api-client/
/apps/api-debtor/
/apps/api-agent/
```

Each MUST have:
- Own `main.ts` and `AppModule`
- Own routes, guards, and CORS config
- Own Dockerfile
- Import shared domain logic from `/packages/backend-core` (when created)
- Map to its own host port in dev

### Port Mapping (Development)

#### API Services

| API App | Purpose | Host Port | Container Port |
|---------|---------|-----------|----------------|
| api-platform | Tenant manager / control plane | 6310 | 3000 |
| api-admin | Tenant internal operations | 6311 | 3000 |
| api-client | Client portal backend | 4312 | 3000 |
| api-debtor | Debtor self-service backend | 4313 | 3000 |
| api-agent | Bailiff / field agent backend | 4314 | 3000 |

#### Frontend Services

| Frontend App | Host Port | Container Port | Notes |
|--------------|-----------|----------------|-------|
| web-platform | 6300 | 4173 | Platform Portal - Tenant management |
| web-admin | 6301 | 4173 | Admin Portal |
| web-client | 6302 | 4173 | Client Portal |
| web-debtor | 6303 | 4173 | Debtor Portal |
| web-agent (future) | 6304 | 4173 | Agent web UI (optional) |

#### Infrastructure Services

| Component | Host Port | Container Port | Access URL |
|-----------|-----------|----------------|------------|
| PostgreSQL | 6543 | 5432 | `127.0.0.2:6543` |
| Redis | 6380 | 6379 | `127.0.0.2:6380` |
| MinIO API | 6900 | 9000 | `http://127.0.0.2:6900` |
| MinIO Console | 6901 | 9001 | `http://127.0.0.2:6901` |
| MailHog SMTP | 61025 | 1025 | `127.0.0.2:61025` |
| MailHog UI | 65025 | 8025 | `http://127.0.0.2:65025` |

**Reserved Ports**: 4304-4309 (for future services)

---

## Platform Control Plane vs Tenant Data Plane

### Platform / Tenant Manager (Control Plane)

**Purpose**: Manages EnforceSense as a product, not as a tenant

**Responsibilities**:
- Creates and manages tenants (name, slug, region, plan, status, feature flags)
- Manages global configuration (AI providers, regions, system limits)
- Platform Admin UI and Platform API
- Separate Platform database/schema for tenant metadata only

**Critical Rule**: Platform API MUST NOT query case/debtor/payment tables directly

**Deployment**:
- Production: Separate subdomain (e.g., `platform-api.enforcesense.com`)
- Most restricted: VPN/SSO/IP allowlist required
- Not publicly exposed

### Tenant Operational System (Data Plane)

**Purpose**: Core business system for tenant operations

**Components**:
- Case management, portals, payments, SAR, audit, finance
- Each tenant's data logically (and potentially physically) isolated
- Tenant admin users are different from Platform admins

**APIs**:
- Admin API, Client API, Debtor API, Agent API
- These APIs operate in data plane, assume tenantId exists and is valid

### Provisioning Flow

1. Platform Admin UI calls Platform API to create tenant in Platform DB
2. Platform triggers provisioning process (background worker/service)
3. Provisioning creates tenant record in operational system
4. Sets up default roles, settings, initial configuration
5. Platform DB remains source of truth for subscription/plan/status

### Support Access & Observability

- Separate, controlled mechanism for EnforceSense staff to inspect tenant environments
- Requires explicit operator action with strong auth (potentially dual control)
- Fully audited in AuditLog (who, which tenant, time window, what viewed/changed)
- Time-limited and revocable (just-in-time access)
- Platform MUST NOT have implicit, permanent superuser access

### Deployment & Network Separation

**Production**:
- Platform API/DB deployed separately from tenant APIs/DBs
- Different subdomain
- Different IAM roles/credentials
- Potentially different VPC or network segment

**Development**:
- Can run in single Docker Compose stack
- Codebase MUST clearly separate Platform modules from tenant operational modules

---

## Security Requirements

### Critical Security Requirements (NestJS Implementation)

#### 1. Authentication & Authorization

- **JWT-based authentication** using `@nestjs/jwt`
- **Refresh token rotation** with database storage
- **Token family detection** to prevent token reuse attacks
- **Role-based access control (RBAC)** per API surface
- **Password security**:
  - Minimum complexity requirements
  - Account lockout after failed attempts (5 attempts, 15-minute lockout)
  - Password history tracking (prevent reuse of last 5 passwords)

#### 2. API Security

- **CORS policies** per API surface:
  - Platform API: Most restrictive
  - Admin API: Internal only
  - Client/Debtor/Agent APIs: Configured per audience
- **Rate limiting** per endpoint type:
  - Admin endpoints: 1000 req/min
  - Login endpoints: 5 req/min (with progressive delays)
  - Public endpoints: 60 req/min
  - Authenticated endpoints: 300 req/min
- **Security headers middleware**:
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security (HSTS)
  - Content-Security-Policy (CSP)
- **CSRF protection** for state-changing operations (POST/PUT/DELETE)

#### 3. Data Security

- **API key encryption** at rest using symmetric encryption (Fernet or similar)
- **Environment-based error handling**: Generic messages in production, detailed in logs only
- **Input validation and sanitization**:
  - XSS prevention (sanitize user input)
  - SQL injection prevention (use Prisma parameterized queries)
  - No `dangerouslySetInnerHTML` in frontend without sanitization

#### 4. Network Security

- **Platform API**: VPN/IP-allowlist preferred
- **Debtor API**: Heavily rate-limited, minimal surface, strong anti-abuse protection
- **Admin/Client/Agent APIs**: Internet-accessible but locked down with authentication

### Security Implementation Checklist

- [ ] JWT token generation/validation
- [ ] Refresh token storage and rotation
- [ ] Password complexity and history
- [ ] Account lockout mechanism
- [ ] CORS configuration per API
- [ ] Rate limiting middleware
- [ ] Security headers middleware
- [ ] CSRF protection
- [ ] API key encryption
- [ ] Error handling (environment-based)
- [ ] Input sanitization (XSS prevention)
- [ ] Comprehensive security tests

---

## Performance Optimization

### Database Optimization

- **N+1 Query Prevention**:
  - Use Prisma's `include` or `select` for eager loading
  - Add database indexes for frequently queried fields
  - Query performance logging for slow operations
- **Connection Pooling**: Configure Prisma connection pool appropriately

### Caching Strategy

- **Redis caching** for:
  - Tenant configurations (TTL: 1 hour)
  - AI analysis results (TTL: 24 hours)
  - Frequently accessed customer data (TTL: 15 minutes)
- **Cache invalidation strategies** implemented
- **Cache hit rate monitoring**

### Async Operations

- **Background job processing** using Redis-based queue (Bull/BullMQ)
- **Avoid blocking operations** in request handlers
- **Proper async/await patterns** (no `asyncio.run()` anti-patterns)

### Background Workers (Celery-style in Node)

EnforceSense MUST use a Celery-style background task model, but implemented in the Node/TypeScript ecosystem (e.g. Bull or BullMQ + Redis), not Python Celery.

Conceptual model:

- We have **task queues** for long-running and non-blocking work.
- We have one or more dedicated **worker services/containers** that consume these queues.
- HTTP APIs enqueue jobs and return quickly; workers process them asynchronously.
- Frontends receive progress/completion via polling or WebSockets.

Implementation requirements:

- Use Redis as the backing store for queues.
- Use a Node-based queue library (e.g. Bull or BullMQ) in a dedicated worker app:
  - Initially a single worker process (e.g. `/apps/worker` or a worker entrypoint in one of the API apps).
  - Later, there may be **one worker per microservice** (notifications, imports, AI, finance, etc.).
- Define named queues for key domains, for example:
  - `imports`
  - `ai-tasks`
  - `reports`
  - `notifications`
  - `finance-jobs`

Examples of tasks that MUST be queued (non-blocking):

- Large CSV/Excel imports
- AI-based analysis (summaries, explanations, classifications)
- SAR data bundle generation
- Bulk status updates
- Heavy reports and exports
- Batch notifications (email/SMS)

Docker / deployment:

- In the initial monolith/multi-API phase, at least one `worker` container MUST be defined in `docker-compose.yml`, e.g.:
  - `enforcesense-worker-core` using the same image as one of the API apps but with a different command such as `node dist/worker/main.js` or an equivalent worker entrypoint.
- In later microservice phases, each major service MAY have its own dedicated worker deployment:
  - `notifications-worker`
  - `ai-worker`
  - `import-worker`
  - `finance-worker`
- All workers MUST connect to the same Redis instance (or a clearly configured cluster) and subscribe only to the queues they are responsible for.

Frontend behaviour:

- Frontend code MUST NOT wait synchronously on heavy operations.
- Instead, when a user triggers a long-running operation, the API:
  - Enqueues a job,
  - Returns a job ID or correlation ID,
  - Optionally triggers a WebSocket subscription.
- Frontends use either:
  - Polling of `/jobs/:id`-style endpoints, or
  - WebSocket events (`job:progress`, `job:completed`, `job:failed`).

AI dev agent rules:

- Never block HTTP requests for long-running work; always enqueue a job and return quickly.
- Treat this pattern as equivalent to "Celery tasks and workers" in the Python world, but implemented with TypeScript, Redis, and a Node queue library (Bull/BullMQ).
- Place queue and worker logic in shared backend packages where appropriate (e.g. `/packages/backend-core/queues`), not copy-pasted into each API.
- Ensure that any new feature that is long-running or computationally heavy is designed from the start to use this background worker pattern.

### Performance Targets

- Sub-100ms response times for 95% of requests
- N+1 queries eliminated (verified with query logging)
- Cache hit rate > 80% for cached endpoints

---

## Development Environment

### Docker Compose Setup

All services run in Docker Compose for development:

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

# Rebuild specific service
docker-compose -f infra/docker/docker-compose.yml -p enforcesense build api-admin
```

### Container-to-Container Communication

Within Docker network (`enforcesense-net`), services use **container names**:

- **API → PostgreSQL**: `postgres:5432`
- **API → Redis**: `redis:6379`
- **API → MinIO**: `minio:9000`
- **API → MailHog**: `mailhog:1025`
- **Frontends → API**: `api-admin:3000`, `api-client:3000`, etc.

### Host-to-Service Access

From host machine, use `localhost` with **host ports**:

- PostgreSQL: `127.0.0.2:6543`
- Redis: `127.0.0.2:6380`
- MinIO Console: `http://127.0.0.2:6901`
- MailHog UI: `http://127.0.0.2:65025`
- APIs: `http://127.0.0.2:6310-6314`
- Frontends: `http://127.0.0.2:6300-6303`

### Environment Variables

See [ENV_EXAMPLE_CONTENT.md](ENV_EXAMPLE_CONTENT.md) for complete environment variable configuration.

### Local Development (Without Docker)

```bash
# Install dependencies
pnpm install

# Run all apps in development mode
pnpm dev

# Or run individual apps
cd apps/api-admin && pnpm start:dev
cd apps/web-admin && pnpm dev
```

---

## Deployment Strategy

### Cloud Deployment Requirements

The system MUST be deployable as **separate cloud services**, one per API:

- **Separate autoscaling groups** / Kubernetes deployments
- **Separate security groups** / firewall rules / WAF profiles
- **Separate service logs** and resource limits
- **Optional different infrastructure tiers** (e.g., beefier admin API instance, smaller debtor API)

### Production Network Topology

- **Platform API**: Most locked-down (VPN/SSO/IP allowlist, not publicly exposed)
- **Admin API**: Internal tenant staff only
- **Client API**: Internet-accessible, authenticated and rate-limited
- **Debtor API**: Internet-accessible, heavily hardened and minimal surface
- **Agent API**: Mobile clients, authenticated and rate-limited

### Scaling Model

Each API can be scaled independently:

- **High-volume public surfaces** (e.g., Debtor API) can scale horizontally
- **Lower-volume but sensitive APIs** (Admin/Platform) can use smaller instances
- **Optional future support**: "Dedicated stack per high-value tenant" by deploying a full set of `api-*` + frontends for that tenant

### Reverse Proxy / API Gateway

In production, use reverse proxy or API gateway for:
- Routing requests to appropriate API services
- SSL/TLS termination
- Request logging and monitoring
- Additional rate limiting and WAF

---

## AI Development Agent Guidelines

### Architecture Enforcement

The AI development agent MUST:

1. **Always generate backend code as separate NestJS apps** for each API
2. **Only import shared business logic** from `/packages/backend-core` (when created)
3. **Ensure no API exposes endpoints** meant for another audience
4. **Ensure frontends always point** to their corresponding API surface
5. **Maintain strict port usage** and Docker separation as defined above
6. **Keep containers cleanly split** to maximize security and cloud portability

### Code Organization

- **Domain logic**: Reusable across `api-*` apps, lives in shared packages
- **Edge/controllers**: Specific per API and audience
- **No code duplication**: Use shared packages, not copy-paste

### Feature Placement Decision

When adding features, decide:

- **Platform (control plane)**: Tenant management, global config, provisioning
- **Tenant Operational System (data plane)**: Cases, debtors, payments, SAR, audit

**Rules**:
- Platform functionality in Platform-specific modules that do NOT access case/debtor/payment data
- Tenant admins in data plane do NOT have access to platform-level controls
- Platform code uses only minimal necessary data about tenants

### Security Implementation

- Place endpoints in appropriate modules per audience
- Respect security boundaries
- Keep domain logic shared and DRY
- Implement proper authentication/authorization per API
- Add rate limiting appropriate to audience
- Configure CORS per API surface

### Docker & Deployment

- Keep Dockerfiles compatible with running each API as its own container
- Update `docker-compose.yml` when adding new services
- Follow port allocation rules (6xxx range for host ports)
- Use container name prefix `enforcesense-`
- Always add services to `enforcesense-net` network

---

## Roadmap to Microservices

EnforceSense is initially implemented as a modular monolith with multiple API apps (Platform, Admin, Client, Debtor, Agent) in a single monorepo. However, the architecture MUST allow a gradual, low-risk migration to microservices when required by scale, security, or organisational needs.

The AI development agent MUST follow this staged roadmap and design code so it can be evolved along these lines.

### Phase 0 – Modular Monolith (Current Baseline)

- Single operational Postgres instance (one DB), Redis, MinIO, Mailhog.
- Multiple API apps (`api-platform`, `api-admin`, `api-client`, `api-debtor`, `api-agent`) as separate NestJS applications but sharing:
  - A common domain layer in shared packages (e.g. `/packages/backend-core`).
- Domain logic is grouped by business area (modules such as `cases`, `debtors`, `clients`, `payments/finance`, `imports`, `sar/compliance`, `ai`, `notifications`).

Rules:

- APIs must call into domain services rather than duplicating logic.
- Domain modules must interact through clear interfaces and avoid circular references.
- No direct cross-module DB access patterns that make later separation impossible.

### Phase 1 – Extract Support Services

When needed, the first services to extract into separate deployables are "support" services that do not own critical core business data:

Examples:

1. **Notification Service**
   - Owns message sending (email, SMS, push, letters).
   - Provides a small HTTP/queue-based interface for other services to request notifications.
   - Consumes events from the core system (e.g. CaseCreated, PaymentReceived).

2. **AI Service**
   - Owns AI provider integration (OpenAI, Azure OpenAI, etc.) and the AI prompt database.
   - Exposes API endpoints for AI tasks (e.g. summarise case, explain import errors).
   - All other services call this AI service instead of providers directly.

3. **Import Processor Service**
   - Owns heavy import processing logic.
   - Admin/Client APIs enqueue jobs; this service processes them and reports status via queues/WebSockets.

The AI dev agent MUST structure these features so they can be easily moved behind a separate API/queue without massive rewrites.

### Phase 2 – Extract Core Domain Services (When Justified)

As the system grows, core domains that justify stronger isolation and independent scaling may be extracted into their own microservices, for example:

1. **Finance / Billing Service**
   - Owns CaseTransactions, financial summaries, remittances, accounting integration.
   - Provides APIs like:
     - `GET /cases/:id/financial-summary`
     - `POST /cases/:id/transactions`
   - Is the single source of truth for case monetary state.

2. **Case / Workflow Service** (optional, later)
   - Owns case lifecycle, status transitions, and workflow rules.
   - Other services hold only references to case IDs and derived read-models.

Rules:

- Domain ownership must be clear: each service owns its own write model.
- Other services may maintain read-only projections (CQRS) backed by events.

### Phase 3 – Data Separation

Over time, move from a single shared schema to clearer data boundaries:

- Start with **schema-per-domain** in the same Postgres instance:
  - `core.cases`, `finance.transactions`, `compliance.sar`, etc.
- Later, if necessary, move heavily loaded or sensitive domains to:
  - Separate Postgres instances or managed DBs.
- Use events / change data capture (CDC) to keep projections in sync across services.

The AI dev agent MUST avoid designs that require cross-service joins at the database layer; communication between services SHOULD be via APIs, queues, or events, not direct cross-schema queries in another service's DB.

### Phase 4 – Cloud-Native Microservice Deployments

When microservices are split:

- Each service runs as its own deployment (e.g. K8s Deployment, ECS Service, App Service).
- An API gateway or ingress routes requests to the correct service.
- Security, scaling, and fault isolation are configured per service:
  - Debtor-facing services: high scale, strict rate limiting, hardened inputs.
  - Finance services: stricter access control, intensive auditing.
  - Platform services: heavily restricted (VPN/SSO/IP allowlist).

Observability:

- Centralised logging across services.
- Metrics per service (latency, error rate, throughput).
- Distributed tracing to follow end-to-end flows.

### Principles & Constraints for the AI Dev Agent

When implementing or changing code, the AI development agent MUST:

- Favour designs that keep domain modules internally cohesive and externally loosely coupled.
- Avoid tight coupling between unrelated modules that would make separation difficult.
- Ensure any new cross-domain feature uses:
  - Clear service boundaries (e.g. via interfaces and injection),
  - Or patterns that map cleanly to future service-to-service calls (e.g. command/query interfaces, events), rather than hard-coded direct DB access.
- Prefer monorepo-based microservices (multiple apps, shared types and domain packages) over separate repos, unless explicitly instructed otherwise.

Microservices are a future deployment option; the current implementation should be microservice-friendly, but not prematurely fragmented.

---

## Success Metrics

### Security

- Zero critical vulnerabilities in security scan
- All XSS vectors eliminated (verified with security testing)
- 100% test coverage for security-critical code paths
- Security rating: 9/10 (Enterprise-grade)

### Performance

- Sub-100ms response times for 95% of requests
- N+1 queries eliminated (verified with query logging)
- Cache hit rate > 80% for cached endpoints
- Performance rating: 9/10 (Optimized for high load)

### Architecture

- All APIs deployable as separate containers
- No cross-API dependencies from frontends
- Shared domain logic properly abstracted
- Platform and tenant systems cleanly separated

---

## 10. AI Integration Specification

EnforceSense will integrate AI capabilities to improve internal efficiency, client value, debtor experience, and compliance. AI is implemented as an **assistive tool** that enhances human decision-making, not as an autonomous decision-maker.

### Key Principles

- **Non-blocking by default**: AI tasks run asynchronously using background workers
- **Prompt governance**: All prompts stored in database, versioned with rollback capability
- **Provider abstraction**: Support OpenAI, Azure OpenAI, and future providers via unified interface
- **Tenant isolation**: AI data never crosses tenant boundaries
- **Immutable records**: Original data unchanged; AI produces derived artifacts
- **Safety first**: Debtor-facing AI is highly constrained; all AI usage is audited

### AI Capabilities

**Internal Staff & Contact Centre:**
- Note cleanup & normalisation
- Call transcript summarisation
- Case handover summaries
- Field agent visit outcome standardisation

**Client Value:**
- Client-facing case summaries
- Import error explanations
- Performance reporting narratives

**Debtor Experience:**
- Plain-English explanations (multilingual)
- Payment & arrangement guidance
- Vulnerability detection assistance

**Compliance & Risk:**
- Tone/risk language scanning
- SAR preparation assistance
- Audit trail explanations

### Architecture

- **AI Orchestrator**: Routes tasks, loads prompts, applies policies
- **Provider Adapters**: OpenAI, Azure OpenAI, future providers
- **Prompt Registry**: Database-backed templates with versioning
- **Background Workers**: Process AI jobs asynchronously
- **Results Store**: Persist AI outputs with full audit trail

### Implementation Status

See [AI Integration Specification](./AI_INTEGRATION_SPEC.md) for:
- Complete data model (Prisma schema extensions)
- API endpoints and WebSocket events
- Prompt templates and governance
- Security and privacy requirements
- Rollout plan (Stage 1 MVP → Stage 3 Advanced)
- Mandatory enforcement rules for AI development

**Current Status**: Specification complete, ready for Stage 1 implementation

---

## Related Documentation

- [AI Integration Specification](./AI_INTEGRATION_SPEC.md) - Comprehensive AI capabilities, architecture, and implementation guide
- [Development Services & Ports](DEV_SERVICES.md) - Service documentation and port mappings
- [Docker Setup Guide](DOCKER_SETUP.md) - Docker configuration details
- [Environment Variables](ENV_EXAMPLE_CONTENT.md) - Environment variable examples

---

**Last Updated**: 2024  
**Version**: 2.0  
**Status**: Active Implementation

