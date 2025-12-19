-- Migration: Create quotes table
-- This migration creates the quotes table if it doesn't exist

-- Create QuoteStatus enum type if it doesn't exist
DO $$ BEGIN
    CREATE TYPE quotestatus AS ENUM (
        'draft',
        'sent',
        'viewed',
        'accepted',
        'rejected',
        'expired',
        'cancelled'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create QuoteApprovalState enum type if it doesn't exist
DO $$ BEGIN
    CREATE TYPE quoteapprovalstate AS ENUM (
        'not_required',
        'pending',
        'approved',
        'rejected'
    );
EXCEPTION
    WHEN duplicate_object THEN null;
END $$;

-- Create quotes table
CREATE TABLE IF NOT EXISTS quotes (
    id VARCHAR(36) PRIMARY KEY,
    customer_id VARCHAR(36) REFERENCES customers(id),
    lead_id VARCHAR(36) REFERENCES leads(id),
    quote_number VARCHAR(100) NOT NULL UNIQUE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    quote_type VARCHAR(100),
    project_title VARCHAR(200),
    project_description TEXT,
    site_address TEXT,
    building_type VARCHAR(100),
    building_size FLOAT,
    number_of_floors INTEGER,
    number_of_rooms INTEGER,
    cabling_type VARCHAR(50),
    wifi_requirements BOOLEAN DEFAULT FALSE,
    cctv_requirements BOOLEAN DEFAULT FALSE,
    door_entry_requirements BOOLEAN DEFAULT FALSE,
    special_requirements TEXT,
    travel_distance_km FLOAT,
    travel_time_minutes FLOAT,
    travel_cost NUMERIC(10, 2),
    ai_analysis JSON,
    recommended_products JSON,
    labour_breakdown JSON,
    quotation_details JSON,
    clarifications_log JSON,
    ai_raw_response TEXT,
    estimated_time INTEGER,
    estimated_cost NUMERIC(10, 2),
    status quotestatus NOT NULL DEFAULT 'draft',
    approval_state quoteapprovalstate NOT NULL DEFAULT 'not_required',
    manual_mode BOOLEAN NOT NULL DEFAULT FALSE,
    version_number INTEGER NOT NULL DEFAULT 1,
    parent_quote_id VARCHAR(36) REFERENCES quotes(id),
    sent_at TIMESTAMP WITH TIME ZONE,
    accepted_at TIMESTAMP WITH TIME ZONE,
    rejected_at TIMESTAMP WITH TIME ZONE,
    cancelled_at TIMESTAMP WITH TIME ZONE,
    cancel_reason TEXT,
    valid_until TIMESTAMP WITH TIME ZONE,
    subtotal NUMERIC(10, 2) NOT NULL DEFAULT 0,
    tax_rate FLOAT NOT NULL DEFAULT 0.20,
    tax_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    total_amount NUMERIC(10, 2) NOT NULL DEFAULT 0,
    payment_terms VARCHAR(100),
    delivery_terms VARCHAR(100),
    notes TEXT,
    template_id VARCHAR(36) REFERENCES quote_templates(id),
    custom_fields JSON,
    viewed_at TIMESTAMP WITH TIME ZONE,
    viewed_count INTEGER NOT NULL DEFAULT 0,
    show_in_customer_portal BOOLEAN NOT NULL DEFAULT FALSE,
    tier_type VARCHAR(20) NOT NULL DEFAULT 'single',
    ai_generation_data JSON,
    last_prompt_text TEXT,
    created_by VARCHAR(36) REFERENCES users(id),
    tenant_id VARCHAR(36) NOT NULL REFERENCES tenants(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL,
    is_deleted BOOLEAN NOT NULL DEFAULT FALSE,
    deleted_at TIMESTAMP WITH TIME ZONE
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_quotes_customer_id ON quotes(customer_id);
CREATE INDEX IF NOT EXISTS idx_quotes_lead_id ON quotes(lead_id);
CREATE INDEX IF NOT EXISTS idx_quotes_tenant_id ON quotes(tenant_id);
CREATE INDEX IF NOT EXISTS idx_quotes_quote_type ON quotes(quote_type);
CREATE INDEX IF NOT EXISTS idx_quotes_status ON quotes(status);
CREATE INDEX IF NOT EXISTS idx_quotes_created_at ON quotes(created_at DESC);

