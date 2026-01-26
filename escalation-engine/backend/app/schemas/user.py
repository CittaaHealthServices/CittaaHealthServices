"""
User schemas for CITTAA Escalation Engine
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    """Schema for creating a new user"""
    email: EmailStr
    password: str
    full_name: str
    role: str  # 'admin', 'psychologist', 'school_admin'
    institution_id: Optional[UUID] = None
    rci_registration: Optional[str] = None
    phone: Optional[str] = None


class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    """Schema for user response"""
    user_id: UUID
    email: str
    full_name: str
    role: str
    institution_id: Optional[UUID] = None
    rci_registration: Optional[str] = None
    phone: Optional[str] = None
    is_active: bool
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    """Schema for token response"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserUpdate(BaseModel):
    """Schema for updating user"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    rci_registration: Optional[str] = None
    is_active: Optional[bool] = None
