import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  List,
  Typography,
  Divider,
  IconButton,
  ListItem,
  ListItemButton,
  ListItemIcon,
  ListItemText,
  Avatar,
  Menu,
  MenuItem,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Collapse
} from '@mui/material';
import {
  Menu as MenuIcon,
  Dashboard as DashboardIcon,
  People as PeopleIcon,
  TrendingUp as LeadsIcon,
  PersonAdd as PersonAddIcon,
  Campaign as CampaignIcon,
  Description as QuotesIcon,
  Settings as SettingsIcon,
  Logout as LogoutIcon,
  AccountCircle,
  Group as GroupIcon,
  Business as CompetitorsIcon,
  Security as SecurityIcon,
  Architecture as ArchitectureIcon,
  LocalShipping as LocalShippingIcon,
  Psychology as PsychologyIcon,
  Support as SupportIcon,
  Timeline as TimelineIcon,
  Assessment as AssessmentIcon,
  Work as OpportunitiesIcon,
  Description as ContractsIcon,
  Assignment as AssignmentIcon,
  Description as TemplateIcon,
  Build as MacroIcon,
  ExpandMore as ExpandMoreIcon,
  Gavel as GavelIcon
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SimpleLanguageSelector from './SimpleLanguageSelector';
import GlobalAIMonitor from './GlobalAIMonitor';
import AIMonitorBadge from './AIMonitorBadge';
import OnboardingTooltips from './OnboardingTooltips';
import VersionDisplay from './VersionDisplay';
import { settingsAPI } from '../services/api';
import { CORE_NAVIGATION_GROUPS, MenuGroup } from '../types/modules';
import ModuleSwitcher from './ModuleSwitcher';
import { isModuleEnabled } from '../modules/registry';

const drawerWidth = 240;

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const { t } = useTranslation();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [anchorEl, setAnchorEl] = useState<null | HTMLElement>(null);
  const [showOnboardingTooltips, setShowOnboardingTooltips] = useState(false);
  const [enabledModules, setEnabledModules] = useState<string[]>(['crm', 'helpdesk']);
  const [featureFlags, setFeatureFlags] = useState<Record<string, boolean>>({});

  const user = JSON.parse(localStorage.getItem('user') || '{}');

  const handleDrawerToggle = () => {
    setMobileOpen(!mobileOpen);
  };

  const handleMenu = (event: React.MouseEvent<HTMLElement>) => {
    setAnchorEl(event.currentTarget);
  };

  const handleClose = () => {
    setAnchorEl(null);
  };

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  // Check AI analysis status and show tooltips if needed
  const checkTooltipStatus = async () => {
    try {
      const response = await settingsAPI.get('/company-profile');
      const data = response.data;
      
      // Check if we have meaningful AI analysis data
      const hasAIAnalysis = !!(data.company_analysis && 
                              typeof data.company_analysis === 'object' && 
                              Object.keys(data.company_analysis).length > 0);
      
      // Check if user has seen tooltips before
      const hasSeenTooltips = localStorage.getItem('onboarding-tooltips-seen');
      
      // Show tooltips if no AI analysis (regardless of whether user has seen them before)
      if (!hasAIAnalysis && user.email) {
        setShowOnboardingTooltips(true);
      }
    } catch (error) {
      console.error('Failed to check AI analysis status:', error);
    }
  };

  // Fetch tenant module configuration
  useEffect(() => {
    const fetchTenantConfig = async () => {
      try {
        // Try to get tenant info from user object or API
        const tenantResponse = await settingsAPI.get('/tenant');
        const tenant = tenantResponse.data;
        
        if (tenant) {
          // Get enabled modules (default to ["crm", "helpdesk"] if not set)
          const modules = tenant.enabled_modules || ['crm', 'helpdesk'];
          setEnabledModules(modules);
          
          // Get feature flags
          const flags = tenant.feature_flags || {};
          setFeatureFlags(flags);
        }
      } catch (error) {
        console.error('Failed to fetch tenant config:', error);
        // Use defaults on error
        setEnabledModules(['crm', 'helpdesk']);
        setFeatureFlags({});
      }
    };
    
    fetchTenantConfig();
  }, []);

  // Check on component mount and when user changes
  useEffect(() => {
    if (user.email) {
      checkTooltipStatus();
    }
  }, [user.email]);

  const handleTooltipComplete = () => {
    setShowOnboardingTooltips(false);
    localStorage.setItem('onboarding-tooltips-seen', 'true');
  };

  const handleTooltipSkip = () => {
    setShowOnboardingTooltips(false);
    localStorage.setItem('onboarding-tooltips-seen', 'true');
  };

  // Map icon names to icon components
  const getIconComponent = (iconName: string) => {
    const iconMap: { [key: string]: React.ReactElement } = {
      Dashboard: <DashboardIcon />,
      People: <PeopleIcon />,
      PersonAdd: <PersonAddIcon />,
      TrendingUp: <LeadsIcon />,
      Work: <OpportunitiesIcon />,
      Architecture: <ArchitectureIcon />,
      Campaign: <CampaignIcon />,
      Description: <QuotesIcon />,
      Support: <SupportIcon />,
      Assessment: <AssessmentIcon />,
      Assignment: <AssignmentIcon />,
      Psychology: <PsychologyIcon />,
      Build: <MacroIcon />,
      Settings: <SettingsIcon />,
      Group: <GroupIcon />,
      Security: <SecurityIcon />,
      LocalShipping: <LocalShippingIcon />,
      Business: <CompetitorsIcon />,
      Timeline: <TimelineIcon />,
      Gavel: <GavelIcon />,
      Folder: <AssignmentIcon />,
    };
    return iconMap[iconName] || <DashboardIcon />;
  };

  // Get user info for permission checks
  const isAdmin = user.role === 'super_admin' || user.role === 'admin' || user.role === 'tenant_admin';
  
  // Filter navigation groups by enabled modules and feature flags
  const filteredGroups = CORE_NAVIGATION_GROUPS.filter((group: MenuGroup) => {
    // Map navigation group IDs to module IDs
    const groupToModuleMap: Record<string, string> = {
      'sales-crm': 'crm',
      'helpdesk': 'helpdesk',
      'enforcesense': 'enforcesense',
      'quoting': 'quoting',
    };
    
    const moduleId = groupToModuleMap[group.id];
    
    // If group has a module mapping, check if module is enabled
    if (moduleId) {
      const isEnabled = isModuleEnabled(moduleId, enabledModules, featureFlags);
      if (!isEnabled) {
        return false;
      }
    }
    
    // Also check feature flag if present (for backward compatibility)
    if (group.featureFlag && !featureFlags[group.featureFlag]) {
      return false;
    }
    
    return true;
  });

  const [expandedGroups, setExpandedGroups] = useState<{ [key: string]: boolean }>({
    'sales-crm': true,
    'quoting': true,
    'helpdesk': true,
    'settings': false,
  });

  const handleGroupToggle = (groupId: string) => {
    setExpandedGroups(prev => ({
      ...prev,
      [groupId]: !prev[groupId]
    }));
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Infometrix
        </Typography>
      </Toolbar>
      <Divider />
      {/* Module Switcher - appears at top of navigation */}
      <ModuleSwitcher
        enabledModules={enabledModules}
        featureFlags={featureFlags}
      />
      <List sx={{ width: '100%', p: 0 }}>
        {filteredGroups.map((group: MenuGroup) => {
          // Filter items by permissions and admin access
          const filteredItems = group.items.filter((item) => {
            if (item.adminOnly && !isAdmin) {
              return false;
            }
            // TODO: Check permissions when permission system is fully implemented
            // if (item.permission && !user.permissions?.includes(item.permission)) {
            //   return false;
            // }
            return true;
          });

          if (filteredItems.length === 0) {
            return null;
          }

          // Check if current path matches any item in this group
          const isGroupActive = filteredItems.some(item => location.pathname === item.path || location.pathname.startsWith(item.path + '/'));

          return (
            <Accordion
              key={group.id}
              expanded={expandedGroups[group.id] ?? false}
              onChange={() => handleGroupToggle(group.id)}
              sx={{
                boxShadow: 'none',
                '&:before': { display: 'none' },
                borderBottom: '1px solid rgba(0, 0, 0, 0.12)',
                '&.Mui-expanded': {
                  margin: 0,
                },
              }}
            >
              <AccordionSummary
                expandIcon={<ExpandMoreIcon />}
                sx={{
                  minHeight: 48,
                  '&.Mui-expanded': {
                    minHeight: 48,
                  },
                  bgcolor: isGroupActive ? 'action.selected' : 'transparent',
                  '&:hover': {
                    bgcolor: 'action.hover',
                  },
                }}
              >
                <Typography variant="subtitle2" sx={{ fontWeight: 600 }}>
                  {group.label}
                </Typography>
              </AccordionSummary>
              <AccordionDetails sx={{ p: 0 }}>
                <List sx={{ width: '100%', p: 0 }}>
                  {filteredItems.map((item) => (
                    <ListItem key={item.path} disablePadding>
                      <ListItemButton
                        selected={location.pathname === item.path || location.pathname.startsWith(item.path + '/')}
                        onClick={() => navigate(item.path)}
                        sx={{
                          pl: 4,
                          '&.Mui-selected': {
                            bgcolor: 'primary.main',
                            color: 'primary.contrastText',
                            '&:hover': {
                              bgcolor: 'primary.dark',
                            },
                            '& .MuiListItemIcon-root': {
                              color: 'primary.contrastText',
                            },
                          },
                        }}
                      >
                        <ListItemIcon sx={{ minWidth: 40 }}>
                          {getIconComponent(item.icon)}
                        </ListItemIcon>
                        <ListItemText 
                          primary={item.text} 
                          primaryTypographyProps={{
                            variant: 'body2',
                            sx: { fontWeight: location.pathname === item.path ? 600 : 400 }
                          }}
                        />
                      </ListItemButton>
                    </ListItem>
                  ))}
                </List>
              </AccordionDetails>
            </Accordion>
          );
        })}
      </List>
    </div>
  );

  return (
    <Box sx={{ display: 'flex' }}>
      <AppBar
        position="fixed"
        sx={{
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          ml: { sm: `${drawerWidth}px` },
        }}
      >
        <Toolbar>
          <IconButton
            color="inherit"
            aria-label="open drawer"
            edge="start"
            onClick={handleDrawerToggle}
            sx={{ mr: 2, display: { sm: 'none' } }}
          >
            <MenuIcon />
          </IconButton>
          <Typography variant="h6" noWrap component="div" sx={{ flexGrow: 1 }}>
            {(() => {
              // Find current page title from navigation groups
              for (const group of filteredGroups) {
                const item = group.items.find(item => 
                  location.pathname === item.path || location.pathname.startsWith(item.path + '/')
                );
                if (item) return item.text;
              }
              return 'Infometrix';
            })()}
          </Typography>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
            <AIMonitorBadge />
            <SimpleLanguageSelector />
            <Typography variant="body2">
              {user.email || 'User'}
            </Typography>
            <IconButton
              size="large"
              aria-label="account of current user"
              aria-controls="menu-appbar"
              aria-haspopup="true"
              onClick={handleMenu}
              color="inherit"
            >
              <AccountCircle />
            </IconButton>
            <Menu
              id="menu-appbar"
              anchorEl={anchorEl}
              anchorOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              keepMounted
              transformOrigin={{
                vertical: 'top',
                horizontal: 'right',
              }}
              open={Boolean(anchorEl)}
              onClose={handleClose}
            >
              <MenuItem onClick={() => { handleClose(); navigate('/profile'); }}>
                Profile
              </MenuItem>
              <MenuItem onClick={() => { handleClose(); navigate('/settings'); }}>
                {t('navigation.settings')}
              </MenuItem>
              <Divider />
              <MenuItem onClick={handleLogout}>
                <LogoutIcon sx={{ mr: 1 }} /> {t('navigation.logout')}
              </MenuItem>
            </Menu>
          </Box>
        </Toolbar>
      </AppBar>
      <Box
        component="nav"
        sx={{ width: { sm: drawerWidth }, flexShrink: { sm: 0 } }}
      >
        <Drawer
          variant="temporary"
          open={mobileOpen}
          onClose={handleDrawerToggle}
          ModalProps={{
            keepMounted: true,
          }}
          sx={{
            display: { xs: 'block', sm: 'none' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
        >
          {drawer}
        </Drawer>
        <Drawer
          variant="permanent"
          sx={{
            display: { xs: 'none', sm: 'block' },
            '& .MuiDrawer-paper': { boxSizing: 'border-box', width: drawerWidth },
          }}
          open
        >
          {drawer}
        </Drawer>
      </Box>
      <Box
        component="main"
        sx={{
          flexGrow: 1,
          width: { sm: `calc(100% - ${drawerWidth}px)` },
          mt: 8,
          display: 'flex',
          flexDirection: 'column',
          minHeight: 'calc(100vh - 64px)'
        }}
      >
        {children}
        
        {/* Global Onboarding Tooltips */}
        <OnboardingTooltips
          isActive={showOnboardingTooltips}
          onComplete={handleTooltipComplete}
          onSkip={handleTooltipSkip}
        />
        
        {/* Version Display */}
        <VersionDisplay variant="footer" />
      </Box>
    </Box>
  );
};

export default Layout;



