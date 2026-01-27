"""
MongoDB-based Reports Router for CITTAA Escalation Engine
Daily, Weekly, and Monthly report submission and management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, date
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid

from app.models.mongodb import get_mongodb
from app.routers.auth_mongodb import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/reports", tags=["Reports"])


class SessionDetail(BaseModel):
    student_code: str
    session_type: str = "individual"
    duration_minutes: int = 45
    presenting_issue: Optional[str] = None
    notes: Optional[str] = None
    follow_up_needed: bool = False


class DailyReportCreate(BaseModel):
    report_date: str
    institution_id: Optional[str] = None
    sessions_details: List[SessionDetail] = []
    key_highlights: Optional[str] = None
    notes_and_observations: Optional[str] = None


class DailyReportResponse(BaseModel):
    id: str
    psychologist_id: str
    report_date: str
    sessions_conducted: int
    key_highlights: Optional[str] = None
    status: str
    created_at: datetime


@router.post("/daily", response_model=DailyReportResponse, status_code=status.HTTP_201_CREATED)
async def submit_daily_report(
    report_data: DailyReportCreate,
    current_user: dict = Depends(get_current_user)
):
    """Submit a Daily Activity Report"""
    if current_user.get("role") not in ["psychologist", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can submit daily reports"
        )
    
    db = get_mongodb()
    
    existing = db.daily_reports.find_one({
        "psychologist_id": current_user["_id"],
        "report_date": report_data.report_date
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A report already exists for this date"
        )
    
    report_doc = {
        "_id": str(uuid.uuid4()),
        "psychologist_id": current_user["_id"],
        "institution_id": report_data.institution_id,
        "report_date": report_data.report_date,
        "sessions_conducted": len(report_data.sessions_details),
        "sessions_details": [s.model_dump() for s in report_data.sessions_details],
        "key_highlights": report_data.key_highlights,
        "notes_and_observations": report_data.notes_and_observations,
        "status": "submitted",
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.daily_reports.insert_one(report_doc)
    
    logger.info(f"Daily report submitted by {current_user['email']} for {report_data.report_date}")
    
    return DailyReportResponse(
        id=report_doc["_id"],
        psychologist_id=report_doc["psychologist_id"],
        report_date=report_doc["report_date"],
        sessions_conducted=report_doc["sessions_conducted"],
        key_highlights=report_doc.get("key_highlights"),
        status=report_doc["status"],
        created_at=report_doc["created_at"]
    )


@router.get("/daily")
async def get_daily_reports(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    current_user: dict = Depends(get_current_user)
):
    """Get daily reports with optional filters"""
    db = get_mongodb()
    
    query = {}
    
    if current_user.get("role") == "psychologist":
        query["psychologist_id"] = current_user["_id"]
    
    if start_date:
        query["report_date"] = {"$gte": start_date}
    if end_date:
        if "report_date" in query:
            query["report_date"]["$lte"] = end_date
        else:
            query["report_date"] = {"$lte": end_date}
    
    reports = list(db.daily_reports.find(query).sort("report_date", -1).limit(100))
    
    return [
        {
            "id": r["_id"],
            "psychologist_id": r["psychologist_id"],
            "report_date": r["report_date"],
            "sessions_conducted": r.get("sessions_conducted", 0),
            "key_highlights": r.get("key_highlights"),
            "status": r.get("status", "submitted"),
            "created_at": r.get("created_at")
        }
        for r in reports
    ]


@router.get("/daily/{report_id}")
async def get_daily_report(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific daily report"""
    db = get_mongodb()
    
    report = db.daily_reports.find_one({"_id": report_id})
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    if current_user.get("role") == "psychologist" and report["psychologist_id"] != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": report["_id"],
        "psychologist_id": report["psychologist_id"],
        "report_date": report["report_date"],
        "sessions_conducted": report.get("sessions_conducted", 0),
        "sessions_details": report.get("sessions_details", []),
        "key_highlights": report.get("key_highlights"),
        "notes_and_observations": report.get("notes_and_observations"),
        "status": report.get("status", "submitted"),
        "created_at": report.get("created_at")
    }


