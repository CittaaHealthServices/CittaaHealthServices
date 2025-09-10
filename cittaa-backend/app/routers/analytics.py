from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime, timedelta

from ..database import get_database
from ..models import (
    UsageAnalytics, User, APIResponse, UserRole
)
from ..auth import get_current_active_user, require_role

router = APIRouter()

@router.get("/family/{family_id}", response_model=APIResponse)
async def get_family_analytics(
    family_id: str,
    days: int = 7,
    current_user: User = Depends(require_role([UserRole.PARENT]))
):
    """Get family analytics dashboard data"""
    db = get_database()
    
    children = await db.child_profiles.find({"parent_id": current_user.id}).to_list(10)
    child_ids = [child["id"] for child in children]
    
    start_date = datetime.utcnow() - timedelta(days=days)
    usage_data = await db.usage_analytics.find({
        "child_id": {"$in": child_ids},
        "date": {"$gte": start_date}
    }).to_list(1000)
    
    filtering_events = await db.filtering_events.find({
        "child_id": {"$in": child_ids},
        "timestamp": {"$gte": start_date}
    }).to_list(1000)
    
    vpn_events = await db.vpn_detection_events.find({
        "child_id": {"$in": child_ids},
        "timestamp": {"$gte": start_date}
    }).to_list(100)
    
    total_screen_time = sum(usage["screen_time_minutes"] for usage in usage_data)
    total_educational_time = sum(usage["educational_time_minutes"] for usage in usage_data)
    total_blocked_attempts = len([event for event in filtering_events if event["action"] == "blocked"])
    total_vpn_attempts = len(vpn_events)
    
    avg_daily_screen_time = total_screen_time / max(days, 1)
    avg_daily_educational_time = total_educational_time / max(days, 1)
    educational_percentage = (total_educational_time / max(total_screen_time, 1)) * 100
    
    category_counts = {}
    for event in filtering_events:
        category = event.get("category", "unknown")
        category_counts[category] = category_counts.get(category, 0) + 1
    
    top_categories = sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:5]
    
    focus_scores = [usage["focus_score"] for usage in usage_data if "focus_score" in usage]
    avg_focus_score = sum(focus_scores) / max(len(focus_scores), 1)
    
    analytics_data = {
        "summary": {
            "total_children": len(children),
            "total_screen_time_hours": round(total_screen_time / 60, 1),
            "total_educational_time_hours": round(total_educational_time / 60, 1),
            "educational_percentage": round(educational_percentage, 1),
            "total_blocked_attempts": total_blocked_attempts,
            "total_vpn_attempts": total_vpn_attempts,
            "avg_daily_screen_time_minutes": round(avg_daily_screen_time, 1),
            "avg_daily_educational_time_minutes": round(avg_daily_educational_time, 1),
            "avg_focus_score": round(avg_focus_score, 1)
        },
        "children_data": [],
        "top_categories": [{"category": cat, "count": count} for cat, count in top_categories],
        "daily_breakdown": [],
        "security_events": {
            "blocked_content": total_blocked_attempts,
            "vpn_attempts": total_vpn_attempts,
            "recent_events": filtering_events[-10:] if filtering_events else []
        }
    }
    
    for child in children:
        child_usage = [u for u in usage_data if u["child_id"] == child["id"]]
        child_events = [e for e in filtering_events if e["child_id"] == child["id"]]
        
        child_screen_time = sum(u["screen_time_minutes"] for u in child_usage)
        child_educational_time = sum(u["educational_time_minutes"] for u in child_usage)
        child_blocked = len([e for e in child_events if e["action"] == "blocked"])
        
        analytics_data["children_data"].append({
            "child_id": child["id"],
            "child_name": child["child_name"],
            "screen_time_hours": round(child_screen_time / 60, 1),
            "educational_time_hours": round(child_educational_time / 60, 1),
            "blocked_attempts": child_blocked,
            "focus_score": round(sum(u.get("focus_score", 0) for u in child_usage) / max(len(child_usage), 1), 1)
        })
    
    daily_data = {}
    for usage in usage_data:
        date_str = usage["date"].strftime("%Y-%m-%d")
        if date_str not in daily_data:
            daily_data[date_str] = {
                "date": date_str,
                "screen_time": 0,
                "educational_time": 0,
                "blocked_attempts": 0
            }
        daily_data[date_str]["screen_time"] += usage["screen_time_minutes"]
        daily_data[date_str]["educational_time"] += usage["educational_time_minutes"]
    
    for event in filtering_events:
        if event["action"] == "blocked":
            date_str = event["timestamp"].strftime("%Y-%m-%d")
            if date_str in daily_data:
                daily_data[date_str]["blocked_attempts"] += 1
    
    analytics_data["daily_breakdown"] = list(daily_data.values())
    
    return APIResponse(
        success=True,
        message="Family analytics retrieved successfully",
        data=analytics_data
    )

