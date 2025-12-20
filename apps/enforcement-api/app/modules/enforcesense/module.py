#!/usr/bin/env python3
"""
EnforceSense Module for Enforcement API

Module definition and metadata.
"""

from fastapi import APIRouter
from app.modules.enforcesense import routes


class EnforceSenseModule:
    """EnforceSense module for Enforcement API"""
    
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
        return "0.1.0"
    
    def get_routes(self) -> APIRouter:
        """Return EnforceSense routes"""
        return routes.router
    
    def get_permissions(self) -> list[str]:
        """Return EnforceSense module permissions"""
        return [
            "enforce:read",
            "enforce:write",
            "enforcesense:view",
            "enforcesense:view_cases",
            "enforcesense:create_case",
            "enforcesense:update_case",
        ]



