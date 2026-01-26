"""
Database configuration and session management
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vocalysis.db")

# Handle SQLite connection args
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

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
    
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    
    # Seed demo accounts if they don't exist
    seed_demo_accounts()

def seed_demo_accounts():
    """Create demo accounts for testing"""
    import bcrypt
    from app.models.user import User
    
    db = SessionLocal()
    try:
        demo_accounts = [
            {
                "email": "admin@cittaa.in",
                "password": "Admin@123",
                "full_name": "Admin User",
                "role": "super_admin",
                "is_active": True,
                "is_verified": True
            },
            {
                "email": "doctor@cittaa.in",
                "password": "Doctor@123",
                "full_name": "Dr. Psychologist",
                "role": "psychologist",
                "is_active": True,
                "is_verified": True
            },
            {
                "email": "patient@cittaa.in",
                "password": "Patient@123",
                "full_name": "Demo Patient",
                "role": "patient",
                "is_active": True,
                "is_verified": True
            },
            {
                "email": "researcher@cittaa.in",
                "password": "Researcher@123",
                "full_name": "Research User",
                "role": "researcher",
                "is_active": True,
                "is_verified": True
            }
        ]
        
        for account in demo_accounts:
            existing = db.query(User).filter(User.email == account["email"]).first()
            if not existing:
                password_hash = bcrypt.hashpw(
                    account["password"].encode('utf-8'), 
                    bcrypt.gensalt()
                ).decode('utf-8')
                
                user = User(
                    email=account["email"],
                    password_hash=password_hash,
                    full_name=account["full_name"],
                    role=account["role"],
                    is_active=account["is_active"],
                    is_verified=account["is_verified"]
                )
                db.add(user)
                print(f"Created demo account: {account['email']}")
        
        db.commit()
        print("Demo accounts seeded successfully")
    except Exception as e:
        print(f"Error seeding demo accounts: {e}")
        db.rollback()
    finally:
        db.close()
