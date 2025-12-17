---
name: EnforceSense Phase 1 MVP Implementation
overview: Comprehensive implementation plan for EnforceSense Phase 1 MVP including API segmentation, containerization strategy, and platform control plane separation
todos: []
---

# EnforceSense Phase 1 MVP Implementation Plan

## 15. API SEGMENTATION & DEPLOYMENT TOPOLOGY

### 15.1 Core vs Edge Design

- Shared core domain layer (`/packages/backend-core`) containing business logic
- Multiple edge API apps (separate NestJS applications) for different audiences
- Edge apps import from core, apply different auth/RBAC/rate-limits/CORS

### 15.2 API Surfaces (By Audience)

- **Admin API**: Internal/high trust, tenant management, cases, imports, SAR, finance, AI prompts
- **Client API**: Medium trust, client-facing operations only
- **Debtor API**: Lowest trust/public-facing, minimal operations, strong rate limiting
- **Agent/Mobile API**: Field staff, authenticated agents, heavier rate limiting

### 15.3 Frontends & Their APIs

- Each frontend only talks to its corresponding API surface
- Strict CORS policies per API surface
- No cross-API communication from frontends

### 15.4 Network & Security Topology (Non-Dev)

- Admin API: VPN/IP-allowlist preferred
- Client API: Internet-accessible, locked down
- Debtor API: Internet-accessible, heavily rate-limited
- Agent API: Internet-accessible, similar to Client API
- Reverse proxy/API gateway routing in production

### 15.5 Dev Environment Simplification

- Single `api` container acceptable in dev, exposing all surfaces on different paths
- Codebase must preserve option to deploy as separate processes
- Path-based routing: `/admin`, `/client`, `/debtor`, `/agent`

### 15.6 Enforcement by the AI Dev Agent

- Place endpoints in appropriate modules per audience
- Respect security boundaries
- Keep domain logic shared and DRY

### 15.7 Containerisation Strategy (Separate API Containers)

EnforceSense MUST be designed so that each API surface (Platform, Admin, Client, Debtor, Agent) can run as an independent containerised service.

The target architecture is:

- Separate NestJS apps:
- `/apps/api-platform`
- `/apps/api-admin`
- `/apps/api-client`
- `/apps/api-debtor`
- `/apps/api-agent`
- Each with its own:
- `main.ts` and `AppModule`
- Dockerfile
- Environment configuration (ports, CORS, logging)
- All importing common domain logic from shared backend packages (e.g. `/packages/backend-core`), to avoid duplication.

In production:

- Each API app runs in its own container (or Kubernetes deployment/Task/etc).
- Different network/security policies can be applied per API:
- Platform API: most restricted (VPN/SSO, IP allowlist).
- Admin API: internal tenant staff only.
- Client API: internet but authenticated and rate-limited.
- Debtor API: internet, heavily hardened and minimal surface.
- Agent API: mobile clients, authenticated and rate-limited.

In development (Docker Compose):

- It is acceptable initially to:
- Either run a single `api` container exposing multiple API surfaces by path (e.g. `/admin`, `/client`, `/debtor`, `/agent`),
- OR to run a subset of the APIs as separate containers.
- HOWEVER, the codebase MUST be structured so that splitting into separate `api-*` apps and containers later does not require major refactoring.

The AI development agent MUST:

- Prefer creating new API modules as separate NestJS apps under `/apps/api-*` when building out the system.
- Ensure shared logic lives in internal packages (e.g. `/packages/backend-core`), not copy-pasted between API apps.
- Keep Dockerfiles and `docker-compose` (dev) compatible with running each API as its own container where required.

### 15.8 Frontend ↔ API Pairing & Scaling Model

Each major user-facing application MUST have a corresponding, separately deployable API app:

- Platform Portal ↔ `api-platform`
- Admin Portal (`web-admin`) ↔ `api-admin`
- Client Portal (`web-client`) ↔ `api-client`
- Debtor Portal (`web-debtor`) ↔ `api-debtor`
- Agent App (`mobile-agent`) ↔ `api-agent`

Each `api-*` app:

- Is a separate NestJS application under `/apps/api-*`.
- Imports shared domain logic from internal packages (e.g. `/packages/backend-core`).
- Has its own Dockerfile and environment configuration.
- Can be scaled independently in a cloud environment (separate service/deployment).

In production, this allows:

- Different WAF, CORS, rate-limits and auth policies per API.
- Independent scaling of:
- High-volume public surfaces (e.g. Debtor API),
- Lower-volume but sensitive admin/Platform APIs.
- Optional future support for "dedicated stack per high-value tenant" by deploying a full set of `api-*` + frontends for that tenant with different env configuration.

The AI development agent MUST:

- Keep frontends and APIs loosely coupled but clearly paired (each frontend calls only its intended API).
- Structure backend code so that:
- Domain logic is reusable across `api-*` apps,
- Edge/controllers are specific per API and audience.

### 15.9 API Containerisation & Port Mapping (Mandatory)

EnforceSense MUST run each API surface as its own independent NestJS application AND its own Docker container, with clean port allocation for development and full separation for production deployment.

This improves:

- Security isolation
- Least-privilege surface exposure
- Scalability per audience type
- Cloud portability (AWS/GCP/Azure)
- Blast-radius reduction in case of compromise

#### A. Frontend ↔ API Server Pairs

Each frontend application MUST speak ONLY to its corresponding API service:

- Platform Portal → `api-platform`
- Admin Portal (`web-admin`) → `api-admin`
- Client Portal (`web-client`) → `api-client`
- Debtor Portal (`web-debtor`) → `api-debtor`
- Agent/Mobile App (`mobile-agent`) → `api-agent`

