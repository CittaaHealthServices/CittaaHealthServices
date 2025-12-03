"""
Database configuration and session management
With MongoDB Atlas for permanent data persistence
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import urllib.parse

# SQLAlchemy setup (SQLite for local operations)
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./vocalysis.db")

# Handle SQLite connection args
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# MongoDB Atlas configuration for permanent storage
MONGODB_URI = os.getenv("MONGODB_URI", "")
mongo_client = None
mongo_db = None

def get_mongo_client():
    """Get MongoDB client (lazy initialization)"""
    global mongo_client, mongo_db
    if mongo_client is None and MONGODB_URI:
        try:
            from pymongo import MongoClient
            mongo_client = MongoClient(MONGODB_URI)
            mongo_db = mongo_client.vocalysis
            print("MongoDB Atlas connected successfully")
        except Exception as e:
            print(f"MongoDB connection failed: {e}")
            mongo_client = None
            mongo_db = None
    return mongo_db

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def sync_user_to_mongodb(user_dict):
    """Sync a user record to MongoDB for permanent storage"""
    db = get_mongo_client()
    if db is not None:
        try:
            db.users.update_one(
                {"id": user_dict["id"]},
                {"$set": user_dict},
                upsert=True
            )
        except Exception as e:
            print(f"Error syncing user to MongoDB: {e}")

def sync_prediction_to_mongodb(prediction_dict):
    """Sync a prediction record to MongoDB for permanent storage"""
    db = get_mongo_client()
    if db is not None:
        try:
            db.predictions.update_one(
                {"id": prediction_dict["id"]},
                {"$set": prediction_dict},
                upsert=True
            )
        except Exception as e:
            print(f"Error syncing prediction to MongoDB: {e}")

def restore_from_mongodb():
    """Restore data from MongoDB to SQLite on startup"""
    db = get_mongo_client()
    if db is None:
        print("MongoDB not configured, skipping restore")
        return
    
    from app.models.user import User
    from app.models.prediction import Prediction
    
    session = SessionLocal()
    try:
        # Restore users
        users_restored = 0
        for user_doc in db.users.find():
            existing = session.query(User).filter(User.id == user_doc.get("id")).first()
            if not existing:
                # Remove MongoDB _id field
                user_doc.pop("_id", None)
                user = User(**user_doc)
                session.add(user)
                users_restored += 1
        
        # Restore predictions
        predictions_restored = 0
        for pred_doc in db.predictions.find():
            existing = session.query(Prediction).filter(Prediction.id == pred_doc.get("id")).first()
            if not existing:
                pred_doc.pop("_id", None)
                # Handle JSON fields
                if "voice_features" in pred_doc and isinstance(pred_doc["voice_features"], dict):
                    import json
                    pred_doc["voice_features"] = json.dumps(pred_doc["voice_features"])
                if "recommendations" in pred_doc and isinstance(pred_doc["recommendations"], list):
                    import json
                    pred_doc["recommendations"] = json.dumps(pred_doc["recommendations"])
                prediction = Prediction(**pred_doc)
                session.add(prediction)
                predictions_restored += 1
        
        session.commit()
        print(f"Restored from MongoDB: {users_restored} users, {predictions_restored} predictions")
    except Exception as e:
        print(f"Error restoring from MongoDB: {e}")
        session.rollback()
    finally:
        session.close()

def init_db():
    """Initialize database tables and restore from MongoDB"""
    from app.models.user import User
    from app.models.voice_sample import VoiceSample
    from app.models.prediction import Prediction
    from app.models.clinical_assessment import ClinicalAssessment
    
    Base.metadata.create_all(bind=engine)
    print("Database tables created successfully")
    
    # Restore data from MongoDB if available
    restore_from_mongodb()
