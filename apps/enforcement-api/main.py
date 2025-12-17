#!/usr/bin/env python3
"""
Enforcement API - Infometrix Platform
Separate API service for sensitive enforcement/debt recovery domain
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn
import os

# Import shared types (will be created)
# from packages.shared.types.tenant import TenantContext
# from packages.shared.types.auth import AuthClaims

# Create FastAPI app
app = FastAPI(
    title="Infometrix Enforcement API",
    description="API for EnforceSense module and debt recovery operations",
    version="0.1.0"
)

# CORS configuration (adjust for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3002"],  # Frontend and Debtor Portal
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    print("Starting Enforcement API...")
    
    # TODO: Initialize database connection
    # TODO: Initialize Redis if needed
    # TODO: Register modules
    
    yield
    
    # Shutdown
    print("Shutting down Enforcement API...")


app.router.lifespan_context = lifespan


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "enforcement-api",
        "version": "0.1.0"
    }


if __name__ == "__main__":
    port = int(os.getenv("ENFORCEMENT_API_PORT", "8001"))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )

