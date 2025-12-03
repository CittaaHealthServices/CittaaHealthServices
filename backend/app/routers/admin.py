"""
Admin router for Vocalysis API
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional

from app.models.database import get_db
from app.models.user import User, UserRole
from app.models.prediction import Prediction
from app.models.voice_sample import VoiceSample
from app.routers.auth import get_current_user, require_role

router = APIRouter()

@router.get("/users")
async def get_all_users(
    role: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_role(["super_admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Get all users (admin only)"""
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    
    total = query.count()
    users = query.offset(offset).limit(limit).all()
    
    return {
        "total": total,
        "users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "role": u.role,
                "is_active": u.is_active,
                "is_clinical_trial_participant": u.is_clinical_trial_participant,
                "trial_status": u.trial_status,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login": u.last_login.isoformat() if u.last_login else None
            }
            for u in users
        ]
    }

@router.get("/pending-approvals")
async def get_pending_approvals(
    current_user: User = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    """Get users pending clinical trial approval"""
    pending_users = db.query(User).filter(
        User.is_clinical_trial_participant == True,
        User.trial_status == "pending"
    ).all()
    
    return {
        "count": len(pending_users),
        "pending_users": [
            {
                "id": u.id,
                "email": u.email,
                "full_name": u.full_name,
                "phone": u.phone,
                "age_range": u.age_range,
                "gender": u.gender,
                "created_at": u.created_at.isoformat() if u.created_at else None
            }
            for u in pending_users
        ]
    }

@router.post("/approve-participant/{user_id}")
async def approve_clinical_trial_participant(
    user_id: str,
    current_user: User = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    """Approve a user for clinical trial participation"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_clinical_trial_participant:
        raise HTTPException(status_code=400, detail="User has not registered for clinical trial")
    
    user.trial_status = "approved"
    user.approved_by = current_user.id
    user.approval_date = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"User {user.email} approved for clinical trial"}

@router.post("/reject-participant/{user_id}")
async def reject_clinical_trial_participant(
    user_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    """Reject a user for clinical trial participation"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.trial_status = "rejected"
    user.approved_by = current_user.id
    user.approval_date = datetime.utcnow()
    
    db.commit()
    
    return {"message": f"User {user.email} rejected for clinical trial", "reason": reason}

from pydantic import BaseModel

class AssignPsychologistRequest(BaseModel):
    patient_id: str
    psychologist_id: str

@router.post("/assign-psychologist")
async def assign_psychologist_to_patient(
    request: AssignPsychologistRequest,
    current_user: User = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
        """Assign a psychologist to a patient"""
        patient = db.query(User).filter(User.id == request.patient_id).first()
        psychologist = db.query(User).filter(
            User.id == request.psychologist_id,
            User.role == "psychologist"
        ).first()
    
        if not patient:
            raise HTTPException(status_code=404, detail="Patient not found")
        if not psychologist:
            raise HTTPException(status_code=404, detail="Psychologist not found")
    
        patient.assigned_psychologist_id = request.psychologist_id
        patient.assignment_date = datetime.utcnow()
    
        db.commit()
    
        return {
            "message": f"Psychologist {psychologist.email} assigned to patient {patient.email}",
            "patient_id": request.patient_id,
            "psychologist_id": request.psychologist_id
        }

@router.get("/statistics")
async def get_system_statistics(
    current_user: User = Depends(require_role(["super_admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Get system-wide statistics"""
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    
    # Users by role
    users_by_role = db.query(
        User.role,
        func.count(User.id)
    ).group_by(User.role).all()
    
    # Clinical trial stats
    trial_participants = db.query(User).filter(
        User.is_clinical_trial_participant == True
    ).count()
    approved_participants = db.query(User).filter(
        User.trial_status == "approved"
    ).count()
    pending_participants = db.query(User).filter(
        User.trial_status == "pending"
    ).count()
    
    # Voice samples and predictions
    total_voice_samples = db.query(VoiceSample).count()
    total_predictions = db.query(Prediction).count()
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_samples = db.query(VoiceSample).filter(
        VoiceSample.recorded_at >= week_ago
    ).count()
    recent_predictions = db.query(Prediction).filter(
        Prediction.predicted_at >= week_ago
    ).count()
    
    # Risk distribution
    risk_distribution = db.query(
        Prediction.overall_risk_level,
        func.count(Prediction.id)
    ).group_by(Prediction.overall_risk_level).all()
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "by_role": {role: count for role, count in users_by_role}
        },
        "clinical_trial": {
            "total_participants": trial_participants,
            "approved": approved_participants,
            "pending": pending_participants
        },
        "voice_analysis": {
            "total_samples": total_voice_samples,
            "total_predictions": total_predictions,
            "recent_samples_7d": recent_samples,
            "recent_predictions_7d": recent_predictions
        },
        "risk_distribution": {
            level or "unknown": count for level, count in risk_distribution
        }
    }

@router.get("/organization/{org_id}/metrics")
async def get_organization_metrics(
    org_id: str,
    current_user: User = Depends(require_role(["super_admin", "hr_admin"])),
    db: Session = Depends(get_db)
):
    """Get aggregated metrics for an organization (HR view)"""
    # Get organization users
    org_users = db.query(User).filter(User.organization_id == org_id).all()
    user_ids = [u.id for u in org_users]
    
    if not user_ids:
        return {
            "organization_id": org_id,
            "total_employees": 0,
            "message": "No users found for this organization"
        }
    
    # Get predictions for org users
    predictions = db.query(Prediction).filter(
        Prediction.user_id.in_(user_ids)
    ).all()
    
    # Calculate risk distribution
    risk_counts = {"low": 0, "moderate": 0, "high": 0, "unknown": 0}
    for p in predictions:
        level = p.overall_risk_level or "unknown"
        if level in risk_counts:
            risk_counts[level] += 1
        else:
            risk_counts["unknown"] += 1
    
    # Calculate compliance
    total_recordings = db.query(VoiceSample).filter(
        VoiceSample.user_id.in_(user_ids)
    ).count()
    
    active_users = len(set(p.user_id for p in predictions))
    
    return {
        "organization_id": org_id,
        "total_employees": len(org_users),
        "active_users": active_users,
        "total_recordings": total_recordings,
        "total_predictions": len(predictions),
        "risk_distribution": risk_counts,
        "compliance_rate": (active_users / len(org_users) * 100) if org_users else 0
    }

@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: str,
    new_role: str,
    current_user: User = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    """Update user role (super admin only)"""
    valid_roles = ["patient", "psychologist", "hr_admin", "super_admin", "researcher"]
    if new_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Valid roles: {valid_roles}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.role = new_role
    db.commit()
    
    return {"message": f"User role updated to {new_role}", "user_id": user_id}

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_role(["super_admin"])),
    db: Session = Depends(get_db)
):
    """Deactivate a user (super admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    user.is_active = False
    db.commit()
    
    return {"message": f"User {user.email} deactivated"}
