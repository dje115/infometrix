# EnforceSense Development Rules

**Version:** 1.0  
**Status:** MANDATORY - Must Follow in All Development  
**Last Updated:** 2025-12-19

## Critical Rules for All EnforceSense Development

**CRITICAL**: Fee transparency is legally required in UK debt recovery/enforcement. See `docs/enforcesense/FEE_TRANSPARENCY.md` for complete fee visibility rules.

### 1. Financial Model Rules (MANDATORY)

**CRITICAL**: All financial development MUST follow the financial model specification.

**Reference**: `docs/enforcesense/FINANCIAL_MODEL.md`

#### Rule 1.1: Ledger is Single Source of Truth

**NEVER**:
- Store balances directly in Case or DebtAccount models
- Calculate totals from stored fields
- Trust "current_balance" or "total_recovered" fields

**ALWAYS**:
- Derive all balances from ledger entries
- Use ledger for all reporting
- Create ledger entry for every financial movement
- Query ledger for financial totals

**Example**:
```python
# ❌ WRONG - Don't do this
case.current_balance = case.original_amount - case.payments_received

# ✅ CORRECT - Do this
case.current_balance = (
    db.query(func.sum(LedgerEntry.amount))
    .filter(LedgerEntry.case_id == case.id)
    .filter(LedgerEntry.entry_type == 'DEBTOR_PAYMENT')
    .scalar() or 0
)
```

#### Rule 1.2: Immutable Ledger Entries

**NEVER**:
- Edit ledger entries after creation
- Delete ledger entries
- Change amounts after posting

**ALWAYS**:
- Create reversal entries for corrections
- Maintain full audit trail
- Track who created/reversed entries
- Store reversal reason

**Example**:
```python
# ❌ WRONG - Don't do this
ledger_entry.amount = new_amount
ledger_entry.save()

# ✅ CORRECT - Do this
# Create reversal
reversal = LedgerEntry(
    entry_type='ADJUSTMENT',
    amount=original_amount,
    case_id=ledger_entry.case_id,
    description=f"Reversal of entry {ledger_entry.id}",
    reversed_entry_id=ledger_entry.id,
    created_by=current_user.id
)
# Create corrected entry
corrected = LedgerEntry(
    entry_type=ledger_entry.entry_type,
    amount=new_amount,
    case_id=ledger_entry.case_id,
    description=f"Corrected entry for {ledger_entry.id}",
    created_by=current_user.id
)
```

#### Rule 1.3: Allocation Validation

**NEVER**:
- Allow allocations that don't sum to payment amount
- Allow negative allocations
- Skip allocation validation

**ALWAYS**:
- Validate `sum(allocation_lines.amount) == payment_entry.amount`
- Validate allocation order (regulatory compliance)
- Store allocation method (AUTOMATIC/MANUAL/RULE_BASED)
- Track who allocated

**Example**:
```python
# ✅ CORRECT - Always validate
def allocate_payment(payment_entry, allocation_lines):
    total_allocated = sum(line['amount'] for line in allocation_lines)
    
    if abs(total_allocated - payment_entry.amount) > 0.01:
        raise ValueError(
            f"Allocation total {total_allocated} does not match "
            f"payment amount {payment_entry.amount}"
        )
    
    # Validate regulatory order (principal before fees)
    validate_allocation_order(allocation_lines)
    
    # Create allocation
    allocation = PaymentAllocation(
        payment_entry_id=payment_entry.id,
        allocation_lines=allocation_lines,
        total_allocated=total_allocated,
        allocation_method='AUTOMATIC',
        allocated_by=current_user.id
    )
```

#### Rule 1.4: Fee Calculation

**NEVER**:
- Hardcode fee percentages
- Calculate fees outside FeeSchedule rules
- Skip fee justification

**ALWAYS**:
- Use FeeSchedule rules
- Link fee entries to FeeRule
- Store calculation details in metadata
- Support client-specific and case-specific overrides

