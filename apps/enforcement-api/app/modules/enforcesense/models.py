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


class LedgerEntryType(enum.Enum):
    """Ledger entry type - single source of truth for all financial movements"""
    DEBTOR_PAYMENT = "DEBTOR_PAYMENT"
    CLIENT_PAYOUT = "CLIENT_PAYOUT"
    FEE_EARNED = "FEE_EARNED"
    DISBURSEMENT = "DISBURSEMENT"
    REFUND = "REFUND"
    ADJUSTMENT = "ADJUSTMENT"
    INTEREST_ACCRUED = "INTEREST_ACCRUED"
    FEE_CHARGED = "FEE_CHARGED"


class LedgerEntryStatus(enum.Enum):
    """Ledger entry status"""
    PENDING = "PENDING"
    CLEARED = "CLEARED"
    REVERSED = "REVERSED"


class PaymentAllocationMethod(enum.Enum):
    """Payment allocation method"""
    AUTOMATIC = "AUTOMATIC"
    MANUAL = "MANUAL"
    RULE_BASED = "RULE_BASED"


class ArrangementStatus(enum.Enum):
    """Arrangement status"""
    ACTIVE = "ACTIVE"
    BROKEN = "BROKEN"
    COMPLETED = "COMPLETED"
    CANCELLED = "CANCELLED"


class FeeScheduleScope(enum.Enum):
    """Fee schedule scope"""
    TENANT_DEFAULT = "TENANT_DEFAULT"
    CLIENT_SPECIFIC = "CLIENT_SPECIFIC"
    CASE_OVERRIDE = "CASE_OVERRIDE"


class FeeType(enum.Enum):
    """Fee calculation type"""
    PERCENTAGE = "PERCENTAGE"
    FIXED = "FIXED"
    TIERED = "TIERED"
    SUCCESS_FEE_ONLY = "SUCCESS_FEE_ONLY"


class FeeCalculationBase(enum.Enum):
    """Fee calculation base"""
    PRINCIPAL = "PRINCIPAL"
    TOTAL_DEBT = "TOTAL_DEBT"
    RECOVERED_AMOUNT = "RECOVERED_AMOUNT"


class FeeWhoPays(enum.Enum):
    """Who pays the fee"""
    CLIENT = "CLIENT"
    DEBTOR = "DEBTOR"


class FeeTriggerEvent(enum.Enum):
    """Fee trigger event"""
    ON_RECOVERY = "ON_RECOVERY"
    ON_CASE_STAGE = "ON_CASE_STAGE"
    ON_CLOSURE = "ON_CLOSURE"
    ON_INSTRUCTION = "ON_INSTRUCTION"


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
    
    # CRM Integration - Link to main CRM Customer
    # CRITICAL: Clients are managed in main CRM. This links EnforcementClient to Customer.
    # EnforcementClient contains enforcement-specific settings only.
    # Client data (name, contacts, sales) is managed in main CRM.
    customer_id = Column(String(36), ForeignKey("customers.id", ondelete="SET NULL"), nullable=True, index=True)
    
    # Relationships
    cases = relationship("EnforcementCase", back_populates="client", cascade="all, delete-orphan")
    
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
    
    # Financial relationships
    ledger_entries = relationship("LedgerEntry", back_populates="case", cascade="all, delete-orphan")
    payment_allocations = relationship("PaymentAllocation", back_populates="case", cascade="all, delete-orphan")
    fee_schedules = relationship("FeeSchedule", back_populates="case", cascade="all, delete-orphan")
    arrangements = relationship("Arrangement", back_populates="case", cascade="all, delete-orphan")
    
    # Support & compliance relationships (Phase 2)
    support_impacts = relationship("CaseSupportImpact", back_populates="case", cascade="all, delete-orphan")
    compliance_notes = relationship("ComplianceNote", back_populates="case", cascade="all, delete-orphan")
    fee_challenges = relationship("FeeChallenge", back_populates="case", cascade="all, delete-orphan")
    
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


