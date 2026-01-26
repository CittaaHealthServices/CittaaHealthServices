"""
Escalation Case model for CITTAA Escalation Engine
"""

from sqlalchemy import Column, String, Text, DateTime, Numeric, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class EscalationCase(Base):
    """Escalation Case model - AI-detected risk cases requiring attention"""
    __tablename__ = "escalation_cases"

    case_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"))
    session_id = Column(UUID(as_uuid=True), ForeignKey("counseling_sessions.session_id"))
    psychologist_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.institution_id"))
    
    # Escalation details
    escalation_level = Column(String(20), nullable=False)  # 'level_1_low', 'level_2_moderate', 'level_3_high', 'level_4_emergency'
    risk_category = Column(String(100))  # 'suicide_risk', 'self_harm', 'abuse_suspected', 'behavioral_crisis', 'severe_depression'
    ai_confidence_score = Column(Numeric(5, 4))
    keywords_detected = Column(ARRAY(String))
    escalation_reason = Column(Text)
    immediate_actions_taken = Column(Text)
    
    # Status tracking
    status = Column(String(50), default='open')  # 'open', 'in_progress', 'resolved', 'referred'
    resolution_notes = Column(Text)
    escalated_at = Column(DateTime, default=datetime.utcnow)
    resolved_at = Column(DateTime)
    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="escalation_cases")
    session = relationship("CounselingSession", back_populates="escalation_cases")
    psychologist = relationship("User", back_populates="escalation_cases_created", foreign_keys=[psychologist_id])
    assigned_user = relationship("User", back_populates="escalation_cases_assigned", foreign_keys=[assigned_to])
    institution = relationship("Institution", back_populates="escalation_cases")
    notifications = relationship("EscalationNotification", back_populates="escalation_case")

    def __repr__(self):
        return f"<EscalationCase {self.case_id} ({self.escalation_level})>"
