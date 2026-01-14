"""
Admin router for Vocalysis API - MongoDB Version
"""

from fastapi import APIRouter, Depends, HTTPException
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)

from app.models.mongodb import get_mongodb
from app.routers.auth import get_current_user_from_token, require_role
from app.services.email_service import email_service
from bson import ObjectId

router = APIRouter()

@router.get("/users")
async def get_all_users(
    role: Optional[str] = None,
    limit: int = 500,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "hr_admin", "admin"]))
):
    """Get all users (admin only)"""
    db = get_mongodb()
    
    query = {}
    if role:
        query["role"] = role
    
    total = db.users.count_documents(query)
    users = list(db.users.find(query).skip(offset).limit(limit))
    
    return {
        "total": total,
        "users": [
            {
                "id": str(u.get("_id", "")),
                "email": u.get("email", ""),
                "full_name": u.get("full_name", ""),
                "role": u.get("role", ""),
                "is_active": u.get("is_active", True),
                "is_clinical_trial_participant": u.get("is_clinical_trial_participant", False),
                "trial_status": u.get("trial_status"),
                "created_at": u.get("created_at").isoformat() if u.get("created_at") else None,
                "last_login": u.get("last_login").isoformat() if u.get("last_login") else None
            }
            for u in users
        ]
    }

@router.get("/pending-approvals")
async def get_pending_approvals(
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Get users pending clinical trial approval"""
    db = get_mongodb()
    
    pending_users = list(db.users.find({
        "is_clinical_trial_participant": True,
        "trial_status": "pending"
    }))
    
    return {
        "count": len(pending_users),
        "pending_users": [
            {
                "id": str(u.get("_id", "")),
                "email": u.get("email", ""),
                "full_name": u.get("full_name", ""),
                "phone": u.get("phone"),
                "age_range": u.get("age_range"),
                "gender": u.get("gender"),
                "created_at": u.get("created_at").isoformat() if u.get("created_at") else None
            }
            for u in pending_users
        ]
    }

@router.post("/approve-participant/{user_id}")
async def approve_clinical_trial_participant(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Approve a user for clinical trial participation"""
    db = get_mongodb()
    
    user = db.users.find_one({"_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if not user.get("is_clinical_trial_participant"):
        raise HTTPException(status_code=400, detail="User has not registered for clinical trial")
    
    db.users.update_one(
        {"_id": user_id},
        {"$set": {
            "trial_status": "approved",
            "approved_by": str(current_user.get("_id", "")),
            "approval_date": datetime.utcnow()
        }}
    )
    
    # Send approval email
    try:
        psychologist_name = None
        if user.get("assigned_psychologist_id"):
            psychologist = db.users.find_one({"_id": user.get("assigned_psychologist_id")})
            if psychologist:
                psychologist_name = psychologist.get("full_name")
        
        email_service.send_trial_approval_email(user.get("email"), user.get("full_name"), psychologist_name)
    except Exception as e:
        print(f"Failed to send approval email: {e}")
    
    return {"message": f"User {user.get('email')} approved for clinical trial"}

@router.post("/reject-participant/{user_id}")
async def reject_clinical_trial_participant(
    user_id: str,
    reason: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Reject a user for clinical trial participation"""
    db = get_mongodb()
    
    user = db.users.find_one({"_id": user_id})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.users.update_one(
        {"_id": user_id},
        {"$set": {
            "trial_status": "rejected",
            "approved_by": str(current_user.get("_id", "")),
            "approval_date": datetime.utcnow(),
            "rejection_reason": reason
        }}
    )
    
    return {"message": f"User {user.get('email')} rejected for clinical trial", "reason": reason}

@router.post("/assign-psychologist")
async def assign_psychologist_to_patient(
    patient_id: str,
    psychologist_id: str,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Assign a psychologist to a patient"""
    db = get_mongodb()
    
    patient = db.users.find_one({"_id": patient_id})
    psychologist = db.users.find_one({"_id": psychologist_id, "role": "psychologist"})
    
    if not patient:
        raise HTTPException(status_code=404, detail="Patient not found")
    if not psychologist:
        raise HTTPException(status_code=404, detail="Psychologist not found")
    
    db.users.update_one(
        {"_id": patient_id},
        {"$set": {
            "assigned_psychologist_id": psychologist_id,
            "assignment_date": datetime.utcnow()
        }}
    )
    
    return {
        "message": f"Psychologist {psychologist.get('email')} assigned to patient {patient.get('email')}",
        "patient_id": patient_id,
        "psychologist_id": psychologist_id
    }

@router.get("/statistics")
async def get_system_statistics(
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "hr_admin", "admin"]))
):
    """Get system-wide statistics"""
    db = get_mongodb()
    
    total_users = db.users.count_documents({})
    active_users = db.users.count_documents({"is_active": True})
    
    # Users by role
    role_pipeline = [
        {"$group": {"_id": "$role", "count": {"$sum": 1}}}
    ]
    users_by_role = {doc["_id"]: doc["count"] for doc in db.users.aggregate(role_pipeline)}
    
    # Clinical trial stats
    trial_participants = db.users.count_documents({"is_clinical_trial_participant": True})
    approved_participants = db.users.count_documents({"trial_status": "approved"})
    pending_participants = db.users.count_documents({"trial_status": "pending"})
    
    # Voice samples and predictions
    total_voice_samples = db.voice_samples.count_documents({})
    total_predictions = db.predictions.count_documents({})
    
    # Recent activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    recent_samples = db.voice_samples.count_documents({"recorded_at": {"$gte": week_ago}})
    recent_predictions = db.predictions.count_documents({"predicted_at": {"$gte": week_ago}})
    
    # Risk distribution
    risk_pipeline = [
        {"$group": {"_id": "$overall_risk_level", "count": {"$sum": 1}}}
    ]
    risk_distribution = {doc["_id"] or "unknown": doc["count"] for doc in db.predictions.aggregate(risk_pipeline)}
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "by_role": users_by_role
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
        "risk_distribution": risk_distribution
    }

