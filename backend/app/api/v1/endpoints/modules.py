"""
Module metadata API endpoint

Returns enabled modules for the current tenant with navigation items filtered by user permissions.
"""

from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_async_db
from app.core.dependencies import get_current_user, get_current_tenant
from app.core.feature_flags import FeatureFlagService
from app.modules import get_module_registry
from app.models.tenant import User, Tenant

router = APIRouter()


@router.get("", response_model=Dict[str, Any])
async def get_modules(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """
    Get enabled modules for the current tenant with navigation items filtered by permissions.
    
    Returns:
    {
        "modules": [
            {
                "module_id": "helpdesk",
                "module_name": "Helpdesk",
                "feature_flag": "HELPDESK_ENABLED",
                "version": "1.0.0",
                "permissions": ["helpdesk:view", ...],
                "navigation_items": [
                    {
                        "text": "Helpdesk",
                        "icon": "Support",
                        "path": "/helpdesk",
                        "permission": "helpdesk:view_tickets"
                    },
                    ...
                ]
            },
            ...
        ],
        "feature_flags": {
            "HELPDESK_ENABLED": true,
            "QUOTING_ENABLED": true,
            ...
        }
    }
    """
    tenant_id = current_tenant.id

    # Get feature flags for tenant
    feature_flags = await FeatureFlagService.get_tenant_flags(db, tenant_id)

    # Get module registry
    module_registry = get_module_registry()

    # Get user permissions
    user_permissions = current_user.permissions or []
    is_admin = current_user.role in ["super_admin", "tenant_admin", "admin"]

    # Get enabled modules - need to handle modules without feature flags (like CRM)
    all_modules = module_registry.get_all_modules()
    enabled_modules = []
    
    for module in all_modules.values():
        # Check if module is enabled
        # Modules without feature flags (enabledByDefault) are always enabled
        # For now, we'll include all registered modules and let the frontend filter
        # based on feature flags. The registry's get_enabled_modules only checks feature flags.
        # We need to include modules that:
        # 1. Don't have a feature flag (always enabled)
        # 2. Have a feature flag that is enabled
        
        # Check if module has a feature flag
        module_feature_flag = getattr(module, 'feature_flag', None)
        
        if not module_feature_flag:
            # No feature flag means always enabled (like CRM)
            enabled_modules.append(module)
        else:
            # Check feature flag
            flag_value = feature_flags.get(module_feature_flag, False)
            if flag_value:
                enabled_modules.append(module)

    # Build response with navigation items filtered by permissions
    modules_data = []
    for module in enabled_modules:
        # Get navigation items for this module, filtered by permissions
        nav_items = module_registry.get_navigation_items(
            feature_flags,
            user_permissions
        )

        # Find this module's navigation items
        module_nav_items = []
        for group in nav_items:
            if group["module_id"] == module.module_id:
                module_nav_items = group["items"]
                break

        # Get feature flag - all backend modules should have one
        module_feature_flag = getattr(module, 'feature_flag', None)
        
        modules_data.append({
            "module_id": module.module_id,
            "module_name": module.module_name,
            "feature_flag": module_feature_flag,
            "version": module.version,
            "permissions": module.get_permissions(),
            "navigation_items": module_nav_items,
        })

    return {
        "modules": modules_data,
        "feature_flags": feature_flags,
    }

