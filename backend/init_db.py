"""
Database initialization script
Run this to create all tables in the database
"""
from app.models.database import Base, engine
from app.models.report import BloodReport, UserContext
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Create all database tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("✅ Database tables created successfully!")

if __name__ == "__main__":
    init_db()
