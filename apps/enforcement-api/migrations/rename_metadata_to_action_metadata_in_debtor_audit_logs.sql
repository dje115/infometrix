-- Migration: Rename metadata column to action_metadata in debtor_audit_logs
-- Purpose: Avoid SQLAlchemy reserved word conflict
-- Date: 2025-12-25

-- Rename the column
ALTER TABLE debtor_audit_logs
RENAME COLUMN metadata TO action_metadata;

-- Add comment to document the change
COMMENT ON COLUMN debtor_audit_logs.action_metadata IS
'Additional context for the audit log entry (renamed from metadata to avoid SQLAlchemy reserved word conflict).';

