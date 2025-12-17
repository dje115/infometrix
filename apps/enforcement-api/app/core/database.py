"""
Database configuration for Enforcement API
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.core.config import settings

# TODO: Configure database connection
# For now, placeholder - will be configured when shared database is set up
Base = declarative_base()

# Database engine (placeholder)
engine = None
AsyncSessionLocal = None

async def init_db():
    """Initialize database connection"""
    global engine, AsyncSessionLocal
    
    if settings.DATABASE_URL:
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=settings.DEBUG,
            future=True
        )
        AsyncSessionLocal = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )


async def get_async_db():
    """Get database session"""
    if AsyncSessionLocal is None:
        await init_db()
    
    async with AsyncSessionLocal() as session:
        yield session

