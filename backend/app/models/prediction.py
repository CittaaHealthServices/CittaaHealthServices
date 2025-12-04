"""
Prediction model for Vocalysis with Continuous Learning Support
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base

# Counter for generating sequential report IDs
_report_counter = 0

def generate_report_id():
    """Generate a sequential report ID in format CITTVOCXXX"""
    global _report_counter
    _report_counter += 1
    return f"CITTVOC{_report_counter:03d}"

def init_report_counter(db_session):
    """Initialize the report counter from the database"""
    global _report_counter
    from sqlalchemy import func
    max_id = db_session.query(func.max(Prediction.report_sequence)).scalar()
    _report_counter = max_id if max_id else 0

class Prediction(Base):
    """Prediction model for mental health analysis results with continuous learning support"""
    __tablename__ = "predictions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    report_id = Column(String(20), unique=True, nullable=True, index=True)  # CITTVOCXXX format
    report_sequence = Column(Integer, nullable=True, index=True)  # Sequential number for report ID
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    voice_sample_id = Column(String(36), ForeignKey("voice_samples.id"), nullable=True, index=True)
    
    # Model information
    model_version = Column(String(20), default="v1.0")
    model_type = Column(String(50), default="ensemble")  # ensemble, bilstm, cnn, xgboost
    calibration_model_version = Column(String(20), nullable=True)  # Local calibration model version
    
    # Classification scores (0-1)
    normal_score = Column(Float, nullable=True)
    depression_score = Column(Float, nullable=True)
    anxiety_score = Column(Float, nullable=True)
    stress_score = Column(Float, nullable=True)
    
    # Overall assessment
    overall_risk_level = Column(String(20), nullable=True)  # low, moderate, high
    mental_health_score = Column(Float, nullable=True)  # 0-100
    confidence = Column(Float, nullable=True)  # 0-1
    
    # Clinical scale mappings
    phq9_score = Column(Float, nullable=True)  # 0-27
    phq9_severity = Column(String(30), nullable=True)
    gad7_score = Column(Float, nullable=True)  # 0-21
    gad7_severity = Column(String(30), nullable=True)
    pss_score = Column(Float, nullable=True)  # 0-40
    pss_severity = Column(String(30), nullable=True)
    wemwbs_score = Column(Float, nullable=True)  # 14-70
    wemwbs_severity = Column(String(30), nullable=True)
    
    # Interpretations and recommendations
    interpretations = Column(JSON, nullable=True)
    recommendations = Column(JSON, nullable=True)
    
    # Voice features summary
    voice_features = Column(JSON, nullable=True)
    
    # Processing metadata
    processing_time_ms = Column(Float, nullable=True)
    
    # ============================================
    # CONTINUOUS LEARNING - Clinician Feedback
    # ============================================
    clinician_reviewed = Column(Boolean, default=False, index=True)
    clinician_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    clinician_review_date = Column(DateTime, nullable=True)
    
    # Clinician-validated scores (ground truth for training)
    clinician_phq9 = Column(Float, nullable=True)
    clinician_gad7 = Column(Float, nullable=True)
    clinician_pss = Column(Float, nullable=True)
    clinician_wemwbs = Column(Float, nullable=True)
    clinician_risk_level = Column(String(20), nullable=True)  # low, mild, moderate, high
    clinician_comment = Column(Text, nullable=True)
    
    # Simple agreement flag for quick labeling
    prediction_agreed = Column(Boolean, nullable=True)  # Did clinician agree with prediction?
    
    # ============================================
    # CONTINUOUS LEARNING - Outcome Tracking
    # ============================================
    outcome_tracked = Column(Boolean, default=False)
    outcome_window_days = Column(Integer, default=30)  # Days to track outcome
    deteriorated_within_window = Column(Boolean, nullable=True)
    improved_within_window = Column(Boolean, nullable=True)
    
    # Follow-up assessment scores (for outcome validation)
    followup_date = Column(DateTime, nullable=True)
    followup_phq9 = Column(Float, nullable=True)
    followup_gad7 = Column(Float, nullable=True)
    followup_pss = Column(Float, nullable=True)
    followup_wemwbs = Column(Float, nullable=True)
    followup_mental_health_score = Column(Float, nullable=True)
    
    # Crisis/escalation events
    crisis_event_occurred = Column(Boolean, default=False)
    crisis_event_type = Column(String(50), nullable=True)  # hospitalization, therapy_started, etc.
    crisis_event_date = Column(DateTime, nullable=True)
    
    # ============================================
    # CONTINUOUS LEARNING - Patient Feedback
    # ============================================
    patient_accuracy_rating = Column(Integer, nullable=True)  # 1-5 scale
    patient_feedback = Column(Text, nullable=True)
    
    # ============================================
    # CONTINUOUS LEARNING - Training Metadata
    # ============================================
    used_for_training = Column(Boolean, default=False)
    training_batch_id = Column(String(36), nullable=True)
    training_date = Column(DateTime, nullable=True)
    
    # Timestamps
    predicted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships - specify foreign_keys to disambiguate multiple FKs to User table
    user = relationship("User", foreign_keys=[user_id], back_populates="predictions")
    clinician = relationship("User", foreign_keys=[clinician_id], backref="reviewed_predictions")
    voice_sample = relationship("VoiceSample", back_populates="prediction")
    
    def __repr__(self):
        return f"<Prediction {self.id} - Risk: {self.overall_risk_level}>"
