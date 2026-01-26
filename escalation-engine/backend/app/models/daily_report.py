"""
Daily Report model for CITTAA Escalation Engine
"""

from sqlalchemy import Column, String, Text, Integer, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class DailyReport(Base):
    """Daily Report model - psychologist daily activity reports"""
    __tablename__ = "daily_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    psychologist_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.institution_id"))
    report_date = Column(Date, nullable=False)
    sessions_conducted = Column(Integer, default=0)
    crisis_interventions = Column(Integer, default=0)
    new_referrals = Column(Integer, default=0)
    follow_ups_completed = Column(Integer, default=0)
    report_content = Column(JSONB)  # Detailed session information
    key_highlights = Column(Text)
    notes_and_observations = Column(Text)
    submitted_at = Column(DateTime)
    status = Column(String(50), default='draft')  # 'draft', 'submitted', 'approved', 'rejected'
    quality_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    psychologist = relationship("User", back_populates="daily_reports")
    institution = relationship("Institution", back_populates="daily_reports")

    def __repr__(self):
        return f"<DailyReport {self.report_id} ({self.report_date})>"
