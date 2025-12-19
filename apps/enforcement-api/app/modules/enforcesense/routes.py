#!/usr/bin/env python3
"""
EnforceSense module routes for Enforcement API

Minimal endpoints to prove the boundary.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timezone
import uuid

from app.core.database import get_async_db
from app.core.dependencies import get_current_tenant
from app.models.tenant import Tenant
from app.modules.enforcesense.models import Case, DebtorParty, CaseStatus, CaseType

router = APIRouter(prefix="/enforcesense", tags=["enforcesense"])


# Pydantic models for request/response
class CaseCreate(BaseModel):
    case_reference: str
    client_id: Optional[str] = None
    debtor_id: str
    case_type: CaseType
    original_amount: float


class CaseResponse(BaseModel):
    id: str
    tenant_id: str
    case_reference: str
    client_account_id: Optional[str]
    debtor_party_id: str
    case_type: Optional[str] = None
    status: str
    original_amount: float
    current_balance: float
    fees_charged: float = 0
    payments_received: float = 0
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
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """
    Get all cases for the current tenant (tenant-scoped).
    """
    # Filter by tenant_id
    stmt = select(Case).where(Case.tenant_id == current_tenant.id)
    result = await db.execute(stmt)
    cases = result.scalars().all()
    
    return [CaseResponse.model_validate(case) for case in cases]


@router.post("/cases", status_code=status.HTTP_201_CREATED, response_model=CaseResponse)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """
    Create a new enforcement case.
    """
    # Create new case
    new_case = Case(
        id=str(uuid.uuid4()),
        tenant_id=current_tenant.id,
        debtor_party_id=case_data.debtor_id,
        client_account_id=case_data.client_id,
        case_reference=case_data.case_reference,
        case_type=case_data.case_type,
        status=CaseStatus.DRAFT,
        original_amount=case_data.original_amount,
        current_balance=case_data.original_amount,
        fees_charged=0,
        payments_received=0
    )
    
    db.add(new_case)
    await db.commit()
    await db.refresh(new_case)
    
    return CaseResponse.model_validate(new_case)


@router.get("/debtors/{debtor_id}", response_model=DebtorResponse)
async def get_debtor(
    debtor_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_tenant: Tenant = Depends(get_current_tenant),
):
    """
    Get a debtor by ID (tenant-scoped).
    """
    # Query debtor with tenant filtering
    stmt = select(DebtorParty).where(
        DebtorParty.id == debtor_id,
        DebtorParty.tenant_id == current_tenant.id
    )
    result = await db.execute(stmt)
    debtor = result.scalar_one_or_none()
    
    if debtor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debtor not found"
        )
    
    return DebtorResponse.model_validate(debtor)

