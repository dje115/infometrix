# EnforceSense Financial Model & Ledger Specification

**Version:** 1.0  
**Status:** MANDATORY - Critical for Payment Traceability & Audit  
**Last Updated:** 2025-12-19

## Overview

This document defines the end-to-end financial model for EnforceSense that supports:
- Multiple debts per debtor
- Partial payments
- Client payouts
- Fee structures
- Complete audit trail
- Regulatory compliance
- **Fee transparency (UK legal requirement)**

**CRITICAL**: The Ledger is the single source of truth for all financial reporting. All balances are derived from ledger entries, never stored directly.

**CRITICAL**: Fee transparency is legally required in UK debt recovery/enforcement. See `docs/enforcesense/FEE_TRANSPARENCY.md` for complete fee visibility rules.

## Five-Layer Architecture

### Layer 1: Core Financial Entities

#### A) DebtAccount (What is Owed)

**Purpose**: Represents what the debtor owes the client (creditor)

**Key Fields**:
- `id` (debtId)
- `tenant_id`
- `client_account_id` (creditor - FK to Customer)
- `debtor_party_id` (FK to Party)
- `original_principal` (Numeric) - Original debt amount
- `interest_rules` (JSON) - Interest calculation rules
- `fee_rules` (JSON) - What can be charged to debtor
- `status` (enum): `ACTIVE`, `SETTLED`, `DISPUTED`, `STAYED`
- `currency` (String, default: "GBP")
- `debt_reference` (String, unique)
- `client_reference` (String, optional)
- `invoice_reference` (String, optional)
- `contract_reference` (String, optional)
- `court_reference` (String, optional)
- `due_date` (DateTime, optional)
- `debt_type` (enum): `INVOICE`, `JUDGMENT`, `CONTRACT`, `COUNCIL_TAX`, `BUSINESS_RATES`, `PARKING_FINE`, `OTHER`
- Timestamps

**CRITICAL RULE**: A debt never directly knows your fees. It only knows:
- What the debtor owes
- What the client is entitled to receive (gross)

**Relationships**:
- `client_account` (many-to-one to Customer)
- `debtor_party` (many-to-one to Party)
- `case_debts` (many-to-many via CaseDebts)
- `ledger_entries` (one-to-many, filtered by debtId)

#### B) Case (Workflow Container)

**Purpose**: Groups one or more Debt Accounts for enforcement

**Key Financial Fields**:
- `id` (caseId)
- `tenant_id`
- `case_reference` (String, unique)
- Financial totals (DERIVED from ledger, not stored):
  - `total_debt` (sum of linked debt accounts)
  - `total_recovered` (sum of DEBTOR_PAYMENT entries)
  - `total_fees_earned` (sum of FEE_EARNED entries)
  - `total_paid_to_client` (sum of CLIENT_PAYOUT entries)
  - `current_balance` (total_debt - total_recovered)

**CRITICAL**: All financial totals are derived from ledger entries, never stored directly.

**Relationships**:
- `case_debts` (one-to-many to CaseDebts)
- `ledger_entries` (one-to-many)
- `payment_allocations` (one-to-many)

#### C) LedgerEntry (Single Source of Truth)

**Purpose**: Every movement of money = a Ledger Entry

**CRITICAL PRINCIPLE**: The Ledger is the single source of truth. All reporting comes from the ledger, not from "balances".

**Key Fields**:
- `id` (entryId)
- `tenant_id`
- `case_id` (FK to Case, nullable if tenant-level)
- `debt_id` (FK to DebtAccount, nullable)
- `entry_type` (enum):
  - `DEBTOR_PAYMENT` - Payment received from debtor
  - `CLIENT_PAYOUT` - Payment made to client
  - `FEE_EARNED` - Your fee revenue
  - `DISBURSEMENT` - Costs incurred (court fees, etc.)
  - `REFUND` - Refund to debtor
  - `ADJUSTMENT` - Manual adjustment
  - `INTEREST_ACCRUED` - Interest added to debt
  - `FEE_CHARGED` - Fee charged to debtor
