#!/usr/bin/env python3
"""
EnforceSense models for debt recovery and enforcement

Core Domain Model:
- Debtor: Real-world person OR legal entity that owes money
- Client: Creditor or instructing organisation
- Case: Single enforcement instruction linking ONE Debtor to ONE Client
"""

from sqlalchemy import Column, String, Boolean, Text, JSON, ForeignKey, Integer, Enum, DateTime, Float, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from .base import Base, BaseModel


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


class CaseType(enum.Enum):
    """Case type enumeration"""
    COUNTY_COURT_JUDGMENT = "county_court_judgment"
    HIGH_COURT_WRIT = "high_court_writ"
    MAGISTRATES_COURT = "magistrates_court"
    COUNCIL_TAX = "council_tax"
    BUSINESS_RATES = "business_rates"
    PARKING_FINE = "parking_fine"
    OTHER = "other"


class TransactionType(enum.Enum):
    """Case transaction type"""
    PAYMENT = "payment"
    FEE = "fee"
    REFUND = "refund"
    ADJUSTMENT = "adjustment"
    WRITE_OFF = "write_off"


ENUM_KWARGS = {
    "values_callable": lambda enum_cls: [member.value for member in enum_cls]
}


class Debtor(BaseModel):
    """
    Debtor model - represents a real-world person OR legal entity
    
    CRITICAL: Debtor-level data is shared across ALL cases.
    Debtor-level data MUST NOT include balances, fees, or enforcement stages.
    """
    __tablename__ = "debtors"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Entity type (required)
    entity_type = Column(Enum(DebtorEntityType, **ENUM_KWARGS), nullable=False)
    
    # Legal name (required for both PERSON and COMPANY)
    legal_name = Column(String(255), nullable=False, index=True)
    
    # Person-specific fields
    first_name = Column(String(100), nullable=True)
    last_name = Column(String(100), nullable=True)
    date_of_birth = Column(DateTime(timezone=True), nullable=True)
    national_identifier = Column(String(50), nullable=True)  # NI number, passport, etc.
    
    # Company-specific fields
    company_registration_number = Column(String(50), nullable=True, index=True)  # Companies House number
    
    # Trading names/aliases (JSON array)
    trading_names = Column(JSON, default=list)
    
    # Contact details
    email = Column(String(255), nullable=True, index=True)
    phone = Column(String(50), nullable=True)
    
    # Address history (JSON array of addresses)
    # Format: [{"address": "...", "postcode": "...", "is_current": true, "from_date": "...", "to_date": "..."}]
    address_history = Column(JSON, default=list)
    
    # Communication preferences
    language_preference = Column(String(5), default="en")  # ISO 639-1 code
    communication_preferences = Column(JSON, default=dict)  # Preferred channels, times, etc.
    
    # Vulnerability indicators (typically PERSON only)
    is_vulnerable = Column(Boolean, default=False, nullable=False)
    vulnerability_notes = Column(Text, nullable=True)
    
    # Risk flags (non-financial risk indicators)
    risk_flags = Column(JSON, default=list)
    
    # External references (UPRN, client refs, etc.)
    external_references = Column(JSON, default=dict)
    
    # AI-generated summaries (derived artifacts, immutable original data)
    ai_summary = Column(Text, nullable=True)
    
    # Relationships
    cases = relationship("EnforcementCase", back_populates="debtor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Debtor {self.legal_name} ({self.entity_type.value})>"


class EnforcementClient(BaseModel):
    """
    Client model - represents the instructing organisation (creditor)
    
    Clients MAY have many Cases and many Debtors.
    Clients MUST NOT own debtor identity.
    """
    __tablename__ = "enforcement_clients"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Client information
    name = Column(String(255), nullable=False, index=True)
    company_name = Column(String(255), nullable=True)
    company_registration_number = Column(String(50), nullable=True)
    
    # Contact details
    email = Column(String(255), nullable=True)
    phone = Column(String(50), nullable=True)
    address = Column(Text, nullable=True)
    postcode = Column(String(20), nullable=True)
    
    # Client-specific settings
    reference_prefix = Column(String(20), nullable=True)  # For case reference generation
    default_case_type = Column(Enum(CaseType, **ENUM_KWARGS), nullable=True)
    settings = Column(JSON, default=dict)  # Client-specific configuration
    
    # Relationships
    cases = relationship("EnforcementCase", back_populates="client", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EnforcementClient {self.name}>"


class EnforcementCase(BaseModel):
    """
    Case model - represents ONE enforcement instruction
    
    CRITICAL: Each Case belongs to EXACTLY ONE Debtor and EXACTLY ONE Client.
    All financial, legal, and enforcement activity belongs to the Case, NOT the Debtor.
    Cases are legally and financially independent even when the Debtor is shared.
    """
    __tablename__ = "enforcement_cases"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign keys (required)
    debtor_id = Column(String(36), ForeignKey("debtors.id"), nullable=False, index=True)
    client_id = Column(String(36), ForeignKey("enforcement_clients.id"), nullable=False, index=True)
    
    # Case reference (unique within tenant)
    case_reference = Column(String(100), nullable=False, unique=True, index=True)
    client_reference = Column(String(100), nullable=True, index=True)  # Client's own reference
    
    # Case type and status
    case_type = Column(Enum(CaseType, **ENUM_KWARGS), nullable=False)
    status = Column(Enum(CaseStatus, **ENUM_KWARGS), default=CaseStatus.DRAFT, nullable=False)
    
    # Legal basis
    legal_basis = Column(Text, nullable=True)
    court_reference = Column(String(100), nullable=True)
    judgment_date = Column(DateTime(timezone=True), nullable=True)
    
    # Financial data (all at Case level, NOT Debtor level)
    original_amount = Column(Numeric(12, 2), nullable=False, default=0)
    fees_charged = Column(Numeric(12, 2), nullable=False, default=0)
    payments_received = Column(Numeric(12, 2), nullable=False, default=0)
    current_balance = Column(Numeric(12, 2), nullable=False, default=0)
    
    # Enforcement stage/status details
    enforcement_stage = Column(String(50), nullable=True)  # e.g., "notice_served", "visit_scheduled"
    assigned_agent = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Case-specific notes and communications
    notes = Column(Text, nullable=True)
    communications = Column(JSON, default=list)  # Array of communication records
    
    # Visits, actions, notices
    visits = Column(JSON, default=list)  # Array of visit records
    actions = Column(JSON, default=list)  # Array of action records
    notices = Column(JSON, default=list)  # Array of notice records
    
    # Case-level risk flags
    risk_flags = Column(JSON, default=list)
    
    # AI-generated summaries (derived artifacts)
    ai_summary = Column(Text, nullable=True)
    
    # Dates
    opened_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    closed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    debtor = relationship("Debtor", back_populates="cases")
    client = relationship("EnforcementClient", back_populates="cases")
    assigned_user = relationship("User", foreign_keys=[assigned_agent])
    transactions = relationship("CaseTransaction", back_populates="case", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EnforcementCase {self.case_reference} - {self.status.value}>"


class CaseTransaction(BaseModel):
    """
    Case Transaction model - immutable ledger entry for all monetary movement
    
    CRITICAL: All monetary movement is recorded in Case Ledger.
    No monetary totals are stored at Debtor level.
    Financial entities reference caseId, NOT debtorId.
    """
    __tablename__ = "case_transactions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to case (required)
    case_id = Column(String(36), ForeignKey("enforcement_cases.id"), nullable=False, index=True)
    
    # Transaction details
    transaction_type = Column(Enum(TransactionType, **ENUM_KWARGS), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=True)
    
    # Reference to payment (if applicable)
    payment_id = Column(String(36), nullable=True)  # Reference to payment record if this is a payment allocation
    
    # Transaction metadata
    reference = Column(String(100), nullable=True)
    transaction_metadata = Column(JSON, default=dict)  # Renamed from 'metadata' (reserved in SQLAlchemy)
    
    # Created by
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    case = relationship("EnforcementCase", back_populates="transactions")
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<CaseTransaction {self.transaction_type.value} {self.amount} for Case {self.case_id}>"


class CaseNote(BaseModel):
    """
    Case Note model - stores notes with AI improvement
    
    CRITICAL: Original note is never overwritten.
    AI generates cleaned/improved version asynchronously.
    """
    __tablename__ = "case_notes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    
    # Foreign key to case (required)
    case_id = Column(String(36), ForeignKey("enforcement_cases.id"), nullable=False, index=True)
    
    # Note content
    note = Column(Text, nullable=False)  # Current note (may be AI-improved)
    original_note = Column(Text, nullable=True)  # Original note (never changed)
    
    # AI improvements
    ai_improved_note = Column(Text, nullable=True)  # AI-cleaned version
    ai_summary = Column(Text, nullable=True)  # AI-generated summary
    risk_flags = Column(JSON, default=list)  # Risk flags detected by AI
    ai_processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    
    # Created by
    created_by = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Relationships
    case = relationship("EnforcementCase", foreign_keys=[case_id])
    created_by_user = relationship("User", foreign_keys=[created_by])
    
    def __repr__(self):
        return f"<CaseNote {self.id[:8]}... for Case {self.case_id}>"


# Create indexes for common queries
Index("idx_debtors_entity_type", Debtor.entity_type)
Index("idx_debtors_email", Debtor.email)
Index("idx_cases_status", EnforcementCase.status)
Index("idx_cases_debtor_client", EnforcementCase.debtor_id, EnforcementCase.client_id)
Index("idx_cases_case_reference", EnforcementCase.case_reference)
Index("idx_transactions_case_type", CaseTransaction.case_id, CaseTransaction.transaction_type)
Index("idx_case_notes_case_id", CaseNote.case_id)
Index("idx_case_notes_created_by", CaseNote.created_by)

