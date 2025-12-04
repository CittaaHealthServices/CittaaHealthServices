"""
Coupon Management Router for Vocalysis API
"""
from fastapi import APIRouter, HTTPException, Depends, status
from datetime import datetime
from typing import List, Optional
from bson import ObjectId

from app.database import db
from app.models import (
    CouponCreate, CouponResponse, CouponValidation, CouponValidationResponse,
    CouponType, CouponStatus
)
from app.routers.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/v1/coupons", tags=["Coupons"])


@router.post("/", response_model=CouponResponse)
async def create_coupon(
    coupon_data: CouponCreate,
    current_user = Depends(get_current_admin)
):
    """Create a new coupon (admin only)"""
    # Check if coupon code already exists
    existing = await db.coupons.find_one({"code": coupon_data.code.upper()})
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Coupon code already exists"
        )
    
    now = datetime.utcnow()
    coupon_doc = {
        "code": coupon_data.code.upper(),
        "coupon_type": coupon_data.coupon_type.value,
        "discount_value": coupon_data.discount_value,
        "description": coupon_data.description,
        "max_uses": coupon_data.max_uses,
        "valid_from": coupon_data.valid_from,
        "valid_until": coupon_data.valid_until,
        "applicable_plans": coupon_data.applicable_plans,
        "status": CouponStatus.ACTIVE.value,
        "total_uses": 0,
        "created_by": str(current_user["_id"]),
        "created_at": now,
        "updated_at": now
    }
    
    result = await db.coupons.insert_one(coupon_doc)
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(current_user["_id"]),
        "action": "coupon_created",
        "entity_type": "coupon",
        "entity_id": str(result.inserted_id),
        "details": {"code": coupon_data.code.upper()},
        "timestamp": now
    })
    
    return CouponResponse(
        id=str(result.inserted_id),
        code=coupon_doc["code"],
        coupon_type=coupon_doc["coupon_type"],
        discount_value=coupon_doc["discount_value"],
        description=coupon_doc["description"],
        max_uses=coupon_doc["max_uses"],
        valid_from=coupon_doc["valid_from"],
        valid_until=coupon_doc["valid_until"],
        applicable_plans=coupon_doc["applicable_plans"],
        status=coupon_doc["status"],
        total_uses=coupon_doc["total_uses"],
        created_by=coupon_doc["created_by"],
        created_at=coupon_doc["created_at"],
        updated_at=coupon_doc["updated_at"]
    )


@router.get("/", response_model=List[CouponResponse])
async def get_all_coupons(
    status: Optional[str] = None,
    current_user = Depends(get_current_admin)
):
    """Get all coupons (admin only)"""
    query = {}
    if status:
        query["status"] = status
    
    cursor = db.coupons.find(query).sort("created_at", -1)
    
    coupons = []
    async for doc in cursor:
        coupons.append(CouponResponse(
            id=str(doc["_id"]),
            code=doc["code"],
            coupon_type=doc["coupon_type"],
            discount_value=doc["discount_value"],
            description=doc.get("description"),
            max_uses=doc.get("max_uses"),
            valid_from=doc["valid_from"],
            valid_until=doc["valid_until"],
            applicable_plans=doc.get("applicable_plans", []),
            status=doc["status"],
            total_uses=doc.get("total_uses", 0),
            created_by=doc["created_by"],
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        ))
    
    return coupons


