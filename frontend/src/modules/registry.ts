/**
 * Module Registry - Central registry for all platform modules
 * 
 * This registry defines which modules are available, their configuration,
 * and how they integrate with the navigation system.
 */

export interface ModuleConfig {
  id: string;
  name: string;
  enabledByDefault: boolean;
  featureFlag?: string;
  routes?: string[];
  navigationGroupId?: string;
}

/**
 * Available modules in the platform
 */
export const MODULE_REGISTRY: Record<string, ModuleConfig> = {
  crm: {
    id: 'crm',
    name: 'Sales / CRM',
    enabledByDefault: true, // CRM is always enabled
    navigationGroupId: 'sales-crm',
  },
  helpdesk: {
    id: 'helpdesk',
    name: 'Helpdesk',
    enabledByDefault: true, // Enabled by default for existing tenants
    featureFlag: 'HELPDESK_ENABLED',
    navigationGroupId: 'helpdesk',
  },
  quoting: {
    id: 'quoting',
    name: 'Quoting & Proposals',
    enabledByDefault: false,
    featureFlag: 'QUOTING_ENABLED',
    navigationGroupId: 'quoting',
  },
  enforcesense: {
    id: 'enforcesense',
    name: 'EnforceSense',
    enabledByDefault: false,
    featureFlag: 'ENFORCESENSE_ENABLED',
    navigationGroupId: 'enforcesense',
  },
};

/**
 * Get all modules that should be enabled by default
 */
export function getDefaultEnabledModules(): string[] {
  return Object.values(MODULE_REGISTRY)
    .filter(module => module.enabledByDefault)
    .map(module => module.id);
}

/**
 * Get module configuration by ID
 */
export function getModuleConfig(moduleId: string): ModuleConfig | undefined {
  return MODULE_REGISTRY[moduleId];
}

/**
 * Get all module IDs
 */
export function getAllModuleIds(): string[] {
  return Object.keys(MODULE_REGISTRY);
}

/**
 * Check if a module is enabled for a tenant
 * 
 * @param moduleId - Module identifier
 * @param enabledModules - Array of enabled module IDs from tenant
 * @param featureFlags - Tenant feature flags object
 * @returns true if module is enabled
 */
export function isModuleEnabled(
  moduleId: string,
  enabledModules: string[],
  featureFlags?: Record<string, boolean>
): boolean {
  const module = MODULE_REGISTRY[moduleId];
  if (!module) return false;

  // Check if module is in enabledModules list
  if (enabledModules.includes(moduleId)) {
    // If module has a feature flag, also check that
    if (module.featureFlag && featureFlags) {
      return featureFlags[module.featureFlag] === true;
    }
    return true;
  }

  // If not explicitly enabled, check if it's enabled by default
  if (module.enabledByDefault) {
    // Still check feature flag if present
    if (module.featureFlag && featureFlags) {
      return featureFlags[module.featureFlag] !== false; // Default enabled unless explicitly disabled
    }
    return true;
  }

  return false;
}

/**
 * Get enabled modules for a tenant
 * 
 * @param enabledModules - Array of enabled module IDs from tenant
 * @param featureFlags - Tenant feature flags object
 * @returns Array of enabled module IDs
 */
export function getEnabledModules(
  enabledModules: string[],
  featureFlags?: Record<string, boolean>
): string[] {
  return getAllModuleIds().filter(moduleId =>
    isModuleEnabled(moduleId, enabledModules, featureFlags)
  );
}

