# Testing Guide - Two-API Architecture

## Quick Start Testing

### 1. Start All Services

```bash
docker-compose up -d
```

### 2. Test Enforcement API

```bash
# Health check
curl http://localhost:8001/health

# Expected response:
# {"status":"healthy","service":"enforcement-api","version":"0.1.0"}
```

### 3. Test Portal Session Creation

```bash
# Create a portal session
curl -X POST http://localhost:8001/api/v1/portal/sessions \
  -H "Content-Type: application/json" \
  -H "X-Tenant-ID: <tenant-id>" \
  -d '{"case_id": "test-case-123"}'

# Expected response:
# {
#   "session_id": "...",
#   "token": "...",
#   "expires_at": "...",
#   "case_id": "test-case-123"
# }
```

### 4. Test Portal Case View

```bash
# Get case data (replace TOKEN with token from step 3)
curl http://localhost:8001/api/v1/portal/cases/test-case-123 \
  -H "Authorization: Bearer TOKEN" \
  -H "X-Tenant-ID: <tenant-id>"
```

### 5. Test Rate Limiting

```bash
# Try creating more than 5 sessions in a minute
for i in {1..6}; do
  curl -X POST http://localhost:8001/api/v1/portal/sessions \
    -H "Content-Type: application/json" \
    -H "X-Tenant-ID: <tenant-id>" \
    -d '{"case_id": "test-case-'$i'"}'
  echo ""
done

# 6th request should return 429 Too Many Requests
```

## Module Enablement Testing

### Test Module API

```bash
# Get enabled modules for current tenant
curl http://localhost:8000/api/v1/modules \
  -H "Cookie: access_token=..." \
  -H "X-CSRF-Token: ..."

# Should return only modules in tenant.enabled_modules
```

### Test Disabling a Module

```sql
-- Disable Helpdesk for a tenant
UPDATE tenants 
SET enabled_modules = '["crm"]'::jsonb 
WHERE slug = 'your-tenant-slug';
```

Then verify:
1. Helpdesk tab disappears from module switcher
2. Helpdesk routes return 403 Forbidden
3. Module API doesn't return Helpdesk

### Test Re-enabling a Module

```sql
-- Re-enable Helpdesk
UPDATE tenants 
SET enabled_modules = '["crm", "helpdesk"]'::jsonb 
WHERE slug = 'your-tenant-slug';
```

## Debtor Portal Testing

### 1. Start Debtor Portal

```bash
cd apps/debtor-portal
npm install
npm run dev
```

Or via Docker:
```bash
docker-compose up -d debtor-portal
```

### 2. Test Language Switching

1. Open http://localhost:3002
2. Click language selector (top right)
3. Switch between English, Romanian, Czech
4. Verify all UI text changes

### 3. Test Login Flow

1. Enter any access code (placeholder)
2. Click "Continue"
3. Should navigate to case view
4. Verify localized labels

## Integration Testing

### End-to-End Portal Flow

1. **Create Session via API:**
   ```bash
   SESSION=$(curl -X POST http://localhost:8001/api/v1/portal/sessions \
     -H "Content-Type: application/json" \
     -H "X-Tenant-ID: <tenant-id>" \
     -d '{"case_id": "test-case-123"}' | jq -r '.token')
   ```

2. **Use Token in Portal:**
   - Open browser console on http://localhost:3002
   - Set token: `sessionStorage.setItem('portal_token', '<TOKEN>')`
   - Navigate to `/case/test-case-123`
   - Verify case data loads

### Test Redis Session Storage

```bash
# Check Redis for stored sessions
docker-compose exec redis redis-cli
> KEYS portal_session:*
> KEYS portal_token:*
> GET portal_session:<session-id>
```

## Performance Testing

### Rate Limiting

```bash
# Test session creation rate limit (5/min)
ab -n 10 -c 2 -p session.json -T application/json \
  -H "X-Tenant-ID: <tenant-id>" \
  http://localhost:8001/api/v1/portal/sessions

# Test case view rate limit (30/min)
ab -n 35 -c 5 -H "Authorization: Bearer <token>" \
  -H "X-Tenant-ID: <tenant-id>" \
  http://localhost:8001/api/v1/portal/cases/test-case-123
```

## Security Testing

### Test Token Validation

```bash
# Invalid token
curl http://localhost:8001/api/v1/portal/cases/test-case-123 \
  -H "Authorization: Bearer invalid-token"

# Should return 401 Unauthorized
```

### Test Tenant Isolation

```bash
# Try accessing case from different tenant
# Should return 403 Forbidden
```

### Test Expired Sessions

```bash
# Manually expire a session in Redis
docker-compose exec redis redis-cli
> DEL portal_session:<session-id>
> DEL portal_token:<token>

# Try using expired token
# Should return 401 Unauthorized
```

## Troubleshooting

### Enforcement API Not Starting

```bash
# Check logs
docker-compose logs enforcement-api

# Common issues:
# - Redis connection failed: Check REDIS_URL
# - Port 8001 already in use: Change port in docker-compose.yml
```

### Portal Sessions Not Persisting

```bash
# Check Redis connection
docker-compose exec redis redis-cli PING

# Check if sessions are stored
docker-compose exec redis redis-cli KEYS portal_session:*
```

### Module Enablement Not Working

```bash
# Verify database migration applied
docker-compose exec postgres psql -U postgres -d ccs_quote_tool \
  -c "SELECT name, enabled_modules FROM tenants;"

# Check module API response
curl http://localhost:8000/api/v1/modules
```

## Test Checklist

- [ ] Enforcement API health endpoint works
- [ ] Portal session creation works
- [ ] Portal case view works with valid token
- [ ] Rate limiting works (429 on limit exceeded)
- [ ] Redis session storage works
- [ ] Token lookup is fast (uses index)
- [ ] Expired sessions are rejected
- [ ] Module enablement works
- [ ] Module disablement works
- [ ] Debtor Portal loads
- [ ] Language switching works
- [ ] All UI strings translated
- [ ] End-to-end portal flow works

