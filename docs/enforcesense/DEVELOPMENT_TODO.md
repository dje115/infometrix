# EnforceSense Development TODO List

> ⚠️ **For AI Agents**: Read [AGENTS_START_HERE.md](AGENTS_START_HERE.md) and [AGENT_GUIDELINES.md](AGENT_GUIDELINES.md) **BEFORE** using this TODO list!

This document tracks the development tasks for the EnforceSense platform. Tasks are organized by priority and category.

## 🤖 Instructions for AI Agents

**CRITICAL: All AI agents working on this project MUST follow these rules:**

### TODO List Management Rules

1. **ALWAYS update the TODO list when:**
   - Starting a new task → Mark it as `in_progress`
   - Completing a task → Mark it as `completed` and add completion date
   - Discovering a new requirement → Add it to the appropriate phase
   - Encountering blockers → Add notes or create new tasks
   - Changing task priority → Update the phase/priority

2. **Use the `todo_write` tool to:**
   - Update task status (pending → in_progress → completed)
   - Add new tasks when discovered
   - Merge updates when working on multiple tasks
   - Mark tasks as cancelled if no longer needed

3. **Before starting any work:**
   - Check this TODO list for existing tasks
   - Mark the task as `in_progress` using `todo_write`
   - Reference the task ID in your work

4. **After completing work:**
   - Mark the task as `completed` using `todo_write`
   - Update this markdown file to reflect completion
   - Add any follow-up tasks discovered during implementation

5. **When adding new tasks:**
   - Use descriptive, actionable task descriptions
   - Assign to appropriate phase/priority
   - Include context if needed
   - Link related tasks

6. **Task Status Values:**
   - `pending` - Not started
   - `in_progress` - Currently being worked on
   - `completed` - Finished
   - `cancelled` - No longer needed

### Collaboration Guidelines

