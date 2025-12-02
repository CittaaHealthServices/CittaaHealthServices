"""
Clinical Assessment model for Vocalysis
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base

class ClinicalAssessment(Base):
    """Clinical Assessment model for psychologist evaluations"""
    __tablename__ = "clinical_assessments"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    psychologist_id = Column(String(36), nullable=True, index=True)
    
    # Assessment date
    assessment_date = Column(DateTime, default=datetime.utcnow)
    
    # Clinical scores (manually entered by psychologist)
    phq9_score = Column(Integer, nullable=True)
    gad7_score = Column(Integer, nullable=True)
    pss_score = Column(Integer, nullable=True)
    
    # Clinical notes
    clinician_notes = Column(Text, nullable=True)
    diagnosis = Column(Text, nullable=True)
    treatment_plan = Column(Text, nullable=True)
    
    # Ground truth label for model validation
    ground_truth_label = Column(String(50), nullable=True)  # normal, depression, anxiety, stress
    
    # Follow-up
    follow_up_date = Column(DateTime, nullable=True)
    follow_up_notes = Column(Text, nullable=True)
    
    # Session information
    session_number = Column(Integer, default=1)
    session_duration_minutes = Column(Integer, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="clinical_assessments")
    
    def __repr__(self):
        return f"<ClinicalAssessment {self.id}>"
