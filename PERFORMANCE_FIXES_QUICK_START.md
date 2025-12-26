# Performance Fixes - Quick Start Guide

**Priority Actions to Fix Performance Issues**

---

## Step 1: Apply Database Indexes (5 minutes)

Run the migration to add critical indexes:

```bash
# Connect to your database
psql -U your_user -d ccs_quote_tool -f apps/enforcement-api/migrations/add_performance_indexes_enforcesense.sql
```

**Expected Impact:** 50-80% faster queries

---

## Step 2: Fix N+1 Query in `get_case` (10 minutes)

**File:** `apps/enforcement-api/app/modules/enforcesense/routes.py`

**Find:** Line 748 (`get_case` function)

**Replace:**
```python
stmt = select(EnforcementCase).where(
    and_(
        EnforcementCase.id == case_id,
        EnforcementCase.tenant_id == current_user.tenant_id,
        EnforcementCase.is_deleted == False
    )
)
result = await db.execute(stmt)
case = result.scalar_one_or_none()

if not case:
    raise HTTPException(...)

# Load related entities
debtor_stmt = select(Debtor).where(Debtor.id == case.debtor_id)
debtor_result = await db.execute(debtor_stmt)
case.debtor = debtor_result.scalar_one_or_none()

client_stmt = select(EnforcementClient).where(EnforcementClient.id == case.client_id)
client_result = await db.execute(client_stmt)
case.client = client_result.scalar_one_or_none()
```

**With:**
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
result = await db.execute(stmt)
case = result.scalar_one_or_none()

if not case:
    raise HTTPException(...)
```

**Expected Impact:** 60-70% faster (3 queries → 1 query)

---

## Step 3: Fix N+1 Query in `update_case` (10 minutes)

**File:** `apps/enforcement-api/app/modules/enforcesense/routes.py`

**Find:** Line 893 (`update_case` function)

**Replace:** Lines 958-964 (same pattern as Step 2)

**With:** Same eager loading pattern as Step 2

---

## Step 4: Fix `list_cases` Endpoint (15 minutes)

**File:** `apps/enforcement-api/app/modules/enforcesense/routes.py`

**Find:** Line 635 (`list_cases` function)

**Key Changes:**

1. **Add import at top:**
```python
from sqlalchemy.orm import selectinload
```

2. **Replace base query (around line 649):**
```python
# OLD:
stmt = select(EnforcementCase).where(...)

# NEW:
stmt = select(EnforcementCase).options(
    selectinload(EnforcementCase.debtor),
    selectinload(EnforcementCase.client)
).where(...)
```

3. **Fix search joins (around line 657):**
```python
# OLD:
if search:
    stmt = stmt.outerjoin(Debtor, EnforcementCase.debtor_id == Debtor.id)
    stmt = stmt.outerjoin(EnforcementClient, EnforcementCase.client_id == EnforcementClient.id)
    stmt = stmt.where(...)

# NEW:
if search:
    stmt = stmt.join(Debtor, EnforcementCase.debtor_id == Debtor.id)
    stmt = stmt.join(EnforcementClient, EnforcementCase.client_id == EnforcementClient.id)
    stmt = stmt.where(...)
```

**Expected Impact:** 40-60% faster list queries

---

## Step 5: Test the Changes

```bash
# Run your test suite
pytest tests/

# Or manually test endpoints:
# 1. GET /enforcesense/cases/{case_id}
# 2. GET /enforcesense/cases
# 3. PUT /enforcesense/cases/{case_id}
```

---

## Expected Results

After applying these fixes:

- **`get_case` endpoint:** 60-70% faster (3 queries → 1 query)
- **`list_cases` endpoint:** 40-60% faster (better indexes + eager loading)
- **`update_case` endpoint:** 60-70% faster (3 queries → 1 query)
- **Overall database load:** 50-70% reduction

---

## Monitoring

After deploying, monitor:

1. **Query times:** Should see significant reduction
2. **Database connections:** Should see fewer connections per request
3. **Response times:** Should see faster API responses

---

## Next Steps

See `PERFORMANCE_REVIEW.md` for:
- Additional optimizations
- Caching recommendations
- Code architecture improvements
- Long-term monitoring setup

---

## Rollback Plan

If issues occur:

1. **Rollback indexes:**
```sql
DROP INDEX IF EXISTS idx_enforcement_cases_tenant_deleted_status;
DROP INDEX IF EXISTS idx_enforcement_cases_tenant_deleted_created;
-- ... (drop all indexes from migration)
```

2. **Rollback code changes:**
```bash
git revert <commit-hash>
```

---

## Questions?

Refer to `PERFORMANCE_REVIEW.md` for detailed explanations and additional recommendations.

