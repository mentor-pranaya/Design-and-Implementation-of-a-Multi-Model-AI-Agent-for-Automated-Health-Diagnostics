from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import Report, Base  # Assuming Base is defined in models.py
from .crud import create_report, get_reports, get_report, update_report, delete_report

# Database setup (adjust path as needed)
DATABASE_URL = "sqlite:///./test.db"  # Use SQLite for testing
engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def test_crud():
    db = SessionLocal()
    try:
        # Test create
        report = create_report(db, "test.pdf", {"param1": "value1"}, ["precaution1"], "Test description")
        print(f"Created: {report.id}")
        
        # Test get all
        reports = get_reports(db)
        print(f"Reports: {len(reports)}")
        
        # Test get by ID
        fetched = get_report(db, report.id)
        print(f"Fetched: {fetched.filename}")
        
        # Test update
        updated = update_report(db, report.id, description="Updated description")
        print(f"Updated: {updated.description}")
        
        # Test delete
        deleted = delete_report(db, report.id)
        print(f"Deleted: {deleted}")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_crud()
