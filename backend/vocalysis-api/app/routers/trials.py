"""
Clinical Trials Router for Vocalysis API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.database import db
from app.models import (
    ParticipantCreate, ParticipantResponse, ParticipantApproval,
    ApprovalStatus, TrialStatus
)
from app.routers.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/v1/trials", tags=["Clinical Trials"])


@router.post("/register", response_model=ParticipantResponse)
async def register_for_trial(
    participant_data: ParticipantCreate,
    current_user = Depends(get_current_user)
):
    """Register current user for clinical trial"""
    # Check if already registered
    existing = await db.clinical_trial_participants.find_one({
        "user_id": str(current_user["_id"])
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Already registered for clinical trial"
        )
    
    now = datetime.utcnow()
    participant_doc = {
        "user_id": str(current_user["_id"]),
        "age": participant_data.age,
        "gender": participant_data.gender,
        "phone": participant_data.phone,
        "institution": participant_data.institution,
        "consent_given": participant_data.consent_given,
        "consent_timestamp": now if participant_data.consent_given else None,
        "medical_history": participant_data.medical_history,
        "current_medications": participant_data.current_medications,
        "emergency_contact_name": participant_data.emergency_contact_name,
        "emergency_contact_phone": participant_data.emergency_contact_phone,
        "preferred_language": participant_data.preferred_language,
        "enrollment_date": now,
        "trial_status": TrialStatus.ENROLLED.value,
        "approval_status": ApprovalStatus.PENDING.value,
        "approved_by": None,
        "approval_date": None,
        "rejection_reason": None,
        "voice_samples_collected": 0,
        "target_samples": 9,
        "baseline_established": False,
        "assigned_psychologist": None,
        "assignment_date": None,
        "clinical_notes": None,
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.clinical_trial_participants.insert_one(participant_doc)
    participant_doc["_id"] = result.inserted_id
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(current_user["_id"]),
        "action": "trial_registration",
        "entity_type": "clinical_trial_participant",
        "entity_id": str(result.inserted_id),
        "details": {"consent_given": participant_data.consent_given},
        "timestamp": now
    })
    
    return ParticipantResponse(
        id=str(result.inserted_id),
        user_id=participant_doc["user_id"],
        age=participant_doc["age"],
        gender=participant_doc["gender"],
        phone=participant_doc["phone"],
        institution=participant_doc["institution"],
        consent_given=participant_doc["consent_given"],
        consent_timestamp=participant_doc["consent_timestamp"],
        medical_history=participant_doc["medical_history"],
        current_medications=participant_doc["current_medications"],
        emergency_contact_name=participant_doc["emergency_contact_name"],
        emergency_contact_phone=participant_doc["emergency_contact_phone"],
        preferred_language=participant_doc["preferred_language"],
        enrollment_date=participant_doc["enrollment_date"],
        trial_status=participant_doc["trial_status"],
        approval_status=participant_doc["approval_status"],
        approved_by=participant_doc["approved_by"],
        approval_date=participant_doc["approval_date"],
        rejection_reason=participant_doc["rejection_reason"],
        voice_samples_collected=participant_doc["voice_samples_collected"],
        target_samples=participant_doc["target_samples"],
        baseline_established=participant_doc["baseline_established"],
        assigned_psychologist=participant_doc["assigned_psychologist"],
        assignment_date=participant_doc["assignment_date"],
        clinical_notes=participant_doc["clinical_notes"],
        created_at=participant_doc["created_at"],
        updated_at=participant_doc["updated_at"]
    )


@router.get("/pending", response_model=List[ParticipantResponse])
async def get_pending_approvals(current_user = Depends(get_current_admin)):
    """Get all pending trial registrations (admin only)"""
    cursor = db.clinical_trial_participants.find({
        "approval_status": ApprovalStatus.PENDING.value
    }).sort("created_at", -1)
    
    participants = []
    async for doc in cursor:
        # Get user info
        user = await db.users.find_one({"_id": ObjectId(doc["user_id"])})
        participants.append(ParticipantResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            age=doc["age"],
            gender=doc["gender"],
            phone=doc["phone"],
            institution=doc.get("institution"),
            consent_given=doc["consent_given"],
            consent_timestamp=doc.get("consent_timestamp"),
            medical_history=doc.get("medical_history"),
            current_medications=doc.get("current_medications"),
            emergency_contact_name=doc.get("emergency_contact_name"),
            emergency_contact_phone=doc.get("emergency_contact_phone"),
            preferred_language=doc.get("preferred_language", "english"),
            enrollment_date=doc["enrollment_date"],
            trial_status=doc["trial_status"],
            approval_status=doc["approval_status"],
            approved_by=doc.get("approved_by"),
            approval_date=doc.get("approval_date"),
            rejection_reason=doc.get("rejection_reason"),
            voice_samples_collected=doc.get("voice_samples_collected", 0),
            target_samples=doc.get("target_samples", 9),
            baseline_established=doc.get("baseline_established", False),
            assigned_psychologist=doc.get("assigned_psychologist"),
            assignment_date=doc.get("assignment_date"),
            clinical_notes=doc.get("clinical_notes"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        ))
    
    return participants


@router.get("/all", response_model=List[ParticipantResponse])
async def get_all_participants(
    status: Optional[str] = None,
    current_user = Depends(get_current_admin)
):
    """Get all trial participants (admin only)"""
    query = {}
    if status:
        query["approval_status"] = status
    
    cursor = db.clinical_trial_participants.find(query).sort("created_at", -1)
    
    participants = []
    async for doc in cursor:
        participants.append(ParticipantResponse(
            id=str(doc["_id"]),
            user_id=doc["user_id"],
            age=doc["age"],
            gender=doc["gender"],
            phone=doc["phone"],
            institution=doc.get("institution"),
            consent_given=doc["consent_given"],
            consent_timestamp=doc.get("consent_timestamp"),
            medical_history=doc.get("medical_history"),
            current_medications=doc.get("current_medications"),
            emergency_contact_name=doc.get("emergency_contact_name"),
            emergency_contact_phone=doc.get("emergency_contact_phone"),
            preferred_language=doc.get("preferred_language", "english"),
            enrollment_date=doc["enrollment_date"],
            trial_status=doc["trial_status"],
            approval_status=doc["approval_status"],
            approved_by=doc.get("approved_by"),
            approval_date=doc.get("approval_date"),
            rejection_reason=doc.get("rejection_reason"),
            voice_samples_collected=doc.get("voice_samples_collected", 0),
            target_samples=doc.get("target_samples", 9),
            baseline_established=doc.get("baseline_established", False),
            assigned_psychologist=doc.get("assigned_psychologist"),
            assignment_date=doc.get("assignment_date"),
            clinical_notes=doc.get("clinical_notes"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        ))
    
    return participants


@router.put("/{participant_id}/approve", response_model=ParticipantResponse)
async def approve_participant(
    participant_id: str,
    approval: ParticipantApproval,
    current_user = Depends(get_current_admin)
):
    """Approve or reject a trial participant (admin only)"""
    participant = await db.clinical_trial_participants.find_one({
        "_id": ObjectId(participant_id)
    })
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Participant not found"
        )
    
    now = datetime.utcnow()
    update_data = {
        "approval_status": approval.approval_status.value,
        "approved_by": str(current_user["_id"]),
        "approval_date": now,
        "updated_at": now
    }
    
    if approval.approval_status == ApprovalStatus.APPROVED:
        update_data["trial_status"] = TrialStatus.ACTIVE.value
    elif approval.approval_status == ApprovalStatus.REJECTED:
        update_data["rejection_reason"] = approval.rejection_reason
    
    await db.clinical_trial_participants.update_one(
        {"_id": ObjectId(participant_id)},
        {"$set": update_data}
    )
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(current_user["_id"]),
        "action": f"trial_{approval.approval_status.value}",
        "entity_type": "clinical_trial_participant",
        "entity_id": participant_id,
        "details": {
            "approval_status": approval.approval_status.value,
            "rejection_reason": approval.rejection_reason
        },
        "timestamp": now
    })
    
    # Get updated participant
    updated = await db.clinical_trial_participants.find_one({
        "_id": ObjectId(participant_id)
    })
    
    return ParticipantResponse(
        id=str(updated["_id"]),
        user_id=updated["user_id"],
        age=updated["age"],
        gender=updated["gender"],
        phone=updated["phone"],
        institution=updated.get("institution"),
        consent_given=updated["consent_given"],
        consent_timestamp=updated.get("consent_timestamp"),
        medical_history=updated.get("medical_history"),
        current_medications=updated.get("current_medications"),
        emergency_contact_name=updated.get("emergency_contact_name"),
        emergency_contact_phone=updated.get("emergency_contact_phone"),
        preferred_language=updated.get("preferred_language", "english"),
        enrollment_date=updated["enrollment_date"],
        trial_status=updated["trial_status"],
        approval_status=updated["approval_status"],
        approved_by=updated.get("approved_by"),
        approval_date=updated.get("approval_date"),
        rejection_reason=updated.get("rejection_reason"),
        voice_samples_collected=updated.get("voice_samples_collected", 0),
        target_samples=updated.get("target_samples", 9),
        baseline_established=updated.get("baseline_established", False),
        assigned_psychologist=updated.get("assigned_psychologist"),
        assignment_date=updated.get("assignment_date"),
        clinical_notes=updated.get("clinical_notes"),
        created_at=updated["created_at"],
        updated_at=updated["updated_at"]
    )


@router.get("/my-status", response_model=ParticipantResponse)
async def get_my_trial_status(current_user = Depends(get_current_user)):
    """Get current user's trial registration status"""
    participant = await db.clinical_trial_participants.find_one({
        "user_id": str(current_user["_id"])
    })
    
    if not participant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not registered for clinical trial"
        )
    
    return ParticipantResponse(
        id=str(participant["_id"]),
        user_id=participant["user_id"],
        age=participant["age"],
        gender=participant["gender"],
        phone=participant["phone"],
        institution=participant.get("institution"),
        consent_given=participant["consent_given"],
        consent_timestamp=participant.get("consent_timestamp"),
        medical_history=participant.get("medical_history"),
        current_medications=participant.get("current_medications"),
        emergency_contact_name=participant.get("emergency_contact_name"),
        emergency_contact_phone=participant.get("emergency_contact_phone"),
        preferred_language=participant.get("preferred_language", "english"),
        enrollment_date=participant["enrollment_date"],
        trial_status=participant["trial_status"],
        approval_status=participant["approval_status"],
        approved_by=participant.get("approved_by"),
        approval_date=participant.get("approval_date"),
        rejection_reason=participant.get("rejection_reason"),
        voice_samples_collected=participant.get("voice_samples_collected", 0),
        target_samples=participant.get("target_samples", 9),
        baseline_established=participant.get("baseline_established", False),
        assigned_psychologist=participant.get("assigned_psychologist"),
        assignment_date=participant.get("assignment_date"),
        clinical_notes=participant.get("clinical_notes"),
        created_at=participant["created_at"],
        updated_at=participant["updated_at"]
    )
