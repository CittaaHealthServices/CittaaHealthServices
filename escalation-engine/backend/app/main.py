"""
CITTAA Internal Escalation AI Engine System
Main FastAPI Application

This is the core API for the CITTAA Case Escalation Engine,
providing AI-powered risk assessment for psychological case reporting
in schools and hospitals across India.

Features:
- Multilingual support (Hindi, English, Telugu, Tamil, Kannada)
- Multi-stage AI assessment pipeline
- DPDP Act 2023 compliance
- POCSO Act compliance for abuse detection
- Role-based access control (RBAC)
- Real-time escalation notifications
"""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
import os

from app.models.database import init_db
from app.routers import (
    auth_router, reports_router, escalation_router,
    admin_router, students_router, institutions_router
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    logger.info("Starting CITTAA Escalation Engine...")
    init_db()
    logger.info("Database initialized successfully")
    yield
    # Shutdown
    logger.info("Shutting down CITTAA Escalation Engine...")


# Create FastAPI application
app = FastAPI(
    title="CITTAA Internal Escalation AI Engine",
    description="""
    AI-powered case escalation system for psychological case reporting
    in schools and hospitals across India.
    
    ## Features
    
    - **Multilingual Support**: Hindi, English, Telugu, Tamil, Kannada
    - **AI Risk Assessment**: Real-time analysis of session notes
    - **Escalation Levels**: Level 1 (Low) to Level 4 (Emergency)
    - **Compliance**: DPDP Act 2023 and POCSO Act compliant
    - **Reports**: Daily, Weekly, Monthly branded PDF reports
    
    ## Escalation Levels
    
    - **Level 1 (Low)**: Standard follow-up
    - **Level 2 (Moderate)**: Increased monitoring
    - **Level 3 (High)**: Action needed within 24 hours
    - **Level 4 (Emergency)**: Immediate intervention required
    
    ## Authentication
    
    All endpoints require JWT authentication. Use the `/auth/login` endpoint
    to obtain an access token.
    """,
    version="1.0.0",
    contact={
        "name": "CITTAA Health Services",
        "url": "https://www.cittaa.in",
        "email": "info@cittaa.in"
    },
    license_info={
        "name": "Proprietary",
        "url": "https://www.cittaa.in/terms"
    },
    lifespan=lifespan
)

# CORS configuration - DO NOT MODIFY
# This allows the frontend to communicate with the backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "detail": "An internal error occurred. Please try again later.",
            "error_id": str(id(exc))
        }
    )


# Include routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(reports_router, prefix="/api/v1")
app.include_router(escalation_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
app.include_router(students_router, prefix="/api/v1")
app.include_router(institutions_router, prefix="/api/v1")


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint for monitoring"""
    return {
        "status": "healthy",
        "service": "CITTAA Escalation Engine",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "name": "CITTAA Internal Escalation AI Engine",
        "version": "1.0.0",
        "description": "AI-powered case escalation for mental health services",
        "documentation": "/docs",
        "health": "/health",
        "contact": {
            "company": "CITTAA Health Services Private Limited",
            "website": "https://www.cittaa.in",
            "email": "info@cittaa.in"
        }
    }


# API info endpoint
@app.get("/api/v1", tags=["API Info"])
async def api_info():
    """API version information"""
    return {
        "api_version": "v1",
        "endpoints": {
            "auth": "/api/v1/auth",
            "reports": "/api/v1/reports",
            "escalation": "/api/v1/escalation",
            "admin": "/api/v1/admin",
            "students": "/api/v1/students",
            "institutions": "/api/v1/institutions"
        },
        "features": [
            "JWT Authentication",
            "Role-Based Access Control",
            "AI Risk Assessment",
            "Multilingual Support",
            "PDF Report Generation",
            "Email Notifications"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
