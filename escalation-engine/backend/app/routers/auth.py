"""
Authentication Router for CITTAA Escalation Engine
JWT-based authentication with role-based access control
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional
import logging

from app.models.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse, UserUpdate
from app.utils.security import (
    hash_password, verify_password, create_access_token, 
    create_refresh_token, verify_token, get_current_user
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user
    
    Roles:
    - admin: Full system access
    - psychologist: Can submit reports, view assigned students
    - school_admin: Can view institution reports and analytics
    """
    # Check if email already exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Validate role
    valid_roles = ["admin", "psychologist", "school_admin"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    # Psychologists must have RCI registration
    if user_data.role == "psychologist" and not user_data.rci_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RCI registration number is required for psychologists"
        )
    
    # Create new user
    new_user = User(
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        institution_id=user_data.institution_id,
        rci_registration=user_data.rci_registration,
        phone=user_data.phone
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info(f"New user registered: {new_user.email} with role {new_user.role}")
    
    return new_user


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    Login and get access token
    
    Returns JWT access token and refresh token
    """
    # Find user by email
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    # Update last login
    user.last_login = datetime.utcnow()
    db.commit()
    
    # Create tokens
    access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.user_id)}
    )
    
    logger.info(f"User logged in: {user.email}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/login/json", response_model=TokenResponse)
async def login_json(login_data: UserLogin, db: Session = Depends(get_db)):
    """
    Login with JSON body (alternative to form-based login)
    """
    user = db.query(User).filter(User.email == login_data.email).first()
    
    if not user or not verify_password(login_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    user.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email, "role": user.role}
    )
    refresh_token = create_refresh_token(
        data={"sub": str(user.user_id)}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_token: str, db: Session = Depends(get_db)):
    """
    Refresh access token using refresh token
    """
    payload = verify_token(refresh_token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token"
        )
    
    user_id = payload.get("sub")
    user = db.query(User).filter(User.user_id == user_id).first()
    
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive"
        )
    
    new_access_token = create_access_token(
        data={"sub": str(user.user_id), "email": user.email, "role": user.role}
    )
    new_refresh_token = create_refresh_token(
        data={"sub": str(user.user_id)}
    )
    
    return TokenResponse(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        user=UserResponse.model_validate(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get current authenticated user information
    """
    return current_user


@router.put("/me", response_model=UserResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update current user's profile
    """
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    if user_update.phone:
        current_user.phone = user_update.phone
    if user_update.rci_registration and current_user.role == "psychologist":
        current_user.rci_registration = user_update.rci_registration
    
    current_user.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(current_user)
    
    return current_user


@router.post("/logout")
async def logout(current_user: User = Depends(get_current_user)):
    """
    Logout current user
    
    Note: JWT tokens are stateless, so this endpoint is mainly for audit logging.
    Client should discard the token.
    """
    logger.info(f"User logged out: {current_user.email}")
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(
    current_password: str,
    new_password: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Change user password
    """
    if not verify_password(current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters"
        )
    
    current_user.password_hash = hash_password(new_password)
    current_user.updated_at = datetime.utcnow()
    db.commit()
    
    logger.info(f"Password changed for user: {current_user.email}")
    
    return {"message": "Password changed successfully"}
