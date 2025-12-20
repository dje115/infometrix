# Fee Transparency & Compliance Specification

**Version:** 1.0  
**Status:** MANDATORY - UK Legal & Regulatory Requirement  
**Last Updated:** 2025-12-19

## Overview

Fee transparency is **legally required** in UK debt recovery/enforcement. This document defines when fees must be transparent, who can see them, and how to implement this cleanly in Infometrix/EnforceSense.

**CRITICAL PRINCIPLE**: If a fee changes what the debtor owes, it must be transparent to the debtor. If it affects what the client receives, it must be transparent to the client. Internally, everything must always be transparent.

## 1. When Fees MUST Be Transparent (UK)

### A) When Fees Are Charged to the Debtor

This is the **highest-risk area**.

#### 1. Enforcement Fees (Bailiff / Enforcement Agent)

If fees are recoverable from the debtor, transparency is **mandatory**.

**Examples**:
- Compliance stage fee
- Enforcement visit fee
- Sale stage fee
- Court fees passed through

**Legal Basis**:
- Taking Control of Goods (Fees) Regulations 2014
- Tribunals, Courts and Enforcement Act 2007

**Requirements**:
- Fees must be:
  - Clearly itemised
  - Charged only when the stage is legitimately reached
  - Explained to the debtor
- Debtors are entitled to:
  - A breakdown of fees
  - Justification of each fee
  - The statutory basis

**➡️ You must show these to the debtor** (letters, portal, notices).

#### 2. Where Fees Affect the Debtor's Balance

Even if fees are technically paid by the client, if they change the debtor's total balance, they must be transparent.

**Example**: "Total owed" increases due to fees or interest.

**This means**:
- Debtor portal must show:
  - Principal
  - Interest
  - Recoverable fees
  - Payments and allocations

### B) When Fees Are Charged to the Client

Different rules apply, but transparency is still required.

#### 3. Contractual Transparency to the Client

Clients must always be able to see:
- What fees were charged
- How they were calculated
- When they were triggered

**This is required for**:
- Contract enforceability
- Audit
- VAT
- Disputes

**➡️ Client statements must show fees clearly**, even if the debtor never sees them.

#### 4. When Fees Are Deducted from Recoveries

If you deduct your fees before paying the client:

**Example**:
- Debtor pays £1,000
- Fee £200
- Client receives £800

**You must show**:
- Gross recovery
- Fee deducted
- Net remitted

Failing to do this is a common source of disputes.

### C) Regulatory & Compliance Triggers

#### 5. FCA / Vulnerability Context

If a debtor is vulnerable, in breathing space, or under debt advice:

**You must be able to demonstrate**:
- No inappropriate fees were charged
- Fees were paused or handled correctly

**This requires internal transparency**, even if not all details are shown to the debtor.

#### 6. Court Scrutiny

If enforcement actions are challenged:

**Courts may require**:
- Full fee breakdown
- Timing
- Statutory basis
- Payment allocation order

**Your system must be able to reconstruct this exactly.**

### D) Accounting, VAT, and Audit

#### 7. VAT Transparency

Where VAT applies:

**Client invoices must show**:
- Net fee
- VAT
- Gross

Debtor recoverable fees may have different VAT treatment.

**➡️ Never hide VAT inside totals.**

#### 8. Trust / Client Account Rules

If you hold money on behalf of clients:

**You must be able to show**:
- What money is client money
- What money is your fee
- When ownership transfers

**This requires ledger-level transparency**, even if UI abstracts it.

## 2. When Fees Should NOT Be Shown to the Debtor

**Important distinction**: Internal or client-only fees.

**Examples**:
- Client subscription fees
- Non-recoverable admin fees
- Platform usage fees
- Reporting or tracing charges not passed on

**These**:
- ❌ Must NOT appear in debtor-facing views
- ❌ Must NOT inflate debtor balances
- ✅ Appear only in client statements/invoices

## 3. Fee Classification Model

### 3.1 FeeDefinition (Mandatory Metadata)

Every fee must declare the following fields at creation time (rule-driven or manual):

**Fields**:
- `fee_id`
- `name`
- `fee_category` (enum):
  - `ENFORCEMENT_STATUTORY` - Statutory enforcement fees
  - `CLIENT_SERVICE` - Client service fees
  - `DISBURSEMENT` - Disbursements
  - `INTEREST` - Interest charges
  - `PLATFORM` - Platform/SaaS fees
- `who_pays` (enum):
  - `DEBTOR` - Debtor pays
  - `CLIENT` - Client pays
