import os
import sys
from pathlib import Path
from dotenv import load_dotenv
import uvicorn
import logging

sys.path.insert(0, str(Path(__file__).parent))
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

Path("data/uploads").mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(parents=True, exist_ok=True)

try:
    from src.api_optimized import app
    logger.info("Optimized API with LLM loaded successfully")
except ImportError as e:
    logger.error(f"Failed to load optimized API: {e}")
    sys.exit(1)

if __name__ == "__main__":
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "10000"))
    
    print("\n" + "="*70)
    print("BLOOD REPORT AI - SERVER STARTING")
    print("="*70)
    print(f"Server:    http://{host}:{port}")
    print(f"API Docs:  http://localhost:{port}/docs")
    print(f"Health:    http://localhost:{port}/health")
    print("="*70 + "\n")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,
        log_level="info"
    )
