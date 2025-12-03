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

from app.routers import auth, voice, predictions, dashboard, admin, psychologist, clinical_trial
from app.models.database import init_db, get_db
from app.utils.config import settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup"""
    init_db()
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
app.include_router(clinical_trial.router, prefix="/api/v1/clinical-trial", tags=["Clinical Trial"])

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
