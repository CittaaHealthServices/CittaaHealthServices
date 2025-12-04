"""
Authentication router for Vocalysis API
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import bcrypt
import secrets
from typing import Optional
from pydantic import BaseModel

from app.models.database import get_db, sync_user_to_mongodb
from app.models.user import User, UserRole
from app.schemas.user import UserCreate, UserLogin, UserResponse, Token, UserUpdate, ConsentUpdate, ClinicalTrialRegistration
from app.utils.config import settings
from app.services.email_service import email_service


class PasswordResetRequest(BaseModel):
    """Request model for password reset"""
    token: str
    new_password: str

router = APIRouter()
security = HTTPBearer()

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Alias for backward compatibility
get_password_hash = hash_password

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

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current user from JWT token"""
    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )
        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        
        return user
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

def require_role(allowed_roles: list):
    """Dependency to require specific roles"""
    def role_checker(current_user: User = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=403,
                detail=f"Access denied. Required roles: {allowed_roles}"
            )
        return current_user
    return role_checker

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """Register a new user"""
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        age_range=user_data.age_range,
        gender=user_data.gender,
        language_preference=user_data.language_preference,
        role=user_data.role,
        organization_id=user_data.organization_id,
        employee_id=user_data.employee_id
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Send welcome email
    try:
        email_service.send_welcome_email(user.email, user.full_name)
    except Exception as e:
        # Log but don't fail registration if email fails
        print(f"Failed to send welcome email: {e}")
    
    # Create token
    token = create_token(user.id, user.role)
    
    return Token(
        access_token=token,
        user=UserResponse.model_validate(user)
    )

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login user"""
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=403,
            detail="Account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create token
    token = create_token(user.id, user.role)
    
    return Token(
        access_token=token,
        user=UserResponse.model_validate(user)
    )

@router.get("/me", response_model=UserResponse)
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse.model_validate(current_user)

@router.put("/me", response_model=UserResponse)
async def update_profile(
    update_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update current user profile"""
    if update_data.full_name is not None:
        current_user.full_name = update_data.full_name
    if update_data.phone is not None:
        current_user.phone = update_data.phone
    if update_data.age_range is not None:
        current_user.age_range = update_data.age_range
    if update_data.gender is not None:
        current_user.gender = update_data.gender
    if update_data.language_preference is not None:
        current_user.language_preference = update_data.language_preference
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)

@router.post("/consent", response_model=UserResponse)
async def update_consent(
    consent_data: ConsentUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update user consent status"""
    current_user.consent_given = consent_data.consent_given
    if consent_data.consent_given:
        current_user.consent_timestamp = datetime.utcnow()
    
    db.commit()
    db.refresh(current_user)
    
    return UserResponse.model_validate(current_user)

@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """Logout user (client should discard token)"""
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
async def forgot_password(email: str, db: Session = Depends(get_db)):
    """
    Request password reset - sends email with reset link
    Always returns success to prevent email enumeration
    """
    user = db.query(User).filter(User.email == email).first()
    
    if user:
        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)
        
        # Set token and expiry (1 hour)
        user.reset_token = reset_token
        user.reset_token_expires_at = datetime.utcnow() + timedelta(hours=1)
        db.commit()
        
        # Send password reset email
        try:
            email_service.send_password_reset_email(
                to_email=user.email,
                reset_token=reset_token,
                full_name=user.full_name
            )
        except Exception as e:
            print(f"Failed to send password reset email: {e}")
    
    # Always return success to prevent email enumeration
    return {"message": "If an account exists with this email, a password reset link has been sent."}


@router.post("/reset-password")
async def reset_password(request: PasswordResetRequest, db: Session = Depends(get_db)):
    """
    Reset password using token from email
    """
    # Find user with valid token
    user = db.query(User).filter(
        User.reset_token == request.token,
        User.reset_token_expires_at > datetime.utcnow()
    ).first()
    
    if not user:
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired reset token"
        )
    
    # Validate new password
    if len(request.new_password) < 8:
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long"
        )
    
    # Update password and clear reset token
    user.password_hash = hash_password(request.new_password)
    user.reset_token = None
    user.reset_token_expires_at = None
    db.commit()
    
    return {"message": "Password has been reset successfully. You can now log in with your new password."}


@router.post("/register-clinical-trial", response_model=Token)
async def register_clinical_trial(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user for clinical trial participation.
    Sets is_clinical_trial_participant=True and trial_status='pending'.
    User must be approved by admin before they can access the platform.
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    # Create new user with clinical trial flags
    user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        phone=user_data.phone,
        age_range=user_data.age_range,
        gender=user_data.gender,
        language_preference=user_data.language_preference,
        role="patient",  # Clinical trial participants are always patients
        organization_id=user_data.organization_id,
        employee_id=user_data.employee_id,
        # Clinical trial specific fields
        is_clinical_trial_participant=True,
        trial_status="pending",
        is_active=False  # User is inactive until approved by admin
    )
    
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Sync to MongoDB for persistence
    try:
        sync_user_to_mongodb(user)
    except Exception as e:
        print(f"Failed to sync user to MongoDB: {e}")
    
    # Send clinical trial registration email
    try:
        email_service.send_clinical_trial_registration_email(user.email, user.full_name)
    except Exception as e:
        # Log but don't fail registration if email fails
        print(f"Failed to send clinical trial registration email: {e}")
    
    # Create token (user can view their status but not access features until approved)
    token = create_token(user.id, user.role)
    
    return Token(
        access_token=token,
        user=UserResponse.model_validate(user)
    )
