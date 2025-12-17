"""
EnforceSense Module API Routes
Minimal endpoints for debt recovery case management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_async_db
from app.core.dependencies import get_current_user, get_current_tenant
from app.modules.enforcesense.models import Case, DebtorParty, CaseStatus, DebtorType

router = APIRouter(prefix="/enforcesense", tags=["enforcesense"])


# Pydantic models for request/response
class CaseCreate(BaseModel):
    client_account_id: Optional[str] = None
    debtor_party_id: Optional[str] = None
    status: CaseStatus = CaseStatus.OPEN


class CaseResponse(BaseModel):
    id: str
    tenant_id: str
    client_account_id: Optional[str]
    debtor_party_id: Optional[str]
    status: str
    created_at: str
    
    class Config:
        from_attributes = True


class DebtorPartyResponse(BaseModel):
    id: str
    tenant_id: str
    type: str
    name: str
    address_ref: Optional[str]
    preferred_language: str
    created_at: str
    
    class Config:
        from_attributes = True


@router.get("/cases", response_model=List[CaseResponse])
async def get_cases(
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant)
):
    """
    Get all cases for the current tenant (tenant-scoped)
    """
    # TODO: Implement actual database query
    # For now, return empty list as placeholder
    return []


@router.post("/cases", status_code=status.HTTP_201_CREATED, response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant)
):
    """
    Create a new enforcement case (tenant-scoped)
    """
    # TODO: Implement actual case creation
    # For now, return placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Case creation not yet implemented"
    )


@router.get("/debtors/{debtor_id}", response_model=DebtorPartyResponse)
async def get_debtor(
    debtor_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user = Depends(get_current_user),
    current_tenant = Depends(get_current_tenant)
):
    """
    Get debtor party by ID (tenant-scoped)
    """
    # TODO: Implement actual database query
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Debtor lookup not yet implemented"
    )

