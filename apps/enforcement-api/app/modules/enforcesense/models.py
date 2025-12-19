#!/usr/bin/env python3
"""
EnforceSense models for Enforcement API

Core Domain Model:
- Debtor: Real-world person OR legal entity that owes money
- Client: Creditor or instructing organisation
- Case: Single enforcement instruction linking ONE Debtor to ONE Client

CRITICAL FINANCIAL RULES:
- Ledger is single source of truth for all financial movements
- All balances are derived from ledger entries, never stored directly
- See: docs/enforcesense/FINANCIAL_MODEL.md for complete specification
- See: docs/enforcesense/DEVELOPMENT_RULES.md for development rules
"""

from sqlalchemy import Column, String, Boolean, Text, JSON, ForeignKey, Integer, Enum, DateTime, Numeric, Index
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import enum
import uuid
from app.core.database import Base


class DebtorEntityType(enum.Enum):
    """Debtor entity type"""
    PERSON = "PERSON"
    COMPANY = "COMPANY"


class PartyType(enum.Enum):
    """Party type - replaces DebtorEntityType"""
    INDIVIDUAL = "INDIVIDUAL"
    ORGANISATION = "ORGANISATION"


class PartyRoleType(enum.Enum):
    """Party role in a case"""
    DEBTOR = "DEBTOR"
    JOINT_DEBTOR = "JOINT_DEBTOR"
    GUARANTOR = "GUARANTOR"
    DIRECTOR = "DIRECTOR"
    THIRD_PARTY = "THIRD_PARTY"
    VULNERABLE_PERSON = "VULNERABLE_PERSON"  # Flag/assessment, not a role if preferred


class DebtAccountStatus(enum.Enum):
    """Debt account status"""
    ACTIVE = "ACTIVE"
    SETTLED = "SETTLED"
    DISPUTED = "DISPUTED"
    STAYED = "STAYED"
    WRITTEN_OFF = "WRITTEN_OFF"


class DebtAccountType(enum.Enum):
    """Debt account type"""
    INVOICE = "INVOICE"
    JUDGMENT = "JUDGMENT"
    CONTRACT = "CONTRACT"
    COUNCIL_TAX = "COUNCIL_TAX"
    BUSINESS_RATES = "BUSINESS_RATES"
    PARKING_FINE = "PARKING_FINE"
    OTHER = "OTHER"


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


