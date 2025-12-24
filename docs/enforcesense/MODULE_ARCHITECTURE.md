# EnforceSense Module Architecture

**Version:** 1.0  
**Last Updated:** 2025-12-24  
**Status:** MANDATORY - Core Architecture Document

## Overview

EnforceSense is a **module** within the Infometrix platform. This document clarifies the critical architectural principles that apply to EnforceSense and all future business-type modules.

---

## 1. MODULE PRINCIPLE

### EnforceSense is a Module, Not a Core Feature

- **EnforceSense is OPTIONAL** - Not all tenants will have this module enabled
- **Module access is controlled by feature flags** - Per-tenant enablement
- **Other business-type modules will follow the same pattern** - Future modules for different business types will be structured similarly

### Module vs. Core Platform

| Component | Location | Purpose |
|-----------|----------|---------|
| **Core CRM** | Main platform | Customer/Account management, sales cycles, lead management, opportunities |
| **EnforceSense Module** | Module | Enforcement-specific features: cases, debtors, enforcement workflows |
| **Other Modules** | Modules | Business-type specific features (e.g., future modules for other industries) |

---

## 2. CLIENT/CUSTOMER ARCHITECTURE

### Critical Principle: Clients Live in Main CRM

**EnforceSense clients ARE main CRM customers.**

- **All client data is managed in the main CRM** (`customers` table)
- **Sales teams need full CRM functionality** - Lead management, opportunities, sales cycles, account management
- **EnforceSense links to CRM customers** - Does NOT duplicate client data

### Data Flow

```
Main CRM (Core Platform)
├── Customer (company_name, status, contacts, sales activities, opportunities)
│   ├── Sales pipeline management
│   ├── Account management
│   ├── Contact management
│   └── Commercial relationship tracking
│
└── EnforceSense Module (when enabled)
    └── EnforcementClient (links to Customer via customer_id FK)
        ├── Enforcement-specific settings (reference_prefix, default_case_type)
        ├── Enforcement-specific configuration (portal policies, commercial terms)
        ├── Case management features
        └── Enforcement reporting & data imports
```

### EnforcementClient Model

The `EnforcementClient` model in EnforceSense:

- **MUST link to main CRM Customer** via `customer_id` foreign key
- **Contains enforcement-specific data only**:
  - `reference_prefix` - For case reference generation
  - `default_case_type` - Default enforcement case type
  - `settings` - Enforcement-specific configuration (JSON)
- **DOES NOT duplicate CRM data**:
  - Name, address, contact details come from CRM Customer
  - Sales activities, opportunities, contacts managed in CRM

### EnforceSense "Clients" Menu Section

The EnforceSense "Clients" section in the UI provides **enforcement-specific features**:

- **Data imports from clients** - CSV uploads, API integrations
- **Client reporting** - Enforcement-specific reports and analytics
- **Client portal configuration** - Portal access, upload permissions
- **Enforcement commercial terms** - Fee structures, allocation rules
- **Case management by client** - Client-specific case views and filters

**NOT for:**
- Creating new clients (done in main CRM)
- Managing client contacts (done in main CRM)
- Sales pipeline management (done in main CRM)
- Account management (done in main CRM)

---

## 3. INTEGRATION PATTERNS

### 3.1 Creating an Enforcement Client

**Workflow:**
1. Client is created/managed in **main CRM** (Customer record)
2. When EnforceSense module is enabled for tenant:
   - EnforcementClient record is created/updated automatically
   - Links to Customer via `customer_id`
   - Syncs basic data (name, company_name) from Customer
3. Enforcement-specific settings are configured in EnforceSense "Clients" section

### 3.2 Data Synchronization

**One-way sync (CRM → EnforceSense):**
- Customer name, company_name → EnforcementClient
- Customer status changes → May affect EnforcementClient visibility
- Customer deletion → Soft-delete EnforcementClient (or prevent if active cases exist)

**Enforcement-specific data (EnforceSense only):**
- Case references, enforcement settings, portal policies
- Enforcement reporting data
- Case upload configurations

### 3.3 API Access

**Main CRM API:**
- `/api/v1/customers/*` - Full customer management
- Used by sales team, account managers

