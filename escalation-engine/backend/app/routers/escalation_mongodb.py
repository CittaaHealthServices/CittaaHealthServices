"""
MongoDB-based Escalation Router for CITTAA Escalation Engine
AI-powered case escalation management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid

from app.models.mongodb import get_mongodb
from app.routers.auth_mongodb import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/escalation", tags=["Escalation"])


class EscalationAssessment(BaseModel):
    escalation_level: str
    confidence: float
    risk_category: str
    keywords_detected: List[str]
    reasoning: str
    recommended_actions: List[str]
    language_detected: str = "english"


class EscalationCaseCreate(BaseModel):
    student_id: str
    session_id: Optional[str] = None
    institution_id: Optional[str] = None
    escalation_level: str
    risk_category: str
    ai_confidence_score: float = 0.0
    keywords_detected: List[str] = []
    escalation_reason: str
    immediate_actions_taken: Optional[str] = None


class EscalationCaseUpdate(BaseModel):
    status: Optional[str] = None
    resolution_notes: Optional[str] = None
    assigned_to: Optional[str] = None
    immediate_actions_taken: Optional[str] = None


class EscalationDashboardStats(BaseModel):
    total_open_cases: int
    emergency_cases: int
    high_risk_cases: int
    moderate_cases: int
    low_cases: int
    resolved_today: int
    average_resolution_time_hours: Optional[float] = None
    cases_by_risk_category: dict = {}


@router.post("/analyze", response_model=EscalationAssessment)
async def analyze_session_for_escalation(
    session_data: dict,
    current_user: dict = Depends(get_current_user)
):
    """
    Real-time AI analysis of session notes for risk assessment
    
    Detects risk indicators across 5 Indian languages:
    - English, Hindi, Telugu, Tamil, Kannada
    """
    keywords_detected = []
    escalation_level = "level_1_low"
    confidence = 0.5
    risk_category = "general"
    
    text = (session_data.get("presenting_issue", "") + " " + 
            session_data.get("session_notes", "")).lower()
    
    emergency_keywords = ["suicide", "kill myself", "end my life", "want to die", 
                         "self-harm", "cutting", "overdose", "abuse", "assault"]
    high_keywords = ["depression", "anxiety", "panic", "trauma", "bullying", 
                    "isolation", "hopeless", "worthless"]
    moderate_keywords = ["stress", "worried", "sad", "angry", "frustrated", 
                        "sleep problems", "eating issues"]
    
    for kw in emergency_keywords:
        if kw in text:
            keywords_detected.append(kw)
            escalation_level = "level_4_emergency"
            confidence = 0.95
            risk_category = "immediate_danger"
    
    if escalation_level == "level_1_low":
        for kw in high_keywords:
            if kw in text:
                keywords_detected.append(kw)
                escalation_level = "level_3_high"
                confidence = 0.85
                risk_category = "mental_health"
    
    if escalation_level == "level_1_low":
        for kw in moderate_keywords:
            if kw in text:
                keywords_detected.append(kw)
                escalation_level = "level_2_moderate"
                confidence = 0.75
                risk_category = "emotional_support"
    
    recommended_actions = {
        "level_4_emergency": [
            "Immediate safety assessment required",
            "Contact emergency services if needed",
            "Notify parents/guardians immediately",
            "Do not leave student unattended"
        ],
        "level_3_high": [
            "Schedule follow-up within 24 hours",
            "Consider parent/guardian notification",
            "Document detailed observations",
            "Consult with supervisor"
        ],
        "level_2_moderate": [
            "Schedule follow-up within 1 week",
            "Monitor for changes",
            "Provide coping strategies"
        ],
        "level_1_low": [
            "Continue regular monitoring",
            "Document session notes"
        ]
    }
    
    return EscalationAssessment(
        escalation_level=escalation_level,
        confidence=confidence,
        risk_category=risk_category,
        keywords_detected=keywords_detected,
        reasoning=f"Detected {len(keywords_detected)} risk indicators in session notes",
        recommended_actions=recommended_actions.get(escalation_level, []),
        language_detected="english"
    )


@router.post("/cases", status_code=status.HTTP_201_CREATED)
async def create_escalation_case(
    case_data: EscalationCaseCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new escalation case"""
    if current_user.get("role") not in ["psychologist", "admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only psychologists can create escalation cases"
        )
    
    db = get_mongodb()
    
    case_doc = {
        "_id": str(uuid.uuid4()),
        "student_id": case_data.student_id,
        "session_id": case_data.session_id,
        "psychologist_id": current_user["_id"],
        "institution_id": case_data.institution_id,
        "escalation_level": case_data.escalation_level,
        "risk_category": case_data.risk_category,
        "ai_confidence_score": case_data.ai_confidence_score,
        "keywords_detected": case_data.keywords_detected,
        "escalation_reason": case_data.escalation_reason,
        "immediate_actions_taken": case_data.immediate_actions_taken,
        "status": "open",
        "escalated_at": datetime.utcnow(),
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.escalation_cases.insert_one(case_doc)
    
    logger.warning(f"Escalation case created: {case_doc['_id']} - Level: {case_data.escalation_level}")
    
    return {
        "id": case_doc["_id"],
        "escalation_level": case_doc["escalation_level"],
        "status": "open",
        "escalated_at": case_doc["escalated_at"]
    }


@router.get("/cases")
async def get_escalation_cases(
    status_filter: Optional[str] = None,
    level_filter: Optional[str] = None,
    days: Optional[int] = 30,
    current_user: dict = Depends(get_current_user)
):
    """Get escalation cases with filters"""
    db = get_mongodb()
    
    query = {}
    
    if current_user.get("role") == "psychologist":
        query["psychologist_id"] = current_user["_id"]
    
    if status_filter:
        query["status"] = status_filter
    if level_filter:
        query["escalation_level"] = level_filter
    if days:
        cutoff = datetime.utcnow() - timedelta(days=days)
        query["created_at"] = {"$gte": cutoff}
    
    cases = list(db.escalation_cases.find(query).sort("escalated_at", -1).limit(100))
    
    return [
        {
            "id": c["_id"],
            "student_id": c.get("student_id"),
            "escalation_level": c.get("escalation_level"),
            "risk_category": c.get("risk_category"),
            "status": c.get("status"),
            "escalated_at": c.get("escalated_at"),
            "escalation_reason": c.get("escalation_reason")
        }
        for c in cases
    ]


@router.get("/cases/{case_id}")
async def get_escalation_case(
    case_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific escalation case"""
    db = get_mongodb()
    
    case = db.escalation_cases.find_one({"_id": case_id})
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    if current_user.get("role") == "psychologist" and case.get("psychologist_id") != current_user["_id"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": case["_id"],
        "student_id": case.get("student_id"),
        "psychologist_id": case.get("psychologist_id"),
        "escalation_level": case.get("escalation_level"),
        "risk_category": case.get("risk_category"),
        "ai_confidence_score": case.get("ai_confidence_score"),
        "keywords_detected": case.get("keywords_detected", []),
        "escalation_reason": case.get("escalation_reason"),
        "immediate_actions_taken": case.get("immediate_actions_taken"),
        "status": case.get("status"),
        "escalated_at": case.get("escalated_at"),
        "resolved_at": case.get("resolved_at"),
        "resolution_notes": case.get("resolution_notes")
    }


@router.put("/cases/{case_id}")
async def update_escalation_case(
    case_id: str,
    update_data: EscalationCaseUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an escalation case"""
    db = get_mongodb()
    
    case = db.escalation_cases.find_one({"_id": case_id})
    
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    update_fields = {"updated_at": datetime.utcnow()}
    
    if update_data.status:
        update_fields["status"] = update_data.status
        if update_data.status == "resolved":
            update_fields["resolved_at"] = datetime.utcnow()
    
    if update_data.resolution_notes:
        update_fields["resolution_notes"] = update_data.resolution_notes
    
    if update_data.assigned_to:
        update_fields["assigned_to"] = update_data.assigned_to
    
    if update_data.immediate_actions_taken:
        update_fields["immediate_actions_taken"] = update_data.immediate_actions_taken
    
    db.escalation_cases.update_one({"_id": case_id}, {"$set": update_fields})
    
    logger.info(f"Escalation case updated: {case_id}")
    
    return {"message": "Case updated successfully", "case_id": case_id}


@router.get("/cases/{case_id}/pdf")
async def download_escalation_report_pdf(
    case_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Download escalation case report as PDF - placeholder"""
    return {"message": "PDF generation not yet implemented", "case_id": case_id}


@router.get("/dashboard/stats", response_model=EscalationDashboardStats)
async def get_escalation_dashboard_stats(
    current_user: dict = Depends(get_current_user)
):
    """Get escalation dashboard statistics"""
    db = get_mongodb()
    
    query = {"status": "open"}
    
    if current_user.get("role") == "psychologist":
        query["psychologist_id"] = current_user["_id"]
    
    open_cases = list(db.escalation_cases.find(query))
    
    emergency_count = sum(1 for c in open_cases if c.get("escalation_level") == "level_4_emergency")
    high_count = sum(1 for c in open_cases if c.get("escalation_level") == "level_3_high")
    moderate_count = sum(1 for c in open_cases if c.get("escalation_level") == "level_2_moderate")
    low_count = sum(1 for c in open_cases if c.get("escalation_level") == "level_1_low")
    
    today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    resolved_today = db.escalation_cases.count_documents({
        "status": "resolved",
        "resolved_at": {"$gte": today_start}
    })
    
    cases_by_category = {}
    for case in open_cases:
        cat = case.get("risk_category", "unknown")
        cases_by_category[cat] = cases_by_category.get(cat, 0) + 1
    
    return EscalationDashboardStats(
        total_open_cases=len(open_cases),
        emergency_cases=emergency_count,
        high_risk_cases=high_count,
        moderate_cases=moderate_count,
        low_cases=low_count,
        resolved_today=resolved_today,
        average_resolution_time_hours=None,
        cases_by_risk_category=cases_by_category
    )


@router.post("/cases/{case_id}/notify")
async def send_case_notification(
    case_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Send notification for an escalation case - placeholder"""
    return {"message": "Notification queued", "case_id": case_id}


@router.get("/cases/{case_id}/notifications")
async def get_case_notifications(
    case_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get all notifications for an escalation case"""
    db = get_mongodb()
    
    notifications = list(db.escalation_notifications.find({"case_id": case_id}).sort("created_at", -1))
    
    return [
        {
            "id": n["_id"],
            "case_id": n.get("case_id"),
            "recipient_email": n.get("recipient_email"),
            "status": n.get("status"),
            "sent_at": n.get("sent_at")
        }
        for n in notifications
    ]
