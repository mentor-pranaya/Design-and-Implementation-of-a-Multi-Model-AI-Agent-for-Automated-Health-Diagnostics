import json
from fastapi import UploadFile, HTTPException
import logging

logger = logging.getLogger(__name__)

async def parse_json(upload_file: UploadFile) -> dict:
    """
    Parse a JSON file upload and return the structured data.
    """
    try:
        content = await upload_file.read()
        data = json.loads(content)
        
        # Reset file pointer
        await upload_file.seek(0)
        
        return data
    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error: {str(e)}")
        raise HTTPException(status_code=400, detail="Invalid JSON format")
    except Exception as e:
        logger.error(f"JSON parsing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to parse JSON: {str(e)}")
