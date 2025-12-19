-- Migration: Create full EnforceSense tables for Enforcement API
-- This migration creates all EnforceSense tables: debtors, enforcement_clients, enforcement_cases, case_transactions, case_notes
-- Based on Core Domain Model: Debtor, Client, Case

-- Create enum types (idempotent)
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

-- Create debtors table (if not exists)
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
    
    -- Company fields
    company_registration_number VARCHAR(50),
    
    -- Trading names/aliases
    trading_names JSON DEFAULT '[]'::jsonb,
    
    -- Contact
    email VARCHAR(255),
    phone VARCHAR(50),
    
    -- Address history
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Indexes
    CONSTRAINT debtors_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_debtors_tenant_id ON debtors(tenant_id);
CREATE INDEX IF NOT EXISTS idx_debtors_legal_name ON debtors(legal_name);
CREATE INDEX IF NOT EXISTS idx_debtors_email ON debtors(email);
CREATE INDEX IF NOT EXISTS idx_debtors_company_registration_number ON debtors(company_registration_number);

-- Create enforcement_clients table (if not exists)
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT enforcement_clients_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_enforcement_clients_tenant_id ON enforcement_clients(tenant_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_clients_name ON enforcement_clients(name);

-- Create enforcement_cases table (if not exists)
CREATE TABLE IF NOT EXISTS enforcement_cases (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- References
    debtor_id VARCHAR(36) NOT NULL REFERENCES debtors(id) ON DELETE CASCADE,
    client_id VARCHAR(36) NOT NULL REFERENCES enforcement_clients(id) ON DELETE CASCADE,
    
    -- Case reference (unique within tenant)
    case_reference VARCHAR(100) NOT NULL UNIQUE,
    client_reference VARCHAR(100),
    
    -- Case type and status
    case_type casetype NOT NULL,
    status casestatus DEFAULT 'draft' NOT NULL,
    
    -- Legal basis
    legal_basis TEXT,
    court_reference VARCHAR(100),
    judgment_date TIMESTAMP WITH TIME ZONE,
    
    -- Financial data (all at Case level, NOT Debtor level)
    original_amount NUMERIC(12, 2) NOT NULL DEFAULT 0,
    fees_charged NUMERIC(12, 2) NOT NULL DEFAULT 0,
    payments_received NUMERIC(12, 2) NOT NULL DEFAULT 0,
    current_balance NUMERIC(12, 2) NOT NULL DEFAULT 0,
    
    -- Enforcement stage/status details
    enforcement_stage VARCHAR(50),
    assigned_agent VARCHAR(36),  -- Reference to Platform API user ID
    
    -- Case-specific notes and communications
    notes TEXT,
    communications JSON DEFAULT '[]'::jsonb,
    
    -- Visits, actions, notices
    visits JSON DEFAULT '[]'::jsonb,
    actions JSON DEFAULT '[]'::jsonb,
    notices JSON DEFAULT '[]'::jsonb,
    
    -- Case-level risk flags
    risk_flags JSON DEFAULT '[]'::jsonb,
    
    -- AI-generated summaries
    ai_summary TEXT,
    
    -- Dates
    opened_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    closed_date TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT enforcement_cases_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT enforcement_cases_debtor_id_fkey FOREIGN KEY (debtor_id) REFERENCES debtors(id) ON DELETE CASCADE,
    CONSTRAINT enforcement_cases_client_id_fkey FOREIGN KEY (client_id) REFERENCES enforcement_clients(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_id ON enforcement_cases(tenant_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_debtor_id ON enforcement_cases(debtor_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_client_id ON enforcement_cases(client_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_case_reference ON enforcement_cases(case_reference);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_status ON enforcement_cases(status);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_client_reference ON enforcement_cases(client_reference);

-- Create case_transactions table (if not exists)
CREATE TABLE IF NOT EXISTS case_transactions (
    id VARCHAR(36) PRIMARY KEY,
    
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
    
    -- Timestamps
    transaction_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT case_transactions_case_id_fkey FOREIGN KEY (case_id) REFERENCES enforcement_cases(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_case_transactions_case_id ON case_transactions(case_id);
CREATE INDEX IF NOT EXISTS idx_case_transactions_transaction_type ON case_transactions(transaction_type);
CREATE INDEX IF NOT EXISTS idx_case_transactions_transaction_date ON case_transactions(transaction_date);

-- Create case_notes table (if not exists)
CREATE TABLE IF NOT EXISTS case_notes (
    id VARCHAR(36) PRIMARY KEY,
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id) ON DELETE CASCADE,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Note content
    note TEXT NOT NULL,  -- Current note (may be AI-improved)
    original_note TEXT,  -- Original note (never changed)
    
    -- AI improvements
    ai_improved_note TEXT,  -- AI-cleaned version
    ai_summary TEXT,  -- AI-generated summary
    risk_flags JSON DEFAULT '[]'::jsonb,  -- Risk flags detected by AI
    ai_processing_status VARCHAR(20) DEFAULT 'pending',  -- pending, processing, completed, failed
    
    -- Created by
    created_by VARCHAR(36),  -- Reference to Platform API user ID
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT case_notes_case_id_fkey FOREIGN KEY (case_id) REFERENCES enforcement_cases(id) ON DELETE CASCADE,
    CONSTRAINT case_notes_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_case_notes_case_id ON case_notes(case_id);
CREATE INDEX IF NOT EXISTS idx_case_notes_tenant_id ON case_notes(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_notes_created_by ON case_notes(created_by);

