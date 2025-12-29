-- Migration: Add missing foreign key indexes
-- Purpose: Improve query performance for foreign key lookups
-- Date: 2025-01-27

-- Customer interactions
CREATE INDEX IF NOT EXISTS idx_customer_interactions_contact_id 
ON customer_interactions(contact_id) 
WHERE contact_id IS NOT NULL;

-- Tickets
CREATE INDEX IF NOT EXISTS idx_tickets_created_by_user_id 
ON tickets(created_by_user_id) 
WHERE created_by_user_id IS NOT NULL;

-- Quotes
CREATE INDEX IF NOT EXISTS idx_quotes_created_by 
ON quotes(created_by) 
WHERE created_by IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_quotes_parent_quote_id 
ON quotes(parent_quote_id) 
WHERE parent_quote_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_quotes_template_id 
ON quotes(template_id) 
WHERE template_id IS NOT NULL;

-- Quote items
CREATE INDEX IF NOT EXISTS idx_quote_items_supplier_id 
ON quote_items(supplier_id) 
WHERE supplier_id IS NOT NULL;

-- SLA breach alerts
CREATE INDEX IF NOT EXISTS idx_sla_breach_alerts_acknowledged_by 
ON sla_breach_alerts(acknowledged_by) 
WHERE acknowledged_by IS NOT NULL;

-- Support contracts
CREATE INDEX IF NOT EXISTS idx_support_contracts_cancelled_by 
ON support_contracts(cancelled_by) 
WHERE cancelled_by IS NOT NULL;

-- Contract renewals
CREATE INDEX IF NOT EXISTS idx_contract_renewals_reminder_sent_to 
ON contract_renewals(reminder_sent_to) 
WHERE reminder_sent_to IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_contract_renewals_approved_by 
ON contract_renewals(approved_by) 
WHERE approved_by IS NOT NULL;

-- Supplier pricing
CREATE INDEX IF NOT EXISTS idx_supplier_pricing_verified_by 
ON supplier_pricing(verified_by) 
WHERE verified_by IS NOT NULL;

-- Product content history
CREATE INDEX IF NOT EXISTS idx_product_content_history_verified_by 
ON product_content_history(verified_by) 
WHERE verified_by IS NOT NULL;



