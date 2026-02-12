from sqlalchemy.orm import Session
from .models import Report
import json
from typing import Optional, Dict, List

def create_report(db: Session, filename: str, params: dict, precautions: list, description: str):
    db_report = Report(
        filename=filename,
        parameters=json.dumps(params),
        precautions=json.dumps(precautions),
        description=description
    )
    db.add(db_report)
    db.commit()
    db.refresh(db_report)
    return db_report

def get_reports(db: Session, skip: int = 0, limit: int = 10):
    return db.query(Report).offset(skip).limit(limit).all()

def get_report(db: Session, report_id: int) -> Optional[Report]:
    return db.query(Report).filter(Report.id == report_id).first()

def update_report(db: Session, report_id: int, filename: Optional[str] = None, params: Optional[Dict] = None, precautions: Optional[List] = None, description: Optional[str] = None) -> Optional[Report]:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise ValueError(f"Report with id {report_id} not found")
    if filename:
        report.filename = filename
    if params is not None and params:  # Only update if params is provided and not empty
        report.parameters = json.dumps(params)
    if precautions is not None and precautions:  # Only update if precautions is provided and not empty
        report.precautions = json.dumps(precautions)
    if description:
        report.description = description
    db.commit()
    db.refresh(report)
    return report

def delete_report(db: Session, report_id: int) -> bool:
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise ValueError(f"Report with id {report_id} not found")
    db.delete(report)
    db.commit()
    return True