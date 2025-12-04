"""
MongoDB Database Connection and Setup
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config import settings

# Global database client
client: Optional[AsyncIOMotorClient] = None
db = None


async def connect_to_mongodb():
    """Connect to MongoDB"""
    global client, db
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.mongodb_db_name]
    
    # Create indexes for better performance
    await create_indexes()
    
    print(f"Connected to MongoDB: {settings.mongodb_db_name}")


async def close_mongodb_connection():
    """Close MongoDB connection"""
    global client
    if client:
        client.close()
        print("Closed MongoDB connection")


async def create_indexes():
    """Create database indexes for performance"""
    global db
    if db is None:
        return
    
    # Users collection indexes
    await db.users.create_index("email", unique=True)
    await db.users.create_index("role")
    
    # Clinical trial participants indexes
    await db.clinical_trial_participants.create_index("user_id")
    await db.clinical_trial_participants.create_index("approval_status")
    await db.clinical_trial_participants.create_index("assigned_psychologist")
    
    # Voice analysis reports indexes
    await db.voice_analysis_reports.create_index("user_id")
    await db.voice_analysis_reports.create_index("participant_id")
    await db.voice_analysis_reports.create_index("created_at")
    
    # Psychologist assignments indexes
    await db.psychologist_assignments.create_index("psychologist_id")
    await db.psychologist_assignments.create_index("patient_id")
    await db.psychologist_assignments.create_index([("psychologist_id", 1), ("patient_id", 1)], unique=True)
    
    # Coupons indexes
    await db.coupons.create_index("code", unique=True)
    await db.coupons.create_index("status")
    
    # Coupon redemptions indexes
    await db.coupon_redemptions.create_index([("coupon_id", 1), ("user_id", 1)], unique=True)
    
    # Subscriptions indexes
    await db.subscriptions.create_index("user_id")
    await db.subscriptions.create_index("status")
    
    # Payments indexes
    await db.payments.create_index("user_id")
    await db.payments.create_index("order_id", unique=True)
    
    # Audit logs indexes
    await db.audit_logs.create_index("user_id")
    await db.audit_logs.create_index("timestamp")
    await db.audit_logs.create_index("action")


def get_database():
    """Get database instance"""
    return db
