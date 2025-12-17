# EnforceSense Core Domain Model

**Version:** 1.0  
**Status:** MANDATORY - Non-negotiable specification  
**Last Updated:** 2025-12-13

## Overview

This document defines the canonical, non-negotiable domain model for EnforceSense. It applies to schemas, APIs, AI, accounting, portals, SAR, reporting, and analytics.

**This is our #1 competitive differentiator** - the correct domain model puts EnforceSense ahead of 90% of the enforcement market.

---

## 1. CORE PRINCIPLE (MANDATORY)

EnforceSense MUST model enforcement using THREE distinct core entities:

1. **Debtor** – the real-world person OR legal entity that owes money
2. **Client** – the creditor or instructing organisation
3. **Case** – a single enforcement instruction linking ONE Debtor to ONE Client

### Rules

- A Debtor MAY owe money to multiple Clients
- A Debtor MUST NOT be duplicated per Client or per Case
- All financial, legal, and enforcement activity belongs to the Case, NOT the Debtor
- Cases are legally and financially independent even when the Debtor is shared

---

## 2. DEBTOR (PERSON OR LEGAL ENTITY)

A Debtor represents a unique real-world entity within a tenant.

### Entity Types

A Debtor MAY be:
- A **natural person** (`PERSON`)
- A **legal entity** (`COMPANY`) - company, partnership, trust, organisation

### Identity Data (Flexible)

The system MUST NOT assume:
- A Debtor is always a person
- A date of birth exists
- A national identifier exists
- A company registration number exists

Debtor identity data MAY be partial, evolving, or incomplete.

### Valid Examples

- Individual with name + address only
- Individual with name + phone/email only
- Company with trading name + address only
- Company with Companies House number but no trading address
- Debtor identified initially only by a client reference

### Debtor-Level Data (Shared Context)

Debtor-level data represents identity and shared context across all cases.

**Typical attributes** (all optional unless stated):

- `entityType`: `PERSON` | `COMPANY` (required)
- `legalName`: Full legal name (for both PERSON and COMPANY)
- `firstName`, `lastName`: Required for PERSON, optional for COMPANY
- `tradingNames`: Array of trading names/aliases
- `companyRegistrationNumber`: For companies (e.g., Companies House number)
- `nationalIdentifier`: NI number, passport, etc.
- Contact details: `email`, `phone`
- `dateOfBirth`: For persons
- Address history: Multiple addresses per debtor
- `languagePreference`: ISO 639-1 code (e.g., "en", "es", "pl")
- `communicationPreferences`: Preferred channels, times, etc.
- Vulnerability indicators: `isVulnerable`, `vulnerabilityNotes` (PERSON only typically)
- `riskFlags`: Non-financial risk indicators
- `externalReferences`: UPRN, client refs, etc.

### Rules

- Debtor-level data is shared across ALL cases
- Debtor-level data MUST NOT include balances, fees, or enforcement stages
- Uniqueness is enforced PER TENANT ONLY
- No cross-tenant debtor linkage

---

## 3. CLIENT (CREDITOR)

A Client represents the instructing organisation.

### Rules

- Clients MAY have many Cases
- Clients MAY have many Debtors
- Clients MUST NOT own debtor identity
- Clients are tenant-scoped

---

## 4. CASE (ENFORCEMENT INSTRUCTION)

A Case represents ONE legal/enforcement instruction.

### Structure

Each Case:
- Belongs to EXACTLY ONE Debtor
- Belongs to EXACTLY ONE Client
- Has a unique reference number within the tenant

### Case-Level Data

Case-level data includes:
- Client references
- Legal basis and case type
- Enforcement stage/status
- **Financial balances and fees** (all financial data is at Case level)
- Payments and allocations
- Visits, actions, notices
- Case-specific notes and communications
- Case-level risk flags
- Audit events and timelines

### Financial Independence

Cases are legally and financially independent even when the Debtor is shared.

**CRITICAL:** All monetary movement is recorded in a **Case Ledger** (`CaseTransaction`). No monetary totals are stored at Debtor level.

---

## 5. ACCOUNTING & LEDGER MODEL

Accounting MUST align to the Case model.

### Rules

- All monetary movement is recorded in a **Case Ledger** (`CaseTransaction`)
- No monetary totals are stored at Debtor level
- Financial entities reference `caseId`, NOT `debtorId`

### Recommended Entities

- `CaseTransaction` (immutable ledger entry)
- `Payment` (incoming funds, references `caseId`)
- `Allocation` (payment → case transaction mapping)
- `Fee` (generated per case event)

