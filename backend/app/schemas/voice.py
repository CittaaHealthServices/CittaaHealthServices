"""
Voice schemas for Vocalysis API
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class VoiceUploadResponse(BaseModel):
    """Schema for voice upload response"""
    sample_id: str
    user_id: str
    status: str
    message: str
    estimated_processing_time: int  # seconds

class VoiceStatusResponse(BaseModel):
    """Schema for voice processing status"""
    sample_id: str
    status: str
    uploaded_at: datetime
    processed_at: Optional[datetime] = None
    message: str
    quality_score: Optional[float] = None

class VoiceSampleResponse(BaseModel):
    """Schema for voice sample details"""
    id: str
    user_id: str
    file_name: Optional[str] = None
    audio_format: Optional[str] = None
    duration_seconds: Optional[float] = None
    processing_status: str
    quality_score: Optional[float] = None
    recorded_at: datetime
    processed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class VoiceAnalysisRequest(BaseModel):
    """Schema for voice analysis request"""
    demo_type: Optional[str] = None  # normal, anxiety, depression, stress

class VoiceFeaturesResponse(BaseModel):
    """Schema for extracted voice features"""
    duration: float
    speech_rate: float
    pitch_mean: float
    pitch_std: float
    rms_mean: float
    zcr_mean: float
    spectral_centroid_mean: float
    jitter_mean: float
    hnr: float
