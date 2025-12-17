"""
FastAPI dependencies for Enforcement API
"""

from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_async_db

# TODO: Implement auth dependencies
# These will use shared auth helpers from packages/shared

async def get_current_user():
    """Get current authenticated user (placeholder)"""
    # TODO: Implement JWT token validation
    # TODO: Use shared auth helpers
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Authentication not yet implemented"
    )


async def get_current_tenant():
    """Get current tenant (placeholder)"""
    # TODO: Extract tenant from user or request
    # TODO: Use shared tenant helpers
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Tenant resolution not yet implemented"
    )

