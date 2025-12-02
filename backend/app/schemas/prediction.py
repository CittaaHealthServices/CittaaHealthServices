"""
Prediction schemas for Vocalysis API
"""

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class ScaleMapping(BaseModel):
    """Schema for clinical scale mapping"""
    score: float
    severity: str

class PredictionResponse(BaseModel):
    """Schema for prediction response"""
    id: str
    user_id: str
    voice_sample_id: Optional[str] = None
    
    # Classification scores
    normal_score: Optional[float] = None
    depression_score: Optional[float] = None
    anxiety_score: Optional[float] = None
    stress_score: Optional[float] = None
    
    # Overall assessment
    overall_risk_level: Optional[str] = None
    mental_health_score: Optional[float] = None
    confidence: Optional[float] = None
    
    # Clinical scale mappings
    phq9_score: Optional[float] = None
    phq9_severity: Optional[str] = None
    gad7_score: Optional[float] = None
    gad7_severity: Optional[str] = None
    pss_score: Optional[float] = None
    pss_severity: Optional[str] = None
    wemwbs_score: Optional[float] = None
    wemwbs_severity: Optional[str] = None
    
    # Interpretations and recommendations
    interpretations: Optional[List[str]] = None
    recommendations: Optional[List[str]] = None
    
    # Voice features
    voice_features: Optional[Dict[str, Any]] = None
    
    # Timestamps
    predicted_at: datetime
    
    class Config:
        from_attributes = True

class DashboardResponse(BaseModel):
    """Schema for user dashboard data"""
    user_id: str
    current_risk_level: str
    risk_trend: str  # improving, stable, worsening
    compliance_rate: float
    total_recordings: int
    recent_predictions: List[PredictionResponse]
    weekly_trend_data: List[Dict[str, Any]]

class AnalysisResultResponse(BaseModel):
    """Schema for complete analysis result"""
    prediction: PredictionResponse
    voice_features: Dict[str, Any]
    scale_mappings: Dict[str, ScaleMapping]
    interpretations: List[str]
    recommendations: List[str]
    pdf_report_available: bool

class TrendDataPoint(BaseModel):
    """Schema for trend data point"""
    date: str
    depression: float
    anxiety: float
    stress: float
    mental_health_score: float
    sample_count: int
