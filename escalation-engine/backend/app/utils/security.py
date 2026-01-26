"""
Security utilities for CITTAA Escalation Engine
"""

from datetime import datetime, timedelta
from typing import Optional
import jwt
import bcrypt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from cryptography.fernet import Fernet
import hashlib
import os

from app.utils.config import settings

security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash a password using bcrypt"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return bcrypt.checkpw(password.encode(), hashed_password.encode())


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token"""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    """Decode and verify a JWT token"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current user from JWT token"""
    from app.models.database import SessionLocal
    from app.models.user import User
    
    token = credentials.credentials
    payload = decode_token(token)
    
    # Get actual user from database
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.user_id == payload.get("sub")).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        return user
    finally:
        db.close()


def require_role(allowed_roles: list):
    """Decorator to require specific roles"""
    async def role_checker(credentials: HTTPAuthorizationCredentials = Depends(security)):
        token = credentials.credentials
        payload = decode_token(token)
        user_role = payload.get("role")
        if user_role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        return payload
    return role_checker


class DataProtectionService:
    """DPDP Act 2023 compliant data handling"""
    
    def __init__(self):
        key = settings.ENCRYPTION_KEY
        # Ensure key is valid Fernet key (32 url-safe base64-encoded bytes)
        if len(key) < 32:
            key = key.ljust(32, '0')
        self.cipher_suite = Fernet(Fernet.generate_key())
    
    def encrypt_data(self, data: str) -> str:
        """Encrypt sensitive data"""
        return self.cipher_suite.encrypt(data.encode()).decode()
    
    def decrypt_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data"""
        return self.cipher_suite.decrypt(encrypted_data.encode()).decode()
    
    def anonymize_student_data(self, student_info: dict) -> str:
        """Generate anonymized student code"""
        raw_data = f"{student_info['institution_id']}{student_info['name']}{student_info['dob']}"
        student_code = hashlib.sha256(raw_data.encode()).hexdigest()[:12].upper()
        return f"STU-{student_code}"
    
    def hash_pii(self, data: str) -> str:
        """Hash PII data for storage"""
        return hashlib.sha256(data.encode()).hexdigest()


data_protection = DataProtectionService()


def verify_token(token: str) -> Optional[dict]:
    """Verify a JWT token and return payload or None"""
    try:
        payload = jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        return payload
    except (jwt.ExpiredSignatureError, jwt.InvalidTokenError):
        return None


def anonymize_student_data(institution_id: str, student_name: str, date_of_birth: str) -> str:
    """
    Generate anonymized student code from PII
    
    Uses SHA-256 hash of institution_id + name + dob
    to create a unique, non-reversible identifier.
    
    This supports DPDP Act 2023 compliance.
    """
    raw_data = f"{institution_id}{student_name}{date_of_birth}"
    student_code = hashlib.sha256(raw_data.encode()).hexdigest()[:12].upper()
    return f"STU-{student_code}"