**EnforceSense API:**
- `/api/v1/modules/enforcesense/clients/*` - Enforcement-specific client features
- Links to CRM customers via `customer_id`
- Used by enforcement operations team

---

## 4. UI/NAVIGATION STRUCTURE

### Main CRM Navigation

```
CRM
├── Customers (main client management)
│   ├── List all customers
│   ├── Customer detail (sales, contacts, opportunities)
│   └── Customer creation/editing
├── Leads
├── Opportunities
└── Sales Activities
```

### EnforceSense Module Navigation

```
EnforceSense (module - only visible if enabled)
├── Dashboard
├── Cases
├── Debtors
├── Clients (enforcement-specific features)
│   ├── Client data imports
│   ├── Client reporting
│   ├── Portal configuration
│   └── Enforcement settings
└── Reports
```

**Note:** The EnforceSense "Clients" section shows enforcement-specific features. To manage the client itself (name, contacts, sales), users navigate to the main CRM "Customers" section.

---

## 5. MULTI-TENANCY & MODULE ISOLATION

### Tenant Module Enablement

- **Feature flags control module visibility** per tenant
- **Tenant A** (enforcement business) → EnforceSense enabled
- **Tenant B** (different business type) → EnforceSense disabled, other modules enabled
- **Tenant C** (general business) → No modules, just core CRM

### Data Isolation

- **CRM customers are tenant-scoped** (existing CRM isolation)
- **EnforcementClient links respect tenant boundaries**
- **Module data is isolated per tenant** (enforcement cases, debtors)

---

## 6. FUTURE MODULES

This architecture pattern applies to **all future business-type modules**:

### Example: Future "Healthcare Module"

```
Main CRM (Core Platform)
├── Customer (managed in CRM)
│
└── Healthcare Module (when enabled)
    └── HealthcareClient (links to Customer via customer_id FK)
        ├── Healthcare-specific settings
        ├── Healthcare workflows
        └── Healthcare reporting
```

**Same principles:**
- Clients live in main CRM
- Module provides business-type-specific features
- Module links to CRM customers
- Module has its own "Clients" section for business-specific features

---

## 7. IMPLEMENTATION REQUIREMENTS

### Database Schema

```sql
-- EnforcementClient MUST have customer_id FK
ALTER TABLE enforcement_clients 
ADD COLUMN customer_id VARCHAR(36) REFERENCES customers(id) ON DELETE SET NULL;

-- Index for performance
CREATE INDEX idx_enforcement_clients_customer_id ON enforcement_clients(customer_id);
```

### API Endpoints

**EnforceSense Client endpoints should:**
- Accept `customer_id` when creating EnforcementClient
- Return linked Customer data in responses
- Provide enforcement-specific features only
- Redirect to main CRM API for customer management

### Frontend Integration

**EnforceSense Client pages should:**
- Display linked Customer information (read-only, from CRM)
- Show "View in CRM" link to main customer record
- Focus on enforcement-specific features
- Not duplicate CRM customer management UI

---

## 8. MIGRATION PATH

### Existing EnforcementClient Records

For existing EnforcementClient records without `customer_id`:

1. **Manual linking** - Admin UI to link EnforcementClient to Customer
2. **Auto-matching** - Match by name/company_name (with confirmation)
3. **Create Customer** - Option to create Customer from EnforcementClient if no match

### Data Migration

- Sync existing EnforcementClient data to Customer records
- Link EnforcementClient to Customer via `customer_id`
- Preserve enforcement-specific settings in EnforcementClient

---

## Summary

**Key Points:**
1. ✅ EnforceSense is a **module** - not all tenants have it
2. ✅ **Clients are in main CRM** - sales teams need full CRM functionality
3. ✅ **EnforceSense links to CRM customers** - via `customer_id` foreign key
4. ✅ **EnforceSense "Clients" section** - enforcement-specific features only
5. ✅ **Same pattern for future modules** - other business types follow this architecture

This architecture ensures:
- Sales teams have full CRM functionality
- Enforcement teams have enforcement-specific features
- No data duplication
- Clear separation of concerns
- Scalable pattern for future modules

