from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()

class Family(Base):
    __tablename__ = "families"
    
    id = Column(Integer, primary_key=True, index=True)
    family_name = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    parents = relationship("Parent", back_populates="family")
    children = relationship("Child", back_populates="family")
    consent_records = relationship("ConsentRecord", back_populates="family")
    activity_logs = relationship("ActivityLog", back_populates="family")

class Parent(Base):
    __tablename__ = "parents"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone_number = Column(String)
    is_primary = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    family = relationship("Family", back_populates="parents")

class Child(Base):
    __tablename__ = "children"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    full_name = Column(String, nullable=False)
    age = Column(Integer, nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    safety_password = Column(String, nullable=False)
    biometric_enabled = Column(Boolean, default=False)
    profile_active = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    family = relationship("Family", back_populates="children")
    consent_records = relationship("ConsentRecord", back_populates="child")
    activity_logs = relationship("ActivityLog", back_populates="child")
    educational_progress = relationship("EducationalProgress", back_populates="child")
    mobile_profiles = relationship("MobileProfile", back_populates="child")

class ConsentRecord(Base):
    __tablename__ = "consent_records"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    consent_type = Column(String, nullable=False)
    consent_given = Column(Boolean, nullable=False)
    consent_date = Column(DateTime, default=datetime.utcnow)
    age_at_consent = Column(Integer, nullable=False)
    explanation_shown = Column(Text)
    parent_consent = Column(Boolean, default=False)
    withdrawal_date = Column(DateTime, nullable=True)
    
    family = relationship("Family", back_populates="consent_records")
    child = relationship("Child", back_populates="consent_records")

class ActivityLog(Base):
    __tablename__ = "activity_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    family_id = Column(Integer, ForeignKey("families.id"), nullable=False)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    activity_type = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    url = Column(String, nullable=True)
    app_name = Column(String, nullable=True)
    blocked = Column(Boolean, default=False)
    educational_alternative_shown = Column(Boolean, default=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    family = relationship("Family", back_populates="activity_logs")
    child = relationship("Child", back_populates="activity_logs")

class ContentBlock(Base):
    __tablename__ = "content_blocks"
    
    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, nullable=False)
    category = Column(String, nullable=False)
    reason = Column(Text, nullable=False)
    age_restriction = Column(Integer, nullable=False)
    educational_explanation = Column(Text, nullable=False)
    alternatives = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class EducationalProgress(Base):
    __tablename__ = "educational_progress"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    lesson_type = Column(String, nullable=False)
    lesson_title = Column(String, nullable=False)
    completed = Column(Boolean, default=False)
    score = Column(Float, nullable=True)
    time_spent = Column(Integer, nullable=False)
    completed_at = Column(DateTime, nullable=True)
    
    child = relationship("Child", back_populates="educational_progress")

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_type = Column(String, nullable=False)
    user_id = Column(Integer, nullable=False)
    action = Column(String, nullable=False)
    resource = Column(String, nullable=False)
    details = Column(JSON)
    ip_address = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)

class SchoolIntegration(Base):
    __tablename__ = "school_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    school_name = Column(String, nullable=False)
    school_code = Column(String, unique=True, nullable=False)
    contact_email = Column(String, nullable=False)
    educational_policy = Column(Text, nullable=False)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class HospitalIntegration(Base):
    __tablename__ = "hospital_integrations"
    
    id = Column(Integer, primary_key=True, index=True)
    hospital_name = Column(String, nullable=False)
    hospital_code = Column(String, unique=True, nullable=False)
    contact_email = Column(String, nullable=False)
    therapy_focus = Column(Text, nullable=False)
    medical_ethics_compliance = Column(Boolean, default=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class MobileProfile(Base):
    __tablename__ = "mobile_profiles"
    
    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, ForeignKey("children.id"), nullable=False)
    device_id = Column(String, nullable=False)
    device_type = Column(String, nullable=False)
    profile_config = Column(JSON, nullable=False)
    download_token = Column(String, unique=True, nullable=False)
    downloaded_at = Column(DateTime, nullable=True)
    activated_at = Column(DateTime, nullable=True)
    last_sync = Column(DateTime, nullable=True)
    active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    child = relationship("Child", back_populates="mobile_profiles")
