# Performance Review - Infometrix Platform

**Date:** 2025-01-27  
**Focus:** Code and Database Performance Analysis  
**Status:** Critical Issues Identified

---

## Executive Summary

This review identifies **critical performance bottlenecks** in the Infometrix platform, particularly in the EnforceSense module. The main issues are:

1. **N+1 Query Problems** - Multiple instances causing excessive database queries
2. **Missing Database Indexes** - Critical composite indexes missing for common query patterns
3. **Inefficient Query Patterns** - Separate queries instead of joins/eager loading
4. **Large Route Files** - 2220-line routes.py file indicating architectural issues
5. **Missing Query Optimization** - No eager loading for related entities

**Estimated Performance Impact:** 50-80% improvement possible with fixes

---

## 1. Critical N+1 Query Problems

### 1.1 Case Detail Endpoint (`get_case`)

**Location:** `apps/enforcement-api/app/modules/enforcesense/routes.py:748-782`

**Problem:**
```python
# Lines 774-780: Loading related entities separately (N+1 problem)
debtor_stmt = select(Debtor).where(Debtor.id == case.debtor_id)
debtor_result = await db.execute(debtor_stmt)
case.debtor = debtor_result.scalar_one_or_none()

client_stmt = select(EnforcementClient).where(EnforcementClient.id == case.client_id)
client_result = await db.execute(client_stmt)
case.client = client_result.scalar_one_or_none()
```

**Impact:** 3 database queries instead of 1 (case + debtor + client)

**Fix:**
```python
from sqlalchemy.orm import selectinload

stmt = select(EnforcementCase).options(
    selectinload(EnforcementCase.debtor),
    selectinload(EnforcementCase.client)
).where(
    and_(
        EnforcementCase.id == case_id,
        EnforcementCase.tenant_id == current_user.tenant_id,
        EnforcementCase.is_deleted == False
    )
)
```

### 1.2 Case Update Endpoint (`update_case`)

**Location:** `apps/enforcement-api/app/modules/enforcesense/routes.py:893-966`

**Problem:** Same N+1 issue as above (lines 958-964)

**Fix:** Use eager loading as shown above

### 1.3 Case List Endpoint (`list_cases`)

**Location:** `apps/enforcement-api/app/modules/enforcesense/routes.py:635-745`

**Problem:** 
- Uses `outerjoin` but doesn't load related entities
- Separate count query (lines 684-719) that duplicates logic
- Missing eager loading for debtor/client relationships

**Current Code:**
```python
# Lines 657-670: Joins but doesn't use eager loading
stmt = stmt.outerjoin(Debtor, EnforcementCase.debtor_id == Debtor.id)
stmt = stmt.outerjoin(EnforcementClient, EnforcementCase.client_id == EnforcementClient.id)
```

**Fix:**
```python
from sqlalchemy.orm import selectinload

stmt = select(EnforcementCase).options(
    selectinload(EnforcementCase.debtor),
    selectinload(EnforcementCase.client)
).where(
    and_(
        EnforcementCase.tenant_id == current_user.tenant_id,
        EnforcementCase.is_deleted == False
    )
)

# For search, use proper join with conditions
if search:
    stmt = stmt.join(Debtor, EnforcementCase.debtor_id == Debtor.id)
    stmt = stmt.join(EnforcementClient, EnforcementCase.client_id == EnforcementClient.id)
    stmt = stmt.where(
        or_(
            EnforcementCase.case_reference.ilike(f"%{search}%"),
            Debtor.legal_name.ilike(f"%{search}%"),
            EnforcementClient.name.ilike(f"%{search}%")
        )
    )
```

### 1.4 Dashboard Endpoint (`get_dashboard`)

**Location:** `apps/enforcement-api/app/modules/enforcesense/routes.py:969-1035`

**Problem:** Multiple separate queries instead of optimized aggregations

**Current:** 4 separate queries (debtors, clients, cases by status, financials)

**Fix:** Combine where possible, use single query with GROUP BY for cases by status

---

## 2. Missing Database Indexes

### 2.1 Critical Missing Composite Indexes

**Location:** `apps/enforcement-api/app/modules/enforcesense/models.py`

#### Missing Indexes for EnforcementCase:

