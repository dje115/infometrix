# EnforceSense Module

## Overview

The EnforceSense module provides debt recovery and enforcement capabilities integrated with the Infometrix platform. This module links clients from the CRM to debtors and manages debt recovery cases.

## Status

**Current Status**: Skeleton/Placeholder - Under Development

This module is currently in the initial development phase. The skeleton provides:
- Module structure and routing
- Placeholder pages (Dashboard, Cases, Reports)
- Integration with Infometrix module system
- Backend models and API structure

## Module Configuration

- **Module Key**: `enforcesense`
- **Feature Flag**: `ENFORCESENSE_ENABLED`
- **Enabled By Default**: No (requires feature flag)

## Routes

- `/enforcesense` - EnforceSense dashboard
- `/enforcesense/cases` - Case management
- `/enforcesense/reports` - Reports and analytics

## Permissions

- `enforcesense:view` - View EnforceSense content
- `enforcesense:view_cases` - View cases
- `enforcesense:create_case` - Create cases
- `enforcesense:update_case` - Update cases
- `enforcesense:admin` - Admin access

## Core Concepts

### Client
- Links to CRM Customer/Account
- The party that is owed the debt

### Debtor
- Person or company that owes the debt
- Can be linked to multiple cases

### Case
- Links a Client (from CRM) to a Debtor
- Tracks debt recovery progress
- Has status, amount, and case number

## File Structure

```
modules/enforcesense/
├── pages/
│   ├── EnforceSenseDashboard.tsx
│   ├── Cases.tsx
│   └── Reports.tsx
├── index.ts
├── routes.tsx
├── types.ts
└── README.md
```

## Integration

The EnforceSense module integrates with:

1. **CRM Module**: Links cases to CRM customers (clients)
2. **Module Registry**: Registered in `frontend/src/modules/registry.ts`
3. **Backend Module**: Defined in `backend/app/modules/enforcesense/module.py`
4. **Routes**: Registered in `frontend/src/App.tsx`

## Future Development

- Complete case management UI
- Debtor management
- Integration with external debt recovery services
- Reporting and analytics
- Workflow automation
- Document management