**Example**:
```python
# ❌ WRONG - Don't do this
fee_amount = recovered_amount * 0.20  # Hardcoded 20%

# ✅ CORRECT - Do this
fee_schedule = get_fee_schedule_for_case(case_id)
fee_rules = fee_schedule.fee_rules.filter(is_active=True)
fees = []
for rule in fee_rules:
    if rule.trigger_event == 'ON_RECOVERY':
        fee_amount = calculate_fee(rule, recovered_amount)
        fees.append({
            'rule_id': rule.id,
            'amount': fee_amount,
            'calculation': {
                'base': rule.calculation_base,
                'rate': rule.rate_or_amount,
                'result': fee_amount
            }
        })
```

### 2. Entity Model Rules

#### Rule 2.1: Party-Level Flags

**ALWAYS**:
- Store flags at Party level (not Case level)
- Use three-layer architecture (PartyProfile, PartyFlags, PartyRestrictions)
- Apply flags across all debts/cases for a party
- Use ComplianceNote for sensitive details

**Reference**: `docs/enforcesense/PARTY_FLAGS_SPEC.md`

#### Rule 2.2: Multi-Debt Support

**ALWAYS**:
- Support multiple DebtAccounts per Party
- Support multiple DebtAccounts per Case (via CaseDebts)
- Allow partial payments across debts
- Maintain audit trail for all allocations

**Reference**: `docs/enforcesense/ENTITY_TREE_SPEC.md`

### 3. API Development Rules

#### Rule 3.1: Financial Endpoints

**MUST**:
- Use ledger for all financial queries
- Return derived balances (not stored)
- Include allocation details in payment responses
- Support audit trail queries

**Example**:
```python
@router.get("/cases/{case_id}/balance")
async def get_case_balance(case_id: str, db: AsyncSession = Depends(get_async_db)):
    # ✅ CORRECT - Derive from ledger
    total_debt = await get_total_debt_from_ledger(case_id, db)
    total_recovered = await get_total_recovered_from_ledger(case_id, db)
    current_balance = total_debt - total_recovered
    
    return {
        "total_debt": total_debt,
        "total_recovered": total_recovered,
        "current_balance": current_balance,
        "derived_from": "ledger_entries"  # Always indicate source
    }
```

#### Rule 3.2: Payment Processing

**MUST**:
- Create ledger entry first (DEBTOR_PAYMENT)
- Then create allocation
- Then calculate and create fees (FEE_EARNED)
- Finally create payout (CLIENT_PAYOUT) when released

**Reference**: `docs/enforcesense/FINANCIAL_MODEL.md` - Payment Flow section

### 4. Reporting Rules

#### Rule 4.1: All Reports from Ledger

**NEVER**:
- Use stored balance fields for reports
- Calculate from Case or DebtAccount totals
- Trust aggregated fields

**ALWAYS**:
- Query ledger entries directly
- Aggregate in SQL/query
- Include entry types in filters
- Show data source in report headers

**Example**:
```python
# ✅ CORRECT - Report from ledger
async def generate_client_statement(client_id: str, period_start: datetime, period_end: datetime):
    entries = await db.execute(
        select(LedgerEntry)
        .join(Case).join(DebtAccount)
        .where(
            DebtAccount.client_account_id == client_id,
            LedgerEntry.posted_at >= period_start,
            LedgerEntry.posted_at <= period_end
        )
    )
    
    # Aggregate by entry type
    recoveries = sum(e.amount for e in entries if e.entry_type == 'DEBTOR_PAYMENT')
    fees = sum(e.amount for e in entries if e.entry_type == 'FEE_EARNED')
    payouts = sum(e.amount for e in entries if e.entry_type == 'CLIENT_PAYOUT')
    
    return {
        "recoveries": recoveries,
        "fees_charged": fees,
        "net_paid": payouts,
        "source": "ledger_entries",
        "period": f"{period_start} to {period_end}"
    }
```

### 5. Testing Rules

#### Rule 5.1: Financial Tests