@router.get("/child/{child_id}", response_model=APIResponse)
async def get_child_analytics(
    child_id: str,
    days: int = 7,
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed analytics for a specific child"""
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
            detail="Not authorized to access this child's analytics"
        )
    
    start_date = datetime.utcnow() - timedelta(days=days)
    
    usage_data = await db.usage_analytics.find({
        "child_id": child_id,
        "date": {"$gte": start_date}
    }).to_list(100)
    
    filtering_events = await db.filtering_events.find({
        "child_id": child_id,
        "timestamp": {"$gte": start_date}
    }).to_list(500)
    
    vpn_events = await db.vpn_detection_events.find({
        "child_id": child_id,
        "timestamp": {"$gte": start_date}
    }).to_list(50)
    
    total_screen_time = sum(usage["screen_time_minutes"] for usage in usage_data)
    total_educational_time = sum(usage["educational_time_minutes"] for usage in usage_data)
    
    category_time = {}
    for usage in usage_data:
        for category in usage.get("top_categories", []):
            category_time[category] = category_time.get(category, 0) + 30  # Estimate 30 min per category
    
    blocked_by_category = {}
    for event in filtering_events:
        if event["action"] == "blocked":
            category = event.get("category", "unknown")
            blocked_by_category[category] = blocked_by_category.get(category, 0) + 1
    
    educational_trend = []
    for usage in sorted(usage_data, key=lambda x: x["date"]):
        educational_trend.append({
            "date": usage["date"].strftime("%Y-%m-%d"),
            "educational_minutes": usage["educational_time_minutes"],
            "focus_score": usage.get("focus_score", 0)
        })
    
    analytics_data = {
        "child_info": {
            "child_id": child_id,
            "child_name": child_profile["child_name"],
            "grade_level": child_profile.get("grade_level"),
            "allowed_screen_time": child_profile.get("allowed_screen_time", 480)
        },
        "summary": {
            "total_screen_time_hours": round(total_screen_time / 60, 1),
            "total_educational_time_hours": round(total_educational_time / 60, 1),
            "educational_percentage": round((total_educational_time / max(total_screen_time, 1)) * 100, 1),
            "avg_daily_screen_time": round(total_screen_time / max(days, 1), 1),
            "avg_focus_score": round(sum(u.get("focus_score", 0) for u in usage_data) / max(len(usage_data), 1), 1),
            "total_blocked_attempts": len([e for e in filtering_events if e["action"] == "blocked"]),
            "total_vpn_attempts": len(vpn_events)
        },
        "time_distribution": [
            {"category": cat, "minutes": mins} for cat, mins in category_time.items()
        ],
        "blocked_content": [
            {"category": cat, "count": count} for cat, count in blocked_by_category.items()
        ],
        "educational_trend": educational_trend,
        "recent_activity": filtering_events[-20:] if filtering_events else [],
        "security_events": {
            "vpn_attempts": len(vpn_events),
            "recent_vpn_events": vpn_events[-5:] if vpn_events else []
        }
    }
    
    return APIResponse(
        success=True,
        message="Child analytics retrieved successfully",
        data=analytics_data
    )

@router.get("/school/{school_id}", response_model=APIResponse)
async def get_school_analytics(
    school_id: str,
    current_user: User = Depends(require_role([UserRole.SCHOOL_ADMIN, UserRole.TEACHER]))
):
    """Get school-wide analytics"""
    db = get_database()
    
    students = await db.child_profiles.find({"school_id": school_id}).to_list(1000)
    student_ids = [student["id"] for student in students]
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    active_devices = await db.devices.find({
        "active_child_id": {"$in": student_ids},
        "is_online": True
    }).to_list(1000)
    
    todays_events = await db.filtering_events.find({
        "child_id": {"$in": student_ids},
        "timestamp": {"$gte": today}
    }).to_list(1000)
    
    total_students = len(students)
    active_students = len(active_devices)
    blocked_attempts_today = len([e for e in todays_events if e["action"] == "blocked"])
    
    focus_scores = []
    for device in active_devices:
        child_events = [e for e in todays_events if e["child_id"] == device.get("active_child_id")]
        blocked_count = len([e for e in child_events if e["action"] == "blocked"])
        focus_score = max(0, 100 - (blocked_count * 10))  # Simplified calculation
        focus_scores.append(focus_score)
    
    avg_focus_score = sum(focus_scores) / max(len(focus_scores), 1)
    
    on_task_students = len([score for score in focus_scores if score >= 80])
    distracted_students = len([score for score in focus_scores if 50 <= score < 80])
    offline_students = total_students - active_students
    
    analytics_data = {
        "school_overview": {
            "total_students": total_students,
            "active_students": active_students,
            "offline_students": offline_students,
            "avg_focus_score": round(avg_focus_score, 1)
        },
        "classroom_status": {
            "on_task_students": on_task_students,
            "distracted_students": distracted_students,
            "offline_students": offline_students,
            "focus_percentage": round((on_task_students / max(active_students, 1)) * 100, 1)
        },
        "security_summary": {
            "blocked_attempts_today": blocked_attempts_today,
            "recent_blocked_attempts": [
                {
                    "student_name": next((s["child_name"] for s in students if s["id"] == e["child_id"]), "Unknown"),
                    "url": e["url"],
                    "category": e["category"],
                    "timestamp": e["timestamp"]
                }
                for e in todays_events[-10:] if e["action"] == "blocked"
            ]
        },
        "active_sessions": [
            {
                "student_name": next((s["child_name"] for s in students if s["id"] == device.get("active_child_id")), "Unknown"),
                "device_type": device.get("device_type"),
                "last_sync": device.get("last_sync"),
                "focus_score": next((score for score, dev in zip(focus_scores, active_devices) if dev["id"] == device["id"]), 0)
            }
            for device in active_devices[:20]  # Limit to 20 for display
        ]
    }
    
    return APIResponse(
        success=True,
        message="School analytics retrieved successfully",
        data=analytics_data
    )

@router.get("/hospital/{hospital_id}", response_model=APIResponse)
async def get_hospital_analytics(
    hospital_id: str,
    current_user: User = Depends(require_role([UserRole.HOSPITAL_ADMIN, UserRole.DOCTOR]))
):
    """Get hospital therapy session analytics"""
    db = get_database()
    
    patients = await db.child_profiles.find({"hospital_id": hospital_id}).to_list(100)
    patient_ids = [patient["id"] for patient in patients]
    
    today = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    
    active_sessions = await db.devices.find({
        "active_child_id": {"$in": patient_ids},
        "is_online": True
    }).to_list(100)
    
    therapy_events = await db.filtering_events.find({
        "child_id": {"$in": patient_ids},
        "timestamp": {"$gte": today}
    }).to_list(500)
    
    total_patients = len(patients)
    active_sessions_count = len(active_sessions)
    
    therapy_metrics = []
    for session in active_sessions:
        patient_id = session.get("active_child_id")
        patient = next((p for p in patients if p["id"] == patient_id), None)
        
        if patient:
            patient_events = [e for e in therapy_events if e["child_id"] == patient_id]
            blocked_count = len([e for e in patient_events if e["action"] == "blocked"])
            
            attention_span = max(1, 10 - blocked_count)  # Scale 1-10
            stress_level = min(blocked_count * 0.5, 5)  # Scale 0-5
            engagement = max(5, 10 - blocked_count)  # Scale 5-10
            
            therapy_metrics.append({
                "patient_name": patient["child_name"],
                "session_duration": "45 minutes",  # Simulated
                "attention_span": attention_span,
                "stress_indicators": "Low" if stress_level < 2 else "Medium" if stress_level < 4 else "High",
                "engagement_level": "High" if engagement >= 8 else "Medium" if engagement >= 6 else "Low",
                "blocked_attempts": blocked_count
            })
    
    analytics_data = {
        "hospital_overview": {
            "total_patients": total_patients,
            "active_sessions": active_sessions_count,
            "avg_attention_span": round(sum(m["attention_span"] for m in therapy_metrics) / max(len(therapy_metrics), 1), 1),
            "high_engagement_sessions": len([m for m in therapy_metrics if m["engagement_level"] == "High"])
        },
        "therapy_sessions": therapy_metrics,
        "security_summary": {
            "blocked_attempts_today": len([e for e in therapy_events if e["action"] == "blocked"]),
            "therapy_mode_violations": len([e for e in therapy_events if e["action"] == "blocked" and "social" in e.get("category", "").lower()])
        },
        "patient_progress": [
            {
                "patient_name": patient["child_name"],
                "therapy_duration": "3 weeks",  # Simulated
                "progress_score": 85,  # Simulated
                "last_session": "Today"
            }
            for patient in patients[:10]  # Limit for display
        ]
    }
    
    return APIResponse(
        success=True,
        message="Hospital analytics retrieved successfully",
        data=analytics_data
    )
