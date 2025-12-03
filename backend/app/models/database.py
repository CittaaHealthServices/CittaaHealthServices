"""
Database configuration and session management
Supports both SQLite (development) and PostgreSQL (production via Cloud SQL)
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import logging

logger = logging.getLogger(__name__)

# Database configuration
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vocalysis.db")

def create_db_engine():
    """Create database engine based on environment configuration"""
    # Handle SQLite connection args
    if DATABASE_URL.startswith("sqlite"):
        logger.info("Using SQLite database")
        return create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False}
        )
    else:
        # PostgreSQL configuration (works with Cloud SQL via Unix socket)
        logger.info(f"Using PostgreSQL database: {DATABASE_URL[:50]}...")
        return create_engine(
            DATABASE_URL,
            pool_size=5,
            max_overflow=2,
            pool_timeout=30,
            pool_recycle=1800,
            pool_pre_ping=True
        )

# Create engine at module load time
engine = create_db_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Initialize database tables"""
    from app.models.user import User
    from app.models.voice_sample import VoiceSample
    from app.models.prediction import Prediction
    from app.models.clinical_assessment import ClinicalAssessment
    from app.models.clinical_trial import ClinicalTrialParticipant, VoiceSession, PersonalizedBaseline
    
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    
    # Seed demo accounts on startup
    seed_demo_accounts()

def seed_demo_accounts():
    """Seed demo accounts if they don't exist"""
    from app.models.user import User
    from passlib.context import CryptContext
    
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    demo_accounts = [
        {"email": "admin@cittaa.in", "password": "Admin@123", "full_name": "Demo Admin", "role": "admin"},
        {"email": "patient@cittaa.in", "password": "Patient@123", "full_name": "Demo Patient", "role": "patient"},
        {"email": "doctor@cittaa.in", "password": "Doctor@123", "full_name": "Demo Doctor", "role": "psychologist"},
        {"email": "researcher@cittaa.in", "password": "Researcher@123", "full_name": "Demo Researcher", "role": "researcher"},
    ]
    
    db = SessionLocal()
    try:
        for account in demo_accounts:
            existing = db.query(User).filter(User.email == account["email"]).first()
            if not existing:
                hashed_password = pwd_context.hash(account["password"])
                user = User(
                    email=account["email"],
                    password_hash=hashed_password,
                    full_name=account["full_name"],
                    role=account["role"],
                    is_active=True,
                    is_verified=True
                )
                db.add(user)
                print(f"Created demo account: {account['email']}")
        db.commit()
        print("Demo accounts seeding completed")
    except Exception as e:
        print(f"Error seeding demo accounts: {e}")
        db.rollback()
    finally:
        db.close()
