"""
MongoDB configuration and connection management for CITTAA Escalation Engine
Provides permanent data storage for critical escalation and case management data
"""

import os
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional
from datetime import datetime
import uuid

# MongoDB connection string - configure via environment variable
# Format: mongodb+srv://username:password@cluster.mongodb.net/?appName=Cluster0
MONGODB_URL = os.getenv("MONGODB_URL", "mongodb+srv://cittaa_esclation:YniccgNtMKBZdd1r@cluster0.ao9qmj.mongodb.net/?appName=Cluster0")
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "cittaa_escalation")

# Global MongoDB client and database
_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_mongodb_client() -> MongoClient:
    """Get MongoDB client (singleton)"""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URL)
        print(f"Connected to MongoDB Atlas for CITTAA Escalation Engine")
    return _client


def get_mongodb() -> Database:
    """Get MongoDB database instance"""
    global _db
    if _db is None:
        client = get_mongodb_client()
        _db = client[MONGODB_DB_NAME]
        print(f"Using database: {MONGODB_DB_NAME}")
    return _db


def init_mongodb():
    """Initialize MongoDB collections and indexes for Escalation Engine"""
    db = get_mongodb()
    
    # Core collections for the CITTAA Escalation Engine
    collections = [
        'users',                      # User accounts (psychologists, admins, managers)
        'roles',                      # Dynamic role definitions
        'institutions',               # Schools and hospitals
        'students',                   # Student records
        'counseling_sessions',        # Counseling session records
        'daily_reports',              # Daily activity reports
        'weekly_reports',             # Weekly summary reports
        'monthly_reports',            # Monthly metrics tracking
        'escalation_cases',           # Escalation case records
        'escalation_notifications',   # Notification history
        'ai_training_data',           # AI model training data
        'audit_logs',                 # System audit logs for compliance
        'settings'                    # System settings
    ]
    existing_collections = db.list_collection_names()
    
    for collection in collections:
        if collection not in existing_collections:
            db.create_collection(collection)
            print(f"Created collection: {collection}")
    
    # Create indexes for better performance
    
    # Users collection
    db.users.create_index("email", unique=True)
    db.users.create_index("role")
    db.users.create_index("is_active")
    db.users.create_index("institution_id")
    db.users.create_index("created_at")
    
    # Roles collection
    db.roles.create_index("name", unique=True)
    db.roles.create_index("is_system_role")
    db.roles.create_index("is_active")
    
    # Institutions collection
    db.institutions.create_index("name")
    db.institutions.create_index("type")
    db.institutions.create_index("is_active")
    
    # Students collection
    db.students.create_index("institution_id")
    db.students.create_index("assigned_psychologist_id")
    db.students.create_index("risk_level")
    db.students.create_index("is_active")
    db.students.create_index([("institution_id", 1), ("is_active", 1)])
    
    # Counseling sessions collection
    db.counseling_sessions.create_index("student_id")
    db.counseling_sessions.create_index("psychologist_id")
    db.counseling_sessions.create_index("session_date")
    db.counseling_sessions.create_index("escalation_level")
    db.counseling_sessions.create_index([("psychologist_id", 1), ("session_date", -1)])
    
    # Daily reports collection
    db.daily_reports.create_index("psychologist_id")
    db.daily_reports.create_index("report_date")
    db.daily_reports.create_index("institution_id")
    db.daily_reports.create_index([("psychologist_id", 1), ("report_date", -1)])
    
    # Weekly reports collection
    db.weekly_reports.create_index("psychologist_id")
    db.weekly_reports.create_index("week_start_date")
    db.weekly_reports.create_index("institution_id")
    
    # Monthly reports collection
    db.monthly_reports.create_index("psychologist_id")
    db.monthly_reports.create_index("month")
    db.monthly_reports.create_index("year")
    db.monthly_reports.create_index("institution_id")
    
    # Escalation cases collection
    db.escalation_cases.create_index("student_id")
    db.escalation_cases.create_index("psychologist_id")
    db.escalation_cases.create_index("escalation_level")
    db.escalation_cases.create_index("status")
    db.escalation_cases.create_index("created_at")
    db.escalation_cases.create_index([("escalation_level", 1), ("status", 1)])
    
    # Escalation notifications collection
    db.escalation_notifications.create_index("escalation_case_id")
    db.escalation_notifications.create_index("recipient_id")
    db.escalation_notifications.create_index("sent_at")
    db.escalation_notifications.create_index("status")
    
    # AI training data collection
    db.ai_training_data.create_index("session_id")
    db.ai_training_data.create_index("created_at")
    db.ai_training_data.create_index("is_verified")
    
    # Audit logs collection
    db.audit_logs.create_index("user_id")
    db.audit_logs.create_index("action")
    db.audit_logs.create_index("timestamp")
    db.audit_logs.create_index("entity_type")
    db.audit_logs.create_index([("timestamp", -1)])
    
    # Settings collection
    db.settings.create_index("type", unique=True)
    
    print("MongoDB indexes created successfully")
    
    # Seed system roles and demo accounts
    seed_system_roles(db)
    seed_demo_accounts(db)


