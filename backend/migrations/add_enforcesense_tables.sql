-- Migration: Create EnforceSense tables
-- This migration creates the core EnforceSense tables: debtors, enforcement_clients, enforcement_cases, case_transactions
-- Based on Core Domain Model: Debtor, Client, Case

-- Create enum types
DO $$ BEGIN
    CREATE TYPE debtorentitytype AS ENUM ('PERSON', 'COMPANY');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE casestatus AS ENUM ('draft', 'active', 'on_hold', 'settled', 'closed', 'cancelled');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE casetype AS ENUM (
        'county_court_judgment',
        'high_court_writ',
        'magistrates_court',
        'council_tax',
        'business_rates',
        'parking_fine',
        'other'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE transactiontype AS ENUM ('payment', 'fee', 'refund', 'adjustment', 'write_off');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create debtors table
CREATE TABLE IF NOT EXISTS debtors (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Entity type (required)
    entity_type debtorentitytype NOT NULL,
    
    -- Legal name (required)
    legal_name VARCHAR(255) NOT NULL,
    
    -- Person-specific fields
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    date_of_birth TIMESTAMP WITH TIME ZONE,
    national_identifier VARCHAR(50),
    
    -- Company-specific fields
    company_registration_number VARCHAR(50),
    
    -- Trading names/aliases (JSON array)
    trading_names JSON DEFAULT '[]'::jsonb,
    
    -- Contact details
    email VARCHAR(255),
    phone VARCHAR(50),
    
    -- Address history (JSON array)
    address_history JSON DEFAULT '[]'::jsonb,
    
    -- Communication preferences
    language_preference VARCHAR(5) DEFAULT 'en',
    communication_preferences JSON DEFAULT '{}'::jsonb,
    
    -- Vulnerability indicators
    is_vulnerable BOOLEAN NOT NULL DEFAULT FALSE,
    vulnerability_notes TEXT,
    
    -- Risk flags
    risk_flags JSON DEFAULT '[]'::jsonb,
    
    -- External references
    external_references JSON DEFAULT '{}'::jsonb,
    
    -- AI-generated summaries
    ai_summary TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create enforcement_clients table
CREATE TABLE IF NOT EXISTS enforcement_clients (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Client information
    name VARCHAR(255) NOT NULL,
    company_name VARCHAR(255),
    company_registration_number VARCHAR(50),
    
    -- Contact details
    email VARCHAR(255),
    phone VARCHAR(50),
    address TEXT,
    postcode VARCHAR(20),
    
    -- Client-specific settings
    reference_prefix VARCHAR(20),
    default_case_type casetype,
    settings JSON DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create enforcement_cases table
CREATE TABLE IF NOT EXISTS enforcement_cases (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign keys (required)
    debtor_id VARCHAR(36) NOT NULL REFERENCES debtors(id) ON DELETE RESTRICT,
    client_id VARCHAR(36) NOT NULL REFERENCES enforcement_clients(id) ON DELETE RESTRICT,
    
    -- Case reference (unique within tenant)
    case_reference VARCHAR(100) NOT NULL UNIQUE,
    client_reference VARCHAR(100),
    
    -- Case type and status
    case_type casetype NOT NULL,
    status casestatus NOT NULL DEFAULT 'draft',
    
    -- Legal basis
    legal_basis TEXT,
    court_reference VARCHAR(100),
    judgment_date TIMESTAMP WITH TIME ZONE,
    
    -- Financial data (all at Case level)
    original_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    fees_charged NUMERIC(12, 2) NOT NULL DEFAULT 0,
    payments_received NUMERIC(12, 2) NOT NULL DEFAULT 0,
    current_balance NUMERIC(12, 2) NOT NULL DEFAULT 0,
    
    -- Enforcement stage
    enforcement_stage VARCHAR(50),
    assigned_agent VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    
    -- Case-specific data
    notes TEXT,
    communications JSON DEFAULT '[]'::jsonb,
    visits JSON DEFAULT '[]'::jsonb,
    actions JSON DEFAULT '[]'::jsonb,
    notices JSON DEFAULT '[]'::jsonb,
    
    -- Risk flags
    risk_flags JSON DEFAULT '[]'::jsonb,
    
    -- AI-generated summaries
    ai_summary TEXT,
    
    -- Dates
    opened_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    closed_date TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create case_transactions table (immutable ledger)
CREATE TABLE IF NOT EXISTS case_transactions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign key to case (required)
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id) ON DELETE CASCADE,
    
    -- Transaction details
    transaction_type transactiontype NOT NULL,
    amount NUMERIC(12, 2) NOT NULL,
    description TEXT,
    
    -- Reference to payment (if applicable)
    payment_id VARCHAR(36),
    
    -- Transaction metadata
    reference VARCHAR(100),
    transaction_metadata JSON DEFAULT '{}'::jsonb,
    
    -- Created by
    created_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for performance
CREATE INDEX IF NOT EXISTS idx_debtors_tenant_id ON debtors(tenant_id);
CREATE INDEX IF NOT EXISTS idx_debtors_entity_type ON debtors(entity_type);
CREATE INDEX IF NOT EXISTS idx_debtors_legal_name ON debtors(legal_name);
CREATE INDEX IF NOT EXISTS idx_debtors_email ON debtors(email);
CREATE INDEX IF NOT EXISTS idx_debtors_company_registration ON debtors(company_registration_number) WHERE company_registration_number IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_enforcement_clients_tenant_id ON enforcement_clients(tenant_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_clients_name ON enforcement_clients(name);

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_id ON enforcement_cases(tenant_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_debtor_id ON enforcement_cases(debtor_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_client_id ON enforcement_cases(client_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_status ON enforcement_cases(status);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_case_reference ON enforcement_cases(case_reference);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_debtor_client ON enforcement_cases(debtor_id, client_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_assigned_agent ON enforcement_cases(assigned_agent) WHERE assigned_agent IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_case_transactions_tenant_id ON case_transactions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_transactions_case_id ON case_transactions(case_id);
CREATE INDEX IF NOT EXISTS idx_case_transactions_type ON case_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_case_transactions_case_type ON case_transactions(case_id, transaction_type);

-- Create case_notes table
CREATE TABLE IF NOT EXISTS case_notes (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign key to case (required)
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id) ON DELETE CASCADE,
    
    -- Note content
    note TEXT NOT NULL,
    original_note TEXT,
    
    -- AI improvements
    ai_improved_note TEXT,
    ai_summary TEXT,
    risk_flags JSON DEFAULT '[]'::jsonb,
    ai_processing_status VARCHAR(20) DEFAULT 'pending',
    
    -- Created by
    created_by VARCHAR(36) REFERENCES users(id) ON DELETE SET NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_case_notes_case_id ON case_notes(case_id);
CREATE INDEX IF NOT EXISTS idx_case_notes_created_by ON case_notes(created_by);

-- Add comments
COMMENT ON TABLE debtors IS 'Debtors represent real-world persons OR legal entities. Debtor-level data is shared across ALL cases.';
COMMENT ON TABLE enforcement_clients IS 'Clients represent the instructing organisation (creditor).';
COMMENT ON TABLE enforcement_cases IS 'Cases represent ONE enforcement instruction linking ONE Debtor to ONE Client. All financial data is at Case level.';
COMMENT ON TABLE case_transactions IS 'Immutable ledger for all monetary movement. All financial entities reference caseId, NOT debtorId.';

