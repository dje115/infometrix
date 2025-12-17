/**
 * Module Switcher Component
 * 
 * Displays horizontal tabs at the top of the left drawer for switching between modules.
 * Only shows modules that are enabled for the tenant and allowed for the current user.
 */

import React from 'react';
import { Box, Tabs, Tab, Tooltip, Typography } from '@mui/material';
import {
  Dashboard as DashboardIcon,
  Support as SupportIcon,
  Description as DescriptionIcon,
  Gavel as GavelIcon,
  Settings as SettingsIcon,
} from '@mui/icons-material';
import { ModuleDefinition } from '../modules/types';
import { useActiveModule } from '../modules/hooks/useActiveModule';

// Map icon names to MUI icon components
const iconMap: Record<string, React.ComponentType> = {
  Dashboard: DashboardIcon,
  Support: SupportIcon,
  Description: DescriptionIcon,
  Gavel: GavelIcon,
  Settings: SettingsIcon,
};

interface ModuleSwitcherProps {
  enabledModules: ModuleDefinition[];
  onModuleChange?: (moduleKey: string) => void;
}

const ModuleSwitcher: React.FC<ModuleSwitcherProps> = ({
  enabledModules,
  onModuleChange,
}) => {
  const { activeModule, setActiveModule } = useActiveModule();

  const handleChange = (event: React.SyntheticEvent, newValue: string) => {
    setActiveModule(newValue);
    if (onModuleChange) {
      onModuleChange(newValue);
    }
  };

  // Get icon component for a module
  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName] || DashboardIcon;
    return <IconComponent />;
  };

  if (enabledModules.length === 0) {
    return (
      <Box sx={{ p: 2, textAlign: 'center' }}>
        <Typography variant="body2" color="text.secondary">
          No modules available
        </Typography>
      </Box>
    );
  }

  // Find current tab index
  const currentTabIndex = enabledModules.findIndex(
    (m) => m.key === activeModule
  );
  // Default to first module if activeModule not found or no active module
  const value = currentTabIndex >= 0 ? currentTabIndex : (enabledModules.length > 0 ? 0 : -1);

  return (
    <Box sx={{ borderBottom: 1, borderColor: 'divider' }}>
      <Tabs
        value={value >= 0 ? value : 0}
        onChange={handleChange}
        variant="scrollable"
        scrollButtons="auto"
        sx={{
          minHeight: 48,
          '& .MuiTab-root': {
            minHeight: 48,
            textTransform: 'none',
            fontSize: '0.875rem',
          },
        }}
      >
        {enabledModules.map((module, index) => (
          <Tab
            key={module.key}
            value={index}
            icon={getIcon(module.icon)}
            label={module.displayName}
            iconPosition="start"
            sx={{
              flexDirection: 'row',
              gap: 1,
              '& .MuiTab-iconWrapper': {
                marginRight: 1,
              },
            }}
          />
        ))}
      </Tabs>
    </Box>
  );
};

export default ModuleSwitcher;