- `is_recoverable` (boolean) - Can be recovered from debtor
- `is_debtor_visible` (boolean) - Must appear in debtor statements
- `vat_applicable` (boolean)
- `legal_basis` (String/enum) - e.g., "Taking Control of Goods (Fees) Regs 2014"
- `calculation_method` (enum):
  - `FIXED` - Fixed amount
  - `PERCENTAGE` - Percentage of amount
  - `STAGE_TRIGGERED` - Triggered by case stage
- `trigger_event` (enum):
  - `CASE_STAGE_CHANGE` - When case reaches stage
  - `PAYMENT_RECEIVED` - When payment received
  - `MANUAL` - Manually applied
- `effective_from`, `effective_to` (DateTime)

**❗ Hard Rule**: If `is_debtor_visible = true`, the fee must:
- Appear in debtor statements
- Affect debtor balance
- Be challengeable

### 3.2 Fee Visibility Matrix (System-Enforced)

| Fee Type | Debtor Portal | Client Portal | Internal |
|----------|---------------|---------------|----------|
| Statutory enforcement fees | ✅ | ✅ | ✅ |
| Interest | ✅ | ✅ | ✅ |
| Client service fees | ❌ | ✅ | ✅ |
| Platform / SaaS fees | ❌ | ❌ | ✅ |
| Disbursements (recoverable) | ✅ | ✅ | ✅ |
| Disbursements (client-only) | ❌ | ✅ | ✅ |

**Visibility is derived, not manually toggled.**

## 4. Permission Matrix

### 4.1 Roles (Example Baseline)

- **Platform Admin** - Full access
- **Finance** - Financial operations
- **Case Officer** - Case management
- **Compliance** - Compliance review
- **Client User** - Client portal access
- **Debtor (Portal)** - Debtor portal access

### 4.2 Permissions Table (Key Actions)

| Action | Admin | Finance | Case Officer | Compliance | Client | Debtor |
|--------|-------|---------|--------------|------------|--------|--------|
| View all fees | ✅ | ✅ | ⚠️ Case only | ✅ | ⚠️ Own cases | ⚠️ Debtor-visible only |
| Create fees | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ |
| Apply statutory fee | ❌ | ❌ | ⚠️ Rule-triggered | ⚠️ Review | ❌ | ❌ |
| Override fee | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| View ledger | ✅ | ✅ | ⚠️ Case | ⚠️ Case | ⚠️ Client | ⚠️ Own |
| Challenge fee | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ |
| Resolve fee challenge | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |
| Approve enforcement after vulnerability | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ |

**⚠️ = restricted / scoped**

## 5. Reporting & Statements

### 5.1 Debtor Statement (Portal + PDF)

**Purpose**: Legal transparency  
**Scope**: Per debtor, per case (or consolidated if allowed)

**Must Show**:
- Case reference
- Client name
- Opening balance
- Breakdown:
  - Principal
  - Interest
  - Statutory enforcement fees (itemised)
  - Payments received
  - Allocation of payments
- Closing balance
- Contact & challenge instructions

**Must NOT Show**:
- Client-only fees
- Platform fees
- Internal notes

**Derived from**: Ledger entries filtered by `is_debtor_visible = true`

### 5.2 Client Statement (Monthly / On Demand)

**Purpose**: Commercial + VAT + audit

**Shows**:
- Debts instructed
- Recoveries (gross)
- Fees charged (itemised)
- VAT breakdown
- Disbursements
- Net remitted
- Trust balance movements

**Derived from**: Ledger entries:
- `DEBTOR_PAYMENT`
- `FEE_EARNED`
- `CLIENT_PAYOUT`

### 5.3 Internal Trust & Compliance Reports

#### Trust Reconciliation
- Client money held
- Unallocated funds
- Aged balances
- Pending payouts

#### Fee Justification Report
- Fee
- Rule used
- Trigger
- Legal basis
- Evidence reference
- User/system that applied it

## 6. Fee Challenge Workflow (Debtor-Initiated)

### 6.1 When a Challenge Can Be Raised

**Debtor may challenge**:
- Statutory enforcement fees
- Interest
- Allocation order
- Duplicated or incorrect fees

**Debtor cannot challenge**:
- Client service fees
- Platform fees

### 6.2 Challenge Entity

**FeeChallenge Model**:

