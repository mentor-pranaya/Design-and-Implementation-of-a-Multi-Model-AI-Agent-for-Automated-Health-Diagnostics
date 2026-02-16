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
    for rid in [87, 88, 89, 90, 91]:
        r = db.query(Report).filter(Report.id == rid).first()
        if r:
            print(f"\n=== Report ID {rid} ({r.filename}) ===")
            print(f"Summary: {r.description}")
            if r.full_results:
                fr = json.loads(r.full_results)
                print(f"Orchestrator Status: {fr.get('status')}")
                # Print agent results if they are in full_results
                # Actually they are in 'agent_results' list in AnalysisReport, 
                # but results_for_response might not include them all.
                # Let's check keys
                print(f"Result Keys: {list(fr.keys())}")
                if 'persistence_error' in fr:
                    print(f"PERSISTENCE ERROR: {fr['persistence_error']}")
        else:
            print(f"Report {rid} not found")
    db.close()

if __name__ == "__main__":
    check_reports()
