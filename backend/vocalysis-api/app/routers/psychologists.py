"""
Psychologist Mapping Router for Vocalysis API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import List
from bson import ObjectId

from app.database import db
from app.models import (
    PsychologistAssignmentCreate, PsychologistAssignmentResponse,
    PsychologistWithPatients, UserRole
)
from app.routers.auth import get_current_user, get_current_admin, get_current_psychologist

router = APIRouter(prefix="/api/v1/psychologists", tags=["Psychologist Mapping"])


@router.get("/", response_model=List[PsychologistWithPatients])
async def get_all_psychologists(current_user = Depends(get_current_admin)):
    """Get all psychologists with their patient counts (admin only)"""
    cursor = db.users.find({"role": UserRole.PSYCHOLOGIST.value})
    
    psychologists = []
    async for doc in cursor:
        # Count assigned patients
        patient_count = await db.psychologist_assignments.count_documents({
            "psychologist_id": str(doc["_id"]),
            "status": "active"
        })
        
        # Get patient details
        assignments_cursor = db.psychologist_assignments.find({
            "psychologist_id": str(doc["_id"]),
            "status": "active"
        })
        
        patients = []
        async for assignment in assignments_cursor:
            patient = await db.users.find_one({"_id": ObjectId(assignment["patient_id"])})
            if patient:
                patients.append({
                    "id": str(patient["_id"]),
                    "full_name": patient["full_name"],
                    "email": patient["email"],
                    "assignment_date": assignment["assignment_date"].isoformat()
                })
        
        psychologists.append(PsychologistWithPatients(
            id=str(doc["_id"]),
            email=doc["email"],
            full_name=doc["full_name"],
            patient_count=patient_count,
            patients=patients
        ))
    
    return psychologists


@router.post("/assign", response_model=PsychologistAssignmentResponse)
async def assign_patient_to_psychologist(
    assignment_data: PsychologistAssignmentCreate,
    current_user = Depends(get_current_admin)
):
    """Assign a patient to a psychologist (admin only)"""
    # Verify psychologist exists and has correct role
    psychologist = await db.users.find_one({
        "_id": ObjectId(assignment_data.psychologist_id),
        "role": UserRole.PSYCHOLOGIST.value
    })
    if not psychologist:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Psychologist not found"
        )
    
    # Verify patient exists
    patient = await db.users.find_one({
        "_id": ObjectId(assignment_data.patient_id)
    })
    if not patient:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Patient not found"
        )
    
    # Check if assignment already exists
    existing = await db.psychologist_assignments.find_one({
        "psychologist_id": assignment_data.psychologist_id,
        "patient_id": assignment_data.patient_id,
        "status": "active"
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Patient already assigned to this psychologist"
        )
    
    now = datetime.utcnow()
    assignment_doc = {
        "psychologist_id": assignment_data.psychologist_id,
        "patient_id": assignment_data.patient_id,
        "assigned_by": str(current_user["_id"]),
        "assignment_date": now,
        "status": "active",
        "notes": assignment_data.notes,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.psychologist_assignments.insert_one(assignment_doc)
    
    # Update participant record if exists
    await db.clinical_trial_participants.update_one(
        {"user_id": assignment_data.patient_id},
        {
            "$set": {
                "assigned_psychologist": assignment_data.psychologist_id,
                "assignment_date": now,
                "updated_at": now
            }
        }
    )
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(current_user["_id"]),
        "action": "patient_assigned",
        "entity_type": "psychologist_assignment",
        "entity_id": str(result.inserted_id),
        "details": {
            "psychologist_id": assignment_data.psychologist_id,
            "patient_id": assignment_data.patient_id
        },
        "timestamp": now
    })
    
    return PsychologistAssignmentResponse(
        id=str(result.inserted_id),
        psychologist_id=assignment_doc["psychologist_id"],
        patient_id=assignment_doc["patient_id"],
        assigned_by=assignment_doc["assigned_by"],
        assignment_date=assignment_doc["assignment_date"],
        status=assignment_doc["status"],
        notes=assignment_doc["notes"],
        created_at=assignment_doc["created_at"],
        updated_at=assignment_doc["updated_at"]
    )


@router.delete("/assign/{assignment_id}")
async def remove_assignment(
    assignment_id: str,
    current_user = Depends(get_current_admin)
):
    """Remove a patient-psychologist assignment (admin only)"""
    assignment = await db.psychologist_assignments.find_one({
        "_id": ObjectId(assignment_id)
    })
    
    if not assignment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Assignment not found"
        )
    
    now = datetime.utcnow()
    await db.psychologist_assignments.update_one(
        {"_id": ObjectId(assignment_id)},
        {"$set": {"status": "inactive", "updated_at": now}}
    )
    
    # Update participant record
    await db.clinical_trial_participants.update_one(
        {"user_id": assignment["patient_id"]},
        {
            "$set": {
                "assigned_psychologist": None,
                "assignment_date": None,
                "updated_at": now
            }
        }
    )
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(current_user["_id"]),
        "action": "assignment_removed",
        "entity_type": "psychologist_assignment",
        "entity_id": assignment_id,
        "details": {
            "psychologist_id": assignment["psychologist_id"],
            "patient_id": assignment["patient_id"]
        },
        "timestamp": now
    })
    
    return {"message": "Assignment removed successfully"}


@router.get("/my-patients", response_model=List[dict])
async def get_my_patients(current_user = Depends(get_current_psychologist)):
    """Get patients assigned to current psychologist"""
    cursor = db.psychologist_assignments.find({
        "psychologist_id": str(current_user["_id"]),
        "status": "active"
    })
    
    patients = []
    async for assignment in cursor:
        patient = await db.users.find_one({"_id": ObjectId(assignment["patient_id"])})
        if patient:
            # Get participant info if exists
            participant = await db.clinical_trial_participants.find_one({
                "user_id": str(patient["_id"])
            })
            
            # Get latest analysis
            latest_analysis = await db.voice_analysis_reports.find_one(
                {"user_id": str(patient["_id"])},
                sort=[("created_at", -1)]
            )
            
            patients.append({
                "id": str(patient["_id"]),
                "full_name": patient["full_name"],
                "email": patient["email"],
                "phone": patient.get("phone"),
                "assignment_date": assignment["assignment_date"].isoformat(),
                "participant_info": {
                    "age": participant.get("age") if participant else None,
                    "gender": participant.get("gender") if participant else None,
                    "voice_samples_collected": participant.get("voice_samples_collected", 0) if participant else 0,
                    "baseline_established": participant.get("baseline_established", False) if participant else False
                } if participant else None,
                "latest_analysis": {
                    "mental_health_score": latest_analysis.get("mental_health_score"),
                    "risk_level": latest_analysis.get("risk_level"),
                    "created_at": latest_analysis.get("created_at").isoformat()
                } if latest_analysis else None
            })
    
    return patients


@router.get("/patient/{patient_id}/reports")
async def get_patient_reports(
    patient_id: str,
    current_user = Depends(get_current_psychologist)
):
    """Get all voice analysis reports for a patient (psychologist only)"""
    # Verify psychologist is assigned to this patient
    if current_user.get("role") != UserRole.ADMIN.value:
        assignment = await db.psychologist_assignments.find_one({
            "psychologist_id": str(current_user["_id"]),
            "patient_id": patient_id,
            "status": "active"
        })
        if not assignment:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this patient's reports"
            )
    
    cursor = db.voice_analysis_reports.find({
        "user_id": patient_id
    }).sort("created_at", -1)
    
    reports = []
    async for doc in cursor:
        reports.append({
            "id": str(doc["_id"]),
            "mental_health_score": doc.get("mental_health_score"),
            "confidence_score": doc.get("confidence_score"),
            "phq9_score": doc.get("phq9_score"),
            "gad7_score": doc.get("gad7_score"),
            "pss_score": doc.get("pss_score"),
            "wemwbs_score": doc.get("wemwbs_score"),
            "risk_level": doc.get("risk_level"),
            "predicted_condition": doc.get("predicted_condition"),
            "recommendations": doc.get("recommendations", []),
            "created_at": doc.get("created_at").isoformat()
        })
    
    return reports
