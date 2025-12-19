#!/usr/bin/env python3
"""
EnforceSense models for Enforcement API

Minimal models to prove the boundary.
These will be expanded in later commits.
"""

from sqlalchemy import Column, String, DateTime, ForeignKey, Enum, Numeric, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.core.database import Base


class DebtorEntityType(enum.Enum):
    """Debtor entity type"""
    PERSON = "PERSON"
    COMPANY = "COMPANY"


class CaseStatus(enum.Enum):
    """Case status enumeration"""
    DRAFT = "draft"
    ACTIVE = "active"
    ON_HOLD = "on_hold"
    SETTLED = "settled"
    CLOSED = "closed"
    CANCELLED = "cancelled"


class DebtorParty(Base):
    """
    Minimal DebtorParty model for Enforcement API
    
    Represents a person or company that owes money.
    """
    __tablename__ = "debtors"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # Entity type
    entity_type = Column(Enum(DebtorEntityType), nullable=False)
    
    # Name
    legal_name = Column(String(255), nullable=False, index=True)
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    
    # Company fields
    company_registration_number = Column(String(50), nullable=True)
    
    # Contact
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    
    # Address reference (can reference Platform API account/contact ID)
    address_ref = Column(String(36), nullable=True)  # Reference to Platform API entity
    
    # Language preference for multilingual support
    preferred_language = Column(String(5), default="en")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    cases = relationship("Case", back_populates="debtor")
    
    def __repr__(self):
        return f"<DebtorParty {self.id} ({self.legal_name})>"


class Case(Base):
    """
    Minimal Case model for Enforcement API
    
    Represents a single enforcement instruction.
    """
    __tablename__ = "enforcement_cases"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), nullable=False, index=True)
    
    # References
    client_account_id = Column(String(36), nullable=True)  # Reference to Platform API account
    debtor_party_id = Column(String(36), ForeignKey("debtors.id"), nullable=False, index=True)
    
    # Case details
    case_reference = Column(String(100), nullable=False, unique=True, index=True)
    status = Column(Enum(CaseStatus), default=CaseStatus.DRAFT, nullable=False)
    
    # Financial
    original_amount = Column(Numeric(10, 2), nullable=False, default=0)
    current_balance = Column(Numeric(10, 2), nullable=False, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    debtor = relationship("DebtorParty", back_populates="cases")
    
    def __repr__(self):
        return f"<Case {self.id} ({self.case_reference})>"

