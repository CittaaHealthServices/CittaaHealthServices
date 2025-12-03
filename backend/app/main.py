"""
Vocalysis API - Voice-based Mental Health Screening Platform
CITTAA Health Services Private Limited
"""

from fastapi import FastAPI, HTTPException, Depends, File, UploadFile, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import os
import uuid
from datetime import datetime, timedelta
import jwt
from typing import Optional

from app.routers import auth, voice, predictions, dashboard, admin, psychologist
from app.models.database import init_db, get_db, SessionLocal
from app.models.user import User
from app.utils.config import settings
import bcrypt

def hash_password(password: str) -> str:
    """Hash password using bcrypt"""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def seed_demo_users():
    """Create demo users if they don't exist (idempotent)"""
    db = SessionLocal()
    try:
        # Admin user
        admin_user = db.query(User).filter(User.email == "admin@cittaa.in").first()
        if not admin_user:
            admin_user = User(
                id=str(uuid.uuid4()),
                email="admin@cittaa.in",
                password_hash=hash_password("Admin@123"),
                full_name="Admin User",
                role="admin",
                is_active=True,
                is_verified=True,
                consent_given=True
            )
            db.add(admin_user)
            print("Created admin user: admin@cittaa.in")
        
        # Patient user
        patient_user = db.query(User).filter(User.email == "patient@cittaa.in").first()
        if not patient_user:
            patient_user = User(
                id=str(uuid.uuid4()),
                email="patient@cittaa.in",
                password_hash=hash_password("Patient@123"),
                full_name="Demo Patient",
                role="patient",
                is_active=True,
                is_verified=True,
                consent_given=True
            )
            db.add(patient_user)
            print("Created patient user: patient@cittaa.in")
        
        # Psychologist user
        psychologist_user = db.query(User).filter(User.email == "doctor@cittaa.in").first()
        if not psychologist_user:
            psychologist_user = User(
                id=str(uuid.uuid4()),
                email="doctor@cittaa.in",
                password_hash=hash_password("Doctor@123"),
                full_name="Demo Psychologist",
                role="psychologist",
                is_active=True,
                is_verified=True,
                consent_given=True
            )
            db.add(psychologist_user)
            print("Created psychologist user: doctor@cittaa.in")
        
        db.commit()
        print("Demo users seeding completed")
    except Exception as e:
        print(f"Error seeding demo users: {e}")
        db.rollback()
    finally:
        db.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
    seed_demo_users()
    yield

app = FastAPI(
    title="Vocalysis API",
    description="AI-Powered Voice Mental Health Screening Platform by CITTAA Health Services",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# CORS middleware - allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])
app.include_router(voice.router, prefix="/api/v1/voice", tags=["Voice Analysis"])
app.include_router(predictions.router, prefix="/api/v1/predictions", tags=["Predictions"])
app.include_router(dashboard.router, prefix="/api/v1/dashboard", tags=["Dashboard"])
app.include_router(admin.router, prefix="/api/v1/admin", tags=["Admin"])
app.include_router(psychologist.router, prefix="/api/v1/psychologist", tags=["Psychologist"])

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Welcome to Vocalysis API",
        "version": "1.0.0",
        "company": "CITTAA Health Services Private Limited",
        "docs": "/api/docs"
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "vocalysis-api",
        "version": "1.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/v1/status")
async def api_status():
    """API status endpoint"""
    return {
        "status": "operational",
        "services": {
            "voice_analysis": "active",
            "ml_inference": "active",
            "database": "connected"
        },
        "timestamp": datetime.utcnow().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
