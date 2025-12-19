# EnforceSense Documentation

**Version:** 2.0  
**Last Updated:** 2025-12-19

## Overview

This directory contains all EnforceSense module documentation. These documents are **MANDATORY** references for all EnforceSense development.

## Core Documents (Must Read)

### 1. Entity Tree Specification
**File**: `ENTITY_TREE_SPEC.md`

**Purpose**: Defines the canonical entity tree for EnforceSense

**Key Topics**:
- Party model (replaces Debtor)
- DebtAccount model (one debt = one record)
- CaseDebts join table (multi-debt support)
- PartySupportProfile (debt advice tracking)
- PartyProfile, PartyFlags, PartyRestrictions (flag system)
- ComplianceNote (sensitive notes)
- CRM integration (Customer/Account linking)

**When to Reference**: 
- Designing new models
- Understanding relationships
- Planning migrations

### 2. Financial Model & Ledger Specification ⚠️ CRITICAL
**File**: `FINANCIAL_MODEL.md`

**Purpose**: Defines the end-to-end financial model for payments, fees, and client payouts

**Key Topics**:
- LedgerEntry (single source of truth)
- Payment flow (debtor → allocation → fees → payout)
- FeeSchedule and FeeRule models
- PaymentAllocation model
- Reporting requirements
- Audit trail requirements

**CRITICAL RULES**:
- Ledger is single source of truth
- All balances derived from ledger (never stored)
- Immutable ledger entries
- Full allocation traceability

**When to Reference**: 
- **ALL financial development**
- Payment processing
- Fee calculation
- Reporting
- Any code that touches money

### 3. Development Rules
**File**: `DEVELOPMENT_RULES.md`

**Purpose**: Mandatory rules for all EnforceSense development

**Key Topics**:
- Financial model rules (MANDATORY)
- Entity model rules
- API development rules
- Reporting rules
- Testing rules
- Security rules

**When to Reference**: 
- **Before writing any code**
- Code reviews
- Testing
- Debugging

### 4. Party Flags Specification
**File**: `PARTY_FLAGS_SPEC.md`

**Purpose**: Defines comprehensive flag system for Party-level data

**Key Topics**:
- Three-layer architecture (PartyProfile, PartyFlags, PartyRestrictions)
- Complete flag list (identity, vulnerability, safety, dispute, fraud, etc.)
- Minimum 8 must-have flags
- ComplianceNote model
- Automation rules

**When to Reference**: 
- Implementing flag system
- Adding new flags
- UI development for flags

### 5. Migration Plan
**File**: `MIGRATION_PLAN.md`

**Purpose**: Step-by-step migration from current to new model

**Key Topics**:
- 6 migration phases
- Data migration strategy
- Risk mitigation
- Testing strategy

**When to Reference**: 
- Planning migrations
- Executing migrations
- Testing migrations

## Quick Reference

### For Financial Development
1. Read `FINANCIAL_MODEL.md` first
2. Follow rules in `DEVELOPMENT_RULES.md`
3. Reference `ENTITY_TREE_SPEC.md` for model relationships

### For Model Development
1. Read `ENTITY_TREE_SPEC.md` first
2. Check `PARTY_FLAGS_SPEC.md` for flag requirements
3. Follow `DEVELOPMENT_RULES.md` for implementation

### For API Development
1. Read `DEVELOPMENT_RULES.md` first
2. Reference `FINANCIAL_MODEL.md` for financial endpoints
3. Check `ENTITY_TREE_SPEC.md` for model structure

### For Reporting
1. Read `FINANCIAL_MODEL.md` - Reporting section
2. Follow `DEVELOPMENT_RULES.md` - Reporting rules
3. Query ledger directly (never use stored balances)

## Document Status

| Document | Status | Priority |
|----------|--------|----------|
| Entity Tree Spec | ✅ Complete | High |
| Financial Model | ✅ Complete | **CRITICAL** |
| Development Rules | ✅ Complete | **CRITICAL** |
| Party Flags Spec | ✅ Complete | High |
| Migration Plan | ✅ Complete | Medium |

## Implementation Status

### Phase 1: Foundation ✅
- [x] Documentation complete
- [x] Entity tree specified
- [x] Financial model specified
- [x] Development rules defined

### Phase 2: Models (Pending)
- [ ] Party model (rename from Debtor)
- [ ] DebtAccount model
- [ ] CaseDebts model
- [ ] LedgerEntry model ⚠️ CRITICAL
- [ ] PaymentAllocation model
- [ ] FeeSchedule and FeeRule models
- [ ] PartyProfile, PartyFlags, PartyRestrictions
- [ ] PartySupportProfile
- [ ] CaseSupportImpact
- [ ] ComplianceNote

### Phase 3: Financial Implementation (Pending)
- [ ] Payment flow implementation
- [ ] Fee calculation engine
- [ ] Allocation engine
- [ ] Payout processing
- [ ] Remove stored balances

### Phase 4: Reporting (Pending)
- [ ] Client Statement
- [ ] Fee Revenue Report
- [ ] Case Recovery Report
- [ ] Trust Reconciliation

## Critical Reminders

### ⚠️ Financial Development
- **ALWAYS** use ledger for financial queries
- **NEVER** store balances directly
- **ALWAYS** create ledger entry for every financial movement
- **ALWAYS** validate allocations
- **ALWAYS** use FeeSchedule rules for fees

### ⚠️ Model Development
- **ALWAYS** store flags at Party level
- **ALWAYS** support multi-debt scenarios
- **ALWAYS** link to CRM Customer/Account
- **ALWAYS** maintain audit trail

### ⚠️ API Development
- **ALWAYS** derive balances from ledger
- **ALWAYS** include allocation details
- **ALWAYS** support audit trail queries
- **ALWAYS** reference documentation in code

## Getting Help

If unsure about implementation:
1. Check `DEVELOPMENT_RULES.md` first
2. Reference relevant specification document
3. Follow examples in documentation
4. Ask for clarification if needed

## Updates

When updating these documents:
1. Update version number
2. Update "Last Updated" date
3. Document changes in commit message
4. Notify team of critical changes

