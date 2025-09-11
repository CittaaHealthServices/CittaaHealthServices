from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr

from .database import engine, get_db
from .models import Base, Family, Parent, Child, ConsentRecord, ActivityLog, ContentBlock, EducationalProgress, AuditLog
from .consent_manager import ConsentManager

Base.metadata.create_all(bind=engine)

app = FastAPI(title="CITTAA Family Safety API", version="1.0.0")

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()

SECRET_KEY = "cittaa-family-safety-secret-key-2024"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class ParentCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str
    phone_number: Optional[str] = None
    family_name: str

class ParentLogin(BaseModel):
    email: EmailStr
    password: str

class ChildCreate(BaseModel):
    full_name: str
    age: int
    date_of_birth: datetime
    safety_password: str

class ConsentRequest(BaseModel):
    child_id: int
    consent_type: str
    consent_given: bool
    parent_consent: bool = False

class ActivityLogCreate(BaseModel):
    child_id: int
    activity_type: str
    description: str
    url: Optional[str] = None
    app_name: Optional[str] = None
    blocked: bool = False
    educational_alternative_shown: bool = False

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_parent(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        parent_id_str = payload.get("sub")
        if parent_id_str is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        parent_id = int(parent_id_str)
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")
    
    parent = db.query(Parent).filter(Parent.id == parent_id).first()
    if parent is None:
        raise HTTPException(status_code=401, detail="Parent not found")
    return parent

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "service": "CITTAA Family Safety API"}

@app.post("/auth/register")
async def register_parent(parent_data: ParentCreate, db: Session = Depends(get_db)):
    existing_parent = db.query(Parent).filter(Parent.email == parent_data.email).first()
    if existing_parent:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    family = Family(family_name=parent_data.family_name)
    db.add(family)
    db.commit()
    db.refresh(family)
    
    hashed_password = get_password_hash(parent_data.password)
    parent = Parent(
        family_id=family.id,
        email=parent_data.email,
        hashed_password=hashed_password,
        full_name=parent_data.full_name,
        phone_number=parent_data.phone_number,
        is_primary=True
    )
    db.add(parent)
    db.commit()
    db.refresh(parent)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(parent.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "family_id": family.id,
        "parent_id": parent.id
    }

@app.post("/auth/login")
async def login_parent(login_data: ParentLogin, db: Session = Depends(get_db)):
    parent = db.query(Parent).filter(Parent.email == login_data.email).first()
    if not parent or not verify_password(login_data.password, parent.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(parent.id)}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "family_id": parent.family_id,
        "parent_id": parent.id
    }

