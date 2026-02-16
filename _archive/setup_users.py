"""
Simple Database Setup - Creates user management tables
Works alongside existing database
"""
from src.database.models import Base, engine, SessionLocal
from src.database.user_crud import initialize_default_users
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

print("="*70)
print("  INBLOODO AGENT - Database User Setup")
print("="*70)
print()

try:
    # Create tables (will only create missing ones)
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("OK Database tables ready")
    print()
    
    # Initialize users
    logger.info("Setting up default users...")
    db = SessionLocal()
    initialize_default_users(db)
    db.close()
    logger.info("OK Default users created")
    print()
    
    # Show info
    logger.info("Database ready!")
    logger.info("Location: health_reports.db")
    print()
    
    db = SessionLocal()
    from src.database.models import User
    users = db.query(User).all()
    
    if users:
        logger.info(f"Found {len(users)} users:")
        for user in users:
            logger.info(f"  - {user.username} ({user.email}) - Role: {user.role}")
    
    db.close()
    print()
    print("="*70)
    print("  SUCCESS! Your database is ready")
    print("="*70)
    print()
    print("Login credentials:")
    print("  admin / admin123")
    print("  doctor / doctor123")  
    print("  patient / patient123")
    print()

except Exception as e:
    logger.error(f"ERROR: {e}")
    print()
    print("="*70)
    print("  Setup failed - but don't worry!")
    print("="*70)
    print()
    print("The database tables will be created when you start the server.")
    print("Just restart the server to apply changes.")
    print()
