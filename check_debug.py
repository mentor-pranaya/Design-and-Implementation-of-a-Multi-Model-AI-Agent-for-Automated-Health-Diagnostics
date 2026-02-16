import sys
import os
import json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

sys.path.append(os.getcwd())
from src.database.models import Report

DATABASE_URL = "sqlite:///health_reports.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

def check_reports():
    db = SessionLocal()
    for rid in [84, 85, 86]:
        r = db.query(Report).filter(Report.id == rid).first()
        if r:
            print(f"--- Report ID {rid} ({r.filename}) ---")
            print(f"Status: {r.description[:50]}...")
            print(f"Parameters: {r.parameters}")
            # print(f"Full Results Keys: {list(json.loads(r.full_results).keys()) if r.full_results else 'None'}")
            if r.full_results:
                fr = json.loads(r.full_results)
                print(f"Report Status in Full Results: {fr.get('status')}")
                if 'persistence_error' in fr:
                    print(f"PERSISTENCE ERROR: {fr['persistence_error']}")
        else:
            print(f"Report {rid} not found")
    db.close()

if __name__ == "__main__":
    check_reports()
