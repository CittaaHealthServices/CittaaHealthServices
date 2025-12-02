"""
Predictions router for Vocalysis API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.database import get_db
from app.models.user import User
from app.models.prediction import Prediction
from app.models.voice_sample import VoiceSample
from app.schemas.prediction import PredictionResponse, DashboardResponse, TrendDataPoint
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/{user_id}", response_model=List[PredictionResponse])
async def get_user_predictions(
    user_id: str,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get prediction history for a user"""
    # Verify user can only access their own data (unless admin/psychologist)
    if current_user.id != user_id and current_user.role not in ["super_admin", "psychologist", "hr_admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # If psychologist, verify they are assigned to this patient
    if current_user.role == "psychologist":
        patient = db.query(User).filter(User.id == user_id).first()
        if not patient or patient.assigned_psychologist_id != current_user.id:
            raise HTTPException(status_code=403, detail="Not assigned to this patient")
    
    predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.predicted_at.desc()).limit(limit).all()
    
    return [PredictionResponse.model_validate(p) for p in predictions]

@router.get("/{user_id}/latest", response_model=PredictionResponse)
async def get_latest_prediction(
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get latest prediction for a user"""
    # Verify access
    if current_user.id != user_id and current_user.role not in ["super_admin", "psychologist", "hr_admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    prediction = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(Prediction.predicted_at.desc()).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="No predictions found")
    
    return PredictionResponse.model_validate(prediction)

@router.get("/{user_id}/trends")
async def get_prediction_trends(
    user_id: str,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get prediction trends over time"""
    # Verify access
    if current_user.id != user_id and current_user.role not in ["super_admin", "psychologist", "hr_admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    predictions = db.query(Prediction).filter(
        Prediction.user_id == user_id,
        Prediction.predicted_at >= start_date
    ).order_by(Prediction.predicted_at.asc()).all()
    
    # Group by date
    trend_data = {}
    for pred in predictions:
        date_key = pred.predicted_at.strftime("%Y-%m-%d")
        if date_key not in trend_data:
            trend_data[date_key] = {
                "date": date_key,
                "depression_scores": [],
                "anxiety_scores": [],
                "stress_scores": [],
                "mental_health_scores": [],
                "count": 0
            }
        
        trend_data[date_key]["depression_scores"].append(pred.depression_score or 0)
        trend_data[date_key]["anxiety_scores"].append(pred.anxiety_score or 0)
        trend_data[date_key]["stress_scores"].append(pred.stress_score or 0)
        trend_data[date_key]["mental_health_scores"].append(pred.mental_health_score or 0)
        trend_data[date_key]["count"] += 1
    
    # Calculate averages
    result = []
    for date_key, data in sorted(trend_data.items()):
        result.append({
            "date": data["date"],
            "depression": sum(data["depression_scores"]) / len(data["depression_scores"]) if data["depression_scores"] else 0,
            "anxiety": sum(data["anxiety_scores"]) / len(data["anxiety_scores"]) if data["anxiety_scores"] else 0,
            "stress": sum(data["stress_scores"]) / len(data["stress_scores"]) if data["stress_scores"] else 0,
            "mental_health_score": sum(data["mental_health_scores"]) / len(data["mental_health_scores"]) if data["mental_health_scores"] else 0,
            "sample_count": data["count"]
        })
    
    return result

@router.get("/{prediction_id}/details", response_model=PredictionResponse)
async def get_prediction_details(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get detailed prediction information"""
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Verify access
    if prediction.user_id != current_user.id and current_user.role not in ["super_admin", "psychologist", "hr_admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return PredictionResponse.model_validate(prediction)

@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a prediction (admin only)"""
    if current_user.role != "super_admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    prediction = db.query(Prediction).filter(Prediction.id == prediction_id).first()
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    db.delete(prediction)
    db.commit()
    
    return {"message": "Prediction deleted successfully"}