@router.get("/daily/{report_id}/pdf")
async def download_daily_report_pdf(
    report_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download daily report as PDF - placeholder"""
    return {"message": "PDF generation not yet implemented", "report_id": report_id}


class WeeklyReportCreate(BaseModel):
    week_start_date: str
    week_end_date: str
    institution_id: Optional[str] = None
    total_sessions: int = 0
    total_students: int = 0
    summary: Optional[str] = None
    challenges: Optional[str] = None


@router.post("/weekly", status_code=status.HTTP_201_CREATED)
async def submit_weekly_report(
    report_data: WeeklyReportCreate,
    current_user: dict = Depends(get_current_user)
):
    """Submit a Weekly Summary Report"""
    if current_user.get("role") not in ["psychologist", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can submit weekly reports"
        )
    
    db = get_mongodb()
    
    report_doc = {
        "_id": str(uuid.uuid4()),
        "psychologist_id": current_user["_id"],
        "institution_id": report_data.institution_id,
        "week_start_date": report_data.week_start_date,
        "week_end_date": report_data.week_end_date,
        "total_sessions": report_data.total_sessions,
        "total_students": report_data.total_students,
        "summary": report_data.summary,
        "challenges": report_data.challenges,
        "status": "submitted",
        "created_at": datetime.utcnow()
    }
    
    db.weekly_reports.insert_one(report_doc)
    
    return {
        "id": report_doc["_id"],
        "week_start_date": report_doc["week_start_date"],
        "week_end_date": report_doc["week_end_date"],
        "status": "submitted"
    }


@router.get("/weekly")
async def get_weekly_reports(current_user: dict = Depends(get_current_user)):
    """Get weekly reports"""
    db = get_mongodb()
    
    query = {}
    if current_user.get("role") == "psychologist":
        query["psychologist_id"] = current_user["_id"]
    
    reports = list(db.weekly_reports.find(query).sort("week_start_date", -1).limit(50))
    
    return [
        {
            "id": r["_id"],
            "week_start_date": r["week_start_date"],
            "week_end_date": r["week_end_date"],
            "total_sessions": r.get("total_sessions", 0),
            "total_students": r.get("total_students", 0),
            "status": r.get("status", "submitted")
        }
        for r in reports
    ]


@router.get("/weekly/{report_id}")
async def get_weekly_report(report_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific weekly report"""
    db = get_mongodb()
    report = db.weekly_reports.find_one({"_id": report_id})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/weekly/{report_id}/pdf")
async def download_weekly_report_pdf(report_id: str, current_user: dict = Depends(get_current_user)):
    """Download weekly report as PDF - placeholder"""
    return {"message": "PDF generation not yet implemented", "report_id": report_id}


class MonthlyReportCreate(BaseModel):
    report_month: str
    institution_id: Optional[str] = None
    executive_summary: Optional[str] = None
    recommendations: Optional[str] = None


@router.post("/monthly", status_code=status.HTTP_201_CREATED)
async def submit_monthly_report(
    report_data: MonthlyReportCreate,
    current_user: dict = Depends(get_current_user)
):
    """Submit a Monthly Metrics Report"""
    if current_user.get("role") not in ["psychologist", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can submit monthly reports"
        )
    
    db = get_mongodb()
    
    report_doc = {
        "_id": str(uuid.uuid4()),
        "psychologist_id": current_user["_id"],
        "institution_id": report_data.institution_id,
        "report_month": report_data.report_month,
        "executive_summary": report_data.executive_summary,
        "recommendations": report_data.recommendations,
        "status": "submitted",
        "created_at": datetime.utcnow()
    }
    
    db.monthly_reports.insert_one(report_doc)
    
    return {
        "id": report_doc["_id"],
        "report_month": report_doc["report_month"],
        "status": "submitted"
    }


@router.get("/monthly")
async def get_monthly_reports(current_user: dict = Depends(get_current_user)):
    """Get monthly reports"""
    db = get_mongodb()
    
    query = {}
    if current_user.get("role") == "psychologist":
        query["psychologist_id"] = current_user["_id"]
    
    reports = list(db.monthly_reports.find(query).sort("report_month", -1).limit(24))
    
    return [
        {
            "id": r["_id"],
            "report_month": r["report_month"],
            "executive_summary": r.get("executive_summary"),
            "status": r.get("status", "submitted")
        }
        for r in reports
    ]


@router.get("/monthly/{report_id}")
async def get_monthly_report(report_id: str, current_user: dict = Depends(get_current_user)):
    """Get a specific monthly report"""
    db = get_mongodb()
    report = db.monthly_reports.find_one({"_id": report_id})
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    return report


@router.get("/monthly/{report_id}/pdf")
async def download_monthly_report_pdf(report_id: str, current_user: dict = Depends(get_current_user)):
    """Download monthly report as PDF - placeholder"""
    return {"message": "PDF generation not yet implemented", "report_id": report_id}