@app.get("/family/overview")
async def get_family_overview(current_parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    family = db.query(Family).filter(Family.id == current_parent.family_id).first()
    children = db.query(Child).filter(Child.family_id == current_parent.family_id).all()
    
    consent_manager = ConsentManager(db)
    consent_overview = consent_manager.get_family_consent_overview(current_parent.family_id)
    
    return {
        "family": {
            "id": family.id,
            "name": family.family_name,
            "created_at": family.created_at
        },
        "children": [
            {
                "id": child.id,
                "name": child.full_name,
                "age": child.age,
                "profile_active": child.profile_active,
                "biometric_enabled": child.biometric_enabled
            } for child in children
        ],
        "consent_overview": consent_overview
    }

@app.post("/children")
async def create_child(child_data: ChildCreate, current_parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    hashed_password = get_password_hash(child_data.safety_password)
    
    child = Child(
        family_id=current_parent.family_id,
        full_name=child_data.full_name,
        age=child_data.age,
        date_of_birth=child_data.date_of_birth,
        safety_password=hashed_password
    )
    db.add(child)
    db.commit()
    db.refresh(child)
    
    return {
        "child_id": child.id,
        "message": "Child profile created successfully"
    }

@app.post("/consent")
async def manage_consent(consent_data: ConsentRequest, current_parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = db.query(Child).filter(
        Child.id == consent_data.child_id,
        Child.family_id == current_parent.family_id
    ).first()
    
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    consent_manager = ConsentManager(db)
    consent_record = consent_manager.create_consent_record(
        family_id=current_parent.family_id,
        child_id=consent_data.child_id,
        consent_type=consent_data.consent_type,
        consent_given=consent_data.consent_given,
        parent_consent=consent_data.parent_consent
    )
    
    return {
        "consent_id": consent_record.id,
        "explanation": consent_record.explanation_shown,
        "message": "Consent recorded successfully"
    }

@app.get("/children/{child_id}/consent-status")
async def get_child_consent_status(child_id: int, current_parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.family_id == current_parent.family_id
    ).first()
    
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    consent_manager = ConsentManager(db)
    consent_types = ["content_filtering", "activity_monitoring", "biometric_data"]
    
    consent_status = {}
    for consent_type in consent_types:
        consent_record = consent_manager.check_consent_status(child_id, consent_type)
        consent_status[consent_type] = {
            "given": consent_record.consent_given if consent_record else False,
            "date": consent_record.consent_date if consent_record else None,
            "explanation": consent_record.explanation_shown if consent_record else None,
            "can_withdraw": consent_manager.get_consent_requirements(child.age)["can_withdraw"]
        }
    
    return consent_status

@app.post("/activity-log")
async def log_activity(activity_data: ActivityLogCreate, current_parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = db.query(Child).filter(
        Child.id == activity_data.child_id,
        Child.family_id == current_parent.family_id
    ).first()
    
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    consent_manager = ConsentManager(db)
    if not consent_manager.validate_consent_for_action(activity_data.child_id, "activity_log"):
        raise HTTPException(status_code=403, detail="Activity logging not consented")
    
    activity_log = ActivityLog(
        family_id=current_parent.family_id,
        child_id=activity_data.child_id,
        activity_type=activity_data.activity_type,
        description=activity_data.description,
        url=activity_data.url,
        app_name=activity_data.app_name,
        blocked=activity_data.blocked,
        educational_alternative_shown=activity_data.educational_alternative_shown
    )
    db.add(activity_log)
    db.commit()
    
    return {"message": "Activity logged successfully"}

@app.get("/children/{child_id}/activity")
async def get_child_activity(child_id: int, current_parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.family_id == current_parent.family_id
    ).first()
    
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    activities = db.query(ActivityLog).filter(
        ActivityLog.child_id == child_id
    ).order_by(ActivityLog.timestamp.desc()).limit(50).all()
    
    return [
        {
            "id": activity.id,
            "activity_type": activity.activity_type,
            "description": activity.description,
            "url": activity.url,
            "app_name": activity.app_name,
            "blocked": activity.blocked,
            "educational_alternative_shown": activity.educational_alternative_shown,
            "timestamp": activity.timestamp
        } for activity in activities
    ]

@app.get("/content-filter/check")
async def check_content_filter(url: str, child_age: int, db: Session = Depends(get_db)):
    content_block = db.query(ContentBlock).filter(
        ContentBlock.url.contains(url),
        ContentBlock.age_restriction >= child_age
    ).first()
    
    if content_block:
        return {
            "blocked": True,
            "reason": content_block.reason,
            "educational_explanation": content_block.educational_explanation,
            "alternatives": content_block.alternatives
        }
    
    return {
        "blocked": False,
        "message": "Content is appropriate for this age group"
    }

@app.get("/educational/progress/{child_id}")
async def get_educational_progress(child_id: int, current_parent: Parent = Depends(get_current_parent), db: Session = Depends(get_db)):
    child = db.query(Child).filter(
        Child.id == child_id,
        Child.family_id == current_parent.family_id
    ).first()
    
    if not child:
        raise HTTPException(status_code=404, detail="Child not found")
    
    progress = db.query(EducationalProgress).filter(
        EducationalProgress.child_id == child_id
    ).all()
    
    return [
        {
            "lesson_type": p.lesson_type,
            "lesson_title": p.lesson_title,
            "completed": p.completed,
            "score": p.score,
            "time_spent": p.time_spent,
            "completed_at": p.completed_at
        } for p in progress
    ]

@app.post("/sample-data")
async def create_sample_data(db: Session = Depends(get_db)):
    from .sample_data import create_sample_data
    try:
        create_sample_data()
        return {"message": "Sample data created successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create sample data: {str(e)}")
