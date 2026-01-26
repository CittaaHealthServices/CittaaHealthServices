"""
Institutions Router for CITTAA Escalation Engine
School and hospital management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Optional
from uuid import UUID
import logging

from app.models.database import get_db
from app.models.user import User
from app.models.institution import Institution
from app.models.student import Student
from app.schemas.institution import InstitutionCreate, InstitutionResponse, InstitutionUpdate
from app.utils.security import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/institutions", tags=["Institutions"])


@router.post("/", response_model=InstitutionResponse, status_code=status.HTTP_201_CREATED)
async def create_institution(
    institution_data: InstitutionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new institution (admin only)
    
    Institution types:
    - school: Educational institution
    - hospital: Healthcare facility
    
    Package types:
    - essential: Basic features
    - comprehensive: Standard features
    - premium: All features including advanced AI
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create institutions"
        )
    
    # Check for duplicate name
    existing = db.query(Institution).filter(
        Institution.name == institution_data.name
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution with this name already exists"
        )
    
    new_institution = Institution(
        name=institution_data.name,
        type=institution_data.type,
        address=institution_data.address,
        contact_email=institution_data.contact_email,
        contact_phone=institution_data.contact_phone,
        state=institution_data.state,
        district=institution_data.district,
        package_type=institution_data.package_type
    )
    
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    
    logger.info(f"Institution created: {new_institution.name} by {current_user.email}")
    
    return new_institution


@router.get("/", response_model=List[InstitutionResponse])
async def get_institutions(
    type_filter: Optional[str] = None,
    state: Optional[str] = None,
    is_active: Optional[bool] = True,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all institutions with optional filters"""
    query = db.query(Institution)
    
    # Non-admins can only see their own institution
    if current_user.role != "admin":
        query = query.filter(Institution.institution_id == current_user.institution_id)
    else:
        if type_filter:
            query = query.filter(Institution.type == type_filter)
        if state:
            query = query.filter(Institution.state == state)
        if is_active is not None:
            query = query.filter(Institution.is_active == is_active)
    
    institutions = query.order_by(Institution.name).all()
    return institutions


@router.get("/{institution_id}", response_model=InstitutionResponse)
async def get_institution(
    institution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific institution"""
    institution = db.query(Institution).filter(
        Institution.institution_id == institution_id
    ).first()
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Check access
    if current_user.role != "admin" and current_user.institution_id != institution_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return institution


@router.put("/{institution_id}", response_model=InstitutionResponse)
async def update_institution(
    institution_id: UUID,
    update_data: InstitutionUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update an institution (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    institution = db.query(Institution).filter(
        Institution.institution_id == institution_id
    ).first()
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    if update_data.name:
        institution.name = update_data.name
    if update_data.address:
        institution.address = update_data.address
    if update_data.contact_email:
        institution.contact_email = update_data.contact_email
    if update_data.contact_phone:
        institution.contact_phone = update_data.contact_phone
    if update_data.state:
        institution.state = update_data.state
    if update_data.district:
        institution.district = update_data.district
    if update_data.package_type:
        institution.package_type = update_data.package_type
    if update_data.is_active is not None:
        institution.is_active = update_data.is_active
    
    institution.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(institution)
    
    return institution


@router.get("/{institution_id}/stats")
async def get_institution_stats(
    institution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get statistics for an institution"""
    institution = db.query(Institution).filter(
        Institution.institution_id == institution_id
    ).first()
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Check access
    if current_user.role != "admin" and current_user.institution_id != institution_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Count students
    total_students = db.query(Student).filter(
        Student.institution_id == institution_id
    ).count()
    
    active_students = db.query(Student).filter(
        Student.institution_id == institution_id,
        Student.is_active == True
    ).count()
    
    # Count users
    total_users = db.query(User).filter(
        User.institution_id == institution_id
    ).count()
    
    psychologists = db.query(User).filter(
        User.institution_id == institution_id,
        User.role == "psychologist"
    ).count()
    
    return {
        "institution": {
            "institution_id": str(institution.institution_id),
            "name": institution.name,
            "type": institution.type,
            "package_type": institution.package_type
        },
        "students": {
            "total": total_students,
            "active": active_students
        },
        "users": {
            "total": total_users,
            "psychologists": psychologists
        }
    }


@router.delete("/{institution_id}")
async def deactivate_institution(
    institution_id: UUID,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Deactivate an institution (admin only)"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    institution = db.query(Institution).filter(
        Institution.institution_id == institution_id
    ).first()
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    institution.is_active = False
    institution.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Institution deactivated: {institution.name} by {current_user.email}")
    
    return {"message": "Institution deactivated successfully"}
