"""
Debtor Portal API Routes
Secure endpoints for debtor portal access
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets

from app.core.database import get_async_db
from app.core.dependencies import get_current_tenant

router = APIRouter(prefix="/portal", tags=["portal"])


class PortalSessionCreate(BaseModel):
    """Request to create a portal session"""
    case_id: str
    debtor_id: Optional[str] = None


class PortalSessionResponse(BaseModel):
    """Portal session response with token"""
    session_id: str
    token: str
    expires_at: str
    case_id: str


class CasePortalResponse(BaseModel):
    """Case data for portal view"""
    id: str
    case_number: str
    status: str
    amount: Optional[float] = None
    due_date: Optional[str] = None
    description: Optional[str] = None


# In-memory session store (TODO: Move to Redis/database in production)
portal_sessions: dict[str, dict] = {}


@router.post("/sessions", status_code=status.HTTP_201_CREATED, response_model=PortalSessionResponse)
async def create_portal_session(
    session_data: PortalSessionCreate,
    db: AsyncSession = Depends(get_async_db),
    current_tenant = Depends(get_current_tenant)
):
    """
    Create a portal session for a case/debtor.
    Returns a short-lived token (24 hours expiry).
    """
    # Generate session ID and token
    session_id = secrets.token_urlsafe(32)
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(hours=24)
    
    # Store session (TODO: Store in database/Redis)
    portal_sessions[session_id] = {
        "session_id": session_id,
        "token": token,
        "case_id": session_data.case_id,
        "debtor_id": session_data.debtor_id,
        "tenant_id": current_tenant.id,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
    }
    
    return PortalSessionResponse(
        session_id=session_id,
        token=token,
        expires_at=expires_at.isoformat(),
        case_id=session_data.case_id,
    )


@router.get("/cases/{case_id}", response_model=CasePortalResponse)
async def get_portal_case(
    case_id: str,
    authorization: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_async_db),
    current_tenant = Depends(get_current_tenant)
):
    """
    Get case data for portal view.
    Requires portal token in Authorization header.
    """
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Portal token required"
        )
    
    token = authorization.replace("Bearer ", "")
    
    # Find session by token
    session = None
    for sess in portal_sessions.values():
        if sess["token"] == token:
            # Check expiry
            expires_at = datetime.fromisoformat(sess["expires_at"])
            if datetime.utcnow() > expires_at:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Portal session expired"
                )
            session = sess
            break
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid portal token"
        )
    
    # Verify tenant match
    if session["tenant_id"] != current_tenant.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Verify case ID match
    if session["case_id"] != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Case ID mismatch"
        )
    
    # Store locale preference from Accept-Language header or session
    locale = accept_language or "en"
    if locale and "," in locale:
        locale = locale.split(",")[0].strip()
    
    # Store locale in session for future requests
    session["preferred_language"] = locale
    
    # TODO: Fetch actual case data from database
    # TODO: Apply locale-aware templates/strings where applicable
    # For now, return placeholder
    return CasePortalResponse(
        id=case_id,
        case_number=f"CASE-{case_id[:8]}",
        status="open",
        amount=None,
        due_date=None,
        description=None,
    )

