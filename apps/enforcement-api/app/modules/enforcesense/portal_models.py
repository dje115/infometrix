#!/usr/bin/env python3
"""
Portal session models for Debtor Portal authentication
"""

from sqlalchemy import Column, String, DateTime, Boolean, Integer, ForeignKey
from sqlalchemy.sql import func
import uuid
from datetime import datetime, timezone
from app.core.database import Base


class PortalSession(Base):
    """
    Portal session model for Debtor Portal token-based authentication
    """
    __tablename__ = "portal_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    token = Column(String(255), unique=True, nullable=False, index=True)
    tenant_id = Column(String(36), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    case_id = Column(String(36), nullable=False, index=True)  # Reference to enforcement_cases.id
    debtor_id = Column(String(36), nullable=False)  # Reference to debtors.id
    case_reference = Column(String(100), nullable=False, index=True)  # For lookup without joining
    
    # Token metadata
    expires_at = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_accessed_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Rate limiting
    access_count = Column(Integer, default=0)
    last_access_ip = Column(String(45))  # IPv4 or IPv6
    
    # Status
    is_revoked = Column(Boolean, default=False)
    revoked_at = Column(DateTime(timezone=True))
    
    def is_expired(self) -> bool:
        """Check if token is expired"""
        return datetime.now(timezone.utc) > self.expires_at
    
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not revoked)"""
        return not self.is_expired() and not self.is_revoked



