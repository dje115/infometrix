/**
 * React hook for accessing module data
 */

import { useState, useEffect } from 'react';
import apiClient from '../../services/api';
import { ModuleMetadata, EnabledModulesResponse } from '../types';
import { getEnabledModules, getAllModules, ModuleDefinition } from '../registry';

interface UseModulesReturn {
  modules: ModuleDefinition[];
  enabledModules: ModuleDefinition[];
  featureFlags: Record<string, boolean>;
  loading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
}

/**
 * Hook to fetch and manage module data from backend
 * 
 * If userPermissions and isAdmin are not provided, they will be read from localStorage
 */
export const useModules = (
  userPermissions?: string[],
  isAdmin?: boolean
): UseModulesReturn => {
  const [modules, setModules] = useState<ModuleDefinition[]>([]);
  const [enabledModules, setEnabledModules] = useState<ModuleDefinition[]>([]);
  const [featureFlags, setFeatureFlags] = useState<Record<string, boolean>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<Error | null>(null);

  const fetchModules = async () => {
    try {
      setLoading(true);
      setError(null);

      // Get user data from localStorage if not provided
      const user = JSON.parse(localStorage.getItem('user') || '{}');
      const effectivePermissions = userPermissions || user.permissions || [];
      const effectiveIsAdmin = isAdmin !== undefined ? isAdmin : 
        (user.role === 'super_admin' || user.role === 'admin' || user.role === 'tenant_admin');

      // Try to fetch from backend API
      try {
        const response = await apiClient.get<EnabledModulesResponse>('/modules');
        const data = response.data;

        // Update feature flags
        setFeatureFlags(data.feature_flags || {});

        // Get enabled modules based on feature flags
        const enabled = getEnabledModules(
          data.feature_flags || {},
          effectivePermissions,
          effectiveIsAdmin
        );
        setEnabledModules(enabled);

        // Also set all modules for reference
        setModules(getAllModules());
      } catch (apiError: any) {
        // If API endpoint doesn't exist yet or CORS/auth error, fall back to local registry
        // Don't log CORS errors as warnings - they're expected if backend is unreachable
        if (apiError?.code !== 'ERR_NETWORK' && apiError?.code !== 'ECONNABORTED') {
          console.warn('Module API not available, using local registry:', apiError?.message || apiError);
        }
        
        // Use default feature flags (all modules enabled by default)
        const defaultFlags: Record<string, boolean> = {
          HELPDESK_ENABLED: true,
          QUOTING_ENABLED: true,
          ENFORCESENSE_ENABLED: false,
        };

        setFeatureFlags(defaultFlags);
        const enabled = getEnabledModules(defaultFlags, effectivePermissions, effectiveIsAdmin);
        setEnabledModules(enabled);
        setModules(getAllModules());
      }
    } catch (err) {
      setError(err instanceof Error ? err : new Error('Failed to load modules'));
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    // Only fetch if we have user data
    const user = JSON.parse(localStorage.getItem('user') || '{}');
    if (user.id) {
      fetchModules();
    } else {
      // No user, use default modules
      setLoading(false);
      const defaultFlags: Record<string, boolean> = {
        HELPDESK_ENABLED: true,
        QUOTING_ENABLED: true,
        ENFORCESENSE_ENABLED: false,
      };
      setFeatureFlags(defaultFlags);
      const enabled = getEnabledModules(defaultFlags, [], false);
      setEnabledModules(enabled);
      setModules(getAllModules());
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []); // Only run once on mount to prevent flashing

  return {
    modules,
    enabledModules,
    featureFlags,
    loading,
    error,
    refresh: fetchModules,
  };
};

