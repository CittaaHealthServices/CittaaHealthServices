"""
Payment Router for Vocalysis API (Cashfree Integration)
"""
from fastapi import APIRouter, HTTPException, Depends, status, Request
from datetime import datetime, timedelta
from typing import Optional
import httpx
import uuid
from bson import ObjectId

from app.config import settings
from app.database import db
from app.models import (
    PaymentCreate, PaymentResponse, CashfreeOrderResponse,
    PaymentStatus, SubscriptionStatus, CouponType
)
from app.routers.auth import get_current_user, get_current_admin

router = APIRouter(prefix="/api/v1/payments", tags=["Payments"])

# Subscription plans
SUBSCRIPTION_PLANS = {
    "premium_individual": {
        "name": "Premium Individual",
        "price": 999,
        "duration_days": 30,
        "features": ["Unlimited voice analysis", "Personalized baseline", "Trend tracking"]
    },
    "premium_plus": {
        "name": "Premium Plus",
        "price": 1999,
        "duration_days": 30,
        "features": ["All Premium features", "Priority support", "Advanced analytics"]
    },
    "corporate": {
        "name": "Corporate",
        "price": 4999,
        "duration_days": 30,
        "features": ["All Premium Plus features", "Team management", "API access"]
    }
}


def get_cashfree_headers():
    """Get headers for Cashfree API requests"""
    return {
        "x-client-id": settings.cashfree_client_id,
        "x-client-secret": settings.cashfree_client_secret,
        "x-api-version": settings.cashfree_api_version,
        "Content-Type": "application/json"
    }


def get_cashfree_base_url():
    """Get Cashfree API base URL based on environment"""
    if settings.cashfree_environment == "production":
        return "https://api.cashfree.com/pg"
    return "https://sandbox.cashfree.com/pg"


@router.get("/plans")
async def get_subscription_plans():
    """Get available subscription plans"""
    return SUBSCRIPTION_PLANS


@router.post("/create-order", response_model=CashfreeOrderResponse)
async def create_payment_order(
    payment_data: PaymentCreate,
    current_user = Depends(get_current_user)
):
    """Create a Cashfree payment order"""
    # Validate plan
    if payment_data.plan_id not in SUBSCRIPTION_PLANS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid plan ID"
        )
    
    plan = SUBSCRIPTION_PLANS[payment_data.plan_id]
    amount = plan["price"]
    discount_amount = 0
    
    # Apply coupon if provided
    if payment_data.coupon_code:
        coupon = await db.coupons.find_one({
            "code": payment_data.coupon_code.upper(),
            "status": "active"
        })
        
        if coupon:
            now = datetime.utcnow()
            
            # Validate coupon
            if now >= coupon["valid_from"] and now <= coupon["valid_until"]:
                # Check if user already used this coupon
                user_redemption = await db.coupon_redemptions.find_one({
                    "coupon_id": str(coupon["_id"]),
                    "user_id": str(current_user["_id"])
                })
                
                if not user_redemption:
                    if coupon["coupon_type"] == CouponType.PERCENTAGE.value:
                        discount_amount = amount * (coupon["discount_value"] / 100)
                    elif coupon["coupon_type"] == CouponType.FIXED_AMOUNT.value:
                        discount_amount = min(coupon["discount_value"], amount)
                    elif coupon["coupon_type"] == CouponType.FREE_TRIAL.value:
                        # Free trial - full discount
                        discount_amount = amount
    
    final_amount = max(amount - discount_amount, 0)
    
    # Generate order ID
    order_id = f"VOC_{uuid.uuid4().hex[:12].upper()}"
    
    # Create Cashfree order
    order_payload = {
        "order_id": order_id,
        "order_amount": final_amount,
        "order_currency": payment_data.currency,
        "customer_details": {
            "customer_id": str(current_user["_id"]),
            "customer_email": current_user["email"],
            "customer_phone": current_user.get("phone", "9999999999"),
            "customer_name": current_user["full_name"]
        },
        "order_meta": {
            "return_url": f"https://vocalysis.cittaa.in/payment/callback?order_id={order_id}",
            "notify_url": f"https://vocalysis-api.cittaa.in/api/v1/payments/webhook"
        }
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{get_cashfree_base_url()}/orders",
            json=order_payload,
            headers=get_cashfree_headers()
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create payment order: {response.text}"
            )
        
        cashfree_response = response.json()
    
    # Save payment record
    now = datetime.utcnow()
    payment_doc = {
        "user_id": str(current_user["_id"]),
        "order_id": order_id,
        "amount": final_amount,
        "original_amount": amount,
        "currency": payment_data.currency,
        "status": PaymentStatus.PENDING.value,
        "plan_id": payment_data.plan_id,
        "coupon_code": payment_data.coupon_code,
        "discount_amount": discount_amount,
        "payment_session_id": cashfree_response.get("payment_session_id"),
        "created_at": now,
        "updated_at": now
    }
    
    await db.payments.insert_one(payment_doc)
    
    return CashfreeOrderResponse(
        order_id=order_id,
        payment_session_id=cashfree_response.get("payment_session_id"),
        order_amount=final_amount,
        order_currency=payment_data.currency
    )


