"""
Tenant context types
"""

from typing import Optional
from pydantic import BaseModel


class TenantContext(BaseModel):
    """Tenant context for request processing"""
    
    tenant_id: str
    tenant_name: str
    tenant_slug: str
    enabled_modules: list[str]
    feature_flags: dict[str, bool]

