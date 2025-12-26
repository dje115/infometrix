# Deployment Verification Guide

**Date:** 2025-01-27  
**Purpose:** Verify all performance fixes are properly applied after deployment

---

## 🎯 Quick Verification

### Option 1: Automated Script (Recommended)

**Windows PowerShell:**
```powershell
.\scripts\verify_deployment.ps1
```

**Linux/Mac:**
```bash
chmod +x scripts/verify_deployment.sh
./scripts/verify_deployment.sh
```

### Option 2: Manual Verification

Follow the steps below to manually verify deployment.

---

## 📋 Verification Checklist

### 1. Docker Containers Status ✅

```bash
# Check if containers are running
docker ps | grep infometrix

# Expected output:
# infometrix-backend
# infometrix-postgres
# infometrix-frontend
# infometrix-redis
```

**✅ Pass:** All containers show "Up" status  
**❌ Fail:** Any container shows "Exited" or missing

---

### 2. Database Indexes ✅

```bash
# Connect to PostgreSQL
docker exec -it infometrix-postgres psql -U postgres -d ccs_quote_tool

# Check foreign key indexes
SELECT COUNT(*) FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%' 
AND (indexname LIKE '%_contact_id%' 
     OR indexname LIKE '%_created_by%' 
     OR indexname LIKE '%_supplier_id%');

# Expected: At least 5 indexes

# Check composite indexes
SELECT COUNT(*) FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname LIKE 'idx_%' 
AND (indexname LIKE '%_tenant_%' 
     OR indexname LIKE '%_customer_%' 
     OR indexname LIKE '%_status%');

# Expected: At least 5 indexes

# Check EnforceSense indexes
SELECT COUNT(*) FROM pg_indexes 
WHERE schemaname = 'public' 
AND (indexname LIKE '%debtor%' 
     OR indexname LIKE '%enforcement%' 
     OR indexname LIKE '%case%' 
     OR indexname LIKE '%ledger%');

# Expected: At least 5 indexes
```

**✅ Pass:** All index counts meet expectations  
**❌ Fail:** Index counts are significantly lower

---

### 3. Backend Health Check ✅

```bash
# Check backend health endpoint
curl http://localhost:8000/health

# Expected: {"status":"healthy"} or similar
```

**✅ Pass:** Backend responds with 200 status  
**❌ Fail:** Backend doesn't respond or returns error

---

### 4. Migration Logs ✅

```bash
# Check backend logs for migration messages
docker logs infometrix-backend | grep -i "migration\|index"

# Expected output should include:
# - "Applying Performance Migrations..."
# - "Missing Foreign Key Indexes"
# - "Composite Indexes for Common Queries"
# - "EnforceSense Performance Indexes"
# - "Migrations completed!"
```

**✅ Pass:** Migration messages found in logs  
**⚠️  Note:** If migrations already applied, logs may not show new messages (this is OK)

---

### 5. Frontend Error Handling ✅

**Manual Test:**
1. Open browser and navigate to `http://localhost:3000`
2. Log in to the application
3. Navigate to **Customers** page
4. Verify:
   - ✅ Page loads without timeout errors
   - ✅ Loading indicator appears during data fetch
   - ✅ If error occurs, error message displays with retry button

**Test Error Handling:**
1. Open browser DevTools (F12)
2. Go to Network tab
3. Enable "Offline" mode
4. Navigate to Customers page
5. Verify:
   - ✅ Error message displays
   - ✅ Retry button is visible
   - ✅ Error message is user-friendly

**✅ Pass:** Error handling works correctly  
**❌ Fail:** No error messages or retry buttons

---

### 6. API Performance Test ✅

```bash
# Test customer list endpoint
time curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/v1/customers/

# Expected: Response time < 2 seconds
```

**✅ Pass:** Response time < 2 seconds  
**❌ Fail:** Response time > 5 seconds

---

### 7. Route Matching ✅

**Manual Test:**
1. Open browser DevTools Console (F12)
2. Navigate through the application:
   - Dashboard
   - Customers
   - Leads
   - Opportunities
3. Check console for warnings:
   - ✅ No "No routes matched location" warnings
   - ✅ No React Router errors

