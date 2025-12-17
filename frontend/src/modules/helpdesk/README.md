# Helpdesk Module

## Overview

The Helpdesk module provides comprehensive ticket management, SLA tracking, and knowledge base functionality for the Infometrix platform.

## Features

- **Ticket Management**: Create, view, update, and manage support tickets
- **SLA Tracking**: Monitor and manage Service Level Agreements
- **Knowledge Base**: Maintain and search knowledge base articles
- **Ticket Templates**: Create reusable ticket templates
- **Ticket Macros**: Automate common ticket actions
- **NPA Dashboard**: Track Non-Productive Activities
- **Performance Analytics**: Monitor helpdesk performance metrics

## Module Configuration

- **Module Key**: `helpdesk`
- **Feature Flag**: `HELPDESK_ENABLED`
- **Enabled By Default**: No (requires feature flag)

## Routes

- `/helpdesk` - Main helpdesk ticket list
- `/helpdesk/ticket/:id` - Ticket detail page
- `/helpdesk/performance` - Performance dashboard
- `/helpdesk/npa-dashboard` - NPA dashboard
- `/helpdesk/knowledge-base` - Knowledge base
- `/helpdesk/templates` - Ticket templates management
- `/helpdesk/macros` - Ticket macros management
- `/sla` - SLA management
- `/sla/dashboard` - SLA dashboard
- `/sla/reports` - SLA reports

## Permissions

- `helpdesk:view` - View helpdesk content
- `helpdesk:view_tickets` - View tickets
- `helpdesk:create_ticket` - Create tickets
- `helpdesk:update_ticket` - Update tickets
- `helpdesk:delete_ticket` - Delete tickets
- `helpdesk:assign_ticket` - Assign tickets
- `helpdesk:admin` - Admin access (templates, macros)
- `helpdesk:sla_view` - View SLA data
- `helpdesk:sla_manage` - Manage SLA policies

## File Structure

```
modules/helpdesk/
├── pages/
│   ├── Helpdesk.tsx
│   ├── TicketDetail.tsx
│   ├── HelpdeskPerformance.tsx
│   ├── KnowledgeBase.tsx
│   ├── TicketTemplates.tsx
│   ├── TicketMacros.tsx
│   ├── SLAManagement.tsx
│   ├── SLADashboard.tsx
│   └── SLAReportBuilder.tsx
├── components/
│   ├── TicketComposer.tsx
│   ├── TicketBulkActions.tsx
│   ├── TicketChatbot.tsx
│   ├── TicketKBAnswer.tsx
│   ├── TicketLinkDialog.tsx
│   ├── TicketMacroMenu.tsx
│   ├── TicketMergeDialog.tsx
│   ├── TicketNPA.tsx
│   ├── TicketTemplateSelector.tsx
│   ├── NPADashboard.tsx
│   ├── CustomerSLAWidget.tsx
│   └── CustomerSLAHistory.tsx
├── index.ts
├── routes.tsx
└── README.md
```

## Integration

The Helpdesk module is integrated into the Infometrix platform through:

1. **Module Registry**: Registered in `frontend/src/modules/registry.ts`
2. **Backend Module**: Defined in `backend/app/modules/helpdesk/module.py`
3. **Routes**: Registered in `frontend/src/App.tsx`
4. **Navigation**: Appears in module switcher when `HELPDESK_ENABLED` is true

## Dependencies

- Backend API: `/api/v1/helpdesk/*` and `/api/v1/sla/*`
- Shared Components: Uses components from `frontend/src/components/` for shared UI elements
- Services: Uses `helpdeskAPI` and `slaAPI` from `frontend/src/services/api`

