"""
MongoDB-based Institutions Router for CITTAA Escalation Engine
School and hospital management
"""

from fastapi import APIRouter, Depends, HTTPException, status
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel
import logging
import uuid

from app.models.mongodb import get_mongodb
from app.routers.auth_mongodb import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/institutions", tags=["Institutions"])


class InstitutionCreate(BaseModel):
    name: str
    type: str = "school"
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    package_type: str = "essential"


class InstitutionUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None
    state: Optional[str] = None
    district: Optional[str] = None
    package_type: Optional[str] = None
    is_active: Optional[bool] = None


@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_institution(
    institution_data: InstitutionCreate,
    current_user: dict = Depends(get_current_user)
):
    """Create a new institution (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can create institutions"
        )
    
    db = get_mongodb()
    
    existing = db.institutions.find_one({"name": institution_data.name})
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Institution with this name already exists"
        )
    
    institution_doc = {
        "_id": str(uuid.uuid4()),
        "name": institution_data.name,
        "type": institution_data.type,
        "address": institution_data.address,
        "contact_email": institution_data.contact_email,
        "contact_phone": institution_data.contact_phone,
        "state": institution_data.state,
        "district": institution_data.district,
        "package_type": institution_data.package_type,
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.institutions.insert_one(institution_doc)
    
    logger.info(f"Institution created: {institution_data.name} by {current_user['email']}")
    
    return {
        "id": institution_doc["_id"],
        "name": institution_doc["name"],
        "type": institution_doc["type"],
        "is_active": True
    }


@router.get("/")
async def get_institutions(
    type_filter: Optional[str] = None,
    state: Optional[str] = None,
    is_active: Optional[bool] = True,
    current_user: dict = Depends(get_current_user)
):
    """Get all institutions with optional filters"""
    db = get_mongodb()
    
    query = {}
    
    if current_user.get("role") != "admin":
        if current_user.get("institution_id"):
            query["_id"] = current_user["institution_id"]
    else:
        if type_filter:
            query["type"] = type_filter
        if state:
            query["state"] = state
        if is_active is not None:
            query["is_active"] = is_active
    
    institutions = list(db.institutions.find(query).sort("name", 1).limit(100))
    
    return [
        {
            "id": i["_id"],
            "name": i.get("name"),
            "type": i.get("type"),
            "address": i.get("address"),
            "contact_email": i.get("contact_email"),
            "contact_phone": i.get("contact_phone"),
            "state": i.get("state"),
            "district": i.get("district"),
            "package_type": i.get("package_type"),
            "is_active": i.get("is_active", True)
        }
        for i in institutions
    ]


@router.get("/{institution_id}")
async def get_institution(
    institution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get a specific institution"""
    db = get_mongodb()
    
    institution = db.institutions.find_one({"_id": institution_id})
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    if current_user.get("role") != "admin" and current_user.get("institution_id") != institution_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return {
        "id": institution["_id"],
        "name": institution.get("name"),
        "type": institution.get("type"),
        "address": institution.get("address"),
        "contact_email": institution.get("contact_email"),
        "contact_phone": institution.get("contact_phone"),
        "state": institution.get("state"),
        "district": institution.get("district"),
        "package_type": institution.get("package_type"),
        "is_active": institution.get("is_active", True),
        "created_at": institution.get("created_at")
    }


@router.put("/{institution_id}")
async def update_institution(
    institution_id: str,
    update_data: InstitutionUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Update an institution (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    
    institution = db.institutions.find_one({"_id": institution_id})
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    update_fields = {"updated_at": datetime.utcnow()}
    
    if update_data.name:
        update_fields["name"] = update_data.name
    if update_data.address:
        update_fields["address"] = update_data.address
    if update_data.contact_email:
        update_fields["contact_email"] = update_data.contact_email
    if update_data.contact_phone:
        update_fields["contact_phone"] = update_data.contact_phone
    if update_data.state:
        update_fields["state"] = update_data.state
    if update_data.district:
        update_fields["district"] = update_data.district
    if update_data.package_type:
        update_fields["package_type"] = update_data.package_type
    if update_data.is_active is not None:
        update_fields["is_active"] = update_data.is_active
    
    db.institutions.update_one({"_id": institution_id}, {"$set": update_fields})
    
    return {"message": "Institution updated successfully", "institution_id": institution_id}


@router.get("/{institution_id}/stats")
async def get_institution_stats(
    institution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Get statistics for an institution"""
    db = get_mongodb()
    
    institution = db.institutions.find_one({"_id": institution_id})
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    if current_user.get("role") != "admin" and current_user.get("institution_id") != institution_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    total_students = db.students.count_documents({"institution_id": institution_id})
    active_students = db.students.count_documents({"institution_id": institution_id, "is_active": True})
    
    total_users = db.users.count_documents({"institution_id": institution_id})
    psychologists = db.users.count_documents({"institution_id": institution_id, "role": "psychologist"})
    
    return {
        "institution": {
            "institution_id": institution["_id"],
            "name": institution.get("name"),
            "type": institution.get("type"),
            "package_type": institution.get("package_type")
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
    institution_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Deactivate an institution (admin only)"""
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    
    db = get_mongodb()
    
    institution = db.institutions.find_one({"_id": institution_id})
    
    if not institution:
        raise HTTPException(status_code=404, detail="Institution not found")
    
    db.institutions.update_one(
        {"_id": institution_id},
        {"$set": {"is_active": False, "updated_at": datetime.utcnow()}}
    )
    
    logger.info(f"Institution deactivated: {institution.get('name')} by {current_user['email']}")
    
    return {"message": "Institution deactivated successfully"}
