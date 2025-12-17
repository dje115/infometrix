"""
EnforceSense Module Definition
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from app.modules.enforcesense.routes import router


class EnforceSenseModule:
    """EnforceSense module for debt recovery and enforcement"""
    
    @property
    def module_id(self) -> str:
        return "enforcesense"
    
    @property
    def module_name(self) -> str:
        return "EnforceSense"
    
    @property
    def version(self) -> str:
        return "0.1.0"
    
    def get_routes(self) -> APIRouter:
        """Return EnforceSense routes"""
        return router
    
    def get_permissions(self) -> List[str]:
        """Return EnforceSense module permissions"""
        return [
            "enforce:read",
            "enforce:write",
            "enforce:view_cases",
            "enforce:create_case",
            "enforce:update_case",
            "enforce:admin",
        ]
    
    def get_navigation_items(self) -> List[Dict[str, Any]]:
        """Return EnforceSense navigation items"""
        return [
            {
                "text": "EnforceSense Dashboard",
                "icon": "Gavel",
                "path": "/enforcesense",
                "permission": "enforce:read"
            },
            {
                "text": "Cases",
                "icon": "Folder",
                "path": "/enforcesense/cases",
                "permission": "enforce:view_cases"
            },
        ]

