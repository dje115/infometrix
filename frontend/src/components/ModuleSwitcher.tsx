/**
 * Module Switcher Component
 * 
 * Displays module tabs at the top of the left navigation.
 * Allows users to switch between different modules (CRM, Helpdesk, etc.)
 */

import React, { useState, useEffect } from 'react';
import { Tabs, Tab, Box, Typography } from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import { MODULE_REGISTRY, getEnabledModules, ModuleConfig } from '../modules/registry';
import { settingsAPI } from '../services/api';

interface ModuleSwitcherProps {
  enabledModules?: string[];
  featureFlags?: Record<string, boolean>;
  onModuleChange?: (moduleId: string) => void;
}

const ModuleSwitcher: React.FC<ModuleSwitcherProps> = ({
  enabledModules = [],
  featureFlags = {},
  onModuleChange,
}) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [currentModule, setCurrentModule] = useState<string>('crm');

  // Get enabled modules based on tenant config
  const availableModules = getEnabledModules(enabledModules, featureFlags);

  // Determine current module based on route
  useEffect(() => {
    const path = location.pathname;
    
    // Check which module this route belongs to
    for (const moduleId of availableModules) {
      const module = MODULE_REGISTRY[moduleId];
      if (module?.navigationGroupId) {
        // Check if path matches this module's routes
        // For now, we'll use navigation group matching
        if (path.startsWith('/helpdesk') && moduleId === 'helpdesk') {
          setCurrentModule('helpdesk');
          return;
        }
        if (path.startsWith('/enforcesense') && moduleId === 'enforcesense') {
          setCurrentModule('enforcesense');
          return;
        }
        if (path.startsWith('/quotes') && moduleId === 'quoting') {
          setCurrentModule('quoting');
          return;
        }
      }
    }
    
    // Default to CRM if no match
    if (path.startsWith('/dashboard') || 
        path.startsWith('/customers') || 
        path.startsWith('/leads') ||
        path.startsWith('/opportunities') ||
        path.startsWith('/campaigns')) {
      setCurrentModule('crm');
    }
  }, [location.pathname, availableModules]);

  const handleModuleChange = (_event: React.SyntheticEvent, newModule: string) => {
    setCurrentModule(newModule);
    
    // Navigate to default route for the module
    const module = MODULE_REGISTRY[newModule];
    if (module) {
      if (newModule === 'crm') {
        navigate('/dashboard');
      } else if (newModule === 'helpdesk') {
        navigate('/helpdesk');
      } else if (newModule === 'enforcesense') {
        navigate('/enforcesense');
      } else if (newModule === 'quoting') {
        navigate('/quotes');
      }
      
      // Notify parent component
      if (onModuleChange) {
        onModuleChange(newModule);
      }
    }
  };

  // Don't render if only one module is available
  if (availableModules.length <= 1) {
    return null;
  }

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider', mb: 1 }}>
      <Tabs
        value={currentModule}
        onChange={handleModuleChange}
        variant="scrollable"
        scrollButtons="auto"
        sx={{
          minHeight: 48,
          '& .MuiTab-root': {
            minHeight: 48,
            textTransform: 'none',
            fontSize: '0.875rem',
            fontWeight: 500,
          },
        }}
      >
        {availableModules.map((moduleId) => {
          const module = MODULE_REGISTRY[moduleId];
          if (!module) return null;
          
          return (
            <Tab
              key={moduleId}
              label={module.name}
              value={moduleId}
              sx={{
                textTransform: 'none',
              }}
            />
          );
        })}
      </Tabs>
    </Box>
  );
};

export default ModuleSwitcher;

