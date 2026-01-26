"""
Student model for CITTAA Escalation Engine
"""

from sqlalchemy import Column, String, Date, DateTime, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class Student(Base):
    """Student model - anonymized student records"""
    __tablename__ = "students"

    student_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    institution_id = Column(UUID(as_uuid=True), ForeignKey("institutions.institution_id"))
    student_code = Column(String(50), unique=True, nullable=False)  # anonymized identifier
    grade = Column(String(10))
    section = Column(String(10))
    gender = Column(String(20))
    date_of_birth = Column(Date)
    guardian_contact = Column(String(20))
    enrollment_date = Column(Date)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    institution = relationship("Institution", back_populates="students")
    counseling_sessions = relationship("CounselingSession", back_populates="student")
    escalation_cases = relationship("EscalationCase", back_populates="student")

    def __repr__(self):
        return f"<Student {self.student_code}>"
