"""
User schemas for Vocalysis API
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class UserCreate(BaseModel):
    """Schema for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age_range: Optional[str] = None
    gender: Optional[str] = None
    language_preference: str = "english"
    role: str = "patient"
    organization_id: Optional[str] = None
    employee_id: Optional[str] = None
    is_clinical_trial_participant: bool = False

class UserLogin(BaseModel):
    """Schema for user login"""
    email: EmailStr
    password: str

class UserUpdate(BaseModel):
    """Schema for user profile update"""
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age_range: Optional[str] = None
    gender: Optional[str] = None
    language_preference: Optional[str] = None

class UserResponse(BaseModel):
    """Schema for user response"""
    id: str
    email: str
    full_name: Optional[str] = None
    phone: Optional[str] = None
    age_range: Optional[str] = None
    gender: Optional[str] = None
    language_preference: str
    role: str
    organization_id: Optional[str] = None
    consent_given: bool
    is_active: bool
    is_verified: bool
    is_clinical_trial_participant: bool
    trial_status: Optional[str] = None
    assigned_psychologist_id: Optional[str] = None
    created_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True

class Token(BaseModel):
    """Schema for JWT token response"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

class ConsentUpdate(BaseModel):
    """Schema for consent update"""
    consent_given: bool

class ClinicalTrialRegistration(BaseModel):
    """Schema for clinical trial registration"""
    age: int
    gender: str
    phone: str
    institution: Optional[str] = None
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    preferred_language: str = "english"