- `amount` (Numeric) - Always positive, direction determined by entry_type
- `currency` (String, default: "GBP")
- `description` (Text)
- `reference` (String, optional) - External reference (payment ref, invoice, etc.)
- `status` (enum): `PENDING`, `CLEARED`, `REVERSED`
- `posted_at` (DateTime) - When entry was posted/cleared
- `reversed_at` (DateTime, optional) - If reversed
- `reversed_by` (FK to User, optional)
- `reversal_reason` (Text, optional)
- `created_at` (DateTime)
- `created_by` (FK to User)
- `metadata` (JSON) - Additional context (payment method, batch ID, etc.)

**Relationships**:
- `case` (many-to-one)
- `debt_account` (many-to-one, optional)
- `payment_allocation` (one-to-one, if DEBTOR_PAYMENT)
- `fee_schedule_rule` (many-to-one, if FEE_EARNED)

**Indexes**:
- `(tenant_id, case_id, entry_type, status)`
- `(tenant_id, debt_id, entry_type)`
- `(tenant_id, posted_at)` - For reporting
- `(tenant_id, created_at)` - For audit

### Layer 2: Payment Flow (Debtor → You → Client)

#### Step 1: Debtor Pays

**Trigger**: Debtor makes payment (portal, card, bank transfer, enforcement agent, etc.)

**Actions**:
1. Create `LedgerEntry`:
   - `entry_type = DEBTOR_PAYMENT`
   - `amount = payment_amount`
   - `case_id = case.id`
   - `debt_id = null` (allocated later)
   - `status = PENDING` (until cleared)
   - `metadata = {payment_method, payment_reference, etc.}`

2. Amount goes into **Client Trust / Holding Balance**
   - At this stage: ❌ not client money, ❌ not your revenue yet
   - Tracked as sum of PENDING DEBTOR_PAYMENT entries

#### Step 2: Allocate the Payment

**Purpose**: Split payment across debts and fee buckets

**Model**: `PaymentAllocation`

**Key Fields**:
- `id`
- `tenant_id`
- `payment_entry_id` (FK to LedgerEntry, type=DEBTOR_PAYMENT)
- `case_id` (FK to Case)
- `allocation_lines` (JSON array):
  ```json
  [
    {
      "target_type": "PRINCIPAL",
      "target_id": "debt-account-id",
      "amount": 100.00,
      "order": 1
    },
    {
      "target_type": "INTEREST",
      "target_id": "debt-account-id",
      "amount": 10.00,
      "order": 2
    },
    {
      "target_type": "ENFORCEMENT_FEE",
      "target_id": "fee-rule-id",
      "amount": 20.00,
      "order": 3
    },
    {
      "target_type": "CLIENT_FEE",
      "target_id": "fee-rule-id",
      "amount": 5.00,
      "order": 4
    }
  ]
  ```
- `total_allocated` (Numeric) - Must equal payment amount
- `allocation_method` (enum): `AUTOMATIC`, `MANUAL`, `RULE_BASED`
- `allocated_at` (DateTime)
- `allocated_by` (FK to User)
- Timestamps

**Allocation Rules**:
- Regulatory ordering (e.g., principal before fees)
- Partial settlements supported
- Multiple debts per payment
- Fee allocation based on FeeSchedule rules

**Validation**:
- `sum(allocation_lines.amount) == payment_entry.amount`
- Allocation order must be valid (principal before fees, etc.)

#### Step 3: Recognise Your Fees

**Trigger**: When allocation includes your fees

**Actions**:
1. For each `ENFORCEMENT_FEE` allocation:
   - Create `LedgerEntry`:
     - `entry_type = FEE_EARNED`
     - `amount = allocation.amount`
     - `case_id = case.id`
     - `debt_id = allocation.target_id` (if applicable)
     - `status = CLEARED` (or PENDING if accrual-based)
     - `metadata = {fee_schedule_rule_id, fee_type, etc.}`

2. Link to:
   - Case
   - Client (via Case → DebtAccount → Customer)
   - FeeScheduleRule

