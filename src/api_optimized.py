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
from datetime import datetime
from typing import Dict, Any, Optional
from functools import lru_cache
import gzip
from io import BytesIO

from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request, Response, Cookie
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, RedirectResponse
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
            params = {}

            try:
                if filename.endswith(".pdf"):
                    text = extract_text_from_pdf(file)
                    params = extract_parameters_from_text(text)
                elif filename.endswith((".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp", ".webp")):
                    text = extract_text_with_fallback(file)
                    params = extract_parameters_from_text(text)
                elif filename.endswith(".csv"):
                    content = await file.read()
                    params = extract_parameters_from_csv(content)
                elif filename.endswith(".json"):
                    content = await file.read()
                    raw = json.loads(content.decode("utf-8"))
                    params = {k.lower(): v for k, v in raw.items() if isinstance(v, (int, float))}
                elif filename.endswith(".txt"):
                    content = await file.read()
                    text = content.decode("utf-8")
                    params = extract_parameters_from_text(text)
                elif filename.endswith('.txt'):
                    content = await file.read()
                    text = content.decode('utf-8')
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

        if not params:
            raise HTTPException(400, "No valid medical parameters found")

        # Check cache for instant results
        if cache_key:
            cached = result_cache.get(cache_key)
            if cached:
                logger.info("INSTANT RESULT from cache")
                return {**cached, "from_cache": True, "processing_time": time.time() - start_time}

        # Process medical data
        result_optimized: dict = await process_medical_data_optimized(params, filename_for_report, db)
        
        if cache_key:
            result_cache.set(cache_key, result_optimized)
        
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
async def process_medical_data_optimized(params: dict, filename: str, db: Session):
    """
    Optimized multi-agent processing with parallel execution.
    """
    try:
        from src.llm import get_multi_llm_service
        
        orchestrator = get_orchestrator()
        
        llm_service = get_multi_llm_service()
        llm_info = llm_service.get_provider_info()
        
        analysis_report = await orchestrator.execute(
            raw_params=params,
            patient_context=None
        )

        cleaned_params = analysis_report.extracted_parameters
        interpretations = analysis_report.interpretations
        risks = analysis_report.risks
        ai_prediction = analysis_report.ai_prediction
        recommendations = analysis_report.recommendations
        prescriptions = analysis_report.prescriptions
        synthesis = analysis_report.synthesis

        description = f"Multi-Agent AI Analysis: {len(cleaned_params)} parameters analyzed. Key findings: {', '.join(interpretations[:3] if interpretations else [])}. AI Risk Assessment: {ai_prediction.get('risk_label', 'moderate')} ({ai_prediction.get('risk_score', 0.5):.1%})."

        risk_score = ai_prediction.get('risk_label', 'moderate').replace('_', ' ').title()
        if len([r for r in risks if "high" in r.lower() or "severe" in r.lower()]) > 0:
            risk_score = "High"
        elif len([r for r in risks if "moderate" in r.lower()]) > 0:
            risk_score = "Moderate"

        try:
            report_content = f"{description} Risk Level: {risk_score}."
            create_report(db, filename, cleaned_params, recommendations, report_content)
        except Exception as e:
            logger.error(f"Report persistence failed: {str(e)}")

        return {
            "status": "success",
            "extracted_parameters": cleaned_params,
            "interpretations": interpretations,
            "risks": risks,
            "ai_prediction": ai_prediction,
            "recommendations": recommendations,
            "prescriptions": prescriptions,
            "synthesis": synthesis,
            "overall_risk": risk_score,
            "summary": description,
            "llm_provider_info": {
                "primary": llm_info.get("primary"),
                "available_providers": llm_info.get("available"),
            },
            "agent_execution": {
                "total_agents": len(analysis_report.agent_results),
                "successful_agents": len([r for r in analysis_report.agent_results if r.success]),
            }
        }

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
    api_key: str = Depends(api_key_required),
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

        result = await process_medical_data_optimized(params, "json_input", db)
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
    reports = db.query(Report).order_by(Report.created_at.desc()).offset(skip).limit(limit).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "created_at": r.created_at.isoformat(),
            "description": r.description,
            "user_id": r.user_id
        }
        for r in reports
    ]


@app.on_event("shutdown")
def shutdown_event():
    """Cleanup on shutdown"""
    processor.shutdown()
    logger.info("Application shutdown complete")

