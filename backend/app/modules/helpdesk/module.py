"""
Helpdesk Module Implementation
"""

from typing import List, Dict, Any
from fastapi import APIRouter
from app.modules.base import BaseModule
from app.api.v1.endpoints import helpdesk, sla


class HelpdeskModule(BaseModule):
    """Helpdesk module for ticket management and SLA tracking"""
    
    @property
    def module_id(self) -> str:
        return "helpdesk"
    
    @property
    def module_name(self) -> str:
        return "Helpdesk"
    
    @property
    def feature_flag(self) -> str:
        return "HELPDESK_ENABLED"
    
    @property
    def version(self) -> str:
        return "1.0.0"
    
    def get_routes(self) -> APIRouter:
        """Return helpdesk routes"""
        router = APIRouter()
        
        # Mount existing helpdesk routes
        router.include_router(
            helpdesk.router,
            prefix="/helpdesk",
            tags=["helpdesk"]
        )
        
        # Mount SLA routes
        router.include_router(
            sla.router,
            prefix="/sla",
            tags=["sla"]
        )
        
        return router
    
    def get_permissions(self) -> List[str]:
        """Return helpdesk module permissions"""
        return [
            "helpdesk:view",
            "helpdesk:view_tickets",
            "helpdesk:create_ticket",
            "helpdesk:update_ticket",
            "helpdesk:delete_ticket",
            "helpdesk:assign_ticket",
            "helpdesk:admin",
            "helpdesk:sla_view",
            "helpdesk:sla_manage",
        ]
    
    def get_navigation_items(self) -> List[Dict[str, Any]]:
        """Return helpdesk navigation items"""
        return [
            {
                "text": "Helpdesk",
                "icon": "Support",
                "path": "/helpdesk",
                "permission": "helpdesk:view_tickets"
            },
            {
                "text": "Helpdesk Performance",
                "icon": "Assessment",
                "path": "/helpdesk/performance",
                "permission": "helpdesk:view"
            },
            {
                "text": "NPA Dashboard",
                "icon": "Assignment",
                "path": "/helpdesk/npa-dashboard",
                "permission": "helpdesk:view"
            },
            {
                "text": "Knowledge Base",
                "icon": "Psychology",
                "path": "/helpdesk/knowledge-base",
                "permission": "helpdesk:view"
            },
            {
                "text": "Ticket Templates",
                "icon": "Description",
                "path": "/helpdesk/templates",
                "permission": "helpdesk:admin"
            },
            {
                "text": "Ticket Macros",
                "icon": "Build",
                "path": "/helpdesk/macros",
                "permission": "helpdesk:admin"
            },
            {
                "text": "SLA Management",
                "icon": "Assessment",
                "path": "/sla",
                "permission": "helpdesk:sla_manage"
            },
            {
                "text": "SLA Dashboard",
                "icon": "Assessment",
                "path": "/sla/dashboard",
                "permission": "helpdesk:sla_view"
            },
            {
                "text": "SLA Reports",
                "icon": "Assessment",
                "path": "/sla/reports",
                "permission": "helpdesk:sla_view"
            },
        ]

