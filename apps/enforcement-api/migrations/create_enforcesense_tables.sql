-- Migration: Create EnforceSense tables for Enforcement API
-- This migration creates the core EnforceSense tables: debtors, enforcement_cases
-- Based on Core Domain Model: Debtor, Client, Case
-- Note: This uses the same database as Platform API (shared database)

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
    
    -- Company fields
    company_registration_number VARCHAR(50),
    
    -- Contact
    email VARCHAR(255),
    phone VARCHAR(50),
    
    -- Address reference (can reference Platform API account/contact ID)
    address_ref VARCHAR(36),  -- Reference to Platform API entity
    
    -- Language preference for multilingual support
    preferred_language VARCHAR(5) DEFAULT 'en',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Indexes
    CONSTRAINT debtors_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_debtors_tenant_id ON debtors(tenant_id);
CREATE INDEX IF NOT EXISTS idx_debtors_legal_name ON debtors(legal_name);
CREATE INDEX IF NOT EXISTS idx_debtors_email ON debtors(email);

-- Create enforcement_cases table (if not exists)
CREATE TABLE IF NOT EXISTS enforcement_cases (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- References
    client_account_id VARCHAR(36),  -- Reference to Platform API account
    debtor_party_id VARCHAR(36) NOT NULL REFERENCES debtors(id) ON DELETE CASCADE,
    
    -- Case details
    case_reference VARCHAR(100) NOT NULL UNIQUE,
    case_type casetype,
    status casestatus DEFAULT 'draft' NOT NULL,
    
    -- Financial
    original_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    current_balance NUMERIC(10, 2) NOT NULL DEFAULT 0,
    fees_charged NUMERIC(10, 2) NOT NULL DEFAULT 0,
    payments_received NUMERIC(10, 2) NOT NULL DEFAULT 0,
    
    -- Timestamps
    opened_date TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraints
    CONSTRAINT enforcement_cases_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE,
    CONSTRAINT enforcement_cases_debtor_party_id_fkey FOREIGN KEY (debtor_party_id) REFERENCES debtors(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_id ON enforcement_cases(tenant_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_debtor_party_id ON enforcement_cases(debtor_party_id);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_case_reference ON enforcement_cases(case_reference);
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_status ON enforcement_cases(status);



