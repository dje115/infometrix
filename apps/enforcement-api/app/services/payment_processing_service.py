#!/usr/bin/env python3
"""
Payment Processing Service

Handles payment recording, allocation, and refunds.
Follows the financial model specification.

CRITICAL: Payment allocation determines how payments are split across:
- Principal debt
- Interest
- Enforcement fees
- Client fees
"""

import logging
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func

from app.modules.enforcesense.models import (
    EnforcementCase,
    LedgerEntry,
    LedgerEntryType,
    LedgerEntryStatus,
    PaymentAllocation,
    PaymentAllocationMethod
)
from app.services.case_transaction_service import CaseTransactionService

logger = logging.getLogger(__name__)


class PaymentProcessingService:
    """
    Service for processing payments and allocations.
    
    Handles:
    - Recording debtor payments
    - Allocating payments across debts/fees
    - Processing refunds
    - Payment history
    """
    
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
        self.transaction_service = CaseTransactionService(db, tenant_id)
    
    async def record_payment(
        self,
        case_id: str,
        amount: Decimal,
        payment_method: str,
        payment_reference: Optional[str] = None,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        created_by: Optional[str] = None
    ) -> LedgerEntry:
        """
        Record a payment from debtor.
        
        Args:
            case_id: Case ID
            amount: Payment amount
            payment_method: Payment method (e.g., "card", "bank_transfer", "cash", "cheque")
            payment_reference: External payment reference
            description: Description
            metadata: Additional metadata
            created_by: User ID
        
        Returns:
            Created LedgerEntry (type=DEBTOR_PAYMENT)
        """
        payment_metadata = {
            "payment_method": payment_method,
            "payment_reference": payment_reference,
            **(metadata or {})
        }
        
        ledger_entry = await self.transaction_service.create_ledger_entry(
            case_id=case_id,
            entry_type=LedgerEntryType.DEBTOR_PAYMENT,
            amount=amount,
            description=description or f"Payment received via {payment_method}",
            reference=payment_reference,
            metadata=payment_metadata,
            created_by=created_by,
            status=LedgerEntryStatus.PENDING  # Will be cleared after allocation
        )
        
        logger.info(
            f"Recorded payment: {amount} for case {case_id}",
            extra={"case_id": case_id, "amount": float(amount), "payment_method": payment_method}
        )
        
        return ledger_entry
    
    async def allocate_payment(
        self,
        payment_entry_id: str,
        allocation_lines: List[Dict[str, Any]],
        allocation_method: PaymentAllocationMethod = PaymentAllocationMethod.MANUAL,
        allocated_by: Optional[str] = None
    ) -> PaymentAllocation:
        """
        Allocate a payment across debts and fees.
        
        Args:
            payment_entry_id: Ledger entry ID (type=DEBTOR_PAYMENT)
            allocation_lines: List of allocation lines:
                [
                    {
                        "target_type": "PRINCIPAL" | "INTEREST" | "ENFORCEMENT_FEE" | "CLIENT_FEE",
                        "target_id": "debt-id or fee-rule-id",
                        "amount": 100.00,
                        "order": 1
                    },
                    ...
                ]
            allocation_method: How allocation was determined
            allocated_by: User ID
        
        Returns:
            PaymentAllocation object
        
        Raises:
            ValueError: If allocation doesn't sum to payment amount
        """
        # Get payment entry
        stmt = select(LedgerEntry).where(
            and_(
                LedgerEntry.id == payment_entry_id,
                LedgerEntry.tenant_id == self.tenant_id,
                LedgerEntry.entry_type == LedgerEntryType.DEBTOR_PAYMENT,
                LedgerEntry.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        payment_entry = result.scalar_one_or_none()
        
        if not payment_entry:
            raise ValueError(f"Payment entry {payment_entry_id} not found")
        
        if payment_entry.status == LedgerEntryStatus.REVERSED:
            raise ValueError(f"Payment entry {payment_entry_id} is reversed")
        
        # Validate allocation sums to payment amount
        total_allocated = sum(Decimal(str(line["amount"])) for line in allocation_lines)
        if total_allocated != payment_entry.amount:
            raise ValueError(
                f"Allocation total ({total_allocated}) does not match payment amount ({payment_entry.amount})"
            )
        
        # Check if allocation already exists
        existing_stmt = select(PaymentAllocation).where(
            and_(
                PaymentAllocation.payment_entry_id == payment_entry_id,
                PaymentAllocation.tenant_id == self.tenant_id,
                PaymentAllocation.is_deleted == False
            )
        )
        existing_result = await self.db.execute(existing_stmt)
        existing_allocation = existing_result.scalar_one_or_none()
        
        if existing_allocation:
            raise ValueError(f"Payment {payment_entry_id} is already allocated")
        
        # Create allocation
        allocation = PaymentAllocation(
            tenant_id=self.tenant_id,
            payment_entry_id=payment_entry_id,
            case_id=payment_entry.case_id,
            allocation_lines=allocation_lines,
            total_allocated=total_allocated,
            allocation_method=allocation_method,
            allocated_by=allocated_by,
            allocated_at=datetime.now(timezone.utc)
        )
        
        self.db.add(allocation)
        
        # Clear payment entry (mark as CLEARED)
        payment_entry.status = LedgerEntryStatus.CLEARED
        payment_entry.posted_at = datetime.now(timezone.utc)
        
        # Process fee entries based on allocation
        await self._process_fee_entries_from_allocation(allocation, payment_entry)
        
        await self.db.flush()
        
        # Update case totals
        await self.transaction_service._update_case_totals(payment_entry.case_id)
        
        logger.info(
            f"Allocated payment {payment_entry_id}: {total_allocated} across {len(allocation_lines)} lines",
            extra={"payment_entry_id": payment_entry_id, "case_id": payment_entry.case_id}
        )
        
        return allocation
    
    async def _process_fee_entries_from_allocation(
        self,
        allocation: PaymentAllocation,
        payment_entry: LedgerEntry
    ):
        """
        Process fee entries based on allocation lines.
        
        When allocation includes fees, create FEE_EARNED entries.
        """
        for line in allocation.allocation_lines:
            target_type = line.get("target_type")
            
            if target_type in ["ENFORCEMENT_FEE", "CLIENT_FEE"]:
                # Create fee entry
                fee_type = "enforcement_fee" if target_type == "ENFORCEMENT_FEE" else "client_fee"
                
                await self.transaction_service.create_ledger_entry(
                    case_id=payment_entry.case_id,
                    entry_type=LedgerEntryType.FEE_EARNED,
                    amount=Decimal(str(line["amount"])),
                    description=f"{fee_type} from payment allocation",
                    metadata={
                        "fee_type": fee_type,
                        "fee_rule_id": line.get("target_id"),
                        "payment_entry_id": payment_entry.id,
                        "allocation_id": allocation.id
                    },
                    created_by=allocation.allocated_by,
                    status=LedgerEntryStatus.CLEARED
                )
    
    async def get_payment_allocation(
        self,
        payment_entry_id: str
    ) -> Optional[PaymentAllocation]:
        """
        Get allocation for a payment entry.
        
        Args:
            payment_entry_id: Payment ledger entry ID
        
        Returns:
            PaymentAllocation or None if not allocated
        """
        stmt = select(PaymentAllocation).where(
            and_(
                PaymentAllocation.payment_entry_id == payment_entry_id,
                PaymentAllocation.tenant_id == self.tenant_id,
                PaymentAllocation.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def get_case_payments(
        self,
        case_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[LedgerEntry]:
        """
        Get all payments for a case.
        
        Args:
            case_id: Case ID
            limit: Maximum number of payments
            offset: Offset for pagination
        
        Returns:
            List of LedgerEntry objects (type=DEBTOR_PAYMENT)
        """
        return await self.transaction_service.get_case_ledger(
            case_id=case_id,
            entry_types=[LedgerEntryType.DEBTOR_PAYMENT],
            limit=limit,
            offset=offset
        )
    
    async def process_refund(
        self,
        case_id: str,
        amount: Decimal,
        original_payment_id: Optional[str] = None,
        reason: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> LedgerEntry:
        """
        Process a refund to debtor.
        
        Args:
            case_id: Case ID
            amount: Refund amount
            original_payment_id: Original payment entry ID (if reversing specific payment)
            reason: Reason for refund
            created_by: User ID
        
        Returns:
            Created LedgerEntry (type=REFUND)
        """
        metadata = {
            "original_payment_id": original_payment_id,
            "reason": reason
        }
        
        refund_entry = await self.transaction_service.create_ledger_entry(
            case_id=case_id,
            entry_type=LedgerEntryType.REFUND,
            amount=amount,
            description=reason or "Refund to debtor",
            metadata=metadata,
            created_by=created_by,
            status=LedgerEntryStatus.CLEARED
        )
        
        logger.info(
            f"Processed refund: {amount} for case {case_id}",
            extra={"case_id": case_id, "amount": float(amount), "reason": reason}
        )
        
        return refund_entry

