"""
Authentication Router for Vocalysis API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from bson import ObjectId

from app.config import settings
from app.database import db
from app.models import (
    UserCreate, UserLogin, UserResponse, Token, UserRole
)

router = APIRouter(prefix="/api/v1/auth", tags=["Authentication"])

# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT Bearer
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password"""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT access token"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt_access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
    return encoded_jwt


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get the current authenticated user from JWT token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = credentials.credentials
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = await db.users.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    
    return user


async def get_current_admin(current_user = Depends(get_current_user)):
    """Require admin role"""
    if current_user.get("role") != UserRole.ADMIN.value:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_current_psychologist(current_user = Depends(get_current_user)):
    """Require psychologist role"""
    if current_user.get("role") not in [UserRole.PSYCHOLOGIST.value, UserRole.ADMIN.value]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Psychologist access required"
        )
    return current_user


@router.post("/register", response_model=Token)
async def register(user_data: UserCreate):
    """Register a new user"""
    # Check if user already exists
    existing_user = await db.users.find_one({"email": user_data.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create user document
    user_doc = {
        "email": user_data.email,
        "full_name": user_data.full_name,
        "role": user_data.role.value,
        "phone": user_data.phone,
        "preferred_language": user_data.preferred_language,
        "hashed_password": get_password_hash(user_data.password),
        "is_active": True,
        "created_at": datetime.utcnow(),
        "updated_at": datetime.utcnow()
    }
    
    result = await db.users.insert_one(user_doc)
    user_doc["_id"] = result.inserted_id
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(result.inserted_id), "role": user_data.role.value}
    )
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(result.inserted_id),
        "action": "user_registered",
        "entity_type": "user",
        "entity_id": str(result.inserted_id),
        "details": {"email": user_data.email, "role": user_data.role.value},
        "timestamp": datetime.utcnow()
    })
    
    return Token(
        access_token=access_token,
        user=UserResponse(
            id=str(result.inserted_id),
            email=user_doc["email"],
            full_name=user_doc["full_name"],
            role=user_doc["role"],
            phone=user_doc["phone"],
            preferred_language=user_doc["preferred_language"],
            created_at=user_doc["created_at"],
            is_active=user_doc["is_active"]
        )
    )


@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login and get access token"""
    user = await db.users.find_one({"email": credentials.email})
    
    if not user or not verify_password(credentials.password, user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not user.get("is_active", True):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is disabled"
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": str(user["_id"]), "role": user["role"]}
    )
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(user["_id"]),
        "action": "user_login",
        "entity_type": "user",
        "entity_id": str(user["_id"]),
        "details": {"email": credentials.email},
        "timestamp": datetime.utcnow()
    })
    
    return Token(
        access_token=access_token,
        user=UserResponse(
            id=str(user["_id"]),
            email=user["email"],
            full_name=user["full_name"],
            role=user["role"],
            phone=user.get("phone"),
            preferred_language=user.get("preferred_language", "english"),
            created_at=user["created_at"],
            is_active=user.get("is_active", True)
        )
    )


@router.get("/me", response_model=UserResponse)
async def get_me(current_user = Depends(get_current_user)):
    """Get current user profile"""
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        full_name=current_user["full_name"],
        role=current_user["role"],
        phone=current_user.get("phone"),
        preferred_language=current_user.get("preferred_language", "english"),
        created_at=current_user["created_at"],
        is_active=current_user.get("is_active", True)
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(current_user = Depends(get_current_user)):
    """Refresh access token"""
    access_token = create_access_token(
        data={"sub": str(current_user["_id"]), "role": current_user["role"]}
    )
    
    return Token(
        access_token=access_token,
        user=UserResponse(
            id=str(current_user["_id"]),
            email=current_user["email"],
            full_name=current_user["full_name"],
            role=current_user["role"],
            phone=current_user.get("phone"),
            preferred_language=current_user.get("preferred_language", "english"),
            created_at=current_user["created_at"],
            is_active=current_user.get("is_active", True)
        )
    )
