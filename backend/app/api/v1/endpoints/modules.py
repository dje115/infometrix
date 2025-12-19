#!/usr/bin/env python3
"""
Module management endpoints

Provides endpoints for querying available modules and their status.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any
from pydantic import BaseModel

from app.core.dependencies import get_current_user, get_current_tenant
from app.core.database import get_async_db
from app.models.tenant import Tenant
from app.core.module_dependencies import get_enabled_modules
from app.modules.registry import get_module_registry

router = APIRouter(prefix="/modules", tags=["modules"])


class ModuleInfo(BaseModel):
    id: str
    name: str
    enabled: bool
    feature_flag: str | None
    version: str | None


class ModulesResponse(BaseModel):
    modules: List[ModuleInfo]
    enabled_modules: List[str]


@router.get("", response_model=ModulesResponse)
async def get_modules(
    current_user = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all available modules and their enabled status for the current tenant.
    
    Returns only modules that are enabled for the tenant.
    """
    # Get enabled modules for tenant
    enabled_module_ids = get_enabled_modules(current_tenant)
    
    # Get module registry
    registry = get_module_registry()
    all_modules = registry.get_all_modules()
    
    # Build module info list
    modules_info = []
    for module_id, module in all_modules.items():
        is_enabled = module_id in enabled_module_ids
        
        modules_info.append(ModuleInfo(
            id=module.module_id,
            name=module.module_name,
            enabled=is_enabled,
            feature_flag=module.feature_flag if hasattr(module, 'feature_flag') else None,
            version=module.version if hasattr(module, 'version') else None
        ))
    
    return ModulesResponse(
        modules=modules_info,
        enabled_modules=enabled_module_ids
    )


@router.get("/enabled", response_model=List[str])
async def get_enabled_module_ids(
    current_user = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get list of enabled module IDs for the current tenant.
    
    This is a lightweight endpoint that returns just the module IDs.
    """
    enabled_module_ids = get_enabled_modules(current_tenant)
    return enabled_module_ids