**Fields**:
- `id` (challengeId)
- `tenant_id`
- `fee_id` (FK to LedgerEntry, type=FEE_EARNED)
- `case_id` (FK to Case)
- `debtor_party_id` (FK to Party)
- `reason_code` (enum):
  - `INCORRECT_AMOUNT` - Fee amount is wrong
  - `WRONG_STAGE` - Fee applied at wrong stage
  - `NOT_INCURRED` - Fee not actually incurred
  - `VULNERABILITY` - Fee inappropriate due to vulnerability
  - `OTHER` - Other reason
- `description` (Text) - Debtor's explanation
- `submitted_at` (DateTime)
- `status` (enum):
  - `OPEN` - Challenge submitted
  - `UNDER_REVIEW` - Being reviewed
  - `UPHELD` - Challenge accepted
  - `REJECTED` - Challenge rejected
- `resolved_by` (FK to User, nullable)
- `resolved_at` (DateTime, nullable)
- `resolution_notes` (Text, nullable)
- `documents` (JSON array) - Supporting documents
- Timestamps

**Relationships**:
- `fee_entry` (many-to-one to LedgerEntry)
- `case` (many-to-one)
- `debtor_party` (many-to-one)
- `resolved_by_user` (many-to-one, optional)

### 6.3 Automatic Effects on Challenge

**When a challenge is submitted**:
1. Case enters **Fee Review Hold**
2. No new enforcement fees can be applied
3. Escalates to Compliance role
4. SLA timer starts (e.g., 10 working days)

### 6.4 Resolution Outcomes

#### Upheld
- Fee reversed (create reversal ledger entry)
- Ledger adjustment entry created
- Debtor statement regenerated
- Client notified (if affected)

#### Rejected
- Written explanation required
- Legal basis referenced
- Debtor notified via portal

**All outcomes are auditable and immutable.**

## 7. Automation Rules

### 7.1 Vulnerability & Advice Interaction

**If debtor has**:
- Debt advice engaged
- Breathing space
- Vulnerability flag

**Then**:
- New enforcement fees = **blocked**
- Existing fees = **review required**
- Compliance approval **mandatory** to proceed

### 7.2 Enforcement Stage Rules

**Fees can only be applied if**:
- Case stage is valid
- Required notice sent
- Required time elapsed
- No active hold or challenge

**System must refuse fee creation otherwise.**

### 7.3 Fee Application Validation

**Before creating FEE_EARNED ledger entry**:
1. Check `is_debtor_visible` flag
2. Check case stage is valid
3. Check no active challenge
4. Check no vulnerability hold
5. Check required notices sent
6. Validate legal basis
7. Create ledger entry with full metadata

## 8. Architecture: Where This Lives

| Component | Location | Reason |
|-----------|---------|--------|
| Fee rules & schedules | Platform API | Business configuration |
| Ledger & allocations | Enforcement API | Core enforcement domain |
| Debtor statements | Debtor Portal + Enforcement API | Debtor-facing |
| Client statements | Platform API | Client-facing |
| Fee challenges | Enforcement API | Compliance workflow |
| Compliance workflows | Enforcement API | Enforcement domain |

## 9. Non-Negotiable Design Principles

1. **Single ledger, multiple views** - Same data, filtered by visibility rules
2. **Visibility is rule-driven, not user-driven** - Derived from fee metadata
3. **If it affects the debtor's balance, it must be explainable** - Full transparency
4. **Every fee must be reconstructable in court** - Complete audit trail
5. **Compliance overrides are explicit and logged** - Full accountability

## 10. Implementation Checklist

### Phase 1: Fee Metadata
- [ ] Add `is_debtor_visible` to FeeRule model
- [ ] Add `legal_basis` to FeeRule model
- [ ] Add `fee_category` to FeeRule model
- [ ] Update FeeSchedule to include visibility rules
- [ ] Validate fee visibility on creation

### Phase 2: Debtor Portal
- [ ] Filter ledger entries by `is_debtor_visible`
- [ ] Show fee breakdown in debtor statement
- [ ] Add fee challenge button/action
- [ ] Display challenge status
- [ ] Show fee legal basis

### Phase 3: Client Statements
- [ ] Show all fees (debtor-visible and client-only)
- [ ] Show VAT breakdown
- [ ] Show fee calculation details
- [ ] Show allocation of fees

### Phase 4: Fee Challenge Workflow
- [ ] Create FeeChallenge model
- [ ] Add challenge submission endpoint
- [ ] Implement automatic hold on challenge
- [ ] Add compliance review workflow
- [ ] Add resolution endpoints
- [ ] Generate reversal entries on uphold