```sql
-- CRITICAL: Most queries filter by tenant_id + is_deleted + status
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_deleted_status 
ON enforcement_cases(tenant_id, is_deleted, status) 
WHERE is_deleted = false;

-- CRITICAL: Common filter pattern for list queries
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_deleted_created 
ON enforcement_cases(tenant_id, is_deleted, created_at DESC) 
WHERE is_deleted = false;

-- CRITICAL: Search queries filter by tenant + deleted + search fields
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_deleted_reference 
ON enforcement_cases(tenant_id, is_deleted, case_reference) 
WHERE is_deleted = false;

-- CRITICAL: Filter by assigned agent (common query pattern)
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_assigned 
ON enforcement_cases(tenant_id, assigned_agent, status) 
WHERE assigned_agent IS NOT NULL AND is_deleted = false;
```

#### Missing Indexes for Debtor:

```sql
-- CRITICAL: Most queries filter by tenant_id + is_deleted
CREATE INDEX IF NOT EXISTS idx_debtors_tenant_deleted 
ON debtors(tenant_id, is_deleted, created_at DESC) 
WHERE is_deleted = false;

-- CRITICAL: Search queries on legal_name
CREATE INDEX IF NOT EXISTS idx_debtors_tenant_legal_name 
ON debtors(tenant_id, legal_name) 
WHERE is_deleted = false;

-- CRITICAL: Email searches (if used frequently)
CREATE INDEX IF NOT EXISTS idx_debtors_tenant_email 
ON debtors(tenant_id, email) 
WHERE email IS NOT NULL AND is_deleted = false;
```

#### Missing Indexes for LedgerEntry:

```sql
-- CRITICAL: Balance calculations filter by case_id + tenant_id + status
CREATE INDEX IF NOT EXISTS idx_ledger_entries_case_tenant_status 
ON ledger_entries(case_id, tenant_id, status, entry_type) 
WHERE is_deleted = false AND status != 'REVERSED';

-- CRITICAL: Ledger queries ordered by posted_at
CREATE INDEX IF NOT EXISTS idx_ledger_entries_case_posted 
ON ledger_entries(case_id, posted_at DESC, created_at DESC) 
WHERE is_deleted = false;

-- CRITICAL: Tenant-level ledger queries
CREATE INDEX IF NOT EXISTS idx_ledger_entries_tenant_posted 
ON ledger_entries(tenant_id, posted_at DESC) 
WHERE is_deleted = false;
```

#### Missing Indexes for CaseNote:

```sql
-- CRITICAL: Notes ordered by created_at
CREATE INDEX IF NOT EXISTS idx_case_notes_case_created 
ON case_notes(case_id, created_at DESC) 
WHERE tenant_id IS NOT NULL;
```

### 2.2 Partial Indexes for Soft Deletes

**Problem:** Most queries filter by `is_deleted = false`, but indexes don't use partial indexes

**Fix:** Use PostgreSQL partial indexes (WHERE clauses) as shown above

---

## 3. Inefficient Query Patterns

### 3.1 Separate Count Query in `list_cases`

**Location:** `apps/enforcement-api/app/modules/enforcesense/routes.py:684-719`

**Problem:** Duplicates query logic for counting, inefficient

**Current:**
```python
# Builds separate count query that duplicates all filters
count_base = select(EnforcementCase).where(...)
# ... duplicates all filter logic ...
count_stmt = select(func.count()).select_from(count_base.subquery())
```

**Fix:** Use window functions or optimize count query:
```python
# Option 1: Use window function (more efficient)
stmt = select(
    EnforcementCase,
    func.count().over().label('total_count')
).where(...)

# Option 2: Use separate optimized count (if window functions not suitable)
count_stmt = select(func.count(EnforcementCase.id)).where(
    and_(
        EnforcementCase.tenant_id == current_user.tenant_id,
        EnforcementCase.is_deleted == False
    )
)
# Apply same filters but simpler
```

### 3.2 Case Reference Uniqueness Check

**Location:** `apps/enforcement-api/app/modules/enforcesense/routes.py:831-862`

**Problem:** Separate query to check uniqueness, could use database constraint

**Current:**
```python
existing_stmt = select(EnforcementCase).where(
    and_(
        EnforcementCase.case_reference == case_reference,
        EnforcementCase.tenant_id == current_user.tenant_id
    )
)
```

**Fix:** 
1. Add unique constraint: `(tenant_id, case_reference)` 
2. Handle IntegrityError instead of pre-checking

### 3.3 Balance Calculations

**Location:** `apps/enforcement-api/app/services/case_transaction_service.py:154-205`

**Problem:** Aggregates all entry types even when only some are needed

**Current:**
```python
stmt = select(
    LedgerEntry.entry_type,
    func.sum(LedgerEntry.amount).label('total')
).where(...).group_by(LedgerEntry.entry_type)
```

