-- Migration: Create debtor_audit_logs table
-- Purpose: Track who accesses debtor records for audit and compliance
-- Date: 2025-12-24

-- Create debtor_audit_logs table
CREATE TABLE IF NOT EXISTS debtor_audit_logs (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    debtor_id VARCHAR(36) NOT NULL REFERENCES debtors(id) ON DELETE CASCADE,
    
    -- User who accessed the record
    user_id VARCHAR(36) NOT NULL,
    user_email VARCHAR(255),
    user_name VARCHAR(255),
    
    -- Access details
    accessed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),  -- IPv4 or IPv6
    user_agent VARCHAR(500),  -- Browser/client info
    
    -- Additional context
    action_type VARCHAR(50) NOT NULL DEFAULT 'view',  -- view, edit, export, etc.
    metadata JSON DEFAULT '{}'::jsonb,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_debtor_audit_tenant ON debtor_audit_logs(tenant_id);
CREATE INDEX IF NOT EXISTS idx_debtor_audit_debtor ON debtor_audit_logs(debtor_id);
CREATE INDEX IF NOT EXISTS idx_debtor_audit_user ON debtor_audit_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_debtor_audit_accessed ON debtor_audit_logs(accessed_at);
CREATE INDEX IF NOT EXISTS idx_debtor_audit_debtor_accessed ON debtor_audit_logs(debtor_id, accessed_at);
CREATE INDEX IF NOT EXISTS idx_debtor_audit_user_accessed ON debtor_audit_logs(user_id, accessed_at);

-- Add comment to document the table
COMMENT ON TABLE debtor_audit_logs IS
'Audit log for debtor record access. Tracks who views/accesses debtor records and when for compliance and security.';

COMMENT ON COLUMN debtor_audit_logs.action_type IS
'Type of action: view, edit, export, etc.';

COMMENT ON COLUMN debtor_audit_logs.metadata IS
'Additional context about the access (JSON object).';