### Phase 5: Compliance Automation
- [ ] Block fees when vulnerability active
- [ ] Require compliance approval for vulnerable debtors
- [ ] Validate case stage before fee application
- [ ] Check required notices before fee
- [ ] Log all fee applications with metadata

### Phase 6: Reporting
- [ ] Debtor statement (filtered)
- [ ] Client statement (all fees)
- [ ] Fee justification report
- [ ] Trust reconciliation
- [ ] Challenge audit report

## 11. Database Schema

### FeeRule Updates

```sql
ALTER TABLE fee_rules ADD COLUMN is_debtor_visible BOOLEAN DEFAULT FALSE;
ALTER TABLE fee_rules ADD COLUMN legal_basis TEXT;
ALTER TABLE fee_rules ADD COLUMN fee_category VARCHAR(50);
ALTER TABLE fee_rules ADD CONSTRAINT check_debtor_visible_if_recoverable CHECK (
    (is_recoverable = TRUE AND is_debtor_visible = TRUE) OR
    (is_recoverable = FALSE)
);
```

### FeeChallenge Table

```sql
CREATE TABLE fee_challenges (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    fee_entry_id VARCHAR(36) NOT NULL REFERENCES ledger_entries(id),
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id),
    debtor_party_id VARCHAR(36) NOT NULL REFERENCES parties(id),
    reason_code VARCHAR(50) NOT NULL,
    description TEXT NOT NULL,
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'OPEN',
    resolved_by VARCHAR(36) REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    documents JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT check_reason_code_valid CHECK (reason_code IN (
        'INCORRECT_AMOUNT', 'WRONG_STAGE', 'NOT_INCURRED', 
        'VULNERABILITY', 'OTHER'
    )),
    CONSTRAINT check_status_valid CHECK (status IN (
        'OPEN', 'UNDER_REVIEW', 'UPHELD', 'REJECTED'
    ))
);

CREATE INDEX idx_fee_challenge_case ON fee_challenges(case_id, status);
CREATE INDEX idx_fee_challenge_debtor ON fee_challenges(debtor_party_id);
CREATE INDEX idx_fee_challenge_fee ON fee_challenges(fee_entry_id);
```

## 12. API Endpoints

### Fee Challenge Endpoints

- `POST /fee-challenges` - Submit fee challenge
- `GET /fee-challenges` - List challenges (filtered by role)
- `GET /fee-challenges/{id}` - Get challenge details
- `POST /fee-challenges/{id}/resolve` - Resolve challenge (compliance only)
- `GET /cases/{id}/fee-challenges` - Get challenges for case

### Fee Visibility Endpoints

- `GET /cases/{id}/fees/debtor-visible` - Get debtor-visible fees
- `GET /cases/{id}/fees/all` - Get all fees (role-based)
- `GET /fees/{id}/justification` - Get fee justification details

### Statement Endpoints

- `GET /statements/debtor/{case_id}` - Debtor statement (filtered)
- `GET /statements/client/{client_id}` - Client statement (all fees)
- `GET /statements/fee-justification` - Fee justification report

## 13. Testing Requirements

### Unit Tests
- Fee visibility filtering
- Challenge creation validation
- Fee application validation (vulnerability checks)
- Statement generation (filtered vs unfiltered)

### Integration Tests
- Debtor portal fee display
- Client statement fee display
- Challenge workflow (submit → review → resolve)
- Fee reversal on challenge uphold
- Vulnerability hold on fee application

### Compliance Tests
- Fee transparency requirements
- Legal basis validation
- Challenge audit trail
- Statement accuracy

## 14. UK Legal References

- **Taking Control of Goods (Fees) Regulations 2014**
- **Tribunals, Courts and Enforcement Act 2007**
- **FCA Consumer Credit Sourcebook (CONC)**
- **Debt Respite Scheme (Breathing Space) Regulations 2020**
- **Data Protection Act 2018 / GDPR**

## 15. Critical Reminders

### ⚠️ Debtor-Facing Fees
- **ALWAYS** show legal basis
- **ALWAYS** allow challenges
- **ALWAYS** itemise fees
- **NEVER** hide recoverable fees

### ⚠️ Client-Facing Fees
- **ALWAYS** show all fees
- **ALWAYS** show VAT breakdown
- **ALWAYS** show calculation method
- **ALWAYS** show allocation

### ⚠️ Internal Transparency
- **ALWAYS** maintain full audit trail
- **ALWAYS** log fee applications
- **ALWAYS** track challenges
- **ALWAYS** document overrides



