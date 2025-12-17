-- Migration: Add enabled_modules column to tenants table
-- Purpose: Store list of enabled modules per tenant (e.g., ["crm", "helpdesk"])
-- Date: 2025-12-17

-- Add enabled_modules column if it doesn't exist
ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS enabled_modules JSONB DEFAULT '[]'::jsonb;

-- Set default enabled modules for existing tenants
-- CRM and Helpdesk are enabled by default for existing tenants
UPDATE tenants 
SET enabled_modules = '["crm", "helpdesk"]'::jsonb
WHERE enabled_modules IS NULL OR enabled_modules = '[]'::jsonb;

-- Add comment for documentation
COMMENT ON COLUMN tenants.enabled_modules IS 'List of enabled module keys for this tenant. CRM is always enabled regardless of this list.';

