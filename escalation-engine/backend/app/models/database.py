"""
Database configuration and session management for CITTAA Escalation Engine
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://cittaa:password@localhost:5432/cittaa_escalation")

# Handle SQLite connection args for development
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
    from app.models.institution import Institution
    from app.models.student import Student
    from app.models.counseling_session import CounselingSession
    from app.models.daily_report import DailyReport
    from app.models.weekly_report import WeeklyReport
    from app.models.monthly_report import MonthlyReport
    from app.models.escalation_case import EscalationCase
    from app.models.escalation_notification import EscalationNotification
    from app.models.ai_training_data import AITrainingData
    
    Base.metadata.create_all(bind=engine)
    print("CITTAA Escalation Engine database tables created successfully")
