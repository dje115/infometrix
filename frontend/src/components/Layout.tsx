import React, { useState, useEffect } from 'react';
import {
  Box,
  Drawer,
  AppBar,
  Toolbar,
  Typography,
  Divider,
  IconButton,
  Avatar,
  Menu,
  MenuItem,
  CircularProgress,
  Alert
} from '@mui/material';
import {
  Menu as MenuIcon,
  Logout as LogoutIcon,
  AccountCircle,
} from '@mui/icons-material';
import { useNavigate, useLocation } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SimpleLanguageSelector from './SimpleLanguageSelector';
import GlobalAIMonitor from './GlobalAIMonitor';
import AIMonitorBadge from './AIMonitorBadge';
import OnboardingTooltips from './OnboardingTooltips';
import VersionDisplay from './VersionDisplay';
import ModuleSwitcher from './ModuleSwitcher';
import ModuleContextMenu from './ModuleContextMenu';
import { settingsAPI } from '../services/api';
import { useModules } from '../modules/hooks/useModules';
import { useActiveModule } from '../modules/hooks/useActiveModule';

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

  const user = JSON.parse(localStorage.getItem('user') || '{}');
  const userPermissions = user.permissions || [];
  const isAdmin = user.role === 'super_admin' || user.role === 'admin' || user.role === 'tenant_admin';

  // Get modules and active module
  const { enabledModules, loading: modulesLoading, error: modulesError } = useModules(userPermissions, isAdmin);
  const { activeModule } = useActiveModule();

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
      
      // Show tooltips if no AI analysis (regardless of whether user has seen them before)
      if (!hasAIAnalysis && user.email) {
        setShowOnboardingTooltips(true);
      }
    } catch (error) {
      console.error('Failed to check AI analysis status:', error);
    }
  };

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

  // Get page title from current route
  const getPageTitle = () => {
    // Try to find title from active module's nav items
    if (activeModule && enabledModules.length > 0) {
      const module = enabledModules.find(m => m.key === activeModule);
      if (module) {
        const navItem = module.navItems.find(item => {
          if (item.path === location.pathname) return true;
          if (!item.path.endsWith('/') && location.pathname.startsWith(item.path + '/')) return true;
          return false;
        });
        if (navItem) {
          return navItem.text;
        }
      }
    }
    return 'Infometrix';
  };

  const drawer = (
    <div>
      <Toolbar>
        <Typography variant="h6" noWrap component="div">
          Infometrix
        </Typography>
      </Toolbar>
      <Divider />
      
      {/* Module Switcher - at top of drawer */}
      {modulesLoading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', p: 2 }}>
          <CircularProgress size={24} />
        </Box>
      ) : modulesError ? (
        <Box sx={{ p: 2 }}>
          <Alert severity="warning" sx={{ fontSize: '0.75rem' }}>
            Failed to load modules
          </Alert>
        </Box>
      ) : enabledModules.length > 0 ? (
        <>
          <ModuleSwitcher enabledModules={enabledModules} />
          <Divider />
          
          {/* Context Menu - shows nav items for active module */}
          <ModuleContextMenu
            moduleKey={activeModule}
            userPermissions={userPermissions}
            isAdmin={isAdmin}
          />
        </>
      ) : (
        <Box sx={{ p: 2 }}>
          <Typography variant="body2" color="text.secondary">
            No modules available
          </Typography>
        </Box>
      )}
      
      <Divider />
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
            {getPageTitle()}
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
