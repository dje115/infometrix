-- Migration: Create case_status_history table
-- Purpose: Track case status changes for audit trail
-- Date: 2025-12-24

-- Create case_status_history table
CREATE TABLE IF NOT EXISTS case_status_history (
    id VARCHAR(36) PRIMARY KEY,
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    case_id VARCHAR(36) NOT NULL REFERENCES enforcement_cases(id) ON DELETE CASCADE,
    
    -- Status change details
    old_status casestatus,  -- Previous status (nullable for initial status)
    new_status casestatus NOT NULL,  -- New status
    
    -- User who made the change
    changed_by VARCHAR(36) NOT NULL,
    changed_by_email VARCHAR(255),
    changed_by_name VARCHAR(255),
    
    -- Change details
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    reason TEXT,
    notes TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for efficient queries
CREATE INDEX IF NOT EXISTS idx_case_status_history_tenant ON case_status_history(tenant_id);
CREATE INDEX IF NOT EXISTS idx_case_status_history_case ON case_status_history(case_id);
CREATE INDEX IF NOT EXISTS idx_case_status_history_changed_by ON case_status_history(changed_by);
CREATE INDEX IF NOT EXISTS idx_case_status_history_changed_at ON case_status_history(changed_at);
CREATE INDEX IF NOT EXISTS idx_case_status_history_case_changed ON case_status_history(case_id, changed_at);
CREATE INDEX IF NOT EXISTS idx_case_status_history_user_changed ON case_status_history(changed_by, changed_at);

-- Add comment to document the table
COMMENT ON TABLE case_status_history IS
'Case status change history. Tracks all status changes for a case, including who made the change and when.';

COMMENT ON COLUMN case_status_history.old_status IS
'Previous status before the change (NULL for initial status).';

COMMENT ON COLUMN case_status_history.reason IS
'Optional reason for the status change.';

