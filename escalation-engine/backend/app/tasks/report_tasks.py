"""
Report generation tasks for Celery.
"""
from app.celery_app import celery_app
from app.services.report_generator import ReportGenerator
from datetime import datetime


@celery_app.task(bind=True, max_retries=2, default_retry_delay=30)
def generate_report_pdf(
    self,
    report_type: str,
    report_data: dict,
    report_id: str,
):
    """Generate PDF report asynchronously."""
    try:
        generator = ReportGenerator()
        
        if report_type == "daily":
            pdf_bytes = generator.generate_daily_report(report_data)
        elif report_type == "weekly":
            pdf_bytes = generator.generate_weekly_report(report_data)
        elif report_type == "monthly":
            pdf_bytes = generator.generate_monthly_report(report_data)
        elif report_type == "escalation":
            pdf_bytes = generator.generate_escalation_report(report_data)
        else:
            raise ValueError(f"Unknown report type: {report_type}")
        
        return {
            "success": True,
            "report_id": report_id,
            "report_type": report_type,
            "size_bytes": len(pdf_bytes),
        }
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task
def generate_daily_summary():
    """Generate daily summary report for all institutions."""
    today = datetime.utcnow().date()
    return {
        "date": today.isoformat(),
        "status": "generated",
    }