**This is your revenue recognition point.**

#### Step 4: Pay the Client

**Trigger**: When funds are released to client (manual or batch)

**Actions**:
1. Calculate payout amount:
   ```
   payout_amount = sum(DEBTOR_PAYMENT) 
                   - sum(FEE_EARNED) 
                   - sum(DISBURSEMENT)
   ```

2. Create `LedgerEntry`:
   - `entry_type = CLIENT_PAYOUT`
   - `amount = payout_amount`
   - `case_id = case.id` (or null for batch payout)
   - `status = PENDING` (until bank transfer confirmed)
   - `metadata = {payout_batch_id, bank_reference, payout_date}`

3. Track:
   - Payout batch
   - Bank reference
   - Payout date
   - Reconciliation status

### Layer 3: Fee Structures

#### A) FeeSchedules (Defined Per Client or Tenant)

**Purpose**: Define how you get paid

**Model**: `FeeSchedule`

**Key Fields**:
- `id` (feeScheduleId)
- `tenant_id`
- `scope` (enum):
  - `TENANT_DEFAULT` - Default for all clients
  - `CLIENT_SPECIFIC` - Override for specific client
  - `CASE_OVERRIDE` - Override for specific case
- `client_id` (FK to Customer, nullable if TENANT_DEFAULT)
- `case_id` (FK to Case, nullable if not CASE_OVERRIDE)
- `effective_from` (DateTime)
- `effective_to` (DateTime, optional)
- `name` (String) - "Standard Recovery Fee Schedule"
- `description` (Text)
- `is_active` (Boolean)
- Timestamps

**Relationships**:
- `fee_rules` (one-to-many)
- `client` (many-to-one, optional)

#### B) FeeRule (How You Get Paid)

**Purpose**: Each rule defines a fee calculation method

**Key Fields**:
- `id`
- `tenant_id`
- `fee_schedule_id` (FK to FeeSchedule)
- `fee_type` (enum):
  - `PERCENTAGE` - % of recovered principal
  - `FIXED` - Fixed amount
  - `TIERED` - Tiered percentage
  - `SUCCESS_FEE_ONLY` - Only if recovered
- `calculation_base` (enum):
  - `PRINCIPAL` - % of principal recovered
  - `TOTAL_DEBT` - % of total debt
  - `RECOVERED_AMOUNT` - % of amount recovered
- `rate_or_amount` (Numeric):
  - If `fee_type = PERCENTAGE`: rate (e.g., 0.20 = 20%)
  - If `fee_type = FIXED`: amount (e.g., 75.00)
- `who_pays` (enum):
  - `CLIENT` - Client pays you (deducted from recovery)
  - `DEBTOR` - Debtor pays you (added to debt)
- `vat_applicable` (Boolean)
- `vat_rate` (Numeric, default: 0.20 for UK)
- `trigger_event` (enum):
  - `ON_RECOVERY` - When payment received
  - `ON_CASE_STAGE` - When case reaches stage
  - `ON_CLOSURE` - When case closed
  - `ON_INSTRUCTION` - When case opened
- `trigger_stage` (String, optional) - If ON_CASE_STAGE
- `minimum_amount` (Numeric, optional)
- `maximum_amount` (Numeric, optional)
- `priority_order` (Integer) - For multiple rules
- `is_active` (Boolean)
- Timestamps

**Examples**:
- "20% of recovered principal" → `fee_type=PERCENTAGE`, `calculation_base=PRINCIPAL`, `rate_or_amount=0.20`
- "£75 on instruction" → `fee_type=FIXED`, `rate_or_amount=75.00`, `trigger_event=ON_INSTRUCTION`
- "Success fee only if recovered" → `fee_type=PERCENTAGE`, `trigger_event=ON_RECOVERY`, `minimum_amount=0.01`

**Relationships**:
- `fee_schedule` (many-to-one)
- `ledger_entries` (one-to-many, type=FEE_EARNED)

#### C) Fee Application Lifecycle