@router.post("/validate", response_model=CouponValidationResponse)
async def validate_coupon(
    validation: CouponValidation,
    current_user = Depends(get_current_user)
):
    """Validate a coupon code"""
    coupon = await db.coupons.find_one({"code": validation.code.upper()})
    
    if not coupon:
        return CouponValidationResponse(
            valid=False,
            message="Invalid coupon code"
        )
    
    now = datetime.utcnow()
    
    # Check if coupon is active
    if coupon["status"] != CouponStatus.ACTIVE.value:
        return CouponValidationResponse(
            valid=False,
            message="Coupon is no longer active"
        )
    
    # Check validity period
    if now < coupon["valid_from"]:
        return CouponValidationResponse(
            valid=False,
            message="Coupon is not yet valid"
        )
    
    if now > coupon["valid_until"]:
        return CouponValidationResponse(
            valid=False,
            message="Coupon has expired"
        )
    
    # Check max uses
    if coupon.get("max_uses") and coupon.get("total_uses", 0) >= coupon["max_uses"]:
        return CouponValidationResponse(
            valid=False,
            message="Coupon has reached maximum uses"
        )
    
    # Check if user has already used this coupon (single-use per person)
    user_redemption = await db.coupon_redemptions.find_one({
        "coupon_id": str(coupon["_id"]),
        "user_id": str(current_user["_id"])
    })
    if user_redemption:
        return CouponValidationResponse(
            valid=False,
            message="You have already used this coupon"
        )
    
    # Check applicable plans
    if validation.plan_id and coupon.get("applicable_plans"):
        if validation.plan_id not in coupon["applicable_plans"]:
            return CouponValidationResponse(
                valid=False,
                message="Coupon not applicable for this plan"
            )
    
    # Calculate discount amount (for display purposes)
    discount_amount = None
    if coupon["coupon_type"] == CouponType.PERCENTAGE.value:
        discount_amount = coupon["discount_value"]  # percentage
    elif coupon["coupon_type"] == CouponType.FIXED_AMOUNT.value:
        discount_amount = coupon["discount_value"]  # fixed amount
    elif coupon["coupon_type"] == CouponType.FREE_TRIAL.value:
        discount_amount = coupon["discount_value"]  # trial days
    
    return CouponValidationResponse(
        valid=True,
        coupon=CouponResponse(
            id=str(coupon["_id"]),
            code=coupon["code"],
            coupon_type=coupon["coupon_type"],
            discount_value=coupon["discount_value"],
            description=coupon.get("description"),
            max_uses=coupon.get("max_uses"),
            valid_from=coupon["valid_from"],
            valid_until=coupon["valid_until"],
            applicable_plans=coupon.get("applicable_plans", []),
            status=coupon["status"],
            total_uses=coupon.get("total_uses", 0),
            created_by=coupon["created_by"],
            created_at=coupon["created_at"],
            updated_at=coupon["updated_at"]
        ),
        discount_amount=discount_amount,
        message="Coupon is valid"
    )


@router.put("/{coupon_id}/disable")
async def disable_coupon(
    coupon_id: str,
    current_user = Depends(get_current_admin)
):
    """Disable a coupon (admin only)"""
    coupon = await db.coupons.find_one({"_id": ObjectId(coupon_id)})
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    now = datetime.utcnow()
    await db.coupons.update_one(
        {"_id": ObjectId(coupon_id)},
        {"$set": {"status": CouponStatus.DISABLED.value, "updated_at": now}}
    )
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(current_user["_id"]),
        "action": "coupon_disabled",
        "entity_type": "coupon",
        "entity_id": coupon_id,
        "details": {"code": coupon["code"]},
        "timestamp": now
    })
    
    return {"message": "Coupon disabled successfully"}


@router.put("/{coupon_id}/enable")
async def enable_coupon(
    coupon_id: str,
    current_user = Depends(get_current_admin)
):
    """Enable a coupon (admin only)"""
    coupon = await db.coupons.find_one({"_id": ObjectId(coupon_id)})
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    now = datetime.utcnow()
    await db.coupons.update_one(
        {"_id": ObjectId(coupon_id)},
        {"$set": {"status": CouponStatus.ACTIVE.value, "updated_at": now}}
    )
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(current_user["_id"]),
        "action": "coupon_enabled",
        "entity_type": "coupon",
        "entity_id": coupon_id,
        "details": {"code": coupon["code"]},
        "timestamp": now
    })
    
    return {"message": "Coupon enabled successfully"}


@router.delete("/{coupon_id}")
async def delete_coupon(
    coupon_id: str,
    current_user = Depends(get_current_admin)
):
    """Delete a coupon (admin only)"""
    coupon = await db.coupons.find_one({"_id": ObjectId(coupon_id)})
    
    if not coupon:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Coupon not found"
        )
    
    await db.coupons.delete_one({"_id": ObjectId(coupon_id)})
    
    # Log audit
    await db.audit_logs.insert_one({
        "user_id": str(current_user["_id"]),
        "action": "coupon_deleted",
        "entity_type": "coupon",
        "entity_id": coupon_id,
        "details": {"code": coupon["code"]},
        "timestamp": datetime.utcnow()
    })
    
    return {"message": "Coupon deleted successfully"}
