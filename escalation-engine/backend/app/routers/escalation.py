"""
Escalation Router for CITTAA Escalation Engine
AI-powered case escalation management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta
from typing import List, Optional
from uuid import UUID
import logging
from io import BytesIO

from app.models.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.institution import Institution
from app.models.counseling_session import CounselingSession
from app.models.escalation_case import EscalationCase
from app.models.escalation_notification import EscalationNotification
from app.schemas.escalation import (
    EscalationCaseCreate, EscalationCaseResponse, EscalationCaseUpdate,
    EscalationAssessment, EscalationDashboardStats,
    EscalationNotificationCreate, EscalationNotificationResponse
)
from app.utils.security import get_current_user, require_role
from app.services.ai_engine import escalation_engine
from app.services.report_generator import report_generator
from app.services.email_service import email_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/escalation", tags=["Escalation"])


@router.post("/analyze", response_model=EscalationAssessment)
async def analyze_session_for_escalation(
    session_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Real-time AI analysis of session notes for risk assessment
    
    This endpoint analyzes session notes as psychologists type,
    detecting risk indicators across 5 Indian languages:
    - English
    - Hindi
    - Telugu
    - Tamil
    - Kannada
    
    Returns escalation level, confidence score, detected keywords,
    and recommended actions.
    
    Performance target: < 3 seconds response time
    """
    # Get student history if student_id provided
    student_history = session_data.get("student_history", [])
    
    # Run AI assessment
    result = escalation_engine.assess_escalation(session_data, student_history)
    
    return EscalationAssessment(
        escalation_level=result.escalation_level,
        confidence=result.confidence,
        risk_category=result.risk_category,
        keywords_detected=result.keywords_detected,
        reasoning=result.reasoning,
        recommended_actions=result.recommended_actions,
        language_detected=result.language_detected
    )


