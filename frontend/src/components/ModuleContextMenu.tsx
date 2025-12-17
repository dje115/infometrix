/**
 * Module Context Menu Component
 * 
 * Displays navigation items for the active module below the module switcher.
 * Filters items by user permissions and respects adminOnly flags.
 */

import React from 'react';
import {
  List,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
} from '@mui/material';
import { useNavigate, useLocation } from 'react-router-dom';
import {
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  PersonAdd as PersonAddIcon,
  TrendingUp as TrendingUpIcon,
  Work as WorkIcon,
  Campaign as CampaignIcon,
  Architecture as ArchitectureIcon,
  Support as SupportIcon,
  Assessment as AssessmentIcon,
  Assignment as AssignmentIcon,
  Psychology as PsychologyIcon,
  Description as DescriptionIcon,
  Build as BuildIcon,
  Gavel as GavelIcon,
  Folder as FolderIcon,
  Settings as SettingsIcon,
  Group as GroupIcon,
  Security as SecurityIcon,
  LocalShipping as LocalShippingIcon,
  Business as BusinessIcon,
  Timeline as TimelineIcon,
} from '@mui/icons-material';
import { ModuleNavItem } from '../modules/types';
import { getModuleNavItems } from '../modules/registry';

// Map icon names to MUI icon components
const iconMap: Record<string, React.ComponentType> = {
  Dashboard: DashboardIcon,
  People: PeopleIcon,
  PersonAdd: PersonAddIcon,
  TrendingUp: TrendingUpIcon,
  Work: WorkIcon,
  Campaign: CampaignIcon,
  Architecture: ArchitectureIcon,
  Support: SupportIcon,
  Assessment: AssessmentIcon,
  Assignment: AssignmentIcon,
  Psychology: PsychologyIcon,
  Description: DescriptionIcon,
  Build: BuildIcon,
  Gavel: GavelIcon,
  Folder: FolderIcon,
  Settings: SettingsIcon,
  Group: GroupIcon,
  Security: SecurityIcon,
  LocalShipping: LocalShippingIcon,
  Business: BusinessIcon,
  Timeline: TimelineIcon,
};

interface ModuleContextMenuProps {
  moduleKey: string | null;
  userPermissions?: string[];
  isAdmin?: boolean;
}

const ModuleContextMenu: React.FC<ModuleContextMenuProps> = ({
  moduleKey,
  userPermissions = [],
  isAdmin = false,
}) => {
  const navigate = useNavigate();
  const location = useLocation();

  if (!moduleKey) {
    return null;
  }

  // Get navigation items for this module, filtered by permissions
  const navItems = getModuleNavItems(moduleKey, userPermissions, isAdmin);

  if (navItems.length === 0) {
    return (
      <List>
        <ListItem>
          <ListItemText
            primary="No items available"
            secondary="You don't have permission to view this module's content"
          />
        </ListItem>
      </List>
    );
  }

  // Get icon component for a nav item
  const getIcon = (iconName: string) => {
    const IconComponent = iconMap[iconName] || DashboardIcon;
    return <IconComponent />;
  };

  return (
    <List>
      {navItems.map((item) => {
        const isSelected = location.pathname === item.path || 
          (!item.path.endsWith('/') && location.pathname.startsWith(item.path + '/'));

        return (
          <ListItem key={item.path} disablePadding>
            <ListItemButton
              selected={isSelected}
              onClick={() => navigate(item.path)}
            >
              <ListItemIcon>{getIcon(item.icon)}</ListItemIcon>
              <ListItemText primary={item.text} />
            </ListItemButton>
          </ListItem>
        );
      })}
    </List>
  );
};

export default ModuleContextMenu;

