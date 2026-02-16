import sys
import os
import json
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker

# Add src to path
sys.path.append(os.getcwd())

from src.database.models import Report, Base

DATABASE_URL = "sqlite:///health_reports.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def verify():
    print(f"Verifying database: {DATABASE_URL}")
    
    # Check schema
    inspector = inspect(engine)
    columns = [c['name'] for c in inspector.get_columns("reports")]
    print(f"Columns in 'reports': {columns}")
    
    if "full_results" not in columns:
        print("CRITICAL: full_results column is missing!")
    else:
        print("SUCCESS: full_results column exists.")

    # Try manual insert
    db = SessionLocal()
    try:
        test_report = Report(
            filename="diag_test.pdf",
            parameters="{}",
            precautions="[]",
            description="Diagnostic test",
            full_results=json.dumps({"test": "data"})
        )
        db.add(test_report)
        db.commit()
        db.refresh(test_report)
        print(f"INSERT SUCCESS: New Report ID: {test_report.id}")
        
        # Verify query
        r = db.query(Report).filter(Report.id == test_report.id).first()
        print(f"QUERY SUCCESS: Found report with ID {r.id}, full_results: {bool(r.full_results)}")
        
    except Exception as e:
        print(f"INSERT FAILED: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    verify()
