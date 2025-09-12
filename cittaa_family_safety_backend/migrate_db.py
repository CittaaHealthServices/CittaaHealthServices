from app.database import engine
from app.models import Base

def migrate_database():
    """Create all database tables including the new MobileProfile table"""
    Base.metadata.create_all(bind=engine)
    print("Database migration completed successfully!")

if __name__ == "__main__":
    migrate_database()
