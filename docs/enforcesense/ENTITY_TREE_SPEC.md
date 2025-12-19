# EnforceSense Entity Tree Specification

**Version:** 2.0  
**Status:** MANDATORY - Canonical Model  
**Last Updated:** 2025-12-19

## Overview

This document defines the canonical entity tree for EnforceSense that supports:
- Multi-debt scenarios (one debtor with multiple debts)
- Multi-client scenarios (one debtor owes to multiple clients)
- Debt advice and vulnerability tracking
- Proper integration with Infometrix CRM (Customer/Account)

## Entity Tree

```
Tenant (Infometrix subscription owner)
└─ Account (Client/Creditor) [CRM core - Customer model]
   ├─ Contacts
   └─ Instructions / Matters (optional CRM view)
      └─ EnforceSense
         ├─ Party (Debtor) ← can be Individual or Organisation
         │  ├─ PartyDetails (addresses, phones, identifiers; may be partial)
         │  └─ PartySupportProfile (debt advice/vulnerability status)
         ├─ DebtAccount (1 per debt)
         │  ├─ principal / fees / interest rules
         │  ├─ references (invoice, contract, court ref, etc.)
         │  └─ clientAccountId (creditor)
         ├─ Case (workflow container)
         │  ├─ CaseDebts (links to 1..many Debt Accounts)
         │  ├─ Actions (visits, calls, trace, enforcement steps)
         │  ├─ Documents / Notices
         │  ├─ Ledger / Payments / Allocations
         │  └─ CaseSupportImpact (support status impact per case)
         └─ PortalAccess (Debtor Portal sessions, preferred language)
```

## Core Entities

### 1. Party (formerly Debtor)

**Purpose**: Represents a person or company that can have multiple roles (Debtor, JointDebtor, Guarantor, Director, etc.)

**Key Changes from Debtor**:
- Renamed to `Party` for neutrality
- Supports multiple roles via `PartyRole` enum
- Can be linked to multiple debts and cases

**Fields**:
- `id`, `tenant_id`
- `party_type`: `INDIVIDUAL` | `ORGANISATION`
- `legal_name` (required)
- `first_name`, `last_name` (for individuals)
- `date_of_birth` (optional - may be missing)
- `national_identifier` (optional)
- `company_registration_number` (for organisations)
- `trading_names` (JSON array)
- Contact details: `email`, `phone`
- `address_history` (JSON array)
- `language_preference` (ISO 639-1)
- `communication_preferences` (JSON)
- `external_references` (JSON)
- `ai_summary`
- Timestamps and soft delete

**Relationships**:
- `party_profile` (one-to-one) - Stable facts and preferences
- `party_flags` (one-to-one) - Boolean/enum signals
- `party_restrictions` (one-to-one) - Enforced rules
- `party_support_profile` (one-to-one) - Debt advice/vulnerability status
- `compliance_notes` (one-to-many) - Restricted detailed notes

**Relationships**:
- `party_support_profile` (one-to-one)
- `debt_accounts` (one-to-many)
- `case_roles` (many-to-many via PartyRole)

### 2. PartyRole

**Purpose**: Links a Party to a Case with a specific role

**Enum Values**:
- `DEBTOR`
- `JOINT_DEBTOR`
- `GUARANTOR`
- `DIRECTOR`
- `THIRD_PARTY`
- `VULNERABLE_PERSON` (flag/assessment)

**Fields**:
- `id`, `tenant_id`
- `party_id` (FK to Party)
- `case_id` (FK to Case)
- `role` (enum)
- `is_primary` (boolean)
- Timestamps

### 3. DebtAccount (new)

**Purpose**: Represents one debt = one record. Supports multiple debts per debtor.

**Key Features**:
- One debt = one record
- Links to Client Account (creditor) via `client_account_id`
- Links to Debtor Party via `debtor_party_id`
- Contains principal, fees, interest rules, references

