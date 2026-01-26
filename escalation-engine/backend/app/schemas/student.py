"""
Student schemas for CITTAA Escalation Engine
"""

from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import date, datetime


class StudentCreate(BaseModel):
    """Schema for creating a new student"""
    institution_id: UUID
    student_code: str  # anonymized identifier
    grade: Optional[str] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    guardian_contact: Optional[str] = None
    enrollment_date: Optional[date] = None


class StudentResponse(BaseModel):
    """Schema for student response"""
    student_id: UUID
    institution_id: UUID
    student_code: str
    grade: Optional[str] = None
    section: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[date] = None
    guardian_contact: Optional[str] = None
    enrollment_date: Optional[date] = None
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class StudentUpdate(BaseModel):
    """Schema for updating student"""
    grade: Optional[str] = None
    section: Optional[str] = None
    guardian_contact: Optional[str] = None
    is_active: Optional[bool] = None
