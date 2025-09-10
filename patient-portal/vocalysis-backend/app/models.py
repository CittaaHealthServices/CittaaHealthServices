from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum

class UserRole(str, Enum):
    PATIENT = "patient"
    DOCTOR = "doctor"
    ADMIN = "admin"
    RESEARCHER = "researcher"

class TrialStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    ACTIVE = "active"
    COMPLETED = "completed"

class AppointmentStatus(str, Enum):
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    phone: Optional[str] = None
    role: UserRole
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    phone: Optional[str] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: str = Field(alias="_id")
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class ParticipantCreate(BaseModel):
    age: int
    gender: str
    institution: str
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    emergency_contact_name: str
    emergency_contact_phone: str
    preferred_language: str = "English"
    consent_given: bool = True

class Participant(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    age: int
    gender: str
    phone: str
    institution: str
    consent_given: bool
    consent_timestamp: datetime
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    emergency_contact_name: str
    emergency_contact_phone: str
    preferred_language: str
    enrollment_date: datetime
    trial_status: TrialStatus
    approval_status: TrialStatus
    approved_by: Optional[str] = None
    approval_date: Optional[datetime] = None
    rejection_reason: Optional[str] = None
    voice_samples_collected: int = 0
    target_samples: int = 9
    baseline_established: bool = False
    assigned_psychologist: Optional[str] = None
    assignment_date: Optional[datetime] = None
    clinical_notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class VoiceAnalysisReport(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    participant_id: Optional[str] = None
    mental_health_score: float
    confidence_score: float
    phq9_score: float
    gad7_score: float
    pss_score: float
    wemwbs_score: float
    risk_level: RiskLevel
    recommendations: List[str]
    voice_features: Dict[str, Any]
    probabilities: Dict[str, float]
    processing_time: float
    sample_count: int
    personalization_score: float
    predicted_condition: str
    model_confidence: float
    personalization_applied: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class AppointmentCreate(BaseModel):
    doctor_id: str
    appointment_date: datetime
    duration_minutes: int = 60
    appointment_type: str = "consultation"
    notes: Optional[str] = None

class AppointmentUpdate(BaseModel):
    appointment_date: Optional[datetime] = None
    status: Optional[AppointmentStatus] = None
    notes: Optional[str] = None

class Appointment(BaseModel):
    id: str = Field(alias="_id")
    patient_id: str
    doctor_id: str
    appointment_date: datetime
    duration_minutes: int
    appointment_type: str
    status: AppointmentStatus
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class DoctorProfile(BaseModel):
    id: str = Field(alias="_id")
    user_id: str
    specialization: str
    experience_years: int
    qualifications: List[str]
    languages: List[str]
    consultation_fee: float
    available_slots: List[str]
    rating: float = 0.0
    total_reviews: int = 0
    bio: Optional[str] = None
    profile_image: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        populate_by_name = True

class MessageCreate(BaseModel):
    receiver_id: str
    content: str
    message_type: str = "text"

class Message(BaseModel):
    id: str = Field(alias="_id")
    sender_id: str
    receiver_id: str
    content: str
    message_type: str
    is_read: bool = False
    created_at: datetime

    class Config:
        populate_by_name = True

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class LoginRequest(BaseModel):
    email: EmailStr
    password: str
