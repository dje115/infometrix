"""
Module Dependencies for Backend

Provides dependencies for checking module enablement and permissions.
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from app.core.database import get_async_db
from app.core.dependencies import get_current_user, get_current_tenant
from app.core.feature_flags import FeatureFlagService
from app.modules import get_module_registry
from app.models.tenant import User, Tenant


async def require_module_enabled(
    module_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> bool:
    """
    Dependency to check if a module is enabled for the current tenant.
    
    Checks both tenant.enabled_modules list and feature flags.
    CRM is always enabled regardless of these checks.
    
    Raises HTTPException if module is not enabled.
    
    Args:
        module_id: Module identifier (e.g., 'helpdesk', 'enforcesense')
        db: Database session
        current_tenant: Current tenant
        
    Returns:
        True if module is enabled
        
    Raises:
        HTTPException: If module is not enabled
    """
    # CRM is always enabled
    if module_id == 'crm':
        return True
    
    # Get module registry
    module_registry = get_module_registry()
    module = module_registry.get_module(module_id)
    
    if not module:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Module '{module_id}' not found"
        )
    
    # Check tenant.enabled_modules list
    tenant_enabled_modules = current_tenant.enabled_modules or []
    if module_id not in tenant_enabled_modules:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Module '{module_id}' is not enabled for this tenant"
        )
    
    # Check if module is always enabled (modules without feature flags)
    module_feature_flag = getattr(module, 'feature_flag', None)
    if not module_feature_flag:
        # Always enabled modules (like Settings) just need to be in enabled_modules
        return True
    
    # Check feature flag
    feature_flags = await FeatureFlagService.get_tenant_flags(db, current_tenant.id)
    is_enabled = feature_flags.get(module_feature_flag, False)
    
    if not is_enabled:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Module '{module_id}' feature flag is not enabled for this tenant"
        )
    
    return True


def require_module_permission(permission: str):
    """
    Dependency factory to check if user has a specific module permission.
    
    Usage:
        @router.get("/endpoint")
        async def my_endpoint(
            _: bool = Depends(require_module_permission("helpdesk:view"))
        ):
            ...
    
    Args:
        permission: Permission string (e.g., "helpdesk:view", "enforcesense:create_case")
        
    Returns:
        Dependency function that raises HTTPException if permission is missing
    """
    async def permission_checker(
        current_user: User = Depends(get_current_user)
    ) -> bool:
        # Super admins have all permissions
        if current_user.is_super_admin:
            return True
        
        # Check if user has the permission
        user_permissions = current_user.permissions or []
        if permission not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission '{permission}' required"
            )
        
        return True
    
    return permission_checker


async def require_module_access(
    module_id: str,
    permission: Optional[str] = None,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
) -> bool:
    """
    Combined dependency to check both module enablement and permission.
    
    Usage:
        @router.get("/endpoint")
        async def my_endpoint(
            _: bool = Depends(require_module_access("helpdesk", "helpdesk:view"))
        ):
            ...
    
    Args:
        module_id: Module identifier
        permission: Optional permission to check
        db: Database session
        current_user: Current user
        current_tenant: Current tenant
        
    Returns:
        True if module is enabled and user has permission
        
    Raises:
        HTTPException: If module is not enabled or permission is missing
    """
    # Check module enablement
    await require_module_enabled(module_id, db, current_tenant)
    
    # Check permission if provided
    if permission:
        # Super admins have all permissions
        if not current_user.is_super_admin:
            user_permissions = current_user.permissions or []
            if permission not in user_permissions:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail=f"Permission '{permission}' required"
                )
    
    return True

