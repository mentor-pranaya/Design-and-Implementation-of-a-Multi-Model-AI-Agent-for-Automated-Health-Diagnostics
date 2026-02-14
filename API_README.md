# Health Report AI Backend API

Production-ready FastAPI backend for the Health Report AI system.

## Quick Start

### Prerequisites

- Python 3.8+
- FastAPI and Uvicorn (already installed in the venv)

### Run the API

From the project root:

```powershell
uvicorn api.main:app --reload
```

Then open your browser to:
- **Interactive Docs (Swagger UI):** http://127.0.0.1:8000/docs
- **Alternative Docs (ReDoc):** http://127.0.0.1:8000/redoc

---

## API Endpoints

### 1. Health Check
**GET** `/health`

Returns the service status.

**Response:**
```json
{
  "status": "ok",
  "service": "Health Report AI Backend"
}
```

---

### 2. Analyze Report (Main Endpoint)
**POST** `/analyze`

Analyze a single medical report.

**Form Parameters:**
- `file` (required): Medical report file (PDF, JPG, PNG, JSON)
- `age` (optional): Patient age (integer)
- `gender` (optional): Patient gender (string)
- `medical_history` (optional): Patient medical history (string)
- `lifestyle` (optional): Patient lifestyle description (string)

**Example using curl:**
```bash
curl -X POST "http://127.0.0.1:8000/analyze" \
  -F "file=@report.pdf" \
  -F "age=45" \
  -F "gender=Male" \
  -F "medical_history=Hypertension" \
  -F "lifestyle=Sedentary"
```

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

### 3. Batch Analysis
**POST** `/analyze/batch`

Analyze multiple reports in batch.

**Form Parameters:**
- `files` (required): List of medical report files

**Example using curl:**
```bash
curl -X POST "http://127.0.0.1:8000/analyze/batch" \
  -F "files=@report1.pdf" \
  -F "files=@report2.pdf"
```

---

### 4. API Info
**GET** `/`

Get API information and available endpoints.

**Response:**
```json
{
  "service": "Health Report AI Backend",
  "version": "1.0.0",
  "docs": "http://127.0.0.1:8000/docs",
  "endpoints": {
    "health": "GET /health",
    "analyze": "POST /analyze",
    "batch_analyze": "POST /analyze/batch"
  }
}
```

---

## Error Handling

### Invalid File Format
**Status:** 400 Bad Request

```json
{
  "status": "error",
  "message": "Request error",
  "error": "Invalid file format. Allowed: .pdf, .jpg, .jpeg, .png, .json"
}
```

### Processing Error
**Status:** 500 Internal Server Error

```json
{
  "status": "error",
  "message": "Report analysis failed",
  "error": "Error details..."
}
```

---

## File Structure

```
api/
├── __init__.py
└── main.py              # FastAPI application
```

---

## Configuration

- **Upload Directory:** `temp_uploads/` (created automatically)
- **Allowed File Formats:** `.pdf`, `.jpg`, `.jpeg`, `.png`, `.json`
- **Temp Files:** Automatically cleaned up after processing

---

## Running with Options

### Dev Server (with auto-reload)
```bash
uvicorn api.main:app --reload
```

### Production Server
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Custom Port
```bash
uvicorn api.main:app --port 9000
```

---

## Testing the API with Swagger UI

1. Start the server: `uvicorn api.main:app --reload`
2. Open: http://127.0.0.1:8000/docs
3. Click the **POST /analyze** endpoint
4. Click "Try it out"
5. Fill in the form fields and upload a file
6. Click "Execute"

---

## Code Quality Features

- Type hints throughout
- Comprehensive docstrings
- Proper error handling
- Graceful cleanup on shutdown
- Forms properly handle `None` values
- Temporary files automatically deleted

---

## Integration

The API integrates seamlessly with the existing pipeline:

1. **Input Processing** → Phase 1 (OCR, PDF extraction, JSON)
2. **Structuring** → Phase 2 (Structuring layer)
3. **Model 1** → Parameter interpretation
4. **Model 2** → Pattern-based risk analysis
5. **Model 3** → Contextual adjustment
6. **Reporting** → Final JSON output

All orchestrated through `main_orchestrator.generate_full_report()`.

---

## Next Steps

- Deploy with Gunicorn for production
- Add authentication (JWT tokens)
- Add request logging and monitoring
- Add rate limiting
- Store reports in database
- Add export formats (PDF, HTML)

