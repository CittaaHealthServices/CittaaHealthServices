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
    collections = ['users', 'voice_samples', 'predictions', 'clinical_assessments', 'audit_logs']
    existing_collections = db.list_collection_names()
    
    for collection in collections:
        if collection not in existing_collections:
            db.create_collection(collection)
            print(f"Created collection: {collection}")
    
    # Create indexes for better performance
    # Users collection
    db.users.create_index("email", unique=True)
    db.users.create_index("role")
    
    # Voice samples collection
    db.voice_samples.create_index("user_id")
    db.voice_samples.create_index("created_at")
    
    # Predictions collection
    db.predictions.create_index("user_id")
    db.predictions.create_index("voice_sample_id")
    db.predictions.create_index("predicted_at")
    
    # Clinical assessments collection
    db.clinical_assessments.create_index("patient_id")
    db.clinical_assessments.create_index("psychologist_id")
    
    # Audit logs collection
    db.audit_logs.create_index("user_id")
    db.audit_logs.create_index("timestamp")
    
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