**Fix:** Use conditional aggregation for better performance:
```python
stmt = select(
    func.sum(
        case(
            (LedgerEntry.entry_type == LedgerEntryType.DEBTOR_PAYMENT, LedgerEntry.amount),
            else_=0
        )
    ).label('total_payments'),
    func.sum(
        case(
            (LedgerEntry.entry_type == LedgerEntryType.FEE_EARNED, LedgerEntry.amount),
            else_=0
        )
    ).label('total_fees'),
    # ... etc
).where(...)
```

---

## 4. Code Architecture Issues

### 4.1 Large Route File

**Problem:** `routes.py` is 2220 lines - violates Single Responsibility Principle

**Impact:** 
- Hard to maintain
- Hard to test
- Performance issues harder to identify
- Code duplication

**Recommendation:** Split into separate route modules:
```
routes/
  ├── __init__.py
  ├── debtors.py
  ├── clients.py
  ├── cases.py
  ├── transactions.py
  ├── payments.py
  ├── arrangements.py
  └── audit.py
```

### 4.2 Missing Service Layer Abstraction

**Problem:** Business logic mixed with route handlers

**Current:** Routes directly query database

**Fix:** Move complex logic to service layer (already started with `CaseTransactionService`)

---

## 5. Database Schema Issues

### 5.1 Missing Foreign Key Indexes

**Problem:** Foreign keys don't always have indexes

**Fix:** Ensure all foreign keys have indexes:
```sql
-- Check existing indexes
SELECT 
    tablename, 
    indexname, 
    indexdef 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND tablename IN ('enforcement_cases', 'debtors', 'ledger_entries');

-- Add missing FK indexes
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_debtor_id 
ON enforcement_cases(debtor_id) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_client_id 
ON enforcement_cases(client_id) 
WHERE is_deleted = false;
```

### 5.2 JSON Field Queries

**Problem:** JSON fields (`address_history`, `risk_flags`, etc.) queried without GIN indexes

**Fix:** Add GIN indexes for JSONB fields if frequently queried:
```sql
-- If JSON fields are frequently queried
CREATE INDEX IF NOT EXISTS idx_debtors_address_history_gin 
ON debtors USING gin(address_history) 
WHERE address_history IS NOT NULL;
```

---

## 6. Query Performance Recommendations

### 6.1 Use Eager Loading Consistently

**Pattern to Follow:**
```python
from sqlalchemy.orm import selectinload, joinedload

# For one-to-many relationships: use selectinload
stmt = select(EnforcementCase).options(
    selectinload(EnforcementCase.ledger_entries),
    selectinload(EnforcementCase.notes)
)

# For many-to-one relationships: use joinedload (more efficient)
stmt = select(EnforcementCase).options(
    joinedload(EnforcementCase.debtor),
    joinedload(EnforcementCase.client)
)
```

### 6.2 Pagination Best Practices

**Current:** Uses `offset` and `limit` (can be slow for large offsets)

**Fix:** Use cursor-based pagination for large datasets:
```python
# Cursor-based pagination (better for large datasets)
stmt = select(EnforcementCase).where(
    EnforcementCase.id > last_id,  # cursor
    EnforcementCase.tenant_id == tenant_id
).order_by(EnforcementCase.id).limit(limit)
```

### 6.3 Query Result Caching

**Problem:** No caching for frequently accessed data

**Recommendation:** Add Redis caching for:
- Case details (TTL: 5 minutes)
- Dashboard statistics (TTL: 1 minute)
- Debtor details (TTL: 10 minutes)

---

## 7. Immediate Action Items

### Priority 1 (Critical - Do Immediately)

1. **Fix N+1 queries in `get_case` and `update_case`**
   - Add eager loading for debtor and client
   - Estimated improvement: 60-70% faster

2. **Add composite indexes for common query patterns**
   - `idx_enforcement_cases_tenant_deleted_status`
   - `idx_enforcement_cases_tenant_deleted_created`
   - `idx_debtors_tenant_deleted`
   - `idx_ledger_entries_case_tenant_status`
   - Estimated improvement: 50-80% faster queries

3. **Fix `list_cases` endpoint**
   - Add eager loading
   - Optimize count query
   - Estimated improvement: 40-60% faster

### Priority 2 (High - Do This Week)

4. **Split routes.py into modules**
   - Better maintainability
   - Easier to optimize individual endpoints

5. **Add query result caching**
   - Redis for frequently accessed data
   - Estimated improvement: 80-90% faster for cached requests