def seed_system_roles(db: Database):
    """Create system roles in MongoDB"""
    system_roles = [
        {
            "_id": str(uuid.uuid4()),
            "name": "admin",
            "display_name": "Administrator",
            "description": "Full system access with all permissions",
            "permissions": {
                "users": ["create", "read", "update", "delete"],
                "roles": ["create", "read", "update", "delete"],
                "reports": ["create", "read", "update", "delete"],
                "escalations": ["create", "read", "update", "delete"],
                "institutions": ["create", "read", "update", "delete"],
                "students": ["create", "read", "update", "delete"],
                "settings": ["read", "update"]
            },
            "is_system_role": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "psychologist",
            "display_name": "Psychologist",
            "description": "Submit reports and manage assigned students",
            "permissions": {
                "reports": ["create", "read", "update"],
                "escalations": ["create", "read"],
                "students": ["read", "update"],
                "sessions": ["create", "read", "update"]
            },
            "is_system_role": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "school_admin",
            "display_name": "School Administrator",
            "description": "View institution data and reports",
            "permissions": {
                "reports": ["read"],
                "escalations": ["read"],
                "students": ["read"],
                "institutions": ["read"]
            },
            "is_system_role": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "manager",
            "display_name": "Psychology Team Manager",
            "description": "Oversee psychology team and view all data",
            "permissions": {
                "users": ["read"],
                "reports": ["read"],
                "escalations": ["read", "update"],
                "students": ["read"],
                "sessions": ["read"],
                "institutions": ["read"]
            },
            "is_system_role": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        },
        {
            "_id": str(uuid.uuid4()),
            "name": "quality_manager",
            "display_name": "Quality Manager",
            "description": "Quality oversight and compliance monitoring",
            "permissions": {
                "users": ["read"],
                "reports": ["read"],
                "escalations": ["read"],
                "students": ["read"],
                "sessions": ["read"],
                "audit_logs": ["read"]
            },
            "is_system_role": True,
            "is_active": True,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
    ]
    
    for role in system_roles:
        existing = db.roles.find_one({"name": role["name"]})
        if not existing:
            db.roles.insert_one(role)
            print(f"Created system role: {role['name']}")
    
    print("System roles seeded successfully")


def seed_demo_accounts(db: Database):
    """Create demo accounts in MongoDB"""
    import bcrypt
    
    default_password = os.getenv("DEMO_ACCOUNT_PASSWORD")
    if not default_password:
        print("DEMO_ACCOUNT_PASSWORD not set, skipping demo account creation")
        return
    
    demo_accounts = [
        {
            "email": "admin@cittaa.in",
            "password": default_password,
            "full_name": "System Administrator",
            "role": "admin",
            "phone": "+91-9876543210",
            "is_active": True,
            "is_verified": True
        },
        {
            "email": "psychologist@cittaa.in",
            "password": default_password,
            "full_name": "Dr. Priya Sharma",
            "role": "psychologist",
            "phone": "+91-9876543211",
            "rci_registration": "RCI/2024/PSY/12345",
            "is_active": True,
            "is_verified": True
        },
        {
            "email": "manager@cittaa.in",
            "password": default_password,
            "full_name": "Rajesh Kumar",
            "role": "manager",
            "phone": "+91-9876543212",
            "is_active": True,
            "is_verified": True
        },
        {
            "email": "quality@cittaa.in",
            "password": default_password,
            "full_name": "Anita Desai",
            "role": "quality_manager",
            "phone": "+91-9876543213",
            "is_active": True,
            "is_verified": True
        },
        {
            "email": "school@cittaa.in",
            "password": default_password,
            "full_name": "School Admin",
            "role": "school_admin",
            "phone": "+91-9876543214",
            "is_active": True,
            "is_verified": True
        }
    ]
    
    for account in demo_accounts:
        existing = db.users.find_one({"email": account["email"]})
        if not existing:
            password_hash = bcrypt.hashpw(
                account["password"].encode('utf-8'), 
                bcrypt.gensalt()
            ).decode('utf-8')
            
            user_doc = {
                "_id": str(uuid.uuid4()),
                "email": account["email"],
                "password_hash": password_hash,
                "full_name": account["full_name"],
                "role": account["role"],
                "phone": account.get("phone"),
                "rci_registration": account.get("rci_registration"),
                "institution_id": None,
                "is_active": account["is_active"],
                "is_verified": account["is_verified"],
                "language_preference": "en",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            db.users.insert_one(user_doc)
            print(f"Created demo account: {account['email']}")
    
    print("Demo accounts seeded successfully")


def close_mongodb():
    """Close MongoDB connection"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        print("MongoDB connection closed")


def log_audit_event(user_id: str, action: str, entity_type: str, entity_id: str, details: dict = None):
    """Log an audit event to MongoDB"""
    db = get_mongodb()
    audit_doc = {
        "_id": str(uuid.uuid4()),
        "user_id": user_id,
        "action": action,
        "entity_type": entity_type,
        "entity_id": entity_id,
        "details": details or {},
        "timestamp": datetime.utcnow()
    }
    db.audit_logs.insert_one(audit_doc)
