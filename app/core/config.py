from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # App
    APP_NAME: str = "BYOM AI Platform"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost/byom_ai"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Encryption
    ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here"
    
    # CORS
    BACKEND_CORS_ORIGINS: list = ["http://localhost:3000", "http://localhost:8000"]
    
    # Google OAuth
    GOOGLE_CLIENT_ID: Optional[str] = None
    GOOGLE_CLIENT_SECRET: Optional[str] = None
    
    # Rate Limiting
    DEFAULT_RPM: int = 60
    DEFAULT_TPM: int = 10000
    DEFAULT_DAILY_CAP: int = 100000
    
    class Config:
        env_file = ".env"

settings = Settings()
