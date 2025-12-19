-- Migration: Add enabled_modules field to tenants table
-- This migration adds the enabled_modules JSONB field to track which modules are enabled per tenant
-- Default value is ["crm", "helpdesk"] for existing tenants

-- Add enabled_modules column if it doesn't exist
DO $$ 
BEGIN
    IF NOT EXISTS (
        SELECT 1 
        FROM information_schema.columns 
        WHERE table_name = 'tenants' 
        AND column_name = 'enabled_modules'
    ) THEN
        ALTER TABLE tenants 
        ADD COLUMN enabled_modules JSONB DEFAULT '["crm", "helpdesk"]'::jsonb;
        
        -- Update existing tenants to have default enabled modules
        UPDATE tenants 
        SET enabled_modules = '["crm", "helpdesk"]'::jsonb 
        WHERE enabled_modules IS NULL;
    END IF;
END $$;

-- Create index for enabled_modules if it doesn't exist (useful for queries)
CREATE INDEX IF NOT EXISTS idx_tenants_enabled_modules ON tenants USING GIN (enabled_modules);

