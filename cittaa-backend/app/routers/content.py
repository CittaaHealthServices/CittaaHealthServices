from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional

from ..database import get_database
from ..models import (
    ContentFilterRequest, ContentFilterResponse, APIResponse,
    EducationalContent, FilteringEvent, VPNDetectionEvent,
    ContentCategory, Language
)
from ..content_filter import content_filter
from ..auth import get_current_active_user

router = APIRouter()

@router.post("/filter", response_model=ContentFilterResponse)
async def filter_content(request: ContentFilterRequest):
    """Filter content and determine if it should be blocked"""
    db = get_database()
    
    analysis_result = await content_filter.analyze_content(
        url=request.url,
        content=request.content
    )
    
    filtering_event = FilteringEvent(
        child_id=request.child_id,
        device_id=request.device_id,
        url=request.url,
        category=analysis_result["category"],
        action="blocked" if analysis_result["is_blocked"] else "allowed",
        metadata=analysis_result
    )
    
    await db.filtering_events.insert_one(filtering_event.dict())
    
    alternative_content = []
    if analysis_result["is_blocked"]:
        alternative_content = await get_educational_alternatives(
            category=analysis_result["category"]
        )
    
    return ContentFilterResponse(
        allowed=not analysis_result["is_blocked"],
        category=analysis_result["category"],
        reason=analysis_result["reason"],
        confidence_score=analysis_result["confidence_score"],
        alternative_content=alternative_content
    )

@router.post("/detect-vpn", response_model=APIResponse)
async def detect_vpn(device_data: dict):
    """Detect VPN usage on device"""
    db = get_database()
    
    vpn_analysis = await content_filter.detect_vpn_usage(device_data)
    
    if vpn_analysis["vpn_detected"]:
        vpn_event = VPNDetectionEvent(
            child_id=device_data.get("child_id", ""),
            device_id=device_data.get("device_id", ""),
            vpn_app_name=", ".join(vpn_analysis["detection_methods"]),
            detection_method="automated_scan",
            action_taken="blocked"
        )
        
        await db.vpn_detection_events.insert_one(vpn_event.dict())
    
    return APIResponse(
        success=True,
        message="VPN detection completed",
        data=vpn_analysis
    )

@router.get("/educational", response_model=APIResponse)
async def get_educational_content(
    language: Language = Language.ENGLISH,
    subject: Optional[str] = None,
    grade_level: Optional[str] = None
):
    """Get curated educational content"""
    db = get_database()
    
    query = {"language": language}
    if subject:
        query["subject"] = subject
    if grade_level:
        query["grade_levels"] = grade_level
    
    educational_content = await db.educational_content.find(query).limit(20).to_list(20)
    
    return APIResponse(
        success=True,
        message="Educational content retrieved",
        data={"content": educational_content, "count": len(educational_content)}
    )

@router.post("/educational", response_model=APIResponse)
async def add_educational_content(
    content_data: dict,
    current_user = Depends(get_current_active_user)
):
    """Add new educational content"""
    db = get_database()
    
    educational_content = EducationalContent(**content_data)
    await db.educational_content.insert_one(educational_content.dict())
    
    return APIResponse(
        success=True,
        message="Educational content added successfully",
        data={"content_id": educational_content.id}
    )

@router.get("/cultural/{region}", response_model=APIResponse)
async def get_cultural_content(
    region: str,
    language: Language = Language.ENGLISH
):
    """Get culturally relevant content for specific Indian regions"""
    db = get_database()
    
    cultural_content = await db.educational_content.find({
        "cultural_context": {"$in": [region.lower(), "indian", "universal"]},
        "language": language
    }).limit(15).to_list(15)
    
    cultural_data = {
        "tamil_nadu": {
            "festivals": ["Pongal", "Diwali", "Tamil New Year"],
            "traditions": ["Classical Dance", "Temple Architecture", "Tamil Literature"],
            "food": ["Sambar", "Rasam", "Idli", "Dosa"]
        },
        "maharashtra": {
            "festivals": ["Ganesh Chaturthi", "Gudi Padwa", "Navratri"],
            "traditions": ["Lavani Dance", "Warli Art", "Marathi Literature"],
            "food": ["Vada Pav", "Puran Poli", "Misal Pav"]
        },
        "west_bengal": {
            "festivals": ["Durga Puja", "Kali Puja", "Poila Boishakh"],
            "traditions": ["Rabindra Sangeet", "Bengali Literature", "Terracotta Art"],
            "food": ["Fish Curry", "Rasgulla", "Sandesh"]
        }
    }
    
    region_data = cultural_data.get(region.lower(), {})
    
    return APIResponse(
        success=True,
        message=f"Cultural content for {region} retrieved",
        data={
            "educational_content": cultural_content,
            "cultural_highlights": region_data,
            "region": region,
            "language": language
        }
    )

@router.get("/blocked-attempts/{child_id}", response_model=APIResponse)
async def get_blocked_attempts(
    child_id: str,
    current_user = Depends(get_current_active_user)
):
    """Get recent blocked content attempts for a child"""
    db = get_database()
    
    blocked_attempts = await db.filtering_events.find({
        "child_id": child_id,
        "action": "blocked"
    }).sort("timestamp", -1).limit(20).to_list(20)
    
    return APIResponse(
        success=True,
        message="Blocked attempts retrieved",
        data={"blocked_attempts": blocked_attempts, "count": len(blocked_attempts)}
    )

async def get_educational_alternatives(category: ContentCategory) -> List[str]:
    """Get educational alternatives based on blocked content category"""
    alternatives = {
        ContentCategory.ADULT_CONTENT: [
            "https://ncert.nic.in/textbook/textbook.htm",
            "https://www.khanacademy.org/",
            "https://byjus.com/ncert-solutions/"
        ],
        ContentCategory.VIOLENCE: [
            "https://www.khanacademy.org/humanities/world-history",
            "https://ncert.nic.in/textbook/textbook.htm?khss=0-9",
            "https://www.britannica.com/kids"
        ],
        ContentCategory.INAPPROPRIATE: [
            "https://www.khanacademy.org/",
            "https://ncert.nic.in/",
            "https://www.nasa.gov/audience/forkids/",
            "https://kids.nationalgeographic.com/"
        ]
    }
    
    return alternatives.get(category, [
        "https://ncert.nic.in/",
        "https://www.khanacademy.org/",
        "https://byjus.com/"
    ])
