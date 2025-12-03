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
    
    # Gemini API settings for voice analysis
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY", None)
    GEMINI_MODEL_NAME: str = os.getenv("GEMINI_MODEL_NAME", "gemini-1.5-flash")
    
    # Email settings
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: str = os.getenv("SMTP_USER", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    EMAIL_FROM: str = os.getenv("EMAIL_FROM", "noreply@cittaa.in")
    EMAIL_FROM_NAME: str = os.getenv("EMAIL_FROM_NAME", "Cittaa Health Services")
    
    # Frontend URL for email links
    FRONTEND_URL: str = os.getenv("FRONTEND_URL", "https://vocalysis-frontend-1081764900204.us-central1.run.app")
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()
