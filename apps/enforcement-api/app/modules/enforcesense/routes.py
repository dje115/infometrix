#!/usr/bin/env python3
"""
EnforceSense API Endpoints

Core Domain Model:
- Debtor: Real-world person OR legal entity that owes money
- Client: Creditor or instructing organisation
- Case: Single enforcement instruction linking ONE Debtor to ONE Client

CRITICAL FINANCIAL RULES:
- Ledger is single source of truth for all financial movements
- All balances are derived from ledger entries, never stored directly
- See: docs/enforcesense/FINANCIAL_MODEL.md for complete specification
- See: docs/enforcesense/DEVELOPMENT_RULES.md for development rules
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime, timezone
import uuid

from app.core.dependencies import get_current_user, get_current_tenant, check_permission
from app.core.database import get_async_db
from app.models.tenant import User, Tenant
from app.modules.enforcesense.models import (
    Debtor, EnforcementClient, EnforcementCase, CaseTransaction, CaseNote,
    DebtorEntityType, CaseStatus, CaseType, TransactionType
)

router = APIRouter(prefix="/enforcesense", tags=["EnforceSense"])


# ============================================================================
# Pydantic Models
# ============================================================================

class DebtorCreate(BaseModel):
    entity_type: DebtorEntityType
    legal_name: str = Field(..., min_length=1, max_length=255)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    national_identifier: Optional[str] = None
    company_registration_number: Optional[str] = None
    trading_names: Optional[List[str]] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_history: Optional[List[Dict[str, Any]]] = None
    language_preference: str = "en"
    communication_preferences: Optional[Dict[str, Any]] = None
    is_vulnerable: bool = False
    vulnerability_notes: Optional[str] = None
    risk_flags: Optional[List[str]] = None
    external_references: Optional[Dict[str, Any]] = None


class DebtorUpdate(BaseModel):
    legal_name: Optional[str] = Field(None, min_length=1, max_length=255)
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    date_of_birth: Optional[datetime] = None
    national_identifier: Optional[str] = None
    company_registration_number: Optional[str] = None
    trading_names: Optional[List[str]] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address_history: Optional[List[Dict[str, Any]]] = None
    language_preference: Optional[str] = None
    communication_preferences: Optional[Dict[str, Any]] = None
    is_vulnerable: Optional[bool] = None
    vulnerability_notes: Optional[str] = None
    risk_flags: Optional[List[str]] = None
    external_references: Optional[Dict[str, Any]] = None


class DebtorResponse(BaseModel):
    id: str
    entity_type: str
    legal_name: str
    first_name: Optional[str]
    last_name: Optional[str]
    date_of_birth: Optional[datetime]
    national_identifier: Optional[str]
    company_registration_number: Optional[str]
    trading_names: List[str]
    email: Optional[str]
    phone: Optional[str]
    address_history: List[Dict[str, Any]]
    language_preference: str
    communication_preferences: Dict[str, Any]
    is_vulnerable: bool
    vulnerability_notes: Optional[str]
    risk_flags: List[str]
    external_references: Dict[str, Any]
    ai_summary: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClientCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    company_name: Optional[str] = None
    company_registration_number: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    reference_prefix: Optional[str] = None
    default_case_type: Optional[CaseType] = None
    settings: Optional[Dict[str, Any]] = None


class ClientUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    company_name: Optional[str] = None
    company_registration_number: Optional[str] = None
    email: Optional[EmailStr] = None
    phone: Optional[str] = None
    address: Optional[str] = None
    postcode: Optional[str] = None
    reference_prefix: Optional[str] = None
    default_case_type: Optional[CaseType] = None
    settings: Optional[Dict[str, Any]] = None


class ClientResponse(BaseModel):
    id: str
    name: str
    company_name: Optional[str]
    company_registration_number: Optional[str]
    email: Optional[str]
    phone: Optional[str]
    address: Optional[str]
    postcode: Optional[str]
    reference_prefix: Optional[str]
    default_case_type: Optional[str]
    settings: Dict[str, Any]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CaseCreate(BaseModel):
    debtor_id: str
    client_id: str
    case_reference: Optional[str] = None  # Auto-generated if not provided
    client_reference: Optional[str] = None
    case_type: CaseType
    status: CaseStatus = CaseStatus.DRAFT
    legal_basis: Optional[str] = None
    court_reference: Optional[str] = None
    judgment_date: Optional[datetime] = None
    original_amount: float = Field(0, ge=0)
    notes: Optional[str] = None
    assigned_agent: Optional[str] = None


class CaseUpdate(BaseModel):
    case_reference: Optional[str] = None
    client_reference: Optional[str] = None
    case_type: Optional[CaseType] = None
    status: Optional[CaseStatus] = None
    legal_basis: Optional[str] = None
    court_reference: Optional[str] = None
    judgment_date: Optional[datetime] = None
    original_amount: Optional[float] = Field(None, ge=0)
    enforcement_stage: Optional[str] = None
    assigned_agent: Optional[str] = None
    notes: Optional[str] = None
    risk_flags: Optional[List[str]] = None


class CaseResponse(BaseModel):
    id: str
    debtor_id: str
    client_id: str
    case_reference: str
    client_reference: Optional[str]
    case_type: str
    status: str
    legal_basis: Optional[str]
    court_reference: Optional[str]
    judgment_date: Optional[datetime]
    original_amount: float
    fees_charged: float
    payments_received: float
    current_balance: float
    enforcement_stage: Optional[str]
    assigned_agent: Optional[str]
    notes: Optional[str]
    communications: List[Dict[str, Any]]
    visits: List[Dict[str, Any]]
    actions: List[Dict[str, Any]]
    notices: List[Dict[str, Any]]
    risk_flags: List[str]
    ai_summary: Optional[str]
    opened_date: datetime
    closed_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    # Include related entities
    debtor: Optional[DebtorResponse] = None
    client: Optional[ClientResponse] = None

    class Config:
        from_attributes = True


# ============================================================================
# Debtor Endpoints
# ============================================================================

@router.get("/debtors", response_model=List[DebtorResponse])
async def list_debtors(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    entity_type: Optional[DebtorEntityType] = Query(None),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """List debtors with tenant isolation"""
    await check_permission(current_user, "enforcesense:view")
    
    stmt = select(Debtor).where(
        and_(
            Debtor.tenant_id == current_user.tenant_id,
            Debtor.is_deleted == False
        )
    )
    
    if search:
        stmt = stmt.where(
            or_(
                Debtor.legal_name.ilike(f"%{search}%"),
                Debtor.first_name.ilike(f"%{search}%"),
                Debtor.last_name.ilike(f"%{search}%"),
                Debtor.email.ilike(f"%{search}%"),
                Debtor.phone.ilike(f"%{search}%")
            )
        )
    
    if entity_type:
        stmt = stmt.where(Debtor.entity_type == entity_type)
    
    stmt = stmt.order_by(Debtor.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    debtors = result.scalars().all()
    
    return debtors


@router.get("/debtors/{debtor_id}", response_model=DebtorResponse)
async def get_debtor(
    debtor_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single debtor"""
    await check_permission(current_user, "enforcesense:view")
    
    stmt = select(Debtor).where(
        and_(
            Debtor.id == debtor_id,
            Debtor.tenant_id == current_user.tenant_id,
            Debtor.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    debtor = result.scalar_one_or_none()
    
    if not debtor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debtor not found"
        )
    
    return debtor


@router.post("/debtors", response_model=DebtorResponse, status_code=status.HTTP_201_CREATED)
async def create_debtor(
    debtor_data: DebtorCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new debtor"""
    await check_permission(current_user, "enforcesense:create_case")
    
    debtor = Debtor(
        tenant_id=current_user.tenant_id,
        entity_type=debtor_data.entity_type,
        legal_name=debtor_data.legal_name,
        first_name=debtor_data.first_name,
        last_name=debtor_data.last_name,
        date_of_birth=debtor_data.date_of_birth,
        national_identifier=debtor_data.national_identifier,
        company_registration_number=debtor_data.company_registration_number,
        trading_names=debtor_data.trading_names or [],
        email=debtor_data.email,
        phone=debtor_data.phone,
        address_history=debtor_data.address_history or [],
        language_preference=debtor_data.language_preference,
        communication_preferences=debtor_data.communication_preferences or {},
        is_vulnerable=debtor_data.is_vulnerable,
        vulnerability_notes=debtor_data.vulnerability_notes,
        risk_flags=debtor_data.risk_flags or [],
        external_references=debtor_data.external_references or {}
    )
    
    db.add(debtor)
    await db.commit()
    await db.refresh(debtor)
    
    return debtor


@router.put("/debtors/{debtor_id}", response_model=DebtorResponse)
async def update_debtor(
    debtor_id: str,
    debtor_data: DebtorUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Update a debtor"""
    await check_permission(current_user, "enforcesense:update_case")
    
    stmt = select(Debtor).where(
        and_(
            Debtor.id == debtor_id,
            Debtor.tenant_id == current_user.tenant_id,
            Debtor.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    debtor = result.scalar_one_or_none()
    
    if not debtor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debtor not found"
        )
    
    # Update fields
    update_data = debtor_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(debtor, field, value)
    
    await db.commit()
    await db.refresh(debtor)
    
    return debtor


@router.delete("/debtors/{debtor_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_debtor(
    debtor_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Soft delete a debtor"""
    await check_permission(current_user, "enforcesense:admin")
    
    stmt = select(Debtor).where(
        and_(
            Debtor.id == debtor_id,
            Debtor.tenant_id == current_user.tenant_id,
            Debtor.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    debtor = result.scalar_one_or_none()
    
    if not debtor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debtor not found"
        )
    
    # Check if debtor has active cases
    cases_stmt = select(func.count(EnforcementCase.id)).where(
        and_(
            EnforcementCase.debtor_id == debtor_id,
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.status != CaseStatus.CLOSED,
            EnforcementCase.is_deleted == False
        )
    )
    cases_result = await db.execute(cases_stmt)
    active_cases = cases_result.scalar()
    
    if active_cases > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot delete debtor with {active_cases} active case(s)"
        )
    
    debtor.is_deleted = True
    debtor.deleted_at = datetime.now(timezone.utc)
    
    await db.commit()


# ============================================================================
# Client Endpoints
# ============================================================================

@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """List clients with tenant isolation"""
    await check_permission(current_user, "enforcesense:view")
    
    stmt = select(EnforcementClient).where(
        and_(
            EnforcementClient.tenant_id == current_user.tenant_id,
            EnforcementClient.is_deleted == False
        )
    )
    
    if search:
        stmt = stmt.where(
            or_(
                EnforcementClient.name.ilike(f"%{search}%"),
                EnforcementClient.company_name.ilike(f"%{search}%"),
                EnforcementClient.email.ilike(f"%{search}%")
            )
        )
    
    stmt = stmt.order_by(EnforcementClient.name).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    clients = result.scalars().all()
    
    return clients


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single client"""
    await check_permission(current_user, "enforcesense:view")
    
    stmt = select(EnforcementClient).where(
        and_(
            EnforcementClient.id == client_id,
            EnforcementClient.tenant_id == current_user.tenant_id,
            EnforcementClient.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    return client


@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new client"""
    await check_permission(current_user, "enforcesense:admin")
    
    client = EnforcementClient(
        tenant_id=current_user.tenant_id,
        name=client_data.name,
        company_name=client_data.company_name,
        company_registration_number=client_data.company_registration_number,
        email=client_data.email,
        phone=client_data.phone,
        address=client_data.address,
        postcode=client_data.postcode,
        reference_prefix=client_data.reference_prefix,
        default_case_type=client_data.default_case_type,
        settings=client_data.settings or {}
    )
    
    db.add(client)
    await db.commit()
    await db.refresh(client)
    
    return client


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: str,
    client_data: ClientUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Update a client"""
    await check_permission(current_user, "enforcesense:admin")
    
    stmt = select(EnforcementClient).where(
        and_(
            EnforcementClient.id == client_id,
            EnforcementClient.tenant_id == current_user.tenant_id,
            EnforcementClient.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    client = result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Update fields
    update_data = client_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    
    await db.commit()
    await db.refresh(client)
    
    return client


# ============================================================================
# Case Endpoints
# ============================================================================

def generate_case_reference(tenant_id: str, client: Optional[EnforcementClient] = None) -> str:
    """Generate a unique case reference"""
    prefix = client.reference_prefix if client and client.reference_prefix else "ES"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d")
    unique_id = str(uuid.uuid4())[:8].upper()
    return f"{prefix}-{timestamp}-{unique_id}"


@router.get("/cases", response_model=List[CaseResponse])
async def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[CaseStatus] = Query(None),
    debtor_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """List cases with tenant isolation"""
    await check_permission(current_user, "enforcesense:view_cases")
    
    stmt = select(EnforcementCase).where(
        and_(
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    
    if search:
        stmt = stmt.join(Debtor).where(
            or_(
                EnforcementCase.case_reference.ilike(f"%{search}%"),
                EnforcementCase.client_reference.ilike(f"%{search}%"),
                Debtor.legal_name.ilike(f"%{search}%")
            )
        )
    
    if status:
        stmt = stmt.where(EnforcementCase.status == status)
    
    if debtor_id:
        stmt = stmt.where(EnforcementCase.debtor_id == debtor_id)
    
    if client_id:
        stmt = stmt.where(EnforcementCase.client_id == client_id)
    
    stmt = stmt.order_by(EnforcementCase.created_at.desc()).offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    cases = result.scalars().all()
    
    return cases


@router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single case with related entities"""
    await check_permission(current_user, "enforcesense:view_cases")
    
    stmt = select(EnforcementCase).where(
        and_(
            EnforcementCase.id == case_id,
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Load related entities
    debtor_stmt = select(Debtor).where(Debtor.id == case.debtor_id)
    debtor_result = await db.execute(debtor_stmt)
    case.debtor = debtor_result.scalar_one_or_none()
    
    client_stmt = select(EnforcementClient).where(EnforcementClient.id == case.client_id)
    client_result = await db.execute(client_stmt)
    case.client = client_result.scalar_one_or_none()
    
    return case


@router.post("/cases", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case_data: CaseCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new case"""
    await check_permission(current_user, "enforcesense:create_case")
    
    # Verify debtor exists and belongs to tenant
    debtor_stmt = select(Debtor).where(
        and_(
            Debtor.id == case_data.debtor_id,
            Debtor.tenant_id == current_user.tenant_id,
            Debtor.is_deleted == False
        )
    )
    debtor_result = await db.execute(debtor_stmt)
    debtor = debtor_result.scalar_one_or_none()
    
    if not debtor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Debtor not found"
        )
    
    # Verify client exists and belongs to tenant
    client_stmt = select(EnforcementClient).where(
        and_(
            EnforcementClient.id == case_data.client_id,
            EnforcementClient.tenant_id == current_user.tenant_id,
            EnforcementClient.is_deleted == False
        )
    )
    client_result = await db.execute(client_stmt)
    client = client_result.scalar_one_or_none()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Client not found"
        )
    
    # Generate case reference if not provided
    case_reference = case_data.case_reference
    if not case_reference:
        case_reference = generate_case_reference(current_user.tenant_id, client)
        # Ensure uniqueness
        existing_stmt = select(EnforcementCase).where(
            EnforcementCase.case_reference == case_reference
        )
        existing_result = await db.execute(existing_stmt)
        if existing_result.scalar_one_or_none():
            # Retry with different unique ID
            case_reference = generate_case_reference(current_user.tenant_id, client)
    
    case = EnforcementCase(
        tenant_id=current_user.tenant_id,
        debtor_id=case_data.debtor_id,
        client_id=case_data.client_id,
        case_reference=case_reference,
        client_reference=case_data.client_reference,
        case_type=case_data.case_type,
        status=case_data.status,
        legal_basis=case_data.legal_basis,
        court_reference=case_data.court_reference,
        judgment_date=case_data.judgment_date,
        original_amount=case_data.original_amount,
        current_balance=case_data.original_amount,  # Initial balance equals original amount
        notes=case_data.notes,
        assigned_agent=case_data.assigned_agent,
        opened_date=datetime.now(timezone.utc)
    )
    
    db.add(case)
    await db.commit()
    await db.refresh(case)
    
    # Load related entities for response
    case.debtor = debtor
    case.client = client
    
    return case


@router.put("/cases/{case_id}", response_model=CaseResponse)
async def update_case(
    case_id: str,
    case_data: CaseUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Update a case"""
    await check_permission(current_user, "enforcesense:update_case")
    
    stmt = select(EnforcementCase).where(
        and_(
            EnforcementCase.id == case_id,
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Update fields
    update_data = case_data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(case, field, value)
    
    # Handle status changes
    if case_data.status == CaseStatus.CLOSED and not case.closed_date:
        case.closed_date = datetime.now(timezone.utc)
    elif case_data.status != CaseStatus.CLOSED and case.closed_date:
        case.closed_date = None
    
    await db.commit()
    await db.refresh(case)
    
    # Load related entities
    debtor_stmt = select(Debtor).where(Debtor.id == case.debtor_id)
    debtor_result = await db.execute(debtor_stmt)
    case.debtor = debtor_result.scalar_one_or_none()
    
    client_stmt = select(EnforcementClient).where(EnforcementClient.id == case.client_id)
    client_result = await db.execute(client_stmt)
    case.client = client_result.scalar_one_or_none()
    
    return case


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get EnforceSense dashboard statistics"""
    await check_permission(current_user, "enforcesense:view")
    
    tenant_id = current_user.tenant_id
    
    # Count debtors
    debtors_stmt = select(func.count(Debtor.id)).where(
        and_(
            Debtor.tenant_id == tenant_id,
            Debtor.is_deleted == False
        )
    )
    debtors_result = await db.execute(debtors_stmt)
    total_debtors = debtors_result.scalar() or 0
    
    # Count clients
    clients_stmt = select(func.count(EnforcementClient.id)).where(
        and_(
            EnforcementClient.tenant_id == tenant_id,
            EnforcementClient.is_deleted == False
        )
    )
    clients_result = await db.execute(clients_stmt)
    total_clients = clients_result.scalar() or 0
    
    # Count cases by status
    cases_stmt = select(
        EnforcementCase.status,
        func.count(EnforcementCase.id).label("count")
    ).where(
        and_(
            EnforcementCase.tenant_id == tenant_id,
            EnforcementCase.is_deleted == False
        )
    ).group_by(EnforcementCase.status)
    cases_result = await db.execute(cases_stmt)
    cases_by_status = {row.status.value: row.count for row in cases_result}
    
    # Total financials
    financials_stmt = select(
        func.sum(EnforcementCase.original_amount).label("total_original"),
        func.sum(EnforcementCase.fees_charged).label("total_fees"),
        func.sum(EnforcementCase.payments_received).label("total_payments"),
        func.sum(EnforcementCase.current_balance).label("total_balance")
    ).where(
        and_(
            EnforcementCase.tenant_id == tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    financials_result = await db.execute(financials_stmt)
    financials = financials_result.first()
    
    return {
        "total_debtors": total_debtors,
        "total_clients": total_clients,
        "cases_by_status": cases_by_status,
        "total_original_amount": float(financials.total_original or 0),
        "total_fees_charged": float(financials.total_fees or 0),
        "total_payments_received": float(financials.total_payments or 0),
        "total_current_balance": float(financials.total_balance or 0)
    }


# ============================================================================
# Case Notes Endpoints (with AI Improvement)
# ============================================================================

class CaseNoteCreate(BaseModel):
    note: str
    trigger_ai: bool = True


class CaseNoteResponse(BaseModel):
    id: str
    case_id: str
    note: str
    original_note: Optional[str]
    ai_improved_note: Optional[str]
    ai_summary: Optional[str]
    risk_flags: List[str]
    ai_processing_status: str
    created_by: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


@router.post("/cases/{case_id}/notes", response_model=CaseNoteResponse, status_code=status.HTTP_201_CREATED)
async def add_case_note(
    case_id: str,
    note_data: CaseNoteCreate,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Add a note to a case with optional AI improvement"""
    await check_permission(current_user, "enforcesense:update_case")
    
    # Verify case exists and belongs to tenant
    stmt = select(EnforcementCase).where(
        and_(
            EnforcementCase.id == case_id,
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Create note
    case_note = CaseNote(
        tenant_id=current_user.tenant_id,
        case_id=case_id,
        note=note_data.note,
        original_note=note_data.note if note_data.trigger_ai else None,
        ai_processing_status='pending' if note_data.trigger_ai else 'not_requested',
        created_by=current_user.id
    )
    
    db.add(case_note)
    await db.commit()
    await db.refresh(case_note)
    
    # Trigger AI improvement asynchronously if requested
    if note_data.trigger_ai:
        import asyncio
        from app.services.enforcesense_ai_service import EnforceSenseAIService
        
        # Create AI service and trigger improvement asynchronously
        ai_service = EnforceSenseAIService(db, current_user.tenant_id)
        # Run in background task
        asyncio.create_task(ai_service.improve_note(case_note.id))
    
    return case_note


@router.get("/cases/{case_id}/notes", response_model=List[CaseNoteResponse])
async def get_case_notes(
    case_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get all notes for a case"""
    await check_permission(current_user, "enforcesense:view_cases")
    
    # Verify case exists and belongs to tenant
    stmt = select(EnforcementCase).where(
        and_(
            EnforcementCase.id == case_id,
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    # Get notes
    notes_stmt = select(CaseNote).where(
        and_(
            CaseNote.case_id == case_id,
            CaseNote.tenant_id == current_user.tenant_id
        )
    ).order_by(CaseNote.created_at.desc())
    
    notes_result = await db.execute(notes_stmt)
    notes = notes_result.scalars().all()
    
    return notes


@router.post("/cases/{case_id}/notes/{note_id}/improve", response_model=CaseNoteResponse)
async def improve_note(
    case_id: str,
    note_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Trigger AI improvement for a note"""
    await check_permission(current_user, "enforcesense:update_case")
    
    # Verify case and note exist
    case_stmt = select(EnforcementCase).where(
        and_(
            EnforcementCase.id == case_id,
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    case_result = await db.execute(case_stmt)
    case = case_result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    note_stmt = select(CaseNote).where(
        and_(
            CaseNote.id == note_id,
            CaseNote.case_id == case_id,
            CaseNote.tenant_id == current_user.tenant_id
        )
    )
    note_result = await db.execute(note_stmt)
    note = note_result.scalar_one_or_none()
    
    if not note:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found"
        )
    
    # Trigger AI improvement
    from app.services.enforcesense_ai_service import EnforceSenseAIService
    
    ai_service = EnforceSenseAIService(db, current_user.tenant_id)
    await ai_service.improve_note(note_id)
    
    await db.refresh(note)
    return note