@router.get("/organization/{org_id}/metrics")
async def get_organization_metrics(
    org_id: str,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "hr_admin", "admin"]))
):
    """Get aggregated metrics for an organization (HR view)"""
    db = get_mongodb()
    
    # Get organization users
    org_users = list(db.users.find({"organization_id": org_id}))
    user_ids = [str(u.get("_id", "")) for u in org_users]
    
    if not user_ids:
        return {
            "organization_id": org_id,
            "total_employees": 0,
            "message": "No users found for this organization"
        }
    
    # Get predictions for org users
    predictions = list(db.predictions.find({"user_id": {"$in": user_ids}}))
    
    # Calculate risk distribution
    risk_counts = {"low": 0, "moderate": 0, "high": 0, "unknown": 0}
    for p in predictions:
        level = p.get("overall_risk_level") or "unknown"
        if level in risk_counts:
            risk_counts[level] += 1
        else:
            risk_counts["unknown"] += 1
    
    # Calculate compliance
    total_recordings = db.voice_samples.count_documents({"user_id": {"$in": user_ids}})
    
    active_users = len(set(p.get("user_id") for p in predictions))
    
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
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Update user role (super admin only)"""
    db = get_mongodb()
    
    valid_roles = ["patient", "psychologist", "hr_admin", "super_admin", "researcher", "admin"]
    if new_role not in valid_roles:
        raise HTTPException(status_code=400, detail=f"Invalid role. Valid roles: {valid_roles}")
    
    user = db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.users.update_one({"_id": user_id}, {"$set": {"role": new_role}})
    
    return {"message": f"User role updated to {new_role}", "user_id": user_id}

@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Deactivate a user (super admin only)"""
    db = get_mongodb()
    
    user = db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if str(user.get("_id", "")) == str(current_user.get("_id", "")):
        raise HTTPException(status_code=400, detail="Cannot deactivate your own account")
    
    db.users.update_one({"_id": user_id}, {"$set": {"is_active": False}})
    
    return {"message": f"User {user.get('email')} deactivated"}


