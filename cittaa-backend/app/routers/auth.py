from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from typing import List

from ..database import get_database
from ..models import (
    User, UserCreate, UserUpdate, Token, APIResponse,
    BiometricAuthRequest, BiometricAuthResponse, ChildProfile,
    EmergencyOverrideRequest, UserRole
)
from ..auth import (
    verify_password, get_password_hash, create_access_token,
    get_current_active_user, require_role, validate_biometric_password,
    generate_biometric_password
)
from ..config import settings

router = APIRouter()

@router.post("/register", response_model=APIResponse)
async def register_user(user: UserCreate):
    """Register a new user (parent, school admin, hospital admin)"""
    db = get_database()
    
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    user_dict = user.dict()
    user_dict["password"] = hashed_password
    
    new_user = User(**user_dict)
    await db.users.insert_one(new_user.dict())
    
    return APIResponse(
        success=True,
        message="User registered successfully",
        data={"user_id": new_user.id, "email": new_user.email}
    )

@router.post("/login", response_model=Token)
async def login_user(form_data: OAuth2PasswordRequestForm = Depends()):
    """Login with email and password"""
    db = get_database()
    
    user = await db.users.find_one({"email": form_data.username})
    if not user or not verify_password(form_data.password, user["password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user["is_active"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    await db.users.update_one(
        {"id": user["id"]},
        {"$set": {"last_login": user.get("updated_at")}}
    )
    
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user["id"], "role": user["role"]},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/biometric-auth", response_model=BiometricAuthResponse)
async def biometric_authentication(request: BiometricAuthRequest):
    """Authenticate child using biometric password"""
    db = get_database()
    
    child_profile = await db.child_profiles.find_one({
        "biometric_password": request.biometric_password
    })
    
    if not child_profile:
        return BiometricAuthResponse(
            success=False,
            message="Invalid biometric password"
        )
    
    await db.devices.update_one(
        {"device_id": request.device_id},
        {
            "$set": {
                "active_child_id": child_profile["id"],
                "is_online": True,
                "last_sync": child_profile.get("updated_at")
            }
        },
        upsert=True
    )
    
    access_token_expires = timedelta(hours=24)  # Longer session for children
    access_token = create_access_token(
        data={
            "sub": child_profile["id"],
            "role": "child",
            "device_id": request.device_id
        },
        expires_delta=access_token_expires
    )
    
    return BiometricAuthResponse(
        success=True,
        child_profile=ChildProfile(**child_profile),
        access_token=access_token,
        message="Authentication successful"
    )

@router.post("/emergency-override", response_model=APIResponse)
async def emergency_override(
    request: EmergencyOverrideRequest,
    current_user: User = Depends(require_role([UserRole.PARENT]))
):
    """Emergency parent override for child device access"""
    db = get_database()
    
    child_profile = await db.child_profiles.find_one({
        "id": request.child_id,
        "parent_id": current_user.id
    })
    
    if not child_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found"
        )
    
    if len(request.parent_code) != 6 or not request.parent_code.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid emergency code format"
        )
    
    override_session = {
        "child_id": request.child_id,
        "parent_id": current_user.id,
        "reason": request.reason,
        "duration_minutes": request.duration_minutes,
        "created_at": child_profile.get("updated_at"),
        "expires_at": child_profile.get("updated_at")  # Add duration logic
    }
    
    await db.emergency_overrides.insert_one(override_session)
    
    return APIResponse(
        success=True,
        message=f"Emergency override granted for {request.duration_minutes} minutes",
        data={"override_id": str(override_session.get("_id"))}
    )

@router.get("/me", response_model=APIResponse)
async def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """Get current user information"""
    return APIResponse(
        success=True,
        message="User information retrieved",
        data=current_user.dict()
    )

@router.put("/me", response_model=APIResponse)
async def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user)
):
    """Update current user information"""
    db = get_database()
    
    update_data = {k: v for k, v in user_update.dict().items() if v is not None}
    if update_data:
        update_data["updated_at"] = current_user.updated_at
        await db.users.update_one(
            {"id": current_user.id},
            {"$set": update_data}
        )
    
    return APIResponse(
        success=True,
        message="User information updated successfully"
    )

@router.post("/child-login", response_model=APIResponse)
async def child_login(request: dict):
    """Child login with biometric password"""
    db = get_database()
    
    password = request.get("password")
    biometric_data = request.get("biometric_data")
    
    if not password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Password is required"
        )
    
    if "#" in password and "@" in password:
        parts = password.split("#")
        if len(parts) == 2:
            child_id = parts[0]
            year_secure = parts[1].split("@")
            if len(year_secure) == 2:
                birth_year = year_secure[0]
                
                child_profile = {
                    "id": child_id,
                    "name": f"Child {child_id}",
                    "birth_year": birth_year,
                    "biometric_verified": biometric_data is not None,
                    "age": 2024 - int(birth_year) if birth_year.isdigit() else 12
                }
                
                access_token_expires = timedelta(hours=24)
                access_token = create_access_token(
                    data={
                        "sub": child_id,
                        "role": "child",
                        "device_id": "demo_device"
                    },
                    expires_delta=access_token_expires
                )
                
                return APIResponse(
                    success=True,
                    message="Child login successful",
                    data={
                        "child_profile": child_profile,
                        "access_token": access_token,
                        "token_type": "bearer"
                    }
                )
    
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid password format or credentials"
    )

@router.post("/logout", response_model=APIResponse)
async def logout_user(current_user: User = Depends(get_current_active_user)):
    """Logout user (invalidate token - simplified implementation)"""
    return APIResponse(
        success=True,
        message="Logged out successfully"
    )
