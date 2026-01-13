"""
Authentication router for Vocalysis API - MongoDB Version
Implements secure authentication with healthcare-grade security measures
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
import jwt
import bcrypt
from typing import Optional, Dict, Any
import uuid
import logging

from app.models.mongodb import get_mongodb
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate, ConsentUpdate
from app.utils.config import settings
from app.services.email_service import email_service
from app.middleware.security import (
    validate_password_strength,
    validate_email,
    validate_phone,
    sanitize_input,
    hash_sensitive_data
)

logger = logging.getLogger(__name__)

router = APIRouter()
security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))


def create_token(user_id: str, role: str) -> str:
    """Create JWT token"""
    payload = {
        "user_id": user_id,
        "role": role,
        "exp": datetime.utcnow() + timedelta(hours=settings.JWT_EXPIRATION_HOURS)
    }
    return jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)


def mongo_user_to_response(user_doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB user document to response format"""
    return {
        "id": str(user_doc.get("_id", "")),
        "email": user_doc.get("email", ""),
        "full_name": user_doc.get("full_name", ""),
        "phone": user_doc.get("phone"),
        "age_range": user_doc.get("age_range"),
        "gender": user_doc.get("gender"),
        "language_preference": user_doc.get("language_preference", "en"),
        "role": user_doc.get("role", "patient"),
        "is_active": user_doc.get("is_active", True),
        "is_verified": user_doc.get("is_verified", False),
        "consent_given": user_doc.get("consent_given", False),
        "consent_timestamp": user_doc.get("consent_timestamp"),
        "is_clinical_trial_participant": user_doc.get("is_clinical_trial_participant", False),
        "assigned_psychologist_id": user_doc.get("assigned_psychologist_id"),
        "organization_id": user_doc.get("organization_id"),
        "employee_id": user_doc.get("employee_id"),
        "created_at": user_doc.get("created_at"),
        "updated_at": user_doc.get("updated_at"),
        "last_login": user_doc.get("last_login"),
    }


def get_current_user_from_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Get current user from JWT token using MongoDB"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        db = get_mongodb()
        user = db.users.find_one({"_id": user_id})
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")


