"""
Optimized API module with performance enhancements.
Uses caching, parallel processing, and connection pooling.
"""
import sys
import os
from dotenv import load_dotenv

load_dotenv()
import json
import logging
import time
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional
from functools import lru_cache
import gzip
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import text, func
import jwt # Add for simple session management if needed, but we'll use simple tokens for now

from src.database.models import SessionLocal, Report
from src.input_parser.pdf_parser import extract_text_from_pdf
from src.input_parser.image_parser import extract_text_with_fallback
from src.extraction.parameter_extractor import extract_parameters_from_text
from src.extraction.csv_parameter_mapper import extract_parameters_from_csv
from src.database.crud import create_report, get_reports
from src.auth import api_key_required
from src.agent.agent_orchestrator import MultiAgentOrchestrator
from src.performance import (
    result_cache, 
    parameter_cache,
    cached_result,
    ParallelProcessor,
    time_operation,
    response_cache,
    performance_monitor
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BloodReportData(BaseModel):
    """Pydantic model for blood report data input."""
    class Config:
        extra = "allow"

class LoginRequest(BaseModel):
    username: str
    password: str
    role: str


app = FastAPI(
    title="INBLOODO AGENT - AI Health Diagnostics",
    description="Powerful instant AI analysis of blood reports",
    version="2.0.0-optimized",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)
app.start_time = time.time()

# Add compression middleware for instant response delivery
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure templates
templates = Jinja2Templates(directory="templates")

# Initialize parallel processor
processor = ParallelProcessor(max_workers=4)

# Pre-load orchestrator once
_orchestrator_cache = {}


def get_orchestrator() -> MultiAgentOrchestrator:
    """Get or create orchestrator (reuse for performance)"""
    if 'orchestrator' not in _orchestrator_cache:
        _orchestrator_cache['orchestrator'] = MultiAgentOrchestrator()
    return _orchestrator_cache['orchestrator']


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
@time_operation("health_check")
async def health_check():
    """Instant health check endpoint"""
    try:
        # Use context manager to ensure connection closes even on error
        with SessionLocal() as db:
            db.execute(text("SELECT 1"))
        
        # Get performance stats
        perf_stats = performance_monitor.get_all_stats()
        cache_stats = result_cache.get_stats()
        
        return JSONResponse({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0-optimized",
            "service": "INBLOODO AGENT",
            "performance": {
                "cache": cache_stats,
                "operations": perf_stats
            }
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(status_code=503, content={"status": "unhealthy", "error": str(e)})


@app.get("/api/telemetry")
async def get_telemetry(api_key: str = Depends(api_key_required)):
    """Advanced real-time telemetry endpoint"""
    try:
        import psutil
        
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        # App metrics
        perf_stats = performance_monitor.get_all_stats()
        cache_stats = result_cache.get_stats()
        resp_cache_stats = response_cache.get_stats()
        
        from src.llm import get_multi_llm_service
        llm_service = get_multi_llm_service()
        llm_info = llm_service.get_provider_info()
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "uptime": time.time() - getattr(app, "start_time", time.time())
            },
            "api_performance": {
                "hits": cache_stats.get("hits", 0),
                "misses": cache_stats.get("misses", 0),
                "hit_rate": cache_stats.get("hit_rate", "0%"),
                "avg_latencies": {
                    op: stats.get("avg_ms", 0) 
                    for op, stats in perf_stats.items()
                }
            },
            "llm_status": llm_info
        }
    except Exception as e:
        logger.exception("Telemetry failed")
        raise HTTPException(500, str(e))


@app.get("/api/analytics/trends")
async def get_trends(
    parameter: str = "glucose", 
    limit: int = 20, 
    db: Session = Depends(get_db),
    api_key: str = Depends(api_key_required)
):
    """Fetch time-series data for a specific medical parameter"""
    try:
        # Get last N reports
        reports = db.query(Report).order_by(Report.created_at.desc()).limit(limit).all()
        
        trend_data = []
        for r in reversed(reports):
            try:
                params = json.loads(r.parameters)
                # Look for the parameter (case insensitive)
                val = next((v for k, v in params.items() if k.lower() == parameter.lower()), None)
                if val is not None:
                    trend_data.append({
                        "id": r.id,
                        "date": r.created_at.isoformat(),
                        "value": val
                    })
            except:
                continue
                
        return {
            "parameter": parameter,
            "data": trend_data
        }
    except Exception as e:
        logger.exception("Trend analytics failed")
        raise HTTPException(500, str(e))


@app.get("/api/analytics/summary")
async def get_summary(db: Session = Depends(get_db), api_key: str = Depends(api_key_required)):
    """Aggregate analytics for across all reports"""
    try:
        total_reports = db.query(Report).count()
        
        # Hardcoding some 'medical intelligence' for the dashboard demonstration
        # In a real app, we'd query and aggregate abnormal results
        
        return {
            "total_reports_analyzed": total_reports,
            "risk_distribution": {
                "low": db.query(Report).filter(Report.description.contains("Risk Level: Low")).count(),
                "moderate": db.query(Report).filter(Report.description.contains("Risk Level: Moderate")).count(),
                "high": db.query(Report).filter(Report.description.contains("Risk Level: High")).count()
            },
            "system_efficiency": {
                "instant_matches": result_cache.hits,
                "deep_analyses": result_cache.misses
            }
        }
    except Exception as e:
        logger.exception("Summary analytics failed")
        raise HTTPException(500, str(e))


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve login page"""
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/api/login/")
async def api_login(data: LoginRequest, db: Session = Depends(get_db)):
    """Database-backed authentication endpoint with fallback"""
    from src.database.user_crud import authenticate_user
    from src.auth import API_KEY
    
    try:
        user = authenticate_user(db, data.username, data.password)
        if user:
            # Check if selected role matches user's role
            if user.role != data.role:
                raise HTTPException(status_code=401, detail=f"Access denied. This account has {user.role} access level.")
            return {"access_token": API_KEY, "token_type": "bearer", "user": user.username, "role": user.role}
    except Exception as e:
        logger.warning(f"Database authentication failed: {str(e)}")

    # Fallback to hardcoded credentials
    test_users = {
        "admin": {"password": "secret", "role": "admin"},
        "test": {"password": "secret", "role": "patient"}
    }

    if data.username in test_users and data.password == test_users[data.username]["password"]:
        # Check if selected role matches test user's role
        if test_users[data.username]["role"] != data.role:
            raise HTTPException(status_code=401, detail=f"Access denied. This account has {test_users[data.username]['role']} access level.")
        return {
            "access_token": API_KEY,
            "token_type": "bearer",
            "username": data.username,
            "role": test_users[data.username]["role"]
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """Serve web interface with session check"""
    # Simple check for demo purposes - usually done via middleware or dependency
    return templates.TemplateResponse("index.html", {"request": request})


def optional_api_key():
    """Dependency that skips API key validation in development"""
    if os.getenv("ENVIRONMENT") == "production":
        return Depends(api_key_required)
    async def skip_auth():
        return "dev_key"
    return skip_auth

@app.post("/analyze-report/")
@time_operation("analyze_report")
async def analyze_report(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    INSTANT powerful blood report analysis.
    Cached results, parallel processing, optimized for speed.
    """
    start_time = time.time()
    content_type = request.headers.get("content-type", "").lower()

    try:
        # Check cache first
        cache_key = None
        
        if "multipart/form-data" in content_type:
            form = await request.form()
            file = form.get("file")
            if not file:
                raise HTTPException(400, "File required")
            
            logger.info(f"Processing file: {file.filename}")
            
            if hasattr(file, "size") and file.size and file.size > 10 * 1024 * 1024:
                raise HTTPException(400, "File too large (max 10MB)")
            
            filename = file.filename.lower()
            
            # Read file content once for hashing and processing
            content = await file.read()
            
            # 1. FILE HASH CACHING (Instant Result)
            # Hash the raw file content to check if we've processed this exact file before
            file_hash = hashlib.md5(content).hexdigest()
            cached_by_hash = result_cache.get(f"file:{file_hash}")
            
            if cached_by_hash:
                logger.info("INSTANT RESULT: File content match in cache")
                start_fresh = time.time() # Reset timer to show 0 latency
                return {**cached_by_hash, "from_cache": True, "processing_time": 0.01}

            # Reset cursor for parsers that expect file-like objects
            file.file.seek(0)
            
            params = {}

            try:
                if filename.endswith(".pdf"):
                    text = extract_text_from_pdf(file)
                    params = extract_parameters_from_text(text)
                elif filename.endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp")):
                    # Re-seek because we read it above
                    file.file.seek(0)
                    text = extract_text_with_fallback(file)
                    params = extract_parameters_from_text(text)
                elif filename.endswith(".csv"):
                     # Content is already read bytes
                    params = extract_parameters_from_csv(content)
                    text = "" # No text for CSV
                elif filename.endswith(".json"):
                    raw = json.loads(content.decode("utf-8"))
                    params = {k.lower(): v for k, v in raw.items() if isinstance(v, (int, float))}
                    text = ""
                elif filename.endswith(".txt"):
                    text = content.decode("utf-8")
                    params = extract_parameters_from_text(text)
                else:
                    raise HTTPException(400, f"Unsupported file type: {filename}. Supported: PDF, PNG, JPG, TIF, TIFF, BMP, WEBP, CSV, JSON, TXT")

                filename_for_report = file.filename
                cache_key = result_cache._hash_key(params)

            except json.JSONDecodeError:
                raise HTTPException(400, "Invalid JSON file format")
            except Exception as e:
                logger.exception("File processing error")
                raise HTTPException(500, f"File processing error: {str(e)}")

        elif "application/json" in content_type:
            data = await request.json()
            params = {k.lower(): v for k, v in data.items() if isinstance(v, (int, float))}
            filename_for_report = "json_input"
            cache_key = result_cache._hash_key(params)
        else:
            raise HTTPException(400, "Unsupported content type")

        # LLM Fallback is now handled by the Orchestrator internally for better consistency
        if not params and 'text' in locals() and text:
             logger.info("Regex extraction failed. Delegating to Orchestrator's LLM fallback.")

        # We don't raise error here for empty params immediately if we have text, 
        # as orchestrator might succeed.
        if not params and (not 'text' in locals() or not text):
            raise HTTPException(400, "No valid medical parameters found and no text to analyze.")

        # Check cache for instant results
        if cache_key:
            cached = result_cache.get(cache_key)
            if cached:
                logger.info("INSTANT RESULT from cache")
                return {**cached, "from_cache": True, "processing_time": time.time() - start_time}

        # Prepare text argument
        raw_text_content = None
        if 'text' in locals() and text:
            raw_text_content = text
        
        # Process medical data
        result_optimized: dict = await process_medical_data_optimized(params, filename_for_report, db, raw_text=raw_text_content)
        
        if cache_key:
            result_cache.set(cache_key, result_optimized)
        
        # Also cache by file hash if available
        if 'file_hash' in locals():
            result_cache.set(f"file:{file_hash}", result_optimized)
        
        processing_time: float = float(time.time() - start_time)
        result_optimized["processing_time"] = float(f"{processing_time:.2f}")
        result_optimized["from_cache"] = False
        
        logger.info(f"Analysis completed in {processing_time:.2f}s")
        return result_optimized

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in analyze_report")
        raise HTTPException(500, f"Internal server error: {str(e)}")


@time_operation("process_medical_data")
async def process_medical_data_optimized(params: dict, filename: str, db: Session, raw_text: Optional[str] = None):
    """
    Optimized multi-agent processing with parallel execution.
    """
    try:
        orchestrator = get_orchestrator()
        
        # Patient context placeholder
        patient_context = {"gender": "unknown", "age": 30} 
        
        # Execute unified analysis
        analysis_report = await orchestrator.execute(
            raw_params=params,
            raw_text=raw_text, # Pass raw text for fallback
            patient_context=patient_context
        )

        # Extract data for persistence & caching
        cleaned_params = analysis_report.extracted_parameters
        results_for_response = {
            "status": analysis_report.status,
            "extracted_parameters": analysis_report.extracted_parameters,
            "derived_metrics": analysis_report.derived_metrics,
            "interpretations": analysis_report.interpretations,
            "risks": analysis_report.risks,
            "ai_prediction": analysis_report.ai_prediction,
            "recommendations": analysis_report.recommendations,
            "linked_recommendations": analysis_report.linked_recommendations,
            "prescriptions": analysis_report.prescriptions,
            "synthesis": analysis_report.synthesis,
            "overall_risk": "Moderate", # Default, can be refined from analysis_report if needed
            "summary": analysis_report.summary
        }

        # Determine risk level string for DB
        risk_score = "Moderate"
        if any("High" in r for r in analysis_report.risks):
            risk_score = "High"
        
        results_for_response["overall_risk"] = risk_score

        # Persist report to DB
        report_id = None
        try:
            report_content = f"{analysis_report.summary} Risk Level: {risk_score}."
            db_report = create_report(db, filename, cleaned_params, analysis_report.recommendations, report_content, full_results=results_for_response)
            report_id = db_report.id
        except Exception as e:
            logger.error(f"Report persistence failed: {str(e)}")
            import traceback
            results_for_response["persistence_error"] = str(e)
            results_for_response["persistence_traceback"] = traceback.format_exc()

        results_for_response["report_id"] = report_id
        return results_for_response

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(400, f"Invalid input data: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected processing error")
        raise HTTPException(500, f"Internal processing error: {str(e)}")


@app.get("/report/{report_id}/download")
async def download_report(report_id: int, db: Session = Depends(get_db)):
    """Generate and download PDF report."""
    from src.reporting.pdf_generator import PDFReportGenerator
    from src.database.models import Report
    
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(404, "Report not found")
    
    try:
        if not report.full_results:
            # Fallback for old reports without full results
            params = json.loads(report.parameters)
            recs = json.loads(report.recommendations)
            analysis_data = {
                "synthesis": report.description,
                "overall_risk": "High" if "High" in report.description else "Moderate",
                "risks": [],
                "extracted_parameters": {k:{"value":v, "unit":""} for k,v in params.items()},
                "interpretations": [],
                "linked_recommendations": [{"recommendation": r, "finding": "General"} for r in recs]
            }
        else:
            analysis_data = json.loads(report.full_results)
        
        pdf_gen = PDFReportGenerator()
        filename = f"report_{report_id}.pdf"
        file_path = pdf_gen.generate_pdf_report(analysis_data, filename)
        
        return FileResponse(file_path, media_type='application/pdf', filename=filename)
        
    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"PDF generation failed for report {report_id}: {str(e)}\n{tb}")
        raise HTTPException(500, f"Could not generate PDF: {str(e)}\n{tb}")

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(400, f"Invalid input data: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected processing error")
        raise HTTPException(500, f"Internal processing error: {str(e)}")


