-- Migration: Add customer_id foreign key to enforcement_clients
-- Purpose: Link EnforcementClient to main CRM Customer
-- Date: 2025-12-24

-- Add customer_id column (nullable for existing records)
ALTER TABLE enforcement_clients 
ADD COLUMN IF NOT EXISTS customer_id VARCHAR(36);

-- Add foreign key constraint (SET NULL on delete to preserve enforcement data if customer deleted)
ALTER TABLE enforcement_clients 
ADD CONSTRAINT fk_enforcement_clients_customer_id 
FOREIGN KEY (customer_id) 
REFERENCES customers(id) 
ON DELETE SET NULL;

-- Add index for performance
CREATE INDEX IF NOT EXISTS idx_enforcement_clients_customer_id 
ON enforcement_clients(customer_id);

-- Add comment to document the relationship
COMMENT ON COLUMN enforcement_clients.customer_id IS 
'Link to main CRM Customer. Clients are managed in main CRM. EnforcementClient contains enforcement-specific settings only.';

