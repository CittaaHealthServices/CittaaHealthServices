"""
Predictions router for Vocalysis API
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any

from app.models.mongodb import get_mongodb
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/{user_id}")
async def get_user_predictions(
    user_id: str,
    limit: int = 10,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get prediction history for a user"""
    db = get_mongodb()
    
    # Verify user can only access their own data (unless admin/psychologist)
    current_user_id = str(current_user.get("_id", current_user.get("id", "")))
    current_user_role = current_user.get("role", "")
    if current_user_id != user_id and current_user_role not in ["super_admin", "psychologist", "hr_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # If psychologist, verify they are assigned to this patient
    if current_user_role == "psychologist":
        patient = db.users.find_one({"_id": user_id})
        if not patient or patient.get("assigned_psychologist_id") != current_user_id:
            raise HTTPException(status_code=403, detail="Not assigned to this patient")
    
    predictions = list(db.predictions.find(
        {"user_id": user_id}
    ).sort("predicted_at", -1).limit(limit))
    
    return [
        {
            "id": str(p.get("_id", "")),
            "user_id": p.get("user_id", ""),
            "voice_sample_id": p.get("voice_sample_id"),
            "depression_score": p.get("depression_score"),
            "anxiety_score": p.get("anxiety_score"),
            "stress_score": p.get("stress_score"),
            "overall_risk_level": p.get("overall_risk_level"),
            "mental_health_score": p.get("mental_health_score"),
            "confidence": p.get("confidence"),
            "phq9_score": p.get("phq9_score"),
            "gad7_score": p.get("gad7_score"),
            "pss_score": p.get("pss_score"),
            "wemwbs_score": p.get("wemwbs_score"),
            "interpretations": p.get("interpretations", []),
            "recommendations": p.get("recommendations", []),
            "predicted_at": p.get("predicted_at").isoformat() if p.get("predicted_at") else None
        }
        for p in predictions
    ]

@router.get("/{user_id}/latest")
async def get_latest_prediction(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get latest prediction for a user"""
    db = get_mongodb()
    
    # Verify access
    current_user_id = str(current_user.get("_id", current_user.get("id", "")))
    current_user_role = current_user.get("role", "")
    if current_user_id != user_id and current_user_role not in ["super_admin", "psychologist", "hr_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    prediction = db.predictions.find_one(
        {"user_id": user_id},
        sort=[("predicted_at", -1)]
    )
    
    if not prediction:
        raise HTTPException(status_code=404, detail="No predictions found")
    
    return {
        "id": str(prediction.get("_id", "")),
        "user_id": prediction.get("user_id", ""),
        "voice_sample_id": prediction.get("voice_sample_id"),
        "depression_score": prediction.get("depression_score"),
        "anxiety_score": prediction.get("anxiety_score"),
        "stress_score": prediction.get("stress_score"),
        "overall_risk_level": prediction.get("overall_risk_level"),
        "mental_health_score": prediction.get("mental_health_score"),
        "confidence": prediction.get("confidence"),
        "phq9_score": prediction.get("phq9_score"),
        "gad7_score": prediction.get("gad7_score"),
        "pss_score": prediction.get("pss_score"),
        "wemwbs_score": prediction.get("wemwbs_score"),
        "interpretations": prediction.get("interpretations", []),
        "recommendations": prediction.get("recommendations", []),
        "predicted_at": prediction.get("predicted_at").isoformat() if prediction.get("predicted_at") else None
    }

@router.get("/{user_id}/trends")
async def get_prediction_trends(
    user_id: str,
    days: int = 30,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get prediction trends over time"""
    db = get_mongodb()
    
    # Verify access
    current_user_id = str(current_user.get("_id", current_user.get("id", "")))
    current_user_role = current_user.get("role", "")
    if current_user_id != user_id and current_user_role not in ["super_admin", "psychologist", "hr_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    predictions = list(db.predictions.find({
        "user_id": user_id,
        "predicted_at": {"$gte": start_date}
    }).sort("predicted_at", 1))
    
    # Group by date
    trend_data = {}
    for pred in predictions:
        predicted_at = pred.get("predicted_at")
        if not predicted_at:
            continue
        date_key = predicted_at.strftime("%Y-%m-%d")
        if date_key not in trend_data:
            trend_data[date_key] = {
                "date": date_key,
                "depression_scores": [],
                "anxiety_scores": [],
                "stress_scores": [],
                "mental_health_scores": [],
                "count": 0
            }
        
        trend_data[date_key]["depression_scores"].append(pred.get("depression_score") or 0)
        trend_data[date_key]["anxiety_scores"].append(pred.get("anxiety_score") or 0)
        trend_data[date_key]["stress_scores"].append(pred.get("stress_score") or 0)
        trend_data[date_key]["mental_health_scores"].append(pred.get("mental_health_score") or 0)
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

@router.get("/{prediction_id}/details")
async def get_prediction_details(
    prediction_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get detailed prediction information"""
    db = get_mongodb()
    
    from bson import ObjectId
    try:
        prediction = db.predictions.find_one({"_id": ObjectId(prediction_id)})
    except:
        prediction = db.predictions.find_one({"_id": prediction_id})
    
    if not prediction:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    # Verify access
    current_user_id = str(current_user.get("_id", current_user.get("id", "")))
    current_user_role = current_user.get("role", "")
    if prediction.get("user_id") != current_user_id and current_user_role not in ["super_admin", "psychologist", "hr_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": str(prediction.get("_id", "")),
        "user_id": prediction.get("user_id", ""),
        "voice_sample_id": prediction.get("voice_sample_id"),
        "depression_score": prediction.get("depression_score"),
        "anxiety_score": prediction.get("anxiety_score"),
        "stress_score": prediction.get("stress_score"),
        "overall_risk_level": prediction.get("overall_risk_level"),
        "mental_health_score": prediction.get("mental_health_score"),
        "confidence": prediction.get("confidence"),
        "phq9_score": prediction.get("phq9_score"),
        "gad7_score": prediction.get("gad7_score"),
        "pss_score": prediction.get("pss_score"),
        "wemwbs_score": prediction.get("wemwbs_score"),
        "interpretations": prediction.get("interpretations", []),
        "recommendations": prediction.get("recommendations", []),
        "predicted_at": prediction.get("predicted_at").isoformat() if prediction.get("predicted_at") else None
    }

@router.delete("/{prediction_id}")
async def delete_prediction(
    prediction_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Delete a prediction (admin only)"""
    db = get_mongodb()
    
    current_user_role = current_user.get("role", "")
    if current_user_role not in ["super_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    from bson import ObjectId
    try:
        result = db.predictions.delete_one({"_id": ObjectId(prediction_id)})
    except:
        result = db.predictions.delete_one({"_id": prediction_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Prediction not found")
    
    return {"message": "Prediction deleted successfully"}
