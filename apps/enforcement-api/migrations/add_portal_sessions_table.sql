-- Migration: Create portal_sessions table for Debtor Portal token-based authentication
-- This table stores secure tokens for debtor portal access

CREATE TABLE IF NOT EXISTS portal_sessions (
    id VARCHAR(36) PRIMARY KEY,
    token VARCHAR(255) NOT NULL UNIQUE,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    case_id VARCHAR(36) NOT NULL,  -- Reference to enforcement_cases.id
    debtor_id VARCHAR(36) NOT NULL,  -- Reference to debtors.id
    case_reference VARCHAR(100) NOT NULL,  -- For lookup without joining
    
    -- Token metadata
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_accessed_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    
    -- Rate limiting
    access_count INTEGER DEFAULT 0,
    last_access_ip VARCHAR(45),  -- IPv4 or IPv6
    
    -- Status
    is_revoked BOOLEAN DEFAULT FALSE,
    revoked_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraints
    CONSTRAINT portal_sessions_tenant_id_fkey FOREIGN KEY (tenant_id) REFERENCES tenants(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_portal_sessions_token ON portal_sessions(token);
CREATE INDEX IF NOT EXISTS idx_portal_sessions_case_id ON portal_sessions(case_id);
CREATE INDEX IF NOT EXISTS idx_portal_sessions_tenant_id ON portal_sessions(tenant_id);
CREATE INDEX IF NOT EXISTS idx_portal_sessions_expires_at ON portal_sessions(expires_at);
CREATE INDEX IF NOT EXISTS idx_portal_sessions_case_reference ON portal_sessions(case_reference);

