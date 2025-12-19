#!/usr/bin/env python3
"""
Debtor Portal routes for Enforcement API

Handles secure token-based authentication for debtor portal.
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets

from app.core.database import get_async_db
from app.modules.enforcesense.models import Case

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


# In-memory token store (TODO: Move to database/Redis in production)
_portal_tokens: dict[str, dict] = {}


@router.post("/sessions", response_model=PortalSessionResponse)
async def create_portal_session(
    session_data: PortalSessionCreate,
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a debtor portal session for a case.
    
    Returns a short-lived token for accessing case details.
    """
    # TODO: Validate case_reference and debtor_id
    # TODO: Check tenant access
    
    # Generate secure token
    token = secrets.token_urlsafe(32)
    
    # Set expiry (24 hours)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # TODO: Look up case by reference
    # For now, use placeholder
    case_id = "placeholder-case-id"
    
    # Store token (TODO: Store in database/Redis)
    _portal_tokens[token] = {
        "case_id": case_id,
        "case_reference": session_data.case_reference,
        "debtor_id": session_data.debtor_id,
        "locale": session_data.locale or "en",
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.utcnow().isoformat()
    }
    
    return PortalSessionResponse(
        token=token,
        expires_at=expires_at.isoformat(),
        case_id=case_id,
        locale=session_data.locale or "en"
    )


def authenticate_debtor_token(
    x_debtor_token: Optional[str] = Header(None, alias="X-Debtor-Token")
) -> dict:
    """
    Dependency to authenticate debtor portal token.
    
    TODO: Implement proper token validation with expiry checking.
    """
    if not x_debtor_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing X-Debtor-Token header"
        )
    
    # Check token exists
    token_data = _portal_tokens.get(x_debtor_token)
    if not token_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    # Check expiry
    expires_at = datetime.fromisoformat(token_data["expires_at"])
    if datetime.utcnow() > expires_at:
        # Remove expired token
        del _portal_tokens[x_debtor_token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    
    return token_data


@router.get("/cases/{case_id}", response_model=PortalCaseResponse)
async def get_portal_case(
    case_id: str,
    db: AsyncSession = Depends(get_async_db),
    token_data: dict = Depends(authenticate_debtor_token),
    accept_language: Optional[str] = Header(None, alias="Accept-Language")
):
    """
    Get case details for debtor portal (requires portal token).
    
    Returns localized case information.
    """
    # Verify token has access to this case
    if token_data["case_id"] != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token does not have access to this case"
        )
    
    # TODO: Query case from database when tables exist
    # For now, return placeholder
    # stmt = select(Case).where(
    #     Case.id == case_id,
    #     Case.tenant_id == token_data.get("tenant_id")
    # )
    # result = await db.execute(stmt)
    # case = result.scalar_one_or_none()
    
    # if not case:
    #     raise HTTPException(
    #         status_code=status.HTTP_404_NOT_FOUND,
    #         detail="Case not found"
    #     )
    
    # Placeholder response
    return PortalCaseResponse(
        id=case_id,
        case_reference=token_data["case_reference"],
        status="active",
        original_amount=1000.00,
        current_balance=850.00
    )


@router.get("/cases/{case_id}/transactions")
async def get_case_transactions(
    case_id: str,
    db: AsyncSession = Depends(get_async_db),
    token_data: dict = Depends(authenticate_debtor_token)
):
    """
    Get transaction history for a case (payment history).
    
    TODO: Implement when CaseTransaction model exists.
    """
    # Verify token has access
    if token_data["case_id"] != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Token does not have access to this case"
        )
    
    # TODO: Query transactions from database
    return []

