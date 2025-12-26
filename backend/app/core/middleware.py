#!/usr/bin/env python3
"""
Custom middleware for CCS Quote Tool v2
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
import time
import logging
from typing import Optional, Dict
from functools import lru_cache
from app.core.config import settings

logger = logging.getLogger(__name__)

# Tenant cache (in-memory, cleared on restart)
# Format: {tenant_slug_or_id: tenant_id}
_tenant_cache: Dict[str, str] = {}
_cache_lock = None  # Will be initialized as asyncio.Lock if needed


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract tenant information from requests for PUBLIC routes only.
    
    SECURITY: For authenticated routes, tenant MUST come from JWT token (via get_current_user).
    This middleware only handles public routes (like /auth/login) where we need to identify
    the tenant from subdomain or header, but we validate the tenant exists in the database.
    
    PERFORMANCE: Tenant lookups are cached to avoid blocking database queries on every request.
    Cache is invalidated when tenant is not found (to allow for new tenant creation).
    
    For authenticated routes, use get_current_tenant() dependency which enforces
    tenant comes from JWT and rejects any header/subdomain mismatch.
    """
    
    async def dispatch(self, request: Request, call_next):
        # Skip tenant processing entirely for endpoints that don't need tenant context
        # Version, health, and root endpoints don't need tenant validation
        path = request.url.path
        
        # Normalize path (remove trailing slashes for comparison)
        normalized_path = path.rstrip('/')
        
        # Check if this is a route that should skip tenant processing
        # Handle both with and without query strings
        path_without_query = path.split('?')[0] if '?' in path else path
        normalized_path_no_query = path_without_query.rstrip('/')
        
        skip_tenant_routes = (
            normalized_path == "/api/v1/version" or
            normalized_path_no_query == "/api/v1/version" or
            path == "/api/v1/version" or
            path_without_query == "/api/v1/version" or
            path.startswith("/api/v1/version") or  # This will match /version, /version/, /version?query
            path.startswith("/api/v1/ws") or  # WebSocket endpoint - handles auth internally
            path.startswith("/health") or
            normalized_path == "/" or
            path == "/"
        )
        
        if skip_tenant_routes:
            # These endpoints don't need tenant context at all - skip all tenant processing
            logger.debug(f"Skipping tenant processing for path: {path}")
            response = await call_next(request)
            return response
        
        # Only set tenant for *unauthenticated* routes that truly need tenant context.
        # Authenticated routes derive tenant from JWT in dependencies (get_current_user/get_current_tenant).
        # Public endpoints like CSRF token and /auth/me should NOT require X-Tenant-ID.
        path_for_public_check = normalized_path_no_query
        public_tenant_required_routes = {
            "/api/v1/auth/login",
            "/api/v1/auth/passwordless/request",
        }
        is_public_route = path_for_public_check in public_tenant_required_routes
        
        tenant_id = None
        
        if is_public_route:
            # For public routes, allow subdomain or header-based tenant detection
            # but we'll validate it exists in the database
            
            # Try to get tenant from header (case-insensitive)
            provided_tenant = request.headers.get("X-Tenant-ID") or request.headers.get("x-tenant-id")
            
            # Debug: log all headers for troubleshooting
            if not provided_tenant:
                logger.debug(f"X-Tenant-ID header not found. Available headers: {list(request.headers.keys())}")
            
            # Try to get tenant from subdomain
            if not provided_tenant:
                host = request.headers.get("host", "")
                if "." in host:
                    subdomain = host.split(".")[0]
                    if subdomain and subdomain not in ["www", "api", "localhost"]:
                        provided_tenant = subdomain
            
            # Require tenant identifier for all environments (dev and production)
            if not provided_tenant:
                logger.warning(f"Public route accessed without tenant identifier: {request.url.path}. Headers: {dict(request.headers)}")
                raise HTTPException(
                    status_code=400,
                    detail="Tenant identifier required (X-Tenant-ID header or subdomain)"
                )
            
            # Check cache first (performance optimization)
            if provided_tenant in _tenant_cache:
                tenant_id = _tenant_cache[provided_tenant]
            else:
                # Validate tenant exists (for public routes) - use async to avoid blocking
                # This prevents tenant impersonation even on public routes
                from app.core.database import async_engine
                from app.models.tenant import Tenant
                from sqlalchemy import select
                from sqlalchemy.ext.asyncio import AsyncSession
                
                async with AsyncSession(async_engine) as session:
                    try:
                        # Query tenant by slug or ID
                        stmt = select(Tenant).where(
                            (Tenant.slug == provided_tenant) | (Tenant.id == provided_tenant)
                        )
                        result = await session.execute(stmt)
                        tenant = result.scalar_one_or_none()
                        
                        if tenant:
                            tenant_id = tenant.id  # Use actual tenant ID, not slug
                            # Cache the mapping (both slug and ID map to tenant ID)
                            _tenant_cache[provided_tenant] = tenant_id
                            if tenant.slug and tenant.slug != tenant.id:
                                _tenant_cache[tenant.slug] = tenant_id
                            if tenant.id != provided_tenant:
                                _tenant_cache[tenant.id] = tenant_id
                            logger.debug(f"Tenant '{provided_tenant}' resolved to tenant_id: {tenant_id}")
                        else:
                            # Tenant doesn't exist - reject for all environments
                            logger.warning(f"Unknown tenant '{provided_tenant}' attempted access to {request.url.path}")
                            raise HTTPException(
                                status_code=404,
                                detail=f"Tenant '{provided_tenant}' not found"
                            )
                    except HTTPException:
                        raise
                    except Exception as e:
                        logger.error(f"Error validating tenant '{provided_tenant}': {e}", exc_info=True)
                        raise HTTPException(
                            status_code=500,
                            detail="Error validating tenant"
                        )
        
        # Store tenant in request state (will be None for authenticated routes until JWT is validated)
        request.state.tenant_id = tenant_id
        request.state.db_tenant_id = tenant_id
        
        response = await call_next(request)
        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests and responses
    """
    
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        
        # Log request
        logger.info(f"Request: {request.method} {request.url.path}")
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate processing time
            process_time = time.time() - start_time
            
            # Add custom header
            response.headers["X-Process-Time"] = str(process_time)
            
            # Log response
            logger.info(
                f"Response: {request.method} {request.url.path} "
                f"Status: {response.status_code} "
                f"Time: {process_time:.3f}s"
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request: {e}")
            raise


class RateLimitMiddleware(BaseHTTPMiddleware):
    """
    Rate limiting middleware using Redis
    
    PERFORMANCE: Uses Redis for distributed rate limiting across multiple workers.
    Rate limits are enforced per IP address with automatic expiration.
    
    SECURITY: Prevents abuse and DoS attacks by limiting request frequency.
    """
    
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.window_seconds = 60  # 1 minute window
    
    async def dispatch(self, request: Request, call_next):
        # Get client IP
        client_ip = request.client.host if request.client else "unknown"
        
        # Skip rate limiting for health checks and static files
        if request.url.path in ["/health", "/metrics", "/favicon.ico"]:
            response = await call_next(request)
            return response
        
        # Use Redis for rate limiting (distributed, process-safe)
        try:
            import redis
            sync_redis = redis.from_url(
                settings.REDIS_URL,
                encoding="utf-8",
                decode_responses=True
            )
            
            # Rate limit key: format: "rate_limit:{ip}:{window}"
            current_window = int(time.time() / self.window_seconds)
            rate_limit_key = f"rate_limit:{client_ip}:{current_window}"
            
            # Increment counter with expiration
            # This atomically increments and sets expiration if key doesn't exist
            count = sync_redis.incr(rate_limit_key)
            if count == 1:
                # First request in this window - set expiration
                sync_redis.expire(rate_limit_key, self.window_seconds + 10)  # Add 10s buffer
            
            # Check if limit exceeded
            if count > self.requests_per_minute:
                logger.warning(
                    f"Rate limit exceeded for IP {client_ip}: {count} requests in {self.window_seconds}s"
                )
                raise HTTPException(
                    status_code=429,
                    detail=f"Too many requests. Limit: {self.requests_per_minute} requests per minute"
                )
            
        except redis.exceptions.ConnectionError:
            # Redis not available - log warning but allow request (fail open)
            logger.warning("Redis not available for rate limiting, allowing request")
        except Exception as e:
            # Error in rate limiting - log but allow request (fail open)
            logger.error(f"Error in rate limiting: {e}", exc_info=True)
        
        response = await call_next(request)
        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Security headers middleware to add security-related HTTP headers
    
    SECURITY: Implements security best practices by adding headers that:
    - Prevent XSS attacks (X-XSS-Protection, CSP)
    - Prevent clickjacking (X-Frame-Options)
    - Enforce HTTPS (HSTS)
    - Prevent MIME type sniffing (X-Content-Type-Options)
    """
    
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # HSTS - only in production with HTTPS
        if settings.ENVIRONMENT == "production":
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        # Content Security Policy
        # Allow same-origin, inline scripts/styles from trusted sources
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "  # unsafe-eval needed for some libraries
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self' data:; "
            "connect-src 'self' https:; "
            "frame-ancestors 'none'; "
            "base-uri 'self'; "
            "form-action 'self'"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy (formerly Feature Policy)
        response.headers["Permissions-Policy"] = (
            "geolocation=(), "
            "microphone=(), "
            "camera=(), "
            "payment=(), "
            "usb=()"
        )
        
        return response

