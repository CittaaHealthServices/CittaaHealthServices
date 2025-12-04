"""
User model for Vocalysis
"""

from sqlalchemy import Column, String, Boolean, DateTime, Enum, Text, Integer, Float
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid
import enum

from app.models.database import Base

class UserRole(str, enum.Enum):
    PATIENT = "patient"
    PSYCHOLOGIST = "psychologist"
    HR_ADMIN = "hr_admin"
    SUPER_ADMIN = "super_admin"
    RESEARCHER = "researcher"

class User(Base):
    """User model"""
    __tablename__ = "users"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    
    # Profile information
    full_name = Column(String(255), nullable=True)
    phone = Column(String(20), nullable=True)
    age_range = Column(String(20), nullable=True)
    gender = Column(String(20), nullable=True)
    language_preference = Column(String(20), default="english")
    
    # Role and organization
    role = Column(String(20), default=UserRole.PATIENT.value)
    organization_id = Column(String(36), nullable=True)
    employee_id = Column(String(50), nullable=True)
    
    # Consent and status
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    
    # Clinical trial
    is_clinical_trial_participant = Column(Boolean, default=False)
    trial_status = Column(String(20), nullable=True)  # pending, approved, rejected
    approved_by = Column(String(36), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    
    # Multi-sample collection tracking (9-12 samples for personalization)
    voice_samples_collected = Column(Integer, default=0)
    target_samples = Column(Integer, default=9)  # Minimum 9 samples for baseline
    baseline_established = Column(Boolean, default=False)
    personalization_score = Column(Float, nullable=True)  # 0-1 based on sample quality
    
    # Psychologist assignment
    assigned_psychologist_id = Column(String(36), nullable=True)
    assignment_date = Column(DateTime, nullable=True)
    
    # Password reset
    reset_token = Column(String(100), nullable=True)
    reset_token_expires_at = Column(DateTime, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime, nullable=True)
    
    # Relationships
    voice_samples = relationship("VoiceSample", back_populates="user")
    predictions = relationship("Prediction", back_populates="user")
    clinical_assessments = relationship("ClinicalAssessment", back_populates="user")
    
    def __repr__(self):
        return f"<User {self.email}>"
