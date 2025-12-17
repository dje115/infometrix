-- Migration: Add feature_flags column to tenants table
-- Purpose: Enable tenant-level feature flags for module control
-- Date: 2025-01-XX

-- Add feature_flags JSONB column if it doesn't exist
ALTER TABLE tenants 
ADD COLUMN IF NOT EXISTS feature_flags JSONB DEFAULT '{}'::jsonb;

-- Add index for JSONB queries (optional, but useful for filtering)
CREATE INDEX IF NOT EXISTS idx_tenants_feature_flags ON tenants USING GIN (feature_flags);

-- Set default feature flags for existing tenants
UPDATE tenants 
SET feature_flags = '{
  "HELPDESK_ENABLED": true,
  "ENFORCESENSE_ENABLED": false,
  "QUOTING_ENABLED": true,
  "SALES_ENABLED": true
}'::jsonb
WHERE feature_flags IS NULL OR feature_flags = '{}'::jsonb;

-- Add comment
COMMENT ON COLUMN tenants.feature_flags IS 'Feature flags for enabling/disabling modules per tenant. Format: {"MODULE_ENABLED": true/false}';