class LedgerEntry(Base):
    """
    Ledger Entry model - immutable ledger entry for all monetary movement
    
    CRITICAL: Ledger is single source of truth for all financial movements.
    All balances are derived from ledger entries, never stored directly.
    
    See: docs/enforcesense/FINANCIAL_MODEL.md
    """
    __tablename__ = "ledger_entries"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign keys (nullable for tenant-level entries)
    case_id = Column(String(36), ForeignKey("enforcement_cases.id", ondelete="CASCADE"), nullable=True, index=True)
    debt_id = Column(String(36), nullable=True)  # FK to debt_accounts (when debt_accounts table exists)
    fee_rule_id = Column(String(36), nullable=True)  # FK to fee_rules (when fee_rules table exists)
    
    # Entry type (required)
    entry_type = Column(Enum(LedgerEntryType), nullable=False)
    
    # Amount (always positive, direction determined by entry_type)
    amount = Column(Numeric(12, 2), nullable=False)
    currency = Column(String(3), default="GBP", nullable=False)
    
    # Description and reference
    description = Column(Text, nullable=True)
    reference = Column(String(100), nullable=True)
    
    # Status
    status = Column(Enum(LedgerEntryStatus), default=LedgerEntryStatus.PENDING, nullable=False)
    posted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Reversal tracking
    reversed_at = Column(DateTime(timezone=True), nullable=True)
    reversed_by = Column(String(36), nullable=True)  # FK to User
    reversal_reason = Column(Text, nullable=True)
    
    # Metadata (JSON)
    # Note: Using 'entry_metadata' instead of 'metadata' to avoid SQLAlchemy reserved word conflict
    entry_metadata = Column(JSON, default=dict)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by = Column(String(36), nullable=True)  # FK to User
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    case = relationship("EnforcementCase", back_populates="ledger_entries")
    
    def __repr__(self):
        return f"<LedgerEntry {self.entry_type.value} {self.amount} for Case {self.case_id}>"


