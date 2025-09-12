import json
import time
import hmac
import hashlib
import base64
from typing import Dict, Tuple


def _gen_token(child_id: str, platform: str, secret: str, ttl_minutes: int = 15) -> str:
    exp = int(time.time()) + ttl_minutes * 60
    payload = f"{child_id}|{platform}|{exp}"
    sig = hmac.new(secret.encode(), payload.encode(), hashlib.sha256).digest()
    token = f"{payload}|{base64.urlsafe_b64encode(sig).decode()}"
    return base64.urlsafe_b64encode(token.encode()).decode()


def _verify_token(token: str, secret: str) -> Tuple[str, str]:
    raw = base64.urlsafe_b64decode(token.encode()).decode()
    parts = raw.split("|")
    if len(parts) != 4:
        raise ValueError("Invalid token")
    child_id, platform, exp_str, sig_b64 = parts
    if int(exp_str) < int(time.time()):
        raise ValueError("Token expired")
    expected_sig = hmac.new(secret.encode(), f"{child_id}|{platform}|{exp_str}".encode(), hashlib.sha256).digest()
    if base64.urlsafe_b64encode(expected_sig).decode() != sig_b64:
        raise ValueError("Invalid token")
    return child_id, platform


def generate_ios_profile(child_id: str, child_data: Dict, family_settings: Dict) -> bytes:
    profile = {
        "PayloadType": "Configuration",
        "PayloadIdentifier": f"com.cittaa.child.{child_id}",
        "PayloadDisplayName": "CITTAA Family Safety",
        "PayloadDescription": "Child protection and educational enhancement",
        "PayloadVersion": 1,
        "ConsentText": "This profile enables family safety features...",
        "PayloadContent": [
            {"VPNBlocking": True},
            {"ContentFilter": {"allowedCategories": ["education", "ncert"], "blockedCategories": ["adult", "violence"]}},
            {"AppWhitelist": ["in.gov.ncert", "org.khanacademy", "com.byjus"]},
            {"CulturalPreferences": family_settings.get("cultural", {"region": "IN"})},
            {"EmergencyContacts": family_settings.get("contacts", [])},
        ],
    }
    return json.dumps(profile, indent=2).encode()


def generate_android_profile(child_id: str, child_data: Dict, family_settings: Dict) -> bytes:
    profile = {
        "applications": ["in.gov.ncert", "org.khanacademy", "com.byjus"],
        "restrictions": {"contentFilter": {"allowed": ["education", "ncert"], "blocked": ["adult", "violence"]}},
        "policies": {"vpnBlocking": True},
        "cultural_settings": family_settings.get("cultural", {"region": "IN"}),
        "emergency_contacts": family_settings.get("contacts", []),
    }
    return json.dumps(profile, indent=2).encode()
