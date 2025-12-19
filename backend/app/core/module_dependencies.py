#!/usr/bin/env python3
"""
Module dependencies and access control

Provides utilities for checking module access based on tenant configuration.
"""

from fastapi import Depends, HTTPException, status
from typing import Optional, List
from functools import wraps

from app.core.dependencies import get_current_tenant
from app.models.tenant import Tenant


def verify_module_access(
    module_id: str,
    tenant: Tenant = Depends(get_current_tenant)
) -> bool:
    """
    Verify that a module is enabled for the current tenant.
    
    Args:
        module_id: Module identifier (e.g., 'crm', 'helpdesk', 'enforcesense')
        tenant: Current tenant (from dependency)
        
    Returns:
        True if module is enabled, False otherwise
        
    Raises:
        HTTPException: If module is not enabled (403 Forbidden)
    """
    # Get enabled modules from tenant (default to ["crm", "helpdesk"])
    enabled_modules = tenant.enabled_modules or ["crm", "helpdesk"]
    
    # CRM is always enabled (enabled by default)
    if module_id == "crm":
        return True
    
    # Check if module is in enabled_modules list
    if module_id in enabled_modules:
        # Also check feature flag if module has one
        feature_flags = tenant.feature_flags or {}
        
        # Map module IDs to feature flags
        module_feature_flags = {
            "helpdesk": "HELPDESK_ENABLED",
            "enforcesense": "ENFORCESENSE_ENABLED",
            "quoting": "QUOTING_ENABLED",
        }
        
        feature_flag = module_feature_flags.get(module_id)
        if feature_flag:
            # If feature flag exists, check it (default to True if not set)
            flag_value = feature_flags.get(feature_flag, True)
            if not flag_value:
                return False
        
        return True
    
    return False


def require_module(module_id: str):
    """
    Decorator to require a module to be enabled for the current tenant.
    
    Usage:
        @router.get("/some-route")
        @require_module("helpdesk")
        async def some_endpoint(...):
            ...
    """
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get tenant from kwargs (should be injected by FastAPI)
            tenant = None
            for key, value in kwargs.items():
                if isinstance(value, Tenant):
                    tenant = value
                    break
            
            if not tenant:
                # Try to get from dependencies
                from app.core.dependencies import get_current_tenant
                tenant = await get_current_tenant()
            
            if not verify_module_access(module_id, tenant):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Module '{module_id}' is not enabled for this tenant"
                )
            
            return await func(*args, **kwargs)
        return wrapper
    return decorator


def check_module_access(module_id: str, tenant: Tenant) -> bool:
    """
    Check if a module is enabled for a tenant (non-decorator version).
    
    Args:
        module_id: Module identifier
        tenant: Tenant object
        
    Returns:
        True if enabled, False otherwise
    """
    return verify_module_access(module_id, tenant)


def get_enabled_modules(tenant: Tenant) -> List[str]:
    """
    Get list of enabled module IDs for a tenant.
    
    Args:
        tenant: Tenant object
        
    Returns:
        List of enabled module IDs
    """
    enabled_modules = tenant.enabled_modules or ["crm", "helpdesk"]
    
    # Filter by feature flags
    feature_flags = tenant.feature_flags or {}
    module_feature_flags = {
        "helpdesk": "HELPDESK_ENABLED",
        "enforcesense": "ENFORCESENSE_ENABLED",
        "quoting": "QUOTING_ENABLED",
    }
    
    filtered_modules = []
    for module_id in enabled_modules:
        if module_id == "crm":
            # CRM is always enabled
            filtered_modules.append(module_id)
        else:
            feature_flag = module_feature_flags.get(module_id)
            if feature_flag:
                # Check feature flag (default to True if not set)
                if feature_flags.get(feature_flag, True):
                    filtered_modules.append(module_id)
            else:
                # No feature flag, include if in enabled_modules
                filtered_modules.append(module_id)
    
    return filtered_modules