6. **Optimize balance calculations**
   - Use conditional aggregation
   - Cache results when possible
   - Estimated improvement: 30-50% faster

### Priority 3 (Medium - Do This Month)

7. **Add database query monitoring**
   - Log slow queries (>100ms)
   - Track N+1 queries
   - Set up alerts

8. **Add database connection pooling optimization**
   - Review pool sizes
   - Monitor connection usage

9. **Add database query explain plans**
   - Analyze query execution plans
   - Identify missing indexes

---

## 8. Performance Testing Recommendations

### 8.1 Load Testing

**Test Scenarios:**
1. List cases with 10,000+ cases
2. Get case details (with related entities)
3. Dashboard with large datasets
4. Balance calculations with many ledger entries

### 8.2 Query Profiling

**Tools:**
- PostgreSQL `EXPLAIN ANALYZE`
- SQLAlchemy query logging
- Application Performance Monitoring (APM)

**Metrics to Track:**
- Query execution time
- Number of queries per request
- Database connection pool usage
- Cache hit rates

---

## 9. Code Examples

### 9.1 Optimized `get_case` Endpoint

```python
@router.get("/cases/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: str,
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user)
):
    """Get a single case with related entities (OPTIMIZED)"""
    await check_permission(current_user, "enforcesense:view_cases")
    
    # Use eager loading to prevent N+1 queries
    stmt = select(EnforcementCase).options(
        selectinload(EnforcementCase.debtor),
        selectinload(EnforcementCase.client),
        selectinload(EnforcementCase.ledger_entries).limit(100),  # Limit ledger entries
        selectinload(EnforcementCase.notes).limit(50)  # Limit notes
    ).where(
        and_(
            EnforcementCase.id == case_id,
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    
    result = await db.execute(stmt)
    case = result.scalar_one_or_none()
    
    if not case:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Case not found"
        )
    
    return case
```

### 9.2 Optimized `list_cases` Endpoint

```python
@router.get("/cases", response_model=List[CaseResponse])
async def list_cases(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: Optional[str] = Query(None),
    status: Optional[CaseStatus] = Query(None),
    debtor_id: Optional[str] = Query(None),
    client_id: Optional[str] = Query(None),
    sort_by: str = Query("created_at"),
    sort_order: str = Query("desc"),
    db: AsyncSession = Depends(get_async_db),
    current_user: User = Depends(get_current_user),
    response: Response = None
):
    """List cases with tenant isolation (OPTIMIZED)"""
    await check_permission(current_user, "enforcesense:view_cases")
    
    # Base query with eager loading
    stmt = select(EnforcementCase).options(
        selectinload(EnforcementCase.debtor),
        selectinload(EnforcementCase.client)
    ).where(
        and_(
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    
    # Apply filters
    if search:
        # Use proper joins for search
        stmt = stmt.join(Debtor, EnforcementCase.debtor_id == Debtor.id)
        stmt = stmt.join(EnforcementClient, EnforcementCase.client_id == EnforcementClient.id)
        stmt = stmt.where(
            or_(
                EnforcementCase.case_reference.ilike(f"%{search}%"),
                Debtor.legal_name.ilike(f"%{search}%"),
                EnforcementClient.name.ilike(f"%{search}%")
            )
        )
    
    if status:
        stmt = stmt.where(EnforcementCase.status == status)
    
    if debtor_id:
        stmt = stmt.where(EnforcementCase.debtor_id == debtor_id)
    
    if client_id:
        stmt = stmt.where(EnforcementCase.client_id == client_id)
    
    # Optimized count query (simpler, uses indexes)
    count_stmt = select(func.count(EnforcementCase.id)).where(
        and_(
            EnforcementCase.tenant_id == current_user.tenant_id,
            EnforcementCase.is_deleted == False
        )
    )
    # Apply same filters to count
    if status:
        count_stmt = count_stmt.where(EnforcementCase.status == status)
    if debtor_id:
        count_stmt = count_stmt.where(EnforcementCase.debtor_id == debtor_id)
    if client_id:
        count_stmt = count_stmt.where(EnforcementCase.client_id == client_id)
    
    count_result = await db.execute(count_stmt)
    total_count = count_result.scalar() or 0
    
    # Apply sorting
    sort_column_map = {
        "created_at": EnforcementCase.created_at,
        "case_reference": EnforcementCase.case_reference,
        "original_amount": EnforcementCase.original_amount,
        "current_balance": EnforcementCase.current_balance,
        "status": EnforcementCase.status
    }
    sort_column = sort_column_map.get(sort_by, EnforcementCase.created_at)
    if sort_order == "asc":
        stmt = stmt.order_by(sort_column.asc())
    else:
        stmt = stmt.order_by(sort_column.desc())
    
    # Apply pagination
    stmt = stmt.offset(skip).limit(limit)
    
    result = await db.execute(stmt)
    cases = result.scalars().all()
    
    # Set total count in response headers
    if response:
        response.headers["X-Total-Count"] = str(total_count)
    
    return cases
```

