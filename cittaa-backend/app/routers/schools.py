from fastapi import APIRouter, UploadFile, File
from pydantic import BaseModel


router = APIRouter(prefix="/api/schools", tags=["schools"])


class BulkRegisterBody(BaseModel):
    school_name: str
    admin_email: str


@router.post("/bulk-register")
def bulk_register(body: BulkRegisterBody):
    return {"status": "ok"}


@router.post("/student-import")
def student_import(file: UploadFile = File(...)):
    return {"status": "ok", "filename": file.filename}


@router.get("/{school_id}/dashboard")
def school_dashboard(school_id: str):
    return {"classes": 10, "students": 300}


@router.post("/classroom-session")
def classroom_session(data: dict):
    return {"status": "ok"}


@router.get("/compliance-report")
def compliance_report():
    return {"report": "ok"}


@router.post("/parent-notification")
def parent_notification(data: dict):
    return {"status": "ok"}
