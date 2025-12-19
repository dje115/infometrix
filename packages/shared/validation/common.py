"""
Common validation helpers
"""

from typing import Any, Optional
from pydantic import BaseModel, validator


def validate_tenant_id(tenant_id: str) -> str:
    """Validate tenant ID format"""
    if not tenant_id or len(tenant_id) != 36:
        raise ValueError("Invalid tenant ID format")
    return tenant_id


def validate_module_id(module_id: str) -> str:
    """Validate module ID format"""
    valid_modules = ["crm", "helpdesk", "enforcesense", "quoting"]
    if module_id not in valid_modules:
        raise ValueError(f"Invalid module ID: {module_id}")
    return module_id

