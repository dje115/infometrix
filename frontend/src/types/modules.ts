/**
 * Module system types for Infometrix platform
 */

export interface MenuItem {
  text: string;
  icon: string; // Icon name (MUI icon component name)
  path: string;
  permission?: string;
  adminOnly?: boolean;
}

export interface MenuGroup {
  id: string;
  label: string;
  featureFlag?: string;
  items: MenuItem[];
}

export interface ModuleNavigation {
  module_id: string;
  module_name: string;
  items: MenuItem[];
}

/**
 * Core navigation groups (not module-based)
 */
export const CORE_NAVIGATION_GROUPS: MenuGroup[] = [
  {
    id: 'sales-crm',
    label: 'Sales / CRM',
    items: [
      { text: 'Dashboard', icon: 'Dashboard', path: '/dashboard' },
      { text: 'Customers', icon: 'People', path: '/customers' },
      { text: 'Leads', icon: 'PersonAdd', path: '/leads-crm' },
      { text: 'Discoveries', icon: 'TrendingUp', path: '/leads' },
      { text: 'Opportunities', icon: 'Work', path: '/opportunities' },
      { text: 'Campaigns', icon: 'Campaign', path: '/campaigns' },
      { text: 'Planning', icon: 'Architecture', path: '/planning-applications' },
    ]
  },
  {
    id: 'quoting',
    label: 'Quoting & Proposals',
    featureFlag: 'QUOTING_ENABLED',
    items: [
      { text: 'Quotes', icon: 'Description', path: '/quotes' },
      { text: 'Contracts', icon: 'Description', path: '/contracts' },
      { text: 'Contract Templates', icon: 'Description', path: '/contracts/templates' },
    ]
  },
  {
    id: 'helpdesk',
    label: 'Helpdesk',
    featureFlag: 'HELPDESK_ENABLED',
    items: [
      { text: 'Helpdesk', icon: 'Support', path: '/helpdesk', permission: 'helpdesk:view_tickets' },
      { text: 'Helpdesk Performance', icon: 'Assessment', path: '/helpdesk/performance', permission: 'helpdesk:view' },
      { text: 'NPA Dashboard', icon: 'Assignment', path: '/helpdesk/npa-dashboard', permission: 'helpdesk:view' },
      { text: 'Knowledge Base', icon: 'Psychology', path: '/helpdesk/knowledge-base', permission: 'helpdesk:view' },
      { text: 'Ticket Templates', icon: 'Description', path: '/helpdesk/templates', permission: 'helpdesk:admin' },
      { text: 'Ticket Macros', icon: 'Build', path: '/helpdesk/macros', permission: 'helpdesk:admin' },
      { text: 'SLA Management', icon: 'Assessment', path: '/sla', permission: 'helpdesk:sla_manage' },
      { text: 'SLA Dashboard', icon: 'Assessment', path: '/sla/dashboard', permission: 'helpdesk:sla_view' },
      { text: 'SLA Reports', icon: 'Assessment', path: '/sla/reports', permission: 'helpdesk:sla_view' },
    ]
  },
  {
    id: 'enforcesense',
    label: 'EnforceSense',
    featureFlag: 'ENFORCESENSE_ENABLED',
    items: [
      { text: 'EnforceSense Dashboard', icon: 'Gavel', path: '/enforcesense', permission: 'enforcesense:view' },
      { text: 'Cases', icon: 'Folder', path: '/enforcesense/cases', permission: 'enforcesense:view_cases' },
      { text: 'Debtors', icon: 'People', path: '/enforcesense/debtors', permission: 'enforcesense:view' },
      { text: 'Clients', icon: 'Business', path: '/enforcesense/clients', permission: 'enforcesense:view' },
      { text: 'Reports', icon: 'Assessment', path: '/enforcesense/reports', permission: 'enforcesense:view' },
    ]
  },
  {
    id: 'settings',
    label: 'Settings',
    items: [
      { text: 'Settings', icon: 'Settings', path: '/settings' },
      { text: 'Users', icon: 'Group', path: '/users' },
      { text: 'Compliance', icon: 'Security', path: '/compliance', adminOnly: true },
      { text: 'AI Prompts', icon: 'Psychology', path: '/prompts', adminOnly: true },
      { text: 'Suppliers', icon: 'LocalShipping', path: '/suppliers' },
      { text: 'Competitors', icon: 'Business', path: '/competitors' },
      { text: 'Trends', icon: 'Timeline', path: '/trends' },
      { text: 'Metrics', icon: 'Assessment', path: '/metrics' },
    ]
  },
];

