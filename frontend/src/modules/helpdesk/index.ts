/**
 * Helpdesk Module
 * 
 * This module provides ticket management, SLA tracking, and knowledge base functionality.
 */

export { default as Helpdesk } from './pages/Helpdesk';
export { default as TicketDetail } from './pages/TicketDetail';
export { default as HelpdeskPerformance } from './pages/HelpdeskPerformance';
export { default as KnowledgeBase } from './pages/KnowledgeBase';
export { default as TicketTemplates } from './pages/TicketTemplates';
export { default as TicketMacros } from './pages/TicketMacros';
export { default as SLAManagement } from './pages/SLAManagement';
export { default as SLADashboard } from './pages/SLADashboard';
export { default as SLAReportBuilder } from './pages/SLAReportBuilder';

// Feature flag key for this module
export const HELPDESK_FEATURE_FLAG = 'HELPDESK_ENABLED';

// Module metadata
export const HELPDESK_MODULE_ID = 'helpdesk';
export const HELPDESK_MODULE_NAME = 'Helpdesk';



