-- Migration: Create FeeChallenge table
-- Creates: fee_challenges table for debtor-initiated fee challenges (UK legal requirement)
-- Date: 2025-12-19

-- Create enum types
DO $$ BEGIN
    CREATE TYPE feechallengereason AS ENUM (
        'INCORRECT_AMOUNT', 'WRONG_STAGE', 'NOT_INCURRED', 'VULNERABILITY', 'OTHER'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE feechallengestatus AS ENUM ('OPEN', 'UNDER_REVIEW', 'UPHELD', 'REJECTED');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create fee_challenges table
CREATE TABLE IF NOT EXISTS fee_challenges (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign keys
    fee_entry_id VARCHAR(36) NOT NULL REFERENCES ledger_entries(id),
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id),
    debtor_party_id VARCHAR(36) NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    
    -- Challenge details
    reason_code feechallengereason NOT NULL,
    description TEXT NOT NULL,
    
    -- Status
    status feechallengestatus DEFAULT 'OPEN' NOT NULL,
    
    -- Resolution
    resolved_by VARCHAR(36),
    resolved_at TIMESTAMP WITH TIME ZONE,
    resolution_notes TEXT,
    
    -- Documents
    documents JSONB DEFAULT '[]'::jsonb,
    
    -- Timestamps
    submitted_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_fee_challenges_tenant_id ON fee_challenges(tenant_id);
CREATE INDEX IF NOT EXISTS idx_fee_challenges_fee_entry_id ON fee_challenges(fee_entry_id);
CREATE INDEX IF NOT EXISTS idx_fee_challenge_case ON fee_challenges(case_id, status);
CREATE INDEX IF NOT EXISTS idx_fee_challenge_debtor ON fee_challenges(debtor_party_id);
CREATE INDEX IF NOT EXISTS idx_fee_challenge_fee ON fee_challenges(fee_entry_id);

