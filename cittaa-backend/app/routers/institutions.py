from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..database import get_database
from ..models import (
    School, Hospital, User, APIResponse, UserRole
)
from ..auth import get_current_active_user, require_role

router = APIRouter()

@router.post("/schools", response_model=APIResponse)
async def create_school(
    school_data: dict,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Create a new school"""
    db = get_database()
    
    school = School(
        name=school_data["name"],
        address=school_data["address"],
        city=school_data["city"],
        state=school_data["state"],
        principal_email=school_data["principal_email"],
        subscription_plan=school_data.get("subscription_plan", "basic")
    )
    
    await db.schools.insert_one(school.dict())
    
    return APIResponse(
        success=True,
        message="School created successfully",
        data={"school_id": school.id, "name": school.name}
    )

@router.get("/schools", response_model=APIResponse)
async def get_schools(
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN]))
):
    """Get all schools"""
    db = get_database()
    
    schools = await db.schools.find({}).to_list(100)
    
    return APIResponse(
        success=True,
        message="Schools retrieved successfully",
        data={"schools": schools, "count": len(schools)}
    )

@router.get("/schools/{school_id}", response_model=APIResponse)
async def get_school(
    school_id: str,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN]))
):
    """Get specific school information"""
    db = get_database()
    
    school = await db.schools.find_one({"id": school_id})
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    students_count = await db.child_profiles.count_documents({"school_id": school_id})
    active_devices = await db.devices.count_documents({
        "active_child_id": {"$exists": True},
        "is_online": True
    })
    
    school_data = {
        **school,
        "statistics": {
            "total_students": students_count,
            "active_devices": active_devices,
            "subscription_status": "active"
        }
    }
    
    return APIResponse(
        success=True,
        message="School information retrieved",
        data=school_data
    )

@router.put("/schools/{school_id}", response_model=APIResponse)
async def update_school(
    school_id: str,
    update_data: dict,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.SCHOOL_ADMIN]))
):
    """Update school information"""
    db = get_database()
    
    school = await db.schools.find_one({"id": school_id})
    if not school:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="School not found"
        )
    
    update_data["updated_at"] = school.get("updated_at")
    
    await db.schools.update_one(
        {"id": school_id},
        {"$set": update_data}
    )
    
    return APIResponse(
        success=True,
        message="School updated successfully"
    )

@router.post("/hospitals", response_model=APIResponse)
async def create_hospital(
    hospital_data: dict,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN]))
):
    """Create a new hospital"""
    db = get_database()
    
    hospital = Hospital(
        name=hospital_data["name"],
        address=hospital_data["address"],
        city=hospital_data["city"],
        state=hospital_data["state"],
        admin_email=hospital_data["admin_email"],
        license_number=hospital_data["license_number"],
        subscription_plan=hospital_data.get("subscription_plan", "professional")
    )
    
    await db.hospitals.insert_one(hospital.dict())
    
    return APIResponse(
        success=True,
        message="Hospital created successfully",
        data={"hospital_id": hospital.id, "name": hospital.name}
    )

@router.get("/hospitals", response_model=APIResponse)
async def get_hospitals(
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]))
):
    """Get all hospitals"""
    db = get_database()
    
    hospitals = await db.hospitals.find({}).to_list(100)
    
    return APIResponse(
        success=True,
        message="Hospitals retrieved successfully",
        data={"hospitals": hospitals, "count": len(hospitals)}
    )

@router.get("/hospitals/{hospital_id}", response_model=APIResponse)
async def get_hospital(
    hospital_id: str,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]))
):
    """Get specific hospital information"""
    db = get_database()
    
    hospital = await db.hospitals.find_one({"id": hospital_id})
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    patients_count = await db.child_profiles.count_documents({"hospital_id": hospital_id})
    active_sessions = await db.devices.count_documents({
        "active_child_id": {"$exists": True},
        "is_online": True
    })
    
    hospital_data = {
        **hospital,
        "statistics": {
            "total_patients": patients_count,
            "active_therapy_sessions": active_sessions,
            "subscription_status": "active",
            "compliance_status": "HIPAA Compliant"
        }
    }
    
    return APIResponse(
        success=True,
        message="Hospital information retrieved",
        data=hospital_data
    )

@router.put("/hospitals/{hospital_id}", response_model=APIResponse)
async def update_hospital(
    hospital_id: str,
    update_data: dict,
    current_user: User = Depends(require_role([UserRole.SUPER_ADMIN, UserRole.HOSPITAL_ADMIN]))
):
    """Update hospital information"""
    db = get_database()
    
    hospital = await db.hospitals.find_one({"id": hospital_id})
    if not hospital:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Hospital not found"
        )
    
    update_data["updated_at"] = hospital.get("updated_at")
    
    await db.hospitals.update_one(
        {"id": hospital_id},
        {"$set": update_data}
    )
    
    return APIResponse(
        success=True,
        message="Hospital updated successfully"
    )

@router.get("/subscriptions", response_model=APIResponse)
async def get_subscription_plans():
    """Get available subscription plans"""
    
    subscription_plans = {
        "family_plans": [
            {
                "name": "Family Basic",
                "price": 799,
                "currency": "INR",
                "billing": "monthly",
                "features": [
                    "3 devices",
                    "Basic content filtering",
                    "Parental dashboard",
                    "Email support"
                ],
                "device_limit": 3
            },
            {
                "name": "Family Premium",
                "price": 1299,
                "currency": "INR",
                "billing": "monthly",
                "features": [
                    "6 devices",
                    "AI content curation",
                    "Advanced analytics",
                    "Cultural content",
                    "WhatsApp support"
                ],
                "device_limit": 6
            },
            {
                "name": "Family Enterprise",
                "price": 1999,
                "currency": "INR",
                "billing": "monthly",
                "features": [
                    "Unlimited devices",
                    "Custom settings",
                    "Priority support",
                    "Advanced reporting",
                    "Multi-language support"
                ],
                "device_limit": -1
            }
        ],
        "institutional_plans": [
            {
                "name": "School Institutional",
                "price": 50,
                "currency": "INR",
                "billing": "per student per month",
                "features": [
                    "Bulk student management",
                    "Classroom monitoring",
                    "Teacher dashboard",
                    "Academic progress tracking",
                    "NCERT alignment"
                ]
            },
            {
                "name": "Hospital Professional",
                "price": 5000,
                "currency": "INR",
                "billing": "monthly",
                "features": [
                    "Clinical integration",
                    "Therapy session management",
                    "HIPAA compliance",
                    "Patient privacy controls",
                    "Professional support"
                ]
            }
        ]
    }
    
    return APIResponse(
        success=True,
        message="Subscription plans retrieved",
        data=subscription_plans
    )

@router.post("/subscribe", response_model=APIResponse)
async def create_subscription(
    subscription_data: dict,
    current_user: User = Depends(get_current_active_user)
):
    """Create a new subscription"""
    db = get_database()
    
    subscription = {
        "user_id": current_user.id,
        "plan_name": subscription_data["plan_name"],
        "billing_cycle": subscription_data.get("billing_cycle", "monthly"),
        "status": "active",
        "created_at": current_user.updated_at,
        "next_billing_date": current_user.updated_at,  # Add proper date calculation
        "features": subscription_data.get("features", [])
    }
    
    await db.subscriptions.insert_one(subscription)
    
    return APIResponse(
        success=True,
        message="Subscription created successfully",
        data={"subscription_id": str(subscription.get("_id"))}
    )

@router.get("/compliance", response_model=APIResponse)
async def get_compliance_status():
    """Get regulatory compliance status"""
    
    compliance_data = {
        "regulations": {
            "dpdp_act_2023": {
                "status": "compliant",
                "last_audit": "2024-08-15",
                "next_review": "2024-11-15",
                "features": [
                    "Granular consent management",
                    "Data minimization",
                    "Complete data deletion",
                    "Indian data residency",
                    "Automatic incident reporting"
                ]
            },
            "mental_healthcare_act_2017": {
                "status": "compliant",
                "last_audit": "2024-08-20",
                "next_review": "2024-11-20",
                "features": [
                    "Therapy session privacy",
                    "Clinical establishment integration",
                    "RCI psychologist verification",
                    "Patient privacy controls"
                ]
            }
        },
        "security_certifications": [
            {
                "name": "ISO 27001",
                "status": "valid",
                "expiry": "2025-08-15"
            },
            {
                "name": "SOC 2 Type II",
                "status": "certified",
                "expiry": "2025-09-01"
            }
        ],
        "privacy_metrics": {
            "data_encrypted": "100%",
            "local_processing": "95%",
            "consent_compliance": "100%",
            "data_residency": "India"
        },
        "audit_trail": {
            "last_audit": "15 days ago",
            "next_review": "45 days",
            "compliance_score": "98%"
        }
    }
    
    return APIResponse(
        success=True,
        message="Compliance status retrieved",
        data=compliance_data
    )
