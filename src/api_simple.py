import json
import logging
from pathlib import Path
from datetime import datetime
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.middleware.gzip import GZIPMiddleware  # Commented out due to import error

logger = logging.getLogger(__name__)
app = FastAPI(title="Blood Report AI", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# app.add_middleware(GZIPMiddleware, minimum_size=1000)  # Commented out due to import error

ALLOWED = {'.pdf', '.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp', '.csv', '.json', '.txt'}
MAX_SIZE = 50 * 1024 * 1024

@app.get("/")
async def root():
    return {
        "service": "Blood Report AI",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "/health": "health check",
            "/api/upload": "file upload",
            "/docs": "api documentation"
        }
    }

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "Blood Report AI",
        "time": str(datetime.now())
    }

@app.post("/api/upload")
async def upload(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(400, "No filename")
    
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED:
        raise HTTPException(400, f"Format not allowed")
    
    content = await file.read()
    if len(content) == 0:
        raise HTTPException(400, "Empty file")
    
    Path("data/uploads").mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{ts}_{file.filename}"
    fpath = Path("data/uploads") / fname
    
    fpath.write_bytes(content)
    logger.info(f"Uploaded: {fname}")
    
    return {
        "status": "success",
        "file": fname,
        "type": ext,
        "size_mb": round(len(content) / 1024 / 1024, 2)
    }

@app.get("/api/formats")
async def formats():
    return {
        "formats": sorted(list(ALLOWED)),
        "total": len(ALLOWED)
    }

@app.get("/api/stats")
async def stats():
    d = Path("data/uploads")
    files = list(d.glob("*")) if d.exists() else []
    size = sum(f.stat().st_size for f in files if f.is_file())
    return {
        "total_files": len(files),
        "total_mb": round(size / 1024 / 1024, 2)
    }

@app.exception_handler(Exception)
async def error_handler(request, exc):
    logger.error(f"Error: {exc}")
    return JSONResponse({"error": str(exc)}, 500)
