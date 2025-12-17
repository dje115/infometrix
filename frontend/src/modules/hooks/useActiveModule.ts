/**
 * React hook for managing active module state
 */

import { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { ModuleDefinition } from '../types';
import { getModule } from '../registry';

/**
 * Determine which module a route belongs to
 */
const getModuleForRoute = (pathname: string): string | null => {
  // Check each module's routes
  const modules = ['crm', 'helpdesk', 'quoting', 'enforcesense', 'settings'];
  
  for (const moduleKey of modules) {
    const module = getModule(moduleKey);
    if (!module) continue;

    // Check if pathname matches any route in this module
    for (const route of module.routes) {
      if (route.exact) {
        if (pathname === route.path) {
          return moduleKey;
        }
      } else {
        if (pathname.startsWith(route.path)) {
          return moduleKey;
        }
      }
    }
  }

  // Default to CRM if no match
  return 'crm';
};

interface UseActiveModuleReturn {
  activeModule: string | null;
  setActiveModule: (moduleKey: string) => void;
  getModuleDefinition: (moduleKey?: string) => ModuleDefinition | undefined;
}

/**
 * Hook to manage active module state based on current route
 */
export const useActiveModule = (): UseActiveModuleReturn => {
  const location = useLocation();
  const navigate = useNavigate();
  const [activeModule, setActiveModuleState] = useState<string | null>(null);

  // Determine active module from current route
  useEffect(() => {
    const moduleKey = getModuleForRoute(location.pathname);
    setActiveModuleState(moduleKey);
  }, [location.pathname]);

  // Set active module and navigate to its default route
  const setActiveModule = useCallback(
    (moduleKey: string) => {
      const module = getModule(moduleKey);
      if (module && module.defaultRoute) {
        navigate(module.defaultRoute);
      }
      setActiveModuleState(moduleKey);
    },
    [navigate]
  );

  const getModuleDefinition = useCallback(
    (moduleKey?: string): ModuleDefinition | undefined => {
      const key = moduleKey || activeModule;
      if (!key) return undefined;
      return getModule(key);
    },
    [activeModule]
  );

  return {
    activeModule,
    setActiveModule,
    getModuleDefinition,
  };
};

