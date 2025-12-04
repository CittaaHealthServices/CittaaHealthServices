"""
Configuration settings for Vocalysis API
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # MongoDB Configuration - Use environment variable for security
    mongodb_url: str = ""  # Set via MONGODB_URL environment variable
    mongodb_db_name: str = "vocalysis_prod"
    
    # JWT Configuration
    jwt_secret_key: str = "vocalysis-super-secret-key-change-in-production"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60 * 24  # 24 hours
    
    # Cashfree Configuration
    cashfree_client_id: str = ""
    cashfree_client_secret: str = ""
    cashfree_api_version: str = "2023-08-01"
    cashfree_environment: str = "production"  # or "sandbox"
    
    # Email Configuration (for patient notifications)
    smtp_host: str = "smtp.gmail.com"
    smtp_port: int = 587
    smtp_user: str = ""
    smtp_password: str = ""
    from_email: str = "noreply@cittaa.in"
    
    # Encryption Key for sensitive data
    encryption_key: str = "vocalysis_secure_encryption_key_for_production"
    
    # API Configuration
    api_v1_prefix: str = "/api/v1"
    
    # Vocalysis ML Backend
    vocalysis_ml_backend_url: str = "https://vocalysis-backend-1081764900204.us-central1.run.app/api/v1"
    
    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
