"""
Escalation Notification model for CITTAA Escalation Engine
"""

from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class EscalationNotification(Base):
    """Escalation Notification model - tracks notifications sent for escalation cases"""
    __tablename__ = "escalation_notifications"

    notification_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("escalation_cases.case_id"))
    recipient_email = Column(String(255), nullable=False)
    recipient_type = Column(String(50))  # 'school_principal', 'admin', 'supervisor', 'emergency_contact'
    notification_type = Column(String(50))  # 'email', 'sms', 'whatsapp'
    sent_at = Column(DateTime)
    delivery_status = Column(String(50), default='pending')  # 'pending', 'sent', 'delivered', 'failed'
    error_message = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    escalation_case = relationship("EscalationCase", back_populates="notifications")

    def __repr__(self):
        return f"<EscalationNotification {self.notification_id} ({self.delivery_status})>"
