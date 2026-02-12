import os
import sys
from dotenv import load_dotenv

load_dotenv()

import logging
import json
import time
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src.database.models import SessionLocal, Report
from src.input_parser.pdf_parser import extract_text_from_pdf
from src.input_parser.image_parser import extract_text_with_fallback
from src.extraction.parameter_extractor import extract_parameters_from_text
from src.extraction.csv_parameter_mapper import extract_parameters_from_csv
from src.database.crud import create_report, get_reports
from src.auth import api_key_required
from src.agent.agent_orchestrator import MultiAgentOrchestrator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BloodReportData(BaseModel):
    """
    Pydantic model for blood report data input.
    Accepts any key-value pairs where values are numbers.
    """
    class Config:
        extra = "allow"  # Allow extra fields


app = FastAPI(
    title="INBLOODO AGENT - AI Health Diagnostics",
    description="Advanced AI-powered analysis of blood reports with instant recommendations",
    version="2.0.0",
    docs_url="/docs" if os.getenv("ENVIRONMENT") != "production" else None,
    redoc_url="/redoc" if os.getenv("ENVIRONMENT") != "production" else None
)
app.start_time = time.time()

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


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/health")
async def health_check():
    """Health check endpoint for monitoring"""
    try:
        from sqlalchemy import text
        # Test database connection
        db = SessionLocal()
        db.execute(text("SELECT 1"))
        db.close()
        
        return JSONResponse({
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat(),
            "version": "2.0.0",
            "service": "INBLOODO AGENT"
        })
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "timestamp": datetime.utcnow().isoformat(),
                "error": str(e)
            }
        )


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Serve the main web interface for blood report analysis.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/api/telemetry")
async def get_telemetry(api_key: str = Depends(api_key_required)):
    """Advanced real-time telemetry endpoint"""
    try:
        import psutil
        
        # System metrics
        cpu_percent = psutil.cpu_percent()
        memory = psutil.virtual_memory()
        
        from src.llm import get_multi_llm_service
        llm_service = get_multi_llm_service()
        llm_info = llm_service.get_provider_info()
        
        uptime = time.time() - getattr(app, "start_time", time.time())
        
        return {
            "status": "operational",
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "uptime": uptime
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
        reports = db.query(Report).order_by(Report.created_at.desc()).limit(limit).all()
        
        trend_data = []
        for r in reversed(reports):
            try:
                params = json.loads(r.parameters)
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
    """Aggregate analytics across all reports"""
    try:
        total_reports = db.query(Report).count()
        
        return {
            "total_reports_analyzed": total_reports,
            "risk_distribution": {
                "low": db.query(Report).filter(Report.description.contains("Risk Level: Low")).count(),
                "moderate": db.query(Report).filter(Report.description.contains("Risk Level: Moderate")).count(),
                "high": db.query(Report).filter(Report.description.contains("Risk Level: High")).count()
            },
            "system_efficiency": {
                "instant_matches": 0, # Placeholders for base API
                "deep_analyses": total_reports
            }
        }
    except Exception as e:
        logger.exception("Summary analytics failed")
        raise HTTPException(500, str(e))


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """
    Serve the login page with social authentication options.
    """
    return templates.TemplateResponse("login_with_social.html", {"request": request})


class LoginRequest(BaseModel):
    """Login request model"""
    username: str
    password: str


@app.post("/api/login/")
async def api_login(data: LoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate user with username/password using database.
    Returns access token on successful authentication.
    """
    from src.auth import API_KEY
    from src.database.user_crud import authenticate_user, get_user_by_username
    import jwt
    from datetime import datetime, timedelta
    
    # Try database authentication first
    try:
        user = authenticate_user(db, data.username, data.password)
        if user:
            # Create JWT token with user info
            token_data = {
                "sub": str(user.id),
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "exp": datetime.utcnow() + timedelta(hours=24),
                "iat": datetime.utcnow()
            }
            
            # Use JWT secret from environment or API_KEY
            secret_key = os.getenv("JWT_SECRET_KEY", API_KEY)
            access_token = jwt.encode(token_data, secret_key, algorithm="HS256")
            
            logger.info(f"User logged in: {user.username} (database)")
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "user_id": user.id
            }
    except Exception as e:
        logger.debug(f"Database authentication failed: {e}")
    
    # Fallback to hardcoded credentials for backward compatibility
    test_users = {
        "admin": {"password": "secret", "role": "admin"},
        "test": {"password": "secret", "role": "patient"}
    }
    
    if data.username in test_users:
        user_data = test_users[data.username]
        if data.password == user_data["password"]:
            logger.info(f"User logged in: {data.username} (fallback)")
            # Return stable API_KEY for session
            return {
                "access_token": API_KEY,
                "token_type": "bearer",
                "username": data.username,
                "role": user_data["role"]
            }
    
    # Authentication failed
    logger.warning(f"Failed login attempt: {data.username}")
    raise HTTPException(status_code=401, detail="Invalid credentials")


@app.post("/analyze-report/")
async def analyze_report(
    request: Request,
    db: Session = Depends(get_db),
    api_key: str = Depends(api_key_required),
):
    """
    Analyze blood report from file upload or JSON data.
    Supports PDF, CSV, JSON, and image files.
    """
    start_time = time.time()
    content_type = request.headers.get("content-type", "").lower()

    try:
        if "multipart/form-data" in content_type:
            # Handle file upload
            form = await request.form()
            file = form.get("file")
            if not file:
                raise HTTPException(400, "File required")
            
            logger.info(f"Processing file: {file.filename}")
            
            # File size check
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
                elif filename.endswith('.txt'):
                    content = await file.read()
                    text = content.decode('utf-8')
                    params = extract_parameters_from_text(text)
                else:
                    raise HTTPException(400, "Unsupported file type. Supported: PDF, CSV, JSON, PNG, JPG, TIF, TIFF, BMP, WEBP, TXT")

                filename_for_report = file.filename

            except json.JSONDecodeError:
                raise HTTPException(400, "Invalid JSON file format")
            except Exception as e:
                logger.exception("File processing error")
                raise HTTPException(500, f"File processing error: {str(e)}")

        elif "application/json" in content_type:
            # Handle JSON data directly
            logger.info("Processing JSON data via analyze-report")
            try:
                data = await request.json()
                params = {k.lower(): v for k, v in data.items() if isinstance(v, (int, float))}
                filename_for_report = "json_input"
            except json.JSONDecodeError:
                raise HTTPException(400, "Invalid JSON format")
            except Exception as e:
                logger.exception("JSON processing error")
                raise HTTPException(400, f"JSON processing error: {str(e)}")

        else:
            raise HTTPException(400, "Unsupported content type. Use multipart/form-data for files or application/json for data.")

        if not params:
            raise HTTPException(400, "No valid medical parameters found in the input")

        # Process the parameters
        dict_result: dict = await process_medical_data(params, filename_for_report, db)
        
        p_time: float = float(time.time() - start_time)
        dict_result["processing_time"] = float(f"{p_time:.2f}")
        
        logger.info(f"Analysis completed in {p_time:.2f}s for {filename_for_report}")
        return dict_result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in analyze_report")
        raise HTTPException(500, f"Internal server error: {str(e)}")


async def process_medical_data(params: dict, filename: str, db: Session):
    """
    Process medical parameters using the multi-agent orchestrator.
    
    The workflow includes:
    - Parameter Extraction Agent
    - Interpretation Agent (Model 1)
    - Risk Analysis Agent (Model 2)
    - Prediction Agent (AI)
    - LLM Recommendation Agent (Multiple LLM providers with fallback)
    - Prescription Agent
    - Synthesis Agent
    """
    try:
        from src.llm import get_multi_llm_service
        
        # Initialize the multi-agent orchestrator
        orchestrator = MultiAgentOrchestrator()
        
        # Get multi-LLM service info for response
        llm_service = get_multi_llm_service()
        llm_info = llm_service.get_provider_info()
        
        # Execute the complete multi-agent workflow
        analysis_report = await orchestrator.execute(
            raw_params=params,
            patient_context=None
        )

        # Extract results from the agent analysis
        cleaned_params = analysis_report.extracted_parameters
        interpretations = analysis_report.interpretations
        risks = analysis_report.risks
        ai_prediction = analysis_report.ai_prediction
        recommendations = analysis_report.recommendations
        prescriptions = analysis_report.prescriptions
        synthesis = analysis_report.synthesis

        # Create comprehensive description with AI insights
        description = f"Multi-Agent AI Analysis: {len(cleaned_params)} parameters analyzed. Key findings: {', '.join(interpretations[:3] if interpretations else [])}. AI Risk Assessment: {ai_prediction.get('risk_label', 'moderate')} ({ai_prediction.get('risk_score', 0.5):.1%})."

        # Enhanced risk score combining rule-based and AI
        risk_score = ai_prediction.get('risk_label', 'moderate').replace('_', ' ').title()
        if len([r for r in risks if "high" in r.lower() or "severe" in r.lower()]) > 0:
            risk_score = "High"
        elif len([r for r in risks if "moderate" in r.lower()]) > 0 and ai_prediction.get('risk_score', 0.5) > 0.3:
            risk_score = "Moderate"

        # Persist report with error handling
        try:
            report_content = f"{description} Risk Level: {risk_score}. Findings: {', '.join(interpretations)}. Risks: {', '.join(risks)}."
            create_report(db, filename, cleaned_params, recommendations, report_content)
        except Exception as e:
            logger.error(f"Report persistence failed: {str(e)}")
            # Continue without failing the entire request

        # Build response with agent execution details and LLM info
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
                "total_available": llm_info.get("total_available"),
                "fallback_enabled": llm_info.get("fallback_enabled")
            },
            "agent_execution": {
                "total_agents": len(analysis_report.agent_results),
                "successful_agents": len([r for r in analysis_report.agent_results if r.success]),
                "agents": [
                    {
                        "name": r.agent_name,
                        "status": "success" if r.success else "failed",
                        "execution_time": r.execution_time,
                        "error": r.error
                    }
                    for r in analysis_report.agent_results
                ]
            }
        }

    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(400, f"Invalid input data: {str(e)}")
    except Exception as e:
        logger.exception("Unexpected processing error")
        raise HTTPException(500, f"Internal processing error: {str(e)}")


@app.post("/analyze-json/")
async def analyze_json_report(
    data: dict,
    db: Session = Depends(get_db),
    api_key: str = Depends(api_key_required),
):
    """
    Analyze blood report data sent as JSON directly.
    Alternative to file upload for programmatic access.
    """
    start_time = time.time()
    logger.info("Processing JSON data directly")

    try:
        # Extract parameters from JSON data
        params = {k.lower(): v for k, v in data.items() if isinstance(v, (int, float))}

        if not params:
            raise HTTPException(400, "No valid medical parameters found in JSON data")

        json_result: dict = await process_medical_data(params, "json_input", db)
        
        j_time: float = float(time.time() - start_time)
        json_result["processing_time"] = float(f"{j_time:.2f}")
        
        logger.info(f"JSON analysis completed in {j_time:.2f}s")
        return json_result

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error in analyze_json_report")
        raise HTTPException(500, f"Internal server error: {str(e)}")


@app.get("/reports/")
def read_reports(
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db), 
    api_key: str = Depends(api_key_required)
):
    """Get list of analyzed reports"""
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
async def api_status():
    """API status endpoint"""
    return {
        "service": "INBLOODO AGENT",
        "status": "operational",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }


def setup_llm_configuration():
    """Interactive setup for multi-LLM configuration."""
    print("\n" + "="*60)
    print("INBLOODO AGENT - Multi-LLM Configuration Setup")
    print("="*60 + "\n")
    
    env_path = ".env"
    
    # Check if .env exists
    if os.path.exists(env_path):
        print("✓ Found existing .env file")
    else:
        print("✗ No .env file found. Creating one...")
        with open(env_path, "w") as f:
            f.write("# Auto-generated by setup script\n")
    
    # Check current configuration
    env_content = {}
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    env_content[key.strip()] = value.strip()
    
    # Define providers
    providers = {
        "gemini": {
            "name": "Google Gemini",
            "key": "GEMINI_API_KEY",
            "url": "https://aistudio.google.com/app/apikey",
            "status": "GEMINI_API_KEY" in env_content
        },
        "openai": {
            "name": "OpenAI GPT",
            "key": "OPENAI_API_KEY",
            "url": "https://platform.openai.com/api-keys",
            "status": "OPENAI_API_KEY" in env_content
        },
        "claude": {
            "name": "Anthropic Claude",
            "key": "ANTHROPIC_API_KEY",
            "url": "https://console.anthropic.com",
            "status": "ANTHROPIC_API_KEY" in env_content
        }
    }
    
    print("\n" + "-"*60)
    print("Available LLM Providers:")
    print("-"*60)
    for i, (provider_id, info) in enumerate(providers.items(), 1):
        status = "✓ Configured" if info["status"] else "✗ Not configured"
        print(f"{i}. {info['name']:<25} [{status}]")
    
    print("\n" + "-"*60)
    print("Configuration Steps:")
    print("-"*60)
    
    # Get selection
    selection = input("\nWhich provider would you like to configure? (1-3 or 'all'): ").strip().lower()
    
    providers_to_configure = []
    if selection == "all":
        providers_to_configure = list(providers.keys())
    elif selection in ["1", "2", "3"]:
        idx = int(selection) - 1
        providers_to_configure = [list(providers.keys())[idx]]
    else:
        print("Invalid selection")
        sys.exit(1)
    
    api_keys = {}
    for provider_id in providers_to_configure:
        provider = providers[provider_id]
        print(f"\n🔑 {provider['name']}")
        print(f"   Get your API key from: {provider['url']}")
        print(f"   Environment variable: {provider['key']}")
        
        api_key = input(f"\n   Enter your {provider['name']} API key (or press Enter to skip): ").strip()
        
        if api_key:
            print(f"   ✓ API key saved")
            api_keys[provider['key']] = api_key
        else:
            print(f"   ⊘ Skipped")
    
    if not api_keys:
        print("\nNo API keys provided. Exiting.")
        sys.exit(0)
    
    # Ask for primary provider
    if len(api_keys) > 1:
        print("\n" + "-"*60)
        print("Select Primary LLM Provider:")
        print("-"*60)
        
        keys_list = list(api_keys.keys())
        for i, key in enumerate(keys_list, 1):
            provider_name = next(p["name"] for p in providers.values() if p["key"] == key)
            print(f"{i}. {provider_name}")
        
        try:
            choice = int(input("\nEnter your choice (1 or higher): ")) - 1
            primary_key = keys_list[choice]
            primary_provider = next(k for k, v in providers.items() if v["key"] == primary_key)
        except (ValueError, IndexError):
            print(f"Using default: Gemini")
            primary_provider = "gemini"
    else:
        primary_provider = list(providers.keys())[
            [p["key"] for p in providers.values()].index(list(api_keys.keys())[0])
        ]
    
    # Update .env file
    print("\n" + "-"*60)
    print("Updating .env file...")
    print("-"*60)
    
    env_lines = []
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            env_lines = f.readlines()
    
    # Update existing entries or add new ones
    for key, value in api_keys.items():
        found = False
        for i, line in enumerate(env_lines):
            if line.startswith(f"{key}="):
                found = True
                env_lines[i] = f"{key}={value}\n"
                break
        if not found:
            env_lines.append(f"{key}={value}\n")
    
    # Update LLM_PROVIDER
    primary_uppercase = primary_provider.lower()
    found = False
    for i, line in enumerate(env_lines):
        if line.startswith("LLM_PROVIDER="):
            found = True
            env_lines[i] = f"LLM_PROVIDER={primary_uppercase}\n"
            break
    if not found:
        env_lines.insert(0, f"LLM_PROVIDER={primary_uppercase}\n")
    
    # Write back
    with open(env_path, "w") as f:
        f.writelines(env_lines)
    
    print(f"✓ Updated {env_path}")
    print(f"✓ Primary provider: {providers[primary_provider]['name']}")
    print(f"✓ Added {len(api_keys)} API key(s)")
    
    print("\n" + "="*60)
    print("Configuration Summary")
    print("="*60)
    print(f"Primary Provider: {providers[primary_provider]['name']}")
    print(f"Fallback Providers: All configured providers will be automatically used as fallback")
    print(f"\nYour .env file has been updated!")
    
    print("\nNext steps:")
    print("1. If you haven't installed optional packages, run:")
    if provider_id != "gemini":
        if provider_id == "openai":
            print("   pip install openai")
        elif provider_id == "claude":
            print("   pip install anthropic")
    
    print("\n2. Start the application:")
    print("   python -m uvicorn src.api:app --reload")
    print("\n3. Test with:")
    print("   curl -X POST 'http://localhost:8000/analyze-report/' \\")
    print("   -H 'X-API-Key: your-api-key' \\")
    print("        -F 'file=@blood_report.pdf'")
    print("\n" + "="*60 + "\n")


if __name__ == "__main__":
    try:
        setup_llm_configuration()
    except KeyboardInterrupt:
        print("\n\nSetup cancelled.")
        sys.exit(0)
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
