"""
Admin router for Vocalysis API - Supreme Admin Portal
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, EmailStr
import uuid
import secrets
import hashlib

from app.models.database import get_db, sync_user_to_mongodb, get_mongo_client
from app.models.user import User, UserRole
from app.models.prediction import Prediction
from app.models.voice_sample import VoiceSample
from app.routers.auth import get_current_user, require_role, get_password_hash
from app.services.email_service import email_service

router = APIRouter()

# Pydantic models for admin operations
class CreateUserRequest(BaseModel):
    email: EmailStr
    full_name: str
    role: str = "patient"
    phone: Optional[str] = None
    send_welcome_email: bool = True

class UpdateUserRequest(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class AssignPsychologistRequest(BaseModel):
    patient_id: str
    psychologist_id: str

class AuditLog(BaseModel):
    id: str
    user_id: str
    user_email: str
    action: str
    entity_type: str
    entity_id: Optional[str]
    details: Optional[str]
    ip_address: Optional[str]
    timestamp: datetime

# In-memory audit log storage (fallback if MongoDB unavailable)
audit_logs = []

def log_admin_action(admin_user: User, action: str, entity_type: str, entity_id: str = None, details: str = None):
    """Log an admin action for audit trail - persists to MongoDB"""
    log_entry = {
        "id": str(uuid.uuid4()),
        "user_id": admin_user.id,
        "user_email": admin_user.email,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details,
        "ip_address": None,
        "timestamp": datetime.utcnow()
    }
    
    # Persist to MongoDB for permanent storage
    db = get_mongo_client()
    if db is not None:
        try:
            db.audit_logs.insert_one(log_entry.copy())
            print(f"[AUDIT LOG] Saved to MongoDB: {action} by {admin_user.email}")
        except Exception as e:
            print(f"[AUDIT LOG] MongoDB save failed: {e}")
            # Fallback to in-memory
            audit_logs.append(log_entry)
    else:
        # Fallback to in-memory if MongoDB not available
        audit_logs.append(log_entry)
        if len(audit_logs) > 1000:
            audit_logs.pop(0)
    
    return log_entry

@router.get("/users")
async def get_all_users(
    role: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_role(["super_admin", "hr_admin", "admin"])),
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
                "assigned_psychologist_id": u.assigned_psychologist_id,
                "assignment_date": u.assignment_date.isoformat() if u.assignment_date else None,
                "created_at": u.created_at.isoformat() if u.created_at else None,
                "last_login": u.last_login.isoformat() if u.last_login else None
            }
            for u in users
        ]
    }

@router.get("/pending-approvals")
async def get_pending_approvals(
    current_user: User = Depends(require_role(["super_admin", "admin"])),
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
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Approve a user for clinical trial participation"""
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.is_clinical_trial_participant:
        raise HTTPException(status_code=400, detail="User has not registered for clinical trial")
    
    user.trial_status = "approved"
    user.is_active = True  # Activate user upon approval
    user.approved_by = current_user.id
    user.approval_date = datetime.utcnow()
    
    db.commit()
    
    # Sync to MongoDB
    try:
        sync_user_to_mongodb(user)
    except Exception as e:
        print(f"Failed to sync user to MongoDB: {e}")
    
    # Send approval email
    try:
        # Get assigned psychologist name if available
        psychologist_name = None
        if user.assigned_psychologist_id:
            psychologist = db.query(User).filter(User.id == user.assigned_psychologist_id).first()
            if psychologist:
                psychologist_name = psychologist.full_name
        
        email_service.send_trial_approval_email(user.email, user.full_name, psychologist_name)
    except Exception as e:
        print(f"Failed to send approval email: {e}")
    
    return {"message": f"User {user.email} approved for clinical trial"}

