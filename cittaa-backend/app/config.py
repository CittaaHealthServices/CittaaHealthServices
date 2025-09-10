from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    mongodb_url: str = "mongodb://localhost:27017"
    database_name: str = "cittaa_parental_control"
    
    redis_url: str = "redis://localhost:6379"
    
    secret_key: str = "cittaa-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    aws_access_key_id: Optional[str] = None
    aws_secret_access_key: Optional[str] = None
    aws_region: str = "ap-south-1"
    s3_bucket: str = "cittaa-parental-control"
    
    content_filter_api_key: Optional[str] = None
    
    class Config:
        env_file = ".env"

settings = Settings()
