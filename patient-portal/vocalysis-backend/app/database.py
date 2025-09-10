from typing import Dict, List, Any, Optional
from datetime import datetime
import json

class MockCollection:
    def __init__(self, name: str):
        self.name = name
        self.data: List[Dict[str, Any]] = []
        self._init_sample_data()
    
    def _init_sample_data(self):
        if self.name == 'users':
            demo_password_hash = "$2b$12$gF4aAJY8zI05x.oZ4abm1uuvY9cuiwFAlwQnF/zRonaR7hrmbxt7G"
            self.data = [
                {
                    "_id": "user_patient_1",
                    "email": "patient@cittaa.in",
                    "full_name": "Demo Patient",
                    "phone": "+91-9876543210",
                    "role": "patient",
                    "is_active": True,
                    "hashed_password": demo_password_hash,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "_id": "user_doctor_1",
                    "email": "doctor@cittaa.in",
                    "full_name": "Dr. Priya Sharma",
                    "phone": "+91-9876543211",
                    "role": "doctor",
                    "is_active": True,
                    "hashed_password": demo_password_hash,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "_id": "user_doctor_2",
                    "email": "doctor2@cittaa.in",
                    "full_name": "Dr. Rajesh Kumar",
                    "phone": "+91-9876543212",
                    "role": "doctor",
                    "is_active": True,
                    "hashed_password": demo_password_hash,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "_id": "user_admin_1",
                    "email": "admin@cittaa.in",
                    "full_name": "Admin User",
                    "phone": "+91-9876543212",
                    "role": "admin",
                    "is_active": True,
                    "hashed_password": demo_password_hash,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
        elif self.name == 'doctor_profiles':
            self.data = [
                {
                    "_id": "doc1",
                    "user_id": "user_doctor_1",
                    "specialization": "Clinical Psychology",
                    "experience_years": 8,
                    "qualifications": ["PhD in Clinical Psychology", "MD Psychiatry"],
                    "languages": ["English", "Hindi", "Tamil"],
                    "consultation_fee": 1500.0,
                    "available_slots": ["Monday 09:00-17:00", "Wednesday 09:00-17:00", "Friday 09:00-17:00"],
                    "rating": 4.8,
                    "total_reviews": 45,
                    "bio": "Experienced clinical psychologist specializing in anxiety and depression treatment.",
                    "profile_image": "/api/placeholder/150/150",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                },
                {
                    "_id": "doc2", 
                    "user_id": "user_doctor_2",
                    "specialization": "Psychiatry",
                    "experience_years": 12,
                    "qualifications": ["MBBS", "MD Psychiatry"],
                    "languages": ["English", "Hindi", "Bengali"],
                    "consultation_fee": 2000.0,
                    "available_slots": ["Tuesday 10:00-18:00", "Thursday 10:00-18:00", "Saturday 09:00-15:00"],
                    "rating": 4.9,
                    "total_reviews": 78,
                    "bio": "Senior psychiatrist with expertise in mood disorders and cognitive behavioral therapy.",
                    "profile_image": "/api/placeholder/150/150",
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
            ]
    
    def find(self, query: Dict[str, Any] = None):
        if query is None:
            return self.data
        results = []
        for item in self.data:
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                results.append(item)
        return results
    
    def find_one(self, query: Dict[str, Any] = None):
        results = self.find(query)
        return results[0] if results else None
    
    def insert_one(self, document: Dict[str, Any]):
        if '_id' not in document:
            document['_id'] = f"id_{len(self.data)}"
        document['created_at'] = datetime.utcnow().isoformat()
        self.data.append(document)
        return type('InsertResult', (), {'inserted_id': document['_id']})()
    
    def update_one(self, query: Dict[str, Any], update: Dict[str, Any]):
        for item in self.data:
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                if '$set' in update:
                    item.update(update['$set'])
                item['updated_at'] = datetime.utcnow().isoformat()
                return type('UpdateResult', (), {'modified_count': 1})()
        return type('UpdateResult', (), {'modified_count': 0})()
    
    def delete_one(self, query: Dict[str, Any]):
        for i, item in enumerate(self.data):
            match = True
            for key, value in query.items():
                if key not in item or item[key] != value:
                    match = False
                    break
            if match:
                del self.data[i]
                return type('DeleteResult', (), {'deleted_count': 1})()
        return type('DeleteResult', (), {'deleted_count': 0})()
    
    def create_index(self, *args, **kwargs):
        pass

class InMemoryDatabase:
    def __init__(self):
        self.collections = {
            'users': MockCollection('users'),
            'clinical_trial_participants': MockCollection('clinical_trial_participants'),
            'appointments': MockCollection('appointments'),
            'doctor_profiles': MockCollection('doctor_profiles'),
            'messages': MockCollection('messages'),
            'voice_analysis_reports': MockCollection('voice_analysis_reports'),
            'audit_logs': MockCollection('audit_logs')
        }
    
    def __getattr__(self, name):
        if name in self.collections:
            return self.collections[name]
        raise AttributeError(f"Collection '{name}' not found")

class Database:
    _instance: Optional[InMemoryDatabase] = None
    
    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            cls._instance = InMemoryDatabase()
            print("Using in-memory database for development")
        return cls._instance

def get_database():
    return Database.get_instance()

def close_database():
    pass

def init_collections():
    db = get_database()
    for collection_name in ['users', 'clinical_trial_participants', 'appointments', 
                           'doctor_profiles', 'messages', 'voice_analysis_reports', 'audit_logs']:
        collection = getattr(db, collection_name)
        collection.create_index("_id")
