"""
Monthly Report model for CITTAA Escalation Engine
"""

from sqlalchemy import Column, String, Text, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class MonthlyReport(Base):
    """Monthly Report model - psychologist monthly comprehensive reports"""
    __tablename__ = "monthly_reports"

    report_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    psychologist_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.institution_id"))
    report_month = Column(Date, nullable=False)  # first day of month
    executive_summary = Column(Text)
    quantitative_metrics = Column(JSONB)
    clinical_outcomes = Column(JSONB)
    institutional_impact = Column(Text)
    recommendations = Column(Text)
    report_content = Column(JSONB)
    submitted_at = Column(DateTime)
    status = Column(String(50), default='draft')  # 'draft', 'submitted', 'approved', 'rejected'
    quality_score = Column(Numeric(5, 2))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    psychologist = relationship("User", back_populates="monthly_reports")
    institution = relationship("Institution", back_populates="monthly_reports")

    def __repr__(self):
        return f"<MonthlyReport {self.report_id} ({self.report_month})>"
