"""
Role schemas for CITTAA Escalation Engine
"""

from pydantic import BaseModel
from typing import Optional, Dict, List, Any
from uuid import UUID
from datetime import datetime


class RoleCreate(BaseModel):
    """Schema for creating a new role"""
    name: str
    display_name: str
    description: Optional[str] = None
    permissions: Dict[str, List[str]] = {}


class RoleUpdate(BaseModel):
    """Schema for updating a role"""
    display_name: Optional[str] = None
    description: Optional[str] = None
    permissions: Optional[Dict[str, List[str]]] = None
    is_active: Optional[bool] = None


class RoleResponse(BaseModel):
    """Schema for role response"""
    role_id: UUID
    name: str
    display_name: str
    description: Optional[str] = None
    permissions: Dict[str, List[str]]
    is_system_role: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserRoleChange(BaseModel):
    """Schema for changing a user's role"""
    role: str
