"""
Email notification tasks for Celery.
"""
from app.celery_app import celery_app
from app.services.email_service import EmailService
from datetime import datetime, timedelta


@celery_app.task(bind=True, max_retries=3, default_retry_delay=60)
def send_escalation_email(
    self,
    recipient_email: str,
    recipient_name: str,
    escalation_level: str,
    student_code: str,
    risk_category: str,
    escalation_reason: str,
    case_id: str,
    psychologist_name: str,
    institution_name: str,
    pdf_attachment: bytes = None,
):
    """Send escalation notification email asynchronously."""
    try:
        email_service = EmailService()
        success = email_service.send_escalation_notification(
            recipient_email=recipient_email,
            recipient_name=recipient_name,
            escalation_level=escalation_level,
            student_code=student_code,
            risk_category=risk_category,
            escalation_reason=escalation_reason,
            case_id=case_id,
            psychologist_name=psychologist_name,
            institution_name=institution_name,
            pdf_attachment=pdf_attachment,
        )
        return {"success": success, "recipient": recipient_email}
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task
def cleanup_old_notifications():
    """Clean up notification records older than 90 days."""
    cutoff_date = datetime.utcnow() - timedelta(days=90)
    return {"cleaned_before": cutoff_date.isoformat()}
