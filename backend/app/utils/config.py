"""
Configuration settings for Vocalysis API
"""

import os
from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """Application settings"""
    
    # App settings
    APP_NAME: str = "Vocalysis API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # JWT settings
    JWT_SECRET: str = os.getenv("JWT_SECRET", "vocalysis_jwt_secret_key_cittaa_2024")
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRATION_HOURS: int = 24 * 30  # 30 days
    
    # Database settings
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./vocalysis.db")
    
    # Storage settings
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_UPLOAD_SIZE: int = 50 * 1024 * 1024  # 50MB
    
    # ML Model settings
    MODEL_PATH: str = os.getenv("MODEL_PATH", "./models")
    
    # Audio processing settings
    TARGET_SAMPLE_RATE: int = 16000
    MIN_AUDIO_DURATION: float = 10.0  # seconds
    MAX_AUDIO_DURATION: float = 300.0  # 5 minutes
    
    # CITTAA Brand Colors
    BRAND_PRIMARY: str = "#8B5A96"
    BRAND_SECONDARY: str = "#7BB3A8"
    BRAND_ACCENT: str = "#FF8C42"
    BRAND_BACKGROUND: str = "#F8F9FA"
    BRAND_TEXT: str = "#2C3E50"
    BRAND_SUCCESS: str = "#27AE60"
    BRAND_WARNING: str = "#F39C12"
    BRAND_ERROR: str = "#E74C3C"
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
