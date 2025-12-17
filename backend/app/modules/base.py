"""
Base module interface for Infometrix platform modules
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from fastapi import APIRouter


class BaseModule(ABC):
    """
    Base class for all Infometrix platform modules.
    
    Each module must:
    1. Define its unique identifier
    2. Register its routes
    3. Define its permissions
    4. Specify feature flag name
    """
    
    @property
    @abstractmethod
    def module_id(self) -> str:
        """Unique module identifier (e.g., 'helpdesk', 'enforcesense')"""
        pass
    
    @property
    @abstractmethod
    def module_name(self) -> str:
        """Human-readable module name (e.g., 'Helpdesk', 'EnforceSense')"""
        pass
    
    @property
    @abstractmethod
    def feature_flag(self) -> str:
        """Feature flag name to check (e.g., 'HELPDESK_ENABLED')"""
        pass
    
    @property
    @abstractmethod
    def version(self) -> str:
        """Module version"""
        pass
    
    @abstractmethod
    def get_routes(self) -> APIRouter:
        """
        Return FastAPI router with module routes.
        Routes will be mounted at /api/v1/modules/{module_id}/
        """
        pass
    
    @abstractmethod
    def get_permissions(self) -> List[str]:
        """
        Return list of permissions this module defines.
        Format: {module_id}:{action}
        Example: ['helpdesk:view', 'helpdesk:create', 'helpdesk:admin']
        """
        pass
    
    def get_navigation_items(self) -> List[Dict[str, Any]]:
        """
        Return navigation items for this module.
        Used by frontend to build left navigation.
        
        Returns:
            List of dicts with keys: text, icon, path, permission, adminOnly
        """
        return []
    
    def get_module_info(self) -> Dict[str, Any]:
        """Return module metadata"""
        return {
            'id': self.module_id,
            'name': self.module_name,
            'feature_flag': self.feature_flag,
            'version': self.version,
            'permissions': self.get_permissions(),
            'navigation_items': self.get_navigation_items()
        }

