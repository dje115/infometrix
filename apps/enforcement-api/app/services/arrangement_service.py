#!/usr/bin/env python3
"""
Arrangement Service - Payment Plans

Handles payment arrangements (payment plans/schedules) for cases.
Arrangements allow debtors to pay in installments.

CRITICAL: Arrangements reference caseId, not debtorId.
"""

import logging
import enum
from typing import List, Optional, Dict, Any
from datetime import datetime, timezone, date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func

from app.modules.enforcesense.models import (
    EnforcementCase,
    Arrangement,
    ArrangementStatus
)

logger = logging.getLogger(__name__)


class ArrangementService:
    """
    Service for managing payment arrangements (payment plans).
    
    Handles:
    - Creating payment arrangements
    - Schedule management
    - Status tracking (ACTIVE, BROKEN, COMPLETED, CANCELLED)
    - Validation
    """
    
    def __init__(self, db: AsyncSession, tenant_id: str):
        self.db = db
        self.tenant_id = tenant_id
    
    async def create_arrangement(
        self,
        case_id: str,
        total_amount: Decimal,
        schedule: List[Dict[str, Any]],
        start_date: date,
        description: Optional[str] = None,
        created_by: Optional[str] = None
    ) -> Arrangement:
        """
        Create a payment arrangement (payment plan).
        
        Args:
            case_id: Case ID
            total_amount: Total amount to be paid
            schedule: Payment schedule:
                [
                    {
                        "due_date": "2025-01-15",
                        "amount": 100.00,
                        "order": 1
                    },
                    ...
                ]
            start_date: Start date of arrangement
            description: Description
            created_by: User ID
        
        Returns:
            Created Arrangement
        
        Raises:
            ValueError: If schedule validation fails
        """
        # Validate case exists
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
        
        # Validate schedule
        await self._validate_schedule(schedule, total_amount)
        
        # Check for existing active arrangement
        existing_stmt = select(Arrangement).where(
            and_(
                Arrangement.case_id == case_id,
                Arrangement.tenant_id == self.tenant_id,
                Arrangement.status == ArrangementStatus.ACTIVE,
                Arrangement.is_deleted == False
            )
        )
        existing_result = await self.db.execute(existing_stmt)
        existing = existing_result.scalar_one_or_none()
        
        if existing:
            raise ValueError(f"Case {case_id} already has an active arrangement")
        
        # Create arrangement
        arrangement = Arrangement(
            tenant_id=self.tenant_id,
            case_id=case_id,
            total_amount=total_amount,
            schedule=schedule,
            start_date=start_date,
            status=ArrangementStatus.ACTIVE,
            description=description,
            created_by=created_by
        )
        
        self.db.add(arrangement)
        await self.db.flush()
        
        logger.info(
            f"Created arrangement for case {case_id}: {total_amount} over {len(schedule)} payments",
            extra={"case_id": case_id, "total_amount": float(total_amount), "payments": len(schedule)}
        )
        
        return arrangement
    
    async def _validate_schedule(
        self,
        schedule: List[Dict[str, Any]],
        total_amount: Decimal
    ):
        """
        Validate payment schedule.
        
        Args:
            schedule: Payment schedule
            total_amount: Expected total amount
        
        Raises:
            ValueError: If validation fails
        """
        if not schedule:
            raise ValueError("Schedule cannot be empty")
        
        # Validate all required fields
        for i, payment in enumerate(schedule):
            if "due_date" not in payment:
                raise ValueError(f"Payment {i+1} missing 'due_date'")
            if "amount" not in payment:
                raise ValueError(f"Payment {i+1} missing 'amount'")
            if "order" not in payment:
                raise ValueError(f"Payment {i+1} missing 'order'")
            
            # Validate amount is positive
            if Decimal(str(payment["amount"])) <= 0:
                raise ValueError(f"Payment {i+1} amount must be positive")
        
        # Validate schedule sums to total
        schedule_total = sum(Decimal(str(p["amount"])) for p in schedule)
        if schedule_total != total_amount:
            raise ValueError(
                f"Schedule total ({schedule_total}) does not match arrangement total ({total_amount})"
            )
        
        # Validate dates are in order
        dates = [datetime.fromisoformat(str(p["due_date"])).date() for p in schedule]
        if dates != sorted(dates):
            raise ValueError("Schedule dates must be in chronological order")
        
        # Validate orders are sequential
        orders = [p["order"] for p in schedule]
        if orders != sorted(orders) or set(orders) != set(range(1, len(schedule) + 1)):
            raise ValueError("Schedule orders must be sequential starting from 1")
    
    async def update_arrangement_schedule(
        self,
        arrangement_id: str,
        schedule: List[Dict[str, Any]],
        updated_by: Optional[str] = None
    ) -> Arrangement:
        """
        Update arrangement schedule.
        
        Args:
            arrangement_id: Arrangement ID
            schedule: New schedule
            updated_by: User ID
        
        Returns:
            Updated Arrangement
        
        Raises:
            ValueError: If validation fails or arrangement is not active
        """
        stmt = select(Arrangement).where(
            and_(
                Arrangement.id == arrangement_id,
                Arrangement.tenant_id == self.tenant_id,
                Arrangement.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        arrangement = result.scalar_one_or_none()
        
        if not arrangement:
            raise ValueError(f"Arrangement {arrangement_id} not found")
        
        if arrangement.status != ArrangementStatus.ACTIVE:
            raise ValueError(f"Cannot update schedule for {arrangement.status.value} arrangement")
        
        # Validate new schedule
        await self._validate_schedule(schedule, arrangement.total_amount)
        
        # Update schedule
        arrangement.schedule = schedule
        arrangement.updated_by = updated_by
        arrangement.updated_at = datetime.now(timezone.utc)
        
        await self.db.flush()
        
        logger.info(
            f"Updated arrangement {arrangement_id} schedule",
            extra={"arrangement_id": arrangement_id, "payments": len(schedule)}
        )
        
        return arrangement
    
    async def update_arrangement_status(
        self,
        arrangement_id: str,
        status: ArrangementStatus,
        reason: Optional[str] = None,
        updated_by: Optional[str] = None
    ) -> Arrangement:
        """
        Update arrangement status.
        
        Args:
            arrangement_id: Arrangement ID
            status: New status
            reason: Reason for status change
            updated_by: User ID
        
        Returns:
            Updated Arrangement
        """
        stmt = select(Arrangement).where(
            and_(
                Arrangement.id == arrangement_id,
                Arrangement.tenant_id == self.tenant_id,
                Arrangement.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        arrangement = result.scalar_one_or_none()
        
        if not arrangement:
            raise ValueError(f"Arrangement {arrangement_id} not found")
        
        old_status = arrangement.status
        arrangement.status = status
        arrangement.updated_by = updated_by
        arrangement.updated_at = datetime.now(timezone.utc)
        
        if reason:
            arrangement.notes = (arrangement.notes or "") + f"\n[{datetime.now(timezone.utc).isoformat()}] Status changed from {old_status.value} to {status.value}: {reason}"
        
        if status == ArrangementStatus.COMPLETED:
            arrangement.completed_date = datetime.now(timezone.utc).date()
        elif status == ArrangementStatus.CANCELLED:
            arrangement.cancelled_date = datetime.now(timezone.utc).date()
        
        await self.db.flush()
        
        logger.info(
            f"Updated arrangement {arrangement_id} status: {old_status.value} -> {status.value}",
            extra={"arrangement_id": arrangement_id, "old_status": old_status.value, "new_status": status.value}
        )
        
        return arrangement
    
    async def get_case_arrangements(
        self,
        case_id: str,
        status: Optional[ArrangementStatus] = None
    ) -> List[Arrangement]:
        """
        Get arrangements for a case.
        
        Args:
            case_id: Case ID
            status: Filter by status (optional)
        
        Returns:
            List of Arrangement objects
        """
        stmt = select(Arrangement).where(
            and_(
                Arrangement.case_id == case_id,
                Arrangement.tenant_id == self.tenant_id,
                Arrangement.is_deleted == False
            )
        )
        
        if status:
            stmt = stmt.where(Arrangement.status == status)
        
        stmt = stmt.order_by(Arrangement.created_at.desc())
        
        result = await self.db.execute(stmt)
        return list(result.scalars().all())
    
    async def get_arrangement(self, arrangement_id: str) -> Optional[Arrangement]:
        """
        Get a single arrangement.
        
        Args:
            arrangement_id: Arrangement ID
        
        Returns:
            Arrangement or None
        """
        stmt = select(Arrangement).where(
            and_(
                Arrangement.id == arrangement_id,
                Arrangement.tenant_id == self.tenant_id,
                Arrangement.is_deleted == False
            )
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