@router.post("/webhook")
async def payment_webhook(request: Request):
    """Handle Cashfree payment webhook"""
    try:
        payload = await request.json()
    except:
        raise HTTPException(status_code=400, detail="Invalid payload")
    
    order_id = payload.get("data", {}).get("order", {}).get("order_id")
    payment_status = payload.get("data", {}).get("payment", {}).get("payment_status")
    
    if not order_id:
        return {"status": "ignored"}
    
    # Find payment record
    payment = await db.payments.find_one({"order_id": order_id})
    if not payment:
        return {"status": "not_found"}
    
    # Check idempotency - don't process if already processed
    if payment["status"] in [PaymentStatus.SUCCESS.value, PaymentStatus.REFUNDED.value]:
        return {"status": "already_processed"}
    
    now = datetime.utcnow()
    
    if payment_status == "SUCCESS":
        # Update payment status
        await db.payments.update_one(
            {"order_id": order_id},
            {
                "$set": {
                    "status": PaymentStatus.SUCCESS.value,
                    "transaction_id": payload.get("data", {}).get("payment", {}).get("cf_payment_id"),
                    "payment_method": payload.get("data", {}).get("payment", {}).get("payment_method"),
                    "updated_at": now
                }
            }
        )
        
        # Create subscription
        plan = SUBSCRIPTION_PLANS.get(payment["plan_id"], {})
        duration_days = plan.get("duration_days", 30)
        
        subscription_doc = {
            "user_id": payment["user_id"],
            "plan_id": payment["plan_id"],
            "status": SubscriptionStatus.ACTIVE.value,
            "start_date": now,
            "end_date": now + timedelta(days=duration_days),
            "payment_id": str(payment["_id"]),
            "auto_renew": False,
            "created_at": now,
            "updated_at": now
        }
        
        await db.subscriptions.insert_one(subscription_doc)
        
        # Record coupon redemption if used
        if payment.get("coupon_code"):
            coupon = await db.coupons.find_one({"code": payment["coupon_code"].upper()})
            if coupon:
                await db.coupon_redemptions.insert_one({
                    "coupon_id": str(coupon["_id"]),
                    "user_id": payment["user_id"],
                    "payment_id": str(payment["_id"]),
                    "redeemed_at": now
                })
                
                # Increment coupon usage
                await db.coupons.update_one(
                    {"_id": coupon["_id"]},
                    {"$inc": {"total_uses": 1}}
                )
        
        # Log audit
        await db.audit_logs.insert_one({
            "user_id": payment["user_id"],
            "action": "payment_success",
            "entity_type": "payment",
            "entity_id": order_id,
            "details": {"amount": payment["amount"], "plan_id": payment["plan_id"]},
            "timestamp": now
        })
    
    elif payment_status == "FAILED":
        await db.payments.update_one(
            {"order_id": order_id},
            {
                "$set": {
                    "status": PaymentStatus.FAILED.value,
                    "updated_at": now
                }
            }
        )
    
    return {"status": "processed"}


@router.get("/my-payments", response_model=list)
async def get_my_payments(current_user = Depends(get_current_user)):
    """Get current user's payment history"""
    cursor = db.payments.find({
        "user_id": str(current_user["_id"])
    }).sort("created_at", -1)
    
    payments = []
    async for doc in cursor:
        payments.append({
            "id": str(doc["_id"]),
            "order_id": doc["order_id"],
            "amount": doc["amount"],
            "currency": doc.get("currency", "INR"),
            "status": doc["status"],
            "plan_id": doc["plan_id"],
            "coupon_code": doc.get("coupon_code"),
            "discount_amount": doc.get("discount_amount", 0),
            "created_at": doc["created_at"].isoformat()
        })
    
    return payments


@router.get("/my-subscription")
async def get_my_subscription(current_user = Depends(get_current_user)):
    """Get current user's active subscription"""
    subscription = await db.subscriptions.find_one({
        "user_id": str(current_user["_id"]),
        "status": SubscriptionStatus.ACTIVE.value,
        "end_date": {"$gt": datetime.utcnow()}
    })
    
    if not subscription:
        return {"has_subscription": False}
    
    plan = SUBSCRIPTION_PLANS.get(subscription["plan_id"], {})
    
    return {
        "has_subscription": True,
        "subscription": {
            "id": str(subscription["_id"]),
            "plan_id": subscription["plan_id"],
            "plan_name": plan.get("name", "Unknown"),
            "status": subscription["status"],
            "start_date": subscription["start_date"].isoformat(),
            "end_date": subscription["end_date"].isoformat(),
            "features": plan.get("features", [])
        }
    }


@router.get("/all", response_model=list)
async def get_all_payments(
    status: Optional[str] = None,
    current_user = Depends(get_current_admin)
):
    """Get all payments (admin only)"""
    query = {}
    if status:
        query["status"] = status
    
    cursor = db.payments.find(query).sort("created_at", -1).limit(100)
    
    payments = []
    async for doc in cursor:
        user = await db.users.find_one({"_id": ObjectId(doc["user_id"])})
        payments.append({
            "id": str(doc["_id"]),
            "order_id": doc["order_id"],
            "user_email": user["email"] if user else "Unknown",
            "amount": doc["amount"],
            "currency": doc.get("currency", "INR"),
            "status": doc["status"],
            "plan_id": doc["plan_id"],
            "coupon_code": doc.get("coupon_code"),
            "discount_amount": doc.get("discount_amount", 0),
            "created_at": doc["created_at"].isoformat()
        })
    
    return payments
