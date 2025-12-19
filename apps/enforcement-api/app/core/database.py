#!/usr/bin/env python3
"""
Database configuration for Enforcement API

Uses shared database with Platform API (same PostgreSQL instance).
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.core.config import settings

# Create async engine
async_engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Base class for models
Base = declarative_base()


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Get async database session.
    """
    async with AsyncSessionLocal() as session:
        yield session


async def close_db():
    """Close database connections"""
    await async_engine.dispose()

