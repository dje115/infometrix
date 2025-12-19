#!/usr/bin/env python3
"""
Enforcement API - Main Application Entry Point

This API handles sensitive enforcement/debt recovery domain operations.
Separate from Platform API for security isolation.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import os
from pathlib import Path

# Import shared package types (will be created)
# from packages.shared.types.tenant import TenantContext
# from packages.shared.types.auth import AuthClaims

app = FastAPI(
    title="Infometrix Enforcement API",
    description="API for EnforceSense module and enforcement operations",
    version="3.6.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS configuration
CORS_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3010",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3002",
    "http://127.0.0.1:3010",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include EnforceSense routes
app.include_router(enforcesense_routes.router)

# Include Debtor Portal routes
app.include_router(portal_routes.router)


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring and load balancers.
    """
    return {
        "status": "healthy",
        "service": "enforcement-api",
        "version": "3.6.0"
    }


@app.get("/")
async def root():
    """
    Root endpoint - API information.
    """
    return {
        "service": "Infometrix Enforcement API",
        "version": "3.6.0",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=True
    )

