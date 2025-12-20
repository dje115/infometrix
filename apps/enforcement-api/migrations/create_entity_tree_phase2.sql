-- Migration: Create Entity Tree Phase 2 Models (Support & Flags)
-- Creates: PartySupportProfile, CaseSupportImpact, PartyProfile, PartyFlags, PartyRestrictions, ComplianceNote tables
-- Date: 2025-12-19

-- Create enum types
DO $$ BEGIN
    CREATE TYPE supportstatus AS ENUM (
        'NONE', 'ADVICE_SOUGHT', 'ADVISOR_ENGAGED', 
        'FORMAL_SOLUTION_PENDING', 'FORMAL_SOLUTION_ACTIVE'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE advisororg AS ENUM ('STEPCHANGE', 'CAB', 'NATIONAL_DEBTLINE', 'OTHER');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE evidencelevel AS ENUM ('SELF_REPORTED', 'ADVISOR_CONFIRMED', 'DOCUMENTED', 'OFFICIAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE supportaction AS ENUM (
        'HOLD', 'REDUCE_CONTACT', 'REFER_TO_COMPLIANCE', 
        'REQUEST_AUTHORITY', 'CONTINUE_ALLOWED'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE vulnerabilitycategory AS ENUM (
        'NONE', 'MENTAL_HEALTH', 'PHYSICAL_HEALTH', 'DISABILITY', 'BEREAVEMENT',
        'LANGUAGE_BARRIER', 'FINANCIAL_HARDSHIP', 'DOMESTIC_ABUSE_RISK', 
        'ELDERLY', 'PREGNANCY', 'CARE_LEAVER', 'OTHER'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE safetyrisk AS ENUM ('NONE', 'CAUTION', 'HIGH_RISK');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE disputestatus AS ENUM ('NONE', 'INFORMAL', 'FORMAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE contactmethod AS ENUM ('LETTER', 'EMAIL', 'PHONE', 'SMS', 'PORTAL');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE representationtype AS ENUM ('NONE', 'SOLICITOR', 'ADVISOR', 'FAMILY_MEMBER', 'OTHER');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE identityconfidence AS ENUM ('LOW', 'MED', 'HIGH');
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

DO $$ BEGIN
    CREATE TYPE compliancenotecategory AS ENUM (
        'VULNERABILITY_DETAILS', 'SAFETY_INCIDENT', 'DISPUTE_DETAILS',
        'FRAUD_INVESTIGATION', 'COMPLIANCE_REVIEW', 'DATA_PROTECTION', 'OTHER'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create party_support_profiles table
CREATE TABLE IF NOT EXISTS party_support_profiles (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    party_id VARCHAR(36) NOT NULL REFERENCES parties(id) ON DELETE CASCADE UNIQUE,
    
    -- Support status
    support_status supportstatus DEFAULT 'NONE' NOT NULL,
    advisor_org advisororg,
    reference_number VARCHAR(100),
    
    -- Dates
    effective_from TIMESTAMP WITH TIME ZONE,
    effective_to TIMESTAMP WITH TIME ZONE,
    
    -- Evidence
    evidence_level evidencelevel,
    notes TEXT,
    documents JSONB DEFAULT '[]'::jsonb,
    
    -- Review dates
    last_verified_at TIMESTAMP WITH TIME ZONE,
    next_review_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_party_support_profiles_tenant_id ON party_support_profiles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_party_support_profiles_party_id ON party_support_profiles(party_id);

-- Create case_support_impacts table
CREATE TABLE IF NOT EXISTS case_support_impacts (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id) ON DELETE CASCADE,
    party_id VARCHAR(36) NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    
    -- Support status at time
    support_status_at_time supportstatus NOT NULL,
    
    -- Action taken
    action_taken supportaction NOT NULL,
    hold_until TIMESTAMP WITH TIME ZONE,
    reason_code VARCHAR(50),
    
    -- Created by
    created_by VARCHAR(36),
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_case_support_impacts_tenant_id ON case_support_impacts(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_support_impacts_case_id ON case_support_impacts(case_id);
CREATE INDEX IF NOT EXISTS idx_case_support_impacts_party_id ON case_support_impacts(party_id);

-- Create party_profiles table
CREATE TABLE IF NOT EXISTS party_profiles (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    party_id VARCHAR(36) NOT NULL REFERENCES parties(id) ON DELETE CASCADE UNIQUE,
    
    -- Language and communication
    preferred_language VARCHAR(5) DEFAULT 'en' NOT NULL,
    interpreter_required BOOLEAN DEFAULT FALSE NOT NULL,
    preferred_contact_method contactmethod,
    
    -- Representation
    representation_type representationtype DEFAULT 'NONE' NOT NULL,
    representation_contact_name VARCHAR(255),
    representation_contact_details JSONB DEFAULT '{}'::jsonb,
    
    -- Identity
    identity_confidence identityconfidence,
    address_verified BOOLEAN DEFAULT FALSE NOT NULL,
    address_verification_date TIMESTAMP WITH TIME ZONE,
    known_aliases JSONB DEFAULT '[]'::jsonb,
    do_not_merge BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_party_profiles_tenant_id ON party_profiles(tenant_id);
CREATE INDEX IF NOT EXISTS idx_party_profiles_party_id ON party_profiles(party_id);

-- Create party_flags table
CREATE TABLE IF NOT EXISTS party_flags (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    party_id VARCHAR(36) NOT NULL REFERENCES parties(id) ON DELETE CASCADE UNIQUE,
    
    -- Vulnerability
    vulnerability_category vulnerabilitycategory,
    vulnerability_review_date TIMESTAMP WITH TIME ZONE,
    safeguarding_required BOOLEAN DEFAULT FALSE NOT NULL,
    safeguarding_review_date TIMESTAMP WITH TIME ZONE,
    
    -- Safety risk
    safety_risk safetyrisk DEFAULT 'NONE' NOT NULL,
    safety_risk_notes_required BOOLEAN DEFAULT FALSE NOT NULL,
    safety_risk_last_incident_date TIMESTAMP WITH TIME ZONE,
    no_doorstep_visits BOOLEAN DEFAULT FALSE NOT NULL,
    no_doorstep_visits_reason VARCHAR(50),
    no_call BOOLEAN DEFAULT FALSE NOT NULL,
    harassment_sensitivity BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- Dispute
    dispute_status disputestatus DEFAULT 'NONE' NOT NULL,
    representation_active BOOLEAN DEFAULT FALSE NOT NULL,
    data_restriction BOOLEAN DEFAULT FALSE NOT NULL,
    sar_in_progress BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- Fraud
    suspected_fraud BOOLEAN DEFAULT FALSE NOT NULL,
    impersonation_risk BOOLEAN DEFAULT FALSE NOT NULL,
    known_scam_reports BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- Address
    address_uncertainty VARCHAR(20),
    deceased BOOLEAN DEFAULT FALSE NOT NULL,
    dissolved BOOLEAN DEFAULT FALSE NOT NULL,
    deceased_dissolved_evidence_level evidencelevel,
    
    -- Financial behavior (derived flags)
    payment_plan_in_place BOOLEAN DEFAULT FALSE NOT NULL,
    affordability_review_date TIMESTAMP WITH TIME ZONE,
    payment_reliability_score VARCHAR(10),
    multiple_active_debts BOOLEAN DEFAULT FALSE NOT NULL,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_party_flags_tenant_id ON party_flags(tenant_id);
CREATE INDEX IF NOT EXISTS idx_party_flags_party_id ON party_flags(party_id);

-- Create party_restrictions table
CREATE TABLE IF NOT EXISTS party_restrictions (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    party_id VARCHAR(36) NOT NULL REFERENCES parties(id) ON DELETE CASCADE UNIQUE,
    
    -- Contact frequency limits
    contact_frequency_limit VARCHAR(20),
    contact_frequency_limit_reason TEXT,
    
    -- Channel blocks (JSON array)
    channel_blocks JSONB DEFAULT '[]'::jsonb,
    
    -- Compliance approval
    require_compliance_approval BOOLEAN DEFAULT FALSE NOT NULL,
    compliance_approval_required_for JSONB DEFAULT '[]'::jsonb,
    
    -- Restriction details
    restriction_effective_from TIMESTAMP WITH TIME ZONE NOT NULL,
    restriction_effective_to TIMESTAMP WITH TIME ZONE,
    restriction_reason TEXT,
    restriction_authorized_by VARCHAR(36),
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_party_restrictions_tenant_id ON party_restrictions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_party_restrictions_party_id ON party_restrictions(party_id);

-- Create compliance_notes table
CREATE TABLE IF NOT EXISTS compliance_notes (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    party_id VARCHAR(36) NOT NULL REFERENCES parties(id) ON DELETE CASCADE,
    case_id VARCHAR(36) REFERENCES enforcement_cases(id),
    
    -- Note details
    category compliancenotecategory NOT NULL,
    title VARCHAR(255) NOT NULL,
    note TEXT NOT NULL,
    evidence_level evidencelevel,
    documents JSONB DEFAULT '[]'::jsonb,
    
    -- Created by
    created_by VARCHAR(36) NOT NULL,
    
    -- Review workflow
    review_required BOOLEAN DEFAULT FALSE NOT NULL,
    review_date TIMESTAMP WITH TIME ZONE,
    reviewed_by VARCHAR(36),
    reviewed_at TIMESTAMP WITH TIME ZONE,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX IF NOT EXISTS idx_compliance_notes_tenant_id ON compliance_notes(tenant_id);
CREATE INDEX IF NOT EXISTS idx_compliance_notes_party_id ON compliance_notes(party_id);
CREATE INDEX IF NOT EXISTS idx_compliance_notes_case_id ON compliance_notes(case_id) WHERE case_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_compliance_notes_category ON compliance_notes(category);