No frontend may call another API surface.

Frontends must use environment variables like `VITE_API_BASE_URL` pointing to the correct API port.

#### B. Required API Apps (Separate Containers)

The following NestJS apps MUST exist under `/apps`:

- `/apps/api-platform`
- `/apps/api-admin`
- `/apps/api-client`
- `/apps/api-debtor`
- `/apps/api-agent`

Each MUST:

- Have its own Nest `main.ts`, `AppModule`, routes, guards, and CORS config.
- Import shared domain logic from `/packages/backend-core`.
- Have its own Dockerfile.
- Map to its own host port in dev.

#### C. Concrete Port Mapping (Development)

**API APPS (separate containers):**

| API App         | Purpose                         | Host Port | Container Port |
|-----------------|----------------------------------|-----------|----------------|
| api-platform    | Tenant manager / control plane  | 4310      | 3000           |
| api-admin       | Tenant internal operations      | 4311      | 3000           |
| api-client      | Client portal backend           | 4312      | 3000           |
| api-debtor      | Debtor self-service backend     | 4313      | 3000           |
| api-agent       | Bailiff / field agent backend   | 4314      | 3000           |

**FRONTEND PORTS (Vite):**

| Frontend App      | Host Port | Notes |
|-------------------|-----------|-------|
| web-admin         | 4301      | Admin Portal |
| web-client        | 4302      | Client Portal |
| web-debtor        | 4303      | Debtor Portal |
| web-agent (opt)   | 4304      | Agent web UI |

**INFRA SERVICES (existing):**

| Component      | Host Port | Container Port |
|----------------|-----------|----------------|
| Postgres       | 4543      | 5432           |
| Redis          | 46379     | 6379           |
| MinIO API      | 49000     | 9000           |
| MinIO Console  | 49001     | 9001           |
| MailHog SMTP   | 41025     | 1025           |
| MailHog UI     | 48025     | 8025           |

#### D. Docker Compose Requirements

The development Docker Compose stack MUST include separate services:

- `api-platform`
- `api-admin`
- `api-client`
- `api-debtor`
- `api-agent`

Each service:

- Must expose its mapped host port.
- Must reference its own Dockerfile within `/apps/<api-name>/Dockerfile`.
- Must depend on Postgres and Redis.
- Must run independently so individual APIs can be restarted without affecting others.

#### E. Cloud Deployment Requirements

The system MUST be deployable as **separate cloud services**, one per API:

- Separate autoscaling groups / Kubernetes deployments
- Separate security groups / firewall rules / WAF profiles
- Separate service logs and resource limits
- Optional different infrastructure tiers (e.g. beefier admin API instance, smaller debtor API)

Platform API MUST be the most locked-down:

- VPN / SSO / IP allowlist required
- Not publicly exposed

Debtor API MUST be the most rate-limited and hardened:

- Strong anti-abuse protection
- No sensitive operational endpoints

Admin API, Client API, and Agent API MUST have different CORS, auth, and rate-limit policies.

#### F. Architecture Enforcement for AI Development Agent

The AI development agent MUST:

- Always generate backend code as separate NestJS apps for each API.
- Only import shared business logic from `/packages/backend-core`.
- Ensure no API exposes endpoints meant for another audience.
- Ensure frontends always point to their corresponding API surface.
- Maintain strict port usage and Docker separation as defined above.

Containers MUST remain cleanly split to maximise security and cloud portability.

## 16. PLATFORM CONTROL PLANE VS TENANT DATA PLANE

### 16.1 Platform / Tenant Manager (Control Plane)

- Manages EnforceSense as a product, not as a tenant
- Creates and manages tenants (name, slug, region, plan, status, feature flags)
- Manages global configuration (AI providers, regions, system limits)
- Includes Platform Admin UI and Platform API
- Separate Platform database/schema for tenant metadata only
- Platform API MUST NOT query case/debtor/payment tables directly

### 16.2 Tenant Operational System (Data Plane)

- Core business system: case management, portals, payments, SAR, audit, finance
- Each tenant's data logically (and potentially physically) isolated
- Tenant admin users are different from Platform admins
- APIs: Admin API, Client API, Debtor API, Agent API
- These APIs operate in data plane, assume tenantId exists and is valid

### 16.3 Provisioning Flow Between Platform and Tenant System

1. Platform Admin UI calls Platform API to create tenant in Platform DB
2. Platform triggers provisioning process (background worker/service)
3. Provisioning creates tenant record in operational system
4. Sets up default roles, settings, initial configuration
5. Platform DB remains source of truth for subscription/plan/status

### 16.4 Support Access & Observability

- Separate, controlled mechanism for EnforceSense staff to inspect tenant environments
- Requires explicit operator action with strong auth (potentially dual control)
- Fully audited in AuditLog (who, which tenant, time window, what viewed/changed)
- Time-limited and revocable (just-in-time access)
- Platform MUST NOT have implicit, permanent superuser access

### 16.5 Deployment & Network Separation

- Production: Platform API/DB deployed separately from tenant APIs/DBs
- Different subdomain (e.g. `platform-api.enforcesense.com`)
- Different IAM roles/credentials
- Potentially different VPC or network segment
- Dev environment can run in single Docker Compose stack
- Codebase MUST clearly separate Platform modules from tenant operational modules

### 16.6 Enforcement by the AI Dev Agent

- Decide whether feature belongs to Platform (control plane) or Tenant Operational System (data plane)
- Put Platform functionality in Platform-specific modules that do NOT access case/debtor/payment data
- Ensure tenant admins in data plane do NOT have access to platform-level controls
- Ensure Platform code uses only minimal necessary data about tenants