"""
Pydantic schemas for CITTAA Escalation Engine
"""
from app.schemas.user import UserCreate, UserResponse, UserLogin, TokenResponse
from app.schemas.institution import InstitutionCreate, InstitutionResponse
from app.schemas.student import StudentCreate, StudentResponse
from app.schemas.session import SessionCreate, SessionResponse, SessionDetail
from app.schemas.report import DailyReportCreate, DailyReportResponse, WeeklyReportCreate, WeeklyReportResponse, MonthlyReportCreate, MonthlyReportResponse
from app.schemas.escalation import EscalationCaseCreate, EscalationCaseResponse, EscalationAssessment
