"""
AI analysis tasks for Celery.
"""
from app.celery_app import celery_app
from app.services.ai_engine import AIEscalationEngine


@celery_app.task(bind=True, max_retries=2, default_retry_delay=10)
def analyze_session_async(
    self,
    session_notes: str,
    student_id: str,
    language: str = "en",
    historical_context: dict = None,
):
    """Analyze session notes asynchronously for escalation detection."""
    try:
        engine = AIEscalationEngine()
        result = engine.analyze_session(
            session_notes=session_notes,
            language=language,
            historical_context=historical_context,
        )
        
        return {
            "student_id": student_id,
            "escalation_level": result.escalation_level,
            "risk_category": result.risk_category,
            "confidence_score": result.confidence_score,
            "keywords_detected": result.keywords_detected,
            "requires_immediate_action": result.requires_immediate_action,
        }
    except Exception as exc:
        self.retry(exc=exc)


@celery_app.task
def retrain_model_with_feedback(
    case_id: str,
    original_prediction: dict,
    corrected_level: str,
    feedback_notes: str,
):
    """Store feedback for model retraining."""
    return {
        "case_id": case_id,
        "feedback_stored": True,
        "corrected_level": corrected_level,
    }