### Optional Features

- Cross-case payment allocation (explicit and auditable)
- Client remittance reporting
- Export to accounting systems (Xero, Sage, etc.)

---

## 6. DEBTOR DE-DUPLICATION STRATEGY

Because strong identifiers may be missing, EnforceSense MUST support **probabilistic de-duplication**, not strict matching.

### Allowed Matching Signals

- Name similarity
- Address similarity
- Phone/email matches
- Company name similarity
- Client-provided references

### Rules

- De-duplication MUST be advisory, not automatic
- Staff must confirm merges
- Merges must be fully audited and reversible
- AI MAY assist by suggesting potential matches but MUST NOT auto-merge

---

## 7. VULNERABILITY HANDLING

Vulnerability is Debtor-level context but MAY have Case-level relevance.

### Rules

- Vulnerability indicators live at Debtor level (`isVulnerable`, `vulnerabilityNotes`)
- Case-level flags may reference vulnerability context
- AI may assist in identifying indicators but MUST NOT assign vulnerability autonomously
- All vulnerability data must be auditable and access-controlled
- Typically applies to PERSON entities only

---

## 8. AI ALIGNMENT (MANDATORY)

AI features MUST respect this domain model.

### Rules

- AI summaries may exist at:
  - Debtor level (identity/context summary)
  - Case level (legal/enforcement summary)
- AI outputs MUST reference Case IDs explicitly
- AI MUST NOT merge or confuse data across cases or clients
- Original data is immutable; AI produces derived artifacts only

---

## 9. SAR & GDPR HANDLING (MANDATORY)

SAR generation MUST:

- Return ONE Debtor record
- Include ALL Cases linked to that Debtor (within tenant)
- Include all communications, notes, documents, and AI outputs
- Maintain a clear structure separating Debtor data from Case data

### Right to Rectification

- Updates to Debtor identity propagate across all cases
- No duplicated debtor records permitted

### SAR Model

- `SarRequest` MUST have `debtorId` (required)
- `SarRequest` MUST NOT have `caseId` (SAR is debtor-level only)
- Data bundle includes all cases for the debtor

---

## 10. API & UI IMPLICATIONS

### APIs

- **Debtor APIs**: Expose identity/context only
- **Case APIs**: Expose enforcement and financial data
- Cross-case aggregation is read-only and auditable

### UI

- **Debtor Portal**:
  - Single login
  - Multiple cases visible
  - Clear separation by Client
- **Staff UI**:
  - Debtor profile with linked cases
  - Case detail screens remain independent

---

## 11. MULTI-TENANCY RULES

- Debtor uniqueness is enforced PER TENANT ONLY
- No cross-tenant debtor linkage
- All access strictly tenant-scoped

---

## 12. PRISMA / SCHEMA DESIGN GUIDANCE

When implementing schemas (e.g., Prisma):

- `Debtor` is a top-level entity
- `Case` has a required `debtorId` and `clientId` (via `clientOrganisationId`)
- Financial tables reference `caseId`, NOT `debtorId`
- Avoid nullable foreign keys that allow bypassing this structure

### Current Schema Alignment

✅ **Correct:**
- `Payment` references `caseId`
- `CaseTransaction` references `caseId`
- `Arrangement` references `caseId`
- `Case` references `debtorId` and `clientOrganisationId`

---

## 13. ENFORCEMENT RULES FOR AI DEVELOPMENT AGENT

The AI development agent MUST:

- Treat Debtor as the canonical identity (person OR company)
- Treat Case as the canonical unit of enforcement and finance
- Never duplicate Debtors per Client or Case
- Never assume completeness of identity data
- Ensure accounting, AI, SAR, portals, and reporting respect this separation

---

## 14. COMPETITIVE ADVANTAGE

This domain model is EnforceSense's **#1 competitive differentiator**:

- Most competitors model accounts, not people
- Most competitors duplicate debtors per client
- Most competitors make SAR generation complex and error-prone
- EnforceSense's correct model makes SARs, portals, AI, and accounting sane

**Market Impact:** This alone puts EnforceSense ahead of 90% of the enforcement market.

---

## Related Documents

- [Competitive Analysis](./COMPETITIVE_ANALYSIS.md) - Market positioning
- [Implementation Plan](./IMPLEMENTATION_PLAN.md) - Architecture and deployment
- [AI Integration Specification](./AI_INTEGRATION_SPEC.md) - AI capabilities


