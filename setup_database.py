"""
Database Setup and Migration Script
Initializes database, creates tables, and sets up default users
"""
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.database.models import Base, engine, SessionLocal, User, Report
from src.database.user_crud import initialize_default_users
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def init_database():
    """Initialize database tables"""
    logger.info("🔧 Initializing database...")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Get database file path
        db_url = os.getenv("DATABASE_URL", "sqlite:///health_reports.db")
        if db_url.startswith("sqlite:///"):
            db_file = db_url.replace("sqlite:///", "")
            logger.info(f"📁 Database location: {os.path.abspath(db_file)}")
        
        return True
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        return False


def setup_default_users():
    """Setup default test users"""
    logger.info("👥 Setting up default users...")
    
    try:
        db = SessionLocal()
        initialize_default_users(db)
        db.close()
        logger.info("✅ Default users setup complete")
        return True
    except Exception as e:
        logger.error(f"❌ User setup failed: {e}")
        return False


def show_database_info():
    """Show database information"""
    logger.info("📊 Database Information:")
    
    try:
        db = SessionLocal()
        
        # Count users
        user_count = db.query(User).count()
        logger.info(f"   Users: {user_count}")
        
        # List users
        if user_count > 0:
            users = db.query(User).all()
            logger.info("   User List:")
            for user in users:
                logger.info(f"      • {user.username} ({user.email}) - Role: {user.role}")
        
        # Count reports
        report_count = db.query(Report).count()
        logger.info(f"   Reports: {report_count}")
        
        db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Failed to show database info: {e}")
        return False


def reset_database():
    """Reset database (DROP all tables and recreate)"""
    logger.warning("⚠️  RESETTING DATABASE - All data will be lost!")
    
    try:
        # Drop all tables
        Base.metadata.drop_all(bind=engine)
        logger.info("✅ All tables dropped")
        
        # Recreate tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Tables recreated")
        
        # Setup default users
        setup_default_users()
        
        return True
    except Exception as e:
        logger.error(f"❌ Database reset failed: {e}")
        return False


def migrate_existing_reports():
    """Migrate existing reports (if any) to work with user system"""
    logger.info("🔄 Checking for existing reports to migrate...")
    
    try:
        db = SessionLocal()
        
        # Get reports without user_id
        orphan_reports = db.query(Report).filter(Report.user_id == None).all()
        
        if orphan_reports:
            logger.info(f"   Found {len(orphan_reports)} reports without user assignment")
            
            # Try to assign to admin user
            admin = db.query(User).filter(User.username == "admin").first()
            if admin:
                for report in orphan_reports:
                    report.user_id = admin.id
                db.commit()
                logger.info(f"✅ Assigned {len(orphan_reports)} reports to admin user")
            else:
                logger.warning("⚠️  No admin user found to assign reports")
        else:
            logger.info("   No orphan reports found")
        
        db.close()
        return True
    except Exception as e:
        logger.error(f"❌ Migration failed: {e}")
        return False


if __name__ == "__main__":
    print("=" * 70)
    print("  INBLOODO AGENT - Database Setup")
    print("=" * 70)
    print()
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "reset":
            print("⚠️  WARNING: This will DELETE ALL DATA!")
            confirm = input("Type 'yes' to confirm: ")
            if confirm.lower() == "yes":
                reset_database()
            else:
                print("❌ Reset cancelled")
        
        elif command == "info":
            show_database_info()
        
        elif command == "migrate":
            migrate_existing_reports()
        
        elif command == "init":
            init_database()
            setup_default_users()
            show_database_info()
        
        else:
            print(f"❌ Unknown command: {command}")
            print()
            print("Available commands:")
            print("  init     - Initialize database and create default users")
            print("  reset    - Reset database (DELETE ALL DATA)")
            print("  info     - Show database information")
            print("  migrate  - Migrate existing reports to user system")
    
    else:
        # Default: Initialize database
        print("No command specified. Running full initialization...")
        print()
        
        if init_database():
            print()
            if setup_default_users():
                print()
                show_database_info()
                print()
                print("=" * 70)
                print("  ✅ Database setup complete!")
                print("=" * 70)
                print()
                print("You can now:")
                print("  1. Start the server: python launch_server.py")
                print("  2. Login at: http://localhost:10000/login")
                print()
                print("Default credentials:")
                print("  • admin / admin123")
                print("  • doctor / doctor123")
                print("  • patient / patient123")
                print()
        else:
            print()
            print("=" * 70)
            print("  ❌ Database setup failed!")
            print("=" * 70)
            sys.exit(1)
