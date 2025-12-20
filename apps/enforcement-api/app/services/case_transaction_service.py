#!/usr/bin/env python3
"""
Case Transaction Service - Ledger System

CRITICAL FINANCIAL RULES:
- Ledger is single source of truth for all financial movements
- All balances are derived from ledger entries, never stored directly
- See: docs/enforcesense/FINANCIAL_MODEL.md for complete specification
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlalchemy.orm import selectinload

from app.modules.enforcesense.models import (
    EnforcementCase,
    LedgerEntry,
    LedgerEntryType,
    LedgerEntryStatus
)

logger = logging.getLogger(__name__)


class CaseTransactionService:
    """
    Service for managing case transactions and ledger entries.
    
    CRITICAL: All financial movements go through the ledger.
    Balances are always derived from ledger entries, never stored.
    """
    
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def create_ledger_entry(
        self,
        case_id: str,
        entry_type: LedgerEntryType,
        amount: Decimal,
        description: Optional[str] = None,
        reference: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None,
        status: LedgerEntryStatus = LedgerEntryStatus.PENDING
    ) -> LedgerEntry:
        """
        Create a new ledger entry (immutable).
        
        Args:
            case_id: Case ID
            entry_type: Type of ledger entry
            amount: Amount (always positive, direction determined by entry_type)
            description: Description
            reference: External reference
            metadata: Additional metadata
            created_by: User ID who created the entry
            status: Entry status (default: PENDING)
        
        Returns:
            Created LedgerEntry
        """
        # Validate case exists and belongs to tenant
        case_stmt = select(EnforcementCase).where(
            and_(
                EnforcementCase.id == case_id,
                EnforcementCase.tenant_id == self.tenant_id,
                EnforcementCase.is_deleted == False
            )
        )
        case_result = await self.db.execute(case_stmt)
        case = case_result.scalar_one_or_none()
        
        if not case:
            raise ValueError(f"Case {case_id} not found or not accessible")
        
        # Validate amount is positive
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        # Create ledger entry
        ledger_entry = LedgerEntry(
            tenant_id=self.tenant_id,
            case_id=case_id,
            entry_type=entry_type,
            amount=amount,
            description=description,
            reference=reference,
            metadata=metadata or {},
            created_by=created_by,
            status=status,
            posted_at=datetime.now(timezone.utc) if status == LedgerEntryStatus.CLEARED else None
        )
        
        self.db.add(ledger_entry)
        await self.db.flush()
        
        # Update case financial totals (derived from ledger)
        await self._update_case_totals(case_id)
        
        logger.info(
            f"Created ledger entry: {entry_type.value} {amount} for case {case_id}",
            extra={"case_id": case_id, "entry_type": entry_type.value, "amount": float(amount)}
        )
        
        return ledger_entry
    
    async def get_case_ledger(
        self,
        case_id: str,
        entry_types: Optional[List[LedgerEntryType]] = None,
        status: Optional[LedgerEntryStatus] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[LedgerEntry]:
        """
        Get ledger entries for a case.
        
        Args:
            case_id: Case ID
            entry_types: Filter by entry types (optional)
            status: Filter by status (optional)
            limit: Maximum number of entries
            offset: Offset for pagination
        
        Returns:
            List of LedgerEntry objects
        """
        stmt = select(LedgerEntry).where(
            and_(
                LedgerEntry.case_id == case_id,
                LedgerEntry.tenant_id == self.tenant_id,
                LedgerEntry.is_deleted == False
            )
        )
        
        if entry_types:
            stmt = stmt.where(LedgerEntry.entry_type.in_(entry_types))
        
        if status:
            stmt = stmt.where(LedgerEntry.status == status)
        
        stmt = stmt.order_by(LedgerEntry.posted_at.desc(), LedgerEntry.created_at.desc())
        stmt = stmt.limit(limit).offset(offset)
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_case_balance(self, case_id: str) -> Dict[str, Decimal]:
        """
        Calculate case balance from ledger entries.
        
        CRITICAL: Balance is derived from ledger, never stored.
        
        Returns:
            Dict with:
            - total_debt: Sum of principal charges
            - total_fees: Sum of fees charged
            - total_payments: Sum of payments received
            - total_interest: Sum of interest accrued
            - current_balance: total_debt + total_fees + total_interest - total_payments
        """
        stmt = select(
            LedgerEntry.entry_type,
            func.sum(LedgerEntry.amount).label('total')
        ).where(
            and_(
                LedgerEntry.case_id == case_id,
                LedgerEntry.tenant_id == self.tenant_id,
                LedgerEntry.is_deleted == False,
                LedgerEntry.status != LedgerEntryStatus.REVERSED
            )
        ).group_by(LedgerEntry.entry_type)
        
        result = await self.db.execute(stmt)
        totals = {row.entry_type: Decimal(str(row.total or 0)) for row in result.all()}
        
        # Calculate balances
        total_debt = totals.get(LedgerEntryType.FEE_CHARGED, Decimal(0))  # Principal charges
        total_fees = totals.get(LedgerEntryType.FEE_EARNED, Decimal(0))
        total_payments = totals.get(LedgerEntryType.DEBTOR_PAYMENT, Decimal(0))
        total_interest = totals.get(LedgerEntryType.INTEREST_ACCRUED, Decimal(0))
        total_refunds = totals.get(LedgerEntryType.REFUND, Decimal(0))
        total_adjustments = totals.get(LedgerEntryType.ADJUSTMENT, Decimal(0))
        
        # Current balance = debt + fees + interest - payments - refunds + adjustments
        current_balance = (
            total_debt + total_fees + total_interest - 
            total_payments - total_refunds + total_adjustments
        )
        
        return {
            "total_debt": total_debt,
            "total_fees": total_fees,
            "total_payments": total_payments,
            "total_interest": total_interest,
            "total_refunds": total_refunds,
            "total_adjustments": total_adjustments,
            "current_balance": current_balance
        }
    
    async def record_principal_charge(
        self,
        case_id: str,
        amount: Decimal,
        description: Optional[str] = None,
        reference: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> LedgerEntry:
        """
        Record a principal charge (debt amount).
        
        Args:
            case_id: Case ID
            amount: Principal amount
            description: Description
            reference: External reference
            created_by: User ID
        
        Returns:
            Created LedgerEntry
        """
        return await self.create_ledger_entry(
            case_id=case_id,
            entry_type=LedgerEntryType.FEE_CHARGED,
            amount=amount,
            description=description or "Principal charge",
            reference=reference,
            created_by=created_by,
            status=LedgerEntryStatus.CLEARED
        )
    
    async def record_fee(
        self,
        case_id: str,
        amount: Decimal,
        fee_type: str,
        description: Optional[str] = None,
        fee_rule_id: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> LedgerEntry:
        """
        Record a fee (FEE_EARNED).
        
        Args:
            case_id: Case ID
            amount: Fee amount
            fee_type: Type of fee (e.g., "enforcement_fee", "compliance_fee")
            description: Description
            fee_rule_id: Fee rule ID that generated this fee
            created_by: User ID
        
        Returns:
            Created LedgerEntry
        """
        metadata = {
            "fee_type": fee_type,
            "fee_rule_id": fee_rule_id
        }
        
        return await self.create_ledger_entry(
            case_id=case_id,
            entry_type=LedgerEntryType.FEE_EARNED,
            amount=amount,
            description=description or f"{fee_type} fee",
            metadata=metadata,
            created_by=created_by,
            status=LedgerEntryStatus.CLEARED
        )
    
    async def record_interest(
        self,
        case_id: str,
        amount: Decimal,
        description: Optional[str] = None,
        interest_rate: Optional[Decimal] = None,
        period_days: Optional[int] = None,
        created_by: Optional[str] = None
    ) -> LedgerEntry:
        """
        Record interest accrued.
        
        Args:
            case_id: Case ID
            amount: Interest amount
            description: Description
            interest_rate: Interest rate (for metadata)
            period_days: Period in days (for metadata)
            created_by: User ID
        
        Returns:
            Created LedgerEntry
        """
        metadata = {}
        if interest_rate:
            metadata["interest_rate"] = float(interest_rate)
        if period_days:
            metadata["period_days"] = period_days
        
        return await self.create_ledger_entry(
            case_id=case_id,
            entry_type=LedgerEntryType.INTEREST_ACCRUED,
            amount=amount,
            description=description or "Interest accrued",
            metadata=metadata,
            created_by=created_by,
            status=LedgerEntryStatus.CLEARED
        )
    
    async def record_cost(
        self,
        case_id: str,
        amount: Decimal,
        description: Optional[str] = None,
        cost_type: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> LedgerEntry:
        """
        Record a disbursement/cost.
        
        Args:
            case_id: Case ID
            amount: Cost amount
            description: Description
            cost_type: Type of cost (e.g., "court_fee", "tracing_fee")
            created_by: User ID
        
        Returns:
            Created LedgerEntry
        """
        metadata = {"cost_type": cost_type} if cost_type else {}
        
        return await self.create_ledger_entry(
            case_id=case_id,
            entry_type=LedgerEntryType.DISBURSEMENT,
            amount=amount,
            description=description or "Disbursement",
            metadata=metadata,
            created_by=created_by,
            status=LedgerEntryStatus.CLEARED
        )
    
    async def _update_case_totals(self, case_id: str):
        """
        Update case financial totals from ledger entries.
        
        NOTE: This updates stored totals for performance, but ledger is source of truth.
        """
        balance = await self.get_case_balance(case_id)
        
        # Update case record
        case_stmt = select(EnforcementCase).where(
            and_(
                EnforcementCase.id == case_id,
                EnforcementCase.tenant_id == self.tenant_id
            )
        )
        case_result = await self.db.execute(case_stmt)
        case = case_result.scalar_one_or_none()
        
        if case:
            # Update stored totals (for performance, but ledger is source of truth)
            case.original_amount = balance["total_debt"]
            case.fees_charged = balance["total_fees"]
            case.payments_received = balance["total_payments"]
            case.current_balance = balance["current_balance"]
            
            await self.db.flush()
    
    async def reverse_ledger_entry(
        self,
        entry_id: str,
        reason: str,
        reversed_by: str
    ) -> LedgerEntry:
        """
        Reverse a ledger entry by creating a reversal entry.
        
        CRITICAL: Original entry is never modified. Reversal creates new entry.
        
        Args:
            entry_id: Ledger entry ID to reverse
            reason: Reason for reversal
            reversed_by: User ID who reversed the entry
        
        Returns:
            Reversal LedgerEntry
        """
        # Get original entry
        stmt = select(LedgerEntry).where(
            and_(
                LedgerEntry.id == entry_id,
                LedgerEntry.tenant_id == self.tenant_id,
                LedgerEntry.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        original_entry = result.scalar_one_or_none()
        
        if not original_entry:
            raise ValueError(f"Ledger entry {entry_id} not found")
        
        if original_entry.status == LedgerEntryStatus.REVERSED:
            raise ValueError(f"Ledger entry {entry_id} is already reversed")
        
        # Create reversal entry (opposite type)
        reversal_type_map = {
            LedgerEntryType.DEBTOR_PAYMENT: LedgerEntryType.REFUND,
            LedgerEntryType.FEE_EARNED: LedgerEntryType.ADJUSTMENT,
            LedgerEntryType.FEE_CHARGED: LedgerEntryType.ADJUSTMENT,
            LedgerEntryType.INTEREST_ACCRUED: LedgerEntryType.ADJUSTMENT,
            LedgerEntryType.DISBURSEMENT: LedgerEntryType.ADJUSTMENT,
            LedgerEntryType.REFUND: LedgerEntryType.DEBTOR_PAYMENT,
            LedgerEntryType.ADJUSTMENT: LedgerEntryType.ADJUSTMENT,  # Can reverse adjustments
        }
        
        reversal_type = reversal_type_map.get(original_entry.entry_type, LedgerEntryType.ADJUSTMENT)
        
        reversal_entry = LedgerEntry(
            tenant_id=self.tenant_id,
            case_id=original_entry.case_id,
            entry_type=reversal_type,
            amount=original_entry.amount,
            description=f"Reversal of: {original_entry.description}",
            reference=f"REV-{original_entry.id}",
            metadata={
                "reversal_of": original_entry.id,
                "reason": reason,
                "original_entry_type": original_entry.entry_type.value
            },
            created_by=reversed_by,
            status=LedgerEntryStatus.CLEARED,
            posted_at=datetime.now(timezone.utc)
        )
        
        # Mark original entry as reversed
        original_entry.status = LedgerEntryStatus.REVERSED
        original_entry.metadata = original_entry.metadata or {}
        original_entry.metadata["reversed_at"] = datetime.now(timezone.utc).isoformat()
        original_entry.metadata["reversed_by"] = reversed_by
        original_entry.metadata["reversal_reason"] = reason
        
        self.db.add(reversal_entry)
        await self.db.flush()
        
        # Update case totals
        await self._update_case_totals(original_entry.case_id)
        
        logger.info(
            f"Reversed ledger entry {entry_id} for case {original_entry.case_id}",
            extra={"entry_id": entry_id, "case_id": original_entry.case_id, "reason": reason}
        )
        
        return reversal_entry