**Fields**:
- `id`, `tenant_id`
- `client_account_id` (FK to Customer/Account in CRM)
- `debtor_party_id` (FK to Party)
- `debt_reference` (unique within tenant)
- `client_reference` (client's own reference)
- `invoice_reference` (optional)
- `contract_reference` (optional)
- `court_reference` (optional)
- `principal_amount` (Numeric)
- `fees_charged` (Numeric)
- `interest_rate` (Numeric, optional)
- `interest_calculation_method` (enum)
- `due_date` (DateTime)
- `debt_type` (enum: INVOICE, JUDGMENT, CONTRACT, etc.)
- `status` (enum: ACTIVE, SETTLED, WRITTEN_OFF, etc.)
- `notes` (Text)
- Timestamps and soft delete

**Relationships**:
- `client_account` (many-to-one to Customer)
- `debtor_party` (many-to-one to Party)
- `case_debts` (many-to-many via CaseDebts)

### 4. Case (EnforcementCase)

**Purpose**: Workflow container that can link to one or more Debt Accounts

**Key Changes**:
- Remove direct `debtor_id` and `client_id` (use relationships via CaseDebts)
- Support multiple debts via `CaseDebts` join table
- Add `CaseSupportImpact` relationship

**Fields**:
- `id`, `tenant_id`
- `case_reference` (unique within tenant)
- `case_type` (enum)
- `status` (enum)
- `legal_basis` (Text)
- `enforcement_stage` (String)
- `assigned_agent` (FK to User)
- Financial totals (derived from transactions)
- `notes`, `communications` (JSON)
- `visits`, `actions`, `notices` (JSON)
- `risk_flags` (JSON)
- `ai_summary`
- `opened_date`, `closed_date`
- Timestamps and soft delete

**Relationships**:
- `case_debts` (one-to-many to CaseDebts)
- `transactions` (one-to-many to CaseTransaction)
- `notes` (one-to-many to CaseNote)
- `support_impacts` (one-to-many to CaseSupportImpact)
- `party_roles` (many-to-many to Party via PartyRole)

### 5. CaseDebts (new)

**Purpose**: Join table linking a Case to one or more Debt Accounts

**Key Features**:
- Supports 1:1 and 1:many relationships
- Allows partial allocation
- Priority order for multiple debts

**Fields**:
- `id`, `tenant_id`
- `case_id` (FK to Case)
- `debt_account_id` (FK to DebtAccount)
- `allocation_percentage` (Numeric, 0-100, optional)
- `allocation_amount` (Numeric, optional)
- `priority_order` (Integer, for ordering)
- `is_primary` (boolean)
- `notes` (Text)
- Timestamps

**Relationships**:
- `case` (many-to-one)
- `debt_account` (many-to-one)

### 6. PartySupportProfile (new)

**Purpose**: Track debt advice and vulnerability status at Party level (applies across all debts/cases)

**Key Features**:
- One profile per Party
- Applies to all debts/cases for that Party
- Supports evidence and documents
- Time-bound status changes

**Fields**:
- `id`, `tenant_id`
- `party_id` (FK to Party, unique)
- `support_status` (enum):
  - `NONE`
  - `ADVICE_SOUGHT` (told you they're seeking advice)
  - `ADVISOR_ENGAGED` (StepChange/CAB engaged)
  - `FORMAL_SOLUTION_PENDING` (DRO/IVA/bankruptcy application)
  - `FORMAL_SOLUTION_ACTIVE` (IVA/DRO/Bankruptcy active)
- `advisor_org` (enum/free text): StepChange / CAB / National Debtline / "Other"
- `reference_number` (optional)
- `effective_from`, `effective_to` (DateTime, optional)
- `evidence_level` (enum): `SELF_REPORTED`, `ADVISOR_CONFIRMED`, `DOCUMENTED`
- `notes` (internal)
- `documents` (JSON array of document links)
- `last_verified_at`, `next_review_at` (DateTime)
- Timestamps

**Relationships**:
- `party` (one-to-one)

### 7. CaseSupportImpact (new)

**Purpose**: Track support status impact per case (audit trail)

**Key Features**:
- Records what action was taken when support status changed
- Provides auditability for compliance
- Links to PartySupportProfile

**Fields**:
- `id`, `tenant_id`
- `case_id` (FK to Case)
- `party_id` (FK to Party)
- `support_status_at_time` (copied from PartySupportProfile)
- `action_taken` (enum):
  - `HOLD`
  - `REDUCE_CONTACT`
  - `REFER_TO_COMPLIANCE`
  - `REQUEST_AUTHORITY`
  - `CONTINUE_ALLOWED`
- `hold_until` (DateTime, optional)
- `reason_code` (enum): `DEBT_ADVICE`, `BREATHING_SPACE`, `MEDICAL`, etc.
- `created_by` (FK to User)
- `notes` (Text)
- Timestamps

**Relationships**:
- `case` (many-to-one)
- `party` (many-to-one)

## Integration with CRM (Customer/Account)

### Linking EnforcementClient to Customer

**Current State**: `EnforcementClient` is a separate entity

**Required Change**: Link `EnforcementClient` to CRM `Customer` model

**Options**:
1. **Option A (Recommended)**: Add `customer_id` FK to `EnforcementClient`
   - `EnforcementClient.customer_id` → `Customer.id`
   - EnforcementClient becomes an extension/enrichment of Customer
   - Allows CRM features (contacts, interactions) to work with enforcement clients

2. **Option B**: Replace `EnforcementClient` entirely with `Customer`
   - Use Customer model directly
   - Add enforcement-specific fields to Customer
   - Simpler but may pollute CRM model

**Recommended Implementation**: Option A
- Add `customer_id` to `EnforcementClient`
- Make it optional initially (backward compatibility)
- Update `DebtAccount.client_account_id` to reference `Customer.id` directly
- Keep `EnforcementClient` for enforcement-specific settings

## Multi-Debt Support

### How "One Debtor with Multiple Debts" Works

1. **One Party** can have many **DebtAccounts**
2. Each **DebtAccount** can be pursued:
   - In its own **Case** (1:1 relationship via CaseDebts)
   - Grouped into a single **Case** via CaseDebts links (1:many)

### Example Scenarios

**Scenario 1**: Debtor owes multiple invoices to same client
- Party: "John Smith"
- DebtAccount 1: Invoice #123, £500
- DebtAccount 2: Invoice #456, £300
- Case 1: Links to both DebtAccount 1 and DebtAccount 2 (consolidated enforcement)

**Scenario 2**: Debtor owes debts to multiple clients
- Party: "John Smith"
- DebtAccount 1: Client A, Invoice #123, £500
- DebtAccount 2: Client B, Invoice #789, £200
- Case 1: Links to DebtAccount 1
- Case 2: Links to DebtAccount 2

## Support Status Workflow

### When PartySupportProfile Changes

**Automation Rules** (when status changes to `ADVISOR_ENGAGED`):

1. For all open cases linked to `party_id`:
   - Create `CaseSupportImpact` entry
   - Apply policy:
     - Soft hold (stop outbound calls/visits)
     - Route to Compliance review
     - Restrict certain enforcement actions

2. For all open debts for that party:
   - Mark as `debtor_support_flag = true` (derived)
   - Show banner on every case/debt UI

**UI Behavior**:
- Show prominent banner: "Debt advice engaged: StepChange (self-reported/confirmed) — Effective from [date]"
- Quick actions (permissioned):
  - "Place hold on all open cases"
  - "Place hold on this case only"
  - "Request advisor confirmation"
  - "Set review date"

**Compliance Nuance**:
- Don't hardcode "Stop everything forever"
- Implement policy-based controls:
  - Default: reduce contact + compliance review + time-bound hold
  - Allow override with reason + audit trail

## Migration Strategy

### Phase 1: Add New Models (Non-Breaking)
1. Create `Party` model (copy from `Debtor`)
2. Create `DebtAccount` model
3. Create `CaseDebts` model
4. Create `PartySupportProfile` model
5. Create `CaseSupportImpact` model
6. Create `PartyRole` model

### Phase 2: Link to CRM
1. Add `customer_id` to `EnforcementClient`
2. Update `DebtAccount.client_account_id` to reference `Customer.id`

### Phase 3: Migrate Data
1. Migrate `Debtor` → `Party`
2. Create `DebtAccount` records from existing `Case` financial data
3. Create `CaseDebts` links
4. Migrate vulnerability data to `PartySupportProfile`

### Phase 4: Update APIs
1. Update all endpoints to use new models
2. Add new endpoints for support status management
3. Update frontend to use new structure

### Phase 5: Deprecate Old Models
1. Mark old `Debtor` model as deprecated
2. Remove after migration complete

## Minimum "Must-Have" Flags (Phase 1 Implementation)

If implementing flags incrementally, prioritize these 8 essential flags:

1. **Preferred language + interpreter required** (PartyProfile)
2. **Preferred contact method + "no call"** (PartyProfile + PartyFlags)
3. **Vulnerability indicator** (category + review date) (PartyFlags)
4. **Debt advice engaged** (StepChange etc.) + evidence level (PartySupportProfile)
5. **Breathing Space / insolvency status** (simple enum + dates) (PartySupportProfile)
6. **Dispute raised** (enum) (PartyFlags)
7. **Safety risk** (none/caution/high) + no-visit flag (PartyFlags)
8. **Identity confidence** (low/med/high) + address verified/unverified (PartyProfile)

Everything else can be added in later phases.

## Design Rules for Sensitive Data

**CRITICAL**: Don't store sensitive vulnerability details in free text everywhere.

**Do**:
- Use structured categories + evidence level + review date
- Keep detailed notes in restricted "Compliance Notes" area with tighter permissions + audit trail
- Separate PartyProfile (stable facts), PartyFlags (signals), PartyRestrictions (rules)

**Don't**:
- Store detailed vulnerability notes in Party model directly
- Allow all users to see sensitive compliance details
- Mix operational flags with sensitive personal information

## Naming Conventions

**Internal (Code/DB)**: Use Naming Set 1 (neutral)
- Account = Client (CRM Customer)
- Party = Party
- DebtAccount = DebtAccount
- Case = Case
- CaseDebts = CaseDebts
- Ledger = Ledger

**UI Labels**: Allow per-module/industry customization
- "Debt Account" can be labeled as "Claim", "Matter", "Instruction" in UI
- "Party" can be labeled as "Debtor", "Respondent" in UI

## Database Schema Changes

### New Tables
1. `parties` (rename from `debtors`)
2. `party_roles`
3. `debt_accounts`
4. `case_debts`
5. `party_profiles` (stable facts and preferences)
6. `party_flags` (boolean/enum signals)
7. `party_restrictions` (enforced rules)
8. `party_support_profiles` (debt advice/vulnerability)
9. `compliance_notes` (restricted detailed notes)
10. `case_support_impacts`

### Modified Tables
1. `enforcement_clients` (add `customer_id` FK)
2. `enforcement_cases` (remove direct `debtor_id`, `client_id` - use via CaseDebts)

### Deprecated Tables
1. `debtors` (after migration to `parties`)

## API Changes

### New Endpoints
- `GET /parties` (replaces `/debtors`)
- `POST /parties`
- `GET /debt-accounts`
- `POST /debt-accounts`
- `GET /cases/{case_id}/debts`
- `POST /cases/{case_id}/debts`
- `GET /parties/{party_id}/support-profile`
- `POST /parties/{party_id}/support-profile`
- `GET /cases/{case_id}/support-impact`
- `POST /cases/{case_id}/support-impact`

### Modified Endpoints
- `GET /cases` (now returns cases with linked debts)
- `POST /cases` (now accepts debt account IDs)
- All debtor endpoints → party endpoints

## Frontend Changes

### New Components
- Party management (replaces Debtor management)
- Debt Account management
- Support Status banner component
- Support Status management UI
- Case Debts linking UI

### Modified Components
- Case detail view (show linked debts)
- Case creation (link to debt accounts)
- Party detail view (show all debts, support status)

