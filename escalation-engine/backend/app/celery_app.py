"""
Celery application configuration for async task processing.
Handles email notifications, PDF generation, and AI analysis tasks.
"""
import os
from celery import Celery

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

celery_app = Celery(
    "cittaa_escalation",
    broker=REDIS_URL,
    backend=REDIS_URL,
    include=[
        "app.tasks.email_tasks",
        "app.tasks.report_tasks",
        "app.tasks.ai_tasks",
    ]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=300,
    task_soft_time_limit=240,
    worker_prefetch_multiplier=1,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    beat_schedule={
        "cleanup-old-notifications": {
            "task": "app.tasks.email_tasks.cleanup_old_notifications",
            "schedule": 86400.0,
        },
        "generate-daily-summary": {
            "task": "app.tasks.report_tasks.generate_daily_summary",
            "schedule": 86400.0,
        },
    },
)