@router.post("/users/create")
async def create_user(
    email: str,
    full_name: str,
    role: str = "patient",
    password: str = None,
    send_email: bool = True,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Create a new user (admin only)"""
    import uuid
    import bcrypt
    
    db = get_mongodb()
    
    # Check if email already exists
    existing_user = db.users.find_one({"email": email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Generate password if not provided
    if not password:
        password = str(uuid.uuid4())[:12]
    
    # Hash password
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Create user document
    user_id = str(uuid.uuid4())
    user_doc = {
        "_id": user_id,
        "email": email,
        "password_hash": password_hash,
        "full_name": full_name,
        "role": role,
        "is_active": True,
        "is_verified": False,
        "consent_given": False,
        "is_clinical_trial_participant": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow(),
        "created_by": str(current_user.get("_id", ""))
    }
    
    db.users.insert_one(user_doc)
    
    # Log audit event
    db.audit_logs.insert_one({
        "action": "user_created",
        "performed_by": str(current_user.get("_id", "")),
        "performed_by_email": current_user.get("email", ""),
        "target_user_id": user_id,
        "target_email": email,
        "details": {"role": role, "full_name": full_name},
        "timestamp": datetime.utcnow()
    })
    
    # Send welcome email to new user
    if send_email:
        try:
            email_service.send_admin_created_user_email(email, full_name, password, role)
        except Exception as e:
            print(f"Failed to send welcome email: {e}")
    
    return {
        "message": f"User {email} created successfully",
        "user_id": user_id,
        "email": email,
        "role": role,
        "temporary_password": password,
        "email_sent": send_email
    }


@router.get("/audit-logs")
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    action: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Get audit logs (super admin and admin)"""
    db = get_mongodb()
    
    query = {}
    if action:
        query["action"] = action
    
    total = db.audit_logs.count_documents(query)
    logs = list(db.audit_logs.find(query).sort("timestamp", -1).skip(offset).limit(limit))
    
    return {
        "total": total,
        "logs": [
            {
                "id": str(log.get("_id", "")),
                "action": log.get("action", ""),
                "performed_by": log.get("performed_by", ""),
                "performed_by_email": log.get("performed_by_email", ""),
                "target_user_id": log.get("target_user_id"),
                "target_email": log.get("target_email"),
                "details": log.get("details", {}),
                "timestamp": log.get("timestamp").isoformat() if log.get("timestamp") else None
            }
            for log in logs
        ]
    }


@router.put("/users/{user_id}/password")
async def reset_user_password(
    user_id: str,
    new_password: Optional[str] = None,
    auto_generate: bool = False,
    send_email: bool = True,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Reset user password (admin only). Can auto-generate or set specific password."""
    import uuid
    import bcrypt
    
    db = get_mongodb()
    
    user = db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate password if auto_generate or no password provided
    if auto_generate or not new_password:
        new_password = str(uuid.uuid4())[:12]
    
    # Hash password
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    # Update user password
    db.users.update_one({"_id": user_id}, {"$set": {"password_hash": password_hash}})
    
    # Log audit event
    db.audit_logs.insert_one({
        "action": "password_reset",
        "performed_by": str(current_user.get("_id", "")),
        "performed_by_email": current_user.get("email", ""),
        "target_user_id": user_id,
        "target_email": user.get("email", ""),
        "details": {"auto_generated": auto_generate or not new_password},
        "timestamp": datetime.utcnow()
    })
    
    # Send email with new password
    if send_email:
        try:
            email_service.send_admin_created_user_email(
                user.get("email"),
                user.get("full_name"),
                new_password,
                user.get("role", "patient")
            )
        except Exception as e:
            logger.error(f"Failed to send password reset email: {e}")
    
    return {
        "message": f"Password reset successfully for {user.get('email')}",
        "user_id": user_id,
        "new_password": new_password,
        "email_sent": send_email
    }


@router.post("/send-reminder")
async def send_reminder_to_users(
    reminder_type: str = "daily_recording",
    user_ids: Optional[List[str]] = None,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Send reminder emails to users (admin only)"""
    db = get_mongodb()
    
    if user_ids:
        users = list(db.users.find({"_id": {"$in": user_ids}, "is_active": True}))
    else:
        # Send to all active patients who haven't completed baseline
        users = list(db.users.find({
            "role": "patient",
            "is_active": True,
            "baseline_established": {"$ne": True}
        }))
    
    sent_count = 0
    failed_count = 0
    
    for user in users:
        try:
            email_service.send_reminder_email(
                user.get("email"),
                user.get("full_name"),
                reminder_type
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send reminder to {user.get('email')}: {e}")
            failed_count += 1
    
    # Log audit event
    db.audit_logs.insert_one({
        "action": "reminders_sent",
        "performed_by": str(current_user.get("_id", "")),
        "performed_by_email": current_user.get("email", ""),
        "details": {
            "reminder_type": reminder_type,
            "sent_count": sent_count,
            "failed_count": failed_count,
            "target_user_ids": user_ids
        },
        "timestamp": datetime.utcnow()
    })
    
    return {
        "message": f"Reminders sent successfully",
        "sent_count": sent_count,
        "failed_count": failed_count
    }


@router.get("/email-settings")
async def get_email_settings(
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Get email settings and configuration"""
    db = get_mongodb()
    
    # Get email settings from database or return defaults
    settings = db.settings.find_one({"type": "email_settings"})
    
    if not settings:
        settings = {
            "reminder_enabled": True,
            "reminder_frequency": "daily",
            "reminder_time": "09:00",
            "reminder_types": {
                "daily_recording": True,
                "baseline_incomplete": True,
                "weekly_summary": False
            },
            "notification_types": {
                "registration": True,
                "trial_approval": True,
                "analysis_results": True,
                "high_risk_alert": True
            },
            "smtp_configured": bool(email_service.smtp_user and email_service.smtp_password)
        }
    else:
        settings = {
            "reminder_enabled": settings.get("reminder_enabled", True),
            "reminder_frequency": settings.get("reminder_frequency", "daily"),
            "reminder_time": settings.get("reminder_time", "09:00"),
            "reminder_types": settings.get("reminder_types", {}),
            "notification_types": settings.get("notification_types", {}),
            "smtp_configured": bool(email_service.smtp_user and email_service.smtp_password)
        }
    
    return settings


@router.put("/email-settings")
async def update_email_settings(
    settings: Dict[str, Any],
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Update email settings"""
    db = get_mongodb()
    
    # Update or insert settings
    db.settings.update_one(
        {"type": "email_settings"},
        {"$set": {
            "type": "email_settings",
            "reminder_enabled": settings.get("reminder_enabled", True),
            "reminder_frequency": settings.get("reminder_frequency", "daily"),
            "reminder_time": settings.get("reminder_time", "09:00"),
            "reminder_types": settings.get("reminder_types", {}),
            "notification_types": settings.get("notification_types", {}),
            "updated_at": datetime.utcnow(),
            "updated_by": str(current_user.get("_id", ""))
        }},
        upsert=True
    )
    
    # Log audit event
    db.audit_logs.insert_one({
        "action": "email_settings_updated",
        "performed_by": str(current_user.get("_id", "")),
        "performed_by_email": current_user.get("email", ""),
        "details": settings,
        "timestamp": datetime.utcnow()
    })
    
    return {"message": "Email settings updated successfully"}


@router.post("/send-test-email")
async def send_test_email(
    email_type: str = "welcome",
    recipient: Optional[str] = None,
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Send a test email to verify SMTP configuration"""
    # Use recipient if provided, otherwise send to admin
    target_email = recipient if recipient else current_user.get("email")
    admin_name = current_user.get("full_name", "Admin")
    
    try:
        if email_type == "welcome":
            success = email_service.send_welcome_email(target_email, admin_name)
        elif email_type == "reminder":
            success = email_service.send_reminder_email(target_email, admin_name, "daily_recording")
        elif email_type == "analysis":
            # Send a sample analysis results email
            success = email_service.send_analysis_results_email(
                target_email, admin_name,
                {"phq9": 5, "gad7": 4, "pss": 12, "wemwbs": 52},
                "low"
            )
        else:
            success = email_service.send_welcome_email(target_email, admin_name)
        
        if success:
            return {"message": f"Test email sent successfully to {target_email}", "success": True}
        else:
            return {"message": "Failed to send test email. Check SMTP configuration.", "success": False}
    except Exception as e:
        return {"message": f"Error sending test email: {str(e)}", "success": False}


@router.get("/users-for-reminder")
async def get_users_for_reminder(
    reminder_type: str = "daily_recording",
    current_user: Dict[str, Any] = Depends(require_role(["super_admin", "admin"]))
):
    """Get list of users who would receive a specific reminder type"""
    db = get_mongodb()
    
    if reminder_type == "baseline_incomplete":
        # Users who haven't completed baseline (less than 9 recordings)
        pipeline = [
            {"$match": {"role": "patient", "is_active": True}},
            {"$lookup": {
                "from": "voice_samples",
                "localField": "_id",
                "foreignField": "user_id",
                "as": "samples"
            }},
            {"$match": {"$expr": {"$lt": [{"$size": "$samples"}, 9]}}},
            {"$project": {
                "email": 1,
                "full_name": 1,
                "sample_count": {"$size": "$samples"}
            }}
        ]
        users = list(db.users.aggregate(pipeline))
    else:
        # All active patients for daily recording reminder
        users = list(db.users.find(
            {"role": "patient", "is_active": True},
            {"email": 1, "full_name": 1}
        ))
    
    return {
        "reminder_type": reminder_type,
        "user_count": len(users),
        "users": [
            {
                "id": str(u.get("_id", "")),
                "email": u.get("email", ""),
                "full_name": u.get("full_name", ""),
                "sample_count": u.get("sample_count", 0) if reminder_type == "baseline_incomplete" else None
            }
            for u in users
        ]
    }
