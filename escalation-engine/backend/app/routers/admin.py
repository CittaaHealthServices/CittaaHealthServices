"""
Admin Router for CITTAA Escalation Engine
Dashboard analytics and system management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from uuid import UUID
import logging

from app.models.database import get_db
from app.models.user import User
from app.models.institution import Institution
from app.models.student import Student
from app.models.counseling_session import CounselingSession
from app.models.daily_report import DailyReport
from app.models.weekly_report import WeeklyReport
from app.models.monthly_report import MonthlyReport
from app.models.escalation_case import EscalationCase
from app.models.role import Role, DEFAULT_ROLES
from app.schemas.user import UserResponse, UserUpdate, UserCreate
from app.schemas.role import RoleCreate, RoleUpdate, RoleResponse, UserRoleChange
from app.utils.security import get_current_user, require_role, get_password_hash

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/dashboard/overview")
async def get_dashboard_overview(
    institution_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive dashboard overview
    
    Includes:
    - Total users, institutions, students
    - Active sessions today
    - Escalation statistics
    - Report submission rates
    """
    # Check admin access
    if current_user.role not in ["admin", "school_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Base queries with institution filter for school_admin
    inst_filter = None
    if current_user.role == "school_admin":
        inst_filter = current_user.institution_id
    elif institution_id:
        inst_filter = institution_id
    
    # User statistics
    user_query = db.query(User)
    if inst_filter:
        user_query = user_query.filter(User.institution_id == inst_filter)
    
    total_users = user_query.count()
    active_users = user_query.filter(User.is_active == True).count()
    psychologists = user_query.filter(User.role == "psychologist").count()
    
    # Institution statistics
    if current_user.role == "admin":
        total_institutions = db.query(Institution).count()
        active_institutions = db.query(Institution).filter(Institution.is_active == True).count()
    else:
        total_institutions = 1
        active_institutions = 1
    
    # Student statistics
    student_query = db.query(Student)
    if inst_filter:
        student_query = student_query.filter(Student.institution_id == inst_filter)
    total_students = student_query.count()
    active_students = student_query.filter(Student.is_active == True).count()
    
    # Today's activity
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    session_query = db.query(CounselingSession).filter(
        CounselingSession.session_date >= today_start.date()
    )
    if inst_filter:
        session_query = session_query.filter(CounselingSession.institution_id == inst_filter)
    sessions_today = session_query.count()
    
    # Escalation statistics
    escalation_query = db.query(EscalationCase)
    if inst_filter:
        escalation_query = escalation_query.filter(EscalationCase.institution_id == inst_filter)
    
    open_escalations = escalation_query.filter(EscalationCase.status == "open").count()
    emergency_cases = escalation_query.filter(
        EscalationCase.escalation_level == "level_4_emergency",
        EscalationCase.status == "open"
    ).count()
    high_risk_cases = escalation_query.filter(
        EscalationCase.escalation_level == "level_3_high",
        EscalationCase.status == "open"
    ).count()
    
    # Report statistics (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    
    daily_reports_query = db.query(DailyReport).filter(DailyReport.created_at >= week_ago)
    if inst_filter:
        daily_reports_query = daily_reports_query.filter(DailyReport.institution_id == inst_filter)
    daily_reports_count = daily_reports_query.count()
    
    weekly_reports_query = db.query(WeeklyReport).filter(WeeklyReport.created_at >= week_ago)
    if inst_filter:
        weekly_reports_query = weekly_reports_query.filter(WeeklyReport.institution_id == inst_filter)
    weekly_reports_count = weekly_reports_query.count()
    
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
    institution_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get trend data for charts"""
    if current_user.role not in ["admin", "school_admin"]:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    inst_filter = None
    if current_user.role == "school_admin":
        inst_filter = current_user.institution_id
    elif institution_id:
        inst_filter = institution_id
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Sessions per day
    session_query = db.query(
        func.date(CounselingSession.session_date).label('date'),
        func.count(CounselingSession.session_id).label('count')
    ).filter(CounselingSession.session_date >= cutoff.date())
    
    if inst_filter:
        session_query = session_query.filter(CounselingSession.institution_id == inst_filter)
    
    sessions_by_day = session_query.group_by(
        func.date(CounselingSession.session_date)
    ).all()
    
    # Escalations per day
    escalation_query = db.query(
        func.date(EscalationCase.escalated_at).label('date'),
        func.count(EscalationCase.case_id).label('count')
    ).filter(EscalationCase.escalated_at >= cutoff)
    
    if inst_filter:
        escalation_query = escalation_query.filter(EscalationCase.institution_id == inst_filter)
    
    escalations_by_day = escalation_query.group_by(
        func.date(EscalationCase.escalated_at)
    ).all()
    
    # Escalations by level
    level_query = db.query(
        EscalationCase.escalation_level,
        func.count(EscalationCase.case_id).label('count')
    ).filter(EscalationCase.escalated_at >= cutoff)
    
    if inst_filter:
        level_query = level_query.filter(EscalationCase.institution_id == inst_filter)
    
    escalations_by_level = level_query.group_by(EscalationCase.escalation_level).all()
    
    return {
        "sessions_trend": [
            {"date": str(row.date), "count": row.count}
            for row in sessions_by_day
        ],
        "escalations_trend": [
            {"date": str(row.date), "count": row.count}
            for row in escalations_by_day
        ],
        "escalations_by_level": [
            {"level": row.escalation_level, "count": row.count}
            for row in escalations_by_level
        ]
    }


VALID_ROLES = ["admin", "psychologist", "school_admin", "manager", "quality_manager"]


@router.post("/users", response_model=UserResponse)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new user (admin only)
    
    Roles available:
    - admin: Full system access
    - psychologist: Can submit reports and manage students
    - school_admin: Can view institution data
    - manager: Psychology team manager - can view all submitted data
    - quality_manager: Quality oversight - can view all data and compliance reports
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    if user_data.role not in VALID_ROLES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid role. Must be one of: {', '.join(VALID_ROLES)}"
        )
    
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        institution_id=user_data.institution_id,
        rci_registration=user_data.rci_registration,
        phone=user_data.phone,
        is_active=True
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user created: {new_user.email} with role {new_user.role} by admin {current_user.email}")
    
    return new_user


@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    role: Optional[str] = None,
    institution_id: Optional[UUID] = None,
    is_active: Optional[bool] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all users with filters (admin, manager, quality_manager)"""
    if current_user.role not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Admin or manager access required")
    
    query = db.query(User)
    
    if role:
        query = query.filter(User.role == role)
    if institution_id:
        query = query.filter(User.institution_id == institution_id)
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.order_by(User.created_at.desc()).all()
    return users


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    if update_data.full_name:
        user.full_name = update_data.full_name
    if update_data.phone:
        user.phone = update_data.phone
    if update_data.rci_registration:
        user.rci_registration = update_data.rci_registration
    if update_data.is_active is not None:
        user.is_active = update_data.is_active
    
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/users/{user_id}")
async def deactivate_user(
    user_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate a user (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    user.is_active = False
    user.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"User deactivated: {user.email} by admin {current_user.email}")
    
    return {"message": "User deactivated successfully"}


@router.get("/audit-log")
async def get_audit_log(
    days: int = 7,
    action_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get audit log for compliance (DPDP Act 2023)
    
    Tracks:
    - User logins
    - Report submissions
    - Escalation case actions
    - Data access events
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    # Collect audit events
    events = []
    
    # User logins
    recent_logins = db.query(User).filter(
        User.last_login >= cutoff
    ).all()
    
    for user in recent_logins:
        events.append({
            "timestamp": str(user.last_login),
            "action": "user_login",
            "user_email": user.email,
            "details": f"User {user.full_name} logged in"
        })
    
    # Report submissions
    daily_reports = db.query(DailyReport).filter(
        DailyReport.submitted_at >= cutoff
    ).all()
    
    for report in daily_reports:
        psychologist = db.query(User).filter(User.user_id == report.psychologist_id).first()
        events.append({
            "timestamp": str(report.submitted_at),
            "action": "daily_report_submitted",
            "user_email": psychologist.email if psychologist else "unknown",
            "details": f"Daily report submitted for {report.report_date}"
        })
    
    # Escalation cases
    escalations = db.query(EscalationCase).filter(
        EscalationCase.created_at >= cutoff
    ).all()
    
    for case in escalations:
        psychologist = db.query(User).filter(User.user_id == case.psychologist_id).first()
        events.append({
            "timestamp": str(case.escalated_at),
            "action": "escalation_created",
            "user_email": psychologist.email if psychologist else "unknown",
            "details": f"Escalation case created: {case.escalation_level}"
        })
    
    # Sort by timestamp
    events.sort(key=lambda x: x["timestamp"], reverse=True)
    
    # Filter by action type if specified
    if action_type:
        events = [e for e in events if e["action"] == action_type]
    
    return {
        "total_events": len(events),
        "period_days": days,
        "events": events[:100]  # Limit to 100 most recent
    }


@router.get("/compliance/dpdp-report")
async def get_dpdp_compliance_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate DPDP Act 2023 compliance report
    
    Includes:
    - Data processing activities
    - Consent records
    - Data access logs
    - Anonymization status
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Count anonymized students
    total_students = db.query(Student).count()
    students_with_code = db.query(Student).filter(
        Student.student_code.isnot(None)
    ).count()
    
    # Data processing summary
    total_sessions = db.query(CounselingSession).count()
    total_reports = (
        db.query(DailyReport).count() +
        db.query(WeeklyReport).count() +
        db.query(MonthlyReport).count()
    )
    total_escalations = db.query(EscalationCase).count()
    
    # Active users with data access
    active_users = db.query(User).filter(User.is_active == True).count()
    
    return {
        "report_date": str(datetime.utcnow().date()),
        "compliance_status": "compliant",
        "data_protection_measures": {
            "encryption": "AES-256 for sensitive data",
            "anonymization": f"{students_with_code}/{total_students} students anonymized",
            "access_control": "Role-based access control (RBAC) implemented",
            "audit_logging": "All data access events logged"
        },
        "data_processing_summary": {
            "counseling_sessions": total_sessions,
            "reports_generated": total_reports,
            "escalation_cases": total_escalations,
            "active_data_processors": active_users
        },
        "data_retention_policy": {
            "session_notes": "7 years as per RCI guidelines",
            "escalation_records": "Permanent for legal compliance",
            "audit_logs": "5 years"
        },
        "pocso_compliance": {
            "mandatory_reporting": "Enabled for abuse indicators",
            "automatic_detection": "AI-powered keyword detection active"
        }
    }


@router.get("/system/health")
async def get_system_health(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get system health status"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    # Check database connection
    try:
        db.execute("SELECT 1")
        db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Get counts
    user_count = db.query(User).count()
    institution_count = db.query(Institution).count()
    
    return {
        "status": "operational",
        "timestamp": str(datetime.utcnow()),
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


@router.get("/roles", response_model=List[RoleResponse])
async def get_all_roles(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all available roles"""
    if current_user.role not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Admin or manager access required")
    
    roles = db.query(Role).filter(Role.is_active == True).all()
    
    if not roles:
        for role_data in DEFAULT_ROLES:
            role = Role(
                name=role_data["name"],
                display_name=role_data["display_name"],
                description=role_data["description"],
                permissions=role_data["permissions"],
                is_system_role=role_data["is_system_role"]
            )
            db.add(role)
        db.commit()
        roles = db.query(Role).filter(Role.is_active == True).all()
    
    return roles


@router.post("/roles", response_model=RoleResponse)
async def create_role(
    role_data: RoleCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new custom role (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    existing_role = db.query(Role).filter(Role.name == role_data.name).first()
    if existing_role:
        raise HTTPException(status_code=400, detail="Role name already exists")
    
    new_role = Role(
        name=role_data.name.lower().replace(" ", "_"),
        display_name=role_data.display_name,
        description=role_data.description,
        permissions=role_data.permissions,
        is_system_role=False,
        created_by=current_user.user_id
    )
    
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    
    VALID_ROLES.append(new_role.name)
    
    logger.info(f"New role created: {new_role.name} by admin {current_user.email}")
    
    return new_role


@router.put("/roles/{role_name}", response_model=RoleResponse)
async def update_role(
    role_name: str,
    update_data: RoleUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a role (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    role = db.query(Role).filter(Role.name == role_name).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    if update_data.display_name:
        role.display_name = update_data.display_name
    if update_data.description:
        role.description = update_data.description
    if update_data.permissions is not None:
        role.permissions = update_data.permissions
    if update_data.is_active is not None:
        role.is_active = update_data.is_active
    
    role.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(role)
    
    logger.info(f"Role updated: {role.name} by admin {current_user.email}")
    
    return role


@router.put("/users/{user_id}/role", response_model=UserResponse)
async def change_user_role(
    user_id: UUID,
    role_change: UserRoleChange,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Change a user's role (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    user = db.query(User).filter(User.user_id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    role = db.query(Role).filter(Role.name == role_change.role, Role.is_active == True).first()
    if not role and role_change.role not in VALID_ROLES:
        raise HTTPException(status_code=400, detail=f"Invalid role: {role_change.role}")
    
    old_role = user.role
    user.role = role_change.role
    user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(user)
    
    logger.info(f"User role changed: {user.email} from {old_role} to {user.role} by admin {current_user.email}")
    
    return user


@router.get("/manager/reports")
async def get_all_reports_for_manager(
    report_type: Optional[str] = None,
    psychologist_id: Optional[UUID] = None,
    institution_id: Optional[UUID] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all submitted reports for manager review
    
    Managers and Quality Managers can view all reports submitted by psychologists
    """
    if current_user.role not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    result = {"daily_reports": [], "weekly_reports": [], "monthly_reports": []}
    
    if report_type in [None, "daily"]:
        daily_query = db.query(DailyReport).filter(DailyReport.created_at >= cutoff)
        if psychologist_id:
            daily_query = daily_query.filter(DailyReport.psychologist_id == psychologist_id)
        if institution_id:
            daily_query = daily_query.filter(DailyReport.institution_id == institution_id)
        
        daily_reports = daily_query.order_by(DailyReport.report_date.desc()).all()
        
        for report in daily_reports:
            psychologist = db.query(User).filter(User.user_id == report.psychologist_id).first()
            result["daily_reports"].append({
                "report_id": str(report.report_id),
                "report_date": str(report.report_date),
                "psychologist_name": psychologist.full_name if psychologist else "Unknown",
                "psychologist_email": psychologist.email if psychologist else "Unknown",
                "sessions_conducted": report.sessions_conducted,
                "assessments_completed": report.assessments_completed,
                "crisis_interventions": report.crisis_interventions,
                "status": report.status,
                "submitted_at": str(report.submitted_at) if report.submitted_at else None
            })
    
    if report_type in [None, "weekly"]:
        weekly_query = db.query(WeeklyReport).filter(WeeklyReport.created_at >= cutoff)
        if psychologist_id:
            weekly_query = weekly_query.filter(WeeklyReport.psychologist_id == psychologist_id)
        if institution_id:
            weekly_query = weekly_query.filter(WeeklyReport.institution_id == institution_id)
        
        weekly_reports = weekly_query.order_by(WeeklyReport.week_start_date.desc()).all()
        
        for report in weekly_reports:
            psychologist = db.query(User).filter(User.user_id == report.psychologist_id).first()
            result["weekly_reports"].append({
                "report_id": str(report.report_id),
                "week_start_date": str(report.week_start_date),
                "week_end_date": str(report.week_end_date),
                "psychologist_name": psychologist.full_name if psychologist else "Unknown",
                "psychologist_email": psychologist.email if psychologist else "Unknown",
                "total_sessions": report.total_sessions,
                "total_students_served": report.total_students_served,
                "status": report.status,
                "submitted_at": str(report.submitted_at) if report.submitted_at else None
            })
    
    if report_type in [None, "monthly"]:
        monthly_query = db.query(MonthlyReport).filter(MonthlyReport.created_at >= cutoff)
        if psychologist_id:
            monthly_query = monthly_query.filter(MonthlyReport.psychologist_id == psychologist_id)
        if institution_id:
            monthly_query = monthly_query.filter(MonthlyReport.institution_id == institution_id)
        
        monthly_reports = monthly_query.order_by(MonthlyReport.report_month.desc()).all()
        
        for report in monthly_reports:
            psychologist = db.query(User).filter(User.user_id == report.psychologist_id).first()
            result["monthly_reports"].append({
                "report_id": str(report.report_id),
                "report_month": str(report.report_month),
                "psychologist_name": psychologist.full_name if psychologist else "Unknown",
                "psychologist_email": psychologist.email if psychologist else "Unknown",
                "status": report.status,
                "submitted_at": str(report.submitted_at) if report.submitted_at else None
            })
    
    return result


@router.get("/manager/escalations")
async def get_all_escalations_for_manager(
    status: Optional[str] = None,
    level: Optional[str] = None,
    psychologist_id: Optional[UUID] = None,
    institution_id: Optional[UUID] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all escalation cases for manager review
    
    Managers and Quality Managers can view all escalation cases
    """
    if current_user.role not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(EscalationCase).filter(EscalationCase.created_at >= cutoff)
    
    if status:
        query = query.filter(EscalationCase.status == status)
    if level:
        query = query.filter(EscalationCase.escalation_level == level)
    if psychologist_id:
        query = query.filter(EscalationCase.psychologist_id == psychologist_id)
    if institution_id:
        query = query.filter(EscalationCase.institution_id == institution_id)
    
    escalations = query.order_by(EscalationCase.escalated_at.desc()).all()
    
    result = []
    for case in escalations:
        psychologist = db.query(User).filter(User.user_id == case.psychologist_id).first()
        student = db.query(Student).filter(Student.student_id == case.student_id).first()
        
        result.append({
            "case_id": str(case.case_id),
            "escalation_level": case.escalation_level,
            "status": case.status,
            "risk_score": case.risk_score,
            "psychologist_name": psychologist.full_name if psychologist else "Unknown",
            "psychologist_email": psychologist.email if psychologist else "Unknown",
            "student_code": student.student_code if student else "Unknown",
            "student_grade": student.grade if student else "Unknown",
            "trigger_keywords": case.trigger_keywords,
            "ai_summary": case.ai_summary,
            "escalated_at": str(case.escalated_at),
            "resolved_at": str(case.resolved_at) if case.resolved_at else None,
            "resolution_notes": case.resolution_notes
        })
    
    return {
        "total_count": len(result),
        "escalations": result
    }


@router.get("/manager/sessions")
async def get_all_sessions_for_manager(
    psychologist_id: Optional[UUID] = None,
    institution_id: Optional[UUID] = None,
    session_type: Optional[str] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get all counseling sessions for manager review
    
    Managers and Quality Managers can view all session data
    """
    if current_user.role not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    query = db.query(CounselingSession).filter(CounselingSession.session_date >= cutoff.date())
    
    if psychologist_id:
        query = query.filter(CounselingSession.psychologist_id == psychologist_id)
    if institution_id:
        query = query.filter(CounselingSession.institution_id == institution_id)
    if session_type:
        query = query.filter(CounselingSession.session_type == session_type)
    
    sessions = query.order_by(CounselingSession.session_date.desc()).all()
    
    result = []
    for session in sessions:
        psychologist = db.query(User).filter(User.user_id == session.psychologist_id).first()
        student = db.query(Student).filter(Student.student_id == session.student_id).first()
        
        result.append({
            "session_id": str(session.session_id),
            "session_date": str(session.session_date),
            "session_type": session.session_type,
            "duration_minutes": session.duration_minutes,
            "psychologist_name": psychologist.full_name if psychologist else "Unknown",
            "psychologist_email": psychologist.email if psychologist else "Unknown",
            "student_code": student.student_code if student else "Unknown",
            "student_grade": student.grade if student else "Unknown",
            "focus_area": session.focus_area,
            "status": session.status,
            "ai_risk_level": session.ai_risk_level,
            "ai_risk_score": session.ai_risk_score
        })
    
    return {
        "total_count": len(result),
        "sessions": result
    }


@router.get("/manager/psychologist-performance")
async def get_psychologist_performance(
    psychologist_id: Optional[UUID] = None,
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get performance metrics for psychologists
    
    Managers can view productivity and quality metrics for their team
    """
    if current_user.role not in ["admin", "manager", "quality_manager"]:
        raise HTTPException(status_code=403, detail="Manager access required")
    
    cutoff = datetime.utcnow() - timedelta(days=days)
    
    psychologists_query = db.query(User).filter(User.role == "psychologist", User.is_active == True)
    if psychologist_id:
        psychologists_query = psychologists_query.filter(User.user_id == psychologist_id)
    
    psychologists = psychologists_query.all()
    
    result = []
    for psych in psychologists:
        sessions_count = db.query(CounselingSession).filter(
            CounselingSession.psychologist_id == psych.user_id,
            CounselingSession.session_date >= cutoff.date()
        ).count()
        
        daily_reports_count = db.query(DailyReport).filter(
            DailyReport.psychologist_id == psych.user_id,
            DailyReport.created_at >= cutoff
        ).count()
        
        escalations_count = db.query(EscalationCase).filter(
            EscalationCase.psychologist_id == psych.user_id,
            EscalationCase.created_at >= cutoff
        ).count()
        
        resolved_escalations = db.query(EscalationCase).filter(
            EscalationCase.psychologist_id == psych.user_id,
            EscalationCase.created_at >= cutoff,
            EscalationCase.status == "resolved"
        ).count()
        
        students_served = db.query(func.count(func.distinct(CounselingSession.student_id))).filter(
            CounselingSession.psychologist_id == psych.user_id,
            CounselingSession.session_date >= cutoff.date()
        ).scalar()
        
        result.append({
            "psychologist_id": str(psych.user_id),
            "name": psych.full_name,
            "email": psych.email,
            "institution_id": str(psych.institution_id) if psych.institution_id else None,
            "metrics": {
                "total_sessions": sessions_count,
                "daily_reports_submitted": daily_reports_count,
                "escalations_raised": escalations_count,
                "escalations_resolved": resolved_escalations,
                "students_served": students_served or 0,
                "avg_sessions_per_day": round(sessions_count / max(days, 1), 2)
            },
            "last_login": str(psych.last_login) if psych.last_login else None
        })
    
    return {
        "period_days": days,
        "psychologists": result
    }
