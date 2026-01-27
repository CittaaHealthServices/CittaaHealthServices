"""
MongoDB-based Admin Router for CITTAA Escalation Engine
Dashboard analytics and system management using MongoDB
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr
import logging
import bcrypt
import uuid

from app.models.mongodb import get_mongodb, log_audit_event
from app.routers.auth_mongodb import get_current_user, hash_password

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "psychologist"
    phone: Optional[str] = None
    rci_registration: Optional[str] = None
    institution_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    rci_registration: Optional[str] = None
    institution_id: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


class RoleCreate(BaseModel):
    name: str
    display_name: str
    description: Optional[str] = None
    permissions: Optional[Dict[str, List[str]]] = None


class RoleResponse(BaseModel):
    id: str
    name: str
    display_name: str
    description: Optional[str] = None
    permissions: Optional[Dict[str, List[str]]] = None
    is_system_role: bool = False
    is_active: bool = True


class UserRoleChange(BaseModel):
    role: str


VALID_ROLES = ["admin", "psychologist", "school_admin", "manager", "quality_manager"]


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    institution_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get comprehensive dashboard overview"""
    if current_user["role"] not in ["admin", "school_admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    
    inst_filter = {}
    if current_user["role"] == "school_admin":
        inst_filter = {"institution_id": current_user.get("institution_id")}
    elif institution_id:
        inst_filter = {"institution_id": institution_id}
    
    total_users = db.users.count_documents({**inst_filter})
    active_users = db.users.count_documents({**inst_filter, "is_active": True})
    psychologists = db.users.count_documents({**inst_filter, "role": "psychologist"})
    
    if current_user["role"] == "admin":
        total_institutions = db.institutions.count_documents({})
        active_institutions = db.institutions.count_documents({"is_active": True})
    else:
        total_institutions = 1
        active_institutions = 1
    
    total_students = db.students.count_documents({**inst_filter})
    active_students = db.students.count_documents({**inst_filter, "is_active": True})
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    sessions_today = db.counseling_sessions.count_documents({
        **inst_filter,
        "session_date": {"$gte": today_start}
    })
    
    open_escalations = db.escalation_cases.count_documents({**inst_filter, "status": "open"})
    emergency_cases = db.escalation_cases.count_documents({
        **inst_filter,
        "escalation_level": "level_4_emergency",
        "status": "open"
    })
    high_risk_cases = db.escalation_cases.count_documents({
        **inst_filter,
        "escalation_level": "level_3_high",
        "status": "open"
    })
    
    week_ago = datetime.utcnow() - timedelta(days=7)
    daily_reports_count = db.daily_reports.count_documents({
        **inst_filter,
        "created_at": {"$gte": week_ago}
    })
    weekly_reports_count = db.weekly_reports.count_documents({
        **inst_filter,
        "created_at": {"$gte": week_ago}
    })
    
    return {
        "users": {
            "total": total_users,
            "active": active_users,
            "psychologists": psychologists
        },
        "institutions": {
            "total": total_institutions,
            "active": active_institutions
        },
        "students": {
            "total": total_students,
            "active": active_students
        },
        "today": {
            "sessions": sessions_today,
            "date": str(today_start.date())
        },
        "escalations": {
            "open": open_escalations,
            "emergency": emergency_cases,
            "high_risk": high_risk_cases
        },
        "reports_last_7_days": {
            "daily": daily_reports_count,
            "weekly": weekly_reports_count
        }
    }


@router.get("/dashboard/trends")
async def get_dashboard_trends(
    days: int = 30,
    institution_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get activity trends for dashboard charts"""
    if current_user["role"] not in ["admin", "school_admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    
    inst_filter = {}
    if current_user["role"] == "school_admin":
        inst_filter = {"institution_id": current_user.get("institution_id")}
    elif institution_id:
        inst_filter = {"institution_id": institution_id}
    
    trends = []
    for i in range(days):
        day = datetime.utcnow() - timedelta(days=days - 1 - i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        sessions_count = db.counseling_sessions.count_documents({
            **inst_filter,
            "session_date": {"$gte": day_start, "$lt": day_end}
        })
        
        reports_count = db.daily_reports.count_documents({
            **inst_filter,
            "created_at": {"$gte": day_start, "$lt": day_end}
        })
        
        escalations_count = db.escalation_cases.count_documents({
            **inst_filter,
            "created_at": {"$gte": day_start, "$lt": day_end}
        })
        
        trends.append({
            "date": str(day_start.date()),
            "sessions": sessions_count,
            "reports": reports_count,
            "escalations": escalations_count
        })
    
    return trends


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    
    roles = db.roles.find({"is_active": True})
    valid_roles = [r["name"] for r in roles]
    if not valid_roles:
        valid_roles = VALID_ROLES
    
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    existing_user = db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    user_doc = {
        "_id": str(uuid.uuid4()),
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": user_data.role,
        "phone": user_data.phone,
        "rci_registration": user_data.rci_registration,
        "institution_id": user_data.institution_id,
        "is_active": True,
        "is_verified": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.users.insert_one(user_doc)
    
    log_audit_event(
        current_user["_id"],
        "create_user",
        "user",
        user_doc["_id"],
        {"email": user_data.email, "role": user_data.role}
    )
    
    logger.info(f"New user created: {user_data.email} with role {user_data.role} by admin {current_user['email']}")
    
    return UserResponse(
        id=user_doc["_id"],
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        role=user_doc["role"],
        phone=user_doc.get("phone"),
        rci_registration=user_doc.get("rci_registration"),
        institution_id=user_doc.get("institution_id"),
        is_active=user_doc["is_active"],
        created_at=user_doc["created_at"]
    )


@router.get("/users")
async def get_all_users(
    role: Optional[str] = None,
    institution_id: Optional[str] = None,
    is_active: Optional[bool] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get all users with filters (admin, manager, quality_manager)"""
    if current_user["role"] not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Admin or manager access required")
    
    db = get_mongodb()
    
    query = {}
    if role:
        query["role"] = role
    if institution_id:
        query["institution_id"] = institution_id
    if is_active is not None:
        query["is_active"] = is_active
    
    users = list(db.users.find(query).sort("created_at", -1))
    
    return [
        UserResponse(
            id=user["_id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            phone=user.get("phone"),
            rci_registration=user.get("rci_registration"),
            institution_id=user.get("institution_id"),
            is_active=user.get("is_active", True),
            created_at=user.get("created_at")
        )
        for user in users
    ]


@router.put("/users/{user_id}/role")
async def change_user_role(
    user_id: str,
    role_change: UserRoleChange,
    current_user: dict = Depends(get_current_user)
):
    """Change a user's role (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    
    roles = db.roles.find({"is_active": True})
    valid_roles = [r["name"] for r in roles]
    if not valid_roles:
        valid_roles = VALID_ROLES
    
    if role_change.role not in valid_roles:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    user = db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    old_role = user["role"]
    
    db.users.update_one(
        {"_id": user_id},
        {"$set": {"role": role_change.role, "updated_at": datetime.utcnow()}}
    )
    
    log_audit_event(
        current_user["_id"],
        "change_user_role",
        "user",
        user_id,
        {"old_role": old_role, "new_role": role_change.role}
    )
    
    logger.info(f"User role changed: {user['email']} from {old_role} to {role_change.role} by admin {current_user['email']}")
    
    return {"message": f"User role changed from {old_role} to {role_change.role}"}


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Deactivate a user (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    
    user = db.users.find_one({"_id": user_id})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    db.users.update_one(
        {"_id": user_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    log_audit_event(
        current_user["_id"],
        "deactivate_user",
        "user",
        user_id,
        {"email": user["email"]}
    )
    
    logger.info(f"User deactivated: {user['email']} by admin {current_user['email']}")
    
    return {"message": "User deactivated successfully"}


@router.get("/roles")
async def get_all_roles(current_user: dict = Depends(get_current_user)):
    """Get all available roles"""
    if current_user["role"] not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Admin or manager access required")
    
    db = get_mongodb()
    
    roles = list(db.roles.find({"is_active": True}))
    
    return [
        RoleResponse(
            id=role["_id"],
            name=role["name"],
            display_name=role["display_name"],
            description=role.get("description"),
            permissions=role.get("permissions"),
            is_system_role=role.get("is_system_role", False),
            is_active=role.get("is_active", True)
        )
        for role in roles
    ]


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new custom role (admin only)"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    
    existing_role = db.roles.find_one({"name": role_data.name})
    if existing_role:
        raise HTTPException(status_code=400, detail="Role name already exists")
    
    role_doc = {
        "_id": str(uuid.uuid4()),
        "name": role_data.name,
        "display_name": role_data.display_name,
        "description": role_data.description,
        "permissions": role_data.permissions or {},
        "is_system_role": False,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.roles.insert_one(role_doc)
    
    log_audit_event(
        current_user["_id"],
        "create_role",
        "role",
        role_doc["_id"],
        {"name": role_data.name}
    )
    
    logger.info(f"New role created: {role_data.name} by admin {current_user['email']}")
    
    return RoleResponse(
        id=role_doc["_id"],
        name=role_doc["name"],
        display_name=role_doc["display_name"],
        description=role_doc.get("description"),
        permissions=role_doc.get("permissions"),
        is_system_role=role_doc["is_system_role"],
        is_active=role_doc["is_active"]
    )


@router.get("/manager/reports")
async def get_all_reports_for_manager(
    report_type: Optional[str] = None,
    psychologist_id: Optional[str] = None,
    institution_id: Optional[str] = None,
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get all reports for manager oversight"""
    if current_user["role"] not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    db = get_mongodb()
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = {"created_at": {"$gte": cutoff}}
    if psychologist_id:
        query["psychologist_id"] = psychologist_id
    if institution_id:
        query["institution_id"] = institution_id
    
    reports = []
    
    if not report_type or report_type == "daily":
        daily = list(db.daily_reports.find(query).sort("created_at", -1).limit(50))
        for r in daily:
            reports.append({
                "id": r["_id"],
                "type": "daily",
                "psychologist_id": r.get("psychologist_id"),
                "report_date": str(r.get("report_date")),
                "created_at": str(r.get("created_at")),
                "sessions_count": r.get("sessions_count", 0)
            })
    
    if not report_type or report_type == "weekly":
        weekly = list(db.weekly_reports.find(query).sort("created_at", -1).limit(20))
        for r in weekly:
            reports.append({
                "id": r["_id"],
                "type": "weekly",
                "psychologist_id": r.get("psychologist_id"),
                "week_start": str(r.get("week_start_date")),
                "created_at": str(r.get("created_at")),
                "total_sessions": r.get("total_sessions", 0)
            })
    
    if not report_type or report_type == "monthly":
        monthly = list(db.monthly_reports.find(query).sort("created_at", -1).limit(12))
        for r in monthly:
            reports.append({
                "id": r["_id"],
                "type": "monthly",
                "psychologist_id": r.get("psychologist_id"),
                "month": r.get("month"),
                "year": r.get("year"),
                "created_at": str(r.get("created_at"))
            })
    
    return {"reports": reports, "total": len(reports)}


@router.get("/manager/escalations")
async def get_all_escalations_for_manager(
    status: Optional[str] = None,
    level: Optional[str] = None,
    psychologist_id: Optional[str] = None,
    institution_id: Optional[str] = None,
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get all escalation cases for manager oversight"""
    if current_user["role"] not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    db = get_mongodb()
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = {"created_at": {"$gte": cutoff}}
    if status:
        query["status"] = status
    if level:
        query["escalation_level"] = level
    if psychologist_id:
        query["psychologist_id"] = psychologist_id
    if institution_id:
        query["institution_id"] = institution_id
    
    escalations = list(db.escalation_cases.find(query).sort("created_at", -1).limit(100))
    
    return {
        "escalations": [
            {
                "id": e["_id"],
                "student_id": e.get("student_id"),
                "psychologist_id": e.get("psychologist_id"),
                "escalation_level": e.get("escalation_level"),
                "status": e.get("status"),
                "risk_score": e.get("risk_score"),
                "created_at": str(e.get("created_at")),
                "resolved_at": str(e.get("resolved_at")) if e.get("resolved_at") else None
            }
            for e in escalations
        ],
        "total": len(escalations)
    }


@router.get("/manager/sessions")
async def get_all_sessions_for_manager(
    psychologist_id: Optional[str] = None,
    institution_id: Optional[str] = None,
    session_type: Optional[str] = None,
    days: int = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get all counseling sessions for manager oversight"""
    if current_user["role"] not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    db = get_mongodb()
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = {"created_at": {"$gte": cutoff}}
    if psychologist_id:
        query["psychologist_id"] = psychologist_id
    if institution_id:
        query["institution_id"] = institution_id
    if session_type:
        query["session_type"] = session_type
    
    sessions = list(db.counseling_sessions.find(query).sort("session_date", -1).limit(100))
    
    return {
        "sessions": [
            {
                "id": s["_id"],
                "student_id": s.get("student_id"),
                "psychologist_id": s.get("psychologist_id"),
                "session_type": s.get("session_type"),
                "session_date": str(s.get("session_date")),
                "duration_minutes": s.get("duration_minutes"),
                "escalation_level": s.get("escalation_level"),
                "created_at": str(s.get("created_at"))
            }
            for s in sessions
        ],
        "total": len(sessions)
    }


@router.get("/system/health")
async def get_system_health(current_user: dict = Depends(get_current_user)):
    """Get system health status"""
    if current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    
    try:
        db.command("ping")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    user_count = db.users.count_documents({})
    institution_count = db.institutions.count_documents({})
    
    return {
        "status": "operational",
        "timestamp": str(datetime.utcnow()),
        "database": "MongoDB Atlas",
        "components": {
            "database": db_status,
            "api": "healthy",
            "ai_engine": "healthy"
        },
        "metrics": {
            "total_users": user_count,
            "total_institutions": institution_count
        },
        "version": "1.0.0"
    }


@router.get("/audit-log")
async def get_audit_log(
    days: int = 7,
    action_type: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get audit log for compliance (DPDP Act 2023)"""
    if current_user["role"] not in ["admin", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = {"timestamp": {"$gte": cutoff}}
    if action_type:
        query["action"] = action_type
    
    events = list(db.audit_logs.find(query).sort("timestamp", -1).limit(100))
    
    return {
        "total_events": len(events),
        "period_days": days,
        "events": [
            {
                "id": e["_id"],
                "user_id": e.get("user_id"),
                "action": e.get("action"),
                "entity_type": e.get("entity_type"),
                "entity_id": e.get("entity_id"),
                "details": e.get("details"),
                "timestamp": str(e.get("timestamp"))
            }
            for e in events
        ]
    }
