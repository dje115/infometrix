/**
 * Frontend Module Registry
 * 
 * Single source of truth for all modules in Infometrix platform.
 * Modules define their routes, navigation items, and permissions.
 */

import { ModuleDefinition } from './types';

/**
 * Get icon component by name
 * This will be used to dynamically render MUI icons
 */
export const getIconComponent = (iconName: string): string => {
  // Return the icon name - Layout will map it to actual MUI icon component
  return iconName;
};

/**
 * Module Registry
 * 
 * All modules must be registered here with their complete definitions.
 */
export const MODULE_REGISTRY: Record<string, ModuleDefinition> = {
  crm: {
    key: 'crm',
    displayName: 'CRM',
    icon: 'Dashboard',
    enabledByDefault: true, // Always enabled
    routes: [
      { path: '/dashboard', component: 'Dashboard', exact: true },
      { path: '/customers', component: 'Customers' },
      { path: '/leads-crm', component: 'LeadsCRM' },
      { path: '/leads', component: 'Leads' },
      { path: '/opportunities', component: 'Opportunities' },
      { path: '/campaigns', component: 'Campaigns' },
      { path: '/planning-applications', component: 'PlanningApplications' },
    ],
    navItems: [
      { text: 'Dashboard', icon: 'Dashboard', path: '/dashboard' },
      { text: 'Customers', icon: 'People', path: '/customers' },
      { text: 'Leads', icon: 'PersonAdd', path: '/leads-crm' },
      { text: 'Discoveries', icon: 'TrendingUp', path: '/leads' },
      { text: 'Opportunities', icon: 'Work', path: '/opportunities' },
      { text: 'Campaigns', icon: 'Campaign', path: '/campaigns' },
      { text: 'Planning', icon: 'Architecture', path: '/planning-applications' },
    ],
    defaultRoute: '/dashboard',
  },

  helpdesk: {
    key: 'helpdesk',
    displayName: 'Helpdesk',
    icon: 'Support',
    enabledByDefault: false,
    featureFlagKey: 'HELPDESK_ENABLED',
    routes: [
      { path: '/helpdesk', component: 'Helpdesk', exact: true },
      { path: '/helpdesk/performance', component: 'HelpdeskPerformance' },
      { path: '/helpdesk/npa-dashboard', component: 'NPADashboard' },
      { path: '/helpdesk/knowledge-base', component: 'KnowledgeBase' },
      { path: '/helpdesk/templates', component: 'TicketTemplates', permission: 'helpdesk:admin' },
      { path: '/helpdesk/macros', component: 'TicketMacros', permission: 'helpdesk:admin' },
      { path: '/sla', component: 'SLAManagement', permission: 'helpdesk:sla_manage' },
      { path: '/sla/dashboard', component: 'SLADashboard', permission: 'helpdesk:sla_view' },
      { path: '/sla/reports', component: 'SLAReportBuilder', permission: 'helpdesk:sla_view' },
    ],
    navItems: [
      { text: 'Helpdesk', icon: 'Support', path: '/helpdesk', permission: 'helpdesk:view_tickets' },
      { text: 'Helpdesk Performance', icon: 'Assessment', path: '/helpdesk/performance', permission: 'helpdesk:view' },
      { text: 'NPA Dashboard', icon: 'Assignment', path: '/helpdesk/npa-dashboard', permission: 'helpdesk:view' },
      { text: 'Knowledge Base', icon: 'Psychology', path: '/helpdesk/knowledge-base', permission: 'helpdesk:view' },
      { text: 'Ticket Templates', icon: 'Description', path: '/helpdesk/templates', permission: 'helpdesk:admin' },
      { text: 'Ticket Macros', icon: 'Build', path: '/helpdesk/macros', permission: 'helpdesk:admin' },
      { text: 'SLA Management', icon: 'Assessment', path: '/sla', permission: 'helpdesk:sla_manage' },
      { text: 'SLA Dashboard', icon: 'Assessment', path: '/sla/dashboard', permission: 'helpdesk:sla_view' },
      { text: 'SLA Reports', icon: 'Assessment', path: '/sla/reports', permission: 'helpdesk:sla_view' },
    ],
    defaultRoute: '/helpdesk',
  },

  quoting: {
    key: 'quoting',
    displayName: 'Quoting',
    icon: 'Description',
    enabledByDefault: false,
    featureFlagKey: 'QUOTING_ENABLED',
    routes: [
      { path: '/quotes', component: 'Quotes' },
      { path: '/contracts', component: 'Contracts' },
      { path: '/contract-templates', component: 'ContractTemplates' },
    ],
    navItems: [
      { text: 'Quotes', icon: 'Description', path: '/quotes' },
      { text: 'Contracts', icon: 'Description', path: '/contracts' },
      { text: 'Contract Templates', icon: 'Description', path: '/contract-templates' },
    ],
    defaultRoute: '/quotes',
  },

  enforcesense: {
    key: 'enforcesense',
    displayName: 'EnforceSense',
    icon: 'Gavel',
    enabledByDefault: false,
    featureFlagKey: 'ENFORCESENSE_ENABLED',
    routes: [
      { path: '/enforcesense', component: 'EnforceSenseDashboard', exact: true },
      { path: '/enforcesense/cases', component: 'Cases', permission: 'enforcesense:view_cases' },
      { path: '/enforcesense/reports', component: 'Reports', permission: 'enforcesense:view' },
    ],
    navItems: [
      { text: 'EnforceSense Dashboard', icon: 'Gavel', path: '/enforcesense', permission: 'enforcesense:view' },
      { text: 'Cases', icon: 'Folder', path: '/enforcesense/cases', permission: 'enforcesense:view_cases' },
      { text: 'Reports', icon: 'Assessment', path: '/enforcesense/reports', permission: 'enforcesense:view' },
    ],
    defaultRoute: '/enforcesense',
  },

  settings: {
    key: 'settings',
    displayName: 'Settings',
    icon: 'Settings',
    enabledByDefault: true, // Always enabled
    routes: [
      { path: '/settings', component: 'Settings' },
      { path: '/users', component: 'Users' },
      { path: '/compliance', component: 'Compliance', adminOnly: true },
      { path: '/prompts', component: 'PromptManagement', adminOnly: true },
      { path: '/suppliers', component: 'Suppliers' },
      { path: '/competitors', component: 'Competitors' },
      { path: '/trends', component: 'TrendsDashboard' },
      { path: '/metrics', component: 'MetricsDashboard' },
    ],
    navItems: [
      { text: 'Settings', icon: 'Settings', path: '/settings' },
      { text: 'Users', icon: 'Group', path: '/users' },
      { text: 'Compliance', icon: 'Security', path: '/compliance', adminOnly: true },
      { text: 'AI Prompts', icon: 'Psychology', path: '/prompts', adminOnly: true },
      { text: 'Suppliers', icon: 'LocalShipping', path: '/suppliers' },
      { text: 'Competitors', icon: 'Business', path: '/competitors' },
      { text: 'Trends', icon: 'Timeline', path: '/trends' },
      { text: 'Metrics', icon: 'Assessment', path: '/metrics' },
    ],
    defaultRoute: '/settings',
  },
};

