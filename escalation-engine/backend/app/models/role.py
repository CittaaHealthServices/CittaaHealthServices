"""
Role model for CITTAA Escalation Engine
Dynamic role management for production use
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid

from app.models.database import Base


class Role(Base):
    """
    Dynamic role management table
    
    Allows admin to create custom roles with specific permissions
    """
    __tablename__ = "roles"
    
    role_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False, index=True)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    
    permissions = Column(JSON, default=dict)
    
    is_system_role = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_by = Column(UUID(as_uuid=True), nullable=True)


DEFAULT_ROLES = [
    {
        "name": "admin",
        "display_name": "Administrator",
        "description": "Full system access - can manage users, roles, institutions, and all data",
        "permissions": {
            "users": ["create", "read", "update", "delete"],
            "roles": ["create", "read", "update", "delete"],
            "institutions": ["create", "read", "update", "delete"],
            "students": ["create", "read", "update", "delete"],
            "reports": ["create", "read", "update", "delete"],
            "escalations": ["create", "read", "update", "delete"],
            "audit": ["read"],
            "compliance": ["read"],
            "system": ["read", "update"]
        },
        "is_system_role": True
    },
    {
        "name": "psychologist",
        "display_name": "Psychologist",
        "description": "Can submit reports, manage assigned students, and handle escalations",
        "permissions": {
            "students": ["create", "read", "update"],
            "reports": ["create", "read", "update"],
            "escalations": ["create", "read", "update"],
            "sessions": ["create", "read", "update"]
        },
        "is_system_role": True
    },
    {
        "name": "school_admin",
        "display_name": "School Administrator",
        "description": "Can view institution data and reports",
        "permissions": {
            "students": ["read"],
            "reports": ["read"],
            "escalations": ["read"],
            "dashboard": ["read"]
        },
        "is_system_role": True
    },
    {
        "name": "manager",
        "display_name": "Psychology Team Manager",
        "description": "Can view all submitted data, manage psychologists, and oversee operations",
        "permissions": {
            "users": ["read"],
            "students": ["read"],
            "reports": ["read"],
            "escalations": ["read", "update"],
            "sessions": ["read"],
            "dashboard": ["read"],
            "audit": ["read"]
        },
        "is_system_role": True
    },
    {
        "name": "quality_manager",
        "display_name": "Quality Manager",
        "description": "Quality oversight - can view all data, compliance reports, and audit logs",
        "permissions": {
            "users": ["read"],
            "students": ["read"],
            "reports": ["read"],
            "escalations": ["read"],
            "sessions": ["read"],
            "dashboard": ["read"],
            "audit": ["read"],
            "compliance": ["read"]
        },
        "is_system_role": True
    }
]
