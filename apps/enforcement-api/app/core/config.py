#!/usr/bin/env python3
"""
Configuration for Enforcement API
"""

from pydantic_settings import BaseSettings
from typing import List, Optional


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    APP_NAME: str = "Infometrix Enforcement API"
    APP_VERSION: str = "3.6.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    
    # Database (shared with Platform API for now)
    DATABASE_URL: str = "postgresql://postgres:postgres_password_2025@postgres:5432/ccs_quote_tool"
    
    # Redis (shared with Platform API for now)
    REDIS_URL: str = "redis://redis:6379/0"
    
    # Security (must match Platform API for shared JWT tokens)
    SECRET_KEY: str = "ccs_super_secret_key_2025_change_in_production"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # CORS
    CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3010",
    ]
    
    # API Keys (for AI features)
    OPENAI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

