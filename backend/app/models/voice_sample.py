"""
Voice Sample model for Vocalysis
"""

from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text, JSON, Integer
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base

class VoiceSample(Base):
    """Voice Sample model"""
    __tablename__ = "voice_samples"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String(36), ForeignKey("users.id"), nullable=False, index=True)
    
    # Audio metadata
    file_path = Column(String(500), nullable=True)
    file_name = Column(String(255), nullable=True)
    audio_format = Column(String(10), nullable=True)
    duration_seconds = Column(Float, nullable=True)
    sample_rate = Column(Integer, nullable=True)
    file_size = Column(Integer, nullable=True)
    
    # Processing status
    processing_status = Column(String(20), default="uploaded")  # uploaded, processing, completed, failed
    quality_score = Column(Float, nullable=True)
    validation_message = Column(Text, nullable=True)
    
    # Extracted features (stored as JSON)
    features = Column(JSON, nullable=True)
    feature_vector = Column(JSON, nullable=True)
    
    # Recording context
    recorded_via = Column(String(50), default="web_app")  # web_app, mobile_app, upload
    recording_prompt = Column(Text, nullable=True)
    
    # Timestamps
    recorded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User", back_populates="voice_samples")
    prediction = relationship("Prediction", back_populates="voice_sample", uselist=False)
    
    def __repr__(self):
        return f"<VoiceSample {self.id}>"