@router.post("/reject-participant/{user_id}")
async def reject_clinical_trial_participant(
    user_id: str,
    reason: Optional[str] = None,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
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

@router.post("/assign-psychologist")
async def assign_psychologist_to_patient(
    request: Optional[AssignPsychologistRequest] = None,
    patient_id: Optional[str] = None,
    psychologist_id: Optional[str] = None,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Assign a psychologist to a patient"""
    # Prefer JSON body, fallback to query params for backward compatibility
    if request is not None:
        patient_id = request.patient_id
        psychologist_id = request.psychologist_id
    
    if not patient_id or not psychologist_id:
        raise HTTPException(
            status_code=400,
            detail="patient_id and psychologist_id are required"
        )
    
    patient = db.query(User).filter(User.id == patient_id).first()
    psychologist = db.query(User).filter(
        User.id == psychologist_id,
        User.role == "psychologist"
    ).first()
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    
    patient.assigned_psychologist_id = psychologist_id
    patient.assignment_date = datetime.utcnow()
    
    db.commit()
    
    # Sync to MongoDB for permanent storage
    sync_user_to_mongodb({
        "id": patient.id,
        "email": patient.email,
        "password_hash": patient.password_hash,
        "full_name": patient.full_name,
        "role": patient.role,
        "is_active": patient.is_active,
        "phone": patient.phone,
        "assigned_psychologist_id": patient.assigned_psychologist_id
    })
    
    # Log the admin action
    log_admin_action(
        current_user,
        "ASSIGN_PSYCHOLOGIST",
        "user",
        patient_id,
        f"Assigned psychologist {psychologist.email} to patient {patient.email}"
    )
    
    return {
        "message": f"Psychologist {psychologist.email} assigned to patient {patient.email}",
        "patient_id": patient_id,
        "psychologist_id": psychologist_id
    }

@router.get("/statistics")
async def get_system_statistics(
    current_user: User = Depends(require_role(["super_admin", "hr_admin", "admin"])),
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
    current_user: User = Depends(require_role(["super_admin", "hr_admin", "admin"])),
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
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Update user role (super admin only)"""
    valid_roles = ["patient", "psychologist", "hr_admin", "super_admin", "admin", "researcher"]
    if new_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Valid roles: {valid_roles}")
    
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = user.role
    user.role = new_role
    db.commit()
    
    # Sync to MongoDB for permanent storage
    sync_user_to_mongodb({
        "id": user.id,
        "email": user.email,
        "password_hash": user.password_hash,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "phone": user.phone
    })
    
    # Log the action
    log_admin_action(current_user, "UPDATE_ROLE", "user", user_id, f"Changed role from {old_role} to {new_role}")
    
    return {"message": f"User role updated to {new_role}", "user_id": user_id}

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Deactivate a user (admin only)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    user.is_active = False
    db.commit()
    
    # Sync to MongoDB for permanent storage
    sync_user_to_mongodb({
        "id": user.id,
        "email": user.email,
        "password_hash": user.password_hash,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "phone": user.phone
    })
    
    # Log the action
    log_admin_action(current_user, "DEACTIVATE_USER", "user", user_id, f"Deactivated user {user.email}")
    
    return {"message": f"User {user.email} deactivated"}

# ==================== NEW SUPREME ADMIN ENDPOINTS ====================

@router.post("/users")
async def create_user(
    request: CreateUserRequest,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Create a new user from admin portal"""
    valid_roles = ["patient", "psychologist", "hr_admin", "super_admin", "admin", "researcher"]
    if request.role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Valid roles: {valid_roles}")
    
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == request.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate a random password
    temp_password = secrets.token_urlsafe(12)
    
    # Create the user
    new_user = User(
        id=str(uuid.uuid4()),
        email=request.email,
        full_name=request.full_name,
        password_hash=get_password_hash(temp_password),
        role=request.role,
        phone=request.phone,
        is_active=True,
        created_at=datetime.utcnow()
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Sync to MongoDB for permanent storage
    sync_user_to_mongodb({
        "id": new_user.id,
        "email": new_user.email,
        "password_hash": new_user.password_hash,
        "full_name": new_user.full_name,
        "role": new_user.role,
        "is_active": new_user.is_active,
        "phone": new_user.phone
    })
    
    # Log the action
    log_admin_action(current_user, "CREATE_USER", "user", new_user.id, f"Created user {request.email} with role {request.role}")
    
    # Send welcome email with temporary password
    if request.send_welcome_email:
        try:
            email_service.send_admin_created_account_email(request.email, request.full_name, temp_password, request.role)
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
    
    return {
        "message": f"User {request.email} created successfully",
        "user_id": new_user.id,
        "temporary_password": temp_password,
        "email_sent": request.send_welcome_email
    }

@router.put("/users/{user_id}")
async def update_user(
    user_id: str,
    request: UpdateUserRequest,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Update user details"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    changes = []
    if request.full_name is not None:
        user.full_name = request.full_name
        changes.append(f"name={request.full_name}")
    if request.phone is not None:
        user.phone = request.phone
        changes.append(f"phone={request.phone}")
    if request.is_active is not None:
        user.is_active = request.is_active
        changes.append(f"is_active={request.is_active}")
    
    db.commit()
    
    # Sync to MongoDB for permanent storage
    sync_user_to_mongodb({
        "id": user.id,
        "email": user.email,
        "password_hash": user.password_hash,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "phone": user.phone
    })
    
    # Log the action
    log_admin_action(current_user, "UPDATE_USER", "user", user_id, f"Updated user {user.email}: {', '.join(changes)}")
    
    return {"message": f"User {user.email} updated", "changes": changes}

@router.post("/users/{user_id}/reactivate")
async def reactivate_user(
    user_id: str,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Reactivate a deactivated user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if user.is_active:
        raise HTTPException(status_code=400, detail="User is already active")
    
    user.is_active = True
    db.commit()
    
    # Sync to MongoDB for permanent storage
    sync_user_to_mongodb({
        "id": user.id,
        "email": user.email,
        "password_hash": user.password_hash,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "phone": user.phone
    })
    
    # Log the action
    log_admin_action(current_user, "REACTIVATE_USER", "user", user_id, f"Reactivated user {user.email}")
    
    return {"message": f"User {user.email} reactivated"}

@router.post("/users/{user_id}/reset-password")
async def admin_reset_user_password(
    user_id: str,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Reset a user's password and send them a new temporary password"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate new temporary password
    temp_password = secrets.token_urlsafe(12)
    user.password_hash = get_password_hash(temp_password)
    db.commit()
    
    # Sync to MongoDB for permanent storage
    sync_user_to_mongodb({
        "id": user.id,
        "email": user.email,
        "password_hash": user.password_hash,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "phone": user.phone
    })
    
    # Log the action
    log_admin_action(current_user, "RESET_PASSWORD", "user", user_id, f"Reset password for user {user.email}")
    
    # Send email with new password
    try:
        email_service.send_password_reset_notification(user.email, user.full_name, temp_password)
    except Exception as e:
        print(f"Failed to send password reset email: {e}")
    
    return {
        "message": f"Password reset for {user.email}",
        "temporary_password": temp_password
    }

@router.get("/audit-logs")
async def get_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_email: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Get audit logs with optional filtering - reads from MongoDB"""
    mongo_db = get_mongo_client()
    
    if mongo_db is not None:
        try:
            # Build MongoDB query
            query = {}
            if action:
                query["action"] = action
            if entity_type:
                query["entity_type"] = entity_type
            if user_email:
                query["user_email"] = {"$regex": user_email, "$options": "i"}
            
            # Get total count
            total = mongo_db.audit_logs.count_documents(query)
            
            # Get paginated logs sorted by timestamp descending
            cursor = mongo_db.audit_logs.find(query).sort("timestamp", -1).skip(offset).limit(limit)
            logs_list = list(cursor)
            
            return {
                "total": total,
                "logs": [
                    {
                        "id": log.get("id", str(log.get("_id", ""))),
                        "user_id": log.get("user_id"),
                        "user_email": log.get("user_email"),
                        "action": log.get("action"),
                        "entity_type": log.get("entity_type"),
                        "entity_id": log.get("entity_id"),
                        "details": log.get("details"),
                        "ip_address": log.get("ip_address"),
                        "timestamp": log["timestamp"].isoformat() if isinstance(log.get("timestamp"), datetime) else log.get("timestamp")
                    }
                    for log in logs_list
                ]
            }
        except Exception as e:
            print(f"[AUDIT LOG] MongoDB read failed: {e}")
            # Fall through to in-memory fallback
    
    # Fallback to in-memory logs if MongoDB unavailable
    filtered_logs = audit_logs.copy()
    
    if action:
        filtered_logs = [l for l in filtered_logs if l["action"] == action]
    if entity_type:
        filtered_logs = [l for l in filtered_logs if l["entity_type"] == entity_type]
    if user_email:
        filtered_logs = [l for l in filtered_logs if user_email.lower() in l["user_email"].lower()]
    
    # Sort by timestamp descending
    filtered_logs.sort(key=lambda x: x["timestamp"], reverse=True)
    
    total = len(filtered_logs)
    paginated_logs = filtered_logs[offset:offset + limit]
    
    return {
        "total": total,
        "logs": [
            {
                **log,
                "timestamp": log["timestamp"].isoformat() if isinstance(log["timestamp"], datetime) else log["timestamp"]
            }
            for log in paginated_logs
        ]
    }

@router.get("/voice-analyses")
async def get_all_voice_analyses(
    user_id: Optional[str] = None,
    risk_level: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Get all voice analyses with optional filtering"""
    query = db.query(Prediction).order_by(desc(Prediction.predicted_at))
    
    if user_id:
        query = query.filter(Prediction.user_id == user_id)
    if risk_level:
        query = query.filter(Prediction.overall_risk_level == risk_level)
    
    total = query.count()
    predictions = query.offset(offset).limit(limit).all()
    
    # Get user emails for display
    user_ids = list(set(p.user_id for p in predictions))
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {u.id: u.email for u in users}
    
    return {
        "total": total,
        "analyses": [
            {
                "id": p.id,
                "user_id": p.user_id,
                "user_email": user_map.get(p.user_id, "Unknown"),
                "mental_health_score": p.mental_health_score,
                "confidence": p.confidence,
                "overall_risk_level": p.overall_risk_level,
                "phq9_score": p.phq9_score,
                "gad7_score": p.gad7_score,
                "pss_score": p.pss_score,
                "wemwbs_score": p.wemwbs_score,
                "predicted_at": p.predicted_at.isoformat() if p.predicted_at else None,
                "processing_time_ms": p.processing_time_ms
            }
            for p in predictions
        ]
    }

@router.get("/voice-samples")
async def get_all_voice_samples(
    user_id: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Get all voice samples with optional filtering"""
    query = db.query(VoiceSample).order_by(desc(VoiceSample.recorded_at))
    
    if user_id:
        query = query.filter(VoiceSample.user_id == user_id)
    
    total = query.count()
    samples = query.offset(offset).limit(limit).all()
    
    # Get user emails for display
    user_ids = list(set(s.user_id for s in samples))
    users = db.query(User).filter(User.id.in_(user_ids)).all()
    user_map = {u.id: u.email for u in users}
    
    return {
        "total": total,
        "samples": [
            {
                "id": s.id,
                "user_id": s.user_id,
                "user_email": user_map.get(s.user_id, "Unknown"),
                "duration_seconds": s.duration_seconds,
                "sample_rate": s.sample_rate,
                "file_size_bytes": s.file_size_bytes,
                "recorded_at": s.recorded_at.isoformat() if s.recorded_at else None,
                "is_processed": s.is_processed
            }
            for s in samples
        ]
    }

@router.get("/psychologists")
async def get_all_psychologists(
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Get all psychologists for assignment dropdown"""
    psychologists = db.query(User).filter(
        User.role == "psychologist",
        User.is_active == True
    ).all()
    
    return {
        "psychologists": [
            {
                "id": p.id,
                "email": p.email,
                "full_name": p.full_name,
                "phone": p.phone
            }
            for p in psychologists
        ]
    }

@router.get("/users/{user_id}/details")
async def get_user_details(
    user_id: str,
    current_user: User = Depends(require_role(["super_admin", "admin"])),
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific user"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Get user's voice samples count
    samples_count = db.query(VoiceSample).filter(VoiceSample.user_id == user_id).count()
    
    # Get user's predictions count
    predictions_count = db.query(Prediction).filter(Prediction.user_id == user_id).count()
    
    # Get latest prediction
    latest_prediction = db.query(Prediction).filter(
        Prediction.user_id == user_id
    ).order_by(desc(Prediction.predicted_at)).first()
    
    # Get assigned psychologist if any
    assigned_psychologist = None
    if user.assigned_psychologist_id:
        psych = db.query(User).filter(User.id == user.assigned_psychologist_id).first()
        if psych:
            assigned_psychologist = {
                "id": psych.id,
                "email": psych.email,
                "full_name": psych.full_name
            }
    
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        "is_active": user.is_active,
        "is_clinical_trial_participant": user.is_clinical_trial_participant,
        "trial_status": user.trial_status,
        "created_at": user.created_at.isoformat() if user.created_at else None,
        "last_login": user.last_login.isoformat() if user.last_login else None,
        "assigned_psychologist": assigned_psychologist,
        "statistics": {
            "voice_samples": samples_count,
            "predictions": predictions_count,
            "latest_risk_level": latest_prediction.overall_risk_level if latest_prediction else None,
            "latest_analysis_date": latest_prediction.predicted_at.isoformat() if latest_prediction else None
        }
    }
