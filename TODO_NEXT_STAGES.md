# TODO List - Next Stages

**Last Updated:** 2025-12-18  
**Current Status:** Migration Complete, Infrastructure Ready

## Stage 1: Core Functionality (High Priority)

### Authentication & Authorization
- [ ] **Implement real JWT authentication in Enforcement API**
  - Replace placeholder dependencies with actual JWT validation
  - Validate token signature and expiry
  - Extract user claims from token
  
- [ ] **Add tenant resolution from JWT claims**
  - Extract tenant_id from token
  - Validate tenant exists and is active
  - Set tenant context for request

### Database Integration
- [ ] **Connect Enforcement API to PostgreSQL database**
  - Configure database connection
  - Test connectivity
  - Set up connection pooling

- [ ] **Create database tables for enforcement_cases and debtor_parties**
  - Write migration scripts
  - Apply migrations
  - Verify table structure

- [ ] **Implement actual database queries for cases**
  - Replace placeholder GET /cases endpoint
  - Add filtering, pagination, sorting
  - Implement tenant-scoped queries

- [ ] **Implement actual database queries for debtors**
  - Replace placeholder GET /debtors/:id endpoint
  - Add debtor search functionality
  - Implement tenant-scoped queries

## Stage 2: Security & Reliability (High Priority)

### Permissions & Access Control
- [ ] **Add permission checks for EnforceSense endpoints**
  - Implement RBAC for enforce:read, enforce:write
  - Add permission validation middleware
  - Test permission enforcement

### Error Handling
- [ ] **Add comprehensive error responses**
  - Standardize error format across all endpoints
  - Add error codes and messages
  - Include request IDs for tracing

- [ ] **Implement error recovery mechanisms**
  - Add retry logic for Redis operations
  - Handle transient failures gracefully
  - Add circuit breaker pattern

- [ ] **Add fallback mechanisms**
  - Handle Redis unavailability gracefully
  - Handle database unavailability
  - Degrade functionality rather than fail completely

## Stage 3: Documentation (Medium Priority)

- [ ] **Add OpenAPI/Swagger documentation for Enforcement API**
  - Document all endpoints with request/response schemas
  - Add authentication requirements
  - Include example requests

- [ ] **Document portal endpoints**
  - Add API documentation for portal session endpoints
  - Document case viewing endpoints
  - Include rate limit information

- [ ] **Add example requests/responses**
  - Include curl examples for all endpoints
  - Add response schema documentation
  - Include error response examples

- [ ] **Document rate limits**
  - Add rate limit information to API documentation
  - Document rate limit headers
  - Include rate limit error responses

## Stage 4: Observability (Medium Priority)

- [ ] **Add application metrics (Prometheus)**
  - Instrument endpoints with metrics
  - Track request counts, latencies, errors
  - Expose metrics endpoint

- [ ] **Add distributed tracing**
  - Implement request tracing across services
  - Add trace IDs to logs
  - Integrate with tracing system (Jaeger, Zipkin)

- [ ] **Set up log aggregation**
  - Configure centralized logging (ELK, Loki, etc.)
  - Set up log shipping
  - Configure log retention

- [ ] **Add health check endpoints for dependencies**
  - Check Redis connectivity
  - Check database connectivity
  - Return detailed health status

## Stage 5: Testing (Medium Priority)

- [ ] **Add unit tests for portal routes**
  - Test session creation logic
  - Test case viewing logic
  - Test rate limiting logic

- [ ] **Add integration tests**
  - Test end-to-end portal flow with real Redis
  - Test database operations
  - Test authentication flow

- [ ] **Add E2E tests for debtor portal**
  - Test login flow
  - Test case view
  - Test language switching

- [ ] **Add load testing**
  - Test rate limiting under load
  - Test session creation under load
  - Identify performance bottlenecks

## Stage 6: Testing & Verification (Immediate)

- [ ] **Set up Debtor Portal for development**
  - Run npm install in apps/debtor-portal
  - Start dev server
  - Verify it runs on port 3002

- [ ] **Test Debtor Portal end-to-end**
  - Verify login flow works
  - Test case viewing
  - Test language switching (en/ro/cs)

- [ ] **Test module enablement/disablement**
  - Disable Helpdesk module for a tenant
  - Verify module switcher updates
  - Verify routes return 403
  - Re-enable and verify it works again

## Stage 7: Production Infrastructure (High Priority)

- [ ] **Configure production environment variables**
  - Set up secrets management (Vault, AWS Secrets Manager, etc.)
  - Configure all required environment variables
  - Document environment variable requirements

- [ ] **Configure database backups**
  - Set up automated backup strategy
  - Configure backup retention
  - Test backup restoration

- [ ] **Enable Redis persistence**
  - Configure Redis for production durability
  - Set up Redis replication
  - Configure Redis failover

- [ ] **Configure load balancer**
  - Set up reverse proxy/API gateway
  - Configure routing rules
  - Set up SSL termination

- [ ] **Install SSL/TLS certificates**
  - Configure HTTPS for all services
  - Set up certificate auto-renewal
  - Enforce HTTPS redirects

## Stage 8: Security Hardening (High Priority)

- [ ] **Complete security audit**
  - Review authentication mechanisms
  - Review authorization checks
  - Review rate limiting implementation
  - Review input validation

- [ ] **Change default SECRET_KEY**
  - Generate strong secret keys
  - Configure in production environment
  - Rotate keys periodically

- [ ] **Configure CORS properly**
  - Set up production CORS policies
  - Whitelist allowed origins
  - Remove development CORS settings

- [ ] **Set up WAF rules**
  - Configure web application firewall
  - Set up protection rules
  - Monitor and tune rules

- [ ] **Enable DDoS protection**
  - Configure protection for public endpoints
  - Set up rate limiting at network level
  - Monitor for attacks

## Stage 9: Monitoring & Alerting (Medium Priority)

- [ ] **Set up monitoring**
  - Configure Prometheus, Grafana, or similar
  - Set up dashboards
  - Configure metric collection

- [ ] **Configure alerting rules**
  - Set up alerts for errors
  - Set up alerts for rate limit violations
  - Set up alerts for service downtime
  - Configure alert channels (email, Slack, PagerDuty)

- [ ] **Enable uptime monitoring**
  - Set up external monitoring service
  - Configure health check endpoints
  - Set up status page

- [ ] **Set up error tracking**
  - Configure Sentry or similar error tracking
  - Set up error notifications
  - Configure error grouping and deduplication

## Stage 10: Advanced Features (Low Priority)

- [ ] **Implement event/outbox pattern**
  - Add event publishing system
  - Implement outbox pattern for reliability
  - Add event consumers

- [ ] **Add Account updated events**
  - Publish events when accounts change in Platform API
  - Subscribe to events in Enforcement API
  - Update case references when accounts change

- [ ] **Add Case status changed events**
  - Publish events for case state changes
  - Allow other services to react to changes
  - Maintain event history

## Stage 11: Infrastructure Enhancements (Low Priority)

- [ ] **Add API gateway/reverse proxy**
  - Configure routing between services
  - Set up SSL termination
  - Add request logging and monitoring
  - Implement API versioning

- [ ] **Consider separate databases per API (optional)**
  - Evaluate full isolation strategy
  - Plan data sync if needed
  - Implement if beneficial

- [ ] **Create Client Portal**
  - Design client-facing portal
  - Implement authentication
  - Add client-specific features

- [ ] **Add webhook support**
  - Allow external systems to subscribe to events
  - Implement webhook delivery
  - Add webhook management UI

## Stage 12: Performance Optimization (Low Priority)

- [ ] **Add caching layer for case data**
  - Cache frequently accessed case information
  - Implement cache invalidation
  - Monitor cache hit rates

- [ ] **Optimize database queries**
  - Add indexes for common queries
  - Optimize slow queries
  - Add query performance monitoring

- [ ] **Tune connection pooling**
  - Optimize database connection pools
  - Optimize Redis connection pools
  - Monitor connection usage

- [ ] **Set up CDN for static assets**
  - Configure CDN for debtor portal assets
  - Optimize asset delivery
  - Monitor CDN performance

## Priority Summary

### 🔴 Critical (Do First)
- Stage 1: Core Functionality (Authentication, Database)
- Stage 7: Production Infrastructure
- Stage 8: Security Hardening

### 🟡 Important (Do Soon)
- Stage 2: Security & Reliability
- Stage 6: Testing & Verification
- Stage 9: Monitoring & Alerting

### 🟢 Nice to Have (Do Later)
- Stage 3: Documentation
- Stage 4: Observability
- Stage 5: Testing
- Stage 10: Advanced Features
- Stage 11: Infrastructure Enhancements
- Stage 12: Performance Optimization

## Notes

- Tasks are organized by logical stages
- Each stage can be worked on independently
- Some tasks have dependencies (noted in descriptions)
- Priority levels are suggestions - adjust based on business needs
- All infrastructure work (Stages 1-2, 7-8) should be completed before production deployment

