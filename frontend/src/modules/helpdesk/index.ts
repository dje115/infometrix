/**
 * Helpdesk Module Definition
 * 
 * Helpdesk module for ticket management, SLA tracking, and knowledge base.
 * Requires HELPDESK_ENABLED feature flag to be enabled for the tenant.
 */

import { ModuleDefinition } from '../types';
import { MODULE_REGISTRY } from '../registry';

export const helpdeskModule: ModuleDefinition = MODULE_REGISTRY.helpdesk;

export default helpdeskModule;

