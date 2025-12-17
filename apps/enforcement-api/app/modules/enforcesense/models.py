"""
EnforceSense Module Models
Minimal data models for debt recovery cases
"""

from sqlalchemy import Column, String, ForeignKey, DateTime, Enum, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.core.database import Base


class CaseStatus(enum.Enum):
    """Case status enumeration"""
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    CLOSED = "closed"
    SETTLED = "settled"


class DebtorType(enum.Enum):
    """Debtor type enumeration"""
    PERSON = "person"
    COMPANY = "company"


class Case(Base):
    """Enforcement case model"""
    __tablename__ = "enforcement_cases"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    client_account_id = Column(String(36), nullable=True)  # Reference to Platform API Account
    debtor_party_id = Column(String(36), ForeignKey("debtor_parties.id"), nullable=True)
    status = Column(Enum(CaseStatus), default=CaseStatus.OPEN, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    debtor_party = relationship("DebtorParty", back_populates="cases")


class DebtorParty(Base):
    """Debtor party model (person or company)"""
    __tablename__ = "debtor_parties"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    type = Column(Enum(DebtorType), nullable=False)
    name = Column(String(255), nullable=False)
    address_ref = Column(Text, nullable=True)  # Reference to address (could be Platform API address ID)
    preferred_language = Column(String(10), default="en", nullable=False)  # ISO 639-1 code (en, ro, cs, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    cases = relationship("Case", back_populates="debtor_party")

