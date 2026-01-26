"""
Institution schemas for CITTAA Escalation Engine
"""

from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime


class InstitutionCreate(BaseModel):
    """Schema for creating a new institution"""
    name: str
    type: str  # 'school', 'hospital'
    address: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    package_type: Optional[str] = None  # 'essential', 'comprehensive', 'premium'


class InstitutionResponse(BaseModel):
    """Schema for institution response"""
    institution_id: UUID
    name: str
    type: str
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    package_type: Optional[str] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class InstitutionUpdate(BaseModel):
    """Schema for updating institution"""
    name: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    package_type: Optional[str] = None
    is_active: Optional[bool] = None
