"""
Students Router for CITTAA Escalation Engine
Student management with anonymization support
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import logging

from app.models.database import get_db
from app.models.user import User
from app.models.student import Student
from app.models.institution import Institution
from app.models.counseling_session import CounselingSession
from app.models.escalation_case import EscalationCase
from app.schemas.student import StudentCreate, StudentResponse, StudentUpdate
from app.utils.security import get_current_user, anonymize_student_data

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/students", tags=["Students"])


@router.post("/", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    student_data: StudentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new student record
    
    Student data is automatically anonymized using a hash of:
    institution_id + name + date_of_birth
    
    This ensures DPDP Act 2023 compliance while maintaining
    the ability to track student progress across sessions.
    """
    if current_user.role not in ["psychologist", "admin", "school_admin"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Insufficient permissions"
        )
    
    # Verify institution exists
    institution = db.query(Institution).filter(
        Institution.institution_id == student_data.institution_id
    ).first()
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Check if student code already exists
    existing = db.query(Student).filter(
        Student.student_code == student_data.student_code,
        Student.institution_id == student_data.institution_id
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Student with this code already exists in this institution"
        )
    
    # Create student
    new_student = Student(
        institution_id=student_data.institution_id,
        student_code=student_data.student_code,
        grade=student_data.grade,
        section=student_data.section,
        gender=student_data.gender,
        date_of_birth=student_data.date_of_birth,
        guardian_contact=student_data.guardian_contact,
        enrollment_date=student_data.enrollment_date
    )
    
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    
    logger.info(f"Student created: {new_student.student_code} in institution {institution.name}")
    
    return new_student


@router.get("/", response_model=List[StudentResponse])
async def get_students(
    institution_id: Optional[UUID] = None,
    grade: Optional[str] = None,
    is_active: Optional[bool] = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get students with optional filters"""
    query = db.query(Student)
    
    # Role-based filtering
    if current_user.role == "school_admin":
        query = query.filter(Student.institution_id == current_user.institution_id)
    elif current_user.role == "psychologist":
        query = query.filter(Student.institution_id == current_user.institution_id)
    elif institution_id:
        query = query.filter(Student.institution_id == institution_id)
    
    if grade:
        query = query.filter(Student.grade == grade)
    if is_active is not None:
        query = query.filter(Student.is_active == is_active)
    
    students = query.order_by(Student.student_code).all()
    return students


@router.get("/{student_id}", response_model=StudentResponse)
async def get_student(
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific student"""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check access
    if current_user.role in ["psychologist", "school_admin"]:
        if student.institution_id != current_user.institution_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    return student


@router.put("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: UUID,
    update_data: StudentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a student record"""
    student = db.query(Student).filter(Student.student_id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check access
    if current_user.role in ["psychologist", "school_admin"]:
        if student.institution_id != current_user.institution_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    if update_data.grade:
        student.grade = update_data.grade
    if update_data.section:
        student.section = update_data.section
    if update_data.guardian_contact:
        student.guardian_contact = update_data.guardian_contact
    if update_data.is_active is not None:
        student.is_active = update_data.is_active
    
    student.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(student)
    
    return student


@router.get("/{student_id}/history")
async def get_student_history(
    student_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get student's counseling history
    
    Returns:
    - All counseling sessions
    - Escalation cases
    - Risk trend analysis
    """
    student = db.query(Student).filter(Student.student_id == student_id).first()
    
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    # Check access
    if current_user.role in ["psychologist", "school_admin"]:
        if student.institution_id != current_user.institution_id:
            raise HTTPException(status_code=403, detail="Access denied")
    
    # Get sessions
    sessions = db.query(CounselingSession).filter(
        CounselingSession.student_id == student_id
    ).order_by(CounselingSession.session_date.desc()).all()
    
    # Get escalation cases
    escalations = db.query(EscalationCase).filter(
        EscalationCase.student_id == student_id
    ).order_by(EscalationCase.escalated_at.desc()).all()
    
    # Calculate risk trend
    risk_levels = []
    for session in sessions:
        if session.risk_level:
            level_score = {
                "low": 1, "moderate": 2, "high": 3, "imminent": 4
            }.get(session.risk_level, 1)
            risk_levels.append({
                "date": str(session.session_date),
                "level": session.risk_level,
                "score": level_score
            })
    
    # Determine trend
    if len(risk_levels) >= 2:
        recent_avg = sum(r["score"] for r in risk_levels[:3]) / min(3, len(risk_levels))
        older_avg = sum(r["score"] for r in risk_levels[3:6]) / max(1, min(3, len(risk_levels) - 3))
        
        if recent_avg > older_avg + 0.5:
            trend = "escalating"
        elif recent_avg < older_avg - 0.5:
            trend = "improving"
        else:
            trend = "stable"
    else:
        trend = "insufficient_data"
    
    return {
        "student": {
            "student_id": str(student.student_id),
            "student_code": student.student_code,
            "grade": student.grade,
            "institution_id": str(student.institution_id)
        },
        "sessions": [
            {
                "session_id": str(s.session_id),
                "session_date": str(s.session_date),
                "session_type": s.session_type,
                "risk_level": s.risk_level,
                "presenting_issue": s.presenting_issue,
                "follow_up_needed": s.follow_up_needed
            }
            for s in sessions
        ],
        "escalations": [
            {
                "case_id": str(e.case_id),
                "escalated_at": str(e.escalated_at),
                "escalation_level": e.escalation_level,
                "risk_category": e.risk_category,
                "status": e.status
            }
            for e in escalations
        ],
        "risk_analysis": {
            "trend": trend,
            "total_sessions": len(sessions),
            "total_escalations": len(escalations),
            "risk_history": risk_levels
        }
    }


@router.post("/anonymize")
async def anonymize_student(
    student_name: str,
    institution_id: UUID,
    date_of_birth: str,
    current_user: User = Depends(get_current_user)
):
    """
    Generate anonymized student code
    
    Uses SHA-256 hash of institution_id + name + dob
    to create a unique, non-reversible identifier.
    
    This supports DPDP Act 2023 compliance.
    """
    anonymized_code = anonymize_student_data(
        str(institution_id),
        student_name,
        date_of_birth
    )
    
    return {
        "student_code": anonymized_code,
        "note": "Use this code when creating the student record"
    }