class PaymentAllocation(Base):
    """
    Payment Allocation model - tracks how payments are allocated
    
    Links a payment (LedgerEntry type=DEBTOR_PAYMENT) to allocation lines
    that split the payment across principal, interest, fees, etc.
    
    See: docs/enforcesense/FINANCIAL_MODEL.md
    """
    __tablename__ = "payment_allocations"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign key to payment ledger entry (unique - one allocation per payment)
    payment_entry_id = Column(String(36), ForeignKey("ledger_entries.id"), nullable=False, unique=True, index=True)
    
    # Case reference
    case_id = Column(String(36), ForeignKey("enforcement_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Allocation lines (JSON array)
    # Format: [{"target_type": "PRINCIPAL", "target_id": "...", "amount": 100.00, "order": 1}, ...]
    allocation_lines = Column(JSON, nullable=False)
    
    # Total allocated (must equal payment amount)
    total_allocated = Column(Numeric(12, 2), nullable=False)
    
    # Allocation method
    allocation_method = Column(Enum(PaymentAllocationMethod), nullable=False)
    
    # Timestamps
    allocated_at = Column(DateTime(timezone=True), server_default=func.now())
    allocated_by = Column(String(36), nullable=True)  # FK to User
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    payment_entry = relationship("LedgerEntry", foreign_keys=[payment_entry_id])
    case = relationship("EnforcementCase", back_populates="payment_allocations")
    
    def __repr__(self):
        return f"<PaymentAllocation {self.id[:8]}... for payment {self.payment_entry_id[:8]}...>"


class Arrangement(Base):
    """
    Arrangement model - payment plans for cases
    
    Allows debtors to pay in installments over time.
    Arrangements reference caseId, not debtorId.
    """
    __tablename__ = "arrangements"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign key to case (required)
    case_id = Column(String(36), ForeignKey("enforcement_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Arrangement details
    total_amount = Column(Numeric(12, 2), nullable=False)
    schedule = Column(JSON, nullable=False)  # Payment schedule: [{"due_date": "...", "amount": 100.00, "order": 1}, ...]
    start_date = Column(DateTime(timezone=True), nullable=False)
    
    # Status
    status = Column(Enum(ArrangementStatus), default=ArrangementStatus.ACTIVE, nullable=False)
    
    # Dates
    completed_date = Column(DateTime(timezone=True), nullable=True)
    cancelled_date = Column(DateTime(timezone=True), nullable=True)
    
    # Notes
    description = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by = Column(String(36), nullable=True)  # FK to User
    updated_by = Column(String(36), nullable=True)  # FK to User
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    case = relationship("EnforcementCase", back_populates="arrangements")
    
    def __repr__(self):
        return f"<Arrangement {self.id[:8]}... for case {self.case_id[:8]}... - {self.status.value}>"


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


# ============================================================================
# Entity Tree Phase 2: Support & Flags Models
# ============================================================================

class SupportStatus(enum.Enum):
    """Party support status (debt advice/vulnerability)"""
    NONE = "NONE"
    ADVICE_SOUGHT = "ADVICE_SOUGHT"
    ADVISOR_ENGAGED = "ADVISOR_ENGAGED"
    FORMAL_SOLUTION_PENDING = "FORMAL_SOLUTION_PENDING"
    FORMAL_SOLUTION_ACTIVE = "FORMAL_SOLUTION_ACTIVE"


class AdvisorOrg(enum.Enum):
    """Debt advisor organization"""
    STEPCHANGE = "STEPCHANGE"
    CAB = "CAB"
    NATIONAL_DEBTLINE = "NATIONAL_DEBTLINE"
    OTHER = "OTHER"


class EvidenceLevel(enum.Enum):
    """Evidence level for support status"""
    SELF_REPORTED = "SELF_REPORTED"
    ADVISOR_CONFIRMED = "ADVISOR_CONFIRMED"
    DOCUMENTED = "DOCUMENTED"
    OFFICIAL = "OFFICIAL"


class SupportAction(enum.Enum):
    """Action taken when support status changes"""
    HOLD = "HOLD"
    REDUCE_CONTACT = "REDUCE_CONTACT"
    REFER_TO_COMPLIANCE = "REFER_TO_COMPLIANCE"
    REQUEST_AUTHORITY = "REQUEST_AUTHORITY"
    CONTINUE_ALLOWED = "CONTINUE_ALLOWED"


class VulnerabilityCategory(enum.Enum):
    """Vulnerability category"""
    NONE = "NONE"
    MENTAL_HEALTH = "MENTAL_HEALTH"
    PHYSICAL_HEALTH = "PHYSICAL_HEALTH"
    DISABILITY = "DISABILITY"
    BEREAVEMENT = "BEREAVEMENT"
    LANGUAGE_BARRIER = "LANGUAGE_BARRIER"
    FINANCIAL_HARDSHIP = "FINANCIAL_HARDSHIP"
    DOMESTIC_ABUSE_RISK = "DOMESTIC_ABUSE_RISK"
    ELDERLY = "ELDERLY"
    PREGNANCY = "PREGNANCY"
    CARE_LEAVER = "CARE_LEAVER"
    OTHER = "OTHER"


class SafetyRisk(enum.Enum):
    """Safety risk level"""
    NONE = "NONE"
    CAUTION = "CAUTION"
    HIGH_RISK = "HIGH_RISK"


class DisputeStatus(enum.Enum):
    """Dispute status"""
    NONE = "NONE"
    INFORMAL = "INFORMAL"
    FORMAL = "FORMAL"


class ContactMethod(enum.Enum):
    """Preferred contact method"""
    LETTER = "LETTER"
    EMAIL = "EMAIL"
    PHONE = "PHONE"
    SMS = "SMS"
    PORTAL = "PORTAL"


class RepresentationType(enum.Enum):
    """Representation type"""
    NONE = "NONE"
    SOLICITOR = "SOLICITOR"
    ADVISOR = "ADVISOR"
    FAMILY_MEMBER = "FAMILY_MEMBER"
    OTHER = "OTHER"


class IdentityConfidence(enum.Enum):
    """Identity confidence level"""
    LOW = "LOW"
    MED = "MED"
    HIGH = "HIGH"


class ComplianceNoteCategory(enum.Enum):
    """Compliance note category"""
    VULNERABILITY_DETAILS = "VULNERABILITY_DETAILS"
    SAFETY_INCIDENT = "SAFETY_INCIDENT"
    DISPUTE_DETAILS = "DISPUTE_DETAILS"
    FRAUD_INVESTIGATION = "FRAUD_INVESTIGATION"
    COMPLIANCE_REVIEW = "COMPLIANCE_REVIEW"
    DATA_PROTECTION = "DATA_PROTECTION"
    OTHER = "OTHER"


class FeeChallengeReason(enum.Enum):
    """Fee challenge reason code"""
    INCORRECT_AMOUNT = "INCORRECT_AMOUNT"
    WRONG_STAGE = "WRONG_STAGE"
    NOT_INCURRED = "NOT_INCURRED"
    VULNERABILITY = "VULNERABILITY"
    OTHER = "OTHER"


class FeeChallengeStatus(enum.Enum):
    """Fee challenge status"""
    OPEN = "OPEN"
    UNDER_REVIEW = "UNDER_REVIEW"
    UPHELD = "UPHELD"
    REJECTED = "REJECTED"


class PartySupportProfile(Base):
    """
    PartySupportProfile model - debt advice/vulnerability status at Party level
    
    Applies across all debts/cases for a party.
    One PartySupportProfile per Party.
    
    See: docs/enforcesense/ENTITY_TREE_SPEC.md
    See: docs/enforcesense/PARTY_FLAGS_SPEC.md
    """
    __tablename__ = "party_support_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign key to Party (unique - one profile per party)
    party_id = Column(String(36), ForeignKey("parties.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Support status
    support_status = Column(Enum(SupportStatus), default=SupportStatus.NONE, nullable=False)
    advisor_org = Column(Enum(AdvisorOrg), nullable=True)
    reference_number = Column(String(100), nullable=True)
    
    # Dates
    effective_from = Column(DateTime(timezone=True), nullable=True)
    effective_to = Column(DateTime(timezone=True), nullable=True)
    
    # Evidence
    evidence_level = Column(Enum(EvidenceLevel), nullable=True)
    notes = Column(Text, nullable=True)  # Internal notes
    documents = Column(JSON, default=list)  # JSON array of document links
    
    # Review dates
    last_verified_at = Column(DateTime(timezone=True), nullable=True)
    next_review_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    party = relationship("Party", back_populates="party_support_profile")
    case_impacts = relationship("CaseSupportImpact", back_populates="party_support_profile", foreign_keys="[CaseSupportImpact.party_id]")
    
    def __repr__(self):
        return f"<PartySupportProfile {self.party_id} - {self.support_status.value}>"


class CaseSupportImpact(Base):
    """
    CaseSupportImpact model - tracks support status impact per case (audit trail)
    
    Records what action was taken when support status changed.
    Provides auditability for compliance.
    
    See: docs/enforcesense/ENTITY_TREE_SPEC.md
    """
    __tablename__ = "case_support_impacts"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign keys
    case_id = Column(String(36), ForeignKey("enforcement_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    party_id = Column(String(36), ForeignKey("parties.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Support status at time of impact
    support_status_at_time = Column(Enum(SupportStatus), nullable=False)
    
    # Action taken
    action_taken = Column(Enum(SupportAction), nullable=False)
    hold_until = Column(DateTime(timezone=True), nullable=True)
    reason_code = Column(String(50), nullable=True)  # DEBT_ADVICE, BREATHING_SPACE, MEDICAL, etc.
    
    # Created by
    created_by = Column(String(36), nullable=True)  # FK to User
    notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    case = relationship("EnforcementCase", back_populates="support_impacts")
    party = relationship("Party", back_populates="case_support_impacts")
    party_support_profile = relationship("PartySupportProfile", back_populates="case_impacts")
    
    def __repr__(self):
        return f"<CaseSupportImpact {self.case_id} - {self.action_taken.value}>"


class PartyProfile(Base):
    """
    PartyProfile model - stable facts and preferences at Party level
    
    Stores stable facts that don't change frequently:
    - Preferred language and interpreter requirements
    - Preferred contact method
    - Representation (advisor/solicitor)
    - Identity confidence
    - Address verification status
    
    See: docs/enforcesense/PARTY_FLAGS_SPEC.md
    """
    __tablename__ = "party_profiles"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign key to Party (unique - one profile per party)
    party_id = Column(String(36), ForeignKey("parties.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Language and communication
    preferred_language = Column(String(5), default="en", nullable=False)  # ISO 639-1
    interpreter_required = Column(Boolean, default=False, nullable=False)
    preferred_contact_method = Column(Enum(ContactMethod), nullable=True)
    
    # Representation
    representation_type = Column(Enum(RepresentationType), default=RepresentationType.NONE, nullable=False)
    representation_contact_name = Column(String(255), nullable=True)
    representation_contact_details = Column(JSON, default=dict)  # Name, phone, email, etc.
    
    # Identity
    identity_confidence = Column(Enum(IdentityConfidence), nullable=True)
    address_verified = Column(Boolean, default=False, nullable=False)
    address_verification_date = Column(DateTime(timezone=True), nullable=True)
    known_aliases = Column(JSON, default=list)  # JSON array of previous names
    do_not_merge = Column(Boolean, default=False, nullable=False)  # Prevents bad dedupe merges
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    party = relationship("Party", back_populates="party_profile")
    
    def __repr__(self):
        return f"<PartyProfile {self.party_id}>"


class PartyFlags(Base):
    """
    PartyFlags model - boolean/enum signals at Party level
    
    Stores boolean/enum signals that indicate status or risk:
    - Vulnerability indicators (structured categories)
    - Safety risk flags
    - Contact restrictions
    - Dispute status
    - Fraud concerns
    - Financial behavior patterns
    
    See: docs/enforcesense/PARTY_FLAGS_SPEC.md
    """
    __tablename__ = "party_flags"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign key to Party (unique - one flags record per party)
    party_id = Column(String(36), ForeignKey("parties.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Vulnerability
    vulnerability_category = Column(Enum(VulnerabilityCategory), nullable=True)
    vulnerability_review_date = Column(DateTime(timezone=True), nullable=True)
    safeguarding_required = Column(Boolean, default=False, nullable=False)
    safeguarding_review_date = Column(DateTime(timezone=True), nullable=True)
    
    # Safety risk
    safety_risk = Column(Enum(SafetyRisk), default=SafetyRisk.NONE, nullable=False)
    safety_risk_notes_required = Column(Boolean, default=False, nullable=False)
    safety_risk_last_incident_date = Column(DateTime(timezone=True), nullable=True)
    no_doorstep_visits = Column(Boolean, default=False, nullable=False)
    no_doorstep_visits_reason = Column(String(50), nullable=True)  # SAFETY, VULNERABILITY, DISPUTE, OTHER
    no_call = Column(Boolean, default=False, nullable=False)
    harassment_sensitivity = Column(Boolean, default=False, nullable=False)
    
    # Dispute
    dispute_status = Column(Enum(DisputeStatus), default=DisputeStatus.NONE, nullable=False)
    representation_active = Column(Boolean, default=False, nullable=False)
    data_restriction = Column(Boolean, default=False, nullable=False)
    sar_in_progress = Column(Boolean, default=False, nullable=False)
    
    # Fraud
    suspected_fraud = Column(Boolean, default=False, nullable=False)
    impersonation_risk = Column(Boolean, default=False, nullable=False)
    known_scam_reports = Column(Boolean, default=False, nullable=False)
    
    # Address
    address_uncertainty = Column(String(20), nullable=True)  # VERIFIED, NOT_VERIFIED, GONE_AWAY, TRACE_REQUIRED
    deceased = Column(Boolean, default=False, nullable=False)  # For individuals
    dissolved = Column(Boolean, default=False, nullable=False)  # For companies
    deceased_dissolved_evidence_level = Column(Enum(EvidenceLevel), nullable=True)
    
    # Financial behavior (derived flags)
    payment_plan_in_place = Column(Boolean, default=False, nullable=False)
    affordability_review_date = Column(DateTime(timezone=True), nullable=True)
    payment_reliability_score = Column(String(10), nullable=True)  # GOOD, MIXED, POOR
    multiple_active_debts = Column(Boolean, default=False, nullable=False)  # Derived
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    party = relationship("Party", back_populates="party_flags")
    
    def __repr__(self):
        return f"<PartyFlags {self.party_id}>"


class PartyRestrictions(Base):
    """
    PartyRestrictions model - enforced rules at Party level
    
    Stores enforced rules that control system behavior:
    - Contact frequency limits
    - Channel blocks
    - Compliance approval requirements
    
    See: docs/enforcesense/PARTY_FLAGS_SPEC.md
    """
    __tablename__ = "party_restrictions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign key to Party (unique - one restrictions record per party)
    party_id = Column(String(36), ForeignKey("parties.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    
    # Contact frequency limits
    contact_frequency_limit = Column(String(20), nullable=True)  # NONE, REDUCED, MINIMAL, NONE_ALLOWED
    contact_frequency_limit_reason = Column(Text, nullable=True)
    
    # Channel blocks (JSON array: ["CALL", "SMS", "EMAIL", "LETTER", "VISIT"])
    channel_blocks = Column(JSON, default=list)
    
    # Compliance approval
    require_compliance_approval = Column(Boolean, default=False, nullable=False)
    compliance_approval_required_for = Column(JSON, default=list)  # ["VISITS", "LEGAL_ACTION", "ENFORCEMENT", "ALL"]
    
    # Restriction details
    restriction_effective_from = Column(DateTime(timezone=True), nullable=False)
    restriction_effective_to = Column(DateTime(timezone=True), nullable=True)
    restriction_reason = Column(Text, nullable=True)
    restriction_authorized_by = Column(String(36), nullable=True)  # FK to User
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    party = relationship("Party", back_populates="party_restrictions")
    
    def __repr__(self):
        return f"<PartyRestrictions {self.party_id}>"


class ComplianceNote(Base):
    """
    ComplianceNote model - detailed sensitive notes with restricted access
    
    Stores detailed sensitive information with:
    - Restricted permissions (compliance team only)
    - Full audit trail (created_by, reviewed_by)
    - Categorization for searchability
    - Evidence attachments
    
    See: docs/enforcesense/PARTY_FLAGS_SPEC.md
    """
    __tablename__ = "compliance_notes"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign keys
    party_id = Column(String(36), ForeignKey("parties.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(36), ForeignKey("enforcement_cases.id"), nullable=True, index=True)  # Optional, if case-specific
    
    # Note details
    category = Column(Enum(ComplianceNoteCategory), nullable=False)
    title = Column(String(255), nullable=False)
    note = Column(Text, nullable=False)  # Detailed notes
    evidence_level = Column(Enum(EvidenceLevel), nullable=True)
    documents = Column(JSON, default=list)  # JSON array of document links
    
    # Created by
    created_by = Column(String(36), nullable=False)  # FK to User (required)
    
    # Review workflow
    review_required = Column(Boolean, default=False, nullable=False)
    review_date = Column(DateTime(timezone=True), nullable=True)
    reviewed_by = Column(String(36), nullable=True)  # FK to User
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    party = relationship("Party", back_populates="compliance_notes")
    case = relationship("EnforcementCase", back_populates="compliance_notes")
    
    def __repr__(self):
        return f"<ComplianceNote {self.id[:8]}... - {self.category.value}>"


# ============================================================================
# Fee Transparency Models
# ============================================================================

class FeeChallenge(Base):
    """
    FeeChallenge model - allows debtors to challenge fees (UK legal requirement)
    
    Debtor-initiated challenge workflow with:
    - Automatic case hold on challenge
    - Compliance review and resolution
    - Fee reversal on uphold
    - Full audit trail
    
    See: docs/enforcesense/FEE_TRANSPARENCY.md
    """
    __tablename__ = "fee_challenges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Foreign keys
    fee_entry_id = Column(String(36), ForeignKey("ledger_entries.id"), nullable=False, index=True)  # FK to LedgerEntry, type=FEE_EARNED
    case_id = Column(String(36), ForeignKey("enforcement_cases.id"), nullable=False, index=True)
    debtor_party_id = Column(String(36), ForeignKey("parties.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Challenge details
    reason_code = Column(Enum(FeeChallengeReason), nullable=False)
    description = Column(Text, nullable=False)  # Debtor's explanation
    
    # Status
    status = Column(Enum(FeeChallengeStatus), default=FeeChallengeStatus.OPEN, nullable=False)
    
    # Resolution
    resolved_by = Column(String(36), nullable=True)  # FK to User
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Documents
    documents = Column(JSON, default=list)  # JSON array of supporting documents
    
    # Timestamps
    submitted_at = Column(DateTime(timezone=True), server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    fee_entry = relationship("LedgerEntry", foreign_keys=[fee_entry_id])
    case = relationship("EnforcementCase", back_populates="fee_challenges")
    debtor_party = relationship("Party", back_populates="fee_challenges")
    
    # Indexes
    __table_args__ = (
        Index('idx_fee_challenge_case', 'case_id', 'status'),
        Index('idx_fee_challenge_debtor', 'debtor_party_id'),
        Index('idx_fee_challenge_fee', 'fee_entry_id'),
    )
    
    def __repr__(self):
        return f"<FeeChallenge {self.id[:8]}... - {self.status.value}>"


class DebtorAuditLog(Base):
    """
    Audit log for debtor record access
    
    Tracks who views/accesses debtor records and when.
    This provides an audit trail for compliance and security.
    """
    __tablename__ = "debtor_audit_logs"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    debtor_id = Column(String(36), ForeignKey("debtors.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # User who accessed the record
    user_id = Column(String(36), nullable=False, index=True)  # Platform API user ID
    user_email = Column(String(255), nullable=True)  # Cached for historical reference
    user_name = Column(String(255), nullable=True)  # Cached for historical reference
    
    # Access details
    accessed_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    ip_address = Column(String(45), nullable=True)  # IPv4 or IPv6
    user_agent = Column(String(500), nullable=True)  # Browser/client info
    
    # Additional context
    action_type = Column(String(50), nullable=False, default="view")  # view, edit, export, etc.
    action_metadata = Column(JSON, default=dict)  # Additional context (renamed from 'metadata' - SQLAlchemy reserved word)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_debtor_audit_debtor_accessed', 'debtor_id', 'accessed_at'),
        Index('idx_debtor_audit_user_accessed', 'user_id', 'accessed_at'),
    )
    
    def __repr__(self):
        return f"<DebtorAuditLog debtor_id={self.debtor_id} user_id={self.user_id} accessed_at={self.accessed_at}>"


class CaseStatusHistory(Base):
    """
    Case status change history
    
    Tracks all status changes for a case, including who made the change and when.
    This provides an audit trail for case status transitions.
    """
    __tablename__ = "case_status_history"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(36), ForeignKey("enforcement_cases.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Status change details
    old_status = Column(Enum(CaseStatus), nullable=True)  # Previous status
    new_status = Column(Enum(CaseStatus), nullable=False)  # New status
    
    # User who made the change
    changed_by = Column(String(36), nullable=False, index=True)  # Platform API user ID
    changed_by_email = Column(String(255), nullable=True)  # Cached for historical reference
    changed_by_name = Column(String(255), nullable=True)  # Cached for historical reference
    
    # Change details
    changed_at = Column(DateTime(timezone=True), nullable=False, default=func.now(), index=True)
    reason = Column(Text, nullable=True)  # Optional reason for the change
    notes = Column(Text, nullable=True)  # Additional notes about the change
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), nullable=False, default=func.now())
    
    # Index for efficient queries
    __table_args__ = (
        Index('idx_case_status_history_case_changed', 'case_id', 'changed_at'),
        Index('idx_case_status_history_user_changed', 'changed_by', 'changed_at'),
    )
    
    def __repr__(self):
        return f"<CaseStatusHistory case_id={self.case_id} {self.old_status} -> {self.new_status} at {self.changed_at}>"
