/**
 * Helpdesk Module Routes
 * 
 * Defines all routes for the Helpdesk module.
 * These routes are registered in App.tsx.
 */

// Routes are defined in the module registry
// This file can be used for route-specific logic if needed in the future

export const helpdeskRoutes = {
  helpdesk: '/helpdesk',
  ticketDetail: '/helpdesk/ticket/:id',
  performance: '/helpdesk/performance',
  npaDashboard: '/helpdesk/npa-dashboard',
  knowledgeBase: '/helpdesk/knowledge-base',
  templates: '/helpdesk/templates',
  macros: '/helpdesk/macros',
  slaManagement: '/sla',
  slaDashboard: '/sla/dashboard',
  slaReports: '/sla/reports',
};

export default helpdeskRoutes;

