#!/usr/bin/env python3
"""
FastAPI dependencies for Enforcement API

Uses shared auth library from packages/shared for JWT validation and tenant resolution.
"""

import sys
from pathlib import Path
from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.config import settings
from app.core.database import get_async_db

# Add packages/shared to path for imports
shared_path = Path(__file__).parent.parent.parent.parent / "packages" / "shared"
if str(shared_path) not in sys.path:
    sys.path.insert(0, str(shared_path))

from auth.jwt import verify_token
from auth.tenant import validate_tenant_access

# Import models (shared database)
# Note: We import from backend models since we share the database
backend_path = Path(__file__).parent.parent.parent.parent / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from app.models.tenant import User, Tenant

# Security - HTTPBearer for Authorization header (backward compatibility)
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token_cookie: Optional[str] = Cookie(None, alias="access_token"),
    db: AsyncSession = Depends(get_async_db)
) -> User:
    """
    Get current authenticated user from JWT token.
    
    Uses shared auth library for JWT validation.
    Supports both HttpOnly cookies (preferred) and Authorization header (backward compatibility).
    """
    # Try to get token from cookie first (more secure)
    token = access_token_cookie
    
    # Fallback to Authorization header for backward compatibility
    if not token and credentials:
        token = credentials.credentials
    
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials - no token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Verify token using shared auth library
        payload = verify_token(
            token,
            settings.SECRET_KEY,
            settings.JWT_ALGORITHM
        )
        
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials"
            )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Get user from database (async)
    stmt = select(User).where(User.id == user_id)
    result = await db.execute(stmt)
    user = result.scalar_one_or_none()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


async def get_current_tenant(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
) -> Tenant:
    """
    Get current tenant from authenticated user's JWT token.
    
    SECURITY: This enforces tenant isolation by:
    1. Deriving tenant from JWT token (current_user.tenant_id) - cannot be spoofed
    2. Validating any provided header/subdomain matches the JWT tenant
    3. Rejecting requests where header/subdomain doesn't match JWT tenant
    
    This prevents tenant impersonation attacks.
    """
    # Get tenant from JWT token (source of truth)
    jwt_tenant_id = current_user.tenant_id
    
    # Check if any tenant was provided in header/subdomain (from middleware)
    provided_tenant_id = getattr(request.state, 'tenant_id', None)
    
    # Validate tenant access using shared library
    validate_tenant_access(
        jwt_tenant_id=jwt_tenant_id,
        header_tenant_id=provided_tenant_id
    )
    
    # Get tenant from database (async)
    stmt = select(Tenant).where(Tenant.id == jwt_tenant_id)
    result = await db.execute(stmt)
    tenant = result.scalar_one_or_none()
    
    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    # Set tenant in request state for RLS (if using row-level security)
    request.state.tenant_id = jwt_tenant_id
    request.state.db_tenant_id = jwt_tenant_id
    
    return tenant


async def check_permission(user: User, permission: str):
    """
    Check if user has a specific permission.
    
    Args:
        user: User object
        permission: Permission string to check (e.g., "enforcesense:view")
    
    Raises:
        HTTPException: If user doesn't have permission
    """
    # Check if user is super admin (has all permissions)
    if hasattr(user, 'is_super_admin') and user.is_super_admin:
        return
    
    # Check if user has the permission
    user_permissions = user.permissions or []
    if permission not in user_permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Permission '{permission}' required"
        )

