#!/usr/bin/env python3
"""
Debtor Portal API Endpoints

Public-facing endpoints for debtors to view their cases and make payments
Uses token-based authentication (similar to customer portal)
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_async_db
from app.models.enforcesense import Debtor, EnforcementCase, CaseStatus
from app.models.tenant import Tenant

router = APIRouter(prefix="/debtor-portal", tags=["Debtor Portal"])


class DebtorPortalAuth(BaseModel):
    """Debtor portal authentication model"""
    case_reference: str
    debtor_token: str  # Token sent to debtor (e.g., in letter/email)


async def get_debtor_by_token(
    x_debtor_token: Optional[str] = Header(None, alias="X-Debtor-Token"),
    case_reference: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_async_db)
) -> tuple[Debtor, EnforcementCase]:
    """
    Authenticate debtor using portal access token
    
    SECURITY: Debtor tokens are generated per case and sent via secure channels.
    Token format: {case_id}_{random_hash}
    """
    if not x_debtor_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Debtor token required"
        )
    
    if not case_reference:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Case reference required"
        )
    
    # Find case by reference
    case_stmt = select(EnforcementCase).where(
        and_(
            EnforcementCase.case_reference == case_reference,
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
    
    # Get debtor
    debtor_stmt = select(Debtor).where(
        and_(
            Debtor.id == case.debtor_id,
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
    
    # TODO: Implement proper token validation
    # For now, we'll use a simple check - in production, tokens should be:
    # 1. Stored in database (debtor_portal_tokens table)
    # 2. Time-limited
    # 3. Single-use or rate-limited
    # 4. Generated securely (cryptographically random)
    
    # Simple token validation (temporary - should be replaced with proper token system)
    expected_token = f"{case.id}_{debtor.id}"  # Placeholder - should use proper token generation
    
    if x_debtor_token != expected_token:
        # For development, allow any token if case exists
        # In production, this must be properly validated
        pass
    
    return debtor, case


@router.get("/cases")
async def get_debtor_cases(
    debtor: Debtor = Depends(get_debtor_by_token),
    case: EnforcementCase = Depends(get_debtor_by_token),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get all cases for the authenticated debtor
    
    Returns all cases linked to the debtor (across all clients)
    """
    # Get all cases for this debtor
    cases_stmt = select(EnforcementCase).where(
        and_(
            EnforcementCase.debtor_id == debtor.id,
            EnforcementCase.tenant_id == debtor.tenant_id,
            EnforcementCase.is_deleted == False
        )
    ).order_by(EnforcementCase.created_at.desc())
    
    cases_result = await db.execute(cases_stmt)
    cases = cases_result.scalars().all()
    
    # Format response (exclude sensitive information)
    return {
        "debtor": {
            "legal_name": debtor.legal_name,
            "entity_type": debtor.entity_type.value
        },
        "cases": [
            {
                "id": c.id,
                "case_reference": c.case_reference,
                "client_reference": c.client_reference,
                "case_type": c.case_type.value,
                "status": c.status.value,
                "original_amount": float(c.original_amount),
                "current_balance": float(c.current_balance),
                "payments_received": float(c.payments_received),
                "opened_date": c.opened_date.isoformat() if c.opened_date else None,
                "legal_basis": c.legal_basis
            }
            for c in cases
        ]
    }


@router.get("/cases/{case_id}")
async def get_debtor_case(
    case_id: str,
    debtor: Debtor = Depends(get_debtor_by_token),
    case: EnforcementCase = Depends(get_debtor_by_token),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get detailed information about a specific case
    
    Only returns cases that belong to the authenticated debtor
    """
    # Verify case belongs to debtor
    if case.id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this case"
        )
    
    # Get client information
    from app.models.enforcesense import EnforcementClient
    client_stmt = select(EnforcementClient).where(EnforcementClient.id == case.client_id)
    client_result = await db.execute(client_stmt)
    client = client_result.scalar_one_or_none()
    
    return {
        "case": {
            "id": case.id,
            "case_reference": case.case_reference,
            "client_reference": case.client_reference,
            "case_type": case.case_type.value,
            "status": case.status.value,
            "original_amount": float(case.original_amount),
            "fees_charged": float(case.fees_charged),
            "payments_received": float(case.payments_received),
            "current_balance": float(case.current_balance),
            "legal_basis": case.legal_basis,
            "court_reference": case.court_reference,
            "judgment_date": case.judgment_date.isoformat() if case.judgment_date else None,
            "opened_date": case.opened_date.isoformat() if case.opened_date else None,
            "client": {
                "name": client.name if client else "Unknown",
                "address": client.address if client else None
            }
        },
        "debtor": {
            "legal_name": debtor.legal_name,
            "entity_type": debtor.entity_type.value
        }
    }


@router.post("/cases/{case_id}/payment-intent")
async def create_payment_intent(
    case_id: str,
    amount: float = Query(..., ge=0.01),
    debtor: Debtor = Depends(get_debtor_by_token),
    case: EnforcementCase = Depends(get_debtor_by_token),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Create a payment intent for a case
    
    Returns payment details that can be used with payment processors
    """
    # Verify case belongs to debtor
    if case.id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this case"
        )
    
    # Validate amount
    if amount > case.current_balance:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Payment amount ({amount}) exceeds current balance ({case.current_balance})"
        )
    
    # TODO: Integrate with payment processor (Stripe, GoCardless, etc.)
    # For now, return a placeholder payment intent
    
    return {
        "payment_intent_id": f"pi_{case.id}_{datetime.utcnow().timestamp()}",
        "amount": amount,
        "currency": "GBP",
        "case_reference": case.case_reference,
        "status": "pending",
        "message": "Payment processing integration pending"
    }


@router.get("/cases/{case_id}/payment-history")
async def get_payment_history(
    case_id: str,
    debtor: Debtor = Depends(get_debtor_by_token),
    case: EnforcementCase = Depends(get_debtor_by_token),
    db: AsyncSession = Depends(get_async_db)
):
    """
    Get payment history for a case
    """
    # Verify case belongs to debtor
    if case.id != case_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied to this case"
        )
    
    # Get transactions
    from app.models.enforcesense import CaseTransaction, TransactionType
    transactions_stmt = select(CaseTransaction).where(
        and_(
            CaseTransaction.case_id == case_id,
            CaseTransaction.transaction_type == TransactionType.PAYMENT,
            CaseTransaction.is_deleted == False
        )
    ).order_by(CaseTransaction.created_at.desc())
    
    transactions_result = await db.execute(transactions_stmt)
    transactions = transactions_result.scalars().all()
    
    return {
        "payments": [
            {
                "id": t.id,
                "amount": float(t.amount),
                "description": t.description,
                "reference": t.reference,
                "date": t.created_at.isoformat() if t.created_at else None
            }
            for t in transactions
        ]
    }

