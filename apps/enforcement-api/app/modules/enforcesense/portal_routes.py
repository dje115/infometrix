"""
Debtor Portal API Routes
Secure endpoints for debtor portal access
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Request
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import secrets
import json
import logging

from app.core.database import get_async_db
from app.core.dependencies import get_current_tenant
from app.core.redis import get_redis

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/portal", tags=["portal"])

# Rate limiting constants
PORTAL_SESSION_RATE_LIMIT = 5  # Max 5 session creations per IP per minute
PORTAL_CASE_VIEW_RATE_LIMIT = 30  # Max 30 case views per IP per minute


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


# Session TTL: 24 hours in seconds
SESSION_TTL_SECONDS = 24 * 60 * 60


async def _get_session_from_redis(session_id: str) -> Optional[dict]:
    """Get portal session from Redis"""
    try:
        redis_client = await get_redis()
        if not redis_client:
            return None
        
        session_data = await redis_client.get(f"portal_session:{session_id}")
        if session_data:
            return json.loads(session_data)
        return None
    except Exception as e:
        logger.error(f"Error getting session from Redis: {e}")
        return None


async def _store_session_in_redis(session_id: str, session_data: dict, ttl: int = SESSION_TTL_SECONDS):
    """Store portal session in Redis"""
    try:
        redis_client = await get_redis()
        if not redis_client:
            logger.warning("Redis not available, session will not persist")
            return False
        
        await redis_client.setex(
            f"portal_session:{session_id}",
            ttl,
            json.dumps(session_data)
        )
        return True
    except Exception as e:
        logger.error(f"Error storing session in Redis: {e}")
        return False


async def _check_rate_limit(request: Request, key_prefix: str, limit: int, window_seconds: int = 60) -> bool:
    """Check rate limit using Redis"""
    try:
        redis_client = await get_redis()
        if not redis_client:
            # If Redis unavailable, allow request (fail open)
            return True
        
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Create rate limit key
        current_window = int(datetime.utcnow().timestamp() / window_seconds)
        rate_limit_key = f"rate_limit:{key_prefix}:{client_ip}:{current_window}"
        
        # Increment counter
        count = await redis_client.incr(rate_limit_key)
        if count == 1:
            # First request in window - set expiration
            await redis_client.expire(rate_limit_key, window_seconds + 10)
        
        # Check if limit exceeded
        if count > limit:
            logger.warning(f"Rate limit exceeded: {key_prefix} for IP {client_ip}: {count} requests")
            return False
        
        return True
    except Exception as e:
        logger.error(f"Error checking rate limit: {e}")
        # Fail open - allow request if rate limiting fails
        return True


@router.post("/sessions", status_code=status.HTTP_201_CREATED, response_model=PortalSessionResponse)
async def create_portal_session(
    session_data: PortalSessionCreate,
    request: Request,
    db: AsyncSession = Depends(get_async_db),
    current_tenant = Depends(get_current_tenant)
):
    """
    Create a portal session for a case/debtor.
    Returns a short-lived token (24 hours expiry).
    
    Rate limited: 5 requests per IP per minute.
    """
    # Check rate limit
    if not await _check_rate_limit(request, "portal_session_create", PORTAL_SESSION_RATE_LIMIT):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many session creation requests. Please try again later."
        )
    
    # Generate session ID and token
    session_id = secrets.token_urlsafe(32)
    token = secrets.token_urlsafe(48)
    expires_at = datetime.utcnow() + timedelta(seconds=SESSION_TTL_SECONDS)
    
    # Store session in Redis
    session_data_dict = {
        "session_id": session_id,
        "token": token,
        "case_id": session_data.case_id,
        "debtor_id": session_data.debtor_id,
        "tenant_id": current_tenant.id,
        "expires_at": expires_at.isoformat(),
        "created_at": datetime.utcnow().isoformat(),
        "preferred_language": "en",  # Default, can be updated from Accept-Language
    }
    
    stored = await _store_session_in_redis(session_id, session_data_dict, SESSION_TTL_SECONDS)
    if not stored:
        logger.warning(f"Failed to store session {session_id} in Redis, but continuing")
    
    logger.info(f"Portal session created: {session_id} for case {session_data.case_id}, tenant {current_tenant.id}")
    
    return PortalSessionResponse(
        session_id=session_id,
        token=token,
        expires_at=expires_at.isoformat(),
        case_id=session_data.case_id,
    )


@router.get("/cases/{case_id}", response_model=CasePortalResponse)
async def get_portal_case(
    case_id: str,
    request: Request,
    authorization: Optional[str] = Header(None),
    accept_language: Optional[str] = Header(None),
    db: AsyncSession = Depends(get_async_db),
    current_tenant = Depends(get_current_tenant)
):
    """
    Get case data for portal view.
    Requires portal token in Authorization header.
    
    Rate limited: 30 requests per IP per minute.
    """
    # Check rate limit
    if not await _check_rate_limit(request, "portal_case_view", PORTAL_CASE_VIEW_RATE_LIMIT):
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="Too many requests. Please try again later."
        )
    
    # Extract token from Authorization header
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning(f"Portal case access attempted without token for case {case_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Portal token required"
        )
    
    token = authorization.replace("Bearer ", "")
    
    # Find session by token in Redis
    # We need to search all sessions - in production, consider storing token->session_id mapping
    session = None
    try:
        redis_client = await get_redis()
        if redis_client:
            # Get all session keys (in production, use a token index)
            # For now, we'll search - in production, maintain token->session_id mapping
            keys = await redis_client.keys("portal_session:*")
            for key in keys:
                session_data = await redis_client.get(key)
                if session_data:
                    sess = json.loads(session_data)
                    if sess.get("token") == token:
                        # Check expiry
                        expires_at = datetime.fromisoformat(sess["expires_at"])
                        if datetime.utcnow() > expires_at:
                            logger.info(f"Portal session expired: {sess.get('session_id')}")
                            raise HTTPException(
                                status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Portal session expired"
                            )
                        session = sess
                        break
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding session in Redis: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error validating session"
        )
    
    if not session:
        logger.warning(f"Invalid portal token used for case {case_id}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid portal token"
        )
    
    # Verify tenant match
    if session["tenant_id"] != current_tenant.id:
        logger.warning(f"Tenant mismatch: session tenant {session['tenant_id']} != request tenant {current_tenant.id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    # Verify case ID match
    if session["case_id"] != case_id:
        logger.warning(f"Case ID mismatch: session case {session['case_id']} != request case {case_id}")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Case ID mismatch"
        )
    
    # Store locale preference from Accept-Language header
    locale = accept_language or session.get("preferred_language", "en")
    if locale and "," in locale:
        locale = locale.split(",")[0].strip()
    
    # Update locale in session if changed
    if session.get("preferred_language") != locale:
        session["preferred_language"] = locale
        await _store_session_in_redis(session["session_id"], session, SESSION_TTL_SECONDS)
    
    logger.info(f"Portal case accessed: {case_id} by session {session['session_id']}, locale: {locale}")
    
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

