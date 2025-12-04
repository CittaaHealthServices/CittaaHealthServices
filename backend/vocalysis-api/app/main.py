"""
Vocalysis Premium API - Main Application
CITTAA Health Services
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.database import connect_to_mongodb, close_mongodb_connection
from app.routers import auth, trials, psychologists, coupons, payments, admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    await connect_to_mongodb()
    yield
    # Shutdown
    await close_mongodb_connection()


app = FastAPI(
    title="Vocalysis Premium API",
    description="Mental Health Voice Analysis API for CITTAA Health Services",
    version="1.0.0",
    lifespan=lifespan
)

# Disable CORS. Do not remove this for full-stack development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Include routers
app.include_router(auth.router)
app.include_router(trials.router)
app.include_router(psychologists.router)
app.include_router(coupons.router)
app.include_router(payments.router)
app.include_router(admin.router)


@app.get("/healthz")
async def healthz():
    """Health check endpoint"""
    return {"status": "ok", "service": "vocalysis-api"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Vocalysis Premium API",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }
