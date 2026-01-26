"""
Database models for CITTAA Escalation Engine
"""
from app.models.database import Base, get_db, init_db
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
