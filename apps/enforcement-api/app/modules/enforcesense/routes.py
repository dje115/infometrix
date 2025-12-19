#!/usr/bin/env python3
"""
EnforceSense module routes for Enforcement API

Minimal endpoints to prove the boundary.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel

from app.core.database import get_async_db
from app.core.dependencies import get_current_tenant
from app.modules.enforcesense.models import Case, DebtorParty, CaseStatus

router = APIRouter(prefix="/enforcesense", tags=["enforcesense"])


# Pydantic models for request/response
class CaseCreate(BaseModel):
    case_reference: str
    client_account_id: Optional[str] = None
    debtor_party_id: str
    original_amount: float
    status: str = "draft"


class CaseResponse(BaseModel):
    id: str
    tenant_id: str
    case_reference: str
    client_account_id: Optional[str]
    debtor_party_id: str
    status: str
    original_amount: float
    current_balance: float
    created_at: str
    
    model_config = ConfigDict(from_attributes=True)


class DebtorResponse(BaseModel):
    id: str
    tenant_id: str
    entity_type: str
    legal_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    preferred_language: str
    
    model_config = ConfigDict(from_attributes=True)


@router.get("/cases", response_model=List[CaseResponse])
async def get_cases(
    db: AsyncSession = Depends(get_async_db),
    # TODO: Add tenant dependency when auth is implemented
    # current_tenant = Depends(get_current_tenant),
):
    """
    Get all cases for the current tenant (tenant-scoped).
    
    TODO: Add tenant filtering when auth is implemented.
    """
    # TODO: Filter by tenant_id when auth is implemented
    # For now, return empty list as placeholder
    # stmt = select(Case).limit(0)  # Placeholder - no cases yet
    # result = await db.execute(stmt)
    # cases = result.scalars().all()
    
    # Return empty list for now (tables don't exist yet)
    return []


@router.post("/cases", status_code=status.HTTP_201_CREATED, response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_async_db),
    # TODO: Add tenant dependency when auth is implemented
    # current_tenant = Depends(get_current_tenant),
):
    """
    Create a new enforcement case.
    
    TODO: Add tenant assignment and validation when auth is implemented.
    """
    # TODO: Get tenant_id from current_tenant when auth is implemented
    tenant_id = "placeholder"  # Placeholder
    
    # TODO: Create case when database tables exist
    # For now, return placeholder response
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Case creation not yet implemented (database tables need to be created)"
    )


@router.get("/debtors/{debtor_id}", response_model=DebtorResponse)
async def get_debtor(
    debtor_id: str,
    db: AsyncSession = Depends(get_async_db),
    # TODO: Add tenant dependency when auth is implemented
    # current_tenant = Depends(get_current_tenant),
):
    """
    Get a debtor by ID (tenant-scoped).
    
    TODO: Add tenant filtering when auth is implemented.
    """
    # TODO: Query debtor when database tables exist
    # For now, return placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Debtor lookup not yet implemented (database tables need to be created)"
    )

