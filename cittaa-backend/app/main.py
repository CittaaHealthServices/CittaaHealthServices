from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import uvicorn

from .database import connect_to_mongo, close_mongo_connection, connect_to_redis, close_redis_connection
from .routers import auth, children, devices, content, analytics, institutions, mobile, schools
from .models import APIResponse

@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_to_mongo()
    await connect_to_redis()
    yield
    await close_mongo_connection()
    await close_redis_connection()

app = FastAPI(
    title="CITTAA Smart Parental Control System",
    description="AI-powered parental control platform for Indian families, schools, and hospitals",
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

app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(children.router, prefix="/api/children", tags=["Children"])
app.include_router(devices.router, prefix="/api/devices", tags=["Devices"])
app.include_router(content.router, prefix="/api/content", tags=["Content Filtering"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(institutions.router, prefix="/api/institutions", tags=["Institutions"])
app.include_router(mobile.router)
app.include_router(schools.router)

@app.get("/healthz")
async def healthz():
    return APIResponse(success=True, message="CITTAA Parental Control System is running")

@app.get("/")
async def root():
    return APIResponse(
        success=True, 
        message="Welcome to CITTAA Smart Parental Control System",
        data={
            "version": "1.0.0",
            "features": [
                "Biometric Authentication",
                "Real-time Content Filtering",
                "VPN Detection & Blocking",
                "Cultural Content Curation",
                "Multi-language Support",
                "Family Analytics Dashboard"
            ]
        }
    )

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