class Debtor(Base):
    """
    Debtor model - represents a real-world person OR legal entity
    
    CRITICAL: Debtor-level data is shared across ALL cases.
    Debtor-level data MUST NOT include balances, fees, or enforcement stages.
    """
    __tablename__ = "debtors"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Entity type (required)
    entity_type = Column(Enum(DebtorEntityType), nullable=False)
    
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
    address_history = Column(JSON, default=list)
    
    # Communication preferences
    language_preference = Column(String(5), default="en")  # ISO 639-1 code
    communication_preferences = Column(JSON, default=dict)
    
    # Vulnerability indicators (typically PERSON only)
    is_vulnerable = Column(Boolean, default=False, nullable=False)
    vulnerability_notes = Column(Text, nullable=True)
    
    # Risk flags (non-financial risk indicators)
    risk_flags = Column(JSON, default=list)
    
    # External references (UPRN, client refs, etc.)
    external_references = Column(JSON, default=dict)
    
    # AI-generated summaries (derived artifacts, immutable original data)
    ai_summary = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships (DEPRECATED - use Party model instead)
    cases = relationship("EnforcementCase", back_populates="debtor", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Debtor {self.legal_name} ({self.entity_type.value})>"


class EnforcementClient(Base):
    """
    Client model - represents the instructing organisation (creditor)
    
    Clients MAY have many Cases and many Debtors.
    Clients MUST NOT own debtor identity.
    """
    __tablename__ = "enforcement_clients"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
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
    default_case_type = Column(Enum(CaseType), nullable=True)
    settings = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    cases = relationship("EnforcementCase", back_populates="client", cascade="all, delete-orphan")
    
    # TODO: Add customer_id FK to link to CRM Customer/Account
    # customer_id = Column(String(36), ForeignKey("customers.id"), nullable=True, index=True)
    
    def __repr__(self):
        return f"<EnforcementClient {self.name}>"


class EnforcementCase(Base):
    """
    Case model - represents ONE enforcement instruction
    
    CRITICAL: Each Case belongs to EXACTLY ONE Debtor and EXACTLY ONE Client.
    All financial, legal, and enforcement activity belongs to the Case, NOT the Debtor.
    Cases are legally and financially independent even when the Debtor is shared.
    """
    __tablename__ = "enforcement_cases"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign keys (required)
    debtor_id = Column(String(36), ForeignKey("debtors.id"), nullable=False, index=True)
    client_id = Column(String(36), ForeignKey("enforcement_clients.id"), nullable=False, index=True)
    
    # Case reference (unique within tenant)
    case_reference = Column(String(100), nullable=False, unique=True, index=True)
    client_reference = Column(String(100), nullable=True, index=True)  # Client's own reference
    
    # Case type and status
    case_type = Column(Enum(CaseType), nullable=False)
    status = Column(Enum(CaseStatus), default=CaseStatus.DRAFT, nullable=False)
    
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
    enforcement_stage = Column(String(50), nullable=True)
    assigned_agent = Column(String(36), nullable=True)  # Reference to Platform API user ID
    
    # Case-specific notes and communications
    notes = Column(Text, nullable=True)
    communications = Column(JSON, default=list)
    
    # Visits, actions, notices
    visits = Column(JSON, default=list)
    actions = Column(JSON, default=list)
    notices = Column(JSON, default=list)
    
    # Case-level risk flags
    risk_flags = Column(JSON, default=list)
    
    # AI-generated summaries (derived artifacts)
    ai_summary = Column(Text, nullable=True)
    
    # Dates
    opened_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    closed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships (legacy - will be updated in Phase 2)
    debtor = relationship("Debtor", back_populates="cases")  # DEPRECATED - use party_roles instead
    client = relationship("EnforcementClient", back_populates="cases")
    transactions = relationship("CaseTransaction", back_populates="case", cascade="all, delete-orphan")
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")
    
    # New relationships (Phase 1)
    case_debts = relationship("CaseDebts", back_populates="case", cascade="all, delete-orphan")
    party_roles = relationship("PartyRole", back_populates="case", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<EnforcementCase {self.case_reference} - {self.status.value}>"


class CaseTransaction(Base):
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
    transaction_type = Column(Enum(TransactionType), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    description = Column(Text, nullable=True)
    
    # Reference to payment (if applicable)
    payment_id = Column(String(36), nullable=True)
    
    # Transaction metadata
    reference = Column(String(100), nullable=True)
    transaction_metadata = Column(JSON, default=dict)
    
    # Timestamps
    transaction_date = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    case = relationship("EnforcementCase", back_populates="transactions")
    
    def __repr__(self):
        return f"<CaseTransaction {self.transaction_type.value} - £{self.amount}>"


class CaseNote(Base):
    """
    Case Note model - agent notes for a case
    """
    __tablename__ = "case_notes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    case_id = Column(String(36), ForeignKey("enforcement_cases.id"), nullable=False, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Note content
    note = Column(Text, nullable=False)  # Current note (may be AI-improved)
    original_note = Column(Text, nullable=True)  # Original note (never changed)
    
    # AI improvements
    ai_improved_note = Column(Text, nullable=True)  # AI-cleaned version
    ai_summary = Column(Text, nullable=True)  # AI-generated summary
    risk_flags = Column(JSON, default=list)  # Risk flags detected by AI
    ai_processing_status = Column(String(20), default='pending')  # pending, processing, completed, failed
    
    # Created by
    created_by = Column(String(36), nullable=True)  # Reference to Platform API user ID
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    case = relationship("EnforcementCase")
    
    def __repr__(self):
        return f"<CaseNote {self.id[:8]}... for case {self.case_id[:8]}...>"
