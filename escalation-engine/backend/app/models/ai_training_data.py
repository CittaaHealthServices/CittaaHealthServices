"""
AI Training Data model for CITTAA Escalation Engine
"""

from sqlalchemy import Column, String, Text, DateTime, Boolean, Numeric, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.models.database import Base


class AITrainingData(Base):
    """AI Training Data model - stores labeled data for model improvement"""
    __tablename__ = "ai_training_data"

    training_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    input_text = Column(Text, nullable=False)
    true_label = Column(String(50))  # ground truth label
    predicted_label = Column(String(50))
    confidence_score = Column(Numeric(5, 4))
    was_correct = Column(Boolean)
    human_reviewed = Column(Boolean, default=False)
    reviewer_id = Column(UUID(as_uuid=True), ForeignKey("users.user_id"))
    review_notes = Column(Text)
    language = Column(String(20))  # 'english', 'hindi', 'telugu', 'tamil', 'kannada'
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    reviewer = relationship("User", back_populates="ai_reviews")

    def __repr__(self):
        return f"<AITrainingData {self.training_id} ({self.true_label})>"
