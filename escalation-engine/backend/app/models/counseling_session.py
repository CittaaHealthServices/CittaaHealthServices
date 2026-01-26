"""
Counseling Session model for CITTAA Escalation Engine
"""

from sqlalchemy import Column, String, Text, Integer, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class CounselingSession(Base):
    """Counseling Session model - individual counseling sessions"""
    __tablename__ = "counseling_sessions"

    session_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("students.student_id"))
    psychologist_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.institution_id"))
    session_date = Column(Date, nullable=False)
    session_type = Column(String(50))  # 'individual', 'group', 'family', 'crisis'
    duration_minutes = Column(Integer)
    presenting_issue = Column(Text)
    interventions_used = Column(Text)
    risk_level = Column(String(20))  # 'low', 'moderate', 'high', 'imminent'
    requires_escalation = Column(Boolean, default=False)
    session_notes = Column(Text)
    follow_up_needed = Column(Boolean, default=False)
    follow_up_date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    student = relationship("Student", back_populates="counseling_sessions")
    psychologist = relationship("User", back_populates="counseling_sessions", foreign_keys=[psychologist_id])
    institution = relationship("Institution", back_populates="counseling_sessions")
    escalation_cases = relationship("EscalationCase", back_populates="session")

    def __repr__(self):
        return f"<CounselingSession {self.session_id} ({self.session_date})>"
