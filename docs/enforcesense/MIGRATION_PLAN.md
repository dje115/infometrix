# EnforceSense Model Migration Plan

**Version:** 1.0  
**Status:** Implementation Plan  
**Last Updated:** 2025-12-19

## Overview

This document outlines the step-by-step migration from the current EnforceSense model to the new canonical model that supports multi-debt, multi-client scenarios and proper CRM integration.

## Current State

### Current Models
- `Debtor` (person/company that owes money)
- `EnforcementClient` (creditor/instructing organisation)
- `EnforcementCase` (1:1 with Debtor and Client)
- `CaseTransaction` (ledger entries)
- `CaseNote` (agent notes)

### Current Limitations
- One Case = One Debt (no multi-debt support)
- No link to CRM Customer/Account
- Vulnerability tracking at Debtor level only (no support status workflow)
- No debt advice tracking

## Target State

### New Models
- `Party` (replaces Debtor, supports multiple roles)
- `PartyRole` (links Party to Case with role)
- `DebtAccount` (one debt = one record)
- `CaseDebts` (join table: Case → Debt Accounts)
- `PartySupportProfile` (debt advice/vulnerability at Party level)
- `CaseSupportImpact` (support status impact per case)
- `EnforcementClient` (linked to CRM Customer)

### New Capabilities
- Multi-debt support (one Party, many DebtAccounts)
- Multi-client support (one Party, debts to multiple Clients)
- Consolidated enforcement (one Case, many DebtAccounts)
- Debt advice tracking with automation
- CRM integration (link to Customer/Account)

## Migration Phases

### Phase 1: Add New Models (Non-Breaking) ✅ TODO

**Goal**: Create new models alongside existing ones without breaking current functionality

**Tasks**:
1. Create `Party` model (copy structure from `Debtor`)
2. Create `PartyRole` model
3. Create `DebtAccount` model
4. Create `CaseDebts` model
5. Create `PartySupportProfile` model
6. Create `CaseSupportImpact` model
7. Create database migrations for new tables
8. Add new API endpoints (alongside existing ones)

**Acceptance Criteria**:
- All new models created and tested
- Database migrations run successfully
- New API endpoints return empty results (no data yet)
- Existing functionality unchanged

### Phase 2: Link to CRM ✅ TODO

**Goal**: Connect EnforcementClient to CRM Customer model

**Tasks**:
1. Add `customer_id` FK to `EnforcementClient` model
2. Create migration to add column (nullable initially)
3. Update `EnforcementClient` API to accept `customer_id`
4. Add lookup endpoint: `GET /clients/{id}/customer` (returns CRM Customer)
5. Update UI to show CRM Customer link

**Acceptance Criteria**:
- EnforcementClient can be linked to Customer
- API endpoints support customer_id
- UI shows customer link when available
- Backward compatible (customer_id optional)

### Phase 3: Data Migration ✅ TODO

**Goal**: Migrate existing data to new structure

**Tasks**:
1. Create migration script to:
   - Copy `Debtor` → `Party`
   - Create `DebtAccount` from `Case` financial data
   - Create `CaseDebts` links (1:1 initially)
   - Create `PartyRole` entries (DEBTOR role)
   - Migrate vulnerability data to `PartySupportProfile`
2. Run migration in test environment
3. Verify data integrity
4. Run migration in production

**Acceptance Criteria**:
- All existing data migrated successfully
- Data integrity verified
- No data loss
- Rollback plan tested

### Phase 4: Update APIs ✅ TODO

**Goal**: Update all endpoints to use new models

**Tasks**:
1. Update `GET /debtors` → `GET /parties`
2. Update `POST /debtors` → `POST /parties`
3. Add `GET /debt-accounts` endpoint
4. Add `POST /debt-accounts` endpoint
5. Update `GET /cases` to include linked debts
6. Update `POST /cases` to accept debt account IDs
7. Add `GET /parties/{id}/support-profile` endpoint
8. Add `POST /parties/{id}/support-profile` endpoint
9. Add support status automation triggers
10. Update all frontend API calls

**Acceptance Criteria**:
- All endpoints updated and tested
- Frontend works with new endpoints
- Support status automation works
- Backward compatibility maintained (old endpoints deprecated but functional)

### Phase 5: Update Frontend ✅ TODO

**Goal**: Update UI to use new model structure

**Tasks**:
1. Rename "Debtors" to "Parties" in UI
2. Add Debt Account management UI
3. Update Case creation to link debt accounts
4. Update Case detail to show linked debts
5. Add Support Status banner component
6. Add Support Status management UI
7. Update Party detail to show all debts
8. Add automation rule configuration UI

**Acceptance Criteria**:
- UI reflects new model structure
- All features work with new models
- Support status workflow visible and functional
- User experience improved

### Phase 6: Deprecate Old Models ✅ TODO

**Goal**: Remove old models after migration complete

**Tasks**:
1. Mark old endpoints as deprecated
2. Add deprecation warnings to API responses
3. Monitor usage of old endpoints
4. Remove old endpoints after grace period
5. Drop old database tables
6. Remove old model code

**Acceptance Criteria**:
- Old endpoints removed
- Old tables dropped
- Codebase cleaned up
- Documentation updated

## Implementation Order

### Week 1: Foundation
- Phase 1: Add new models
- Phase 2: Link to CRM

### Week 2: Migration
- Phase 3: Data migration
- Testing and verification

### Week 3: Integration
- Phase 4: Update APIs
- Phase 5: Update frontend (partial)

### Week 4: Completion
- Phase 5: Update frontend (complete)
- Phase 6: Deprecate old models

## Risk Mitigation

### Data Loss Prevention
- Full database backup before migration
- Test migration on copy of production data
- Rollback plan documented and tested
- Gradual rollout (test → staging → production)

### Backward Compatibility
- Keep old endpoints during transition
- Version API endpoints (`/api/v1/` vs `/api/v2/`)
- Feature flags for new vs old models
- Gradual migration of frontend

### Testing Strategy
- Unit tests for new models
- Integration tests for new endpoints
- End-to-end tests for critical workflows
- Performance tests for multi-debt scenarios

## Success Metrics

- ✅ All new models created and tested
- ✅ CRM integration working
- ✅ Multi-debt scenarios supported
- ✅ Support status workflow functional
- ✅ Zero data loss during migration
- ✅ All existing features still work
- ✅ Performance maintained or improved

