"""
Escalation schemas for CITTAA Escalation Engine
"""

from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime


class EscalationAssessment(BaseModel):
    """Schema for AI escalation assessment result"""
    escalation_level: str  # 'level_1_low', 'level_2_moderate', 'level_3_high', 'level_4_emergency'
    confidence: float
    risk_category: str  # 'suicide_risk', 'self_harm', 'abuse_suspected', 'behavioral_crisis', 'severe_depression'
    keywords_detected: List[str]
    reasoning: str
    recommended_actions: List[str]
    language_detected: Optional[str] = None


class EscalationCaseCreate(BaseModel):
    """Schema for creating an escalation case"""
    student_id: UUID
    session_id: Optional[UUID] = None
    institution_id: UUID
    escalation_level: str
    risk_category: Optional[str] = None
    ai_confidence_score: Optional[float] = None
    keywords_detected: Optional[List[str]] = None
    escalation_reason: Optional[str] = None
    immediate_actions_taken: Optional[str] = None


class EscalationCaseResponse(BaseModel):
    """Schema for escalation case response"""
    case_id: UUID
    student_id: UUID
    session_id: Optional[UUID] = None
    psychologist_id: UUID
    institution_id: UUID
    escalation_level: str
    risk_category: Optional[str] = None
    ai_confidence_score: Optional[float] = None
    keywords_detected: Optional[List[str]] = None
    escalation_reason: Optional[str] = None
    immediate_actions_taken: Optional[str] = None
    status: str
    resolution_notes: Optional[str] = None
    escalated_at: datetime
    resolved_at: Optional[datetime] = None
    assigned_to: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EscalationCaseUpdate(BaseModel):
    """Schema for updating escalation case"""
    status: Optional[str] = None  # 'open', 'in_progress', 'resolved', 'referred'
    resolution_notes: Optional[str] = None
    assigned_to: Optional[UUID] = None
    immediate_actions_taken: Optional[str] = None


class EscalationNotificationCreate(BaseModel):
    """Schema for creating escalation notification"""
    case_id: UUID
    recipient_email: str
    recipient_type: str  # 'school_principal', 'admin', 'supervisor', 'emergency_contact'
    notification_type: str = "email"  # 'email', 'sms', 'whatsapp'


class EscalationNotificationResponse(BaseModel):
    """Schema for escalation notification response"""
    notification_id: UUID
    case_id: UUID
    recipient_email: str
    recipient_type: Optional[str] = None
    notification_type: Optional[str] = None
    sent_at: Optional[datetime] = None
    delivery_status: str
    error_message: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True


class EscalationDashboardStats(BaseModel):
    """Schema for escalation dashboard statistics"""
    total_open_cases: int
    emergency_cases: int
    high_risk_cases: int
    moderate_cases: int
    low_cases: int
    resolved_today: int
    average_resolution_time_hours: Optional[float] = None
    cases_by_institution: Dict[str, int] = {}
    cases_by_risk_category: Dict[str, int] = {}
    trend_data: Optional[List[Dict[str, Any]]] = None
