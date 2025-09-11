from typing import Dict, List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from .models import Child, ConsentRecord, Family

class ConsentManager:
    def __init__(self, db: Session):
        self.db = db
    
    def get_age_appropriate_explanation(self, age: int, consent_type: str) -> str:
        explanations = {
            "content_filtering": {
                "under_13": "Hi! Your family uses CITTAA to keep you safe online. We help block websites that might not be good for kids your age, and we show you fun learning websites instead!",
                "13_to_18": "Your family uses CITTAA Family Safety to help protect you online. We filter content that might be inappropriate for your age and promote educational resources. You can always talk to your parents about any blocks.",
                "18_plus": "Your family has chosen to use CITTAA Family Safety. This system filters content and promotes educational resources. You have full rights to review and modify these settings."
            },
            "activity_monitoring": {
                "under_13": "Your parents can see what websites and apps you use to make sure you're safe. This helps them know if you need help or if something scary happens online.",
                "13_to_18": "Your online activity is monitored to ensure your safety. Your parents can see your browsing history and app usage. This is to protect you and help with any issues that might come up.",
                "18_plus": "Your online activity is being monitored as part of your family's safety agreement. You have the right to review this data and request changes to monitoring settings."
            },
            "biometric_data": {
                "under_13": "We use your face or fingerprint to know it's really you when you use your device. This keeps your account safe and makes sure only you can use it.",
                "13_to_18": "Biometric authentication (face/fingerprint recognition) is used to verify your identity and activate safety features. This data is encrypted and only used for authentication.",
                "18_plus": "Biometric data collection for authentication purposes. You have full control over this feature and can disable it at any time while maintaining account security through passwords."
            }
        }
        
        if age < 13:
            return explanations[consent_type]["under_13"]
        elif age < 18:
            return explanations[consent_type]["13_to_18"]
        else:
            return explanations[consent_type]["18_plus"]
    
    def get_consent_requirements(self, age: int) -> Dict[str, bool]:
        if age < 13:
            return {
                "requires_parent_consent": True,
                "requires_child_assent": True,
                "can_withdraw": False,
                "requires_explanation": True
            }
        elif age < 18:
            return {
                "requires_parent_consent": True,
                "requires_child_consent": True,
                "can_withdraw": True,
                "requires_explanation": True
            }
        else:
            return {
                "requires_parent_consent": False,
                "requires_child_consent": True,
                "can_withdraw": True,
                "requires_explanation": True
            }
    
    def create_consent_record(
        self,
        family_id: int,
        child_id: int,
        consent_type: str,
        consent_given: bool,
        parent_consent: bool = False
    ) -> ConsentRecord:
        child = self.db.query(Child).filter(Child.id == child_id).first()
        if not child:
            raise ValueError("Child not found")
        
        explanation = self.get_age_appropriate_explanation(child.age, consent_type)
        
        consent_record = ConsentRecord(
            family_id=family_id,
            child_id=child_id,
            consent_type=consent_type,
            consent_given=consent_given,
            age_at_consent=child.age,
            explanation_shown=explanation,
            parent_consent=parent_consent
        )
        
        self.db.add(consent_record)
        self.db.commit()
        self.db.refresh(consent_record)
        
        return consent_record
    
    def check_consent_status(self, child_id: int, consent_type: str) -> Optional[ConsentRecord]:
        return self.db.query(ConsentRecord).filter(
            ConsentRecord.child_id == child_id,
            ConsentRecord.consent_type == consent_type,
            ConsentRecord.withdrawal_date.is_(None)
        ).order_by(ConsentRecord.consent_date.desc()).first()
    
    def withdraw_consent(self, child_id: int, consent_type: str) -> bool:
        consent_record = self.check_consent_status(child_id, consent_type)
        if consent_record:
            consent_record.withdrawal_date = datetime.utcnow()
            self.db.commit()
            return True
        return False
    
    def get_family_consent_overview(self, family_id: int) -> List[Dict]:
        family = self.db.query(Family).filter(Family.id == family_id).first()
        if not family:
            return []
        
        overview = []
        for child in family.children:
            child_consent = {
                "child_id": child.id,
                "child_name": child.full_name,
                "age": child.age,
                "consents": {}
            }
            
            consent_types = ["content_filtering", "activity_monitoring", "biometric_data"]
            for consent_type in consent_types:
                consent_record = self.check_consent_status(child.id, consent_type)
                child_consent["consents"][consent_type] = {
                    "given": consent_record.consent_given if consent_record else False,
                    "date": consent_record.consent_date if consent_record else None,
                    "parent_consent": consent_record.parent_consent if consent_record else False
                }
            
            overview.append(child_consent)
        
        return overview
    
    def validate_consent_for_action(self, child_id: int, action_type: str) -> bool:
        consent_mapping = {
            "content_filter": "content_filtering",
            "activity_log": "activity_monitoring",
            "biometric_auth": "biometric_data"
        }
        
        required_consent = consent_mapping.get(action_type)
        if not required_consent:
            return True
        
        consent_record = self.check_consent_status(child_id, required_consent)
        return bool(consent_record and consent_record.consent_given)
