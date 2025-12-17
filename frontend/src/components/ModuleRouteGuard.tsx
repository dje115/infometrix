/**
 * Module Route Guard Component
 * 
 * Protects routes by checking:
 * 1. Module is enabled for the tenant (feature flag)
 * 2. User has required permissions
 * 
 * Redirects to appropriate page if access is denied.
 */

import React, { useEffect, useState } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { Box, CircularProgress, Alert, Typography, Button } from '@mui/material';
import { useModules } from '../modules/hooks/useModules';
import { getModule } from '../modules/registry';
import { ModuleDefinition } from '../modules/types';

interface ModuleRouteGuardProps {
  children: React.ReactNode;
  moduleKey: string;
  requiredPermission?: string;
  adminOnly?: boolean;
}

const ModuleRouteGuard: React.FC<ModuleRouteGuardProps> = ({
  children,
  moduleKey,
  requiredPermission,
  adminOnly = false,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [isAuthorized, setIsAuthorized] = useState<boolean | null>(null);
  const [loading, setLoading] = useState(true);

  // Get user data
  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const userPermissions = user.permissions || [];
  const isAdmin = user.role === 'super_admin' || user.role === 'admin' || user.role === 'tenant_admin';

  // Get modules data
  const { enabledModules, featureFlags, loading: modulesLoading } = useModules(userPermissions, isAdmin);

  useEffect(() => {
    const checkAuthorization = () => {
      setLoading(true);

      // Get module definition
      const module = getModule(moduleKey);
      if (!module) {
        console.error(`Module ${moduleKey} not found in registry`);
        setIsAuthorized(false);
        setLoading(false);
        return;
      }

      // Check if module is enabled
      // Always-enabled modules (like CRM, Settings) don't need feature flag check
      if (!module.enabledByDefault && module.featureFlagKey) {
        const isEnabled = featureFlags[module.featureFlagKey] ?? false;
        if (!isEnabled) {
          setIsAuthorized(false);
          setLoading(false);
          return;
        }
      }

      // Check admin-only requirement
      if (adminOnly && !isAdmin) {
        setIsAuthorized(false);
        setLoading(false);
        return;
      }

      // Check permission requirement
      if (requiredPermission) {
        if (!userPermissions.includes(requiredPermission) && !isAdmin) {
          setIsAuthorized(false);
          setLoading(false);
          return;
        }
      }

      // All checks passed
      setIsAuthorized(true);
      setLoading(false);
    };

    // Wait for modules to load
    if (!modulesLoading) {
      checkAuthorization();
    }
  }, [moduleKey, requiredPermission, adminOnly, userPermissions, isAdmin, featureFlags, modulesLoading]);

  // Show loading state
  if (loading || modulesLoading) {
    return (
      <Box
        sx={{
          display: 'flex',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '50vh',
        }}
      >
        <CircularProgress />
      </Box>
    );
  }

  // Show unauthorized message
  if (isAuthorized === false) {
    const module = getModule(moduleKey);
    const moduleName = module?.displayName || moduleKey;

    return (
      <Box
        sx={{
          display: 'flex',
          flexDirection: 'column',
          justifyContent: 'center',
          alignItems: 'center',
          minHeight: '50vh',
          p: 4,
        }}
      >
        <Alert severity="error" sx={{ mb: 2, maxWidth: 600 }}>
          <Typography variant="h6" gutterBottom>
            Access Denied
          </Typography>
          <Typography variant="body2" paragraph>
            You don't have permission to access the {moduleName} module.
          </Typography>
          {requiredPermission && (
            <Typography variant="body2" color="text.secondary">
              Required permission: {requiredPermission}
            </Typography>
          )}
          {adminOnly && (
            <Typography variant="body2" color="text.secondary">
              Admin access required
            </Typography>
          )}
        </Alert>
        <Button
          variant="contained"
          onClick={() => navigate('/dashboard')}
          sx={{ mt: 2 }}
        >
          Go to Dashboard
        </Button>
      </Box>
    );
  }

  // Authorized - render children
  return <>{children}</>;
};

export default ModuleRouteGuard;