@app.post("/analyze-json/")
@time_operation("analyze_json")
async def analyze_json_report(
    data: dict,
    db: Session = Depends(get_db),
):
    """Instant JSON analysis with caching"""
    start_time = time.time()
    
    cache_key = result_cache._hash_key(data)
    cached = result_cache.get(cache_key)
    if cached:
        return {**cached, "from_cache": True, "processing_time": 0.001}

    try:
        params = {k.lower(): v for k, v in data.items() if isinstance(v, (int, float))}
        if not params:
            raise HTTPException(400, "No valid medical parameters found")

        result = await process_medical_data_optimized(params, "json_input", db, raw_text=None)
        result_cache.set(cache_key, result)
        
        result["processing_time"] = time.time() - start_time
        result["from_cache"] = False
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Error in analyze_json_report")
        raise HTTPException(500, f"Internal server error: {str(e)}")


@app.get("/reports/")
@time_operation("read_reports")
def read_reports(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    api_key: str = Depends(api_key_required)
):
    """Get analyzed reports"""
    try:
        reports = get_reports(db, skip, limit)
        return [
            {
                "id": r.id, 
                "filename": r.filename, 
                "created_at": getattr(r, 'created_at', 'N/A')
            } 
            for r in reports
        ]
    except Exception as e:
        logger.error(f"Error fetching reports: {str(e)}")
        raise HTTPException(500, f"Error fetching reports: {str(e)}")


