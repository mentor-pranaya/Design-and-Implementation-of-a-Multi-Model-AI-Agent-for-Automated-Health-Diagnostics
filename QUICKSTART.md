# FastAPI Backend—Quick Start Guide

## Overview

The FastAPI backend provides a production-ready REST API for your Health Report AI system. It integrates all model layers (1, 2, 3) and the reporting pipeline into a single, scalable endpoint.

## Installation

All dependencies are already installed in your virtual environment.

If you need to reinstall:

```bash
pip install fastapi uvicorn python-multipart
```

## Running the Server

From the project root:

```bash
uvicorn api.main:app --reload
```

**Expected output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete
```

## Accessing the API

### Interactive Docs (Swagger UI)
Open your browser to: **http://127.0.0.1:8000/docs**

This provides an interactive interface where you can:
- Test all endpoints directly
- Upload files
- Fill in form parameters
- See response schemas
- Try different scenarios

### Alternative Docs (ReDoc)
**http://127.0.0.1:8000/redoc**

## Making Your First Request

### Using Swagger UI (Simplest)

1. Start the server: `uvicorn api.main:app --reload`
2. Open: http://127.0.0.1:8000/docs
3. Click "POST /analyze"
4. Click "Try it out"
5. Upload a PDF, JPG, PNG, or JSON file
6. (Optional) Fill in age, gender, medical_history, lifestyle
7. Click "Execute"
8. View the response

### Using curl (Command Line)

```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "file=@report.pdf" \
  -F "age=45" \
  -F "gender=Male" \
  -F "medical_history=Hypertension"
```

### Using Python

```python
import requests

with open("report.pdf", "rb") as f:
    response = requests.post(
        "http://127.0.0.1:8000/analyze",
        files={"file": f},
        data={
            "age": 45,
            "gender": "Male",
            "medical_history": "Hypertension",
            "lifestyle": "Sedentary"
        }
    )
    print(response.json())
```

## API Endpoints

### 1. GET /health
Quick health check.

**Response:**
```json
{
  "status": "ok",
  "service": "Health Report AI Backend"
}
```

---

### 2. POST /analyze ⭐ (Main Endpoint)

Analyze a single medical report.

**Form Parameters:**
- `file` (required): PDF, JPG, PNG, or JSON file
- `age` (optional): Integer
- `gender` (optional): String
- `medical_history` (optional): String
- `lifestyle` (optional): String

**Response:**
```json
{
  "status": "success",
  "message": "Report analyzed successfully",
  "data": {
    "summary": "Elevated risk signals...",
    "key_findings": [...],
    "risks": [...],
    "recommendations": [...],
    "urgency_level": "high",
    "confidence_summary": "...",
    "disclaimer": "This AI-generated report..."
  }
}
```

---

### 3. POST /analyze/batch
Analyze multiple reports in one request.

**Form Parameters:**
- `files` (required): List of files

---

### 4. GET /
API information.

**Response:**
```json
{
  "service": "Health Report AI Backend",
  "version": "1.0.0",
  "docs": "http://127.0.0.1:8000/docs",
  "endpoints": {...}
}
```

---

## File Structure

```
api/
├── __init__.py
└── main.py                 # FastAPI application

reporting/
├── __init__.py
├── finding_synthesizer.py  # Extract findings from models
├── recommendation_engine.py # Generate recommendations
└── report_formatter.py     # Format final output
```

## Error Handling

### Invalid File Format

```json
{
  "status": "error",
  "message": "Invalid file format",
  "error": "Allowed formats: .pdf, .jpg, .jpeg, .png, .json"
}
```

### Missing Required Parameters

```json
{
  "detail": [
    {
      "loc": ["body", "file"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### Processing Error

```json
{
  "status": "error",
  "message": "Report analysis failed",
  "error": "Error details..."
}
```

## Pipeline Flow

The API orchestrates your entire AI system:

```
File Upload
    ↓
Phase 1: Input Handling (OCR, PDF extraction, JSON parsing)
    ↓
Phase 2: Structuring (Normalize values, extract parameters)
    ↓
Model 1: Parameter Interpretation (Identify abnormalities)
    ↓
Model 2: Pattern-Based Risk Analysis (Find risk patterns)
    ↓
Model 3: Contextual Adjustment (Apply user context)
    ↓
Reporting Layer:
  - Synthesize findings (Extract abnormalities + risks)
  - Generate recommendations (Rule-based personalization)
  - Format report (Frontend-ready JSON)
    ↓
JSON Response
```

## Production Deployment

### Running with Gunicorn (Recommended for Production)

```bash
pip install gunicorn
gunicorn api.main:app --workers 4 --worker-class uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
```

### Running on Different Port

```bash
uvicorn api.main:app --port 9000
```

### Running with Custom Host

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000
```

## Testing

Run the API tests:

```bash
pytest tests/test_api.py -v
```

All tests pass and cover:
- Health check endpoint
- Root endpoint
- File validation
- Response structure
- Error handling

## Configuration

- **Upload Directory:** `temp_uploads/` (created automatically)
- **Allowed Formats:** `.pdf`, `.jpg`, `.jpeg`, `.png`, `.json`
- **Temp File Cleanup:** Automatic after processing
- **Timeout:** No hard limit (adjust as needed)

## Environment Variables (Optional)

You can set these for production:

```bash
set WORKERS=4                    # Number of Gunicorn workers
set API_HOST=0.0.0.0             # Bind address
set API_PORT=8000                # Port
set LOG_LEVEL=info               # Logging level
```

## Troubleshooting

### Port Already in Use

```bash
# Find and kill process on port 8000
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Or use a different port
uvicorn api.main:app --port 9000
```

### PaddleOCR Warnings

These are normal deprecation warnings from PyTorch. They don't affect functionality.

### Slow First Request

The first request triggers OCR model loading. This is expected and only happens once per session.

## Integration with Frontend

The API response is production-ready for frontend integration:

```javascript
const response = await fetch('http://127.0.0.1:8000/analyze', {
    method: 'POST',
    body: formData  // Contains file + user context
});

const report = await response.json();

// Access report data
console.log(report.data.summary);
console.log(report.data.risks);
console.log(report.data.recommendations);
console.log(report.data.urgency_level);
```

## Next Steps

1. ✅ Start the API: `uvicorn api.main:app --reload`
2. ✅ Test with Swagger UI: http://127.0.0.1:8000/docs
3. ✅ Upload a sample report
4. ✅ Review the generated report
5. → Deploy to production (see Production Deployment section)
6. → Add authentication (JWT tokens)
7. → Add request logging
8. → Set up monitoring

---

**For more info:** See [API_README.md](API_README.md)
