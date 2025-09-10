from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
from typing import List, Optional
import bcrypt
from bson import ObjectId

from .database import get_database, init_collections, close_database
from .models import (
    User, UserCreate, UserUpdate, LoginRequest, Token,
    Participant, ParticipantCreate, 
    Appointment, AppointmentCreate, AppointmentUpdate,
    DoctorProfile, Message, MessageCreate,
    VoiceAnalysisReport, UserRole, TrialStatus, AppointmentStatus
)
from .auth import (
    get_password_hash, verify_password, create_access_token,
    get_current_user, get_current_active_user, require_role,
    ACCESS_TOKEN_EXPIRE_MINUTES
)

app = FastAPI(
    title="Vocalysis Patient Portal API",
    description="Mental Health Voice Analysis Patient Portal for Cittaa Health Services",
    version="1.0.0"
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.on_event("startup")
async def startup_event():
    init_collections()

@app.on_event("shutdown")
async def shutdown_event():
    close_database()

@app.get("/healthz")
async def healthz():
    return {"status": "ok"}

@app.post("/api/v1/auth/register", response_model=dict)
async def register(user: UserCreate):
    db = get_database()
    
    if db.users.find_one({"email": user.email}):
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    
    user_doc = {
        "_id": str(ObjectId()),
        "email": user.email,
        "full_name": user.full_name,
        "phone": user.phone,
        "role": user.role,
        "is_active": True,
        "hashed_password": hashed_password,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.users.insert_one(user_doc)
    
    audit_log = {
        "_id": str(ObjectId()),
        "user_id": user_doc["_id"],
        "action": "user_registration",
        "entity_type": "user",
        "entity_id": user_doc["_id"],
        "details": {"email": user.email, "role": user.role},
        "timestamp": datetime.utcnow(),
        "ip_address": "unknown",
        "user_agent": "unknown"
    }
    db.audit_logs.insert_one(audit_log)
    
    return {"message": "User registered successfully", "user_id": user_doc["_id"]}

@app.post("/api/v1/auth/login", response_model=Token)
async def login(login_request: LoginRequest):
    db = get_database()
    
    user = db.users.find_one({"email": login_request.email})
    if not user or not verify_password(login_request.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["email"]}, expires_delta=access_token_expires
    )
    
    audit_log = {
        "_id": str(ObjectId()),
        "user_id": user["_id"],
        "action": "user_login",
        "entity_type": "user",
        "entity_id": user["_id"],
        "details": {"email": user["email"]},
        "timestamp": datetime.utcnow(),
        "ip_address": "unknown",
        "user_agent": "unknown"
    }
    db.audit_logs.insert_one(audit_log)
    
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/api/v1/users/me", response_model=User)
async def read_users_me(current_user: User = Depends(get_current_active_user)):
    return current_user

@app.put("/api/v1/users/me", response_model=User)
async def update_user_me(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    db = get_database()
    
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    update_data["updated_at"] = datetime.utcnow()
    
    db.users.update_one(
        {"_id": current_user.id},
        {"$set": update_data}
    )
    
    updated_user = db.users.find_one({"_id": current_user.id})
    return User(**updated_user)

@app.post("/api/v1/participants/register", response_model=dict)
async def register_participant(
    participant_data: ParticipantCreate,
    current_user: User = Depends(get_current_active_user)
):
    db = get_database()
    
    existing = db.clinical_trial_participants.find_one({"user_id": current_user.id})
    if existing:
        raise HTTPException(
            status_code=400,
            detail="User is already registered as a participant"
        )
    
    participant_doc = {
        "_id": str(ObjectId()),
        "user_id": current_user.id,
        "age": participant_data.age,
        "gender": participant_data.gender,
        "phone": current_user.phone or "",
        "institution": participant_data.institution,
        "consent_given": participant_data.consent_given,
        "consent_timestamp": datetime.utcnow(),
        "medical_history": participant_data.medical_history,
        "current_medications": participant_data.current_medications,
        "emergency_contact_name": participant_data.emergency_contact_name,
        "emergency_contact_phone": participant_data.emergency_contact_phone,
        "preferred_language": participant_data.preferred_language,
        "enrollment_date": datetime.utcnow(),
        "trial_status": TrialStatus.PENDING,
        "approval_status": TrialStatus.PENDING,
        "voice_samples_collected": 0,
        "target_samples": 9,
        "baseline_established": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.clinical_trial_participants.insert_one(participant_doc)
    
    return {"message": "Participant registration submitted for approval", "participant_id": participant_doc["_id"]}

@app.get("/api/v1/participants/pending", response_model=List[Participant])
async def get_pending_participants(
    current_user: User = Depends(require_role("admin"))
):
    db = get_database()
    
    participants = list(db.clinical_trial_participants.find(
        {"approval_status": TrialStatus.PENDING}
    ))
    
    return [Participant(**p) for p in participants]

@app.put("/api/v1/participants/{participant_id}/approve")
async def approve_participant(
    participant_id: str,
    current_user: User = Depends(require_role("admin"))
):
    db = get_database()
    
    result = db.clinical_trial_participants.update_one(
        {"_id": participant_id},
        {
            "$set": {
                "approval_status": TrialStatus.APPROVED,
                "trial_status": TrialStatus.ACTIVE,
                "approved_by": current_user.id,
                "approval_date": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
        }
    )
    
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Participant not found")
    
    return {"message": "Participant approved successfully"}

@app.post("/api/v1/appointments", response_model=dict)
async def create_appointment(
    appointment: AppointmentCreate,
    current_user: User = Depends(get_current_active_user)
):
    db = get_database()
    
    doctor = db.users.find_one({"_id": appointment.doctor_id, "role": UserRole.DOCTOR})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    appointment_doc = {
        "_id": str(ObjectId()),
        "patient_id": current_user.id,
        "doctor_id": appointment.doctor_id,
        "appointment_date": appointment.appointment_date,
        "duration_minutes": appointment.duration_minutes,
        "appointment_type": appointment.appointment_type,
        "status": AppointmentStatus.SCHEDULED,
        "notes": appointment.notes,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.appointments.insert_one(appointment_doc)
    
    return {"message": "Appointment scheduled successfully", "appointment_id": appointment_doc["_id"]}

@app.get("/api/v1/appointments", response_model=List[Appointment])
async def get_appointments(
    current_user: User = Depends(get_current_active_user)
):
    db = get_database()
    
    if current_user.role == UserRole.PATIENT:
        appointments = list(db.appointments.find({"patient_id": current_user.id}))
    elif current_user.role == UserRole.DOCTOR:
        appointments = list(db.appointments.find({"doctor_id": current_user.id}))
    else:
        appointments = list(db.appointments.find({}))
    
    return [Appointment(**a) for a in appointments]

@app.get("/api/v1/doctors", response_model=List[DoctorProfile])
async def get_doctors():
    db = get_database()
    
    doctors = list(db.doctor_profiles.find({}))
    return [DoctorProfile(**d) for d in doctors]

@app.get("/api/v1/doctors/{doctor_id}", response_model=DoctorProfile)
async def get_doctor(doctor_id: str):
    db = get_database()
    
    doctor = db.doctor_profiles.find_one({"_id": doctor_id})
    if not doctor:
        raise HTTPException(status_code=404, detail="Doctor not found")
    
    return DoctorProfile(**doctor)

@app.post("/api/v1/messages", response_model=dict)
async def send_message(
    message: MessageCreate,
    current_user: User = Depends(get_current_active_user)
):
    db = get_database()
    
    message_doc = {
        "_id": str(ObjectId()),
        "sender_id": current_user.id,
        "receiver_id": message.receiver_id,
        "content": message.content,
        "message_type": message.message_type,
        "is_read": False,
        "created_at": datetime.utcnow()
    }
    
    db.messages.insert_one(message_doc)
    
    return {"message": "Message sent successfully", "message_id": message_doc["_id"]}

@app.get("/api/v1/messages", response_model=List[Message])
async def get_messages(
    current_user: User = Depends(get_current_active_user)
):
    db = get_database()
    
    messages = list(db.messages.find({
        "$or": [
            {"sender_id": current_user.id},
            {"receiver_id": current_user.id}
        ]
    }).sort("created_at", -1))
    
    return [Message(**m) for m in messages]

@app.get("/api/v1/voice-analysis/reports", response_model=List[VoiceAnalysisReport])
async def get_voice_reports(
    current_user: User = Depends(get_current_active_user)
):
    db = get_database()
    
    if current_user.role == UserRole.PATIENT:
        reports = list(db.voice_analysis_reports.find({"user_id": current_user.id}))
    elif current_user.role == UserRole.DOCTOR:
        assigned_patients = list(db.clinical_trial_participants.find(
            {"assigned_psychologist": current_user.id}
        ))
        patient_ids = [p["user_id"] for p in assigned_patients]
        reports = list(db.voice_analysis_reports.find({"user_id": {"$in": patient_ids}}))
    else:
        reports = list(db.voice_analysis_reports.find({}))
    
    return [VoiceAnalysisReport(**r) for r in reports]
