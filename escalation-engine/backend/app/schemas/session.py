"""
Session schemas for CITTAA Escalation Engine
"""

from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import date, datetime


class SessionDetail(BaseModel):
    """Schema for individual session detail within a report"""
    student_code: str  # Anonymized
    student_name: Optional[str] = None  # For internal use only
    grade: Optional[str] = None
    session_type: str  # 'individual', 'group', 'family', 'crisis'
    time: Optional[str] = None
    duration: int  # minutes
    focus_area: Optional[str] = None
    presenting_issue: str  # AI analyzes this
    interventions: Optional[str] = None
    risk_level: str  # 'low', 'moderate', 'high', 'imminent'
    follow_up_needed: bool = False
    notes: Optional[str] = None  # AI analyzes this


class AssessmentDetail(BaseModel):
    """Schema for assessment details"""
    assessment_type: str  # 'Learning/Academic', 'Behavioral', 'Emotional/Social', 'Other'
    student_name: Optional[str] = None
    student_code: str
    grade: Optional[str] = None
    status: str  # 'Initiated', 'In Progress', 'Completed'
    notes: Optional[str] = None


class ConsultationDetail(BaseModel):
    """Schema for consultation details"""
    consultation_type: str  # 'Teacher', 'Parent', 'Admin'
    with_person: str
    regarding: str
    duration: int  # minutes
    outcome: Optional[str] = None
    follow_up_needed: bool = False


class CrisisInterventionDetail(BaseModel):
    """Schema for crisis intervention details"""
    student_name: Optional[str] = None
    student_code: str
    grade: Optional[str] = None
    nature_of_crisis: str
    action_taken: str
    follow_up_plan: Optional[str] = None
    parent_notified: bool = False


class CurriculumImplementationDetail(BaseModel):
    """Schema for curriculum implementation details"""
    activity: str
    grade_class: str
    topic: str
    materials_used: Optional[str] = None
    student_engagement: int  # 1-5 scale
    notes: Optional[str] = None


class ReferralDetail(BaseModel):
    """Schema for referral details"""
    student_name: Optional[str] = None
    student_code: str
    grade: Optional[str] = None
    reason: str
    referred_to: str
    status: str  # 'Pending', 'In Progress', 'Completed'
    notes: Optional[str] = None


class SessionCreate(BaseModel):
    """Schema for creating a new counseling session"""
    student_id: UUID
    institution_id: UUID
    session_date: date
    session_type: str  # 'individual', 'group', 'family', 'crisis'
    duration_minutes: Optional[int] = None
    presenting_issue: Optional[str] = None
    interventions_used: Optional[str] = None
    risk_level: Optional[str] = None  # 'low', 'moderate', 'high', 'imminent'
    requires_escalation: bool = False
    session_notes: Optional[str] = None
    follow_up_needed: bool = False
    follow_up_date: Optional[date] = None


class SessionResponse(BaseModel):
    """Schema for session response"""
    session_id: UUID
    student_id: UUID
    psychologist_id: UUID
    institution_id: UUID
    session_date: date
    session_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    presenting_issue: Optional[str] = None
    interventions_used: Optional[str] = None
    risk_level: Optional[str] = None
    requires_escalation: bool
    session_notes: Optional[str] = None
    follow_up_needed: bool
    follow_up_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class SessionUpdate(BaseModel):
    """Schema for updating session"""
    session_type: Optional[str] = None
    duration_minutes: Optional[int] = None
    presenting_issue: Optional[str] = None
    interventions_used: Optional[str] = None
    risk_level: Optional[str] = None
    requires_escalation: Optional[bool] = None
    session_notes: Optional[str] = None
    follow_up_needed: Optional[bool] = None
    follow_up_date: Optional[date] = None
