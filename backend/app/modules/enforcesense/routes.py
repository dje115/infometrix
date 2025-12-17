"""
EnforceSense Module API Routes

Placeholder routes for debt recovery case management.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_async_db
from app.core.dependencies import get_current_user, get_current_tenant
from app.models.tenant import User, Tenant

router = APIRouter(prefix="/enforcesense", tags=["enforcesense"])


# Pydantic models for API
class DebtorCreate(BaseModel):
    name: str
    type: str  # "person" or "company"
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None


class DebtorResponse(BaseModel):
    id: str
    name: str
    type: str
    email: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    created_at: str
    updated_at: str


class CaseCreate(BaseModel):
    client_id: str  # CRM Customer ID
    debtor_id: str
    case_number: str
    amount: float
    currency: str = "GBP"


class CaseResponse(BaseModel):
    id: str
    client_id: str
    debtor_id: str
    case_number: str
    status: str
    amount: float
    currency: str
    created_at: str
    updated_at: str


@router.get("/debtors", response_model=List[DebtorResponse])
async def list_debtors(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """
    List all debtors for the current tenant.
    
    Placeholder implementation - returns empty list for now.
    """
    # TODO: Implement actual database query
    return []


@router.post("/debtors", response_model=DebtorResponse)
async def create_debtor(
    debtor: DebtorCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """
    Create a new debtor.
    
    Placeholder implementation - returns error for now.
    """
    raise HTTPException(status_code=501, detail="EnforceSense module is under development")


@router.get("/cases", response_model=List[CaseResponse])
async def list_cases(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """
    List all cases for the current tenant.
    
    Placeholder implementation - returns empty list for now.
    """
    # TODO: Implement actual database query
    return []


@router.post("/cases", response_model=CaseResponse)
async def create_case(
    case: CaseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """
    Create a new case linking a client (from CRM) to a debtor.
    
    Placeholder implementation - returns error for now.
    """
    raise HTTPException(status_code=501, detail="EnforceSense module is under development")