/**
 * Get module definition by key
 */
export const getModule = (key: string): ModuleDefinition | undefined => {
  return MODULE_REGISTRY[key];
};

/**
 * Get all modules
 */
export const getAllModules = (): ModuleDefinition[] => {
  return Object.values(MODULE_REGISTRY);
};

/**
 * Get enabled modules based on feature flags
 */
export const getEnabledModules = (
  featureFlags: Record<string, boolean>,
  userPermissions: string[] = [],
  isAdmin: boolean = false
): ModuleDefinition[] => {
  return getAllModules().filter((module) => {
    // Always enabled modules
    if (module.enabledByDefault) {
      return true;
    }

    // Check feature flag
    if (module.featureFlagKey) {
      const isEnabled = featureFlags[module.featureFlagKey] ?? false;
      if (!isEnabled) {
        return false;
      }
    }

    // Check if user has at least one permission for this module
    // For now, we'll show the module if feature flag is enabled
    // Permission checks happen at route/nav item level
    return true;
  });
};

/**
 * Get navigation items for a module, filtered by permissions
 */
export const getModuleNavItems = (
  moduleKey: string,
  userPermissions: string[] = [],
  isAdmin: boolean = false
): ModuleDefinition['navItems'] => {
  const module = getModule(moduleKey);
  if (!module) {
    return [];
  }

  return module.navItems.filter((item) => {
    // Check adminOnly flag
    if (item.adminOnly && !isAdmin) {
      return false;
    }

    // Check permission
    if (item.permission) {
      return userPermissions.includes(item.permission);
    }

    // No permission required
    return true;
  });
};

