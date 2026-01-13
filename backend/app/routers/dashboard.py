"""
Dashboard router for Vocalysis API
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List, Dict, Any

from app.models.mongodb import get_mongodb
from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/{user_id}")
async def get_user_dashboard(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get comprehensive dashboard data for a user"""
    db = get_mongodb()
    
    # Verify access
    current_user_id = str(current_user.get("_id", current_user.get("id", "")))
    current_user_role = current_user.get("role", "")
        if current_user_id != user_id and current_user_role not in ["super_admin", "psychologist", "hr_admin", "admin"]:
            raise HTTPException(status_code=403, detail="Access denied")
    
        # Get latest prediction from MongoDB
        latest_prediction = db.predictions.find_one(
            {"user_id": user_id},
            sort=[("predicted_at", -1)]
        )
    
        current_risk_level = latest_prediction.get("overall_risk_level", "unknown") if latest_prediction else "unknown"
    
        # Calculate risk trend (comparing last 7 days vs previous 7 days)
        now = datetime.utcnow()
        recent_start = now - timedelta(days=7)
        previous_start = now - timedelta(days=14)
    
        recent_predictions = list(db.predictions.find({
            "user_id": user_id,
            "predicted_at": {"$gte": recent_start}
        }))
    
        previous_predictions = list(db.predictions.find({
            "user_id": user_id,
            "predicted_at": {"$gte": previous_start, "$lt": recent_start}
        }))
    
        # Calculate average scores
        def calc_avg_score(predictions):
            if not predictions:
                return None
            scores = []
            for p in predictions:
                avg = ((p.get("depression_score") or 0) + (p.get("anxiety_score") or 0) + (p.get("stress_score") or 0)) / 3
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
        total_recordings = db.voice_samples.count_documents({"user_id": user_id})
    
        # Count days with recordings in last 30 days
        thirty_days_ago = now - timedelta(days=30)
        voice_samples = list(db.voice_samples.find({
            "user_id": user_id,
            "recorded_at": {"$gte": thirty_days_ago}
        }))
    
        # Group by date
        daily_counts = {}
        for sample in voice_samples:
            recorded_at = sample.get("recorded_at")
            if recorded_at:
                date_key = recorded_at.strftime("%Y-%m-%d")
                daily_counts[date_key] = daily_counts.get(date_key, 0) + 1
    
        total_days = len(daily_counts)
        total_recent_recordings = sum(daily_counts.values())
        expected_recordings = total_days * 9 if total_days > 0 else 1
        compliance_rate = min(100, (total_recent_recordings / expected_recordings) * 100) if expected_recordings > 0 else 0
    
        # Get recent predictions (last 5)
        recent_preds = list(db.predictions.find(
            {"user_id": user_id}
        ).sort("predicted_at", -1).limit(5))
    
        recent_predictions_response = [
            {
                "id": str(p.get("_id", "")),
                "user_id": p.get("user_id", ""),
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
                "predicted_at": p.get("predicted_at").isoformat() if p.get("predicted_at") else None
            }
            for p in recent_preds
        ]
    
        # Get weekly trend data
        weekly_trend_data = []
        for i in range(7):
            day = now - timedelta(days=6-i)
            day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
            day_end = day_start + timedelta(days=1)
        
            day_predictions = list(db.predictions.find({
                "user_id": user_id,
                "predicted_at": {"$gte": day_start, "$lt": day_end}
            }))
        
            if day_predictions:
                weekly_trend_data.append({
                    "date": day_start.strftime("%Y-%m-%d"),
                    "depression": sum(p.get("depression_score") or 0 for p in day_predictions) / len(day_predictions),
                    "anxiety": sum(p.get("anxiety_score") or 0 for p in day_predictions) / len(day_predictions),
                    "stress": sum(p.get("stress_score") or 0 for p in day_predictions) / len(day_predictions),
                    "mental_health_score": sum(p.get("mental_health_score") or 0 for p in day_predictions) / len(day_predictions),
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
    
        return {
            "user_id": user_id,
            "current_risk_level": current_risk_level,
            "risk_trend": risk_trend,
            "compliance_rate": compliance_rate,
            "total_recordings": total_recordings,
            "recent_predictions": recent_predictions_response,
            "weekly_trend_data": weekly_trend_data
        }

@router.get("/{user_id}/summary")
async def get_dashboard_summary(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get quick dashboard summary"""
    db = get_mongodb()
    
    # Verify access
    current_user_id = str(current_user.get("_id", current_user.get("id", "")))
    current_user_role = current_user.get("role", "")
    if current_user_id != user_id and current_user_role not in ["super_admin", "psychologist", "hr_admin", "admin"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Get latest prediction from MongoDB
    latest = db.predictions.find_one(
        {"user_id": user_id},
        sort=[("predicted_at", -1)]
    )
    
    # Get total recordings
    total_recordings = db.voice_samples.count_documents({"user_id": user_id})
    
    # Get total predictions
    total_predictions = db.predictions.count_documents({"user_id": user_id})
    
    return {
        "user_id": user_id,
        "latest_risk_level": latest.get("overall_risk_level", "unknown") if latest else "unknown",
        "latest_mental_health_score": latest.get("mental_health_score") if latest else None,
        "latest_prediction_date": latest.get("predicted_at").isoformat() if latest and latest.get("predicted_at") else None,
        "total_recordings": total_recordings,
        "total_predictions": total_predictions
    }
