from pydantic import BaseModel, Field, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

class UserRole(str, Enum):
    PARENT = "parent"
    CHILD = "child"
    SCHOOL_ADMIN = "school_admin"
    TEACHER = "teacher"
    HOSPITAL_ADMIN = "hospital_admin"
    DOCTOR = "doctor"
    SUPER_ADMIN = "super_admin"

class DeviceType(str, Enum):
    ANDROID = "android"
    IOS = "ios"
    WINDOWS = "windows"
    MACOS = "macos"
    WEB = "web"
    SMART_TV = "smart_tv"

class ContentCategory(str, Enum):
    EDUCATIONAL = "educational"
    ENTERTAINMENT = "entertainment"
    SOCIAL_MEDIA = "social_media"
    GAMING = "gaming"
    NEWS = "news"
    ADULT_CONTENT = "adult_content"
    VIOLENCE = "violence"
    INAPPROPRIATE = "inappropriate"

class Language(str, Enum):
    ENGLISH = "en"
    HINDI = "hi"
    TAMIL = "ta"
    TELUGU = "te"
    BENGALI = "bn"
    MARATHI = "mr"

class UserBase(BaseModel):
    email: EmailStr
    full_name: str
    role: UserRole
    language_preference: Language = Language.ENGLISH
    is_active: bool = True

class UserCreate(UserBase):
    password: str

class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    language_preference: Optional[Language] = None
    is_active: Optional[bool] = None

class User(UserBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    last_login: Optional[datetime] = None

class ChildProfile(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str
    parent_id: str
    child_name: str
    birth_year: int
    biometric_password: str  # Format: child_unique_id#birthyear@secure
    grade_level: Optional[str] = None
    school_id: Optional[str] = None
    allowed_screen_time: int = 480  # minutes per day
    educational_goals: List[str] = []
    blocked_categories: List[ContentCategory] = []
    emergency_contacts: List[str] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Device(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    device_name: str
    device_type: DeviceType
    device_id: str  # Unique device identifier
    owner_id: str  # User who owns the device
    active_child_id: Optional[str] = None  # Currently active child profile
    is_online: bool = False
    last_sync: Optional[datetime] = None
    location: Optional[Dict[str, float]] = None  # lat, lng
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class ContentFilter(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str
    category: ContentCategory
    is_blocked: bool
    reason: str
    confidence_score: float
    language: Language
    created_at: datetime = Field(default_factory=datetime.utcnow)

class FilteringEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    child_id: str
    device_id: str
    url: str
    category: ContentCategory
    action: str  # blocked, allowed, flagged
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = {}

class VPNDetectionEvent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    child_id: str
    device_id: str
    vpn_app_name: str
    detection_method: str
    action_taken: str  # blocked, warned, logged
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class EducationalContent(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str
    description: str
    url: str
    subject: str
    grade_levels: List[str]
    language: Language
    content_type: str  # video, article, interactive, game
    ncert_aligned: bool = False
    cultural_context: str  # indian, regional, universal
    created_at: datetime = Field(default_factory=datetime.utcnow)

class School(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    address: str
    city: str
    state: str
    principal_email: EmailStr
    subscription_plan: str
    active_students: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Hospital(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    address: str
    city: str
    state: str
    admin_email: EmailStr
    license_number: str
    subscription_plan: str
    active_patients: int = 0
    created_at: datetime = Field(default_factory=datetime.utcnow)

class UsageAnalytics(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    child_id: str
    device_id: str
    date: datetime
    screen_time_minutes: int
    educational_time_minutes: int
    blocked_attempts: int
    top_categories: List[str]
    focus_score: float
    created_at: datetime = Field(default_factory=datetime.utcnow)

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    user_id: Optional[str] = None
    role: Optional[UserRole] = None

class APIResponse(BaseModel):
    success: bool
    message: str
    data: Optional[Any] = None
    error: Optional[str] = None

class BiometricAuthRequest(BaseModel):
    biometric_password: str
    device_id: str
    device_type: DeviceType

class BiometricAuthResponse(BaseModel):
    success: bool
    child_profile: Optional[ChildProfile] = None
    access_token: Optional[str] = None
    message: str

class ContentFilterRequest(BaseModel):
    url: str
    content: Optional[str] = None
    child_id: str
    device_id: str

class ContentFilterResponse(BaseModel):
    allowed: bool
    category: ContentCategory
    reason: str
    confidence_score: float
    alternative_content: List[str] = []

class EmergencyOverrideRequest(BaseModel):
    child_id: str
    parent_code: str
    reason: str
    duration_minutes: int

class DeviceSyncRequest(BaseModel):
    device_id: str
    child_id: Optional[str] = None
    status: str
    location: Optional[Dict[str, float]] = None
