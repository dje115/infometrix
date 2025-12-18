# Next Steps - Two-API Architecture Migration

## Immediate Actions

### 1. Apply Database Migration
The migration file has been created but needs to be applied:

```bash
# Option 1: Apply via docker-compose
docker-compose exec postgres psql -U postgres -d ccs_quote_tool -f /path/to/add_tenant_enabled_modules.sql

# Option 2: Apply manually
psql -U postgres -d ccs_quote_tool -f backend/migrations/add_tenant_enabled_modules.sql
```

### 2. Test New Services

#### Enforcement API
```bash
# Start service
docker-compose up -d enforcement-api

# Test health endpoint
curl http://localhost:8001/health

# Expected response:
# {"status":"healthy","service":"enforcement-api","version":"0.1.0"}
```

#### Debtor Portal
```bash
# Start service (requires npm install first)
cd apps/debtor-portal
npm install
npm run dev

# Or via docker-compose
docker-compose up -d debtor-portal

# Open in browser: http://localhost:3002
```

### 3. Verify Module Enablement

```bash
# Check tenant enabled_modules
docker-compose exec postgres psql -U postgres -d ccs_quote_tool -c "SELECT id, name, enabled_modules FROM tenants;"

# Test disabling a module (via admin portal or direct DB update)
# Then verify module API returns only enabled modules
curl http://localhost:8000/api/v1/modules
```

## Integration Testing

### Test Module Switcher
1. Log into frontend (http://localhost:3000)
2. Verify module switcher shows CRM and Helpdesk tabs
3. Switch between modules
4. Verify context menu updates

### Test Module Enablement
1. Disable Helpdesk for a tenant:
   ```sql
   UPDATE tenants SET enabled_modules = '["crm"]'::jsonb WHERE slug = 'your-tenant-slug';
   ```
2. Verify Helpdesk tab disappears from module switcher
3. Verify Helpdesk routes return 403

### Test Debtor Portal Flow
1. Open http://localhost:3002
2. Test language switching (en/ro/cs)
3. Enter access code (placeholder - will need real implementation)
4. Verify case view loads with localized labels

## Production Readiness Tasks

### High Priority

1. **Move Portal Sessions to Database/Redis**
   - Current: In-memory storage (lost on restart)
   - Target: Redis or database table
   - File: `apps/enforcement-api/app/modules/enforcesense/portal_routes.py`

2. **Implement Real Authentication**
   - Current: Placeholder dependencies
   - Target: JWT validation, tenant resolution
   - Files: `apps/enforcement-api/app/core/dependencies.py`

3. **Add Rate Limiting**
   - Portal endpoints need rate limiting
   - Use FastAPI rate limiting middleware
   - File: `apps/enforcement-api/app/modules/enforcesense/portal_routes.py`

4. **Database Models Implementation**
   - Current: Placeholder models
   - Target: Real database queries
   - Files: `apps/enforcement-api/app/modules/enforcesense/routes.py`

### Medium Priority

5. **Error Handling**
   - Comprehensive error responses
   - Proper HTTP status codes
   - User-friendly error messages

6. **Logging & Monitoring**
   - Structured logging
   - Request/response logging
   - Error tracking

7. **API Documentation**
   - OpenAPI/Swagger docs for Enforcement API
   - Document portal endpoints

### Low Priority (Phase 2)

8. **Event/Outbox Pattern**
   - Inter-service communication
   - Account updated events
   - Case status changed events

9. **API Gateway**
   - Reverse proxy for routing
   - SSL/TLS termination
   - Request logging

10. **Separate Databases** (Optional)
    - Full isolation between APIs
    - Requires data sync strategy

## Code Quality Improvements

1. **Type Safety**
   - Add Pydantic models for all requests/responses
   - Type hints throughout Enforcement API

2. **Testing**
   - Unit tests for module enablement
   - Integration tests for portal flow
   - E2E tests for debtor portal

3. **Documentation**
   - API documentation
   - Architecture diagrams
   - Deployment guides

## Deployment Checklist

Before deploying to production:

- [ ] Database migration applied
- [ ] All services tested locally
- [ ] Environment variables configured
- [ ] Portal sessions moved to persistent storage
- [ ] Rate limiting implemented
- [ ] Error handling comprehensive
- [ ] Logging configured
- [ ] Monitoring set up
- [ ] API documentation complete
- [ ] Security review completed
- [ ] Performance testing done

## Branch Management

Current branch: `infometrix-platform-migration`

### Option 1: Merge to Main
```bash
git checkout main
git merge infometrix-platform-migration
git push origin main
```

### Option 2: Create PR
- Push branch to remote
- Create pull request
- Review and merge

## Questions to Resolve

1. **Portal Session Storage**: Redis or database table?
2. **Authentication**: Reuse Platform API auth or separate system?
3. **Database**: Shared or separate for Enforcement API?
4. **Deployment**: Same cluster or separate services?
5. **Client Portal**: When to implement?

## Support

For issues or questions:
- Check `MIGRATION_COMPLETE.md` for architecture overview
- Review commit messages for detailed changes
- Check TODO comments in code for pending work

