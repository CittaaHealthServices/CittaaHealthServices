"""
Pydantic models for Vocalysis API
"""
from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from bson import ObjectId


class PyObjectId(str):
    """Custom type for MongoDB ObjectId"""
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return str(v)
        return str(v)


# Enums
class UserRole(str, Enum):
    ADMIN = "admin"
    PSYCHOLOGIST = "psychologist"
    PATIENT = "patient"
    RESEARCHER = "researcher"
    CORPORATE_ADMIN = "corporate_admin"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class TrialStatus(str, Enum):
    ENROLLED = "enrolled"
    ACTIVE = "active"
    COMPLETED = "completed"
    WITHDRAWN = "withdrawn"


class CouponType(str, Enum):
    PERCENTAGE = "percentage"
    FIXED_AMOUNT = "fixed_amount"
    FREE_TRIAL = "free_trial"


class CouponStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    DISABLED = "disabled"


class SubscriptionStatus(str, Enum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    TRIAL = "trial"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    SUCCESS = "success"
    FAILED = "failed"
    REFUNDED = "refunded"


class RiskLevel(str, Enum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


# User Models
class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole = UserRole.PATIENT
    phone: Optional[str] = None
    preferred_language: str = "english"


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_active: bool = True

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# Clinical Trial Participant Models
class ParticipantBase(BaseModel):
    age: int
    gender: str
    phone: str
    institution: Optional[str] = None
    consent_given: bool = False
    medical_history: Optional[str] = None
    current_medications: Optional[str] = None
    emergency_contact_name: Optional[str] = None
    emergency_contact_phone: Optional[str] = None
    preferred_language: str = "english"


class ParticipantCreate(ParticipantBase):
    pass


class ParticipantResponse(ParticipantBase):
    id: str
    user_id: str
    consent_timestamp: Optional[datetime] = None
    enrollment_date: datetime
    trial_status: TrialStatus = TrialStatus.ENROLLED
    approval_status: ApprovalStatus = ApprovalStatus.PENDING
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
        from_attributes = True


class ParticipantApproval(BaseModel):
    approval_status: ApprovalStatus
    rejection_reason: Optional[str] = None


# Psychologist Assignment Models
class PsychologistAssignmentCreate(BaseModel):
    psychologist_id: str
    patient_id: str
    notes: Optional[str] = None


class PsychologistAssignmentResponse(BaseModel):
    id: str
    psychologist_id: str
    patient_id: str
    assigned_by: str
    assignment_date: datetime
    status: str = "active"
    notes: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PsychologistWithPatients(BaseModel):
    id: str
    email: str
    full_name: str
    patient_count: int
    patients: List[Dict[str, Any]]


# Voice Analysis Report Models
class VoiceAnalysisCreate(BaseModel):
    audio_duration: float
    language: str = "english"


class VoiceAnalysisResponse(BaseModel):
    id: str
    user_id: str
    participant_id: Optional[str] = None
    mental_health_score: float
    confidence_score: float
    phq9_score: int
    gad7_score: int
    pss_score: int
    wemwbs_score: int
    risk_level: RiskLevel
    recommendations: List[str]
    voice_features: Dict[str, Any]
    probabilities: Dict[str, float]
    processing_time: float
    sample_count: int
    personalization_score: Optional[float] = None
    predicted_condition: str
    model_confidence: float
    personalization_applied: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Coupon Models
class CouponBase(BaseModel):
    code: str
    coupon_type: CouponType
    discount_value: float  # percentage (0-100), fixed amount, or trial days
    description: Optional[str] = None
    max_uses: Optional[int] = None
    valid_from: datetime
    valid_until: datetime
    applicable_plans: List[str] = []  # empty = all plans


class CouponCreate(CouponBase):
    pass


class CouponResponse(CouponBase):
    id: str
    status: CouponStatus = CouponStatus.ACTIVE
    total_uses: int = 0
    created_by: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CouponValidation(BaseModel):
    code: str
    plan_id: Optional[str] = None


class CouponValidationResponse(BaseModel):
    valid: bool
    coupon: Optional[CouponResponse] = None
    discount_amount: Optional[float] = None
    message: str


# Payment Models
class PaymentCreate(BaseModel):
    amount: float
    currency: str = "INR"
    plan_id: str
    coupon_code: Optional[str] = None


class PaymentResponse(BaseModel):
    id: str
    user_id: str
    order_id: str
    amount: float
    currency: str
    status: PaymentStatus
    plan_id: str
    coupon_code: Optional[str] = None
    discount_amount: float = 0
    payment_method: Optional[str] = None
    transaction_id: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CashfreeOrderResponse(BaseModel):
    order_id: str
    payment_session_id: str
    order_amount: float
    order_currency: str


# Subscription Models
class SubscriptionCreate(BaseModel):
    plan_id: str
    payment_id: Optional[str] = None


class SubscriptionResponse(BaseModel):
    id: str
    user_id: str
    plan_id: str
    status: SubscriptionStatus
    start_date: datetime
    end_date: datetime
    payment_id: Optional[str] = None
    auto_renew: bool = False
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Admin Metrics Models
class DashboardMetrics(BaseModel):
    total_users: int
    total_analyses: int
    active_subscriptions: int
    ai_accuracy: float
    users_by_platform: Dict[str, int]
    risk_distribution: Dict[str, int]
    recent_analyses: List[Dict[str, Any]]
    revenue_this_month: float


class AnalyticsTrend(BaseModel):
    date: str
    analyses: int
    users: int


# Audit Log Models
class AuditLogCreate(BaseModel):
    action: str
    entity_type: str
    entity_id: str
    details: Optional[Dict[str, Any]] = None


class AuditLogResponse(BaseModel):
    id: str
    user_id: str
    action: str
    entity_type: str
    entity_id: str
    details: Optional[Dict[str, Any]] = None
    timestamp: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None

    class Config:
        from_attributes = True
