from sqlalchemy.orm import Session
from .models import Family, Parent, Child, ConsentRecord, ActivityLog, ContentBlock, EducationalProgress
from .database import SessionLocal, engine
from .models import Base
from .consent_manager import ConsentManager
from datetime import datetime, timedelta
import json

def create_sample_data():
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        family = Family(family_name="The Sharma Family")
        db.add(family)
        db.commit()
        db.refresh(family)
        
        from passlib.context import CryptContext
        pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        
        parent = Parent(
            family_id=family.id,
            email="rajesh.sharma@example.com",
            hashed_password=pwd_context.hash("password123"),
            full_name="Rajesh Sharma",
            phone_number="+91 98765 43210",
            is_primary=True
        )
        db.add(parent)
        db.commit()
        db.refresh(parent)
        
        child1 = Child(
            family_id=family.id,
            full_name="Aarav Sharma",
            age=12,
            date_of_birth=datetime.now() - timedelta(days=12*365),
            safety_password=pwd_context.hash("aarav123"),
            profile_active=True,
            biometric_enabled=True
        )
        
        child2 = Child(
            family_id=family.id,
            full_name="Priya Sharma",
            age=8,
            date_of_birth=datetime.now() - timedelta(days=8*365),
            safety_password=pwd_context.hash("priya123"),
            profile_active=True,
            biometric_enabled=False
        )
        
        db.add(child1)
        db.add(child2)
        db.commit()
        db.refresh(child1)
        db.refresh(child2)
        
        consent_manager = ConsentManager(db)
        
        consent_manager.create_consent_record(
            family_id=family.id,
            child_id=child1.id,
            consent_type="content_filtering",
            consent_given=True,
            parent_consent=True
        )
        
        consent_manager.create_consent_record(
            family_id=family.id,
            child_id=child1.id,
            consent_type="activity_monitoring",
            consent_given=True,
            parent_consent=True
        )
        
        consent_manager.create_consent_record(
            family_id=family.id,
            child_id=child2.id,
            consent_type="content_filtering",
            consent_given=True,
            parent_consent=True
        )
        
        content_blocks = [
            ContentBlock(
                url="inappropriate-site.com",
                category="adult_content",
                reason="Contains adult content not suitable for children",
                age_restriction=18,
                educational_explanation="This website contains content meant for adults. Instead, try these educational resources that are perfect for learning!",
                alternatives=json.dumps([
                    {"title": "Khan Academy", "url": "https://khanacademy.org"},
                    {"title": "National Geographic Kids", "url": "https://kids.nationalgeographic.com"},
                    {"title": "NASA Kids", "url": "https://www.nasa.gov/audience/forkids/"}
                ])
            ),
            ContentBlock(
                url="violent-game.com",
                category="violence",
                reason="Contains violent content inappropriate for children",
                age_restriction=16,
                educational_explanation="This content contains violence that might be scary or harmful. Here are some fun, safe alternatives!",
                alternatives=json.dumps([
                    {"title": "Scratch Programming", "url": "https://scratch.mit.edu"},
                    {"title": "Code.org", "url": "https://code.org"},
                    {"title": "Educational Games", "url": "https://pbskids.org/games"}
                ])
            )
        ]
        
        for block in content_blocks:
            db.add(block)
        
        activities = [
            ActivityLog(
                family_id=family.id,
                child_id=child1.id,
                activity_type="web_browsing",
                description="Visited Khan Academy Mathematics",
                url="https://khanacademy.org/math",
                blocked=False,
                educational_alternative_shown=False
            ),
            ActivityLog(
                family_id=family.id,
                child_id=child1.id,
                activity_type="web_browsing",
                description="Attempted to visit inappropriate content",
                url="inappropriate-site.com",
                blocked=True,
                educational_alternative_shown=True
            ),
            ActivityLog(
                family_id=family.id,
                child_id=child2.id,
                activity_type="app_usage",
                description="Used educational drawing app",
                app_name="Kids Drawing App",
                blocked=False,
                educational_alternative_shown=False
            )
        ]
        
        for activity in activities:
            db.add(activity)
        
        educational_progress = [
            EducationalProgress(
                child_id=child1.id,
                lesson_type="internet_safety",
                lesson_title="Understanding Online Privacy",
                completed=True,
                score=85.0,
                time_spent=1800,
                completed_at=datetime.now() - timedelta(days=2)
            ),
            EducationalProgress(
                child_id=child1.id,
                lesson_type="digital_citizenship",
                lesson_title="Respectful Online Communication",
                completed=False,
                score=None,
                time_spent=900,
                completed_at=None
            ),
            EducationalProgress(
                child_id=child2.id,
                lesson_type="internet_safety",
                lesson_title="Safe Browsing for Kids",
                completed=True,
                score=92.0,
                time_spent=1200,
                completed_at=datetime.now() - timedelta(days=1)
            )
        ]
        
        for progress in educational_progress:
            db.add(progress)
        
        db.commit()
        print("Sample data created successfully!")
        
    except Exception as e:
        print(f"Error creating sample data: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_sample_data()
