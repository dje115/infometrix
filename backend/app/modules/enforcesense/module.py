"""
EnforceSense Module Implementation

EnforceSense debt recovery and enforcement module following the Core Domain Model:
- Debtor: Real-world person OR legal entity that owes money
- Client: Creditor or instructing organisation
- Case: Single enforcement instruction linking ONE Debtor to ONE Client
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from app.modules.base import BaseModule
from app.api.v1.endpoints import enforcesense


class EnforceSenseModule(BaseModule):
    """EnforceSense module for debt recovery and enforcement"""
    
    @property
    def module_id(self) -> str:
        return "enforcesense"
    
    @property
    def module_name(self) -> str:
        return "EnforceSense"
    
    @property
    def feature_flag(self) -> str:
        return "ENFORCESENSE_ENABLED"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get_routes(self) -> APIRouter:
        """Return EnforceSense routes"""
        router = APIRouter()
        
        # Mount EnforceSense routes
        router.include_router(
            enforcesense.router,
            tags=["enforcesense"]
        )
        
        return router
    
    def get_permissions(self) -> List[str]:
        """Return EnforceSense module permissions"""
        return [
            "enforcesense:view",
            "enforcesense:view_cases",
            "enforcesense:create_case",
            "enforcesense:update_case",
            "enforcesense:admin",
        ]
    
    def get_navigation_items(self) -> List[Dict[str, Any]]:
        """Return EnforceSense navigation items (placeholder)"""
        return [
            {
                "text": "EnforceSense Dashboard",
                "icon": "Gavel",
                "path": "/enforcesense",
                "permission": "enforcesense:view"
            },
            {
                "text": "Cases",
                "icon": "Folder",
                "path": "/enforcesense/cases",
                "permission": "enforcesense:view_cases"
            },
            {
                "text": "Reports",
                "icon": "Assessment",
                "path": "/enforcesense/reports",
                "permission": "enforcesense:view"
            },
        ]

