from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..database import get_database
from ..models import (
    Device, DeviceType, User, APIResponse, UserRole,
    DeviceSyncRequest
)
from ..auth import get_current_active_user, require_role

router = APIRouter()

@router.post("/", response_model=APIResponse)
async def register_device(
    device_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Register a new device"""
    db = get_database()
    
    device = Device(
        device_name=device_data["device_name"],
        device_type=DeviceType(device_data["device_type"]),
        device_id=device_data["device_id"],
        owner_id=current_user.id,
        location=device_data.get("location")
    )
    
    await db.devices.insert_one(device.dict())
    
    return APIResponse(
        success=True,
        message="Device registered successfully",
        data={"device_id": device.id, "device_name": device.device_name}
    )

@router.get("/", response_model=APIResponse)
async def get_devices(
    current_user: User = Depends(get_current_active_user)
):
    """Get all devices for current user"""
    db = get_database()
    
    if current_user.role in [UserRole.PARENT]:
        devices = await db.devices.find({"owner_id": current_user.id}).to_list(50)
    elif current_user.role == UserRole.SCHOOL_ADMIN:
        devices = await db.devices.find({"device_type": {"$in": ["web", "windows", "macos"]}}).to_list(100)
    elif current_user.role == UserRole.HOSPITAL_ADMIN:
        devices = await db.devices.find({"device_type": {"$in": ["web", "windows", "macos"]}}).to_list(100)
    else:
        devices = []
    
    return APIResponse(
        success=True,
        message="Devices retrieved successfully",
        data={"devices": devices, "count": len(devices)}
    )

@router.get("/{device_id}", response_model=APIResponse)
async def get_device(
    device_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get specific device information"""
    db = get_database()
    
    device = await db.devices.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    if (current_user.role == UserRole.PARENT and 
        device["owner_id"] != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this device"
        )
    
    return APIResponse(
        success=True,
        message="Device information retrieved",
        data=device
    )

@router.put("/{device_id}", response_model=APIResponse)
async def update_device(
    device_id: str,
    update_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Update device information"""
    db = get_database()
    
    device = await db.devices.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    if (current_user.role == UserRole.PARENT and 
        device["owner_id"] != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this device"
        )
    
    update_data["updated_at"] = device.get("updated_at")
    
    await db.devices.update_one(
        {"id": device_id},
        {"$set": update_data}
    )
    
    return APIResponse(
        success=True,
        message="Device updated successfully"
    )

@router.delete("/{device_id}", response_model=APIResponse)
async def delete_device(
    device_id: str,
    current_user: User = Depends(require_role([UserRole.PARENT]))
):
    """Delete device"""
    db = get_database()
    
    result = await db.devices.delete_one({
        "id": device_id,
        "owner_id": current_user.id
    })
    
    if result.deleted_count == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    return APIResponse(
        success=True,
        message="Device deleted successfully"
    )

@router.post("/{device_id}/sync", response_model=APIResponse)
async def sync_device(
    device_id: str,
    sync_request: DeviceSyncRequest
):
    """Sync device status and location"""
    db = get_database()
    
    device = await db.devices.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    sync_data = {
        "is_online": sync_request.status == "online",
        "last_sync": device.get("updated_at")
    }
    
    if sync_request.child_id:
        sync_data["active_child_id"] = sync_request.child_id
    
    if sync_request.location:
        sync_data["location"] = sync_request.location
    
    await db.devices.update_one(
        {"id": device_id},
        {"$set": sync_data}
    )
    
    return APIResponse(
        success=True,
        message="Device sync completed",
        data={
            "device_id": device_id,
            "sync_status": "success",
            "timestamp": sync_data["last_sync"]
        }
    )

@router.get("/{device_id}/status", response_model=APIResponse)
async def get_device_status(
    device_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get real-time device status"""
    db = get_database()
    
    device = await db.devices.find_one({"id": device_id})
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found"
        )
    
    active_child = None
    if device.get("active_child_id"):
        active_child = await db.child_profiles.find_one({
            "id": device["active_child_id"]
        })
    
    recent_events = await db.filtering_events.find({
        "device_id": device_id
    }).sort("timestamp", -1).limit(5).to_list(5)
    
    status_data = {
        "device": device,
        "active_child": active_child,
        "recent_events": recent_events,
        "sync_status": {
            "is_online": device.get("is_online", False),
            "last_sync": device.get("last_sync"),
            "location": device.get("location")
        }
    }
    
    return APIResponse(
        success=True,
        message="Device status retrieved",
        data=status_data
    )

@router.post("/bulk-sync", response_model=APIResponse)
async def bulk_sync_devices(
    sync_requests: List[DeviceSyncRequest],
    current_user: User = Depends(get_current_active_user)
):
    """Sync multiple devices at once"""
    db = get_database()
    
    sync_results = []
    
    for sync_request in sync_requests:
        try:
            sync_data = {
                "is_online": sync_request.status == "online",
                "last_sync": current_user.updated_at
            }
            
            if sync_request.child_id:
                sync_data["active_child_id"] = sync_request.child_id
            
            if sync_request.location:
                sync_data["location"] = sync_request.location
            
            result = await db.devices.update_one(
                {"device_id": sync_request.device_id},
                {"$set": sync_data},
                upsert=True
            )
            
            sync_results.append({
                "device_id": sync_request.device_id,
                "status": "success",
                "updated": result.modified_count > 0 or result.upserted_id is not None
            })
            
        except Exception as e:
            sync_results.append({
                "device_id": sync_request.device_id,
                "status": "error",
                "error": str(e)
            })
    
    return APIResponse(
        success=True,
        message=f"Bulk sync completed for {len(sync_requests)} devices",
        data={
            "sync_results": sync_results,
            "total_devices": len(sync_requests),
            "successful_syncs": len([r for r in sync_results if r["status"] == "success"])
        }
    )