def require_role(allowed_roles: list):
    """Dependency to require specific roles"""
    def role_checker(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
        if current_user.get("role") not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user in MongoDB with security validations"""
    db = get_mongodb()
    
    # Validate email format
    if not validate_email(user_data.email):
        raise HTTPException(
            status_code=400,
            detail="Invalid email format"
        )
    
    # Validate password strength
    is_valid, error_msg = validate_password_strength(user_data.password)
    if not is_valid:
        raise HTTPException(
            status_code=400,
            detail=error_msg
        )
    
    # Validate phone number if provided
    if user_data.phone and not validate_phone(user_data.phone):
        raise HTTPException(
            status_code=400,
            detail="Invalid phone number format. Use Indian format: +91XXXXXXXXXX"
        )
    
    # Sanitize inputs to prevent injection attacks
    try:
        sanitized_email = sanitize_input(user_data.email)
        sanitized_name = sanitize_input(user_data.full_name) if user_data.full_name else ""
    except ValueError as e:
        logger.warning(f"Potential injection attempt detected: {hash_sensitive_data(user_data.email)}")
        raise HTTPException(
            status_code=400,
            detail="Invalid input detected"
        )
    
    # Check if email already exists
    existing_user = db.users.find_one({"email": sanitized_email})
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user document
    user_id = str(uuid.uuid4())
    user_doc = {
        "_id": user_id,
        "email": sanitized_email,
        "password_hash": hash_password(user_data.password),
        "full_name": sanitized_name,
        "phone": user_data.phone,
        "age_range": user_data.age_range,
        "gender": user_data.gender,
        "language_preference": user_data.language_preference or "en",
        "role": user_data.role or "patient",
        "organization_id": user_data.organization_id,
        "employee_id": user_data.employee_id,
        "is_active": True,
        "is_verified": False,
        "consent_given": False,
        "is_clinical_trial_participant": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.users.insert_one(user_doc)
    logger.info(f"New user registered: {hash_sensitive_data(sanitized_email)}")
    
    # Send welcome email
    try:
        email_service.send_welcome_email(user_data.email, user_data.full_name)
    except Exception as e:
        # Log but don't fail registration if email fails
        logger.warning(f"Failed to send welcome email: {e}")
    
    # Create token
    token = create_token(user_id, user_doc["role"])
    
    return Token(
        access_token=token,
        user=UserResponse.model_validate(mongo_user_to_response(user_doc))
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user using MongoDB with security logging"""
    db = get_mongodb()
    
    # Sanitize email input
    try:
        sanitized_email = sanitize_input(credentials.email)
    except ValueError:
        logger.warning(f"Potential injection attempt in login: {hash_sensitive_data(credentials.email)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    user = db.users.find_one({"email": sanitized_email})
    
    if not user or not verify_password(credentials.password, user.get("password_hash", "")):
        # Log failed login attempt (for security monitoring)
        logger.warning(f"Failed login attempt for: {hash_sensitive_data(sanitized_email)}")
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    if not user.get("is_active", True):
        logger.warning(f"Login attempt for deactivated account: {hash_sensitive_data(sanitized_email)}")
        raise HTTPException(
            status_code=403,
            detail="Account is deactivated"
        )
    
    # Update last login
    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    user["last_login"] = datetime.utcnow()
    
    # Log successful login
    logger.info(f"Successful login for user: {hash_sensitive_data(sanitized_email)}")
    
    # Create token - convert ObjectId to string if needed
    user_id = str(user["_id"]) if user.get("_id") else ""
    token = create_token(user_id, user.get("role", "patient"))
    
    return Token(
        access_token=token,
        user=UserResponse.model_validate(mongo_user_to_response(user))
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Get current user profile"""
    return UserResponse.model_validate(mongo_user_to_response(current_user))


@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """Update current user profile in MongoDB"""
    db = get_mongodb()
    
    update_fields = {}
    if update_data.full_name is not None:
        update_fields["full_name"] = update_data.full_name
    if update_data.phone is not None:
        update_fields["phone"] = update_data.phone
    if update_data.age_range is not None:
        update_fields["age_range"] = update_data.age_range
    if update_data.gender is not None:
        update_fields["gender"] = update_data.gender
    if update_data.language_preference is not None:
        update_fields["language_preference"] = update_data.language_preference
    
    if update_fields:
        update_fields["updated_at"] = datetime.utcnow()
        db.users.update_one(
            {"_id": current_user["_id"]},
            {"$set": update_fields}
        )
    
    # Get updated user
    updated_user = db.users.find_one({"_id": current_user["_id"]})
    return UserResponse.model_validate(mongo_user_to_response(updated_user))


@router.post("/consent", response_model=UserResponse)
async def update_consent(
    consent_data: ConsentUpdate,
    current_user: Dict[str, Any] = Depends(get_current_user_from_token)
):
    """Update user consent status in MongoDB"""
    db = get_mongodb()
    
    update_fields = {
        "consent_given": consent_data.consent_given,
        "updated_at": datetime.utcnow()
    }
    if consent_data.consent_given:
        update_fields["consent_timestamp"] = datetime.utcnow()
    
    db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": update_fields}
    )
    
    # Get updated user
    updated_user = db.users.find_one({"_id": current_user["_id"]})
    return UserResponse.model_validate(mongo_user_to_response(updated_user))


@router.post("/logout")
async def logout(current_user: Dict[str, Any] = Depends(get_current_user_from_token)):
    """Logout user (client should discard token)"""
    return {"message": "Logged out successfully"}


# Keep the old get_current_user for backward compatibility with other routers
def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> Dict[str, Any]:
    """Alias for get_current_user_from_token for backward compatibility"""
    return get_current_user_from_token(credentials)
