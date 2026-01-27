"""
MongoDB-based Students Router for CITTAA Escalation Engine
Student management with anonymization support
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid
import hashlib

from app.models.mongodb import get_mongodb
from app.routers.auth_mongodb import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["Students"])


class StudentCreate(BaseModel):
    institution_id: Optional[str] = None
    student_code: str
    grade: str
    section: Optional[str] = None
    gender: Optional[str] = None
    date_of_birth: Optional[str] = None
    guardian_contact: Optional[str] = None


class StudentUpdate(BaseModel):
    grade: Optional[str] = None
    section: Optional[str] = None
    guardian_contact: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new student record"""
    if current_user.get("role") not in ["psychologist", "admin", "school_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    db = get_mongodb()
    
    existing = db.students.find_one({
        "student_code": student_data.student_code,
        "institution_id": student_data.institution_id
    })
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this code already exists in this institution"
        )
    
    student_doc = {
        "_id": str(uuid.uuid4()),
        "institution_id": student_data.institution_id,
        "student_code": student_data.student_code,
        "grade": student_data.grade,
        "section": student_data.section,
        "gender": student_data.gender,
        "date_of_birth": student_data.date_of_birth,
        "guardian_contact": student_data.guardian_contact,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.students.insert_one(student_doc)
    
    logger.info(f"Student created: {student_data.student_code}")
    
    return {
        "id": student_doc["_id"],
        "student_code": student_doc["student_code"],
        "grade": student_doc["grade"],
        "is_active": True
    }


@router.get("/")
async def get_students(
    institution_id: Optional[str] = None,
    grade: Optional[str] = None,
    is_active: Optional[bool] = True,
    current_user: dict = Depends(get_current_user)
):
    """Get students with optional filters"""
    db = get_mongodb()
    
    query = {}
    
    if current_user.get("role") in ["school_admin", "psychologist"]:
        if current_user.get("institution_id"):
            query["institution_id"] = current_user["institution_id"]
    elif institution_id:
        query["institution_id"] = institution_id
    
    if grade:
        query["grade"] = grade
    if is_active is not None:
        query["is_active"] = is_active
    
    students = list(db.students.find(query).sort("student_code", 1).limit(500))
    
    return [
        {
            "id": s["_id"],
            "student_code": s.get("student_code"),
            "grade": s.get("grade"),
            "section": s.get("section"),
            "gender": s.get("gender"),
            "is_active": s.get("is_active", True),
            "institution_id": s.get("institution_id")
        }
        for s in students
    ]


@router.get("/{student_id}")
async def get_student(
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific student"""
    db = get_mongodb()
    
    student = db.students.find_one({"_id": student_id})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    return {
        "id": student["_id"],
        "student_code": student.get("student_code"),
        "grade": student.get("grade"),
        "section": student.get("section"),
        "gender": student.get("gender"),
        "date_of_birth": student.get("date_of_birth"),
        "guardian_contact": student.get("guardian_contact"),
        "is_active": student.get("is_active", True),
        "institution_id": student.get("institution_id"),
        "created_at": student.get("created_at")
    }


@router.put("/{student_id}")
async def update_student(
    student_id: str,
    update_data: StudentUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update a student record"""
    db = get_mongodb()
    
    student = db.students.find_one({"_id": student_id})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    update_fields = {"updated_at": datetime.utcnow()}
    
    if update_data.grade:
        update_fields["grade"] = update_data.grade
    if update_data.section:
        update_fields["section"] = update_data.section
    if update_data.guardian_contact:
        update_fields["guardian_contact"] = update_data.guardian_contact
    if update_data.is_active is not None:
        update_fields["is_active"] = update_data.is_active
    
    db.students.update_one({"_id": student_id}, {"$set": update_fields})
    
    return {"message": "Student updated successfully", "student_id": student_id}


@router.get("/{student_id}/history")
async def get_student_history(
    student_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get student's counseling history"""
    db = get_mongodb()
    
    student = db.students.find_one({"_id": student_id})
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    sessions = list(db.counseling_sessions.find({"student_id": student_id}).sort("session_date", -1).limit(50))
    
    escalations = list(db.escalation_cases.find({"student_id": student_id}).sort("escalated_at", -1).limit(20))
    
    return {
        "student": {
            "student_id": student["_id"],
            "student_code": student.get("student_code"),
            "grade": student.get("grade"),
            "institution_id": student.get("institution_id")
        },
        "sessions": [
            {
                "session_id": s["_id"],
                "session_date": s.get("session_date"),
                "session_type": s.get("session_type"),
                "risk_level": s.get("risk_level"),
                "presenting_issue": s.get("presenting_issue"),
                "follow_up_needed": s.get("follow_up_needed")
            }
            for s in sessions
        ],
        "escalations": [
            {
                "case_id": e["_id"],
                "escalated_at": e.get("escalated_at"),
                "escalation_level": e.get("escalation_level"),
                "risk_category": e.get("risk_category"),
                "status": e.get("status")
            }
            for e in escalations
        ],
        "risk_analysis": {
            "trend": "stable",
            "total_sessions": len(sessions),
            "total_escalations": len(escalations)
        }
    }


@router.post("/anonymize")
async def anonymize_student(
    student_name: str,
    institution_id: str,
    date_of_birth: str,
    current_user: dict = Depends(get_current_user)
):
    """Generate anonymized student code"""
    raw_data = f"{institution_id}{student_name}{date_of_birth}"
    student_code = hashlib.sha256(raw_data.encode()).hexdigest()[:12].upper()
    anonymized_code = f"STU-{student_code}"
    
    return {
        "student_code": anonymized_code,
        "note": "Use this code when creating the student record"
    }
