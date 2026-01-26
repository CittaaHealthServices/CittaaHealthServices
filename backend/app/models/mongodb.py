"""
MongoDB configuration and connection management for persistent storage
"""

import os
from pymongo import MongoClient
from pymongo.database import Database
from typing import Optional

# MongoDB connection string from environment
# Password VocalysisDB2026 (no special characters)
MONGODB_URL = os.getenv(
    "MONGODB_URL", 
    "mongodb+srv://sairam_db_user:VocalysisDB2026@cluster0.ao9qmj.mongodb.net/vocalysis?retryWrites=true&w=majority"
)
MONGODB_DB_NAME = os.getenv("MONGODB_DB_NAME", "vocalysis")

# Global MongoDB client and database
_client: Optional[MongoClient] = None
_db: Optional[Database] = None


def get_mongodb_client() -> MongoClient:
    """Get MongoDB client (singleton)"""
    global _client
    if _client is None:
        _client = MongoClient(MONGODB_URL)
        print(f"Connected to MongoDB Atlas")
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
    """Initialize MongoDB collections and indexes"""
    db = get_mongodb()
    
    # Create collections if they don't exist
    # Core collections for the Vocalysis healthcare system
    collections = [
        'users',                          # User accounts (patients, psychologists, admins)
        'voice_samples',                  # Voice recordings for analysis
        'predictions',                    # Voice analysis results/predictions
        'clinical_assessments',           # Clinical assessment records
        'clinical_trial_participants',    # Clinical trial participant data
        'psychologist_patient_assignments', # Psychologist-patient relationships
        'audit_logs',                     # System audit logs for compliance
        'settings',                       # System settings (email, etc.)
        'baselines'                       # User baseline data for personalization
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
    db.users.create_index("assigned_psychologist_id")
    db.users.create_index("is_clinical_trial_participant")
    db.users.create_index("trial_status")
    db.users.create_index("created_at")
    
    # Voice samples collection
    db.voice_samples.create_index("user_id")
    db.voice_samples.create_index("created_at")
    db.voice_samples.create_index([("user_id", 1), ("created_at", -1)])
    
    # Predictions collection
    db.predictions.create_index("user_id")
    db.predictions.create_index("voice_sample_id")
    db.predictions.create_index("predicted_at")
    db.predictions.create_index("overall_risk_level")
    db.predictions.create_index([("user_id", 1), ("predicted_at", -1)])
    
    # Clinical assessments collection
    db.clinical_assessments.create_index("patient_id")
    db.clinical_assessments.create_index("psychologist_id")
    db.clinical_assessments.create_index("created_at")
    
    # Clinical trial participants collection
    db.clinical_trial_participants.create_index("user_id", unique=True)
    db.clinical_trial_participants.create_index("approval_status")
    db.clinical_trial_participants.create_index("assigned_psychologist")
    db.clinical_trial_participants.create_index("enrollment_date")
    
    # Psychologist-patient assignments collection
    db.psychologist_patient_assignments.create_index("psychologist_id")
    db.psychologist_patient_assignments.create_index("patient_id")
    db.psychologist_patient_assignments.create_index("status")
    db.psychologist_patient_assignments.create_index([("psychologist_id", 1), ("status", 1)])
    
    # Audit logs collection
    db.audit_logs.create_index("user_id")
    db.audit_logs.create_index("action")
    db.audit_logs.create_index("timestamp")
    db.audit_logs.create_index("entity_type")
    db.audit_logs.create_index([("timestamp", -1)])
    
    # Baselines collection
    db.baselines.create_index("user_id", unique=True)
    db.baselines.create_index("created_at")
    
    # Settings collection
    db.settings.create_index("type", unique=True)
    
    print("MongoDB indexes created successfully")
    
    # Seed demo accounts
    seed_mongodb_demo_accounts(db)


def seed_mongodb_demo_accounts(db: Database):
    """Create demo accounts in MongoDB"""
    import bcrypt
    from datetime import datetime
    import uuid
    
    demo_accounts = [
        {
            "email": "admin@cittaa.in",
            "password": "Admin@123",
            "full_name": "Admin User",
            "role": "super_admin",
            "is_active": True,
            "is_verified": True
        },
        {
            "email": "doctor@cittaa.in",
            "password": "Doctor@123",
            "full_name": "Dr. Psychologist",
            "role": "psychologist",
            "is_active": True,
            "is_verified": True
        },
        {
            "email": "patient@cittaa.in",
            "password": "Patient@123",
            "full_name": "Demo Patient",
            "role": "patient",
            "is_active": True,
            "is_verified": True
        },
        {
            "email": "researcher@cittaa.in",
            "password": "Researcher@123",
            "full_name": "Research User",
            "role": "researcher",
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
                "is_active": account["is_active"],
                "is_verified": account["is_verified"],
                "language_preference": "en",
                "consent_given": True,
                "is_clinical_trial_participant": False,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            db.users.insert_one(user_doc)
            print(f"Created MongoDB demo account: {account['email']}")
    
    print("MongoDB demo accounts seeded successfully")


def close_mongodb():
    """Close MongoDB connection"""
    global _client, _db
    if _client:
        _client.close()
        _client = None
        _db = None
        print("MongoDB connection closed")
