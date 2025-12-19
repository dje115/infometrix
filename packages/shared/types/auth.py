"""
Authentication and authorization types
"""

from typing import Optional, List
from pydantic import BaseModel


class AuthClaims(BaseModel):
    """JWT token claims"""
    
    sub: str  # User ID
    email: str
    tenant_id: str
    permissions: List[str]
    role: Optional[str] = None
    exp: Optional[int] = None
    iat: Optional[int] = None

