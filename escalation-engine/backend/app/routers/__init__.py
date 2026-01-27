"""
API Routers for CITTAA Escalation Engine
Using MongoDB-based routers for all features
"""
from app.routers.auth_mongodb import router as auth_router
from app.routers.reports_mongodb import router as reports_router
from app.routers.escalation_mongodb import router as escalation_router
from app.routers.admin_mongodb import router as admin_router
from app.routers.students_mongodb import router as students_router
from app.routers.institutions_mongodb import router as institutions_router