---

## 10. Database Migration Script

Create a new migration file: `apps/enforcement-api/migrations/add_performance_indexes_enforcesense.sql`

```sql
-- Migration: Add performance indexes for EnforceSense module
-- Purpose: Improve query performance for common access patterns

-- EnforcementCase indexes
CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_deleted_status 
ON enforcement_cases(tenant_id, is_deleted, status) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_deleted_created 
ON enforcement_cases(tenant_id, is_deleted, created_at DESC) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_deleted_reference 
ON enforcement_cases(tenant_id, is_deleted, case_reference) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_enforcement_cases_tenant_assigned 
ON enforcement_cases(tenant_id, assigned_agent, status) 
WHERE assigned_agent IS NOT NULL AND is_deleted = false;

-- Debtor indexes
CREATE INDEX IF NOT EXISTS idx_debtors_tenant_deleted 
ON debtors(tenant_id, is_deleted, created_at DESC) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_debtors_tenant_legal_name 
ON debtors(tenant_id, legal_name) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_debtors_tenant_email 
ON debtors(tenant_id, email) 
WHERE email IS NOT NULL AND is_deleted = false;

-- LedgerEntry indexes
CREATE INDEX IF NOT EXISTS idx_ledger_entries_case_tenant_status 
ON ledger_entries(case_id, tenant_id, status, entry_type) 
WHERE is_deleted = false AND status != 'REVERSED';

CREATE INDEX IF NOT EXISTS idx_ledger_entries_case_posted 
ON ledger_entries(case_id, posted_at DESC, created_at DESC) 
WHERE is_deleted = false;

CREATE INDEX IF NOT EXISTS idx_ledger_entries_tenant_posted 
ON ledger_entries(tenant_id, posted_at DESC) 
WHERE is_deleted = false;

-- CaseNote indexes
CREATE INDEX IF NOT EXISTS idx_case_notes_case_created 
ON case_notes(case_id, created_at DESC) 
WHERE tenant_id IS NOT NULL;

-- EnforcementClient indexes
CREATE INDEX IF NOT EXISTS idx_enforcement_clients_tenant_deleted 
ON enforcement_clients(tenant_id, is_deleted, name) 
WHERE is_deleted = false;

-- Comments
COMMENT ON INDEX idx_enforcement_cases_tenant_deleted_status IS 
'Composite index for common case list queries filtered by tenant, deleted status, and status';

COMMENT ON INDEX idx_ledger_entries_case_tenant_status IS 
'Composite index for balance calculations and ledger queries';
```

---

## 11. Monitoring and Metrics

### 11.1 Key Metrics to Track

1. **Query Performance:**
   - Average query time per endpoint
   - P95/P99 query times
   - Number of queries per request

2. **Database:**
   - Connection pool usage
   - Slow query count (>100ms)
   - Index usage statistics

3. **Application:**
   - Request latency
   - Error rates
   - Cache hit rates

### 11.2 Recommended Tools

- **PostgreSQL:** `pg_stat_statements` extension
- **Application:** SQLAlchemy query logging
- **APM:** Sentry, New Relic, or Datadog
- **Database Monitoring:** pgAdmin, pg_stat_monitor

---

## 12. Conclusion

The performance issues identified are **fixable** and will result in **significant improvements** (50-80% faster) once addressed. The main focus should be:

1. **Immediate:** Fix N+1 queries and add missing indexes
2. **Short-term:** Optimize query patterns and add caching
3. **Long-term:** Refactor code architecture and add monitoring

**Estimated Total Improvement:** 60-80% faster response times for affected endpoints.

---

## Appendix: Query Performance Checklist

- [ ] All foreign keys have indexes
- [ ] Composite indexes for common filter patterns
- [ ] Partial indexes for soft-delete queries
- [ ] Eager loading for related entities
- [ ] No N+1 query problems
- [ ] Query result caching implemented
- [ ] Pagination optimized
- [ ] Slow query logging enabled
- [ ] Database connection pooling optimized
- [ ] Query execution plans analyzed

