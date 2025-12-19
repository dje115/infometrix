#!/usr/bin/env python3
"""
Database configuration for Enforcement API

Uses shared database with Platform API (same PostgreSQL instance).
"""

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import text
from typing import AsyncGenerator
from pathlib import Path

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


async def init_db():
    """
    Initialize database - create tables if they don't exist.
    Runs migration scripts to create EnforceSense tables and portal_sessions.
    """
    migrations = [
        ("create_enforcesense_tables.sql", "debtors"),
        ("add_portal_sessions_table.sql", "portal_sessions")
    ]
    
    for migration_file, check_table in migrations:
        migration_path = Path(__file__).parent.parent.parent / "migrations" / migration_file
        
        if not migration_path.exists():
            print(f"⚠️  Warning: Migration script not found at {migration_path}")
            continue
        
        try:
            async with async_engine.connect() as conn:
                # Check if table already exists
                result = await conn.execute(text(f"""
                    SELECT EXISTS (
                        SELECT FROM information_schema.tables 
                        WHERE table_name = '{check_table}'
                    )
                """))
                table_exists = result.scalar()
                
                if not table_exists:
                    print(f"📦 Running migration: {migration_file}...")
                    with open(migration_path, 'r') as f:
                        migration_sql = f.read()
                    
                    # Execute migration (split by semicolons for multiple statements)
                    statements = [s.strip() for s in migration_sql.split(';') if s.strip() and not s.strip().startswith('--')]
                    
                    for statement in statements:
                        if statement:
                            try:
                                await conn.execute(text(statement))
                            except Exception as e:
                                # Some statements might fail if objects already exist (idempotent)
                                if "already exists" not in str(e).lower() and "duplicate" not in str(e).lower():
                                    print(f"⚠️  Warning: Migration statement failed: {e}")
                    
                    await conn.commit()
                    print(f"✅ Migration {migration_file} completed successfully.")
                else:
                    print(f"✅ Table {check_table} already exists.")
        except Exception as e:
            print(f"❌ Error running migration {migration_file}: {e}")
            import traceback
            traceback.print_exc()

