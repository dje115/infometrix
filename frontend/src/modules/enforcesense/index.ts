/**
 * EnforceSense Module Definition
 * 
 * EnforceSense module for debt recovery and enforcement.
 * Requires ENFORCESENSE_ENABLED feature flag to be enabled for the tenant.
 */

import { ModuleDefinition } from '../types';
import { MODULE_REGISTRY } from '../registry';

export const enforcesenseModule: ModuleDefinition = MODULE_REGISTRY.enforcesense;

export default enforcesenseModule;

