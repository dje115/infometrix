/**
 * Settings Module Definition
 * 
 * Settings is always enabled for all tenants (no feature flag required).
 * Provides platform configuration and administration features.
 */

import { ModuleDefinition } from '../types';
import { MODULE_REGISTRY } from '../registry';

export const settingsModule: ModuleDefinition = MODULE_REGISTRY.settings;

export default settingsModule;

