#!/usr/bin/env python3
"""
Debtor Portal routes for Enforcement API

Handles secure token-based authentication for debtor portal.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional
from pydantic import BaseModel, ConfigDict
from datetime import datetime, timedelta, timezone
import secrets
import uuid

from app.core.database import get_async_db
from app.modules.enforcesense.models import Case, DebtorParty
from app.modules.enforcesense.portal_models import PortalSession

router = APIRouter(prefix="/portal", tags=["portal"])


# Pydantic models
class PortalSessionCreate(BaseModel):
    case_reference: str
    debtor_id: Optional[str] = None
    locale: Optional[str] = "en"


class PortalSessionResponse(BaseModel):
    token: str
    expires_at: str
    case_id: str
    locale: str


class PortalCaseResponse(BaseModel):
    id: str
    case_reference: str
    status: str
    original_amount: float
    current_balance: float
    
    model_config = ConfigDict(from_attributes=True)


# Rate limiting: Max 5 session creation attempts per hour per case_reference
# (This would ideally be in Redis, but for now we'll check database)


@router.post("/sessions", response_model=PortalSessionResponse)
async def create_portal_session(
    session_data: PortalSessionCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a debtor portal session for a case.
    
    Returns a short-lived token for accessing case details.
    
    Rate limiting: Max 5 attempts per hour per case_reference.
    """
    # Look up case by reference
    stmt = select(Case).where(Case.case_reference == session_data.case_reference)
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found with the provided reference"
        )
    
    # If debtor_id provided, validate it matches the case
    if session_data.debtor_id and case.debtor_party_id != session_data.debtor_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Debtor ID does not match case"
        )
    
    # Rate limiting: Check recent session creation attempts
    one_hour_ago = datetime.now(timezone.utc) - timedelta(hours=1)
    recent_sessions_stmt = select(PortalSession).where(
        and_(
            PortalSession.case_reference == session_data.case_reference,
            PortalSession.created_at >= one_hour_ago,
            PortalSession.is_revoked == False
        )
    )
    recent_result = await db.execute(recent_sessions_stmt)
    recent_sessions = recent_result.scalars().all()
    
    if len(recent_sessions) >= 5:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many session creation attempts. Please try again later."
        )
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    # Set expiry (24 hours)
    expires_at = datetime.now(timezone.utc) + timedelta(hours=24)
    
    # Get client IP for rate limiting
    client_ip = request.client.host if request.client else None
    
    # Create portal session
    portal_session = PortalSession(
        id=str(uuid.uuid4()),
        token=token,
        tenant_id=case.tenant_id,
        case_id=case.id,
        debtor_id=case.debtor_party_id,
        case_reference=session_data.case_reference,
        expires_at=expires_at,
        last_access_ip=client_ip
    )
    
    db.add(portal_session)
    await db.commit()
    await db.refresh(portal_session)
    
    return PortalSessionResponse(
        token=token,
        expires_at=expires_at.isoformat(),
        case_id=case.id,
        locale=session_data.locale or "en"
    )


async def authenticate_debtor_token(
    x_debtor_token: Optional[str] = Header(None, alias="X-Debtor-Token"),
    request: Request = None,
    db: AsyncSession = Depends(get_async_db)
) -> PortalSession:
    """
    Dependency to authenticate debtor portal token.
    
    Validates token from database and checks expiry.
    """
    if not x_debtor_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Debtor-Token header"
        )
    
    # Query token from database
    stmt = select(PortalSession).where(PortalSession.token == x_debtor_token)
    result = await db.execute(stmt)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Check if token is valid (not expired and not revoked)
    if not session.is_valid():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired or been revoked"
        )
    
    # Update last accessed timestamp and access count
    session.last_accessed_at = datetime.now(timezone.utc)
    session.access_count += 1
    if request and request.client:
        session.last_access_ip = request.client.host
    
    await db.commit()
    await db.refresh(session)
    
    return session


@router.get("/cases/{case_id}", response_model=PortalCaseResponse)
async def get_portal_case(
    case_id: str,
    db: AsyncSession = Depends(get_async_db),
    session: PortalSession = Depends(authenticate_debtor_token),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    """
    Get case details for debtor portal (requires portal token).
    
    Returns localized case information.
    """
    # Verify token has access to this case
    if session.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token does not have access to this case"
        )
    
    # Query case from database
    stmt = select(Case).where(
        Case.id == case_id,
        Case.tenant_id == session.tenant_id
    )
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return PortalCaseResponse(
        id=case.id,
        case_reference=case.case_reference,
        status=case.status.value if hasattr(case.status, 'value') else str(case.status),
        original_amount=float(case.original_amount),
        current_balance=float(case.current_balance)
    )


@router.get("/cases/{case_id}/transactions")
async def get_case_transactions(
    case_id: str,
    db: AsyncSession = Depends(get_async_db),
    session: PortalSession = Depends(authenticate_debtor_token)
):
    """
    Get transaction history for a case (payment history).
    
    TODO: Implement when CaseTransaction model exists.
    """
    # Verify token has access
    if session.case_id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token does not have access to this case"
        )
    
    # TODO: Query transactions from database when CaseTransaction model exists
    # For now, return empty list
    return []

