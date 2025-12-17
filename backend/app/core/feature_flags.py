"""
Feature flags system for Infometrix platform

Feature flags control which modules and features are enabled per tenant.
"""

from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.tenant import Tenant


class FeatureFlagService:
    """Service for managing and checking feature flags"""
    
    # Default feature flags (applied to new tenants)
    DEFAULT_FLAGS = {
        'HELPDESK_ENABLED': True,
        'ENFORCESENSE_ENABLED': False,
        'QUOTING_ENABLED': True,
        'SALES_ENABLED': True,
    }
    
    @staticmethod
    async def get_tenant_flags(db: AsyncSession, tenant_id: str) -> Dict[str, bool]:
        """
        Get feature flags for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            
        Returns:
            Dict of feature flag name -> value
        """
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await db.execute(stmt)
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            return FeatureFlagService.DEFAULT_FLAGS.copy()
        
        # Get feature_flags JSONB column
        flags = getattr(tenant, 'feature_flags', None)
        
        if not flags or not isinstance(flags, dict):
            return FeatureFlagService.DEFAULT_FLAGS.copy()
        
        # Merge with defaults (tenant flags override defaults)
        merged = FeatureFlagService.DEFAULT_FLAGS.copy()
        merged.update(flags)
        
        return merged
    
    @staticmethod
    async def set_tenant_flag(
        db: AsyncSession,
        tenant_id: str,
        flag_name: str,
        flag_value: bool
    ) -> None:
        """
        Set a feature flag for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            flag_name: Feature flag name
            flag_value: Feature flag value
        """
        stmt = select(Tenant).where(Tenant.id == tenant_id)
        result = await db.execute(stmt)
        tenant = result.scalar_one_or_none()
        
        if not tenant:
            raise ValueError(f"Tenant {tenant_id} not found")
        
        # Get current flags
        flags = getattr(tenant, 'feature_flags', None) or {}
        if not isinstance(flags, dict):
            flags = {}
        
        # Update flag
        flags[flag_name] = flag_value
        
        # Save
        tenant.feature_flags = flags
        await db.commit()
        await db.refresh(tenant)
    
    @staticmethod
    async def is_enabled(db: AsyncSession, tenant_id: str, flag_name: str) -> bool:
        """
        Check if a feature flag is enabled for a tenant.
        
        Args:
            db: Database session
            tenant_id: Tenant ID
            flag_name: Feature flag name
            
        Returns:
            True if enabled, False otherwise
        """
        flags = await FeatureFlagService.get_tenant_flags(db, tenant_id)
        return flags.get(flag_name, False)


# Convenience function
async def is_feature_enabled(db: AsyncSession, tenant_id: str, flag_name: str) -> bool:
    """Check if a feature is enabled for a tenant"""
    return await FeatureFlagService.is_enabled(db, tenant_id, flag_name)

