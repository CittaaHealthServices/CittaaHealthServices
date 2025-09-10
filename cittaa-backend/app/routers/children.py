from fastapi import APIRouter, Depends, HTTPException, status
from typing import List

from ..database import get_database
from ..models import (
    ChildProfile, User, APIResponse, UserRole, DeviceSyncRequest
)
from ..auth import get_current_active_user, require_role, generate_biometric_password

router = APIRouter()

@router.post("/", response_model=APIResponse)
async def create_child_profile(
    child_data: dict,
    current_user: User = Depends(require_role([UserRole.PARENT]))
):
    """Create a new child profile"""
    db = get_database()
    
    biometric_password = generate_biometric_password(
        child_data["child_name"],
        child_data["birth_year"]
    )
    
    child_profile = ChildProfile(
        user_id=child_data.get("user_id", ""),
        parent_id=current_user.id,
        child_name=child_data["child_name"],
        birth_year=child_data["birth_year"],
        biometric_password=biometric_password,
        grade_level=child_data.get("grade_level"),
        school_id=child_data.get("school_id"),
        allowed_screen_time=child_data.get("allowed_screen_time", 480),
        educational_goals=child_data.get("educational_goals", []),
        blocked_categories=child_data.get("blocked_categories", []),
        emergency_contacts=child_data.get("emergency_contacts", [])
    )
    
    await db.child_profiles.insert_one(child_profile.dict())
    
    return APIResponse(
        success=True,
        message="Child profile created successfully",
        data={
            "child_id": child_profile.id,
            "biometric_password": biometric_password,
            "child_name": child_profile.child_name
        }
    )

@router.get("/", response_model=APIResponse)
async def get_children(
    current_user: User = Depends(require_role([UserRole.PARENT, UserRole.SCHOOL_ADMIN, UserRole.HOSPITAL_ADMIN]))
):
    """Get all children for current user"""
    db = get_database()
    
    if current_user.role == UserRole.PARENT:
        children = await db.child_profiles.find({"parent_id": current_user.id}).to_list(100)
    elif current_user.role == UserRole.SCHOOL_ADMIN:
        children = await db.child_profiles.find({"school_id": {"$exists": True}}).to_list(100)
    else:
        children = await db.child_profiles.find({"hospital_id": {"$exists": True}}).to_list(100)
    
    return APIResponse(
        success=True,
        message="Children retrieved successfully",
        data={"children": children, "count": len(children)}
    )

@router.get("/{child_id}", response_model=APIResponse)
async def get_child_profile(
    child_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific child profile"""
    db = get_database()
    
    child_profile = await db.child_profiles.find_one({"id": child_id})
    if not child_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found"
        )
    
    if (current_user.role == UserRole.PARENT and 
        child_profile["parent_id"] != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this child profile"
        )
    
    return APIResponse(
        success=True,
        message="Child profile retrieved",
        data=child_profile
    )

@router.put("/{child_id}", response_model=APIResponse)
async def update_child_profile(
    child_id: str,
    update_data: dict,
    current_user: User = Depends(require_role([UserRole.PARENT]))
):
    """Update child profile"""
    db = get_database()
    
    child_profile = await db.child_profiles.find_one({
        "id": child_id,
        "parent_id": current_user.id
    })
    
    if not child_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found"
        )
    
    if "child_name" in update_data or "birth_year" in update_data:
        new_name = update_data.get("child_name", child_profile["child_name"])
        new_birth_year = update_data.get("birth_year", child_profile["birth_year"])
        update_data["biometric_password"] = generate_biometric_password(new_name, new_birth_year)
    
    update_data["updated_at"] = child_profile.get("updated_at")
    
    await db.child_profiles.update_one(
        {"id": child_id},
        {"$set": update_data}
    )
    
    return APIResponse(
        success=True,
        message="Child profile updated successfully"
    )

@router.delete("/{child_id}", response_model=APIResponse)
async def delete_child_profile(
    child_id: str,
    current_user: User = Depends(require_role([UserRole.PARENT]))
):
    """Delete child profile"""
    db = get_database()
    
    result = await db.child_profiles.delete_one({
        "id": child_id,
        "parent_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found"
        )
    
    await db.devices.update_many(
        {"active_child_id": child_id},
        {"$unset": {"active_child_id": ""}}
    )
    
    return APIResponse(
        success=True,
        message="Child profile deleted successfully"
    )

@router.post("/{child_id}/sync", response_model=APIResponse)
async def sync_child_device(
    child_id: str,
    sync_request: DeviceSyncRequest
):
    """Sync child device status"""
    db = get_database()
    
    child_profile = await db.child_profiles.find_one({"id": child_id})
    if not child_profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Child profile not found"
        )
    
    sync_data = {
        "active_child_id": child_id,
        "is_online": sync_request.status == "online",
        "last_sync": child_profile.get("updated_at")
    }
    
    if sync_request.location:
        sync_data["location"] = sync_request.location
    
    await db.devices.update_one(
        {"device_id": sync_request.device_id},
        {"$set": sync_data},
        upsert=True
    )
    
    return APIResponse(
        success=True,
        message="Device sync completed",
        data={"sync_status": "success", "timestamp": sync_data["last_sync"]}
    )

@router.get("/{child_id}/activity", response_model=APIResponse)
async def get_child_activity(
    child_id: str,
    current_user: User = Depends(require_role([UserRole.PARENT, UserRole.TEACHER, UserRole.DOCTOR]))
):
    """Get child's recent activity and analytics"""
    db = get_database()
    
    filtering_events = await db.filtering_events.find(
        {"child_id": child_id}
    ).sort("timestamp", -1).limit(50).to_list(50)
    
    usage_analytics = await db.usage_analytics.find(
        {"child_id": child_id}
    ).sort("date", -1).limit(7).to_list(7)
    
    vpn_events = await db.vpn_detection_events.find(
        {"child_id": child_id}
    ).sort("timestamp", -1).limit(10).to_list(10)
    
    return APIResponse(
        success=True,
        message="Child activity retrieved",
        data={
            "filtering_events": filtering_events,
            "usage_analytics": usage_analytics,
            "vpn_events": vpn_events,
            "summary": {
                "total_blocked_attempts": len([e for e in filtering_events if e["action"] == "blocked"]),
                "total_vpn_attempts": len(vpn_events),
                "avg_daily_screen_time": sum(u["screen_time_minutes"] for u in usage_analytics) / max(len(usage_analytics), 1)
            }
        }
    )
