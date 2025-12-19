-- Migration: Create Entity Tree Phase 1 Models
-- Creates: Party, PartyRole, DebtAccount, CaseDebts tables
-- Date: 2025-12-19

-- Create enum types
DO $$ BEGIN
    CREATE TYPE partytype AS ENUM ('INDIVIDUAL', 'ORGANISATION');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE partyroletype AS ENUM ('DEBTOR', 'JOINT_DEBTOR', 'GUARANTOR', 'DIRECTOR', 'THIRD_PARTY', 'VULNERABLE_PERSON');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE debtaccountstatus AS ENUM ('ACTIVE', 'SETTLED', 'DISPUTED', 'STAYED', 'WRITTEN_OFF');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE debtaccounttype AS ENUM ('INVOICE', 'JUDGMENT', 'CONTRACT', 'COUNCIL_TAX', 'BUSINESS_RATES', 'PARKING_FINE', 'OTHER');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create parties table (replaces debtors)
CREATE TABLE IF NOT EXISTS parties (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Party type (required)
    party_type partytype NOT NULL,
    
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
    trading_names JSONB DEFAULT '[]'::jsonb,
    
    -- Contact details
    email VARCHAR(255),
    phone VARCHAR(50),
    
    -- Address history (JSON array)
    address_history JSONB DEFAULT '[]'::jsonb,
    
    -- Communication preferences
    language_preference VARCHAR(5) DEFAULT 'en',
    communication_preferences JSONB DEFAULT '{}'::jsonb,
    
    -- External references
    external_references JSONB DEFAULT '{}'::jsonb,
    
    -- AI summary
    ai_summary TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for parties
CREATE INDEX IF NOT EXISTS idx_parties_tenant_id ON parties(tenant_id);
CREATE INDEX IF NOT EXISTS idx_parties_legal_name ON parties(legal_name);
CREATE INDEX IF NOT EXISTS idx_parties_email ON parties(email);
CREATE INDEX IF NOT EXISTS idx_parties_company_reg ON parties(company_registration_number) WHERE company_registration_number IS NOT NULL;

-- Create party_roles table
CREATE TABLE IF NOT EXISTS party_roles (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign keys
    party_id VARCHAR(36) NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id) ON DELETE CASCADE,
    
    -- Role
    role partyroletype NOT NULL,
    is_primary BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for party_roles
CREATE INDEX IF NOT EXISTS idx_party_roles_tenant_id ON party_roles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_party_roles_party_id ON party_roles(party_id);
CREATE INDEX IF NOT EXISTS idx_party_roles_case_id ON party_roles(case_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_party_role_unique ON party_roles(party_id, case_id, role);

-- Create debt_accounts table
CREATE TABLE IF NOT EXISTS debt_accounts (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign keys
    client_account_id VARCHAR(36) NOT NULL,  -- FK to Customer/Account in CRM (will be added later)
    debtor_party_id VARCHAR(36) NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    
    -- Debt reference (unique within tenant)
    debt_reference VARCHAR(100) NOT NULL,
    client_reference VARCHAR(100),
    invoice_reference VARCHAR(100),
    contract_reference VARCHAR(100),
    court_reference VARCHAR(100),
    
    -- Financial details
    principal_amount NUMERIC(12, 2) NOT NULL,
    currency VARCHAR(3) DEFAULT 'GBP' NOT NULL,
    
    -- Interest rules (JSON)
    interest_rules JSONB DEFAULT '{}'::jsonb,
    
    -- Fee rules (JSON)
    fee_rules JSONB DEFAULT '{}'::jsonb,
    
    -- Status and type
    status debtaccountstatus DEFAULT 'ACTIVE' NOT NULL,
    debt_type debtaccounttype NOT NULL,
    
    -- Dates
    due_date TIMESTAMP WITH TIME ZONE,
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE,
    is_deleted BOOLEAN DEFAULT FALSE NOT NULL,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for debt_accounts
CREATE INDEX IF NOT EXISTS idx_debt_accounts_tenant_id ON debt_accounts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_debt_accounts_client_account_id ON debt_accounts(client_account_id);
CREATE INDEX IF NOT EXISTS idx_debt_accounts_debtor_party_id ON debt_accounts(debtor_party_id);
CREATE INDEX IF NOT EXISTS idx_debt_accounts_debt_reference ON debt_accounts(debt_reference);
CREATE INDEX IF NOT EXISTS idx_debt_accounts_client_reference ON debt_accounts(client_reference) WHERE client_reference IS NOT NULL;
CREATE UNIQUE INDEX IF NOT EXISTS idx_debt_account_reference ON debt_accounts(tenant_id, debt_reference);

-- Create case_debts table (join table)
CREATE TABLE IF NOT EXISTS case_debts (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    
    -- Foreign keys
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id) ON DELETE CASCADE,
    debt_account_id VARCHAR(36) NOT NULL REFERENCES debt_accounts(id) ON DELETE CASCADE,
    
    -- Allocation (optional)
    allocation_percentage NUMERIC(5, 2),
    allocation_amount NUMERIC(12, 2),
    
    -- Priority order
    priority_order INTEGER DEFAULT 0 NOT NULL,
    
    -- Flags
    is_primary BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- Notes
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes for case_debts
CREATE INDEX IF NOT EXISTS idx_case_debts_tenant_id ON case_debts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_debts_case_id ON case_debts(case_id);
CREATE INDEX IF NOT EXISTS idx_case_debts_debt_account_id ON case_debts(debt_account_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_case_debts_unique ON case_debts(case_id, debt_account_id);

