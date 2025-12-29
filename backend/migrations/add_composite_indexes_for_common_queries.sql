-- Migration: Add composite indexes for common query patterns
-- Purpose: Improve query performance for frequently used filter combinations
-- Date: 2025-01-27

-- Customer queries
CREATE INDEX IF NOT EXISTS idx_customers_tenant_status_deleted 
ON customers(tenant_id, status, is_deleted);

CREATE INDEX IF NOT EXISTS idx_customers_tenant_competitor_deleted 
ON customers(tenant_id, is_competitor, is_deleted);

-- Quote queries
CREATE INDEX IF NOT EXISTS idx_quotes_customer_status_deleted 
ON quotes(customer_id, status, is_deleted) 
WHERE customer_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_quotes_tenant_status_deleted 
ON quotes(tenant_id, status, is_deleted);

CREATE INDEX IF NOT EXISTS idx_quotes_lead_status_deleted 
ON quotes(lead_id, status, is_deleted) 
WHERE lead_id IS NOT NULL;

-- Ticket queries
CREATE INDEX IF NOT EXISTS idx_tickets_customer_status_deleted 
ON tickets(customer_id, status, is_deleted) 
WHERE customer_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_tickets_tenant_type_status 
ON tickets(tenant_id, ticket_type, status);

-- Contact queries
CREATE INDEX IF NOT EXISTS idx_contacts_customer_deleted 
ON contacts(customer_id, is_deleted);

-- Sales activity queries
CREATE INDEX IF NOT EXISTS idx_sales_activities_customer_date 
ON sales_activities(customer_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_sales_activities_tenant_date 
ON sales_activities(tenant_id, created_at DESC);

-- Customer interaction queries
CREATE INDEX IF NOT EXISTS idx_customer_interactions_customer_type 
ON customer_interactions(customer_id, interaction_type);

-- Quote item queries
CREATE INDEX IF NOT EXISTS idx_quote_items_quote_deleted 
ON quote_items(quote_id, is_deleted);



