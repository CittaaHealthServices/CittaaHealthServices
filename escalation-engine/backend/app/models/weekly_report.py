"""
Weekly Report model for CITTAA Escalation Engine
"""

from sqlalchemy import Column, String, Text, Integer, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class WeeklyReport(Base):
    """Weekly Report model - psychologist weekly summary reports"""
    __tablename__ = "weekly_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    psychologist_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.institution_id"))
    week_start_date = Column(Date, nullable=False)
    week_end_date = Column(Date, nullable=False)
    total_sessions = Column(Integer, default=0)
    total_students = Column(Integer, default=0)
    new_intakes = Column(Integer, default=0)
    no_shows = Column(Integer, default=0)
    report_content = Column(JSONB)
    summary = Column(Text)
    challenges = Column(Text)
    recommendations = Column(Text)
    submitted_at = Column(DateTime)
    status = Column(String(50), default='draft')  # 'draft', 'submitted', 'approved', 'rejected'
    quality_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    psychologist = relationship("User", back_populates="weekly_reports")
    institution = relationship("Institution", back_populates="weekly_reports")

    def __repr__(self):
        return f"<WeeklyReport {self.report_id} ({self.week_start_date} - {self.week_end_date})>"
