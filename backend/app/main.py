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
import logging

from app.routers import auth, voice, predictions, dashboard, admin, psychologist
from app.models.database import init_db, get_db
from app.models.mongodb import init_mongodb, close_mongodb
from app.utils.config import settings
from app.middleware.security import SecurityMiddleware

# Configure logging for security audit trail
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize databases on startup"""
    logger.info("Starting Vocalysis API...")
    # Initialize SQLite (for backward compatibility)
    init_db()
    # Initialize MongoDB (for persistent storage)
    try:
        init_mongodb()
        logger.info("MongoDB initialized successfully")
    except Exception as e:
        logger.warning(f"MongoDB initialization warning: {e}")
    yield
    # Cleanup on shutdown
    logger.info("Shutting down Vocalysis API...")
    close_mongodb()

app = FastAPI(
    title="Vocalysis API",
    description="AI-Powered Voice Mental Health Screening Platform by CITTAA Health Services",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan
)

# Add security middleware (rate limiting, security headers, audit logging)
app.add_middleware(SecurityMiddleware)

# CORS middleware - configured for production security
# In production, replace "*" with specific allowed origins
ALLOWED_ORIGINS = [
    "https://vocalysis-frontend-1081764900204.us-central1.run.app",
    "https://vocalysis.cittaa.in",
    "https://cittaa.in",
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "X-Requested-With"],
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
