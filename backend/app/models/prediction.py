"""
Prediction model for Vocalysis
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base

class Prediction(Base):
    """Prediction model for mental health analysis results"""
    __tablename__ = "predictions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    voice_sample_id = Column(String(36), ForeignKey("voice_samples.id"), nullable=True, index=True)
    
    # Model information
    model_version = Column(String(20), default="v1.0")
    model_type = Column(String(50), default="ensemble")  # ensemble, bilstm, cnn, xgboost
    
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
    
    # Psychologist analysis tracking
    analyzed_by_psychologist_id = Column(String(36), ForeignKey("users.id"), nullable=True)
    
    # Timestamps
    predicted_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="predictions")
    voice_sample = relationship("VoiceSample", back_populates="prediction")
    
    def __repr__(self):
        return f"<Prediction {self.id} - Risk: {self.overall_risk_level}>"