1. **Fee rules are evaluated** (when trigger event occurs)
2. **Fee entries are generated** (LedgerEntry type=FEE_EARNED)
3. **Fees become ledger entries** (immutable audit trail)
4. **Fees appear in**:
   - Client statements
   - Internal revenue reports
   - VAT returns

### Layer 4: Reporting (What You and Clients See)

#### A) Client-Facing Reports

##### 1. Client Statement

**Purpose**: Per client, per period

**Shows**:
- Opening balance
- Debts instructed
- Recoveries
- Fees charged
- Disbursements
- Net paid to client
- Closing balance

**Derived from Ledger**:
```sql
SELECT 
  entry_type,
  SUM(amount) as total
FROM ledger_entries
WHERE tenant_id = ? 
  AND case_id IN (SELECT id FROM cases WHERE client_id = ?)
  AND posted_at BETWEEN ? AND ?
GROUP BY entry_type
```

**Entry Types Used**:
- `DEBTOR_PAYMENT` → Recoveries
- `FEE_EARNED` → Fees charged
- `DISBURSEMENT` → Disbursements
- `CLIENT_PAYOUT` → Net paid to client

##### 2. Case Recovery Report

**Shows**:
- Case reference
- Debtor
- Total debt
- Total recovered
- Fees deducted
- Net remitted

**Derived from Ledger**:
- Total debt: Sum of DebtAccount.original_principal
- Total recovered: Sum of DEBTOR_PAYMENT entries
- Fees deducted: Sum of FEE_EARNED entries (where who_pays=CLIENT)
- Net remitted: Sum of CLIENT_PAYOUT entries

##### 3. Outstanding Debt Report

**Shows**:
- Debt reference
- Original amount
- Amount recovered
- Balance remaining
- Case status

**Derived from Ledger**:
- Original amount: DebtAccount.original_principal
- Amount recovered: Sum of DEBTOR_PAYMENT entries allocated to this debt
- Balance remaining: original_principal - amount_recovered

#### B) Internal (Your Business)

##### 4. Fee Revenue Report

**Shows**:
- Fees earned by:
  - Client
  - Case
  - Fee type
  - Period
- VAT split
- Accrual vs paid

**Derived from Ledger**:
```sql
SELECT 
  client_id,
  case_id,
  fee_type,
  DATE_TRUNC('month', posted_at) as period,
  SUM(amount) as fees_earned,
  SUM(amount * vat_rate) as vat_amount
FROM ledger_entries
WHERE entry_type = 'FEE_EARNED'
  AND tenant_id = ?
  AND posted_at BETWEEN ? AND ?
GROUP BY client_id, case_id, fee_type, period
```

##### 5. Trust / Client Account Reconciliation

**Shows**:
- Funds held (sum of PENDING DEBTOR_PAYMENT)
- Funds pending allocation
- Funds pending payout
- Aged balances (compliance-critical)

**Derived from Ledger**:
- Funds held: Sum of DEBTOR_PAYMENT where status=PENDING
- Funds pending payout: Sum of CLIENT_PAYOUT where status=PENDING
- Aged balances: Group by age buckets (0-30 days, 31-60 days, etc.)

##### 6. Performance & ROI

**Shows**:
- Recovery rate % (recovered / total debt)
- Average days to recovery
- Revenue per case
- Revenue per debtor
- Agent performance (if applicable)

**Derived from Ledger**:
- Recovery rate: `SUM(DEBTOR_PAYMENT) / SUM(DebtAccount.original_principal)`
- Revenue per case: `SUM(FEE_EARNED) / COUNT(DISTINCT case_id)`

#### C) Compliance / Audit Reports

##### 7. Full Ledger Export

**Purpose**: Complete audit trail

**Shows**:
- All ledger entries
- Allocations
- Fee justifications
- Reversals

##### 8. Allocation Trace

**Purpose**: Payment → Debt → Fee traceability

**Shows**:
- Payment entry
- Allocation lines
- Linked debt accounts
- Fee entries generated

##### 9. Fee Justification

**Purpose**: Rule + trigger audit

**Shows**:
- Fee entry
- FeeScheduleRule used
- Trigger event
- Calculation details

##### 10. Breathing Space / Vulnerability Impact Logs

**Purpose**: Compliance tracking

**Shows**:
- When support status changed
- Which cases were affected
- What actions were taken
- Fee adjustments made

### Layer 5: Real-World Complexity Handling

#### ✔ Debtor Has Multiple Debts

**Scenario**: One payment → allocated across multiple debts

**Solution**:
- PaymentAllocation supports multiple allocation lines
- Each line targets different debt_id
- Ledger links preserve audit trail
- Reports aggregate correctly

#### ✔ Client-Specific Fee Agreements

**Scenario**: Different clients have different fee structures

**Solution**:
- FeeSchedule scoped per client (CLIENT_SPECIFIC)
- Override at case level if required (CASE_OVERRIDE)
- Default fallback to TENANT_DEFAULT

#### ✔ Partial Settlements

**Scenario**: Debtor pays less than full amount

**Solution**:
- Allocation engine handles partial amounts
- Reports still balance (allocated amount = payment amount)
- Remaining balance tracked via ledger

#### ✔ Regulated Enforcement

**Scenario**: Fees must be flagged as recoverable/non-recoverable

**Solution**:
- FeeRule includes `recoverable_from_debtor` flag
- Automatically excluded from client payout if debtor-paid
- Separate tracking for recoverable vs non-recoverable fees

## Architecture: Where Things Live

| Component | Lives in | Reason |
|-----------|----------|--------|
| Ledger | Enforcement API | Core enforcement domain |
| Allocations | Enforcement API | Payment processing |
| Fee Schedules | Platform API | Business configuration |
| Client Statements | Platform API | Reads ledger, generates reports |
| Payout Batching | Platform API | Financial operations |
| Debtor Portal Payments | Enforcement API | Payment collection |
| VAT Logic | Platform API | Tax calculations |

## Minimum Viable Implementation (Phase 1)

### Must-Have Features

1. **Ledger**
   - LedgerEntry model with all entry types
   - Immutable entries (reversals only, no edits)
   - Full audit trail

2. **Single Fee Schedule Per Client**
   - FeeSchedule model
   - FeeRule model
   - Basic fee calculation (percentage or fixed)

3. **Manual Payout Trigger**
   - CLIENT_PAYOUT ledger entry creation
   - Manual approval workflow
   - Basic reconciliation

4. **Core Reports**
   - Client Statement (derived from ledger)
   - Fee Revenue Report (derived from ledger)

### Phase 2 (Future)

- Automated payout batching
- Advanced allocation rules
- VAT & accrual accounting
- Xero export
- Multi-currency support
- Interest calculations

## Critical Development Rules

### 1. Ledger is Single Source of Truth

**NEVER**:
- Store balances directly in Case or DebtAccount
- Calculate totals from stored fields
- Trust "current_balance" fields

**ALWAYS**:
- Derive all balances from ledger entries
- Use ledger for all reporting
- Create ledger entry for every financial movement

### 2. Immutable Ledger Entries

**NEVER**:
- Edit ledger entries
- Delete ledger entries
- Change amounts after posting

**ALWAYS**:
- Create reversal entries for corrections
- Maintain full audit trail
- Track who created/reversed entries

### 3. Allocation Validation

**NEVER**:
- Allow allocations that don't sum to payment amount
- Allow negative allocations
- Skip allocation validation

**ALWAYS**:
- Validate `sum(allocation_lines.amount) == payment_entry.amount`
- Validate allocation order (regulatory compliance)
- Store allocation method (AUTOMATIC/MANUAL/RULE_BASED)

### 4. Fee Calculation

**NEVER**:
- Hardcode fee percentages
- Calculate fees outside FeeSchedule rules
- Skip fee justification

**ALWAYS**:
- Use FeeSchedule rules
- Link fee entries to FeeRule
- Store calculation details in metadata

### 5. Audit Trail

