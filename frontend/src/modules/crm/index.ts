/**
 * CRM Module Definition
 * 
 * CRM is always enabled for all tenants (no feature flag required).
 * This is the core module of the Infometrix platform.
 */

import { ModuleDefinition } from '../types';
import { MODULE_REGISTRY } from '../registry';

export const crmModule: ModuleDefinition = MODULE_REGISTRY.crm;

export default crmModule;

