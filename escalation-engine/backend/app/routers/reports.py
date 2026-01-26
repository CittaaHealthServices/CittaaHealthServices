"""
Reports Router for CITTAA Escalation Engine
Daily, Weekly, and Monthly report submission and management
"""

from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from datetime import datetime, date
from typing import List, Optional
from uuid import UUID
import logging
from io import BytesIO

from app.models.database import get_db
from app.models.user import User
from app.models.daily_report import DailyReport
from app.models.weekly_report import WeeklyReport
from app.models.monthly_report import MonthlyReport
from app.models.institution import Institution
from app.schemas.report import (
    DailyReportCreate, DailyReportResponse,
    WeeklyReportCreate, WeeklyReportResponse,
    MonthlyReportCreate, MonthlyReportResponse
)
from app.utils.security import get_current_user, require_role
from app.services.report_generator import report_generator
from app.services.email_service import email_service
from app.services.ai_engine import escalation_engine

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


# ============== DAILY REPORTS ==============

@router.post("/daily", response_model=DailyReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_daily_report(
    report_data: DailyReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a Daily Activity Report
    
    This endpoint accepts comprehensive daily reports including:
    - Sessions conducted (individual, group, family, crisis)
    - Assessments initiated/in progress/completed
    - Teacher, parent, and admin consultations
    - Crisis interventions with action plans
    - Curriculum implementation activities
    - Referrals made
    - Documentation status
    - Priorities for next day
    
    The AI engine automatically analyzes session notes for risk indicators.
    """
    # Verify user is a psychologist
    if current_user.role not in ["psychologist", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can submit daily reports"
        )
    
    # Check for existing report on same date
    existing = db.query(DailyReport).filter(
        DailyReport.psychologist_id == current_user.user_id,
        DailyReport.report_date == report_data.report_date
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A report already exists for this date. Use PUT to update."
        )
    
    # Calculate summary metrics
    sessions_conducted = len(report_data.sessions_details)
    crisis_count = len(report_data.crisis_interventions)
    new_referrals = len(report_data.referrals)
    follow_ups = sum(1 for s in report_data.sessions_details if s.follow_up_needed)
    
    # AI analysis of session notes for risk detection
    escalation_flags = []
    for session in report_data.sessions_details:
        if session.presenting_issue or session.notes:
            assessment = escalation_engine.assess_escalation({
                "presenting_issue": session.presenting_issue or "",
                "session_notes": session.notes or ""
            })
            if assessment.escalation_level in ["level_3_high", "level_4_emergency"]:
                escalation_flags.append({
                    "student_code": session.student_code,
                    "level": assessment.escalation_level,
                    "keywords": assessment.keywords_detected
                })
    
    # Create report
    new_report = DailyReport(
        psychologist_id=current_user.user_id,
        institution_id=report_data.institution_id,
        report_date=report_data.report_date,
        sessions_conducted=sessions_conducted,
        crisis_interventions=crisis_count,
        new_referrals=new_referrals,
        follow_ups_completed=follow_ups,
        report_content={
            "sessions_details": [s.model_dump() for s in report_data.sessions_details],
            "assessments": [a.model_dump() for a in report_data.assessments],
            "consultations": [c.model_dump() for c in report_data.consultations],
            "crisis_interventions": [cr.model_dump() for cr in report_data.crisis_interventions],
            "curriculum_activities": [cu.model_dump() for cu in report_data.curriculum_activities],
            "referrals": [r.model_dump() for r in report_data.referrals],
            "documentation_completed": report_data.documentation_completed.model_dump() if report_data.documentation_completed else None,
            "priorities_for_tomorrow": report_data.priorities_for_tomorrow,
            "escalation_flags": escalation_flags
        },
        key_highlights=report_data.key_highlights,
        notes_and_observations=report_data.notes_and_observations,
        submitted_at=datetime.utcnow(),
        status="submitted"
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    logger.info(f"Daily report submitted by {current_user.email} for {report_data.report_date}")
    
    # If there are escalation flags, log them
    if escalation_flags:
        logger.warning(f"Escalation flags detected in daily report: {len(escalation_flags)} cases")
    
    return new_report


@router.get("/daily", response_model=List[DailyReportResponse])
async def get_daily_reports(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    institution_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get daily reports with optional filters"""
    query = db.query(DailyReport)
    
    # Role-based filtering
    if current_user.role == "psychologist":
        query = query.filter(DailyReport.psychologist_id == current_user.user_id)
    elif current_user.role == "school_admin":
        query = query.filter(DailyReport.institution_id == current_user.institution_id)
    
    # Apply filters
    if start_date:
        query = query.filter(DailyReport.report_date >= start_date)
    if end_date:
        query = query.filter(DailyReport.report_date <= end_date)
    if institution_id:
        query = query.filter(DailyReport.institution_id == institution_id)
    
    reports = query.order_by(DailyReport.report_date.desc()).all()
    return reports


@router.get("/daily/{report_id}", response_model=DailyReportResponse)
async def get_daily_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific daily report"""
    report = db.query(DailyReport).filter(DailyReport.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check access
    if current_user.role == "psychologist" and report.psychologist_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == "school_admin" and report.institution_id != current_user.institution_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return report


@router.get("/daily/{report_id}/pdf")
async def download_daily_report_pdf(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download daily report as branded PDF"""
    report = db.query(DailyReport).filter(DailyReport.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Get institution name
    institution = db.query(Institution).filter(Institution.institution_id == report.institution_id).first()
    
    # Prepare report data
    report_data = {
        "report_date": str(report.report_date),
        "psychologist_name": current_user.full_name,
        "institution_name": institution.name if institution else "N/A",
        "submitted_at": str(report.submitted_at) if report.submitted_at else None,
        "sessions_conducted": report.sessions_conducted,
        "crisis_interventions": report.crisis_interventions,
        "new_referrals": report.new_referrals,
        "follow_ups_completed": report.follow_ups_completed,
        "key_highlights": report.key_highlights,
        **(report.report_content or {})
    }
    
    # Generate PDF
    pdf_bytes = report_generator.generate_daily_report(report_data)
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=daily_report_{report.report_date}.pdf"
        }
    )


# ============== WEEKLY REPORTS ==============

@router.post("/weekly", response_model=WeeklyReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_weekly_report(
    report_data: WeeklyReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a Weekly Summary Report
    
    Comprehensive weekly report including:
    - Service delivery statistics
    - Group interventions summary
    - Mental health curriculum implementation
    - Cases of concern
    - Teacher support & collaboration
    - Parent engagement
    - Assessment status
    - Program implementation metrics
    - Resource utilization
    - Successes & challenges
    - Professional development
    - Goals for next week
    - Support needed
    """
    if current_user.role not in ["psychologist", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can submit weekly reports"
        )
    
    # Check for existing report for same week
    existing = db.query(WeeklyReport).filter(
        WeeklyReport.psychologist_id == current_user.user_id,
        WeeklyReport.week_start_date == report_data.week_start_date
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A report already exists for this week. Use PUT to update."
        )
    
    # Calculate totals from service delivery stats
    total_sessions = sum(s.number_of_sessions for s in report_data.service_delivery_stats)
    total_students = sum(s.number_of_students for s in report_data.service_delivery_stats)
    
    new_report = WeeklyReport(
        psychologist_id=current_user.user_id,
        institution_id=report_data.institution_id,
        week_start_date=report_data.week_start_date,
        week_end_date=report_data.week_end_date,
        total_sessions=report_data.total_sessions or total_sessions,
        total_students=report_data.total_students or total_students,
        new_intakes=report_data.new_intakes or 0,
        no_shows=report_data.no_shows or 0,
        report_content={
            "service_delivery_stats": [s.model_dump() for s in report_data.service_delivery_stats],
            "group_interventions": [g.model_dump() for g in report_data.group_interventions],
            "curriculum_implementation": [c.model_dump() for c in report_data.curriculum_implementation],
            "cases_of_concern": [c.model_dump() for c in report_data.cases_of_concern],
            "teacher_support": [t.model_dump() for t in report_data.teacher_support],
            "parent_engagement": [p.model_dump() for p in report_data.parent_engagement],
            "assessments_status": [a.model_dump() for a in report_data.assessments_status],
            "program_metrics": report_data.program_metrics.model_dump() if report_data.program_metrics else None,
            "resource_utilization": [r.model_dump() for r in report_data.resource_utilization],
            "successes_this_week": report_data.successes_this_week,
            "challenges_this_week": report_data.challenges_this_week,
            "solutions_approaches": report_data.solutions_approaches,
            "professional_development": [p.model_dump() for p in report_data.professional_development],
            "goals_for_next_week": report_data.goals_for_next_week,
            "support_needed": report_data.support_needed
        },
        summary=report_data.summary,
        challenges=report_data.challenges,
        recommendations=report_data.recommendations,
        submitted_at=datetime.utcnow(),
        status="submitted"
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    logger.info(f"Weekly report submitted by {current_user.email} for week {report_data.week_start_date}")
    
    return new_report


@router.get("/weekly", response_model=List[WeeklyReportResponse])
async def get_weekly_reports(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    institution_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get weekly reports with optional filters"""
    query = db.query(WeeklyReport)
    
    if current_user.role == "psychologist":
        query = query.filter(WeeklyReport.psychologist_id == current_user.user_id)
    elif current_user.role == "school_admin":
        query = query.filter(WeeklyReport.institution_id == current_user.institution_id)
    
    if start_date:
        query = query.filter(WeeklyReport.week_start_date >= start_date)
    if end_date:
        query = query.filter(WeeklyReport.week_end_date <= end_date)
    if institution_id:
        query = query.filter(WeeklyReport.institution_id == institution_id)
    
    reports = query.order_by(WeeklyReport.week_start_date.desc()).all()
    return reports


@router.get("/weekly/{report_id}", response_model=WeeklyReportResponse)
async def get_weekly_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific weekly report"""
    report = db.query(WeeklyReport).filter(WeeklyReport.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if current_user.role == "psychologist" and report.psychologist_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == "school_admin" and report.institution_id != current_user.institution_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return report


@router.get("/weekly/{report_id}/pdf")
async def download_weekly_report_pdf(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download weekly report as branded PDF"""
    report = db.query(WeeklyReport).filter(WeeklyReport.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    institution = db.query(Institution).filter(Institution.institution_id == report.institution_id).first()
    
    report_data = {
        "week_start_date": str(report.week_start_date),
        "week_end_date": str(report.week_end_date),
        "psychologist_name": current_user.full_name,
        "institution_name": institution.name if institution else "N/A",
        "total_sessions": report.total_sessions,
        "total_students": report.total_students,
        "new_intakes": report.new_intakes,
        "no_shows": report.no_shows,
        **(report.report_content or {})
    }
    
    pdf_bytes = report_generator.generate_weekly_report(report_data)
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=weekly_report_{report.week_start_date}.pdf"
        }
    )


# ============== MONTHLY REPORTS ==============

@router.post("/monthly", response_model=MonthlyReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_monthly_report(
    report_data: MonthlyReportCreate,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a Monthly Metrics Tracking Report
    
    Comprehensive monthly report including:
    - Service delivery metrics
    - Implementation metrics
    - Outcome metrics
    - Clinical outcomes
    - Executive summary
    - Institutional impact
    - Recommendations
    """
    if current_user.role not in ["psychologist", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can submit monthly reports"
        )
    
    # Check for existing report for same month
    existing = db.query(MonthlyReport).filter(
        MonthlyReport.psychologist_id == current_user.user_id,
        MonthlyReport.report_month == report_data.report_month
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A report already exists for this month. Use PUT to update."
        )
    
    new_report = MonthlyReport(
        psychologist_id=current_user.user_id,
        institution_id=report_data.institution_id,
        report_month=report_data.report_month,
        executive_summary=report_data.executive_summary,
        quantitative_metrics=report_data.quantitative_metrics,
        clinical_outcomes=report_data.clinical_outcomes,
        institutional_impact=report_data.institutional_impact,
        recommendations=report_data.recommendations,
        report_content={
            "service_delivery_metrics": [m.model_dump() for m in report_data.service_delivery_metrics],
            "implementation_metrics": [m.model_dump() for m in report_data.implementation_metrics],
            "outcome_metrics": [m.model_dump() for m in report_data.outcome_metrics]
        },
        submitted_at=datetime.utcnow(),
        status="submitted"
    )
    
    db.add(new_report)
    db.commit()
    db.refresh(new_report)
    
    logger.info(f"Monthly report submitted by {current_user.email} for {report_data.report_month}")
    
    return new_report


@router.get("/monthly", response_model=List[MonthlyReportResponse])
async def get_monthly_reports(
    year: Optional[int] = None,
    institution_id: Optional[UUID] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get monthly reports with optional filters"""
    query = db.query(MonthlyReport)
    
    if current_user.role == "psychologist":
        query = query.filter(MonthlyReport.psychologist_id == current_user.user_id)
    elif current_user.role == "school_admin":
        query = query.filter(MonthlyReport.institution_id == current_user.institution_id)
    
    if institution_id:
        query = query.filter(MonthlyReport.institution_id == institution_id)
    
    reports = query.order_by(MonthlyReport.report_month.desc()).all()
    return reports


@router.get("/monthly/{report_id}", response_model=MonthlyReportResponse)
async def get_monthly_report(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific monthly report"""
    report = db.query(MonthlyReport).filter(MonthlyReport.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if current_user.role == "psychologist" and report.psychologist_id != current_user.user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    if current_user.role == "school_admin" and report.institution_id != current_user.institution_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return report


@router.get("/monthly/{report_id}/pdf")
async def download_monthly_report_pdf(
    report_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Download monthly report as branded PDF"""
    report = db.query(MonthlyReport).filter(MonthlyReport.report_id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    institution = db.query(Institution).filter(Institution.institution_id == report.institution_id).first()
    
    report_data = {
        "report_month": str(report.report_month),
        "psychologist_name": current_user.full_name,
        "institution_name": institution.name if institution else "N/A",
        "executive_summary": report.executive_summary,
        "clinical_outcomes": report.clinical_outcomes,
        "institutional_impact": report.institutional_impact,
        "recommendations": report.recommendations,
        **(report.report_content or {})
    }
    
    pdf_bytes = report_generator.generate_monthly_report(report_data)
    
    return StreamingResponse(
        BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={
            "Content-Disposition": f"attachment; filename=monthly_report_{report.report_month}.pdf"
        }
    )
