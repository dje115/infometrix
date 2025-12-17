"""
Module registry for Infometrix platform

Central registry for all platform modules.
Modules register themselves here and can be queried by feature flags/permissions.
"""

from typing import Dict, List, Optional, Any
from .base import BaseModule


class ModuleRegistry:
    """
    Central registry for all platform modules.
    
    Modules register themselves here, and the registry provides:
    - Module lookup by ID
    - Feature flag checking
    - Permission checking
    - Navigation item aggregation
    """
    
    def __init__(self):
        self._modules: Dict[str, BaseModule] = {}
    
    def register(self, module: BaseModule) -> None:
        """Register a module"""
        if module.module_id in self._modules:
            raise ValueError(f"Module {module.module_id} is already registered")
        self._modules[module.module_id] = module
    
    def get_module(self, module_id: str) -> Optional[BaseModule]:
        """Get module by ID"""
        return self._modules.get(module_id)
    
    def get_all_modules(self) -> Dict[str, BaseModule]:
        """Get all registered modules"""
        return self._modules.copy()
    
    def is_module_enabled(self, module_id: str, tenant_feature_flags: Dict[str, bool]) -> bool:
        """
        Check if a module is enabled for a tenant.
        
        Args:
            module_id: Module identifier
            tenant_feature_flags: Dict of feature flags for tenant
            
        Returns:
            True if module is enabled, False otherwise
        """
        module = self.get_module(module_id)
        if not module:
            return False
        
        # Modules without feature flags are always enabled
        if not hasattr(module, 'feature_flag') or not module.feature_flag:
            return True
        
        # Check feature flag (default to False if not set)
        flag_value = tenant_feature_flags.get(module.feature_flag, False)
        return bool(flag_value)
    
    def get_enabled_modules(self, tenant_feature_flags: Dict[str, bool]) -> List[BaseModule]:
        """
        Get all enabled modules for a tenant.
        
        Includes:
        - Modules without feature flags (always enabled)
        - Modules with feature flags that are enabled
        """
        enabled = []
        for module in self._modules.values():
            if self.is_module_enabled(module.module_id, tenant_feature_flags):
                enabled.append(module)
        return enabled
    
    def get_navigation_items(self, tenant_feature_flags: Dict[str, bool], user_permissions: List[str]) -> List[Dict[str, Any]]:
        """
        Get all navigation items from enabled modules, filtered by permissions.
        
        Args:
            tenant_feature_flags: Feature flags for tenant
            user_permissions: List of permissions user has
            
        Returns:
            List of navigation items grouped by module
        """
        items = []
        enabled_modules = self.get_enabled_modules(tenant_feature_flags)
        
        for module in enabled_modules:
            module_items = module.get_navigation_items()
            # Filter items by permissions
            filtered_items = []
            for item in module_items:
                # Check if user has required permission
                required_permission = item.get('permission')
                if required_permission:
                    if required_permission not in user_permissions:
                        continue
                
                # Check adminOnly flag
                if item.get('adminOnly'):
                    # Assume admin permissions include module:admin
                    admin_permission = f"{module.module_id}:admin"
                    if admin_permission not in user_permissions:
                        continue
                
                filtered_items.append(item)
            
            if filtered_items:
                items.append({
                    'module_id': module.module_id,
                    'module_name': module.module_name,
                    'items': filtered_items
                })
        
        return items


# Global registry instance
_registry: Optional[ModuleRegistry] = None


def get_module_registry() -> ModuleRegistry:
    """Get the global module registry instance"""
    global _registry
    if _registry is None:
        _registry = ModuleRegistry()
    return _registry

