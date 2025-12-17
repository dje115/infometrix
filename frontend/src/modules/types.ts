/**
 * Module system type definitions for Infometrix platform
 */

import { ReactNode } from 'react';

/**
 * Navigation item within a module
 */
export interface ModuleNavItem {
  text: string;
  icon: string; // MUI icon component name (e.g., "Dashboard", "People")
  path: string;
  permission?: string; // Required permission (e.g., "helpdesk:view")
  adminOnly?: boolean; // If true, requires admin role
}

/**
 * Route definition for a module
 */
export interface ModuleRoute {
  path: string;
  component: string; // Component name or path
  permission?: string;
  exact?: boolean;
}

/**
 * Module definition
 */
export interface ModuleDefinition {
  key: string; // Unique module identifier (e.g., "crm", "helpdesk")
  displayName: string; // Human-readable name
  icon: string; // MUI icon component name for module switcher
  enabledByDefault: boolean; // If true, always enabled (like CRM)
  featureFlagKey?: string; // Feature flag key (e.g., "HELPDESK_ENABLED")
  routes: ModuleRoute[]; // Module routes
  navItems: ModuleNavItem[]; // Navigation items for context menu
  defaultRoute?: string; // Default route when module is activated
}

/**
 * Module metadata from backend
 */
export interface ModuleMetadata {
  module_id: string;
  module_name: string;
  feature_flag: string;
  version: string;
  permissions: string[];
  navigation_items: Array<{
    text: string;
    icon: string;
    path: string;
    permission?: string;
    adminOnly?: boolean;
  }>;
}

/**
 * Enabled modules response from API
 */
export interface EnabledModulesResponse {
  modules: ModuleMetadata[];
  feature_flags: Record<string, boolean>;
}

