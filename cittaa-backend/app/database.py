from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
import redis.asyncio as redis
from .config import settings

class Database:
    def __init__(self):
        self.client = None
        self.database = None
        self.redis_client = None

db = Database()

async def connect_to_mongo():
    """Create database connection"""
    db.client = AsyncIOMotorClient(settings.mongodb_url)
    db.database = db.client[settings.database_name]
    
async def close_mongo_connection():
    """Close database connection"""
    if db.client:
        db.client.close()

async def connect_to_redis():
    """Create Redis connection"""
    db.redis_client = redis.from_url(settings.redis_url)

async def close_redis_connection():
    """Close Redis connection"""
    if db.redis_client:
        await db.redis_client.close()

def get_database():
    return db.database

def get_redis():
    return db.redis_client
