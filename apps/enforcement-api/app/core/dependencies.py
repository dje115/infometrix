#!/usr/bin/env python3
"""
FastAPI dependencies for Enforcement API

Shared auth/tenant context with Platform API.
"""

from fastapi import Depends, HTTPException, status, Request, Cookie
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from jose import jwt

from app.core.config import settings
from app.core.database import get_async_db
# TODO: Import from shared package when created
# from packages.shared.types.tenant import TenantContext
# from packages.shared.types.auth import AuthClaims

# Security - HTTPBearer for Authorization header
security = HTTPBearer(auto_error=False)


async def get_current_user(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    access_token_cookie: Optional[str] = Cookie(None, alias="access_token"),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current authenticated user from JWT token.
    
    TODO: Implement proper JWT validation using shared auth library.
    For now, this is a placeholder.
    """
    # TODO: Implement JWT validation
    # This should use the shared auth library from packages/shared
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented in Enforcement API"
    )


async def get_current_tenant(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get current tenant from user context.
    
    TODO: Implement tenant resolution using shared library.
    """
    # TODO: Implement tenant resolution
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Tenant resolution not yet implemented in Enforcement API"
    )

