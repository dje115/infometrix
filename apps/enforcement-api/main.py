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
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import EnforceSense module
from app.modules.enforcesense.module import EnforceSenseModule
from app.modules.enforcesense.routes import router as enforcesense_router
from app.modules.enforcesense.portal_routes import router as portal_router

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
    logger.info("Starting Enforcement API...")
    
    # Initialize Redis
    from app.core.redis import init_redis, close_redis
    await init_redis()
    
    # TODO: Initialize database connection
    
    # Register EnforceSense module routes
    app.include_router(enforcesense_router, prefix="/api/v1")
    
    # Register portal routes
    app.include_router(portal_router, prefix="/api/v1")
    
    logger.info("Enforcement API started successfully")
    
    yield
    
    # Shutdown
    await close_redis()
    logger.info("Shutting down Enforcement API...")


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