**NEVER**:
- Skip user tracking
- Skip timestamp tracking
- Allow unlogged financial changes

**ALWAYS**:
- Track `created_by` for all entries
- Track `posted_at` for all entries
- Track reversals with reason
- Maintain full allocation trace

## Database Schema

### LedgerEntry Table

```sql
CREATE TABLE ledger_entries (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    case_id VARCHAR(36) REFERENCES enforcement_cases(id),
    debt_id VARCHAR(36) REFERENCES debt_accounts(id),
    entry_type VARCHAR(50) NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP',
    description TEXT,
    reference VARCHAR(100),
    status VARCHAR(20) DEFAULT 'PENDING',
    posted_at TIMESTAMP WITH TIME ZONE,
    reversed_at TIMESTAMP WITH TIME ZONE,
    reversed_by VARCHAR(36) REFERENCES users(id),
    reversal_reason TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36) REFERENCES users(id),
    metadata JSONB,
    
    CONSTRAINT check_amount_positive CHECK (amount > 0),
    CONSTRAINT check_entry_type_valid CHECK (entry_type IN (
        'DEBTOR_PAYMENT', 'CLIENT_PAYOUT', 'FEE_EARNED', 
        'DISBURSEMENT', 'REFUND', 'ADJUSTMENT', 
        'INTEREST_ACCRUED', 'FEE_CHARGED'
    ))
);

CREATE INDEX idx_ledger_tenant_case_type_status 
    ON ledger_entries(tenant_id, case_id, entry_type, status);
CREATE INDEX idx_ledger_tenant_debt_type 
    ON ledger_entries(tenant_id, debt_id, entry_type);
CREATE INDEX idx_ledger_tenant_posted_at 
    ON ledger_entries(tenant_id, posted_at);
```

### PaymentAllocation Table

```sql
CREATE TABLE payment_allocations (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    payment_entry_id VARCHAR(36) NOT NULL REFERENCES ledger_entries(id),
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id),
    allocation_lines JSONB NOT NULL,
    total_allocated NUMERIC(12, 2) NOT NULL,
    allocation_method VARCHAR(20) NOT NULL,
    allocated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    allocated_by VARCHAR(36) REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    CONSTRAINT check_total_matches_payment CHECK (
        total_allocated = (SELECT amount FROM ledger_entries WHERE id = payment_entry_id)
    )
);

CREATE INDEX idx_payment_alloc_tenant_case 
    ON payment_allocations(tenant_id, case_id);
CREATE INDEX idx_payment_alloc_payment_entry 
    ON payment_allocations(payment_entry_id);
```

### FeeSchedule Table

```sql
CREATE TABLE fee_schedules (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    scope VARCHAR(20) NOT NULL,
    client_id VARCHAR(36) REFERENCES customers(id),
    case_id VARCHAR(36) REFERENCES enforcement_cases(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    effective_from TIMESTAMP WITH TIME ZONE NOT NULL,
    effective_to TIMESTAMP WITH TIME ZONE,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT check_scope_valid CHECK (scope IN (
        'TENANT_DEFAULT', 'CLIENT_SPECIFIC', 'CASE_OVERRIDE'
    )),
    CONSTRAINT check_client_if_specific CHECK (
        (scope = 'CLIENT_SPECIFIC' AND client_id IS NOT NULL) OR
        (scope != 'CLIENT_SPECIFIC')
    )
);

CREATE INDEX idx_fee_schedule_tenant_scope 
    ON fee_schedules(tenant_id, scope, is_active);
CREATE INDEX idx_fee_schedule_client 
    ON fee_schedules(tenant_id, client_id) WHERE client_id IS NOT NULL;
```

### FeeRule Table

