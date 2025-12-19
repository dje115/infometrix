-- Migration: Create Financial Phase 1 Models
-- Creates: LedgerEntry, PaymentAllocation, FeeSchedule, FeeRule tables
-- Date: 2025-12-19

-- Create enum types
DO $$ BEGIN
    CREATE TYPE ledgerentrytype AS ENUM (
        'DEBTOR_PAYMENT', 'CLIENT_PAYOUT', 'FEE_EARNED', 'DISBURSEMENT', 
        'REFUND', 'ADJUSTMENT', 'INTEREST_ACCRUED', 'FEE_CHARGED'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE ledgerentrystatus AS ENUM ('PENDING', 'CLEARED', 'REVERSED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE paymentallocationmethod AS ENUM ('AUTOMATIC', 'MANUAL', 'RULE_BASED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE feeschedulescope AS ENUM ('TENANT_DEFAULT', 'CLIENT_SPECIFIC', 'CASE_OVERRIDE');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE feetype AS ENUM ('PERCENTAGE', 'FIXED', 'TIERED', 'SUCCESS_FEE_ONLY');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE feecalculationbase AS ENUM ('PRINCIPAL', 'TOTAL_DEBT', 'RECOVERED_AMOUNT');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE feewhopays AS ENUM ('CLIENT', 'DEBTOR');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE feetriggerevent AS ENUM ('ON_RECOVERY', 'ON_CASE_STAGE', 'ON_CLOSURE', 'ON_INSTRUCTION');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create ledger_entries table
CREATE TABLE IF NOT EXISTS ledger_entries (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign keys (nullable for tenant-level entries)
    case_id VARCHAR(36) REFERENCES enforcement_cases(id),
    debt_id VARCHAR(36) REFERENCES debt_accounts(id),
    fee_rule_id VARCHAR(36),  -- FK to fee_rules (will be added after fee_rules table exists)
    
    -- Entry type (required)
    entry_type ledgerentrytype NOT NULL,
    
    -- Amount (always positive, direction determined by entry_type)
    amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP' NOT NULL,
    
    -- Description and reference
    description TEXT,
    reference VARCHAR(100),
    
    -- Status
    status ledgerentrystatus DEFAULT 'PENDING' NOT NULL,
    posted_at TIMESTAMP WITH TIME ZONE,
    
    -- Reversal tracking
    reversed_at TIMESTAMP WITH TIME ZONE,
    reversed_by VARCHAR(36),  -- FK to User
    reversal_reason TEXT,
    
    -- Metadata (JSON)
    metadata JSONB DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_by VARCHAR(36)  -- FK to User
);

-- Create indexes for ledger_entries
CREATE INDEX IF NOT EXISTS idx_ledger_entries_tenant_id ON ledger_entries(tenant_id);
CREATE INDEX IF NOT EXISTS idx_ledger_entries_case_id ON ledger_entries(case_id) WHERE case_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ledger_entries_debt_id ON ledger_entries(debt_id) WHERE debt_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ledger_entries_fee_rule_id ON ledger_entries(fee_rule_id) WHERE fee_rule_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ledger_tenant_case_type_status ON ledger_entries(tenant_id, case_id, entry_type, status) WHERE case_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ledger_tenant_debt_type ON ledger_entries(tenant_id, debt_id, entry_type) WHERE debt_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_ledger_tenant_posted_at ON ledger_entries(tenant_id, posted_at);

-- Add constraint: amount must be positive
ALTER TABLE ledger_entries ADD CONSTRAINT check_amount_positive CHECK (amount > 0);

-- Create payment_allocations table
CREATE TABLE IF NOT EXISTS payment_allocations (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign key to payment ledger entry
    payment_entry_id VARCHAR(36) NOT NULL REFERENCES ledger_entries(id) UNIQUE,
    
    -- Case reference
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id),
    
    -- Allocation lines (JSON array)
    allocation_lines JSONB NOT NULL,
    
    -- Total allocated (must equal payment amount)
    total_allocated NUMERIC(12, 2) NOT NULL,
    
    -- Allocation method
    allocation_method paymentallocationmethod NOT NULL,
    
    -- Timestamps
    allocated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    allocated_by VARCHAR(36),  -- FK to User
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for payment_allocations
CREATE INDEX IF NOT EXISTS idx_payment_allocations_tenant_id ON payment_allocations(tenant_id);
CREATE INDEX IF NOT EXISTS idx_payment_allocations_payment_entry_id ON payment_allocations(payment_entry_id);
CREATE INDEX IF NOT EXISTS idx_payment_alloc_tenant_case ON payment_allocations(tenant_id, case_id);

-- Create fee_schedules table
CREATE TABLE IF NOT EXISTS fee_schedules (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Scope
    scope feeschedulescope NOT NULL,
    client_id VARCHAR(36),  -- FK to Customer (if CLIENT_SPECIFIC)
    case_id VARCHAR(36) REFERENCES enforcement_cases(id),  -- If CASE_OVERRIDE
    
    -- Schedule details
    name VARCHAR(255) NOT NULL,
    description TEXT,
    
    -- Effective dates
    effective_from TIMESTAMP WITH TIME ZONE NOT NULL,
    effective_to TIMESTAMP WITH TIME ZONE,
    
    -- Active flag
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for fee_schedules
CREATE INDEX IF NOT EXISTS idx_fee_schedules_tenant_id ON fee_schedules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_fee_schedules_scope ON fee_schedules(scope);
CREATE INDEX IF NOT EXISTS idx_fee_schedule_tenant_scope ON fee_schedules(tenant_id, scope, is_active);
CREATE INDEX IF NOT EXISTS idx_fee_schedule_client ON fee_schedules(tenant_id, client_id) WHERE client_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_fee_schedules_case_id ON fee_schedules(case_id) WHERE case_id IS NOT NULL;

-- Create fee_rules table
CREATE TABLE IF NOT EXISTS fee_rules (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign key to fee schedule
    fee_schedule_id VARCHAR(36) NOT NULL REFERENCES fee_schedules(id) ON DELETE CASCADE,
    
    -- Fee type and calculation
    fee_type feetype NOT NULL,
    calculation_base feecalculationbase,
    rate_or_amount NUMERIC(12, 2) NOT NULL,
    
    -- Who pays
    who_pays feewhopays NOT NULL,
    
    -- Fee transparency (UK legal requirement)
    is_recoverable BOOLEAN DEFAULT FALSE NOT NULL,
    is_debtor_visible BOOLEAN DEFAULT FALSE NOT NULL,
    fee_category VARCHAR(50),
    legal_basis TEXT,
    
    -- VAT
    vat_applicable BOOLEAN DEFAULT FALSE NOT NULL,
    vat_rate NUMERIC(5, 4) DEFAULT 0.20 NOT NULL,
    
    -- Trigger
    trigger_event feetriggerevent NOT NULL,
    trigger_stage VARCHAR(50),
    
    -- Limits
    minimum_amount NUMERIC(12, 2),
    maximum_amount NUMERIC(12, 2),
    
    -- Priority order
    priority_order INTEGER DEFAULT 0 NOT NULL,
    
    -- Active flag
    is_active BOOLEAN DEFAULT TRUE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for fee_rules
CREATE INDEX IF NOT EXISTS idx_fee_rules_tenant_id ON fee_rules(tenant_id);
CREATE INDEX IF NOT EXISTS idx_fee_rules_fee_schedule_id ON fee_rules(fee_schedule_id);
CREATE INDEX IF NOT EXISTS idx_fee_rule_schedule ON fee_rules(fee_schedule_id, is_active, priority_order);

-- Add constraint: if recoverable, must be debtor visible
ALTER TABLE fee_rules ADD CONSTRAINT check_debtor_visible_if_recoverable CHECK (
    (is_recoverable = TRUE AND is_debtor_visible = TRUE) OR
    (is_recoverable = FALSE)
);

-- Now add foreign key constraint for fee_rule_id in ledger_entries
ALTER TABLE ledger_entries ADD CONSTRAINT fk_ledger_entries_fee_rule 
    FOREIGN KEY (fee_rule_id) REFERENCES fee_rules(id);

