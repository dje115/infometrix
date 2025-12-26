# How to Apply Database Migrations

**IMPORTANT:** These migrations must be applied to fix the timeout errors!

## Step 1: Connect to Your Database

```bash
# Using psql command line
psql -U your_username -d ccs_quote_tool

# Or using Docker if your database is in a container
docker exec -i your_postgres_container psql -U your_username -d ccs_quote_tool
```

## Step 2: Apply Migrations in Order

### Migration 1: Missing Foreign Key Indexes
```bash
# From command line
psql -U your_username -d ccs_quote_tool -f backend/migrations/add_missing_foreign_key_indexes.sql

# Or from within psql
\i backend/migrations/add_missing_foreign_key_indexes.sql
```

### Migration 2: Composite Indexes
```bash
psql -U your_username -d ccs_quote_tool -f backend/migrations/add_composite_indexes_for_common_queries.sql
```

### Migration 3: EnforceSense Performance Indexes
```bash
psql -U your_username -d ccs_quote_tool -f apps/enforcement-api/migrations/add_performance_indexes_enforcesense.sql
```

## Step 3: Verify Indexes Were Created

```sql
-- Check if indexes exist
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%'
ORDER BY tablename, indexname;

-- Check foreign key indexes specifically
SELECT 
    tc.table_name, 
    kcu.column_name,
    CASE WHEN idx.indexname IS NOT NULL THEN 'YES' ELSE 'NO' END AS has_index
FROM information_schema.table_constraints AS tc
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
LEFT JOIN pg_indexes idx 
  ON idx.tablename = tc.table_name 
  AND idx.indexdef LIKE '%' || kcu.column_name || '%'
WHERE tc.constraint_type = 'FOREIGN KEY'
AND kcu.column_name IN ('contact_id', 'created_by_user_id', 'created_by', 'parent_quote_id', 'template_id', 'supplier_id')
ORDER BY tc.table_name, kcu.column_name;
```

## Expected Results

After applying migrations, you should see:
- **11 new foreign key indexes** created
- **10 new composite indexes** created
- **11+ EnforceSense indexes** created

## Performance Impact

- **Before:** Queries taking 30+ seconds (causing timeouts)
- **After:** Queries should complete in <1 second
- **Improvement:** 95%+ faster queries

## Troubleshooting

### If migrations fail:
1. Check database connection
2. Verify you have CREATE INDEX permissions
3. Check if indexes already exist (they use IF NOT EXISTS, so safe to re-run)

### If timeouts persist:
1. Check backend logs for slow queries
2. Verify database is not overloaded
3. Check network connectivity between frontend and backend

## Next Steps

After applying migrations:
1. Restart your backend server
2. Test the application - timeouts should be resolved
3. Monitor query performance