@router.post("/cases", response_model=EscalationCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_escalation_case(
    case_data: EscalationCaseCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new escalation case
    
    Automatically triggers:
    - Email notifications based on escalation level
    - PDF report generation
    - Audit trail logging
    
    Escalation Levels:
    - level_1_low: Standard follow-up
    - level_2_moderate: Increased monitoring
    - level_3_high: Action needed within 24 hours
    - level_4_emergency: Immediate intervention required
    """
    if current_user.role not in ["psychologist", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can create escalation cases"
        )
    
    # Verify student exists
    student = db.query(Student).filter(Student.student_id == case_data.student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Create escalation case
    new_case = EscalationCase(
        student_id=case_data.student_id,
        session_id=case_data.session_id,
        psychologist_id=current_user.user_id,
        institution_id=case_data.institution_id,
        escalation_level=case_data.escalation_level,
        risk_category=case_data.risk_category,
        ai_confidence_score=case_data.ai_confidence_score,
        keywords_detected=case_data.keywords_detected,
        escalation_reason=case_data.escalation_reason,
        immediate_actions_taken=case_data.immediate_actions_taken,
        status="open",
        escalated_at=datetime.utcnow()
    )
    
    db.add(new_case)
    db.commit()
    db.refresh(new_case)
    
    logger.warning(f"Escalation case created: {new_case.case_id} - Level: {case_data.escalation_level}")
    
    # Trigger background tasks for notifications
    background_tasks.add_task(
        send_escalation_notifications,
        case_id=str(new_case.case_id),
        escalation_level=case_data.escalation_level,
        db=db
    )
    
    return new_case


@router.get("/cases", response_model=List[EscalationCaseResponse])
async def get_escalation_cases(
    status_filter: Optional[str] = None,
    level_filter: Optional[str] = None,
    institution_id: Optional[UUID] = None,
    days: Optional[int] = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get escalation cases with filters"""
    query = db.query(EscalationCase)
    
    # Role-based filtering
    if current_user.role == "psychologist":
        query = query.filter(EscalationCase.psychologist_id == current_user.user_id)
    elif current_user.role == "school_admin":
        query = query.filter(EscalationCase.institution_id == current_user.institution_id)
    
    # Apply filters
    if status_filter:
        query = query.filter(EscalationCase.status == status_filter)
    if level_filter:
        query = query.filter(EscalationCase.escalation_level == level_filter)
    if institution_id:
        query = query.filter(EscalationCase.institution_id == institution_id)
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query = query.filter(EscalationCase.created_at >= cutoff)
    
    cases = query.order_by(EscalationCase.escalated_at.desc()).all()
    return cases


@router.get("/cases/{case_id}", response_model=EscalationCaseResponse)
async def get_escalation_case(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific escalation case"""
    case = db.query(EscalationCase).filter(EscalationCase.case_id == case_id).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check access
    if current_user.role == "psychologist" and case.psychologist_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == "school_admin" and case.institution_id != current_user.institution_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return case


@router.put("/cases/{case_id}", response_model=EscalationCaseResponse)
async def update_escalation_case(
    case_id: UUID,
    update_data: EscalationCaseUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an escalation case (status, resolution, assignment)"""
    case = db.query(EscalationCase).filter(EscalationCase.case_id == case_id).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Update fields
    if update_data.status:
        case.status = update_data.status
        if update_data.status == "resolved":
            case.resolved_at = datetime.utcnow()
    
    if update_data.resolution_notes:
        case.resolution_notes = update_data.resolution_notes
    
    if update_data.assigned_to:
        case.assigned_to = update_data.assigned_to
    
    if update_data.immediate_actions_taken:
        case.immediate_actions_taken = update_data.immediate_actions_taken
    
    case.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(case)
    
    logger.info(f"Escalation case updated: {case_id} - Status: {case.status}")
    
    return case


@router.get("/cases/{case_id}/pdf")
async def download_escalation_report_pdf(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download escalation case report as branded PDF"""
    case = db.query(EscalationCase).filter(EscalationCase.case_id == case_id).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Get related data
    student = db.query(Student).filter(Student.student_id == case.student_id).first()
    institution = db.query(Institution).filter(Institution.institution_id == case.institution_id).first()
    psychologist = db.query(User).filter(User.user_id == case.psychologist_id).first()
    
    # Run AI assessment for recommended actions
    assessment = escalation_engine.assess_escalation({
        "presenting_issue": case.escalation_reason or "",
        "session_notes": ""
    })
    
    case_data = {
        "case_id": str(case.case_id),
        "escalated_at": str(case.escalated_at),
        "student_code": student.student_code if student else "N/A",
        "institution_name": institution.name if institution else "N/A",
        "psychologist_name": psychologist.full_name if psychologist else "N/A",
        "psychologist_phone": psychologist.phone if psychologist else "N/A",
        "psychologist_email": psychologist.email if psychologist else "N/A",
        "escalation_level": case.escalation_level,
        "risk_category": case.risk_category,
        "ai_confidence_score": float(case.ai_confidence_score) if case.ai_confidence_score else 0,
        "keywords_detected": case.keywords_detected or [],
        "escalation_reason": case.escalation_reason,
        "immediate_actions_taken": case.immediate_actions_taken,
        "recommended_actions": assessment.recommended_actions
    }
    
    pdf_bytes = report_generator.generate_escalation_report(case_data)
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=escalation_report_{case_id}.pdf"
        }
    )


@router.get("/dashboard/stats", response_model=EscalationDashboardStats)
async def get_escalation_dashboard_stats(
    institution_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get escalation dashboard statistics"""
    query = db.query(EscalationCase)
    
    # Role-based filtering
    if current_user.role == "psychologist":
        query = query.filter(EscalationCase.psychologist_id == current_user.user_id)
    elif current_user.role == "school_admin":
        query = query.filter(EscalationCase.institution_id == current_user.institution_id)
    elif institution_id:
        query = query.filter(EscalationCase.institution_id == institution_id)
    
    # Open cases by level
    open_cases = query.filter(EscalationCase.status == "open").all()
    
    emergency_count = sum(1 for c in open_cases if c.escalation_level == "level_4_emergency")
    high_count = sum(1 for c in open_cases if c.escalation_level == "level_3_high")
    moderate_count = sum(1 for c in open_cases if c.escalation_level == "level_2_moderate")
    low_count = sum(1 for c in open_cases if c.escalation_level == "level_1_low")
    
    # Resolved today
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today = query.filter(
        EscalationCase.status == "resolved",
        EscalationCase.resolved_at >= today_start
    ).count()
    
    # Average resolution time
    resolved_cases = query.filter(
        EscalationCase.status == "resolved",
        EscalationCase.resolved_at.isnot(None)
    ).all()
    
    if resolved_cases:
        total_hours = sum(
            (c.resolved_at - c.escalated_at).total_seconds() / 3600
            for c in resolved_cases if c.resolved_at and c.escalated_at
        )
        avg_resolution_time = total_hours / len(resolved_cases)
    else:
        avg_resolution_time = None
    
    # Cases by risk category
    cases_by_category = {}
    for case in open_cases:
        cat = case.risk_category or "unknown"
        cases_by_category[cat] = cases_by_category.get(cat, 0) + 1
    
    return EscalationDashboardStats(
        total_open_cases=len(open_cases),
        emergency_cases=emergency_count,
        high_risk_cases=high_count,
        moderate_cases=moderate_count,
        low_cases=low_count,
        resolved_today=resolved_today,
        average_resolution_time_hours=avg_resolution_time,
        cases_by_risk_category=cases_by_category
    )


@router.post("/cases/{case_id}/notify")
async def send_case_notification(
    case_id: UUID,
    notification_data: EscalationNotificationCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Manually send notification for an escalation case"""
    case = db.query(EscalationCase).filter(EscalationCase.case_id == case_id).first()
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Create notification record
    notification = EscalationNotification(
        case_id=case_id,
        recipient_email=notification_data.recipient_email,
        recipient_type=notification_data.recipient_type,
        notification_type=notification_data.notification_type,
        delivery_status="pending"
    )
    
    db.add(notification)
    db.commit()
    db.refresh(notification)
    
    # Send notification in background
    background_tasks.add_task(
        process_notification,
        notification_id=str(notification.notification_id),
        case_id=str(case_id),
        db=db
    )
    
    return {"message": "Notification queued", "notification_id": str(notification.notification_id)}


@router.get("/cases/{case_id}/notifications", response_model=List[EscalationNotificationResponse])
async def get_case_notifications(
    case_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all notifications for an escalation case"""
    notifications = db.query(EscalationNotification).filter(
        EscalationNotification.case_id == case_id
    ).order_by(EscalationNotification.created_at.desc()).all()
    
    return notifications


# Background task functions

async def send_escalation_notifications(case_id: str, escalation_level: str, db: Session):
    """Send notifications based on escalation level"""
    try:
        case = db.query(EscalationCase).filter(EscalationCase.case_id == case_id).first()
        if not case:
            return
        
        # Get institution for contact emails
        institution = db.query(Institution).filter(
            Institution.institution_id == case.institution_id
        ).first()
        
        # Get psychologist info
        psychologist = db.query(User).filter(User.user_id == case.psychologist_id).first()
        student = db.query(Student).filter(Student.student_id == case.student_id).first()
        
        # Determine recipients based on level
        recipients = []
        
        if escalation_level == "level_4_emergency":
            # Emergency: notify everyone
            if institution and institution.contact_email:
                recipients.append(institution.contact_email)
            # Add admin emails
            admins = db.query(User).filter(
                User.role == "admin",
                User.is_active == True
            ).all()
            recipients.extend([a.email for a in admins])
        
        elif escalation_level == "level_3_high":
            # High: notify school admin and supervisors
            if institution and institution.contact_email:
                recipients.append(institution.contact_email)
            school_admins = db.query(User).filter(
                User.role == "school_admin",
                User.institution_id == case.institution_id,
                User.is_active == True
            ).all()
            recipients.extend([a.email for a in school_admins])
        
        elif escalation_level == "level_2_moderate":
            # Moderate: notify school admin
            if institution and institution.contact_email:
                recipients.append(institution.contact_email)
        
        # Remove duplicates
        recipients = list(set(recipients))
        
        if not recipients:
            logger.warning(f"No recipients found for escalation case {case_id}")
            return
        
        # Prepare case data for email
        assessment = escalation_engine.assess_escalation({
            "presenting_issue": case.escalation_reason or "",
            "session_notes": ""
        })
        
        case_data = {
            "case_id": str(case.case_id),
            "escalated_at": str(case.escalated_at),
            "student_code": student.student_code if student else "N/A",
            "institution_name": institution.name if institution else "N/A",
            "psychologist_name": psychologist.full_name if psychologist else "N/A",
            "psychologist_phone": psychologist.phone if psychologist else "N/A",
            "psychologist_email": psychologist.email if psychologist else "N/A",
            "escalation_level": case.escalation_level,
            "risk_category": case.risk_category,
            "ai_confidence_score": float(case.ai_confidence_score) if case.ai_confidence_score else 0,
            "keywords_detected": case.keywords_detected or [],
            "escalation_reason": case.escalation_reason,
            "immediate_actions_taken": case.immediate_actions_taken,
            "recommended_actions": assessment.recommended_actions
        }
        
        # Generate PDF
        pdf_bytes = report_generator.generate_escalation_report(case_data)
        
        # Send emails
        result = email_service.send_escalation_notification(
            case_data=case_data,
            recipients=recipients,
            pdf_attachment=pdf_bytes
        )
        
        # Record notifications
        for recipient in recipients:
            notification = EscalationNotification(
                case_id=case.case_id,
                recipient_email=recipient,
                recipient_type="auto",
                notification_type="email",
                sent_at=datetime.utcnow() if result.get("success") else None,
                delivery_status="sent" if result.get("success") else "failed"
            )
            db.add(notification)
        
        db.commit()
        
        logger.info(f"Escalation notifications sent for case {case_id}: {result}")
        
    except Exception as e:
        logger.error(f"Error sending escalation notifications: {str(e)}")


async def process_notification(notification_id: str, case_id: str, db: Session):
    """Process a single notification"""
    try:
        notification = db.query(EscalationNotification).filter(
            EscalationNotification.notification_id == notification_id
        ).first()
        
        if not notification:
            return
        
        case = db.query(EscalationCase).filter(EscalationCase.case_id == case_id).first()
        if not case:
            notification.delivery_status = "failed"
            notification.error_message = "Case not found"
            db.commit()
            return
        
        # Get related data
        student = db.query(Student).filter(Student.student_id == case.student_id).first()
        institution = db.query(Institution).filter(Institution.institution_id == case.institution_id).first()
        psychologist = db.query(User).filter(User.user_id == case.psychologist_id).first()
        
        assessment = escalation_engine.assess_escalation({
            "presenting_issue": case.escalation_reason or "",
            "session_notes": ""
        })
        
        case_data = {
            "case_id": str(case.case_id),
            "escalated_at": str(case.escalated_at),
            "student_code": student.student_code if student else "N/A",
            "institution_name": institution.name if institution else "N/A",
            "psychologist_name": psychologist.full_name if psychologist else "N/A",
            "psychologist_phone": psychologist.phone if psychologist else "N/A",
            "psychologist_email": psychologist.email if psychologist else "N/A",
            "escalation_level": case.escalation_level,
            "risk_category": case.risk_category,
            "ai_confidence_score": float(case.ai_confidence_score) if case.ai_confidence_score else 0,
            "keywords_detected": case.keywords_detected or [],
            "escalation_reason": case.escalation_reason,
            "immediate_actions_taken": case.immediate_actions_taken,
            "recommended_actions": assessment.recommended_actions
        }
        
        pdf_bytes = report_generator.generate_escalation_report(case_data)
        
        result = email_service.send_escalation_notification(
            case_data=case_data,
            recipients=[notification.recipient_email],
            pdf_attachment=pdf_bytes
        )
        
        notification.sent_at = datetime.utcnow()
        notification.delivery_status = "sent" if result.get("success") else "failed"
        if not result.get("success"):
            notification.error_message = str(result.get("error", "Unknown error"))
        
        db.commit()
        
    except Exception as e:
        logger.error(f"Error processing notification {notification_id}: {str(e)}")
        notification = db.query(EscalationNotification).filter(
            EscalationNotification.notification_id == notification_id
        ).first()
        if notification:
            notification.delivery_status = "failed"
            notification.error_message = str(e)
            db.commit()
