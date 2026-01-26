"""
API Routers for CITTAA Escalation Engine
"""
from app.routers.auth_mongodb import router as auth_router
from app.routers.reports import router as reports_router
from app.routers.escalation import router as escalation_router
from app.routers.admin_mongodb import router as admin_router
from app.routers.students import router as students_router
from app.routers.institutions import router as institutions_router
