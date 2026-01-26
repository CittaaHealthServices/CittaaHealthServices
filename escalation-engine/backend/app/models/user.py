"""
User model for CITTAA Escalation Engine
"""

from sqlalchemy import Column, String, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class User(Base):
    """User model - admins, psychologists, school_admins"""
    __tablename__ = "users"

    user_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False)  # 'admin', 'psychologist', 'school_admin'
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.institution_id"))
    rci_registration = Column(String(100))  # for psychologists
    phone = Column(String(20))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    institution = relationship("Institution", back_populates="users")
    counseling_sessions = relationship("CounselingSession", back_populates="psychologist", foreign_keys="CounselingSession.psychologist_id")
    daily_reports = relationship("DailyReport", back_populates="psychologist")
    weekly_reports = relationship("WeeklyReport", back_populates="psychologist")
    monthly_reports = relationship("MonthlyReport", back_populates="psychologist")
    escalation_cases_created = relationship("EscalationCase", back_populates="psychologist", foreign_keys="EscalationCase.psychologist_id")
    escalation_cases_assigned = relationship("EscalationCase", back_populates="assigned_user", foreign_keys="EscalationCase.assigned_to")
    ai_reviews = relationship("AITrainingData", back_populates="reviewer")

    def __repr__(self):
        return f"<User {self.email} ({self.role})>"
