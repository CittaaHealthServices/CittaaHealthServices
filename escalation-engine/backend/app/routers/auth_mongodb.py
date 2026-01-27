"""
MongoDB-based Authentication Router for CITTAA Escalation Engine
JWT-based authentication with role-based access control using MongoDB
"""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from typing import Optional
from pydantic import BaseModel, EmailStr
import logging
import bcrypt
import jwt
import os
import uuid

from app.models.mongodb import get_mongodb

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "cittaa-escalation-engine-secret-key-2024")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24
REFRESH_TOKEN_EXPIRE_DAYS = 7


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    role: str = "psychologist"
    phone: Optional[str] = None
    rci_registration: Optional[str] = None
    institution_id: Optional[str] = None


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str
    role: str
    phone: Optional[str] = None
    rci_registration: Optional[str] = None
    institution_id: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))


def create_access_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire, "type": "access"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "type": "refresh"})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = verify_token(token)
    if payload is None:
        raise credentials_exception
    
    user_id = payload.get("sub")
    if user_id is None:
        raise credentials_exception
    
    db = get_mongodb()
    user = db.users.find_one({"_id": user_id})
    
    if user is None:
        raise credentials_exception
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordReset(BaseModel):
    token: str
    new_password: str


class PasswordChange(BaseModel):
    current_password: str
    new_password: str


def validate_cittaa_email(email: str) -> bool:
    """Validate that email is from @cittaa.in domain"""
    return email.lower().endswith("@cittaa.in")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(user_data: UserCreate, current_user: dict = Depends(get_current_user)):
    """Register a new user - Admin only, @cittaa.in emails only"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can create new accounts"
        )
    
    if not validate_cittaa_email(user_data.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only @cittaa.in email addresses are allowed"
        )
    
    db = get_mongodb()
    
    existing_user = db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    valid_roles = ["admin", "psychologist", "school_admin", "manager", "quality_manager"]
    if user_data.role not in valid_roles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(valid_roles)}"
        )
    
    if user_data.role == "psychologist" and not user_data.rci_registration:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="RCI registration number is required for psychologists"
        )
    
    user_doc = {
        "_id": str(uuid.uuid4()),
        "email": user_data.email,
        "password_hash": hash_password(user_data.password),
        "full_name": user_data.full_name,
        "role": user_data.role,
        "phone": user_data.phone,
        "rci_registration": user_data.rci_registration,
        "institution_id": user_data.institution_id,
        "is_active": True,
        "is_verified": False,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    db.users.insert_one(user_doc)
    
    logger.info(f"New user registered by admin {current_user['email']}: {user_data.email} with role {user_data.role}")
    
    return UserResponse(
        id=user_doc["_id"],
        email=user_doc["email"],
        full_name=user_doc["full_name"],
        role=user_doc["role"],
        phone=user_doc.get("phone"),
        rci_registration=user_doc.get("rci_registration"),
        institution_id=user_doc.get("institution_id"),
        is_active=user_doc["is_active"],
        created_at=user_doc["created_at"]
    )


@router.post("/login", response_model=TokenResponse)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login and get access token"""
    db = get_mongodb()
    
    user = db.users.find_one({"email": form_data.username})
    
    if not user or not verify_password(form_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    access_token = create_access_token(
        data={"sub": user["_id"], "email": user["email"], "role": user["role"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": user["_id"]}
    )
    
    logger.info(f"User logged in: {user['email']}")
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user["_id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            phone=user.get("phone"),
            rci_registration=user.get("rci_registration"),
            institution_id=user.get("institution_id"),
            is_active=user.get("is_active", True),
            created_at=user.get("created_at")
        )
    )


@router.post("/login/json", response_model=TokenResponse)
async def login_json(login_data: UserLogin):
    """Login with JSON body"""
    db = get_mongodb()
    
    user = db.users.find_one({"email": login_data.email})
    
    if not user or not verify_password(login_data.password, user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {"last_login": datetime.utcnow()}}
    )
    
    access_token = create_access_token(
        data={"sub": user["_id"], "email": user["email"], "role": user["role"]}
    )
    refresh_token = create_refresh_token(
        data={"sub": user["_id"]}
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponse(
            id=user["_id"],
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            phone=user.get("phone"),
            rci_registration=user.get("rci_registration"),
            institution_id=user.get("institution_id"),
            is_active=user.get("is_active", True),
            created_at=user.get("created_at")
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user information"""
    return UserResponse(
        id=current_user["_id"],
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        phone=current_user.get("phone"),
        rci_registration=current_user.get("rci_registration"),
        institution_id=current_user.get("institution_id"),
        is_active=current_user.get("is_active", True),
        created_at=current_user.get("created_at")
    )


@router.post("/logout")
async def logout(current_user: dict = Depends(get_current_user)):
    """Logout current user"""
    logger.info(f"User logged out: {current_user['email']}")
    return {"message": "Successfully logged out"}


@router.post("/change-password")
async def change_password(password_data: PasswordChange, current_user: dict = Depends(get_current_user)):
    """Change password for current user (psychologists and other users can reset their own password)"""
    db = get_mongodb()
    
    if not verify_password(password_data.current_password, current_user["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )
    
    if len(password_data.new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    new_hash = hash_password(password_data.new_password)
    
    db.users.update_one(
        {"_id": current_user["_id"]},
        {"$set": {
            "password_hash": new_hash,
            "updated_at": datetime.utcnow()
        }}
    )
    
    logger.info(f"Password changed for user: {current_user['email']}")
    
    return {"message": "Password changed successfully"}


@router.post("/admin/reset-user-password")
async def admin_reset_user_password(
    email: EmailStr,
    new_password: str,
    current_user: dict = Depends(get_current_user)
):
    """Admin can reset any user's password"""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can reset user passwords"
        )
    
    db = get_mongodb()
    
    user = db.users.find_one({"email": email})
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if len(new_password) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password must be at least 8 characters long"
        )
    
    new_hash = hash_password(new_password)
    
    db.users.update_one(
        {"_id": user["_id"]},
        {"$set": {
            "password_hash": new_hash,
            "updated_at": datetime.utcnow()
        }}
    )
    
    logger.info(f"Password reset by admin {current_user['email']} for user: {email}")
    
    return {"message": f"Password reset successfully for {email}"}
