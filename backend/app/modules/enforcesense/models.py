"""
EnforceSense Module Models

Minimal models for debt recovery cases.
Links clients (from CRM) to debtors and tracks cases.
"""

from sqlalchemy import Column, String, Numeric, ForeignKey, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.models.base import Base


class CaseStatus(str, enum.Enum):
    """Case status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class DebtorType(str, enum.Enum):
    """Debtor type enumeration"""
    PERSON = "person"
    COMPANY = "company"


class Debtor(Base):
    """
    Debtor model - person or company that owes debt
    
    Links to cases but not directly to CRM (cases provide the link to clients).
    """
    __tablename__ = "enforcesense_debtors"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(DebtorType), nullable=False)
    
    # Contact information (stored as JSONB in future, simple strings for now)
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(String(500), nullable=True)
    
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    cases = relationship("Case", back_populates="debtor", cascade="all, delete-orphan")


class Case(Base):
    """
    Case model - links client (from CRM) to debtor
    
    The client_id references a Customer from the CRM module.
    """
    __tablename__ = "enforcesense_cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Link to CRM Customer (client)
    client_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    
    # Link to Debtor
    debtor_id = Column(UUID(as_uuid=True), ForeignKey("enforcesense_debtors.id"), nullable=False, index=True)
    
    case_number = Column(String(50), nullable=False, unique=True)
    status = Column(SQLEnum(CaseStatus), nullable=False, default=CaseStatus.OPEN)
    
    amount = Column(Numeric(10, 2), nullable=False)
    currency = Column(String(3), nullable=False, default="GBP")
    
    created_at = Column(String, default=lambda: datetime.utcnow().isoformat())
    updated_at = Column(String, default=lambda: datetime.utcnow().isoformat(), onupdate=lambda: datetime.utcnow().isoformat())
    
    # Relationships
    debtor = relationship("Debtor", back_populates="cases")