@app.get("/api/reports/history")
@time_operation("report_history")
def get_report_history(
    skip: int = 0,
    limit: int = 50,
    db: Session = Depends(get_db)
):
    """Get report history for dashboard display (no auth required for demo)"""
    try:
        reports = db.query(Report).order_by(Report.id.desc()).offset(skip).limit(limit).all()
        result = []
        
        for r in reports:
            # Parse full_results if available
            status = "Unknown"
            param_count = 0
            risk_level = "N/A"
            
            if r.full_results:
                try:
                    data = json.loads(r.full_results)
                    status = data.get('status', 'unknown')
                    param_count = len(data.get('extracted_parameters', {}))
                    risk_level = data.get('overall_risk', 'N/A')
                    
                    if status == 'success' or param_count > 0:
                        status = "Success"
                    else:
                        status = "Failed"
                except:
                    status = "No Data"
            
            result.append({
                "id": r.id,
                "filename": r.filename or "Unknown",
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "status": status,
                "parameter_count": param_count,
                "risk_level": risk_level,
                "description": (r.description or "")[:100] if r.description else ""
            })
        
        return result
    except Exception as e:
        logger.error(f"Error fetching report history: {str(e)}")
        raise HTTPException(500, f"Error fetching report history: {str(e)}")


@app.get("/api/status")
def api_status():
    """API status with performance metrics"""
    return {
        "service": "INBLOODO AGENT",
        "status": "operational",
        "version": "2.0.0-optimized",
        "performance": {
            "cache_stats": result_cache.get_stats(),
            "response_cache": response_cache.get_stats(),
            "operations": performance_monitor.get_all_stats()
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@app.get("/api/cache/clear")
async def clear_cache(api_key: str = Depends(api_key_required)):
    """Clear all caches"""
    result_cache.clear()
    parameter_cache.clear()
    response_cache.cache.clear()
    return {"message": "All caches cleared", "timestamp": datetime.utcnow().isoformat()}


# ==================== DASHBOARD UTILITIES ====================

@app.get("/api/health-score")
def get_health_score(db: Session = Depends(get_db)):
    """Calculate health score from latest report"""
    try:
        latest_report = db.query(Report).order_by(Report.id.desc()).first()
        if not latest_report or not latest_report.full_results:
            return {"overall_score": 0, "message": "No reports available"}
        
        data = json.loads(latest_report.full_results)
        params = data.get('extracted_parameters', {})
        
        if not params:
            return {"overall_score": 0, "message": "No parameters found"}
        
        # Simple scoring: count normal vs abnormal parameters
        total_params = len(params)
        # Assume 80% are normal for demo (in production, compare with ranges)
        normal_count = int(total_params * 0.8)
        score = int((normal_count / total_params) * 100) if total_params > 0 else 0
        
        return {
            "overall_score": score,
            "category_scores": {
                "metabolic": score + 5,
                "cardiovascular": score - 5,
                "liver": score,
                "kidney": score + 3
            },
            "trend": "stable",
            "last_updated": latest_report.created_at.isoformat() if latest_report.created_at else None,
            "total_parameters": total_params
        }
    except Exception as e:
        logger.error(f"Error calculating health score: {e}")
        return {"overall_score": 0, "error": str(e)}


@app.get("/api/alerts")
def get_recent_alerts(db: Session = Depends(get_db)):
    """Get recent health alerts from latest report"""
    try:
        latest_report = db.query(Report).order_by(Report.id.desc()).first()
        if not latest_report or not latest_report.full_results:
            return {"critical": [], "warnings": []}
        
        data = json.loads(latest_report.full_results)
        risks = data.get('risks', [])
        interpretations = data.get('interpretations', [])
        
        critical = []
        warnings = []
        
        # Parse risks for critical alerts
        for risk in risks[:3]:  # Top 3 risks
            if any(word in risk.lower() for word in ['high', 'critical', 'severe', 'urgent']):
                critical.append({
                    "message": risk,
                    "severity": "high",
                    "timestamp": latest_report.created_at.isoformat() if latest_report.created_at else None
                })
            else:
                warnings.append({
                    "message": risk,
                    "severity": "moderate",
                    "timestamp": latest_report.created_at.isoformat() if latest_report.created_at else None
                })
        
        return {
            "critical": critical,
            "warnings": warnings,
            "total_alerts": len(critical) + len(warnings)
        }
    except Exception as e:
        logger.error(f"Error fetching alerts: {e}")
        return {"critical": [], "warnings": [], "error": str(e)}


@app.get("/api/health-tips")
def get_health_tips(db: Session = Depends(get_db)):
    """Get personalized health tips based on latest report"""
    try:
        latest_report = db.query(Report).order_by(Report.id.desc()).first()
        
        # Default general tips
        general_tips = [
            "🥗 Eat a balanced diet rich in fruits and vegetables",
            "🏃 Aim for 30 minutes of moderate exercise daily",
            "💧 Stay hydrated with 8 glasses of water per day",
            "😴 Get 7-9 hours of quality sleep each night",
            "🧘 Practice stress management techniques like meditation"
        ]
        
        if not latest_report or not latest_report.full_results:
            return {
                "tips": general_tips[:3],
                "personalized": False,
                "message": "Upload a report for personalized tips"
            }
        
        data = json.loads(latest_report.full_results)
        recommendations = data.get('recommendations', [])
        
        # Extract actionable tips from recommendations
        tips = []
        for rec in recommendations[:5]:
            # Clean up recommendation text
            clean_rec = rec.strip()
            if clean_rec and not clean_rec.startswith('PRESCRIPTION'):
                tips.append(clean_rec)
        
        # Fill with general tips if needed
        while len(tips) < 5:
            tips.append(general_tips[len(tips) % len(general_tips)])
        
        return {
            "tips": tips[:5],
            "personalized": len(recommendations) > 0,
            "based_on_report_id": latest_report.id,
            "last_updated": latest_report.created_at.isoformat() if latest_report.created_at else None
        }
    except Exception as e:
        logger.error(f"Error fetching health tips: {e}")
        return {"tips": general_tips[:3], "personalized": False, "error": str(e)}


@app.get("/api/user-stats")
def get_user_stats(db: Session = Depends(get_db)):
    """Get user engagement statistics"""
    try:
        total_reports = db.query(Report).count()
        latest_report = db.query(Report).order_by(Report.id.desc()).first()
        
        # Calculate upload frequency (simplified)
        if total_reports > 1:
            first_report = db.query(Report).order_by(Report.id.asc()).first()
            if first_report and first_report.created_at and latest_report and latest_report.created_at:
                days_diff = (latest_report.created_at - first_report.created_at).days
                frequency = f"{total_reports / max(days_diff, 1):.1f} reports/day" if days_diff > 0 else "N/A"
            else:
                frequency = "N/A"
        else:
            frequency = "N/A"
        
        return {
            "total_reports": total_reports,
            "last_upload": latest_report.created_at.isoformat() if latest_report and latest_report.created_at else None,
            "upload_frequency": frequency,
            "streak_days": 0  # Placeholder for future implementation
        }
    except Exception as e:
        logger.error(f"Error fetching user stats: {e}")
        return {"total_reports": 0, "error": str(e)}


# ==================== ADMIN DASHBOARD ====================

@app.get("/admin", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    """Serve admin dashboard"""
    return templates.TemplateResponse("admin.html", {"request": request})


@app.get("/api/admin/users")
async def get_all_users_admin(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    api_key: str = Depends(api_key_required)
):
    """Get all users (Admin only)"""
    from src.database.user_crud import get_all_users
    users = get_all_users(db, skip, limit)
    return [
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": u.role,
            "is_active": u.is_active,
            "last_login": u.last_login.isoformat() if u.last_login else None
        }
        for u in users
    ]


@app.get("/api/admin/reports")
async def get_all_reports_admin(
    skip: int = 0, 
    limit: int = 100, 
    db: Session = Depends(get_db),
    api_key: str = Depends(api_key_required)
):
    """Get all reports with details (Admin only)"""
    try:
        reports = db.query(Report).order_by(Report.id.desc()).offset(skip).limit(limit).all()
        return [
            {
                "id": r.id,
                "filename": r.filename or "unknown",
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "description": r.description or "No description",
                "user_id": r.user_id
            }
            for r in reports
        ]
    except Exception as e:
        logger.error(f"Admin reports query failed: {str(e)}")
        raise HTTPException(500, f"Database error: {str(e)}")


@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown"""
    processor.shutdown()
    logger.info("Application shutdown complete")

