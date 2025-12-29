-- Migration: Add performance indexes for EnforceSense module
-- Purpose: Improve query performance for common access patterns
-- Date: 2025-01-27

-- EnforcementCase indexes
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_deleted_status 
ON enforcement_cases(tenant_id, is_deleted, status) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_deleted_created 
ON enforcement_cases(tenant_id, is_deleted, created_at DESC) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_deleted_reference 
ON enforcement_cases(tenant_id, is_deleted, case_reference) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_assigned 
ON enforcement_cases(tenant_id, assigned_agent, status) 
WHERE assigned_agent IS NOT NULL AND is_deleted = false;

-- Debtor indexes
CREATE INDEX IF NOT EXISTS idx_debtors_tenant_deleted 
ON debtors(tenant_id, is_deleted, created_at DESC) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_debtors_tenant_legal_name 
ON debtors(tenant_id, legal_name) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_debtors_tenant_email 
ON debtors(tenant_id, email) 
WHERE email IS NOT NULL AND is_deleted = false;

-- LedgerEntry indexes (only create if table exists)
DO $$
BEGIN
    IF EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'ledger_entries') THEN
        CREATE INDEX IF NOT EXISTS idx_ledger_entries_case_tenant_status 
        ON ledger_entries(case_id, tenant_id, status, entry_type) 
        WHERE is_deleted = false AND status != 'REVERSED';

        CREATE INDEX IF NOT EXISTS idx_ledger_entries_case_posted 
        ON ledger_entries(case_id, posted_at DESC, created_at DESC) 
        WHERE is_deleted = false;

        CREATE INDEX IF NOT EXISTS idx_ledger_entries_tenant_posted 
        ON ledger_entries(tenant_id, posted_at DESC) 
        WHERE is_deleted = false;
    END IF;
END $$;

-- CaseNote indexes
CREATE INDEX IF NOT EXISTS idx_case_notes_case_created 
ON case_notes(case_id, created_at DESC) 
WHERE tenant_id IS NOT NULL;

-- EnforcementClient indexes
CREATE INDEX IF NOT EXISTS idx_enforcement_clients_tenant_deleted 
ON enforcement_clients(tenant_id, is_deleted, name) 
WHERE is_deleted = false;

-- Comments (only add if indexes exist)
DO $$
BEGIN
    IF EXISTS (SELECT FROM pg_indexes WHERE indexname = 'idx_enforcement_cases_tenant_deleted_status') THEN
        COMMENT ON INDEX idx_enforcement_cases_tenant_deleted_status IS 
        'Composite index for common case list queries filtered by tenant, deleted status, and status';
    END IF;
    
    IF EXISTS (SELECT FROM pg_indexes WHERE indexname = 'idx_ledger_entries_case_tenant_status') THEN
        COMMENT ON INDEX idx_ledger_entries_case_tenant_status IS 
        'Composite index for balance calculations and ledger queries';
    END IF;
    
    IF EXISTS (SELECT FROM pg_indexes WHERE indexname = 'idx_debtors_tenant_deleted') THEN
        COMMENT ON INDEX idx_debtors_tenant_deleted IS 
        'Composite index for debtor list queries filtered by tenant and deleted status';
    END IF;
END $$;

