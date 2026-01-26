"""
Institution model for schools and hospitals
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class Institution(Base):
    """Institution model - schools and hospitals"""
    __tablename__ = "institutions"

    institution_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    type = Column(String(50), nullable=False)  # 'school', 'hospital'
    address = Column(Text)
    contact_email = Column(String(255))
    contact_phone = Column(String(20))
    state = Column(String(100))
    district = Column(String(100))
    package_type = Column(String(50))  # 'essential', 'comprehensive', 'premium'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    users = relationship("User", back_populates="institution")
    students = relationship("Student", back_populates="institution")
    counseling_sessions = relationship("CounselingSession", back_populates="institution")
    daily_reports = relationship("DailyReport", back_populates="institution")
    weekly_reports = relationship("WeeklyReport", back_populates="institution")
    monthly_reports = relationship("MonthlyReport", back_populates="institution")
    escalation_cases = relationship("EscalationCase", back_populates="institution")

    def __repr__(self):
        return f"<Institution {self.name} ({self.type})>"
