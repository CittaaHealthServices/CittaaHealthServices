"""
Clinical Trial Participant model for Vocalysis
Tracks participant enrollment, sample collection, and personalized baselines
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Integer, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class ClinicalTrialParticipant(Base):
    """Clinical Trial Participant model for tracking enrollment and sample collection"""
    __tablename__ = "clinical_trial_participants"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Demographics
    age = Column(Integer, nullable=True)
    gender = Column(String(20), nullable=True)
    phone = Column(String(20), nullable=True)
    institution = Column(String(255), nullable=True)
    preferred_language = Column(String(50), default="english")
    
    # Consent
    consent_given = Column(Boolean, default=False)
    consent_timestamp = Column(DateTime, nullable=True)
    
    # Medical information
    medical_history = Column(Text, nullable=True)
    current_medications = Column(Text, nullable=True)
    
    # Emergency contact
    emergency_contact_name = Column(String(255), nullable=True)
    emergency_contact_phone = Column(String(20), nullable=True)
    
    # Enrollment status
    enrollment_date = Column(DateTime, default=datetime.utcnow)
    trial_status = Column(String(20), default="enrolled")  # enrolled, active, completed, withdrawn
    approval_status = Column(String(20), default="pending")  # pending, approved, rejected
    approved_by = Column(String(36), nullable=True)
    approval_date = Column(DateTime, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Sample collection tracking (9-12 samples required)
    voice_samples_collected = Column(Integer, default=0)
    target_samples = Column(Integer, default=10)  # Target: 9-12 samples
    min_samples_required = Column(Integer, default=9)
    max_samples_allowed = Column(Integer, default=12)
    
    # Personalized baseline
    baseline_established = Column(Boolean, default=False)
    baseline_data = Column(JSON, nullable=True)  # Stores personalized baseline features
    baseline_established_at = Column(DateTime, nullable=True)
    
    # Psychologist assignment
    assigned_psychologist_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    assignment_date = Column(DateTime, nullable=True)
    
    # Clinical notes
    clinical_notes = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", foreign_keys=[user_id], backref="clinical_trial_participant")
    assigned_psychologist = relationship("User", foreign_keys=[assigned_psychologist_id])
    voice_sessions = relationship("VoiceSession", back_populates="participant")
    
    def __repr__(self):
        return f"<ClinicalTrialParticipant {self.id} - Samples: {self.voice_samples_collected}/{self.target_samples}>"


class VoiceSession(Base):
    """Voice Session model for tracking individual recording sessions (2-5 min each)"""
    __tablename__ = "voice_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    participant_id = Column(String(36), ForeignKey("clinical_trial_participants.id"), nullable=False, index=True)
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Session metadata
    session_number = Column(Integer, nullable=False)  # 1-12
    session_type = Column(String(50), default="baseline")  # baseline, follow_up, assessment
    
    # Recording requirements (2-5 min)
    min_duration_seconds = Column(Integer, default=120)  # 2 minutes
    max_duration_seconds = Column(Integer, default=300)  # 5 minutes
    actual_duration_seconds = Column(Float, nullable=True)
    
    # Recording status
    status = Column(String(20), default="pending")  # pending, recording, completed, failed
    recording_started_at = Column(DateTime, nullable=True)
    recording_completed_at = Column(DateTime, nullable=True)
    
    # Voice sample reference
    voice_sample_id = Column(String(36), ForeignKey("voice_samples.id"), nullable=True)
    
    # Analysis results
    prediction_id = Column(String(36), ForeignKey("predictions.id"), nullable=True)
    
    # Quality metrics
    audio_quality_score = Column(Float, nullable=True)
    noise_level = Column(Float, nullable=True)
    is_valid = Column(Boolean, default=True)
    validation_message = Column(Text, nullable=True)
    
    # Extracted features for this session
    session_features = Column(JSON, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    participant = relationship("ClinicalTrialParticipant", back_populates="voice_sessions")
    user = relationship("User")
    voice_sample = relationship("VoiceSample")
    prediction = relationship("Prediction")
    
    def __repr__(self):
        return f"<VoiceSession {self.id} - Session {self.session_number}>"


class PersonalizedBaseline(Base):
    """Personalized Baseline model for storing user-specific voice characteristics"""
    __tablename__ = "personalized_baselines"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    participant_id = Column(String(36), ForeignKey("clinical_trial_participants.id"), nullable=True)
    
    # Number of samples used to establish baseline
    samples_used = Column(Integer, default=0)
    
    # Baseline voice features (averaged from multiple samples)
    # Pitch baseline
    baseline_pitch_mean = Column(Float, nullable=True)
    baseline_pitch_std = Column(Float, nullable=True)
    baseline_pitch_cv = Column(Float, nullable=True)
    
    # Energy baseline
    baseline_rms_mean = Column(Float, nullable=True)
    baseline_rms_std = Column(Float, nullable=True)
    
    # Speech rate baseline
    baseline_speech_rate = Column(Float, nullable=True)
    
    # Voice quality baseline
    baseline_jitter = Column(Float, nullable=True)
    baseline_shimmer = Column(Float, nullable=True)
    baseline_hnr = Column(Float, nullable=True)
    
    # MFCC baseline
    baseline_mfcc_mean = Column(Float, nullable=True)
    baseline_mfcc_std = Column(Float, nullable=True)
    
    # Full feature vector (JSON for flexibility)
    baseline_features = Column(JSON, nullable=True)
    
    # Personalization thresholds (deviation from baseline)
    anxiety_threshold = Column(Float, default=0.25)  # 25% deviation
    depression_threshold = Column(Float, default=0.20)  # 20% deviation
    stress_threshold = Column(Float, default=0.30)  # 30% deviation
    
    # Confidence in baseline
    baseline_confidence = Column(Float, nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    last_updated_at = Column(DateTime, default=datetime.utcnow)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = relationship("User", backref="personalized_baseline")
    
    def __repr__(self):
        return f"<PersonalizedBaseline {self.id} - Samples: {self.samples_used}>"
