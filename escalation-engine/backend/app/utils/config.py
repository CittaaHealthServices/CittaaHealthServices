"""
Configuration settings for CITTAA Escalation Engine
"""

from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """Application settings"""
    
    # Application
    APP_NAME: str = "CITTAA Escalation Engine"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://cittaa:password@localhost:5432/cittaa_escalation")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # JWT
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "cittaa-escalation-secret-key-change-in-production")
    JWT_ALGORITHM: str = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    
    # SendGrid
    SENDGRID_API_KEY: Optional[str] = os.getenv("SENDGRID_API_KEY")
    FROM_EMAIL: str = "escalations@cittaa.in"
    
    # AWS S3
    AWS_ACCESS_KEY_ID: Optional[str] = os.getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY: Optional[str] = os.getenv("AWS_SECRET_ACCESS_KEY")
    AWS_S3_BUCKET: str = os.getenv("AWS_S3_BUCKET", "cittaa-escalation-reports")
    AWS_REGION: str = os.getenv("AWS_REGION", "ap-south-1")
    
    # Encryption
    ENCRYPTION_KEY: str = os.getenv("ENCRYPTION_KEY", "default-encryption-key-change-in-production")
    
    # CITTAA Brand Colors
    CITTAA_PURPLE: str = "#8B5A96"
    CITTAA_TEAL: str = "#7BB3A8"
    WARM_GRAY: str = "#6B7280"
    
    # AI Model Settings
    AI_CONFIDENCE_THRESHOLD_EMERGENCY: float = 0.60
    AI_CONFIDENCE_THRESHOLD_HIGH: float = 0.70
    AI_CONFIDENCE_THRESHOLD_MODERATE: float = 0.75
    AI_CONFIDENCE_THRESHOLD_LOW: float = 0.80
    
    # Escalation Settings
    ESCALATION_EMAIL_TIMEOUT_MINUTES: int = 1
    AI_PROCESSING_TIMEOUT_SECONDS: int = 3
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
