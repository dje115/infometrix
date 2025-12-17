"""
Authentication and authorization types
"""

from typing import Optional, List
from pydantic import BaseModel


class AuthClaims(BaseModel):
    """JWT token claims"""
    user_id: str
    tenant_id: str
    email: str
    role: str
    permissions: List[str] = []
    is_super_admin: bool = False


class PortalTokenClaims(BaseModel):
    """Debtor portal token claims (separate from staff JWT)"""
    session_id: str
    case_id: str
    tenant_id: str
    debtor_id: Optional[str] = None
    expires_at: int  # Unix timestamp