**MUST**:
- Test ledger immutability
- Test allocation validation
- Test fee calculation
- Test balance derivation
- Test audit trail

**Example**:
```python
def test_ledger_immutability():
    entry = create_ledger_entry(amount=100.00)
    entry_id = entry.id
    
    # Try to edit (should fail or be prevented)
    with pytest.raises(ImmutableError):
        entry.amount = 150.00
        entry.save()
    
    # Verify original unchanged
    original = get_ledger_entry(entry_id)
    assert original.amount == 100.00

def test_allocation_validation():
    payment = create_payment(amount=100.00)
    allocation_lines = [
        {"target_type": "PRINCIPAL", "amount": 80.00},
        {"target_type": "FEE", "amount": 20.00}
    ]
    
    # Should succeed (sums to 100)
    allocate_payment(payment, allocation_lines)
    
    # Should fail (sums to 90)
    allocation_lines[1]["amount"] = 10.00
    with pytest.raises(ValidationError):
        allocate_payment(payment, allocation_lines)
```

### 6. Documentation Rules

#### Rule 6.1: Reference Financial Model

**ALWAYS**:
- Reference `docs/enforcesense/FINANCIAL_MODEL.md` in financial code
- Add comments linking to specification
- Document any deviations from spec

**Example**:
```python
# See: docs/enforcesense/FINANCIAL_MODEL.md - Payment Flow section
async def process_debtor_payment(payment_data):
    """
    Process debtor payment following financial model specification.
    
    Steps:
    1. Create DEBTOR_PAYMENT ledger entry
    2. Allocate payment across debts/fees
    3. Calculate and create FEE_EARNED entries
    4. Update case balances (derived from ledger)
    
    Reference: docs/enforcesense/FINANCIAL_MODEL.md
    """
    ...
```

### 7. Security Rules

#### Rule 7.1: Financial Data Access

**MUST**:
- Restrict financial data access by role
- Audit all financial changes
- Require approval for reversals
- Log all allocation changes

#### Rule 7.2: Compliance Notes

**MUST**:
- Restrict ComplianceNote access to compliance team
- Audit all access to sensitive notes
- Require review workflow
- Track who viewed/edited notes

### 8. Performance Rules

#### Rule 8.1: Ledger Queries

**OPTIMIZE**:
- Use indexes on ledger queries
- Cache derived balances (with TTL)
- Use materialized views for reports (if needed)
- Batch ledger queries

**Example**:
```python
# ✅ CORRECT - Use indexed query
balance = await db.execute(
    select(func.sum(LedgerEntry.amount))
    .where(
        LedgerEntry.case_id == case_id,
        LedgerEntry.entry_type == 'DEBTOR_PAYMENT',
        LedgerEntry.status == 'CLEARED'
    )
    .where(LedgerEntry.tenant_id == tenant_id)  # Use index
)
```

## Checklist for Financial Development

Before implementing any financial feature, verify:

- [ ] Ledger entry created for every financial movement
- [ ] Balances derived from ledger (not stored)
- [ ] Allocation validation implemented
- [ ] Fee calculation uses FeeSchedule rules
- [ ] Audit trail complete (who, when, why)
- [ ] Reports query ledger directly
- [ ] Tests cover immutability and validation
- [ ] Documentation references financial model spec
- [ ] Security/permissions checked
- [ ] Performance optimized (indexes, caching)

## Quick Reference

| Rule | Reference Document |
|------|-------------------|
| Financial Model | `docs/enforcesense/FINANCIAL_MODEL.md` |
| Entity Tree | `docs/enforcesense/ENTITY_TREE_SPEC.md` |
| Party Flags | `docs/enforcesense/PARTY_FLAGS_SPEC.md` |
| Migration Plan | `docs/enforcesense/MIGRATION_PLAN.md` |

## Enforcement

**These rules are MANDATORY for all EnforceSense development.**

Code reviews MUST check:
- Financial code follows ledger model
- Balances are derived, not stored
- Allocation validation is present
- Audit trail is complete
- Documentation references are included