- **Only ONE task should be `in_progress` per agent at a time**
- **Check for conflicts** before marking a task `in_progress`
- **Update immediately** after status changes (don't wait until end of session)
- **Be specific** in task descriptions to avoid duplication
- **Reference task IDs** in commit messages when applicable

### Example Workflow

```typescript
// 1. Before starting work
todo_write({
  merge: true,
  todos: [{ id: 'dev-1', status: 'in_progress' }]
})

// 2. Do the work...

// 3. After completing
todo_write({
  merge: true,
  todos: [{ id: 'dev-1', status: 'completed' }]
})

// 4. Update markdown file
// Mark [ ] as [x] in DEVELOPMENT_TODO.md
```

### TODO List File Location

- **Primary TODO**: `docs/DEVELOPMENT_TODO.md` (this file)
- **Tool-based TODO**: Managed via `todo_write` tool (synced with this file)
- **Both must be kept in sync**

---

## 🐳 Development Environment

**⚠️ IMPORTANT: All development and testing must be done in Docker containers.**

- Do NOT run services locally (`pnpm dev`, `npm start`, etc.)
- Always rebuild Docker containers to test changes
- Access services via `localhost` ports (see [DEV_SERVICES.md](DEV_SERVICES.md))
- See [DOCKER_SETUP.md](DOCKER_SETUP.md) for Docker setup instructions

## 📋 Task Status Legend

- [ ] = Pending (not started)
- [🚧] = In Progress (currently being worked on)
- [x] = Completed
- [❌] = Cancelled (no longer needed)

## ✅ Completed Setup Tasks

- [x] Infrastructure setup - Docker containers, services, networking
- [x] Version management system - Display version on all portals and APIs
- [x] GitHub release automation - Auto-create releases from version tags
- [x] Documentation - Setup guides, architecture docs, version management

## 🚀 Phase 1: Foundation (Priority 1)

### Database & Schema
- [ ] **Database setup**
  - [ ] Run Prisma migrations
  - [ ] Verify schema matches requirements
  - [ ] Create seed data script
  - [ ] Test database connections from all API services

### Authentication & Authorization
- [x] **Authentication system**
  - [x] JWT token generation and validation
  - [x] Login endpoint (all APIs)
  - [x] Logout endpoint
  - [x] Password reset flow
  - [x] Refresh token mechanism
  - [x] Password hashing (bcrypt)

- [x] **Authorization**
  - [x] Role-based access control (RBAC)
  - [x] Permission system (basic RBAC implemented)
  - [x] Multi-tenant isolation guards
  - [x] API route guards

### User Management
- [x] **User CRUD operations**
  - [x] Create user (api-platform, api-admin)
  - [x] Update user (api-platform, api-admin)
  - [x] Delete user (soft delete) (api-platform, api-admin)
  - [x] List users with pagination (api-platform, api-admin)
  - [x] Search users (api-platform, api-admin)
  - [ ] User profile management

- [x] **User roles and permissions**
  - [x] Assign roles to users (via update endpoint)
  - [x] Permission checking middleware (RolesGuard implemented)
  - [ ] Role hierarchy (can be extended later if needed)

## 🏗️ Phase 2: Core Business Logic (Priority 2)

### Tenant Management
- [x] **Tenant/Organization CRUD**
  - [x] Create tenant (api-platform)
  - [x] Update tenant configuration (api-platform)
  - [ ] Tenant settings management
  - [ ] Tenant branding (logos, colors)

### Client Organization Management
- [x] **Client CRUD operations**
  - [x] Create client organization (api-admin)
  - [x] Update client details (api-admin)
  - [x] Link clients to tenants (automatic via tenant scoping)
  - [x] Client contact management (api-admin)
  - [ ] Client reporting

### Debtor Management
- [x] **Debtor CRUD operations**
  - [x] Create debtor record (api-admin)
  - [x] Update debtor information (api-admin)
  - [x] Search debtors (api-admin)
  - [x] Filter debtors (by vulnerable status) (api-admin)
  - [x] Debtor contact information (api-admin)
  - [x] Debtor address management (api-admin)

### Case Management
- [x] **Case CRUD operations**
  - [x] Create case (api-admin)
  - [x] Link case to debtor and client (api-admin)
  - [x] Update case status (api-admin)
  - [x] Case reference number generation (api-admin)
  - [x] Case search and filtering (api-admin)
  - [x] Case assignment to agents/managers (api-admin)

- [x] **Case status workflow**
  - [x] Status transitions (api-admin)
  - [ ] Status history (can be added via audit logs)
  - [ ] Automated status updates

### Case Transactions
- [x] **Transaction recording**
  - [x] Record principal charges (api-admin)
  - [x] Record fees (api-admin)
  - [x] Record interest charges (api-admin)
  - [x] Record cost charges (api-admin)
  - [x] Transaction history (api-admin)
  - [x] Balance calculations (api-admin)

### Payment Processing
- [x] **Payment operations**
  - [x] Record payment receipt (api-admin)
  - [x] Update case balance (api-admin - automatic via transactions)
  - [ ] Generate payment receipts (can be added later)
  - [x] Payment allocation (principal vs fees) (api-admin - via CaseTransactionsService)
  - [x] Refund processing (api-admin)
  - [x] Payment history (api-admin)

### Case Notes
- [x] **Note management**
  - [x] Add case notes
  - [x] Timestamp tracking
  - [x] User attribution
  - [x] Note search
  - [ ] Note attachments (future enhancement)

### Arrangements
- [x] **Payment plan/schedule management**
  - [x] Create payment arrangements (api-admin)
  - [x] Update arrangement schedule (api-admin)
  - [x] Arrangement status management (ACTIVE, BROKEN, COMPLETED, CANCELLED) (api-admin)
  - [x] Schedule validation (api-admin)
  - [x] List arrangements with filtering (api-admin)

## 🔌 Phase 3: API Development (Priority 3)

### API Platform (Port 6310)
- [ ] **Platform endpoints**
  - [ ] Tenant management endpoints
  - [ ] Platform admin features
  - [ ] System configuration
  - [ ] User management across tenants

### API Admin (Port 6311)
- [x] **Admin endpoints** ✅ MOSTLY COMPLETE
  - [x] Case management endpoints (CRUD, search, filtering)
  - [x] Debtor management endpoints (CRUD, addresses, search)
  - [x] Client management endpoints (CRUD, search)
  - [x] Case transactions (charges, fees, interest, costs)
  - [x] Payment processing (record payments, refunds, allocation)
  - [x] Arrangements (payment plans/schedules)
  - [x] Case notes (add, list, search)
  - [x] User management (CRUD, roles, permissions)
  - [ ] Dashboard data endpoints (statistics, summaries)
  - [ ] Reporting endpoints (exports, analytics)

### API Client (Port 4312)
- [ ] **Client portal endpoints**
  - [ ] Case viewing (read-only for clients)
  - [ ] Payment submission
  - [ ] Client reports
  - [ ] Case status updates notifications

### API Debtor (Port 4313)
- [ ] **Debtor self-service endpoints**
  - [ ] Case lookup (by reference number)
  - [ ] Payment options
  - [ ] Payment processing
  - [ ] Communication with agency
  - [ ] Document access

### API Agent (Port 4314)
- [ ] **Mobile/field agent endpoints**
  - [ ] Case updates from field
  - [ ] Location tracking
  - [ ] Photo/document upload
  - [ ] Case notes from mobile
  - [ ] Offline capability (future)

## 🎨 Phase 4: Frontend Development (Priority 4)

### Platform Portal (Port 6300)
- [x] **Tenant Management UI** ✅ COMPLETE
  - [x] List tenants with pagination
  - [x] Create tenant form
  - [x] Edit tenant details
  - [x] Tenant status management
  - [x] Delete tenant functionality
  - [x] Dashboard with statistics and overview
  - [x] Beautiful sidebar navigation layout
  - [x] API Key management interface
  - [ ] Tenant user management (future)
  - [ ] Platform-level user management (future)

### Admin Portal (Port 6301)
- [ ] **Dashboard**
  - [ ] Overview statistics
  - [ ] Recent cases
  - [ ] Pending tasks
  - [ ] Charts and graphs

- [ ] **Case management UI**
  - [ ] Case list view
  - [ ] Case detail view
  - [ ] Create/edit case form
  - [ ] Case search and filters
  - [ ] Bulk operations

- [ ] **User management UI**
  - [ ] User list
  - [ ] User create/edit form
  - [ ] Role assignment
  - [ ] Permission management

- [ ] **Reports**
  - [ ] Case reports
  - [ ] Payment reports
  - [ ] Export functionality

### Client Portal (Port 4302)
- [ ] **Client dashboard**
  - [ ] Case overview
  - [ ] Payment summary
  - [ ] Recent activity

- [ ] **Case viewing**
  - [ ] Case list (client's cases)
  - [ ] Case detail view
  - [ ] Transaction history
  - [ ] Document access

- [ ] **Payment interface**
  - [ ] Payment form
  - [ ] Payment history
  - [ ] Receipt download

### Debtor Portal (Port 4303)
- [ ] **Case lookup**
  - [ ] Search by reference number
  - [ ] Case details view
  - [ ] Balance information

- [ ] **Payment options**
  - [ ] Payment form
  - [ ] Payment methods
  - [ ] Payment confirmation

- [ ] **Communication**
  - [ ] Contact form
  - [ ] Message history
  - [ ] Document access

## 🔒 Phase 5: Security & Compliance (Priority 5)

### Security Hardening
- [ ] **Input validation**
  - [ ] Request validation (DTOs)
  - [ ] SQL injection prevention
  - [ ] XSS protection
  - [ ] CSRF protection

- [ ] **API security**
  - [ ] Rate limiting
  - [ ] CORS configuration
  - [ ] API authentication guards
  - [ ] Request logging

- [ ] **Data protection**
  - [ ] Encryption at rest
  - [ ] Encryption in transit (HTTPS)
  - [ ] PII data handling
  - [ ] GDPR compliance features

### Audit & Compliance
- [ ] **Audit trails**
  - [ ] User action logging
  - [ ] Case change history
  - [ ] Payment audit logs
  - [ ] Access logging

## 🛠️ Phase 6: Infrastructure & Integration (Priority 6)

### File Storage
- [ ] **MinIO integration**
  - [ ] Document upload
  - [ ] Document download
  - [ ] Case attachments
  - [ ] File type validation
  - [ ] File size limits

### Email System
- [ ] **MailHog integration**
  - [ ] Email service setup
  - [ ] Password reset emails
  - [ ] Case notification emails
  - [ ] Payment confirmation emails
  - [ ] Email templates

### Caching
- [ ] **Redis integration**
  - [ ] Session management
  - [ ] Query result caching
  - [ ] Rate limiting storage
  - [ ] Cache invalidation strategy

### Logging
- [ ] **Structured logging**
  - [ ] Log levels configuration
  - [ ] Error tracking
  - [ ] Request/response logging
  - [ ] Log aggregation

## 🧪 Phase 7: Testing (Priority 7)

### Unit Tests
- [ ] **Service layer tests**
  - [ ] User service tests
  - [ ] Case service tests
  - [ ] Payment service tests
  - [ ] Transaction service tests

### Integration Tests
- [ ] **API endpoint tests**
  - [ ] Authentication tests
  - [ ] CRUD operation tests
  - [ ] Authorization tests
  - [ ] Error handling tests

### E2E Tests
- [ ] **Frontend tests**
  - [ ] User flows
  - [ ] Case creation flow
  - [ ] Payment flow
  - [ ] Login/logout flow

## 📊 Phase 8: Reporting & Analytics (Priority 8)

- [ ] **Reporting system**
  - [ ] Case reports
  - [ ] Payment reports
  - [ ] User activity reports
  - [ ] Export to CSV/PDF
  - [ ] Scheduled reports

- [ ] **Analytics**
  - [ ] Dashboard metrics
  - [ ] Performance tracking
  - [ ] Usage statistics

## 🚢 Phase 9: Deployment & DevOps (Priority 9)

- [ ] **CI/CD pipeline**
  - [ ] Automated testing
  - [ ] Build automation
  - [ ] Deployment scripts
  - [ ] Environment configuration

- [ ] **Monitoring**
  - [ ] Health checks
  - [ ] Performance monitoring
  - [ ] Error alerting
  - [ ] Uptime monitoring

## 📝 Notes

- Tasks are organized by priority (1 = highest, 9 = lowest)
- Each phase should be completed before moving to the next
- Security and testing should be integrated throughout development
- Version numbers should be incremented for each release

## Quick Start Development

1. **Start with Phase 1**: Database setup and authentication
2. **Build core features**: Cases, debtors, clients (Phase 2)
3. **Develop APIs**: Implement endpoints for each service (Phase 3)
4. **Build frontends**: Create user interfaces (Phase 4)
5. **Secure everything**: Add security and compliance (Phase 5)
6. **Integrate services**: File storage, email, caching (Phase 6)
7. **Test thoroughly**: Unit, integration, E2E tests (Phase 7)
8. **Add reporting**: Analytics and reporting features (Phase 8)
9. **Deploy**: CI/CD and monitoring (Phase 9)

---

## 📝 TODO List Maintenance

### How to Update This File

1. **When completing a task:**
   - Change `[ ]` to `[x]` in the markdown
   - Add completion date: `[x] (2025-12-11)`
   - Update the "Last Updated" date at bottom

2. **When starting a task:**
   - Change `[ ]` to `[🚧]` in the markdown
   - Add start date: `[🚧] (Started: 2025-12-11)`

3. **When adding new tasks:**
   - Add to appropriate phase section
   - Use consistent formatting
   - Include sub-tasks if needed

4. **When cancelling a task:**
   - Change `[ ]` to `[❌]` in the markdown
   - Add reason: `[❌] (Reason: No longer needed)`

### Sync with todo_write Tool

The `todo_write` tool manages tasks programmatically. This markdown file should reflect the same state. When updating:

1. Use `todo_write` tool for status changes
2. Update this markdown file to match
3. Commit both changes together

### Version Control

- Commit TODO updates with related code changes
- Use clear commit messages: "Complete task dev-1: Database setup"
- Review TODO list in PRs to ensure it's current

---

**Last Updated**: 2025-12-11  
**Current Version**: 0.0.2  
**Next Milestone**: Phase 1 - Foundation  
**Active Tasks**: Check `todo_write` tool for current in-progress tasks

