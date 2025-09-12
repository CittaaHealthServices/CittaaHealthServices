import os
from fastapi import APIRouter, HTTPException, Response
from pydantic import BaseModel
from ..services.mobile_profile_generator import generate_ios_profile, generate_android_profile, _gen_token, _verify_token


router = APIRouter(prefix="/api/mobile", tags=["mobile"])

SECRET = os.getenv("MOBILE_PROFILE_SECRET", "dev-secret")


class GenerateBody(BaseModel):
    platform: str
    family_settings: dict = {}
    child_data: dict = {}


class ActivateBody(BaseModel):
    child_id: str
    platform: str
    device_fingerprint: str
    biometric_setup: bool = True


@router.post("/generate-profile/{child_id}")
def generate_profile(child_id: str, body: GenerateBody):
    if body.platform not in ("ios", "android"):
        raise HTTPException(status_code=400, detail="Unsupported platform")
    token = _gen_token(child_id, body.platform, SECRET, ttl_minutes=15)
    return {"profile_token": token, "platform": body.platform, "expires_in": 900}


@router.get("/download-profile/{profile_token}")
def download_profile(profile_token: str):
    try:
        child_id, platform = _verify_token(profile_token, SECRET)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

    family_settings = {"cultural": {"region": "IN"}, "contacts": [{"name": "Parent", "phone": "+91XXXXXXXXXX"}]}
    child_data = {}

    if platform == "ios":
        blob = generate_ios_profile(child_id, child_data, family_settings)
        return Response(content=blob, media_type="application/x-apple-aspen-config", headers={"Content-Disposition": 'attachment; filename="CITTAA.mobileconfig"'})
    blob = generate_android_profile(child_id, child_data, family_settings)
    return Response(content=blob, media_type="application/json", headers={"Content-Disposition": 'attachment; filename="CITTAA_android_profile.json"'})


@router.post("/activate-profile")
def activate_profile(body: ActivateBody):
    return {"status": "ok", "child_id": body.child_id, "platform": body.platform}