**✅ Pass:** No route warnings in console  
**❌ Fail:** Route warnings appear

---

## 🔍 Detailed Verification

### Check Specific Indexes

```sql
-- Verify foreign key indexes exist
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname IN (
    'idx_customer_interactions_contact_id',
    'idx_tickets_created_by_user_id',
    'idx_quotes_created_by',
    'idx_quotes_parent_quote_id',
    'idx_quotes_template_id',
    'idx_quote_items_supplier_id'
);

-- Expected: 6 indexes

-- Verify composite indexes exist
SELECT indexname, tablename 
FROM pg_indexes 
WHERE schemaname = 'public' 
AND indexname IN (
    'idx_customers_tenant_status',
    'idx_customers_tenant_status_deleted',
    'idx_quotes_tenant_customer_status',
    'idx_tickets_tenant_customer_status'
);

-- Expected: At least 4 indexes
```

---

### Check Backend Logs

```bash
# View recent backend logs
docker logs --tail 100 infometrix-backend

# Look for:
# - "Starting Infometrix Backend..."
# - "PostgreSQL is ready!"
# - "Applying Performance Migrations..."
# - "Migrations completed!"
# - "Starting application..."
```

---

### Check Frontend Build

```bash
# Check frontend container logs
docker logs --tail 50 infometrix-frontend

# Look for:
# - No build errors
# - Server started successfully
# - No TypeScript errors
```

---

## 🐛 Troubleshooting

### Issue: Migrations Not Applied

**Symptoms:**
- Indexes don't exist in database
- Backend logs show no migration messages

**Solution:**
```bash
# Manually apply migrations
.\scripts\apply_migrations_docker.ps1

# Or restart backend container
docker-compose restart backend
```

---

### Issue: Backend Not Responding

**Symptoms:**
- Health check fails
- Frontend shows connection errors

**Solution:**
```bash
# Check backend logs
docker logs infometrix-backend

# Restart backend
docker-compose restart backend

# Check if port 8000 is available
netstat -an | findstr :8000
```

---

### Issue: Frontend Errors

**Symptoms:**
- Error messages don't display
- Retry buttons missing

**Solution:**
```bash
# Rebuild frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# Check frontend logs
docker logs infometrix-frontend
```

---

### Issue: Database Connection Errors

**Symptoms:**
- Backend can't connect to database
- Migration errors

**Solution:**
```bash
# Check PostgreSQL is running
docker ps | grep postgres

# Check database connection
docker exec -it infometrix-postgres psql -U postgres -d ccs_quote_tool -c "SELECT 1;"

# Restart PostgreSQL if needed
docker-compose restart postgres
```

---

## ✅ Success Criteria

All of the following must be true:

- [x] All Docker containers are running
- [x] At least 15+ indexes exist in database
- [x] Backend health check returns 200
- [x] Frontend loads without errors
- [x] Error handling works (test with offline mode)
- [x] API responses are fast (< 2 seconds)
- [x] No route warnings in browser console
- [x] Migrations applied successfully (check logs)

---

## 📊 Performance Benchmarks

### Expected Performance After Fixes:

| Operation | Before | After | Improvement |
|-----------|--------|-------|-------------|
| Customer List | 30+ sec | <1 sec | 95%+ faster |
| Foreign Key Lookup | 2-5 sec | <0.5 sec | 80%+ faster |
| Composite Query | 5-10 sec | <1 sec | 90%+ faster |
| Error Display | N/A | Instant | New feature |

---

## 🎯 Next Steps After Verification

1. **Monitor Performance**
   - Check backend logs for slow queries
   - Monitor API response times
   - Track error rates

2. **User Testing**
   - Have users test the application
   - Collect feedback on performance
   - Monitor for any issues

3. **Documentation**
   - Update deployment docs if needed
   - Document any issues found
   - Update runbooks

---

## 📞 Support

If verification fails:

1. Check the troubleshooting section above
2. Review backend logs: `docker logs infometrix-backend`
3. Review frontend logs: `docker logs infometrix-frontend`
4. Check database logs: `docker logs infometrix-postgres`
5. Run verification script: `.\scripts\verify_deployment.ps1`

---

**Last Updated:** 2025-01-27  
**Status:** Ready for Use

