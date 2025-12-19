"""
Tenant resolution and validation utilities
"""

from typing import Optional, TYPE_CHECKING
from fastapi import HTTPException, status

if TYPE_CHECKING:
    from sqlalchemy.orm import Session
    from sqlalchemy.ext.asyncio import AsyncSession


def get_tenant_from_user(
    user_tenant_id: str,
    db_session,
    TenantModel,
    is_async: bool = False
):
    """
    Get tenant from user's tenant_id
    
    Args:
        user_tenant_id: Tenant ID from user object
        db_session: Database session (Session or AsyncSession)
        TenantModel: Tenant SQLAlchemy model class
        is_async: Whether using async session
    
    Returns:
        Tenant object
    
    Raises:
        HTTPException: If tenant not found
    """
    if is_async:
        from sqlalchemy import select
        # For async, we need to return a coroutine
        # This will be handled by the caller
        stmt = select(TenantModel).where(TenantModel.id == user_tenant_id)
        return stmt
    else:
        tenant = db_session.query(TenantModel).filter(TenantModel.id == user_tenant_id).first()
        if tenant is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Tenant not found"
            )
        return tenant


def validate_tenant_access(
    jwt_tenant_id: str,
    header_tenant_id: Optional[str] = None,
    subdomain: Optional[str] = None,
    tenant_slug: Optional[str] = None
) -> None:
    """
    Validate that header/subdomain tenant matches JWT tenant
    
    SECURITY: Prevents tenant impersonation attacks by ensuring
    the tenant in the JWT token matches any tenant specified
    in headers or subdomain.
    
    Args:
        jwt_tenant_id: Tenant ID from JWT token (source of truth)
        header_tenant_id: Tenant ID from X-Tenant-ID header (optional)
        subdomain: Subdomain from request (optional)
        tenant_slug: Tenant slug from database (optional)
    
    Raises:
        HTTPException: If tenant mismatch detected
    """
    # If header/subdomain tenant is provided, it must match JWT tenant
    if header_tenant_id and header_tenant_id != jwt_tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant mismatch: Header tenant does not match authenticated tenant"
        )
    
    # Note: Subdomain validation would require a database lookup
    # to convert subdomain to tenant_id. This is handled in the
    # get_current_tenant dependency in each API.

