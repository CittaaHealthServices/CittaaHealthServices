"""
Dashboard router for Vocalysis API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List

from app.models.database import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.models.voice_sample import VoiceSample
from app.schemas.prediction import DashboardResponse, PredictionResponse
from app.routers.auth import get_current_user
import json

router = APIRouter()

def _normalize_prediction_json_fields(pred: Prediction) -> Prediction:
    """
    Normalize JSON fields that may have been stored as strings (legacy data).
    SQLAlchemy JSON columns should contain Python dict/list, not JSON strings.
    """
    if isinstance(pred.interpretations, str):
        try:
            pred.interpretations = json.loads(pred.interpretations)
        except Exception:
            pred.interpretations = []
    if isinstance(pred.recommendations, str):
        try:
            pred.recommendations = json.loads(pred.recommendations)
        except Exception:
            pred.recommendations = []
    if isinstance(pred.voice_features, str):
        try:
            pred.voice_features = json.loads(pred.voice_features)
        except Exception:
            pred.voice_features = {}
    return pred

@router.get("/{user_id}", response_model=DashboardResponse)
async def get_user_dashboard(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get comprehensive dashboard data for a user"""
    # Verify access
    if current_user.id != user_id and current_user.role not in ["super_admin", "psychologist", "hr_admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get latest prediction
    latest_prediction = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.predicted_at.desc()).first()
    
    current_risk_level = latest_prediction.overall_risk_level if latest_prediction else "unknown"
    
    # Calculate risk trend (comparing last 7 days vs previous 7 days)
    now = datetime.utcnow()
    recent_start = now - timedelta(days=7)
    previous_start = now - timedelta(days=14)
    
    recent_predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id,
        Prediction.predicted_at >= recent_start
    ).all()
    
    previous_predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id,
        Prediction.predicted_at >= previous_start,
        Prediction.predicted_at < recent_start
    ).all()
    
    # Calculate average scores
    def calc_avg_score(predictions):
        if not predictions:
            return None
        scores = []
        for p in predictions:
            avg = ((p.depression_score or 0) + (p.anxiety_score or 0) + (p.stress_score or 0)) / 3
            scores.append(avg)
        return sum(scores) / len(scores) if scores else None
    
    recent_avg = calc_avg_score(recent_predictions)
    previous_avg = calc_avg_score(previous_predictions)
    
    if recent_avg is not None and previous_avg is not None:
        if recent_avg < previous_avg * 0.9:
            risk_trend = "improving"
        elif recent_avg > previous_avg * 1.1:
            risk_trend = "worsening"
        else:
            risk_trend = "stable"
    else:
        risk_trend = "insufficient_data"
    
    # Calculate compliance rate (target: 9 recordings per day)
    total_recordings = db.query(VoiceSample).filter(
        VoiceSample.user_id == user_id
    ).count()
    
    # Count days with recordings in last 30 days
    thirty_days_ago = now - timedelta(days=30)
    daily_counts = db.query(
        func.date(VoiceSample.recorded_at),
        func.count(VoiceSample.id)
    ).filter(
        VoiceSample.user_id == user_id,
        VoiceSample.recorded_at >= thirty_days_ago
    ).group_by(func.date(VoiceSample.recorded_at)).all()
    
    total_days = len(daily_counts)
    total_recent_recordings = sum(count for _, count in daily_counts)
    expected_recordings = total_days * 9 if total_days > 0 else 1
    compliance_rate = min(100, (total_recent_recordings / expected_recordings) * 100) if expected_recordings > 0 else 0
    
    # Get recent predictions (last 5)
    recent_preds = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.predicted_at.desc()).limit(5).all()
    
    # Normalize JSON fields before Pydantic validation (handles legacy string data)
    recent_predictions_response = [
        PredictionResponse.model_validate(_normalize_prediction_json_fields(p)) 
        for p in recent_preds
    ]
    
    # Get weekly trend data
    weekly_trend_data = []
    for i in range(7):
        day = now - timedelta(days=6-i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_predictions = db.query(Prediction).filter(
            Prediction.user_id == user_id,
            Prediction.predicted_at >= day_start,
            Prediction.predicted_at < day_end
        ).all()
        
        if day_predictions:
            weekly_trend_data.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "depression": sum(p.depression_score or 0 for p in day_predictions) / len(day_predictions),
                "anxiety": sum(p.anxiety_score or 0 for p in day_predictions) / len(day_predictions),
                "stress": sum(p.stress_score or 0 for p in day_predictions) / len(day_predictions),
                "mental_health_score": sum(p.mental_health_score or 0 for p in day_predictions) / len(day_predictions),
                "sample_count": len(day_predictions)
            })
        else:
            weekly_trend_data.append({
                "date": day_start.strftime("%Y-%m-%d"),
                "depression": 0,
                "anxiety": 0,
                "stress": 0,
                "mental_health_score": 0,
                "sample_count": 0
            })
    
    return DashboardResponse(
        user_id=user_id,
        current_risk_level=current_risk_level,
        risk_trend=risk_trend,
        compliance_rate=compliance_rate,
        total_recordings=total_recordings,
        recent_predictions=recent_predictions_response,
        weekly_trend_data=weekly_trend_data
    )

@router.get("/{user_id}/summary")
async def get_dashboard_summary(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get quick dashboard summary"""
    # Verify access
    if current_user.id != user_id and current_user.role not in ["super_admin", "psychologist", "hr_admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get latest prediction
    latest = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.predicted_at.desc()).first()
    
    # Get total recordings
    total_recordings = db.query(VoiceSample).filter(
        VoiceSample.user_id == user_id
    ).count()
    
    # Get total predictions
    total_predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).count()
    
    return {
        "user_id": user_id,
        "latest_risk_level": latest.overall_risk_level if latest else "unknown",
        "latest_mental_health_score": latest.mental_health_score if latest else None,
        "latest_prediction_date": latest.predicted_at.isoformat() if latest else None,
        "total_recordings": total_recordings,
        "total_predictions": total_predictions
    }