```sql
CREATE TABLE fee_rules (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    fee_schedule_id VARCHAR(36) NOT NULL REFERENCES fee_schedules(id) ON DELETE CASCADE,
    fee_type VARCHAR(20) NOT NULL,
    calculation_base VARCHAR(20),
    rate_or_amount NUMERIC(12, 2) NOT NULL,
    who_pays VARCHAR(20) NOT NULL,
    vat_applicable BOOLEAN DEFAULT FALSE,
    vat_rate NUMERIC(5, 4) DEFAULT 0.20,
    trigger_event VARCHAR(20) NOT NULL,
    trigger_stage VARCHAR(50),
    minimum_amount NUMERIC(12, 2),
    maximum_amount NUMERIC(12, 2),
    priority_order INTEGER DEFAULT 0,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    
    CONSTRAINT check_fee_type_valid CHECK (fee_type IN (
        'PERCENTAGE', 'FIXED', 'TIERED', 'SUCCESS_FEE_ONLY'
    )),
    CONSTRAINT check_who_pays_valid CHECK (who_pays IN ('CLIENT', 'DEBTOR')),
    CONSTRAINT check_trigger_event_valid CHECK (trigger_event IN (
        'ON_RECOVERY', 'ON_CASE_STAGE', 'ON_CLOSURE', 'ON_INSTRUCTION'
    ))
);

CREATE INDEX idx_fee_rule_schedule 
    ON fee_rules(fee_schedule_id, is_active, priority_order);
```

## API Endpoints

### Ledger Endpoints

- `GET /ledger/entries` - List ledger entries (with filters)
- `GET /ledger/entries/{id}` - Get ledger entry details
- `POST /ledger/entries/{id}/reverse` - Reverse a ledger entry
- `GET /ledger/reconciliation` - Trust account reconciliation
- `GET /ledger/export` - Export ledger for audit

### Payment Endpoints

- `POST /payments` - Record debtor payment
- `POST /payments/{id}/allocate` - Allocate payment
- `GET /payments/{id}/allocation` - Get allocation details
- `POST /payments/{id}/clear` - Clear payment (mark as cleared)

### Fee Endpoints

- `GET /fee-schedules` - List fee schedules
- `POST /fee-schedules` - Create fee schedule
- `GET /fee-schedules/{id}/rules` - Get fee rules
- `POST /fee-schedules/{id}/rules` - Add fee rule
- `POST /cases/{id}/calculate-fees` - Calculate fees for case

### Payout Endpoints

- `POST /payouts` - Create client payout
- `GET /payouts` - List payouts
- `POST /payouts/batch` - Create batch payout
- `GET /payouts/{id}/reconciliation` - Payout reconciliation

### Reporting Endpoints

- `GET /reports/client-statement` - Client statement
- `GET /reports/fee-revenue` - Fee revenue report
- `GET /reports/case-recovery` - Case recovery report
- `GET /reports/outstanding-debts` - Outstanding debts
- `GET /reports/trust-reconciliation` - Trust reconciliation

## Testing Requirements

### Unit Tests

- Ledger entry creation
- Allocation validation
- Fee calculation
- Balance derivation

### Integration Tests

- Payment flow (debtor → allocation → fees → payout)
- Multi-debt allocation
- Fee schedule application
- Report generation

### Audit Tests

- Immutability of ledger entries
- Full allocation trace
- Reversal audit trail
- User tracking

## Compliance Considerations

### UK Regulations

- **FCA Compliance**: Fee structures must be transparent
- **Data Protection**: Financial data is sensitive (GDPR)
- **Audit Requirements**: Full audit trail mandatory
- **Trust Account Rules**: Client funds must be segregated

### Audit Trail Requirements

- Who created entry
- When created
- Who approved (if applicable)
- Who reversed (if applicable)
- Why reversed
- Full allocation trace

## Migration from Current Model

### Current State

- `CaseTransaction` model exists
- Financial totals stored in `Case` model
- No fee schedule system
- No allocation system

### Migration Steps

1. Create `LedgerEntry` model
2. Migrate `CaseTransaction` → `LedgerEntry`
3. Create `PaymentAllocation` model
4. Create `FeeSchedule` and `FeeRule` models
5. Remove stored balances from `Case` model
6. Update all reports to use ledger
7. Add allocation workflow
8. Add fee calculation engine

