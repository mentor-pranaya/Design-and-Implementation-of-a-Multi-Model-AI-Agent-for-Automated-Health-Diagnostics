from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from typing import Optional
import logging
import json
import aiofiles
from pathlib import Path
from datetime import datetime
from app.models.database import get_db
from app.models.report import BloodReport, ReportStatus as DBReportStatus
from app.schemas.report import (
    ReportUploadResponse,
    ReportAnalysisResponse,
    UserContextInput,
    ReportStatus
)
from app.services.orchestrator import processing_pipeline
from app.core.config import settings

router = APIRouter(prefix="/reports", tags=["reports"])
logger = logging.getLogger(__name__)

@router.post("/upload", response_model=ReportUploadResponse)
async def upload_report(
    file: UploadFile = File(...),
    user_context: Optional[str] = Form(None),  # JSON string
    age: Optional[int] = Form(None),
    gender: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    """
    Upload a blood report for analysis
    
    Supports: PDF, JPEG, PNG, JSON formats
    """
    try:
        # Validate file extension
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in ['.pdf', '.json', '.jpg', '.jpeg', '.png']:
            raise HTTPException(status_code=400, detail=f"Unsupported file format: {file_ext}")
        
        # Save uploaded file
        upload_dir = Path("data/uploads")
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safe_filename = f"{timestamp}_{file.filename}"
        file_path = upload_dir / safe_filename
        
        async with aiofiles.open(file_path, 'wb') as f:
            content = await file.read()
            await f.write(content)
        
        # Create database record
        report = BloodReport(
            filename=file.filename,
            file_type=file_ext[1:],  # Remove dot
            file_path=str(file_path),
            status=DBReportStatus.PENDING
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        # Parse user context
        user_ctx = None
        if user_context:
            try:
                user_ctx = json.loads(user_context)
            except json.JSONDecodeError:
                pass
        elif age or gender:
            user_ctx = {"age": age, "gender": gender}
        
        # Process report asynchronously
        report.status = DBReportStatus.PROCESSING
        db.commit()
        
        try:
            result = await processing_pipeline.process_report(str(file_path), user_ctx)
            
            if result["status"] == "completed":
                # Update report with results
                report.status = DBReportStatus.COMPLETED
                report.extracted_parameters = result.get("extracted_parameters")
                report.validated_parameters = result.get("validated_parameters")
                report.model_1_results = {
                    "interpretations": result.get("interpretations"),
                    "summary": result.get("summary"),
                    "critical_findings": result.get("critical_findings"),
                    "abnormal_findings": result.get("abnormal_findings")
                }
                report.extraction_confidence = result["confidence_scores"].get("extraction")
                report.analysis_confidence = result["confidence_scores"].get("interpretation")
                report.processed_at = datetime.now()
            else:
                report.status = DBReportStatus.FAILED
                report.error_message = result.get("error", "Unknown error")
                
        except Exception as e:
            logger.error(f"Processing error: {e}", exc_info=True)
            report.status = DBReportStatus.FAILED
            report.error_message = str(e)
        
        db.commit()
        
        return ReportUploadResponse(
            report_id=report.id,
            filename=file.filename,
            status=ReportStatus(report.status.value),
            message=f"Report processed. Status: {report.status.value}"
        )
        
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{report_id}")
async def get_report_analysis(
    report_id: int,
    db: Session = Depends(get_db)
):
    """
    Get analysis results for a specific report
    """
    report = db.query(BloodReport).filter(BloodReport.id == report_id).first()
    
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "report_id": report.id,
        "filename": report.filename,
        "status": report.status.value,
        "file_type": report.file_type,
        "uploaded_at": report.created_at,
        "processed_at": report.processed_at,
        "extraction_confidence": report.extraction_confidence,
        "analysis_confidence": report.analysis_confidence,
        "extracted_parameters": report.extracted_parameters,
        "validated_parameters": report.validated_parameters,
        "interpretations": report.model_1_results.get("interpretations") if report.model_1_results else None,
        "summary": report.model_1_results.get("summary") if report.model_1_results else None,
        "critical_findings": report.model_1_results.get("critical_findings") if report.model_1_results else None,
        "abnormal_findings": report.model_1_results.get("abnormal_findings") if report.model_1_results else None,
        "error_message": report.error_message,
        "disclaimer": settings.DISCLAIMER_TEXT
    }

@router.get("/")
async def list_reports(
    skip: int = 0,
    limit: int = 10,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """
    List all reports (paginated)
    """
    query = db.query(BloodReport)
    
    if status:
        try:
            status_enum = DBReportStatus(status)
            query = query.filter(BloodReport.status == status_enum)
        except ValueError:
            pass
    
    total = query.count()
    reports = query.order_by(BloodReport.created_at.desc()).offset(skip).limit(limit).all()
    
    return {
        "reports": [
            {
                "id": r.id,
                "filename": r.filename,
                "status": r.status.value,
                "uploaded_at": r.created_at,
                "processed_at": r.processed_at
            }
            for r in reports
        ],
        "total": total,
        "skip": skip,
        "limit": limit
    }
